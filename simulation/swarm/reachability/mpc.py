"""Convex planning around a physical nonlinear reference trajectory.

The optimizer uses local Jacobians of the shared flight equations. Every
returned trajectory is predicted using the full equations.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

import casadi
import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.model import PredictionModel
from simulation.swarm.reachability.proto.engagement_config_pb2 import \
    EngagementConfig
from simulation.swarm.reachability.state import State


@dataclass
class MpcProblem:
    """Shared data for constructing an MPC objective and constraints.

    Attributes:
        optimizer: Optimizer containing the control variables.
        positions: Predicted position expressions in meters.
        velocities: Predicted velocity expressions in m/s.
        reference_states: States along the nonlinear reference trajectory.
        prediction_model: Shared nonlinear flight model.
        max_normal_accelerations: Reference normal acceleration limits in m/s^2.
    """

    optimizer: casadi.Opti
    positions: list[casadi.MX | casadi.DM]
    velocities: list[casadi.MX | casadi.DM]
    reference_states: list[State]
    prediction_model: PredictionModel
    max_normal_accelerations: np.ndarray


class ConvexMpc(ABC):
    """Interface for solving a convex QCQP.

    Attributes:
        engagement_config: Engagement configuration.
    """

    def __init__(self, engagement_config: EngagementConfig) -> None:
        self.engagement_config = engagement_config

    @abstractmethod
    def _control_regularization(self) -> float:
        """Returns the objective weight for squared acceleration commands."""

    def _solve(
        self,
        initial_state: State,
        prediction_model: PredictionModel,
        horizon: int,
        initial_controls: np.ndarray | None,
        objective: Callable[[MpcProblem], casadi.MX],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Solves the convex program.

        Args:
            initial_state: Initial state.
            prediction_model: Shared nonlinear model used to form local
                approximations.
            horizon: Number of steps.
            initial_controls: Initial controls or None to start from zero.
            objective: Function building the cost and agent-specific
                constraints.

        Returns:
            The successful solver result.

        Raises:
            RuntimeError: If optimization fails. An unsolved plan must not be
                applied or recorded as a valid reachability result.
        """
        time_step = self.engagement_config.mpc_config.mpc_time_step
        # Start from the previous plan, or zero commands on the first solve.
        # Limit these commands along the evolving reference trajectory.
        reference_controls = (np.zeros(
            (horizon, 3)) if initial_controls is None else initial_controls)
        reference_controls = prediction_model.reference_controls(
            initial_state, reference_controls, time_step)

        # Approximate each nonlinear transition around the reference plan:
        (
            reference_states,
            state_jacobians,
            command_jacobians,
            offsets,
        ) = prediction_model.linearize(initial_state, reference_controls,
                                       time_step)

        # Freeze speed-dependent normal limits at each interval's start.
        max_forward_acceleration = prediction_model.max_forward_acceleration
        reference_velocities = np.array(
            [state.velocity for state in reference_states[:-1]])
        max_normal_accelerations = prediction_model.max_normal_accelerations(
            reference_velocities)

        optimizer = casadi.Opti()
        # Optimize dimensionless normal inputs with magnitude at most one,
        # then scale them to physical accelerations in m/s^2.
        normal_inputs = optimizer.variable(2, horizon)
        normal_scales = casadi.repmat(
            casadi.DM(max_normal_accelerations).T, 2, 1)
        normal_controls = normal_scales * normal_inputs

        # Optimize a forward input in [-1, 1] only when forward acceleration
        # is available. Otherwise, fix the forward command to zero.
        forward_input = None
        if max_forward_acceleration > 0:
            forward_input = optimizer.variable(1, horizon)
            forward_controls = max_forward_acceleration * forward_input
            optimizer.subject_to(optimizer.bounded(-1, forward_input, 1))
        else:
            forward_controls = casadi.DM.zeros(1, horizon)
        controls = casadi.vertcat(forward_controls, normal_controls)
        states = [initial_state]
        for step in range(horizon):
            states.append(
                State(
                    casadi.DM(state_jacobians[step]) @ states[-1].vector +
                    casadi.DM(command_jacobians[step]) @ controls[:, step] +
                    casadi.DM(offsets[step])))
        positions = [casadi.vertcat(state.position) for state in states]
        velocities = [casadi.vertcat(state.velocity) for state in states]

        problem = MpcProblem(optimizer, positions, velocities, reference_states,
                             prediction_model, max_normal_accelerations)
        cost = objective(problem)
        cost += self._control_regularization() * casadi.sumsqr(controls)
        optimizer.minimize(cost)

        for step in range(horizon):
            optimizer.subject_to(casadi.sumsqr(normal_inputs[:, step]) <= 1)

        optimizer.solver(
            "ipopt",
            {"print_time": False},
            {
                "print_level": 0,
                "sb": "yes",
            },
        )
        if initial_controls is not None:
            optimizer.set_initial(
                normal_inputs,
                np.divide(reference_controls[:, 1:].T,
                          max_normal_accelerations[None, :],
                          out=np.zeros((2, horizon)),
                          where=max_normal_accelerations[None, :] > 0))
            if forward_input is not None:
                optimizer.set_initial(
                    forward_input, reference_controls[:, 0][None, :] /
                    max_forward_acceleration)
        try:
            solution = optimizer.solve()
            solved_controls = np.array(solution.value(controls)).reshape(
                3, horizon).T
        except RuntimeError as err:
            raise RuntimeError(
                f"Failed to solve optimization problem: {err}") from err
        positions, velocities = prediction_model.trajectory(
            initial_state, solved_controls, time_step)
        return solved_controls, positions, velocities


