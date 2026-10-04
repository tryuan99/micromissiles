"""The engagement class simulates a single interceptor-threat engagement.

During each control step, the interceptor and the threat re-solve their convex
MPC against the other's predicted trajectory, warm-started from the previous
control step's plan. The first control is applied, and the nonlinear plant is
integrated forward one control step, which may be shorter than a plan step.

The MPC horizon is adaptive depending on the predicted time-to-intercept.
"""

from dataclasses import dataclass

import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.closest_approach import ClosestApproach
from simulation.swarm.reachability.interceptor import Interceptor
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
    """One control step's plans and the commands applied from them."""

    # Acceleration controls over the horizon in the local coordinates.
    interceptor_controls: np.ndarray
    threat_controls: np.ndarray

    # Acceleration command for the next control in the global coordinates.
    interceptor_command: np.ndarray
    threat_command: np.ndarray

    # Number of solver failures.
    solver_failures: int


@dataclass
class EngagementResult:
    """Result of one engagement."""

    # If true, the interceptor intercepted the threat.
    success: bool

    # Minimum separation between the interceptor and the threat in meters.
    min_separation: float

    # Time of minimum separation in seconds.
    time_of_min_separation: float

    # Intercept time in seconds. None if unsuccessful.
    intercept_time: float | None

    # Reason for why the engagement ended.
    reason: str

    # Number of control steps.
    step_count: int

    # Number of solver failures that fell back to the warm start.
    solver_failures: int

    # 6-DOF interceptor and threat states over time.
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
        num_plant_steps_per_control_step: Number of plant steps per control step.
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
        self.interceptor_mpc = InterceptorMpc(engagement_config)
        self.threat_mpc = ThreatMpc(engagement_config)
        self.num_plant_steps_per_control_step = max(
            1,
            round(engagement_config.mpc_config.control_time_step /
                  engagement_config.plant_time_step))
        self.plant_time_step = (engagement_config.mpc_config.control_time_step /
                                self.num_plant_steps_per_control_step)
        self.warm_start_shift = round(
            engagement_config.mpc_config.control_time_step /
            engagement_config.mpc_config.mpc_time_step)

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
        """
        initial_range = np.linalg.norm(threat_state.position -
                                       interceptor_state.position)
        closest_approach = ClosestApproach(initial_range)
        termination = Termination(self.engagement_config, initial_range)
        trajectory = Trajectory()
        trajectory.append(0.0, interceptor_state, threat_state)

        plan = None
        intercepted = False
        reason = TerminationReason.MAX_TIME
        solver_failures = 0
        control_step = 0
        for control_step in range(
                int(
                    round(
                        self.engagement_config.termination_config.max_time /
                        self.engagement_config.mpc_config.control_time_step))):
            plan = self._plan(interceptor_state, threat_state, plan)
            solver_failures += plan.solver_failures
            elapsed_time = control_step * self.engagement_config.mpc_config.control_time_step
            interceptor_state, threat_state, intercepted = self._integrate(
                plan, interceptor_state, threat_state, closest_approach,
                elapsed_time)
            trajectory.append(
                elapsed_time +
                self.engagement_config.mpc_config.control_time_step,
                interceptor_state, threat_state)
            if intercepted:
                reason = TerminationReason.INTERCEPT
                break
            reason = termination.reason(
                interceptor_state, threat_state, elapsed_time +
                self.engagement_config.mpc_config.control_time_step,
                closest_approach.separation)
            if reason is not None:
                break
            reason = TerminationReason.MAX_TIME

        times, interceptor_trajectory, threat_trajectory = trajectory.arrays()
        return EngagementResult(
            success=intercepted,
            min_separation=closest_approach.separation,
            time_of_min_separation=closest_approach.time,
            intercept_time=closest_approach.time if intercepted else None,
            reason=reason,
            step_count=control_step + 1,
            solver_failures=solver_failures,
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
        """
        horizon = self._horizon(interceptor_state, threat_state)
        interceptor_model = self.interceptor.prediction_model(interceptor_state)
        threat_model = self.threat.prediction_model(threat_state)
        interceptor_controls, threat_controls = None, None
        if previous_plan is not None:
            interceptor_controls = self._shift_controls(
                previous_plan.interceptor_controls, horizon)
            threat_controls = self._shift_controls(
                previous_plan.threat_controls, horizon)

        interceptor_positions, interceptor_forwards = (
            self._predict_constant_velocity(
                interceptor_state, horizon,
                self.engagement_config.mpc_config.mpc_time_step))
        threat_positions, _ = self._predict_constant_velocity(
            threat_state, horizon,
            self.engagement_config.mpc_config.mpc_time_step)
        away_from_interceptor = constants.normalize_vector(
            threat_state.position - interceptor_state.position)

        failures = 0
        for _ in range(
                max(1, self.engagement_config.mpc_config.
                    best_response_iterations)):
            away_directions = self._unit_rows(
                threat_positions - interceptor_positions, away_from_interceptor)
            threat_controls, threat_positions, _, threat_solved = (
                self.threat_mpc.solve(
                    threat_state,
                    threat_model,
                    away_directions,
                    interceptor_forwards,
                    horizon,
                    threat_controls,
                ))
            (
                interceptor_controls,
                interceptor_positions,
                interceptor_velocities,
                interceptor_solved,
            ) = self.interceptor_mpc.solve(interceptor_state, interceptor_model,
                                           threat_positions, horizon,
                                           interceptor_controls)
            interceptor_forwards = self._unit_rows(interceptor_velocities,
                                                   constants.FORWARD)
            failures += int(not interceptor_solved) + int(not threat_solved)

        return Plan(
            interceptor_controls=interceptor_controls,
            threat_controls=threat_controls,
            interceptor_command=(
                interceptor_model.basis_matrix() @ interceptor_controls[0]),
            threat_command=threat_model.basis_matrix() @ threat_controls[0],
            solver_failures=failures,
        )

    def _integrate(self, plan: Plan, interceptor_state: State,
                   threat_state: State, closest_approach: ClosestApproach,
                   start_time: float) -> tuple[State, State, bool]:
        """Integrates the interceptor and the threat models over one control step.

        Args:
            plan: Plan to execute over the control step.
            interceptor_state: State of the interceptor.
            threat_state: State of the threat.
            closest_approach: Closest approach tracker to update.
            start_time: Simulation time at the start in seconds.

        Returns:
            A tuple consisting of the new interceptor and threat states and
            whether the capture radius was breached during the time step.
        """
        for step in range(self.num_plant_steps_per_control_step):
            start_offset = threat_state.position - interceptor_state.position
            interceptor_state = self.interceptor.step(interceptor_state,
                                                      plan.interceptor_command,
                                                      self.plant_time_step)
            threat_state = self.threat.step(threat_state, plan.threat_command,
                                            self.plant_time_step)
            closest_approach.update(
                start_offset,
                threat_state.position - interceptor_state.position,
                start_time + step * self.plant_time_step, self.plant_time_step)
            if closest_approach.separation <= self.engagement_config.capture_radius:
                return interceptor_state, threat_state, True
        return interceptor_state, threat_state, False

    def _shift_controls(
        self,
        controls: np.ndarray | None,
        horizon: int,
    ) -> np.ndarray | None:
        """Advances the previous plan to serve as the next warm start.

        Args:
            controls: Controls of the previous plan over the previous horizon.
            horizon: Number of steps in the horizon.

        Returns:
            The previous plan advanced by the elapsed control period and
            truncated or padded to the new horizon, or None.
        """
        if controls is None:
            return None
        shifted = controls[min(self.warm_start_shift, len(controls) - 1):]
        if len(shifted) >= horizon:
            return shifted[:horizon]
        padding = np.repeat(shifted[-1:], horizon - len(shifted), axis=0)
        return np.vstack([shifted, padding])

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

    @staticmethod
    def _predict_constant_velocity(
        state: State,
        horizon: int,
        time_step: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Predicts an agent's path assuming a constant velocity.

        Args:
            state: Current state of the agent.
            horizon: Number of steps in the horizon.
            time_step: Time step in seconds.

        Returns:
            A tuple consisting of the agent's future positions and forward
            directions over the horizon.
        """
        steps = np.arange(horizon + 1)[:, None]
        positions = (state.position[None, :] +
                     steps * time_step * state.velocity[None, :])
        return positions, np.tile(state.forward, (horizon + 1, 1))

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
