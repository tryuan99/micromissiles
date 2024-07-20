"""The patch antenna class represents a single patch antenna."""

import numpy as np

from simulation.antenna.antenna import Antenna


class PatchAntenna(Antenna):
    """Patch antenna.

    The patch antenna lies in the x-y plane, fed in the y-direction (W parallel
    to the x-axis and L parallel to the y-axis).

    Attributes:
        width: Width in units of lambda.
        length: Length in units of lambda.
    """

    def __init__(self, width: float, length: float) -> None:
        super().__init__()
        self.width = width
        self.length = length

    def calculate_pattern(self, azimuth: float | np.ndarray,
                          elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        # Transform the coordinate systems.
        x = -np.sin(azimuth) * np.cos(elevation)
        y = np.sin(elevation)
        z = np.cos(azimuth) * np.cos(elevation)
        azimuth_pattern = np.arccos(y / np.sqrt(x**2 + y**2))
        azimuth_pattern = np.nan_to_num(azimuth_pattern)
        azimuth_pattern[x > 0] *= -1
        elevation_pattern = np.arccos(z)
        return self._calculate_pattern(azimuth_pattern, elevation_pattern)

    def _calculate_pattern(self, azimuth: float | np.ndarray,
                           elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Adapted from https://www.antenna-theory.com/antennas/patches/antenna.php.
        The equation assumes that the patch antenna lies in the x-y plane, fed
        in the y-direction (W parallel to the x-axis and L parallel to the
        y-axis). The azimuth is the angle on the x-y plane measured
        counterclockwise from the y-axis, and the elevation is the angle
        measured from the z-axis.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        projected_sinc = np.sinc(
            self.width * np.sin(azimuth) * np.sin(elevation)) * np.cos(
                np.pi * self.length * np.cos(azimuth) * np.sin(elevation))
        E_azimuth = -projected_sinc * np.sin(azimuth) * np.cos(elevation)
        E_elevation = projected_sinc * np.cos(azimuth)
        return np.sqrt(np.abs(E_azimuth)**2 + np.abs(E_elevation)**2)
