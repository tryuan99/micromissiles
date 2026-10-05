"""The agent interface is an interface for interceptors and threats."""

from abc import ABC, abstractmethod
from collections.abc import Callable

import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.model import PredictionModel
from simulation.swarm.reachability.proto.static_config_pb2 import StaticConfig
from simulation.swarm.reachability.state import State


class Agent(ABC):
    """Interface for an agent.

    Attributes:
        static_config: The agent's static configuration.
    """

    def __init__(self, static_config: StaticConfig) -> None:
        self.static_config = static_config

    def max_forward_acceleration(self) -> float:
        """Returns the maximum forward acceleration in m/s^2."""
        return (
            self.static_config.acceleration_config.max_forward_acceleration *
            constants.GRAVITY)

    def max_normal_acceleration_coefficient(self) -> float:
        """Returns the coefficient of the maximum speed-squared normal acceleration."""
        acceleration_config = self.static_config.acceleration_config
        return (acceleration_config.max_reference_normal_acceleration *
                constants.GRAVITY / acceleration_config.reference_speed**2)

    def max_normal_acceleration(self, speed: float) -> float:
        """Returns the maximum speed-dependent normal acceleration in m/s^2.

        Args:
            speed: Speed in m/s.
        """
        return self.max_normal_acceleration_coefficient() * speed**2

    def max_speed(self) -> float | None:
        """Returns the power-table maximum speed."""
        speeds = [entry.speed for entry in self.static_config.power_table]
        return max(speeds) if speeds else None

    def limit_acceleration_input(
        self,
        acceleration: np.ndarray,
        forward: np.ndarray,
        speed: float,
    ) -> np.ndarray:
        """Returns the acceleration clamped to the maximum forward and normal
        accelerations.

        Args:
            acceleration: Acceleration in m/s^2.
            forward: Forward direction.
            speed: Speed in m/s.
        """
        forward_component = constants.clamp_magnitude(
            constants.project_onto_axis(acceleration, forward),
            self.max_forward_acceleration())
        normal_component = constants.clamp_magnitude(
            constants.project_off_axis(acceleration, forward),
            self.max_normal_acceleration(speed))
        return forward_component + normal_component

    @abstractmethod
    def total_acceleration(self, state: State,
                           acceleration: np.ndarray) -> np.ndarray:
        """Returns the total acceleration for the applied acceleration command.

        Args:
            state: Agent state.
            acceleration: Acceleration command in m/s^2.
        """

    @abstractmethod
    def prediction_model(self, state: State) -> PredictionModel:
        """Returns the linearized prediction model at the state.

        Args:
            state: Agent state.
        """

    def _prediction_model(
        self,
        state: State,
        acceleration_bias: np.ndarray,
        max_forward_acceleration: float,
        speed_profile: Callable[[np.ndarray], np.ndarray],
    ) -> PredictionModel:
        """Returns the model at the given state.

        Args:
            state: Agent state.
            acceleration_bias: Acceleration bias in m/s^2.
            max_forward_acceleration: Maximum forward acceleration in m/s^2.
            speed_profile: Predicted speed in m/s as a function of the elapsed
                time in seconds.
        """
        first_normal, second_normal = constants.normal_basis(state.forward)
        return PredictionModel(
            forward=state.forward,
            first_normal=first_normal,
            second_normal=second_normal,
            acceleration_bias=acceleration_bias,
            max_forward_acceleration=max_forward_acceleration,
            max_normal_acceleration_coefficient=self.
            max_normal_acceleration_coefficient(),
            speed_profile=speed_profile,
        )

    def step(
        self,
        state: State,
        acceleration: np.ndarray,
        time_step: float,
    ) -> State:
        """Returns the next state after one semi-implicit Euler step.

        Args:
            state: Agent state.
            acceleration: Acceleration command in m/s^2.
            time_step: Time step in seconds.
        """
        acceleration = self.total_acceleration(state, acceleration)
        velocity = state.velocity + time_step * acceleration
        position = state.position + time_step * velocity
        return State(position=position, velocity=velocity)
