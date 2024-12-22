"""The coordinates classes encapsulate coordinates and transformations between them.

Radars and antennas use the following coordinate system:
  y ^
    |     ^ x
    |    /
    |   /
    |  /
    | /
    |/
    -------------> z

The target and boresight are in the positive z-direction.
The antennas are positioned in the x-y plane at z=0, where "horizontal"
denotes the x-direction and "vertical" denotes the y-direction.

We use spherical coordinates for the azimuth and elevation.
The azimuth denotes the angle from the projection of the target onto the x-z
plane to the z-axis, where a positive azimuth denotes a negative x-coordinate
and a negative azimuth denotes a positive x-coordinate.
    azimuth = arctan2(-x / z)
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

    @abstractmethod
    def coordinates(self) -> np.ndarray:
        """Returns the coordinates."""


class CartesianCoordinates(Coordinates):
    """Represents Cartesian coordinates.

    Attributes:
        x: x-coordinate.
        y: y-coordinate.
        z: z-coordinate.
    """

    def __init__(
        self,
        x: float | np.ndarray,
        y: float | np.ndarray,
        z: float | np.ndarray,
    ) -> None:
        self.x = x
        self.y = y
        self.z = z

    def coordinates(self) -> np.ndarray:
        """Returns the coordinates."""
        return np.array([self.x, self.y, self.z])

    def transform_to_spherical(self) -> "SphericalCoordinates":
        """Transforms the coordinates to spherical coordinates.

        Returns:
            The spherical coordinates.
        """
        range, azimuth, elevation = self.transform_to_spherical_arrays(
            self.x,
            self.y,
            self.z,
        )
        return SphericalCoordinates(range, azimuth, elevation)

    @staticmethod
    def transform_to_spherical_arrays(
        x: float | np.ndarray,
        y: float | np.ndarray,
        z: float | np.ndarray,
    ) -> tuple[float | np.ndarray, float | np.ndarray, float | np.ndarray]:
        """Transforms the coordinates to spherical coordinates.

        Returns:
            The spherical coordinates.
        """
        range = np.sqrt(x**2 + y**2 + z**2)
        azimuth = -np.arctan2(x, z)
        elevation = np.arctan(np.divide(y, np.sqrt(x**2 + z**2)))
        return range, azimuth, elevation


class SphericalCoordinates(Coordinates):
    """Represents spherical coordinates.

    Attributes:
        range: Distance from the origin.
        azimuth: Azimuth in radians.
        elevation: Elevation in radians.
    """

    def __init__(
        self,
        rnge: float | np.ndarray,
        azimuth: float | np.ndarray,
        elevation: float | np.ndarray,
    ) -> None:
        self.range = rnge
        self.azimuth = azimuth
        self.elevation = elevation

    def coordinates(self) -> np.ndarray:
        """Returns the coordinates."""
        return np.array([self.range, self.azimuth, self.elevation])

    def transform_to_cartesian(self) -> "CartesianCoordinates":
        """Transforms the coordinates to Cartesian coordinates.

        Returns:
            The Cartesian coordinates.
        """
        x, y, z = self.transform_to_cartesian_arrays(
            self.range,
            self.azimuth,
            self.elevation,
        )
        return CartesianCoordinates(x, y, z)

    @staticmethod
    def transform_to_cartesian_arrays(
        range: float | np.ndarray,
        azimuth: float | np.ndarray,
        elevation: float | np.ndarray,
    ) -> tuple[float | np.ndarray, float | np.ndarray, float | np.ndarray]:
        """Transforms the coordinates to Cartesian coordinates.

        Returns:
            The x, y, and z-coordinates.
        """
        x = -range * np.sin(azimuth) * np.cos(elevation)
        y = range * np.sin(elevation)
        z = range * np.cos(azimuth) * np.cos(elevation)
        return x, y, z
