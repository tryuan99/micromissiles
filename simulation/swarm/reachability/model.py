"""The prediction model is the linearized per-replan model consumed by the
convex MPC.
"""

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
    speed: float
    drag: float

    def basis_matrix(self) -> np.ndarray:
        """Returns the 3x3 matrix whose columns are the forward and normal axes."""
        return np.column_stack([
            self.forward,
            self.first_normal,
            self.second_normal,
        ])

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
        predicted_speeds = np.maximum(
            self.speed - self.drag * time_step * np.arange(horizon), 0.0)
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
        """
        accelerations = controls @ self.basis_matrix().T + self.acceleration_bias
        velocities = np.vstack([
            initial_state.velocity, initial_state.velocity +
            time_step * np.cumsum(accelerations, axis=0)
        ])
        positions = np.vstack([
            initial_state.position, initial_state.position +
            time_step * np.cumsum(velocities[1:], axis=0)
        ])
        return positions, velocities
