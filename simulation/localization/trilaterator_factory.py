"""The trilaterator factory class instantiates various trilaterators."""

from enum import Enum

import numpy as np

from simulation.localization.least_squares_trilaterator import \
    LeastSquaresTrilaterator
from simulation.localization.nonlinear_least_squares_trilaterator import \
    NonlinearLeastSquaresTrilaterator
from simulation.localization.trilaterator import Trilaterator
from utils.coordinates import CartesianCoordinates


# Trilaterator type enum.
class TrilateratorType(str, Enum):
    LEAST_SQUARES = "least_squares"
    NONLINEAR_LEAST_SQUARES = "nonlinear_least_squares"

    @classmethod
    def values(cls):
        """Returns a list of all enum values."""
        return list(cls._value2member_map_.keys())


# Map from trilaterator type to trilaterator class.
TRILATERATOR_MAP = {
    TrilateratorType.LEAST_SQUARES: LeastSquaresTrilaterator,
    TrilateratorType.NONLINEAR_LEAST_SQUARES: NonlinearLeastSquaresTrilaterator,
}


class TrilateratorFactory:
    """Trilaterator factory."""

    @staticmethod
    def create_trilaterator(
        type: TrilateratorType,
        positions: list[CartesianCoordinates],
        ranges: np.ndarray | list[float],
    ) -> Trilaterator:
        """Creates a trilaterator according to the type.

        Args:
            type: Trilaterator type.
            positions: Sensor positions.
            ranges: Range measurements for each sensor.

        Returns:
            The trilaterator instance.
        """
        return TRILATERATOR_MAP[type](positions, ranges)
