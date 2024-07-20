"""The horn antenna class represents a single pyramidal horn antenna."""

import numpy as np
import scipy.special

from simulation.antenna.antenna import Antenna


class HornAntenna(Antenna):
    """Horn antenna.

    The aperture of the horn antenna lies in the x-y plane, fed in the
    z-direction (a and a1 parallel to the x-axis and b and b1 parallel to the
    y-axis). The E-field is polarized along the y-axis.
    a and b refer to the dimensions of the antenna aperture before the flare,
    and a1 and b1 refer to the dimensions of the antenna aperture after the
    flare.

    Attributes:
        a: Width in units of lambda before the flare.
        b: Height in uints of lambda before the flare.
        a1: Width in units of lambda after the flare.
        b1: Height in units of lambda after the flare.
        rho1: Depth of the pyramid in the y-z plane in units of lambda.
        rho2: Depth of the pyramid in the x-z plane in units of lambda.
    """

    def __init__(self, a: float, b: float, a1: float, b1: float, rho1: float,
                 rho2: float) -> None:
        super().__init__()
        self.a = a
        self.b = b
        self.a1 = a1
        self.b1 = b1
        self.rho1 = rho1
        self.rho2 = rho2

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
        azimuth_pattern = np.arccos(x / np.sqrt(x**2 + y**2))
        azimuth_pattern = np.nan_to_num(azimuth_pattern)
        azimuth_pattern[y < 0] *= -1
        elevation_pattern = np.arccos(z)
        return self._calculate_pattern(azimuth_pattern, elevation_pattern)

    def _calculate_pattern(self, azimuth: float | np.ndarray,
                           elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Adapted from "Antenna Theory: Analysis and Design" by Constantine A.
        Balanis.
        The equation assumes that the aperture of the horn antenna lies in the
        x-y plane, fed in the z-direction (a and a1 parallel to the x-axis and
        b and b1 parallel to the y-axis). The azimuth is the angle on the x-y
        plane measured counterclockwise from the x-axis, and the elevation is
        the angle measured from the z-axis.
        See page 26 for the coordinate system.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        # Define the Fresnel integrals.
        S = lambda x: scipy.special.fresnel(x)[0]
        C = lambda x: scipy.special.fresnel(x)[1]

        k = 2 * np.pi
        ky = k * np.sin(elevation) * np.sin(azimuth)
        t1 = (np.sqrt(1 / (np.pi * k * self.rho1)) *
              (-k * self.b1 / 2 - ky * self.rho1))
        t2 = (np.sqrt(1 / (np.pi * k * self.rho1)) *
              (k * self.b1 / 2 - ky * self.rho1))

        kxp = k * np.sin(elevation) * np.cos(azimuth) + np.pi / self.a1
        t1p = (np.sqrt(1 / (np.pi * k * self.rho2)) *
               (-k * self.a1 / 2 - kxp * self.rho2))
        t2p = (np.sqrt(1 / (np.pi * k * self.rho2)) *
               (k * self.a1 / 2 - kxp * self.rho2))

        kxpp = k * np.sin(elevation) * np.cos(azimuth) - np.pi / self.a1
        t1pp = (np.sqrt(1 / (np.pi * k * self.rho2)) *
                (-k * self.a1 / 2 - kxpp * self.rho2))
        t2pp = (np.sqrt(1 / (np.pi * k * self.rho2)) *
                (k * self.a1 / 2 - kxpp * self.rho2))

        I1 = (1 / 2 * np.sqrt(np.pi * self.rho2 / k) *
              np.exp(1j * kxp**2 * self.rho2 /
                     (2 * k)) * (C(t2p) - C(t1p) - 1j * (S(t2p) - S(t1p))) +
              np.exp(1j * kxpp**2 * self.rho2 /
                     (2 * k)) * (C(t2pp) - C(t1pp) - 1j * (S(t2pp) - S(t1pp))))
        I2 = (np.sqrt(np.pi * self.rho1 / k) *
              np.exp(1j * ky**2 * self.rho1 / (2 * k)) * (C(t2) - C(t1) - 1j *
                                                          (S(t2) - S(t1))))

        E_azimuth = (1j * k * np.exp(-1j * k) / (4 * np.pi) *
                     (np.cos(azimuth) * (np.cos(elevation) + 1) * I1 * I2))
        E_elevation = (1j * k * np.exp(-1j * k) / (4 * np.pi) *
                       (np.sin(azimuth) * (np.cos(elevation) + 1) * I1 * I2))
        return np.sqrt(np.abs(E_azimuth)**2 + np.abs(E_elevation)**2)
