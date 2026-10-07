"""Nonlinear flight prediction and local linearization for convex planning."""

from collections.abc import Iterator

import casadi
import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.agent import Agent
from simulation.swarm.reachability.state import State


class PredictionModel:
    """Predicts motion using the shared flight equations.

    Controls use the initial flight basis. The shared equations project
    the acceleration commands onto the agent's coordinate system at every
    integration step.

    Attributes:
        agent: Agent providing shared acceleration, integration, and
            derivatives.
        plant_time_step: Maximum integration step in seconds.
        control_time_step: Control period in seconds, or None to use each
            prediction interval as the control period.
        forward: Initial body forward direction with shape (3,).
        basis: Matrix mapping local commands to global coordinates, with shape
            (3, 3). Columns are the initial forward and two normal directions.
        max_forward_acceleration: Available commanded forward acceleration
            in m/s^2.
    """

    # Margin acceleration to prevent full saturation.
    ACCELERATION_MARGIN = 0.99

    def __init__(
        self,
        agent: Agent,
        state: State,
        plant_time_step: float,
        control_time_step: float | None = None,
    ) -> None:
        self.agent = agent
        self.plant_time_step = plant_time_step
        self.control_time_step = control_time_step
        self.forward = state.forward
        self.basis = np.column_stack(
            [self.forward, *constants.normal_basis(self.forward)])
        self.max_forward_acceleration = agent.max_forward_acceleration()

    def max_normal_accelerations(self, velocities: np.ndarray) -> np.ndarray:
        """Returns normal acceleration limits along the predicted trajectory.

        Args:
            velocities: Global velocities in m/s with shape (samples, 3).
        """
        return np.array([
            self.agent.max_normal_acceleration(np.linalg.norm(velocity))
            for velocity in velocities
        ])

    def intervals(
        self,
        horizon: int,
        time_step: float,
    ) -> Iterator[tuple[casadi.Function, casadi.Function]]:
        """Splits prediction intervals at plant and control-period boundaries.

        Args:
            horizon: Number of prediction intervals to generate.
            time_step: Duration of each prediction interval in seconds.

        Yields:
            A pair of CasADi functions for each interval: the integrated state
            transition and its state and acceleration command Jacobians.
        """
        control_time_step = (time_step if self.control_time_step is None else
                             self.control_time_step)
        for step in range(horizon):
            start_time = step * time_step
            end_time = (step + 1) * time_step
            time_steps = []
            while start_time < end_time:
                control_index = np.floor(start_time / control_time_step)
                control_boundary = (control_index + 1) * control_time_step
                if control_boundary <= start_time:
                    control_boundary = (control_index + 2) * control_time_step
                duration = min(self.plant_time_step, end_time - start_time,
                               control_boundary - start_time)
                time_steps.append(duration)
                start_time += duration
            yield self.agent.interval(tuple(time_steps))

    def trajectory(
        self,
        initial_state: State,
        controls: np.ndarray,
        time_step: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Predicts a trajectory using the nonlinear flight equations.

        Args:
            initial_state: Initial position in meters and velocity in m/s.
            controls: Local acceleration commands in m/s^2 with shape (horizon,
                3).
            time_step: Duration of each prediction interval in seconds.

        Returns:
            Positions in meters and velocities in m/s, each with shape
            (horizon + 1, 3), including the initial state.
        """
        state = initial_state
        states = [state]
        commands = controls @ self.basis.T
        intervals = self.intervals(len(controls), time_step)
        for command, (transition, _) in zip(commands, intervals):
            state = State(transition(state.vector, command))
            states.append(state)
        positions = np.array([state.position for state in states])
        velocities = np.array([state.velocity for state in states])
        return positions, velocities

    def reference_controls(
        self,
        initial_state: State,
        controls: np.ndarray,
        time_step: float,
    ) -> np.ndarray:
        """Limits initial acceleration commands along the predicted trajectory.

        Args:
            initial_state: Initial state of the reference trajectory.
            controls: Local acceleration commands in m/s^2 with shape (horizon,
                3).
            time_step: Duration of each prediction interval in seconds.

        Returns:
            A copy of controls with normal and forward components limited along
            the reference trajectory, retaining shape (horizon, 3).
        """
        reference = np.array(controls, dtype=float, copy=True)
        state = initial_state
        intervals = self.intervals(len(reference), time_step)
        for step, (transition, _) in enumerate(intervals):
            maximum = self.agent.max_normal_acceleration(state.speed)
            magnitude = np.linalg.norm(reference[step, 1:])
            if magnitude > self.ACCELERATION_MARGIN * maximum:
                reference[step, 1:] *= (self.ACCELERATION_MARGIN * maximum /
                                        magnitude)
            reference[step, 0] = np.clip(reference[step, 0],
                                         -self.max_forward_acceleration,
                                         self.max_forward_acceleration)
            command = self.basis @ reference[step]
            state = State(transition(state.vector, command))
        return reference

    def linearize(
        self,
        initial_state: State,
        controls: np.ndarray,
        time_step: float,
    ) -> tuple[list[State], np.ndarray, np.ndarray, np.ndarray]:
        """Returns nonlinear reference states and affine transition matrices.

        The approximation is x[k+1] = A[k] x[k] + B[k] u[k] + c[k].
        Trajectory prediction uses the full flight equations.

        State Jacobians have shape (horizon, 10, 10), command Jacobians
        (horizon, 10, 3), and offsets (horizon, 10).

        Args:
            initial_state: State at the beginning of the reference trajectory.
            controls: Local acceleration commands in m/s^2 with shape (horizon,
                3).
            time_step: Duration of each prediction interval in seconds.
        """
        state = initial_state
        states = [state]
        state_jacobians, command_jacobians, offsets = [], [], []
        for control, (transition, derivative) in zip(
                controls, self.intervals(len(controls), time_step)):
            command = self.basis @ control
            state_jacobian, global_command_jacobian = derivative(
                state.vector, command)
            state_jacobian = np.array(state_jacobian)
            command_jacobian = np.array(global_command_jacobian) @ self.basis
            next_state = State(transition(state.vector, command))
            state_jacobians.append(state_jacobian)
            command_jacobians.append(command_jacobian)
            offsets.append(next_state.to_array() -
                           state_jacobian @ state.to_array() -
                           command_jacobian @ control)
            states.append(next_state)
            state = next_state
        return (
            states,
            np.array(state_jacobians),
            np.array(command_jacobians),
            np.array(offsets),
        )
