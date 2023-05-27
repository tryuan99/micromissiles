"""The samples class is an interface for a collection of samples."""

import numpy as np


class Samples:
    """Represents a collection of samples."""

    # TODO(titan): Change the type to "Samples" | np.ndarray.
    def __init__(self, samples: "Samples"):
        if isinstance(samples, Samples):
            return Samples.__init__(self, samples.samples)
        self.samples = np.copy(samples)

    @property
    def shape(self) -> tuple[int, ...]:
        """Shape of the samples."""
        return self.samples.shape

    def add_samples(self, samples: "Samples") -> None:
        """Adds the samples."""
        self.samples = self.samples + samples.samples

    def get_abs_samples(self) -> np.ndarray:
        """Returns the absolute value of the samples."""
        return np.abs(self.samples)

    def get_amplitude(self) -> float:
        """Returns the empirical amplitude, or RMS value, of the samples."""
        return np.sqrt(np.mean(np.abs(self.samples)**2))
