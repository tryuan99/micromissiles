"""The coordinates classes encapsulate coordinates and transformations between them.

The radar uses the following coordinate system:
  y ^
    |     ^ x
    |    /
    |   /
    |  /
    | /
    |/
    -------------> z

The target is in the positive z-direction.
The antennas are positioned in the x-y plane at z=0, where "horizontal"
denotes the x-direction and "vertical" denotes the y-direction.

We use spherical coordinates for the azimuth and elevation.
The azimuth denotes the angle from the projection of the target onto the x-z
plane to the z-axis, where a positive azimuth denotes a negative x-coordinate
and a negative azimuth denotes a positive x-coordinate.
    azimuth = arctan(-x / z)
The elevation denotes the angle from the target to its projection onto the
x-z plane, where a positive elevation denotes a positive y-coordinate
and a negative elevation denotes a negative y-coordinate.
    elevation = arctan(y / sqrt(x^2 + z^2))
Converting to Cartesian coordinates:
    x = -tan(azimuth) * z = -r * sin(azimuth) * cos(elevation)
    y = tan(elevation) * sqrt(x^2 + z^2) = r * sin(elevation)
    z = r * cos(azimuth) * cos(elevation)
"""

from abc import ABC, abstractmethod

import numpy as np


class Coordinates(ABC):
    """Interface for coordinates."""

    @property
    @abstractmethod
    def coordinates(self) -> np.ndarray:
        """Returns the coordinates."""


class CartesianCoordinates(Coordinates):
    """Represents Cartesian coordinates."""

    def __init__(self, x: float | np.ndarray, y: float | np.ndarray,
                 z: float | np.ndarray):
        self.x = x
        self.y = y
        self.z = z

    @property
    def coordinates(self) -> np.ndarray:
        """Returns the coordinates."""
        return np.array([self.x, self.y, self.z])

    def transform_to_polar(self) -> "PolarCoordinates":
        """Transforms the coordinates to polar coordinates.

        Returns:
            Polar coordinates.
        """
        r = np.sqrt(self.x**2 + self.y**2 + self.z**2)
        theta = np.arctan(-self.x / self.z)
        phi = np.arctan(self.y / np.sqrt(self.x**2 + self.z**2))
        return PolarCoordinates(r, theta, phi)


class PolarCoordinates(Coordinates):
    """Represents polar coordinates."""

    def __init__(self, r: float | np.ndarray, theta: float | np.ndarray,
                 phi: float | np.ndarray):
        self.r = r
        self.theta = theta  # Azimuth.
        self.phi = phi  # Elevation.

    @property
    def coordinates(self) -> np.ndarray:
        """Returns the coordinates."""
        return np.array([self.r, self.theta, self.phi])

    def transform_to_cartesian(self) -> "CartesianCoordinates":
        """Transforms the coordinates to Cartesian coordinates.

        Returns:
            Cartesian coordinates.
        """
        x = -self.r * np.sin(self.theta) * np.cos(self.phi)
        y = self.r * np.sin(self.phi)
        z = self.r * np.cos(self.theta) * np.cos(self.phi)
        return CartesianCoordinates(x, y, z)
