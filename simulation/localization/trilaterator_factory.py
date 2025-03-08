"""The trilaterator factory class instantiates various trilaterators."""

import numpy as np

from simulation.localization.least_squares_trilaterator import \
    LeastSquaresTrilaterator
from simulation.localization.nonlinear_least_squares_trilaterator import \
    NonlinearLeastSquaresTrilaterator
from simulation.localization.trilaterator import Trilaterator
from utils.coordinates import CartesianCoordinates

# List of trilaterators.
TRILATERATORS = {
    "least_squares": LeastSquaresTrilaterator,
    "nonlinear_least_squares": NonlinearLeastSquaresTrilaterator,
}


class TrilateratorFactory:
    """Trilaterator factory."""

    @staticmethod
    def create_trilaterator(
        type: str,
        positions: list[CartesianCoordinates],
        ranges: np.ndarray | list[float],
    ) -> Trilaterator:
        """Creates a trilaterator according to the type.

        Args:
            type: Trilaterator type string.
            positions: Sensor positions.
            ranges: Range measurements for each sensor.

        Returns:
            The trilaterator instance.
        """
        if type in TRILATERATORS:
            return TRILATERATORS[type](positions, ranges)
        raise ValueError(f"Invalid trilaterator type: {type}.")
