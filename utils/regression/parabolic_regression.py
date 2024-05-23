"""The parabolic regression class performs a parabolic interpolation on the
given data.

y = ax^2 + bx + c
"""

import numpy as np

from utils.regression.polynomial_regression import PolynomialRegression


class ParabolicRegression(PolynomialRegression):
    """Performs a parabolic interpolation."""

    def __init__(self, x: np.ndarray, y: np.ndarray):
        super().__init__(x, y, 2)

    @property
    def a(self) -> float:
        """Quadratic coefficient of the parabolic regression."""
        return self.coefficients[2]

    @property
    def b(self) -> float:
        """Linear coefficient of the parabolic regression."""
        return self.coefficients[1]

    @property
    def c(self) -> float:
        """y-intercept of the parabolic regression."""
        return self.coefficients[0]

    def peak(self) -> tuple[float, float]:
        """Returns the x and y-values of the vertex of the parabola."""
        peak_x = -self.b / (2 * self.a)
        return peak_x, self.evaluate(peak_x)
