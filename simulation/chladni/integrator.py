"""The integrator class integrates over the area of a shape."""

from collections.abc import Callable

import numpy as np

from simulation.chladni.shape import Shape

# Function of the x and y-coordinates in m that returns one row per point and
# one column per function.
Function = Callable[[np.ndarray, np.ndarray], np.ndarray]


class Integrator:
    """Approximates integrals over the area of a shape as weighted sums.

    The bounding box is split into a grid of cells. Each cell contributes its
    center point, weighted by how much of its area lies inside the shape.

    Attributes:
        x: x-coordinates of the cell centers in m.
        y: y-coordinates of the cell centers in m.
        weights: Area of each cell that lies inside the shape in m^2.
    """

    def __init__(
        self,
        shape: Shape,
        num_integration_points_per_side: int,
        num_coverage_points_per_side: int = 4,
    ) -> None:
        """Builds the cell centers and weights.

        Args:
            shape: Area to integrate over.
            num_integration_points_per_side: Number of cells, and hence
                integration points, along each side of the bounding box.
            num_coverage_points_per_side: Number of test points along each
                side of a cell to measure how much of the cell the shape
                covers.
        """
        # Calculate the integration cell grid.
        x_min, x_max, y_min, y_max = shape.bounding_box
        cell_width = (x_max - x_min) / num_integration_points_per_side
        cell_height = (y_max - y_min) / num_integration_points_per_side
        cell_indices = np.arange(num_integration_points_per_side) + 0.5
        cell_x, cell_y = np.meshgrid(
            x_min + cell_indices * cell_width,
            y_min + cell_indices * cell_height,
            indexing="ij",
        )

        # Calculate the test point coordinates of every cell.
        test_indices = (np.arange(num_coverage_points_per_side) +
                        0.5) / num_coverage_points_per_side - 0.5
        test_x = (cell_x[:, :, None, None] + test_indices[:, None] * cell_width)
        test_y = (cell_y[:, :, None, None] +
                  test_indices[None, :] * cell_height)
        coverage_fraction = shape.contains(test_x, test_y).mean(axis=(2, 3))

        # Calculate the coverage fraction of every cell.
        weights = coverage_fraction * cell_width * cell_height

        # Only keep the cells that actually cover some part of the shape.
        inside_shape = weights > 0
        self.x = cell_x[inside_shape]
        self.y = cell_y[inside_shape]
        self.weights = weights[inside_shape]

    def integrate(
        self,
        function: Function,
        other_function: Function | None = None,
    ) -> np.ndarray:
        """Returns the integral over the shape of each function, or of each
        product of two functions.

        Args:
            function: Functions to integrate, evaluated at the cell centers.
            other_function: Optional functions to multiply with.
        """
        values = function(self.x, self.y)
        if other_function is None:
            return self.weights @ values
        other_values = (values if other_function is function else
                        other_function(self.x, self.y))
        return (values * self.weights[:, None]).T @ other_values
