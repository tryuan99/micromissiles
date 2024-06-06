"""The real frequency estimator is an interface for an estimator that, given
the samples of a linear combination of real exponentials estimates their
amplitude and damping factor.
"""

from abc import abstractmethod

from simulation.estimator.complex_exponential_estimator import \
    ComplexExponentialEstimator
from simulation.estimator.real_exponential import RealExponentialParams
from simulation.radar.components.samples import Samples


class RealExponentialEstimator(ComplexExponentialEstimator):
    """Interface for a real exponential estimator."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

    @abstractmethod
    def estimate_single_exponential(self) -> RealExponentialParams:
        """Estimates the parameters of a single real exponential.

        Returns:
            The estimated parameters of the real exponential.
        """

    @abstractmethod
    def estimate_multiple_exponentials(
            self, num_exponentials: int) -> list[RealExponentialParams]:
        """Estimates the parameters of multiple real exponentials.

        Args:
            num_exponentials: Number of real exponentials.

        Returns:
            The estimated parameters of the real exponentials.
        """
