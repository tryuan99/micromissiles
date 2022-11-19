"""The following noise classes each represent a different type of noise."""

import numpy as np
from typing import Tuple


class GaussianNoise:
    """Represents complex white Gaussian noise."""

    def __init__(self, shape: Tuple[int, ...], amplitude: float = 1) -> np.ndarray:
        self.amplitude = amplitude
        self.samples = (
            amplitude
            / np.sqrt(2)
            * (np.random.normal(size=shape) + 1j * np.random.normal(size=shape))
        )

    @property
    def mean(self) -> float:
        """Mean of the noise."""
        return 0

    @property
    def std(self) -> float:
        """Standard deviation, or RMS value, of the noise."""
        return self.amplitude


class UniformNoise:
    """Represents complex white uniform noise."""

    def __init__(
        self, shape: Tuple[int, ...], low: float = -0.5, high: float = 0.5
    ) -> np.ndarray:
        self.low = low
        self.high = high
        self.samples = np.random.normal(
            low=low, high=high, size=shape
        ) + 1j * np.random.normal(low=low, high=high, size=shape)

    @property
    def mean(self) -> float:
        """Mean of the noise."""
        return (self.high - self.low) / 2

    @property
    def std(self) -> float:
        """Standard deviation, or RMS value, of the noise."""
        return np.sqrt(2) / np.sqrt(12) * (self.high - self.low)
