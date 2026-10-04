"""The threat classes represent a threat model."""

from abc import ABC

import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.agent import Agent
from simulation.swarm.reachability.model import PredictionModel
from simulation.swarm.reachability.state import State


class Threat(Agent, ABC):
    """Interface for a threat."""


class FixedWingThreat(Threat):
    """Fixed-wing threat model.

    The threat is not subject to drag or gravity, but has a maximum speed
    dependent on the power table.
    """

    def total_acceleration(
        self,
        state: State,
        acceleration: np.ndarray,
    ) -> np.ndarray:
        """Returns the total acceleration for the applied acceleration command.

        Args:
            state: Agent state.
            acceleration: Acceleration command in m/s^2.
        """

        forward_unit = state.forward
        controlled = self._apply_speed_control(acceleration, forward_unit,
                                               state.speed)
        return self.limit_acceleration_input(controlled, forward_unit,
                                             state.speed)

    def prediction_model(self, state: State) -> PredictionModel:
        """Returns the linearized prediction model at the state.

        Args:
            state: Agent state.
        """
        # The plant's speed control overrides any forward acceleration command.
        return self._prediction_model(
            state,
            acceleration_bias=self._apply_speed_control(
                np.zeros(3),
                state.forward,
                state.speed,
            ),
            drag=0.0,
            max_forward_acceleration=0.0,
        )

    def _apply_speed_control(
        self,
        acceleration: np.ndarray,
        forward: np.ndarray,
        speed: float,
    ) -> np.ndarray:
        """Returns the acceleration command with the forward component tracking
        the maximum speed.

        Args:
            acceleration: Acceleration in m/s^2.
            forward: Forward direction.
            speed: Speed in m/s.
        """
        desired_speed = self.max_speed()
        if desired_speed is None:
            return acceleration
        speed_error = desired_speed - speed
        normal_acceleration = constants.project_off_axis(acceleration, forward)
        if np.abs(speed_error) < constants.SPEED_ERROR_THRESHOLD:
            return normal_acceleration
        return normal_acceleration + (np.sign(speed_error) *
                                      self.max_forward_acceleration() * forward)
