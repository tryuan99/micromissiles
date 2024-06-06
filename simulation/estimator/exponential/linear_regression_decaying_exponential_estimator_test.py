import numpy as np
from absl.testing import absltest

from simulation.estimator.exponential.linear_regression_decaying_exponential_estimator import \
    LinearRegressionDecayingExponentialEstimator
from simulation.estimator.real_exponential import RealExponential

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 100  # Hz

# Number of samples.
NUM_SAMPLES = 1000


class LinearRegressionDecayingExponentialEstimatorTestCase(absltest.TestCase):

    def test_decaying_exponential(self):
        decaying_exponential = RealExponential(SAMPLING_FREQUENCY,
                                               NUM_SAMPLES,
                                               amplitude=2,
                                               alpha=np.log(0.5),
                                               snr=np.inf)
        estimator = LinearRegressionDecayingExponentialEstimator(
            decaying_exponential, SAMPLING_FREQUENCY)
        params = estimator.estimate_single_exponential()
        self.assertIsNone(np.testing.assert_allclose(params.amplitude, 2))
        self.assertIsNone(np.testing.assert_allclose(params.alpha, np.log(0.5)))


if __name__ == "__main__":
    absltest.main()
