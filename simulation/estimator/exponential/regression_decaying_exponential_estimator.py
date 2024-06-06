"""The regression decaying exponential estimator estimates the parameters of a
real decaying exponential using a regression.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.estimator.real_exponential import RealExponentialParams
from simulation.estimator.real_exponential_estimator import \
    RealExponentialEstimator
from simulation.radar.components.samples import Samples

# Number of ADC samples to average at the end to find the minimum ADC output.
NUM_AVERAGES_FOR_MIN_ADC_OUTPUT = 10


class RegressionDecayingExponentialEstimator(RealExponentialEstimator, ABC):
    """Decaying exponential estimator using a regression."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

    def estimate_single_exponential(self) -> RealExponentialParams:
        """Estimates the parameters of a single decaying exponential.

        Returns:
            The estimated parameters of the decaying exponential.
        """
        t = np.arange(self.size) / self.fs
        three_tau_index = self._estimate_three_tau_index()
        return self._run_regression(
            t[:three_tau_index],
            self.samples[:three_tau_index] - self._get_min_sample())

    def estimate_multiple_exponentials(
            self, num_exponentials: int) -> list[RealExponentialParams]:
        """Estimates the parameters of multiple decaying exponentials.

        Args:
            num_exponentials: Number of decaying exponentials.

        Returns:
            The estimated parameters of the decaying exponentials.
        """
        raise AttributeError(("Estimating multiple decaying exponentials is "
                              "not supported."))

    def _get_min_sample(self) -> float:
        """Returns the minimum exponential sample."""
        # TODO(titan): Average the last few exponential samples if there is a
        # vertical offset.
        # return np.mean(self.samples[-NUM_AVERAGES_FOR_MIN_ADC_OUTPUT:])
        return 0

    @abstractmethod
    def _run_regression(self, t_axis: np.ndarray,
                        samples: np.ndarray) -> RealExponentialParams:
        """Runs the regression on the time axis and the exponential samples.

        Args:
            t_axis: Time axis.
            samples: Exponential samples.

        Returns:
            The parameters of the decaying exponential.
        """

    def _get_max_sample(self) -> float:
        """Returns the maximum exponential sample."""
        return np.max(self.samples)

    def _estimate_three_tau_index(self) -> int:
        """Estimates the index at 3tau.

        The sample at 3tau corresponds to where the exponential has decayed by
        95%. Note that this function only estimates 3tau due to the presence
        of noise.

        Returns:
            The index at 3tau.
        """
        three_tau_index = (
            np.argmax(self.samples < 0.95 * self._get_min_sample() +
                      0.05 * self._get_max_sample()) or self.size)
        return three_tau_index
