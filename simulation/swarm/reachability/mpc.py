"""The convex MPC class is an interface for the convex quadratic programs to be
solved for each agent. The interceptor and threat MPC classes implement the
specific objectives.

At each control step, each agent solves a convex QCQP on the linearized
prediction model.
"""

from abc import ABC, abstractmethod

import casadi
import numpy as np
from absl import logging

from simulation.swarm.reachability.model import PredictionModel
from simulation.swarm.reachability.proto.engagement_config_pb2 import \
    EngagementConfig
from simulation.swarm.reachability.state import State
from simulation.swarm.reachability.threat import Threat

# The result consists of the (controls, positions, velocities, solved), where
# solved is false if the solve fell back to the warm start.
Result = tuple[np.ndarray, np.ndarray, np.ndarray, bool]


class ConvexMpc(ABC):
    """Interface for solving a convex QCQP.

    Attributes:
        engagement_config: Engagement configuration.
    """

    def __init__(self, engagement_config: EngagementConfig) -> None:
        self.engagement_config = engagement_config

    @abstractmethod
    def _objective(
        self,
        optimizer: casadi.Opti,
        positions: list[casadi.MX],
        velocities: list[casadi.MX],
        horizon: int,
        **kwargs: np.ndarray,
    ) -> casadi.MX:
        """Builds the agent's objective.

        Args:
            optimizer: Optimizer stack.
            positions: Positions for each step during the horizon.
            velocities: Velocities for each step during the horizon.
            horizon: Number of steps.
            **kwargs: Agent-specific inputs passed to the solver.

        Returns:
            The cost expression to minimize.
        """

    @abstractmethod
    def _control_regularization(self) -> float:
        """Returns the control effort weight."""

    def _solve(
        self,
        initial_state: State,
        prediction_model: PredictionModel,
        horizon: int,
        initial_controls: np.ndarray | None,
        **kwargs: np.ndarray,
    ) -> Result:
        """Solves the convex program.

        Args:
            initial_state: Initial state.
            prediction_model: Linearized model at the current state.
            horizon: Number of steps.
            initial_controls: Initial controls or None to start from zero.
            **kwargs: Agent-specific inputs passed to the solver.

        Returns:
            The solver result. Returns the fallback or zero controls on failure.
        """
        time_step = self.engagement_config.mpc_config.mpc_time_step
        basis = casadi.DM(prediction_model.basis_matrix())
        acceleration_bias = casadi.DM(prediction_model.acceleration_bias)
        max_forward_acceleration = prediction_model.max_forward_acceleration
        max_normal_accelerations = prediction_model.max_normal_accelerations(
            horizon, time_step)

        optimizer = casadi.Opti()
        controls = optimizer.variable(3, horizon)
        positions = [casadi.DM(initial_state.position)]
        velocities = [casadi.DM(initial_state.velocity)]
        for step in range(horizon):
            acceleration = acceleration_bias + basis @ controls[:, step]
            velocities.append(velocities[step] + time_step * acceleration)
            positions.append(positions[step] + time_step * velocities[step + 1])

        cost = self._objective(optimizer, positions, velocities, horizon,
                               **kwargs)
        cost += self._control_regularization() * casadi.sumsqr(controls)
        optimizer.minimize(cost)

        for step in range(horizon):
            if max_forward_acceleration > 0:
                optimizer.subject_to(controls[0,
                                              step] <= max_forward_acceleration)
                optimizer.subject_to(
                    controls[0, step] >= -max_forward_acceleration)
            else:
                optimizer.subject_to(controls[0, step] == 0)
            optimizer.subject_to(
                controls[1, step]**2 +
                controls[2, step]**2 <= max_normal_accelerations[step]**2)

        optimizer.solver(
            "ipopt",
            {"print_time": False},
            {
                "print_level": 0,
                "sb": "yes",
            },
        )
        if initial_controls is not None:
            optimizer.set_initial(controls, initial_controls.T)
        solved = True
        try:
            solution = optimizer.solve()
            solved_controls = np.array(solution.value(controls)).reshape(
                3, horizon).T
        except RuntimeError as err:
            logging.info("Failed to solve the convex MPC: %s.", err)
            solved = False
            solved_controls = (np.zeros(
                (horizon, 3)) if initial_controls is None else initial_controls)
        positions, velocities = prediction_model.trajectory(
            initial_state, solved_controls, time_step)
        return solved_controls, positions, velocities, solved


