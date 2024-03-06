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
        # Transform coordinate systems.
        x = -np.sin(azimuth) * np.cos(elevation)
        y = np.sin(elevation)
        z = np.cos(azimuth) * np.cos(elevation)
        x_pattern = y
        y_pattern = z
        z_pattern = x
        azimuth_pattern = np.arctan(y_pattern / x_pattern) % np.pi
        elevation_pattern = np.arctan(z_pattern /
                                      np.sqrt(x_pattern**2 + y_pattern**2))
        return self._calculate_pattern(azimuth_pattern, elevation_pattern)

    def _calculate_pattern(self, azimuth: float | np.ndarray,
                           elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Adapted from https://www.antenna-theory.com/antennas/patches/antenna.php.
        The field equation assumes that the patch antenna lies in the x-z plane,
        fed in the x-direction (W parallel to the z-axis and L parallel to the
        x-axis).

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
        return np.sqrt(E_azimuth**2 + E_elevation**2)
