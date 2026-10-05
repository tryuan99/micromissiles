"""The prediction model is the linearized per-replan model consumed by the
convex MPC.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from simulation.swarm.reachability.state import State


@dataclass
class PredictionModel:
    """Linearized per-replan model consumed by the convex MPC."""

    forward: np.ndarray
    first_normal: np.ndarray
    second_normal: np.ndarray
    acceleration_bias: np.ndarray
    max_forward_acceleration: float
    # The normal acceleration is limited to the coefficient multiplied by the
    # speed squared.
    max_normal_acceleration_coefficient: float
    # Predicted speed in m/s as a function of the elapsed time in seconds.
    speed_profile: Callable[[np.ndarray], np.ndarray]

    def basis_matrix(self) -> np.ndarray:
        """Returns the 3x3 matrix whose columns are the forward and normal axes."""
        return np.column_stack([
            self.forward,
            self.first_normal,
            self.second_normal,
        ])

    def predicted_speeds(self, horizon: int, time_step: float) -> np.ndarray:
        """Returns the predicted speed at each of the horizon + 1 steps.

        Args:
            horizon: Number of steps in the horizon.
            time_step: Time step in seconds.

        Returns:
            The predicted speeds in m/s with shape (horizon + 1,).
        """
        return self.speed_profile(time_step * np.arange(horizon + 1))

    def acceleration_biases(self, horizon: int, time_step: float) -> np.ndarray:
        """Returns the per-step acceleration bias, including the forward
        acceleration from the predicted speed change.

        Args:
            horizon: Number of steps in the horizon.
            time_step: Time step in seconds.

        Returns:
            The acceleration biases in m/s^2 with shape (horizon, 3).
        """
        forward_accelerations = np.diff(
            self.predicted_speeds(horizon, time_step)) / time_step
        return (self.acceleration_bias +
                forward_accelerations[:, None] * self.forward)

    def max_normal_accelerations(
        self,
        horizon: int,
        time_step: float,
    ) -> np.ndarray:
        """Returns the per-step maximum normal acceleration along the predicted
        speed.

        The normal acceleration is floored above zero, so the QCQP constraints
        keep a strict interior even if the predicted speed decays to zero.

        Args:
            horizon: Number of steps in the horizon.
            time_step: Time step in seconds.

        Returns:
            The per-step maximum normal acceleration.
        """
        predicted_speeds = self.predicted_speeds(horizon, time_step)[:-1]
        return np.maximum(
            self.max_normal_acceleration_coefficient * predicted_speeds**2,
            1e-3)

    def trajectory(
        self,
        initial_state: State,
        controls: np.ndarray,
        time_step: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Returns the (positions, velocities) over the horizon for the given
        controls.

        Integrates the linearized model with semi-implicit Euler, matching the
        plant.

        Args:
            initial_state: Initial state.
            controls: Controls in the local coordinates with shape (horizon, 3).
            time_step: Time step in seconds.

        Returns:
            The positions and velocities, each with shape (horizon + 1, 3).
        """
        accelerations = (controls @ self.basis_matrix().T +
                         self.acceleration_biases(len(controls), time_step))
        velocities = np.vstack([
            initial_state.velocity, initial_state.velocity +
            time_step * np.cumsum(accelerations, axis=0)
        ])
        positions = np.vstack([
            initial_state.position, initial_state.position +
            time_step * np.cumsum(velocities[1:], axis=0)
        ])
        return positions, velocities
