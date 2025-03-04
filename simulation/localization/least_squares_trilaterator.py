"""The least-squares trilaterator class uses least-squares to trilaterate the
target position.
"""

import numpy as np

from simulation.localization.trilaterator import Trilaterator
from utils.coordinates import CartesianCoordinates


class LeastSquaresTrilaterator(Trilaterator):
    """Least-squarestTrilaterator interface."""

    def __init__(self, positions: list[CartesianCoordinates],
                 ranges: np.ndarray | list[float]) -> None:
        super().__init__(positions, ranges)

    def trilaterate(self) -> CartesianCoordinates:
        """Trilaterate the target position.

        Returns:
            The estimated target position.
        """
        W = np.zeros((self.num_sensors() - 1, 3))
        b = np.zeros(self.num_sensors() - 1)
        reference_position_coordinates = self.positions[0].coordinates()
        reference_distance = np.linalg.norm(reference_position_coordinates)
        reference_range = self.ranges[0]
        for index, (position, range) in enumerate(
                zip(
                    self.positions[1:],
                    self.ranges[1:],
                )):
            position_coordinates = position.coordinates()
            distance = np.linalg.norm(position_coordinates)
            W[index] = position_coordinates - reference_position_coordinates
            b[index] = (1 / 2 * (reference_range**2 - range**2 -
                                 reference_distance**2 + distance**2))
        return np.linalg.lstsq(W, b)[0]
