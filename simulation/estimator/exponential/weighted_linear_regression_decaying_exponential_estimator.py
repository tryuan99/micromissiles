"""The exponential regression decaying exponential estimator estimates the
parameters of a real decaying exponential using a weighted linear regression.

See https://ieeexplore.ieee.org/document/10446713.
"""

import numpy as np

from simulation.estimator.exponential.regression_decaying_exponential_estimator import \
    RegressionDecayingExponentialEstimator
from simulation.estimator.real_exponential import RealExponentialParams
from simulation.radar.components.samples import Samples
from utils.regression.linear_regression import WeightedLinearRegression


class WeightedLinearRegressionDecayingExponentialEstimator(
        RegressionDecayingExponentialEstimator):
    """Decaying exponential estimator using a weighted linear regression."""

    def __init__(self,
                 samples: Samples,
                 fs: float,
                 offset: bool = False) -> None:
        super().__init__(samples, fs, offset)

    def _run_regression(self, t_axis: np.ndarray,
                        samples: np.ndarray) -> RealExponentialParams:
        """Runs the regression on the time axis and the exponential samples.

        Args:
            t_axis: Time axis.
            samples: Exponential samples.

        Returns:
            The parameters of the decaying exponential.
        """
        variances = (np.exp(t_axis / self._estimate_tau()))**2
        weights = 1 / variances
        weighted_linear_regression = WeightedLinearRegression(
            t_axis, np.log(samples), weights)
        return RealExponentialParams(amplitude=np.exp(
            weighted_linear_regression.y_intercept),
                                     alpha=weighted_linear_regression.slope)

    def _estimate_tau(self) -> float:
        """Estimates the time constant based on the three tau index.

        Returns:
            The estimated time constant.
        """
        three_tau_index = self._estimate_three_tau_index()
        return three_tau_index / (3 * self.fs)
