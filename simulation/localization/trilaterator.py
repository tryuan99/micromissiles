"""The trilaterator class is an interface for trilaterating the 3D position of
a target.
"""

from abc import ABC, abstractmethod

import numpy as np

from utils.coordinates import CartesianCoordinates


class Trilaterator(ABC):
    """Trilaterator interface.

    Attributes:
        positions: Sensor positions.
        ranges: Range measurements for each sensor.
    """

    def __init__(
        self,
        positions: list[CartesianCoordinates],
        ranges: np.ndarray | list[float],
    ) -> None:
        self.positions = positions
        self.ranges = ranges

    def num_sensors(self) -> int:
        """Returns the number of sensors."""
        return len(self.positions)

    @abstractmethod
    def trilaterate(self) -> CartesianCoordinates:
        """Trilaterate the target position.

        Returns:
            The estimated target position.
        """

    def cramer_rao_lower_bound(
        self,
        position: np.ndarray,
        standard_deviations: np.ndarray,
    ) -> np.ndarray:
        """Returns the minimum covariance matrix of the estimated position
        according to the Cramér-Rao lower bound.

        Args:
            position: Target position.
            standard_deviations: Standard deviation of the range measurement
              noise.
        """
        positions_matrix = np.array(
            [position.coordinates() for position in self.positions])
        gradient = (position - positions_matrix) / self.ranges[:, np.newaxis]
        sigma_inv = np.diag(1 / standard_deviations**2)
        fisher_information_matrix = gradient.T @ sigma_inv @ gradient
        return np.linalg.inv(fisher_information_matrix)
