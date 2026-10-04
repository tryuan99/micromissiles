"""The termination class determines when a non-capturing engagement can be
abandoned as a miss.
"""

from enum import StrEnum

import numpy as np

from simulation.swarm.reachability.proto.engagement_config_pb2 import \
    EngagementConfig
from simulation.swarm.reachability.state import State


class TerminationReason(StrEnum):
    """Termination reason enumeration."""
    INTERCEPT = "intercept"
    MAX_TIME = "max_time"
    INTERCEPTOR_GROUND = "interceptor_ground"
    INTERCEPTOR_TOO_SLOW = "interceptor_too_slow"
    DIVERGING = "diverging"
    ESCAPING = "escaping"
    STALLED = "stalled"


class Termination:
    """The termination class determines when to abandon the engagement as a miss.

    Attributes:
        engagement_config: Engagement configuration.
        initial_range: Initial range in meters.
        previous_range: Previous range in meters.
        diverging_time: Duration over which the distance is increasing.
        min_distance: Closest point of approach.
        last_improvement_time: Time at which the closest point of approach last
            improved by more than the stall tolerance.
    """

    def __init__(
        self,
        engagement_config: EngagementConfig,
        initial_range: float,
    ) -> None:
        self.engagement_config = engagement_config
        self.initial_range = initial_range
        self.previous_range = initial_range
        self.diverging_time = 0.0
        self.min_distance = initial_range
        self.last_improvement_time = 0.0

    def reason(self, interceptor_state: State, threat_state: State,
               elapsed_time: float, min_distance: float) -> str | None:
        """Checks whether the engagement is decided.

        Args:
            interceptor_state: Interceptor state.
            threat_state: Threat state.
            elapsed_time: Elapsed simulation time in seconds.
            min_distance: Minimum distance so far in meters.

        Returns:
            The reason the engagement should stop or None to keep going.
        """
        termination_config = self.engagement_config.termination_config
        if interceptor_state.position[1] < termination_config.ground_level:
            return TerminationReason.INTERCEPTOR_GROUND
        if interceptor_state.speed < termination_config.min_intercept_speed:
            return TerminationReason.INTERCEPTOR_TOO_SLOW

        missing = min_distance > self.engagement_config.capture_radius
        current_range = np.linalg.norm(threat_state.position -
                                       interceptor_state.position)
        diverging = current_range > self.previous_range
        self.previous_range = current_range

        if (missing and diverging and current_range
                > termination_config.post_cpa_factor * min_distance):
            return TerminationReason.DIVERGING
        if diverging and current_range > termination_config.escape_margin * self.initial_range:
            self.diverging_time += self.engagement_config.mpc_config.control_time_step
            if self.diverging_time >= termination_config.escape_dwell:
                return TerminationReason.ESCAPING
        else:
            self.diverging_time = 0.0

        if min_distance < self.min_distance - termination_config.stall_tolerance:
            self.min_distance = min_distance
            self.last_improvement_time = elapsed_time
        if (missing and elapsed_time - self.last_improvement_time
                > termination_config.stall_time):
            return TerminationReason.STALLED
        return None
