"""The frequency estimator is an interface for an estimator that, given some
samples of a signal, estimates the frequencies in the signal.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.radar.components.samples import Samples


class FrequencyEstimator(Samples, ABC):
    """Interface for a frequency estimator."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples)
        self.fs = fs

        if self.ndim != 1:
            raise ValueError("Only signals of dimension 1 are supported.")

    @abstractmethod
    def estimate_single_frequency(self) -> float:
        """Estimates a single frequency.

        Returns:
            The estimated frequency in Hz.
        """

    @abstractmethod
    def estimate_multiple_frequencies(self, num_frequencies: int) -> np.ndarray:
        """Estimates multiple frequencies.

        Args:
            num_frequencies: Number of frequencies.

        Returns:
            The estimated frequencies in Hz.
        """
