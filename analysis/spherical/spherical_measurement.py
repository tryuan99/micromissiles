"""Spherical near-field measurement at a single frequency."""

from dataclasses import dataclass

import numpy as np

from utils import constants


@dataclass
class SphericalMeasurement:
    """Spherical near-field measurement at a single frequency.

    Attributes:
        frequency: Frequency in Hz.
        distance: Distance in meters from the test antenna coordinate origin to
            the probe coordinate origin.
        w: Received signal with shape (2, num_theta, num_phi) for the two probe
            polarizations.
        theta: Equispaced theta from 0 to pi inclusive with shape (num_theta,).
        phi: Equispaced phi covering 2pi with shape (num_theta, num_phi).
        chi: Probe rotation angle with shape (2, num_theta).
    """
    frequency: float
    distance: float
    w: np.ndarray
    theta: np.ndarray
    phi: np.ndarray
    chi: np.ndarray

    @property
    def wavenumber(self) -> float:
        """Free-space wavenumber k in rad/m."""
        return 2 * np.pi * self.frequency / constants.SPEED_OF_LIGHT

    @property
    def kA(self) -> float:
        """Wavenumber times the measurement distance."""
        return self.wavenumber * self.distance
