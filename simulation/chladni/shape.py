"""The shape classes represent different shapes centered at the origin."""

from abc import ABC, abstractmethod

import numpy as np


class Shape(ABC):
    """Interface for a shape.

    Attributes:
        bounding_box: Bounding box (x_min, x_max, y_min, y_max) in m.
    """

    def __init__(
        self,
        bounding_box: tuple[float, float, float, float],
    ) -> None:
        self.bounding_box = bounding_box

    @abstractmethod
    def contains(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Returns whether the points lie inside the shape.

        Args:
            x: x-coordinates in m.
            y: y-coordinates in m.
        """


class Circle(Shape):
    """Circle with the given diameter in m.

    Attributes:
        radius: Radius in m.
    """

    def __init__(self, diameter: float) -> None:
        radius = diameter / 2
        super().__init__((-radius, radius, -radius, radius))
        self.radius = radius

    def contains(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Returns whether the points lie inside the shape.

        Args:
            x: x-coordinates in m.
            y: y-coordinates in m.
        """
        return (x / self.radius)**2 + (y / self.radius)**2 <= 1


class Rectangle(Shape):
    """Rectangle.

    Attributes:
        width: Side length along x in m.
        height: Side length along y in m.
    """

    def __init__(self, width: float, height: float) -> None:
        super().__init__((-width / 2, width / 2, -height / 2, height / 2))
        self.width = width
        self.height = height

    def contains(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Returns whether the points lie inside the shape.

        Args:
            x: x-coordinates in m.
            y: y-coordinates in m.
        """
        return (np.abs(x) <= self.width / 2) & (np.abs(y) <= self.height / 2)


class Square(Rectangle):
    """Square with the given side length in m."""

    def __init__(self, side_length: float) -> None:
        super().__init__(side_length, side_length)


class ShapeFactory:
    """Shape factory."""

    @staticmethod
    def create(type: str, *args: float) -> Shape:
        """Creates a shape.

        Args:
            type: Shape type.
            *args: Arguments to construct the shape.

        Raises:
            ValueError: If the shape name is unknown.
        """
        if type not in SHAPES:
            raise ValueError(f"Invalid shape type: {type}.")
        return SHAPES[type](*args)


# Shape classes by name.
SHAPES: dict[str, type[Shape]] = {
    "circle": Circle,
    "rectangle": Rectangle,
    "square": Square,
}
