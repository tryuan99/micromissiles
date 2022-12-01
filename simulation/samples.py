"""The samples class is an interface for a collection of samples."""

import numpy as np


class Samples:
    """Represents a collection of samples."""

    def __init__(self, samples: np.ndarray):
        self.samples = samples

    @property
    def shape(self) -> tuple[int, ...]:
        """Shape of the samples."""
        return self.samples.shape

    def add_samples(self, samples: "Samples") -> None:
        """Adds the samples."""
        self.samples = self.samples + samples.get_samples()

    def get_samples(self) -> np.ndarray:
        """Returns the samples."""
        return np.copy(self.samples)

    def get_amplitude(self) -> float:
        """Returns the empirical amplitude, or RMS value, of the samples."""
        return np.sqrt(np.mean(np.abs(self.samples) ** 2))
