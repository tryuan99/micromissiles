"""The engagement class simulates a single interceptor-threat engagement.

During each control step, the interceptor and the threat re-solve their convex
MPC against the other's nonlinear predicted trajectory, warm-started from the
previous control step's commands. Each convex problem is a local approximation
of the shared flight equations. Planned commands are applied over one control
period, and the nonlinear plant stops at the first interception or other
terminal event.

The MPC horizon is adaptive depending on the predicted time-to-intercept.
"""

from dataclasses import dataclass

import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.closest_approach import ClosestApproach
from simulation.swarm.reachability.interceptor import Interceptor
from simulation.swarm.reachability.model import PredictionModel
from simulation.swarm.reachability.mpc import InterceptorMpc, ThreatMpc
from simulation.swarm.reachability.proto.engagement_config_pb2 import \
    EngagementConfig
from simulation.swarm.reachability.state import State
from simulation.swarm.reachability.termination import (Termination,
                                                       TerminationReason)
from simulation.swarm.reachability.threat import Threat
from simulation.swarm.reachability.trajectory import Trajectory


@dataclass
class Plan:
    """Stores a control period's plans and commands.

    Attributes:
        interceptor_controls: Local interceptor acceleration commands in
            m/s^2 with shape (horizon, 3).
        threat_controls: Local threat acceleration commands in m/s^2 with
            shape (horizon, 3).
        interceptor_commands: Interceptor commands in m/s^2 with shape
            (horizon, 3).
        threat_commands: Threat commands in m/s^2 with shape (horizon, 3).
    """

    # Acceleration controls over the horizon in the local coordinates.
    interceptor_controls: np.ndarray
    threat_controls: np.ndarray

    # Acceleration commands over the horizon in the global coordinates.
    interceptor_commands: np.ndarray
    threat_commands: np.ndarray


@dataclass
class EngagementResult:
    """Stores the outcome and sampled states of one engagement.

    Attributes:
        min_separation: Minimum agent separation in meters.
        time_of_min_separation: Time of minimum separation in seconds.
        reason: Reason the engagement ended.
        times: Sample timestamps in seconds with shape (samples,).
        interceptor_trajectory: Interceptor positions in meters and velocities
            in m/s with shape (samples, 6).
        threat_trajectory: Threat positions in meters and velocities in m/s
            with shape (samples, 6).
    """

    # Minimum separation between the interceptor and the threat in meters.
    min_separation: float

    # Time of minimum separation in seconds.
    time_of_min_separation: float

    # Reason for why the engagement ended.
    reason: TerminationReason

    # Interceptor and threat positions and velocities over time.
    times: np.ndarray
    interceptor_trajectory: np.ndarray
    threat_trajectory: np.ndarray