class InterceptorMpc(ConvexMpc):
    """The interceptor MPC minimizes separation from the threat trajectory."""

    def solve(
        self,
        initial_state: State,
        prediction_model: PredictionModel,
        threat_positions: np.ndarray,
        horizon: int,
        initial_controls: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Solves the interceptor's quadratic problem.

        Args:
            initial_state: Initial state.
            prediction_model: Shared nonlinear model used to form local
                approximations.
            threat_positions: Predicted threat positions.
            horizon: Number of steps.
            initial_controls: Initial controls or None to start from zero.

        Returns:
            The solver result minimizing separation from the threat trajectory.
        """
        # Predict closest approach using the previous plan. Interpolate between
        # prediction steps to locate closest approach within a time interval.
        prediction_controls = (np.zeros(
            (horizon, 3)) if initial_controls is None else initial_controls)
        positions, _ = prediction_model.trajectory(
            initial_state, prediction_controls,
            self.engagement_config.mpc_config.mpc_time_step)
        offsets = positions - threat_positions
        deltas = np.diff(offsets, axis=0)
        lengths_squared = np.sum(deltas**2, axis=1)
        fractions = np.clip(
            -np.sum(offsets[:-1] * deltas, axis=1) /
            np.maximum(lengths_squared, 1e-18), 0, 1)
        misses = offsets[:-1] + fractions[:, None] * deltas
        closest_approach_step = int(np.argmin(np.sum(misses**2, axis=1)))
        closest_approach_fraction = float(fractions[closest_approach_step])
        return self._solve(
            initial_state, prediction_model, horizon,
            initial_controls, lambda problem: self._objective(
                problem.positions, threat_positions, closest_approach_step,
                closest_approach_fraction))

    def _objective(
        self,
        positions: list[casadi.MX | casadi.DM],
        threat_positions: np.ndarray,
        closest_approach_step: int,
        closest_approach_fraction: float,
    ) -> casadi.MX:
        """Builds the interceptor's objective.

        Args:
            positions: Positions for each step during the horizon.
            threat_positions: Predicted threat positions.
            closest_approach_step: Step containing predicted closest approach.
            closest_approach_fraction: Fraction of the step at closest
                approach.

        Returns:
            The cost expression to minimize.
        """
        cost = 0
        for step in range(1, closest_approach_step + 1):
            offset = positions[step] - casadi.DM(threat_positions[step])
            cost += (self.engagement_config.mpc_config.interceptor_config.
                     running_weight) * casadi.dot(offset, offset)
        start_offset = (positions[closest_approach_step] -
                        casadi.DM(threat_positions[closest_approach_step]))
        end_offset = (positions[closest_approach_step + 1] -
                      casadi.DM(threat_positions[closest_approach_step + 1]))
        offset = ((1 - closest_approach_fraction) * start_offset +
                  closest_approach_fraction * end_offset)
        cost += (self.engagement_config.mpc_config.interceptor_config.
                 terminal_weight) * casadi.dot(offset, offset)
        return cost

    def _control_regularization(self) -> float:
        """Returns the objective weight for squared acceleration commands."""
        return (self.engagement_config.mpc_config.interceptor_config.
                control_regularization)


class ThreatMpc(ConvexMpc):
    """The threat MPC maximizes separation from the interceptor."""

    def solve(
        self,
        initial_state: State,
        prediction_model: PredictionModel,
        interceptor_away_directions: np.ndarray,
        interceptor_forward_directions: np.ndarray,
        horizon: int,
        initial_controls: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Solves the threat's quadratic problem.

        Args:
            initial_state: Initial state.
            prediction_model: Shared nonlinear model used to form local
                approximations.
            interceptor_away_directions: Directions away from the interceptor.
            interceptor_forward_directions: Predicted forward directions of
                the interceptor.
            horizon: Number of steps.
            initial_controls: Initial controls or None to start from zero.

        Returns:
            The solver result maximizing the separation from the interceptor.
        """
        return self._solve(
            initial_state, prediction_model, horizon,
            initial_controls, lambda problem: self._objective(
                problem, interceptor_away_directions,
                interceptor_forward_directions))

    def _objective(
        self,
        problem: MpcProblem,
        interceptor_away_directions: np.ndarray,
        interceptor_forward_directions: np.ndarray,
    ) -> casadi.MX:
        """Builds the threat's objective.

        The threat's planned positions are also constrained to remain above the
        ground level with enough altitude to stop a descent, so it cannot
        choose a dive that makes the next replan infeasible.

        Args:
            problem: Shared optimization and nonlinear reference data.
            interceptor_away_directions: Directions away from the interceptor.
            interceptor_forward_directions: Predicted forward directions of
                the interceptor.

        Returns:
            The cost expression to minimize.
        """
        optimizer = problem.optimizer
        positions, velocities = problem.positions, problem.velocities
        reference_states = problem.reference_states
        prediction_model = problem.prediction_model
        ground_level = self.engagement_config.termination_config.ground_level

        # Project the normal acceleration limit onto the vertical axis.
        forwards = np.array([state.forward for state in reference_states[:-1]])
        vertical_components = forwards[:, 1]
        normal_vertical_fractions = np.sqrt(
            np.maximum(1 - vertical_components**2, 0))

        # Forward acceleration is available outside the speed error deadband.
        speeds = np.array([state.speed for state in reference_states[:-1]])
        speed_errors = prediction_model.agent.max_speed() - speeds
        forward_limits = prediction_model.max_forward_acceleration * (
            np.abs(speed_errors) >= constants.SPEED_ERROR_THRESHOLD)

        # Combine vertical contributions from normal and forward acceleration.
        max_vertical_accelerations = (
            problem.max_normal_accelerations * normal_vertical_fractions +
            forward_limits * np.abs(vertical_components))

        cost = 0
        for step in range(1, len(positions)):
            # Favor movement away from the interceptor.
            cost -= (self.engagement_config.mpc_config.threat_config.
                     evade_range_weight) * casadi.dot(
                         positions[step],
                         casadi.DM(interceptor_away_directions[step]))

            # Penalize velocity along the interceptor's forward direction.
            alignment = casadi.dot(
                velocities[step],
                casadi.DM(interceptor_forward_directions[step]))
            cost += (self.engagement_config.mpc_config.threat_config.
                     evade_orthogonal_weight) * alignment**2

            # Keep the threat above ground.
            altitude = positions[step][1] - ground_level
            optimizer.subject_to(altitude >= 0)

            # Leave enough altitude to stop a descent using upward acceleration.
            descent_speed = casadi.fmax(-velocities[step][1], 0)
            optimizer.subject_to(descent_speed**2 <= 2 *
                                 max_vertical_accelerations[step - 1] *
                                 altitude)

        return cost

    def _control_regularization(self) -> float:
        """Returns the objective weight for squared acceleration commands."""
        return (self.engagement_config.mpc_config.threat_config.
                control_regularization)
