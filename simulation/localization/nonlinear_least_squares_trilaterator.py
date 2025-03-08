"""The nonlinear least-squares trilaterator class uses nonlinear least-squares
to trilaterate the target position.
"""

import numpy as np
import scipy.optimize

from simulation.localization.trilaterator import Trilaterator
from utils.coordinates import CartesianCoordinates


class NonlinearLeastSquaresTrilaterator(Trilaterator):
    """Nonlinear least-squares trilaterator."""

    def __init__(
        self,
        positions: list[CartesianCoordinates],
        ranges: np.ndarray | list[float],
    ) -> None:
        super().__init__(positions, ranges)

    def trilaterate(self) -> CartesianCoordinates:
        """Trilaterate the target position.

        Returns:
            The estimated target position.
        """

        def calculate_residuals(
            x: np.ndarray,
            positions: np.ndarray,
            ranges: np.ndarray,
        ) -> np.ndarray:
            """Calculates the residuals for the given target position.

            Args:
                x: Target position.
                positions: Sensor positions.
                ranges: Range measurements for each sensor.

            Returns:
                The vector of residuals.
            """
            position_difference = x - positions
            return np.linalg.norm(position_difference, axis=1) - ranges

        # Run nonlinear least-squares.
        positions = np.array(
            [position.coordinates() for position in self.positions])
        x0 = np.mean(positions, axis=0)
        result = scipy.optimize.least_squares(calculate_residuals,
                                              x0,
                                              args=(positions, self.ranges))
        return result.x
