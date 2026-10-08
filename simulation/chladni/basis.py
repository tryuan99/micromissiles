"""This file contains 2D basis functions defined over a bounding box."""

import numpy as np


class LegendreBasis2D:
    """2D basis functions P_i(x) * P_j(y) made from Legendre polynomials.

    x and y are rescaled, so that the bounding box spans -1 to 1.

    Attributes:
        bounding_box: Bounding box (x_min, x_max, y_min, y_max) in m.
        degree: Highest polynomial degree in each direction.
    """

    def __init__(self, bounding_box: tuple[float, float, float, float],
                 degree: int) -> None:
        self.bounding_box = bounding_box
        self.degree = degree

    def evaluate(
        self,
        x: np.ndarray | float,
        y: np.ndarray | float,
        x_order: int = 0,
        y_order: int = 0,
    ) -> np.ndarray:
        """Returns a derivative of the functions at the points.

        Args:
            x: x-coordinates in m, flattened.
            y: y-coordinates in m, flattened.
            x_order: Number of derivatives in x.
            y_order: Number of derivatives in y.

        Returns:
            The derivative with one row per point and one column per function.
        """
        x_min, x_max, y_min, y_max = self.bounding_box
        half_width, half_height = 0.5 * (x_max - x_min), 0.5 * (y_max - y_min)
        x = np.ravel(x)
        y = np.ravel(y)
        # Due to the 1/half_width or 1/half_height rescaling, each derivative
        # needs to be scaled by 1/half_width or 1/half_height.
        legendre_x = self._legendre_1d(
            (x - 0.5 *
             (x_min + x_max)) / half_width, x_order) / half_width**x_order
        legendre_y = self._legendre_1d(
            (y - 0.5 *
             (y_min + y_max)) / half_height, y_order) / half_height**y_order
        # Build the 2D basis at every point.
        return (legendre_x[:, :, None] * legendre_y[:, None, :]).reshape(
            len(x), -1)

    def _legendre_1d(self, coordinates: np.ndarray, order: int) -> np.ndarray:
        """Returns a derivative of the Legendre polynomials at the coordinates.

        Args:
            coordinates: Rescaled coordinates between -1 and 1.
            order: Number of derivatives.

        Returns:
            The derivative with one row per coordinate and one column per
            polynomial degree, from 0 to the maximum degree.
        """
        values = np.polynomial.legendre.legvander(coordinates, self.degree)
        # Matrix that differentiates a polynomial given by its coefficients.
        derivative_matrix = np.zeros((self.degree + 1, self.degree + 1))
        # Assemble the derivative matrix.
        for polynomial_degree in range(1, self.degree + 1):
            coefficients = np.polynomial.legendre.legder(
                np.eye(self.degree + 1)[polynomial_degree])
            derivative_matrix[:len(coefficients),
                              polynomial_degree] = coefficients
        # Apply the derivative matrix up to the given derivative order.
        for _ in range(order):
            values = values @ derivative_matrix
        return values
