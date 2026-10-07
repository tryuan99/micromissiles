"""The engagement runner class handles initializing and running a single
engagement.
"""

from typing import Any

import numpy as np
from absl import logging

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.engagement import (Engagement,
                                                      EngagementResult)
from simulation.swarm.reachability.interceptor import Interceptor
from simulation.swarm.reachability.proto.engagement_config_pb2 import \
    EngagementConfig
from simulation.swarm.reachability.state import State
from simulation.swarm.reachability.threat import Threat


class EngagementRunner:
    """Engagement runner.

    Attributes:
        interceptor: Interceptor.
        threat: Threat.
        engagement_config: Engagement configuration.
    """

    def __init__(
        self,
        interceptor: Interceptor,
        threat: Threat,
        engagement_config: EngagementConfig,
    ) -> None:
        self.interceptor = interceptor
        self.threat = threat
        self.engagement_config = engagement_config

    def __call__(
        self,
        sample: tuple[Any, ...],
    ) -> tuple[tuple[Any, ...], EngagementResult | None]:
        """Runs one engagement.

        Args:
            sample: A tuple consisting of the interceptor speed in m/s, the
                range in m, the relative azimuth and elevation in degrees, the
                threat speed in m/s, and the threat heading azimuth and
                elevation in degrees.

        Returns:
            A tuple consisting of the sample and the engagement result. The
            result is None if the threat starts below the ground level, in
            which case the engagement is skipped.

        Raises:
            RuntimeError: If optimization fails.
        """
        (
            interceptor_speed,
            relative_range,
            relative_azimuth,
            relative_elevation,
            threat_speed,
            threat_heading_azimuth,
            threat_heading_elevation,
        ) = sample
        relative_azimuth = np.deg2rad(relative_azimuth)
        relative_elevation = np.deg2rad(relative_elevation)
        threat_heading_azimuth = np.deg2rad(threat_heading_azimuth)
        threat_heading_elevation = np.deg2rad(threat_heading_elevation)

        interceptor_velocity = constants.FORWARD * interceptor_speed
        interceptor_position = np.array([
            0.0,
            self.engagement_config.altitude,
            0.0,
        ])

        threat_velocity = threat_speed * np.array([
            np.sin(threat_heading_azimuth) * np.cos(threat_heading_elevation),
            np.sin(threat_heading_elevation),
            np.cos(threat_heading_azimuth) * np.cos(threat_heading_elevation),
        ])
        threat_position = interceptor_position + relative_range * np.array([
            np.sin(relative_azimuth) * np.cos(relative_elevation),
            np.sin(relative_elevation),
            np.cos(relative_azimuth) * np.cos(relative_elevation),
        ])
        ground_level = self.engagement_config.termination_config.ground_level
        if threat_position[1] < ground_level:
            logging.warning(
                "Skipping the engagement for sample %s because the threat "
                "starts underground at an altitude of %.3f m, which is below "
                "the ground level of %.3f m.", tuple(float(x) for x in sample),
                threat_position[1], ground_level)
            return sample, None

        interceptor_state = State.from_components(
            interceptor_position,
            interceptor_velocity,
        )
        threat_state = State.from_components(
            threat_position,
            threat_velocity,
        )

        engagement = Engagement(
            self.interceptor,
            self.threat,
            self.engagement_config,
        )
        try:
            return sample, engagement.run(
                interceptor_state,
                threat_state,
            )
        except RuntimeError as err:
            raise RuntimeError(
                f"Engagement failed for sample {sample}: {err}") from err
