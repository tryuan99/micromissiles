"""Shared flight equations and integration for interceptors and threats."""

import casadi
import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.proto.static_config_pb2 import StaticConfig
from simulation.swarm.reachability.state import State


class Agent:
    """Base agent equations with shared numerical and symbolic integration.

    Attributes:
        static_config: The agent's static configuration.
    """

    def __init__(self, static_config: StaticConfig) -> None:
        self.static_config = static_config

        self._intervals: dict[tuple[float, ...], tuple[casadi.Function,
                                                       casadi.Function]] = {}
        state = State(casadi.SX.sym("state", State.SIZE))
        command = casadi.SX.sym("command", 3)
        time_step = casadi.SX.sym("time_step")
        acceleration = self._total_acceleration(state, command)
        next_velocity = state.velocity + time_step * acceleration
        next_rotation = constants.casadi_align_rotation(
            state.rotation,
            state.velocity,
            time_step,
        )
        next_state = State.from_components(
            state.position + time_step * next_velocity,
            next_velocity,
            next_rotation,
        )
        self._step_function = casadi.Function(
            "flight_step",
            [state.vector, command, time_step],
            [next_state.vector],
        )

    def max_forward_acceleration(self) -> float:
        """Returns the maximum forward acceleration in m/s^2."""
        return (
            self.static_config.acceleration_config.max_forward_acceleration *
            constants.GRAVITY)

    def max_normal_acceleration(
        self,
        speed: float | casadi.SX | casadi.MX,
    ) -> float | casadi.SX | casadi.MX:
        """Returns the normal acceleration limit in m/s^2 at the supplied speed.

        Args:
            speed: Speed in m/s.
        """
        return (constants.GRAVITY * self.static_config.acceleration_config.
                max_reference_normal_acceleration /
                self.static_config.acceleration_config.reference_speed**2 *
                speed**2)

    def max_speed(self) -> float:
        """Returns the highest power-table speed in m/s."""
        return max(entry.speed for entry in self.static_config.power_table)

    def step(
        self,
        state: State,
        acceleration: np.ndarray,
        time_step: float,
    ) -> State:
        """Returns the state after one semi-implicit Euler step.

        Args:
            state: Current position in meters and velocity in m/s.
            acceleration: Acceleration command in m/s^2 with shape (3,).
            time_step: Integration step in seconds.
        """
        return State(self._step_function(state.vector, acceleration, time_step))

    def interval(
        self,
        time_steps: tuple[float, ...],
    ) -> tuple[casadi.Function, casadi.Function]:
        """Returns the transition and Jacobian functions for an acceleration command.

        The returned tuple contains an integrated transition and a derivative
        function. Both accept a ten-component state and a three-component
        command in m/s^2. The transition returns the final state. The derivative
        function returns state and command Jacobians with shapes (10, 10) and
        (10, 3), respectively.

        Args:
            time_steps: A nonempty tuple of positive integration durations in
                seconds. The same command is held throughout these steps.
        """
        if time_steps not in self._intervals:
            state = State(casadi.MX.sym("state", State.SIZE))
            command = casadi.MX.sym("command", 3)
            path = self._step_function.mapaccum(len(time_steps))(
                state.vector,
                casadi.repmat(command, 1, len(time_steps)),
                casadi.DM(time_steps).T,
            )
            final = path[:, -1]
            transition = casadi.Function(
                "flight_interval",
                [state.vector, command],
                [final],
            )
            derivative = casadi.Function(
                "flight_jacobians",
                [state.vector, command],
                [
                    casadi.jacobian(final, state.vector),
                    casadi.jacobian(final, command),
                ],
            )
            self._intervals[time_steps] = transition, derivative
        return self._intervals[time_steps]

    def _total_acceleration(
        self,
        state: State,
        command: casadi.SX | casadi.MX,
    ) -> casadi.SX | casadi.MX:
        """Returns symbolic acceleration with shared forward and normal limits.

        Args:
            state: Flight state with position, velocity, and rotation.
            command: Acceleration command in m/s^2.
        """
        along = casadi.dot(command, state.forward) * state.forward
        normal = constants.casadi_project_off_axis(command, state.forward)
        forward_acceleration = constants.casadi_clamp_magnitude(
            along, self.max_forward_acceleration())
        normal_acceleration = constants.casadi_clamp_magnitude(
            normal, self.max_normal_acceleration(state.speed))
        return forward_acceleration + normal_acceleration
