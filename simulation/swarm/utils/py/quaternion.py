"""The quaternion class represents a four-dimensional number, such that
q = s + v[0] * i + v[1] * j + v[2] * k.
"""

from typing import Self

import numpy as np


class Quaternion:
    """Quaternion.

    Attributes:
        s: The real quaternion part.
        v: The pure quaternion part.
    """

    def __init__(self, s: float, v: np.ndarray) -> None:
        self.s = s
        self.v = v

    def add(self, other: Self) -> Self:
        """Adds two quaternions.

        Args:
            other: Quaternion to add.

        Returns:
            The sum of two quaternions.
        """
        return Quaternion(s=self.s + other.s, v=self.v + other.v)

    def subtract(self, other: Self) -> Self:
        """Subtracts two quaternions.

        Args:
            other: Quaternion to subtract.

        Returns:
            The difference of two quaternions.
        """
        return self.add(other.multiply(-1))

    def multiply(self, other: Self | float) -> Self:
        """Multiplies two quaternions.

        Args:
            other: Quaternion or scalar to multiply.

        Returns:
            The product of two quaternions or a scalar and a quaternion.
        """
        if isinstance(other, Quaternion):
            return Quaternion(s=self.s * other.s - np.dot(self.v, other.v),
                              v=self.s * other.v + other.s * self.v +
                              np.cross(self.v, other.v))
        return Quaternion(s=self.s * other, v=self.v * other)

    def divide(self, other: float) -> Self:
        """Divides the quaternion by a scalar.

        Args:
            other: Scalar to divide.

        Returns:
            The quotient of a quaternion and a scalar.
        """
        return Quaternion(s=self.s / other, v=self.v / other)

    def norm(self) -> float:
        """Returns the norm of the quaternion."""
        return np.sqrt(self.s**2 + np.linalg.norm(self.v)**2)

    def conjugate(self) -> Self:
        """Returns the conjugate of the quaternion."""
        return Quaternion(s=self.s, v=-self.v)

    def inverse(self) -> Self:
        """Returns the inverse of the quaternion."""
        return self.conjugate().divide(self.norm()**2)

    def dot(self, other: Self) -> float:
        """Calculates the dot product with another quaternion.

        Args:
            other: Quaternion to dot.

        Returns:
            The dot product with another quaternion.
        """
        return self.s * other.s + np.dot(self.v, other.v)

    def rotate(self, other: "RotationQuaternion") -> Self:
        """Rotates the quaternion.

        Args:
            other: Rotation quaternion.

        Returns:
            The quaternion after rotation.
        """
        return other.multiply(self).multiply(other.inverse())


class PointQuaternion(Quaternion):
    """Point quaternion."""

    def __init__(self,
                 x: float = None,
                 y: float = None,
                 z: float = None,
                 coordinates: np.ndarray = None) -> None:
        if coordinates is None:
            coordinates = np.array([x, y, z])
        super().__init__(s=0, v=coordinates)


class RotationQuaternion(Quaternion):
    """Rotation quaternion."""

    def __init__(self,
                 theta: float,
                 x: float = None,
                 y: float = None,
                 z: float = None,
                 axis: np.ndarray = None) -> None:
        if axis is None:
            axis = np.array([x, y, z])

        # Normalize the axis.
        super().__init__(s=np.cos(theta / 2),
                         v=axis / np.linalg.norm(axis) * np.sin(theta / 2))

    def compose(self, other: Self) -> Self:
        """Composes two rotation quaternions.

        Args:
            other: Rotation quaternion to compose.

        Returns:
            The rotation quaternion corresponding to the composition.
        """
        return other.multiply(self)
