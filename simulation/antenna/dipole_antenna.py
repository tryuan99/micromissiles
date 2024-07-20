"""The dipole antenna class represents a single dipole antenna."""

import numpy as np
import scipy.special

from simulation.antenna.antenna import Antenna


class DipoleAntenna(Antenna):
    """Dipole antenna.

    The dipole antenna lies along the y-axis, so the E-field is polarized along
    the y-axis as well.
    The length of the dipole specifies the total length.

    Attributes:
        length: Length in units of lambda.
    """

    def __init__(self, length: float) -> None:
        super().__init__()
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
        azimuth_pattern = -azimuth
        elevation_pattern = np.pi / 2 - elevation
        return self._calculate_pattern(azimuth_pattern, elevation_pattern)

    def _calculate_pattern(self, azimuth: float | np.ndarray,
                           elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Adapted from "Antenna Theory: Analysis and Design" by Constantine A.
        Balanis.
        The equation assumes that the dipole antenna lies along the y-axis. The
        azimuth is the angle on the x-z plane measured counterclockwise from
        the z-axis, and the elevation is the angle measured from the y-axis.
        See page 146 for the coordinate system.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        k = 2 * np.pi
        E = (1j * 120 * np.pi * np.exp(-1j * k) / (2 * np.pi) *
             (np.cos(1 / 2 * k * self.length * np.cos(elevation)) -
              np.cos(1 / 2 * k * self.length)) / np.sin(elevation))
        E_shape = np.broadcast_shapes(np.shape(azimuth), np.shape(elevation))
        return np.broadcast_to(np.abs(np.nan_to_num(E)), E_shape)
