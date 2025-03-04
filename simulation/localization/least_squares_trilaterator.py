"""The least-squares trilaterator class uses least-squares to trilaterate the
target position.
"""

import itertools

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
        W = np.zeros((self.num_sensors() * (self.num_sensors() - 1) // 2, 3))
        b = np.zeros(self.num_sensors() * (self.num_sensors() - 1) // 2)
        for index, (i, j) in enumerate(
                itertools.combinations(range(self.num_sensors()), 2)):
            position_i = self.positions[i]
            position_j = self.positions[j]
            range_i = self.ranges[i]
            range_j = self.ranges[j]
            distance_i = np.linalg.norm(position_i.coordinates())
            distance_j = np.linalg.norm(position_j.coordinates())
            W[index] = position_j.coordinates() - position_i.coordinates()
            b[index] = (
                1 / 2 *
                (range_i**2 - range_j**2 - distance_i**2 + distance_j**2))
        return np.linalg.lstsq(W, b)[0]