class InterceptorMpc(ConvexMpc):
    """The interceptor MPC minimizes the miss to the predicted threat
    path.
    """

    def solve(self,
              initial_state: State,
              prediction_model: PredictionModel,
              threat_positions: np.ndarray,
              horizon: int,
              initial_controls: np.ndarray | None = None) -> Result:
        """Solves the interceptor's quadratic problem.

        Args:
            initial_state: Initial state.
            prediction_model: Linearized model at the current state.
            threat_positions: Predicted threat positions.
            horizon: Number of steps.
            initial_controls: Initial controls or None to start from zero.

        Returns:
            The solver result minimizing the miss to the predicted threat path.
        """
        return self._solve(initial_state,
                           prediction_model,
                           horizon,
                           initial_controls,
                           threat_positions=threat_positions)

    def _objective(self, optimizer: casadi.Opti, positions: list[casadi.MX],
                   velocities: list[casadi.MX], horizon: int,
                   threat_positions: np.ndarray) -> casadi.MX:
        """Builds the interceptor's objective.

        Args:
            optimizer: Optimizer stack.
            positions: Positions for each step during the horizon.
            velocities: Velocities for each step during the horizon.
            horizon: Number of steps.
            threat_positions: Predicted threat positions.

        Returns:
            The cost expression to minimize.
        """
        cost = 0
        for step in range(1, horizon + 1):
            weight = (self.engagement_config.mpc_config.interceptor_config.
                      terminal_weight
                      if step == horizon else self.engagement_config.mpc_config.
                      interceptor_config.running_weight)
            offset = positions[step] - casadi.DM(threat_positions[step])
            cost += weight * casadi.dot(offset, offset)
        return cost

    def _control_regularization(self) -> float:
        """Returns the control effort weight."""
        return self.engagement_config.mpc_config.interceptor_config.control_regularization


class ThreatMpc(ConvexMpc):
    """The threat MPC maximizes separation from the pursuer.

    Attributes:
        threat: Threat configuration.
    """

    def __init__(self, threat: Threat,
                 engagement_config: EngagementConfig) -> None:
        super().__init__(engagement_config)
        self.threat = threat

    def solve(self,
              initial_state: State,
              prediction_model: PredictionModel,
              pursuer_away_directions: np.ndarray,
              pursuer_forward_directions: np.ndarray,
              horizon: int,
              initial_controls: np.ndarray | None = None) -> Result:
        """Solves the threat's quadratic problem.

        Args:
            initial_state: Initial state.
            prediction_model: Linearized model at the current state.
            pursuer_away_directions: Directions away from the pursuer.
            pursuer_forward_directions: Predicted pursuer forward directions.
            horizon: Number of steps.
            initial_controls: Initial controls or None to start from zero.

        Returns:
            The solver result maximizing the separation from the pursuer.
        """
        return self._solve(
            initial_state,
            prediction_model,
            horizon,
            initial_controls,
            pursuer_away_directions=pursuer_away_directions,
            pursuer_forward_directions=pursuer_forward_directions)

    def _objective(self, optimizer: casadi.Opti, positions: list[casadi.MX],
                   velocities: list[casadi.MX], horizon: int,
                   pursuer_away_directions: np.ndarray,
                   pursuer_forward_directions: np.ndarray) -> casadi.MX:
        """Builds the threat's objective.

        Args:
            optimizer: The optimizer stack.
            positions: Positions for each step during the horizon.
            velocities: Velocities for each step during the horizon.
            horizon: Number of steps.
            pursuer_away_directions: Directions away from the pursuer.
            pursuer_forward_directions: Predicted pursuer forward directions.

        Returns:
            The cost expression to minimize.
        """
        max_speed = self.threat.max_speed()
        cost = 0
        for step in range(1, horizon + 1):
            cost -= self.engagement_config.mpc_config.threat_config.evade_range_weight * casadi.dot(
                positions[step], casadi.DM(pursuer_away_directions[step]))
            alignment = casadi.dot(velocities[step],
                                   casadi.DM(pursuer_forward_directions[step]))
            cost += self.engagement_config.mpc_config.threat_config.evade_orthogonal_weight * alignment**2
            if max_speed is not None:
                optimizer.subject_to(
                    casadi.dot(velocities[step], velocities[step]) <= max_speed
                    **2)
        return cost

    def _control_regularization(self) -> float:
        """Returns the control effort weight."""
        return self.engagement_config.mpc_config.threat_config.control_regularization
