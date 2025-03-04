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

    def __init__(self, positions: list[CartesianCoordinates],
                 ranges: np.ndarray | list[float]) -> None:
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
