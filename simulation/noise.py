"""The following noise classes each represent a different type of noise."""

from abc import ABC, abstractmethod

import numpy as np


class Noise(ABC):
    """Represents some noise."""

    def __init__(self, samples: np.ndarray):
        self.samples = samples

    @property
    def shape(self) -> tuple[int, ...]:
        """Shape of the noise."""
        return self.samples.shape

    @property
    @abstractmethod
    def mean(self) -> float:
        """Mean of the noise."""
        pass

    @property
    @abstractmethod
    def std(self) -> float:
        """Standard deviation, or RMS value, of the noise."""
        pass


class GaussianNoise(Noise):
    """Represents complex white Gaussian noise."""

    def __init__(self, shape: tuple[int, ...], amplitude: float = 1) -> np.ndarray:
        super().__init__(
            amplitude
            / np.sqrt(2)
            * (np.random.normal(size=shape) + 1j * np.random.normal(size=shape))
        )
        self.amplitude = amplitude

    @property
    def mean(self) -> float:
        """Mean of the noise."""
        return 0

    @property
    def std(self) -> float:
        """Standard deviation, or RMS value, of the noise."""
        return self.amplitude


class UniformNoise(Noise):
    """Represents complex white uniform noise."""

    def __init__(
        self, shape: tuple[int, ...], low: float = -0.5, high: float = 0.5
    ) -> np.ndarray:
        super().__init__(
            np.random.uniform(low=low, high=high, size=shape)
            + 1j * np.random.uniform(low=low, high=high, size=shape)
        )
        self.low = low
        self.high = high

    @property
    def mean(self) -> float:
        """Mean of the noise."""
        return (self.high - self.low) / 2

    @property
    def std(self) -> float:
        """Standard deviation, or RMS value, of the noise."""
        return np.sqrt(2) / np.sqrt(12) * (self.high - self.low)
