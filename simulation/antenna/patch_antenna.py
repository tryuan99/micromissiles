"""The patch antenna class represents a single patch antenna."""

import numpy as np

from simulation.antenna.antenna import Antenna


class PatchAntenna(Antenna):
    """Patch antenna.

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

        Adapted from https://www.antenna-theory.com/antennas/patches/antenna.php.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        projected_sinc = np.sinc(
            self.width * np.sin(azimuth) * np.sin(elevation)) * np.cos(
                np.pi * np.cos(azimuth) * np.sin(elevation))
        E_azimuth = -projected_sinc * np.sin(azimuth) * np.cos(elevation)
        E_elevation = projected_sinc * np.cos(azimuth)
        return np.sqrt(E_azimuth**2 + E_elevation**2)
