"""The following noise classes each represent a different type of noise."""

from abc import ABC, abstractmethod

import numpy as np

from simulation.radar.components.samples import Samples


class Noise(Samples, ABC):
    """Represents some noise."""

    @abstractmethod
    def get_mean(self) -> float:
        """Returns the mean of the noise."""


class GaussianNoise(Noise):
    """Represents complex white Gaussian noise."""

    def __init__(self,
                 shape: tuple[int, ...],
                 amplitude: float = 1,
                 real: bool = False):
        super().__init__(self.generate_noise_samples(shape, amplitude, real))

    def get_mean(self) -> float:
        """Returns the mean of the noise."""
        return 0

    @staticmethod
    def generate_noise_samples(shape: tuple[int, ...],
                               amplitude: float,
                               real: bool = False) -> np.ndarray:
        """Generates noise samples.

        Args:
            shape: Shape of the noise.
            amplitude: Noise amplitude.
            real: If true, generate only real samples.

        Returns:
            Noise samples.
        """
        if real:
            return amplitude * np.random.normal(size=shape)
        return (
            amplitude / np.sqrt(2) *
            (np.random.normal(size=shape) + 1j * np.random.normal(size=shape)))


class UniformNoise(Noise):
    """Represents complex white uniform noise."""

    def __init__(
        self,
        shape: tuple[int, ...],
        amplitude: float = 1,
        low: float = -0.5,
        high: float = 0.5,
    ):
        super().__init__(
            self.generate_noise_samples(shape, amplitude, low, high))
        self.low = low
        self.high = high

    def get_mean(self) -> float:
        """Returns the mean of the noise."""
        return (self.high - self.low) / 2

    @staticmethod
    def generate_noise_samples(shape: tuple[int, ...], amplitude: float,
                               low: float, high: float) -> np.ndarray:
        """Generates noise samples.

        Args:
            shape: Shape of the noise.
            amplitude: Noise amplitude.
            low: Lower bound of the output interval.
            high: Upper bound of the output interval.

        Returns:
            Noise samples.
        """
        return (amplitude / (np.sqrt(2) / np.sqrt(12) * (high - low)) *
                (np.random.uniform(low=low, high=high, size=shape) +
                 1j * np.random.uniform(low=low, high=high, size=shape)))
