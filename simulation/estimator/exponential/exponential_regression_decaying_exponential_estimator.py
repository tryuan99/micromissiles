"""The exponential regression decaying exponential estimator estimates the
parameters of a real decaying exponential using an exponential regression.
"""

import numpy as np

from simulation.estimator.exponential.regression_decaying_exponential_estimator import \
    RegressionDecayingExponentialEstimator
from simulation.estimator.real_exponential import RealExponentialParams
from simulation.radar.components.samples import Samples
from utils.regression.exponential_regression import ExponentialRegression


class ExponentialRegressionDecayingExponentialEstimator(
        RegressionDecayingExponentialEstimator):
    """Decaying exponential estimator using an exponential regression."""

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
        exponential_regression = ExponentialRegression(t_axis, samples)
        return RealExponentialParams(
            amplitude=exponential_regression.a,
            alpha=(-1 / exponential_regression.time_constant))
