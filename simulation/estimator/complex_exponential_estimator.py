"""The complex frequency estimator is an interface for an estimator that, given
the samples of a linear combination of complex exponentials estimates their
frequency, phase, amplitude, and damping factor.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.estimator.complex_exponential import ComplexExponentialParams
from simulation.estimator.estimator import Estimator1D
from simulation.radar.components.samples import Samples


class ComplexExponentialEstimator(Estimator1D, ABC):
    """Interface for a complex exponential estimator."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

    @abstractmethod
    def estimate_single_exponential(self) -> ComplexExponentialParams:
        """Estimates the parameters of a single complex exponential.

        Returns:
            The estimated parameters of the complex exponential.
        """

    @abstractmethod
    def estimate_multiple_exponentials(
            self, num_exponentials: int) -> list[ComplexExponentialParams]:
        """Estimates the parameters of multiple complex exponentials.

        Args:
            num_exponentials: Number of complex exponentials.

        Returns:
            The estimated parameters of the complex exponentials.
        """