class Engagement:
    """Represents one interceptor-vs.-threat engagement.

    Attributes:
        interceptor: Interceptor.
        threat: Threat.
        engagement_config: Engagement configuration.
        interceptor_mpc: Interceptor MPC.
        threat_mpc: Threat MPC.
        num_plant_steps_per_control_step: Number of plant steps per control
            step.
        plant_time_step: Plant time step.
        warm_start_shift: Number of plan steps to shift for the next replan.
    """

    # Threshold for zero.
    _EPSILON = 1e-9

    def __init__(
        self,
        interceptor: Interceptor,
        threat: Threat,
        engagement_config: EngagementConfig,
    ) -> None:
        self.interceptor = interceptor
        self.threat = threat
        self.engagement_config = engagement_config
        mpc_config = engagement_config.mpc_config

        self.interceptor_mpc = InterceptorMpc(engagement_config)
        self.threat_mpc = ThreatMpc(engagement_config)
        self.num_plant_steps_per_control_step = int(
            np.ceil(mpc_config.control_time_step /
                    engagement_config.plant_time_step))
        self.plant_time_step = (engagement_config.mpc_config.control_time_step /
                                self.num_plant_steps_per_control_step)
        self.warm_start_shift = (mpc_config.control_time_step /
                                 mpc_config.mpc_time_step)

    def run(
        self,
        interceptor_state: State,
        threat_state: State,
    ) -> EngagementResult:
        """Simulates the engagement.

        Args:
            interceptor_state: Initial state of the interceptor.
            threat_state: Initial state of the threat.

        Returns:
            The engagement result.

        Raises:
            RuntimeError: If either agent's optimization fails.
        """
        initial_range = np.linalg.norm(threat_state.position -
                                       interceptor_state.position)
        closest_approach = ClosestApproach(initial_range)
        termination = Termination(self.engagement_config, initial_range)
        trajectory = Trajectory()
        trajectory.append(0.0, interceptor_state, threat_state)

        plan = None
        ground_level = self.engagement_config.termination_config.ground_level
        if interceptor_state.position[1] < ground_level:
            reason = TerminationReason.INTERCEPTOR_GROUND
        elif threat_state.position[1] < ground_level:
            reason = TerminationReason.THREAT_GROUND
        elif initial_range <= self.engagement_config.capture_radius:
            reason = TerminationReason.INTERCEPT
        else:
            reason = termination.reason(interceptor_state, threat_state, 0.0,
                                        initial_range, 0.0)
        elapsed_time = 0.0
        max_time = self.engagement_config.termination_config.max_time
        while reason is None and elapsed_time < max_time:
            remaining = max_time - elapsed_time
            control_time_step = (
                self.engagement_config.mpc_config.control_time_step)
            duration = min(remaining, control_time_step)
            plan = self._plan(interceptor_state, threat_state, plan)
            previous_time = elapsed_time
            (interceptor_state, threat_state, elapsed_time,
             reason) = self._integrate(plan, interceptor_state, threat_state,
                                       closest_approach, elapsed_time, duration)
            trajectory.append(elapsed_time, interceptor_state, threat_state)
            if reason is None:
                reason = termination.reason(interceptor_state, threat_state,
                                            elapsed_time,
                                            closest_approach.separation,
                                            elapsed_time - previous_time)
        if reason is None:
            reason = TerminationReason.MAX_TIME

        times, interceptor_trajectory, threat_trajectory = trajectory.arrays()
        return EngagementResult(
            min_separation=closest_approach.separation,
            time_of_min_separation=closest_approach.time,
            reason=reason,
            times=times,
            interceptor_trajectory=interceptor_trajectory,
            threat_trajectory=threat_trajectory,
        )

    def _plan(
        self,
        interceptor_state: State,
        threat_state: State,
        previous_plan: Plan | None,
    ) -> Plan:
        """Plans one control step.

        Runs the Gauss-Seidel best response between the two convex MPCs,
        warm-starting each solve from the previous plan shifted one step. The
        threat is omniscient and always plans to evade the interceptor's state
        every step with no delay.

        Args:
            interceptor_state: Current state of the interceptor.
            threat_state: Current state of the threat.
            previous_plan: The previous control step's plan or None on the
                first control step.

        Returns:
            The plan for the current control step.

        Raises:
            RuntimeError: If either agent's optimization fails.
        """
        horizon = self._horizon(interceptor_state, threat_state)
        interceptor_model = PredictionModel(
            self.interceptor, interceptor_state, self.plant_time_step,
            self.engagement_config.mpc_config.control_time_step)
        threat_model = PredictionModel(
            self.threat, threat_state, self.plant_time_step,
            self.engagement_config.mpc_config.control_time_step)
        interceptor_controls, threat_controls = None, None
        if previous_plan is not None:
            # Carry commands into the new flight basis. Reusing old local
            # components would rotate the intended warm-start maneuver.
            interceptor_controls = (
                self._shift_controls(previous_plan.interceptor_commands,
                                     horizon) @ interceptor_model.basis)
            threat_controls = (self._shift_controls(
                previous_plan.threat_commands, horizon) @ threat_model.basis)

        time_step = self.engagement_config.mpc_config.mpc_time_step
        initial_interceptor_controls = (np.zeros(
            (horizon,
             3)) if interceptor_controls is None else interceptor_controls)
        (
            interceptor_positions,
            interceptor_velocities,
        ) = interceptor_model.trajectory(interceptor_state,
                                         initial_interceptor_controls,
                                         time_step)
        interceptor_forwards = self._unit_rows(interceptor_velocities,
                                               interceptor_state.forward)
        initial_threat_controls = (np.zeros(
            (horizon, 3)) if threat_controls is None else threat_controls)
        threat_positions, _ = threat_model.trajectory(threat_state,
                                                      initial_threat_controls,
                                                      time_step)
        away_from_interceptor = constants.normalize_vector(
            threat_state.position - interceptor_state.position)

        for _ in range(
                self.engagement_config.mpc_config.best_response_iterations):
            away_directions = self._unit_rows(
                threat_positions - interceptor_positions, away_from_interceptor)
            threat_controls, threat_positions, _ = self.threat_mpc.solve(
                threat_state,
                threat_model,
                away_directions,
                interceptor_forwards,
                horizon,
                threat_controls,
            )
            (
                interceptor_controls,
                interceptor_positions,
                interceptor_velocities,
            ) = self.interceptor_mpc.solve(interceptor_state, interceptor_model,
                                           threat_positions, horizon,
                                           interceptor_controls)
            interceptor_forwards = self._unit_rows(interceptor_velocities,
                                                   constants.FORWARD)

        return Plan(
            interceptor_controls=interceptor_controls,
            threat_controls=threat_controls,
            interceptor_commands=(
                interceptor_controls @ interceptor_model.basis.T),
            threat_commands=threat_controls @ threat_model.basis.T,
        )

    def _integrate(
        self,
        plan: Plan,
        interceptor_state: State,
        threat_state: State,
        closest_approach: ClosestApproach,
        start_time: float,
        duration: float,
    ) -> tuple[State, State, float, TerminationReason | None]:
        """Integrates until the control period ends or a terminal event occurs.

        Args:
            plan: Commands to apply during this control period.
            interceptor_state: Interceptor state at the start of integration.
            threat_state: Threat state at the start of integration.
            closest_approach: Tracker updated with each executed plant segment.
            start_time: Absolute simulation start time in seconds.
            duration: Duration to integrate in seconds.

        Returns:
            A tuple containing the final interceptor state, final threat state,
            absolute simulation time in seconds, and terminal reason. The reason
            is None when integration finishes without a terminal event.
        """
        offset_time = 0.0
        command_step = 0
        mpc_time_step = self.engagement_config.mpc_config.mpc_time_step
        ground_level = self.engagement_config.termination_config.ground_level
        while offset_time < duration:
            while offset_time >= (command_step + 1) * mpc_time_step:
                command_step += 1
            # Split plant steps at plan-command boundaries as well as at the
            # end of the control period.
            time_step = min(self.plant_time_step, duration - offset_time,
                            (command_step + 1) * mpc_time_step - offset_time)
            interceptor_next = self.interceptor.step(
                interceptor_state, plan.interceptor_commands[min(
                    command_step,
                    len(plan.interceptor_commands) - 1)], time_step)
            threat_next = self.threat.step(
                threat_state,
                plan.threat_commands[min(command_step,
                                         len(plan.threat_commands) - 1)],
                time_step)
            start_offset = threat_state.position - interceptor_state.position
            end_offset = threat_next.position - interceptor_next.position
            fraction = ClosestApproach.first_contact_fraction(
                start_offset, end_offset, self.engagement_config.capture_radius)
            reason = (TerminationReason.INTERCEPT
                      if fraction is not None else None)
            for state, next_state, ground_reason in (
                (interceptor_state, interceptor_next,
                 TerminationReason.INTERCEPTOR_GROUND),
                (threat_state, threat_next, TerminationReason.THREAT_GROUND),
            ):
                if next_state.position[1] < ground_level:
                    ground_fraction = (
                        (state.position[1] - ground_level) /
                        (state.position[1] - next_state.position[1]))
                    if fraction is None or ground_fraction < fraction:
                        fraction = ground_fraction
                        reason = ground_reason
            min_speed = (
                self.engagement_config.termination_config.min_intercept_speed)
            if min_speed > 0 and interceptor_next.speed < min_speed:
                slow_fraction = ClosestApproach.first_contact_fraction(
                    interceptor_state.velocity, interceptor_next.velocity,
                    min_speed)
                if slow_fraction is not None and (fraction is None or
                                                  slow_fraction < fraction):
                    fraction = slow_fraction
                    reason = TerminationReason.INTERCEPTOR_TOO_SLOW
            if fraction is not None:
                interceptor_next = interceptor_state.interpolate(
                    interceptor_next, fraction)
                threat_next = threat_state.interpolate(threat_next, fraction)
                time_step *= fraction
            closest_approach.update(
                start_offset, threat_next.position - interceptor_next.position,
                start_time + offset_time, time_step)
            interceptor_state, threat_state = interceptor_next, threat_next
            offset_time += time_step
            if reason is not None:
                if reason == TerminationReason.INTERCEPT:
                    # First contact is exactly on the radius boundary. Keep
                    # its analytic distance and time rather than roundoff from
                    # subtracting interpolated absolute positions.
                    closest_approach.separation = (
                        self.engagement_config.capture_radius)
                    closest_approach.time = start_time + offset_time
                return (interceptor_state, threat_state,
                        start_time + offset_time, reason)
        return interceptor_state, threat_state, start_time + duration, None

    def _shift_controls(self, controls: np.ndarray | None,
                        horizon: int) -> np.ndarray | None:
        """Averages the elapsed plan onto the next plan's time intervals.

        Fractional shifts preserve elapsed time when control and planning
        periods
        differ. The final command is held beyond the previous horizon.

        Args:
            controls: Previous commands with shape (previous_horizon, 3), or
                None
                when there is no previous plan.
            horizon: Number of intervals in the next plan.

        Returns:
            Shifted commands with shape (horizon, 3), or None if controls is
            None.
        """
        if controls is None:
            return None
        indices = self.warm_start_shift + np.arange(horizon)
        left = np.floor(indices).astype(int)
        fractions = (indices - left)[:, None]
        return ((1 - fractions) * controls[np.minimum(left,
                                                      len(controls) - 1)] +
                fractions * controls[np.minimum(left + 1,
                                                len(controls) - 1)])

    def _horizon(
        self,
        interceptor_state: State,
        threat_state: State,
    ) -> int:
        """Calculates the number of steps in the adaptive horizon.

        The horizon is calculated as time_to_go_horizon_factor multiplied by the
        predicted time-to-intercept. This time is converted to the number of
        MPC time steps and clamped to the minimum and maximum horizon lengths.

        Args:
            interceptor_state: State of the interceptor.
            threat_state: State of the threat.

        Returns:
            The number of plan steps in the horizon.
        """
        relative_position = threat_state.position - interceptor_state.position
        range_to_target = np.linalg.norm(relative_position)
        line_of_sight = relative_position / max(range_to_target, self._EPSILON)
        closing_speed = -float(
            (threat_state.velocity - interceptor_state.velocity)
            @ line_of_sight)
        if closing_speed <= 1e-6:
            steps = self.engagement_config.mpc_config.max_horizon
        else:
            steps = round(
                self.engagement_config.mpc_config.time_to_go_horizon_factor *
                range_to_target / closing_speed /
                self.engagement_config.mpc_config.mpc_time_step)
        return int(
            np.clip(
                steps,
                self.engagement_config.mpc_config.min_horizon,
                self.engagement_config.mpc_config.max_horizon,
            ))

    def _unit_rows(self, vectors: np.ndarray,
                   fallback: np.ndarray) -> np.ndarray:
        """Normalizes each row of a matrix.

        Args:
            vectors: A 2-dimensional matrix of vectors.
            fallback: The unit vector substituted for near-zero rows.

        Returns:
            The 2-dimensional matrix of row-wise unit vectors.
        """
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return np.where(
            norms > 1e-6,
            vectors / np.maximum(norms, self._EPSILON),
            fallback,
        )
