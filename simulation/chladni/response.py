"""The response class holds the motion of the vibrating plate."""

from dataclasses import dataclass

import numpy as np


@dataclass
class Response:
    """Motion of the plate once it vibrates steadily, NaN off the plate.

    Attributes:
        x: x-coordinates in m.
        y: y-coordinates in m.
        deflection: Complex deflection W in m.
        drive_amplitude: Amplitude of the drive point in m.
        drive_frequency: Drive frequency in Hz.
    """

    x: np.ndarray
    y: np.ndarray
    deflection: np.ndarray
    drive_amplitude: float
    drive_frequency: float

    @property
    def mask(self) -> np.ndarray:
        """Returns whether each grid point lies on the plate."""
        return ~np.isnan(self.deflection)

    @property
    def amplitude(self) -> np.ndarray:
        """Returns the amplitude |W| in m."""
        return np.abs(self.deflection)

    @property
    def phase(self) -> np.ndarray:
        """Returns the phase in rad relative to the drive point."""
        return np.angle(self.deflection)
