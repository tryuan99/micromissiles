import numpy as np
from absl.testing import absltest

from simulation.estimator.real_exponential import (RealExponential,
                                                   RealExponentialParams)

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 1  # Hz

# Number of samples.
NUM_SAMPLES = 4


class RealExponentialTestCase(absltest.TestCase):

    def test_dc(self):
        dc = RealExponential(SAMPLING_FREQUENCY,
                             NUM_SAMPLES,
                             amplitude=2,
                             alpha=0,
                             snr=np.inf)
        self.assertIsNone(
            np.testing.assert_array_equal(dc.samples, np.array([2, 2, 2, 2])))

    def test_decaying_exponential(self):
        decaying_exponential = RealExponential(SAMPLING_FREQUENCY,
                                               NUM_SAMPLES,
                                               amplitude=2,
                                               alpha=np.log(0.5),
                                               snr=np.inf)
        self.assertIsNone(
            np.testing.assert_allclose(decaying_exponential.samples,
                                       np.array([2, 1, 0.5, 0.25])))

    def test_params(self):
        params = RealExponentialParams(amplitude=2, alpha=np.log(0.5))
        decaying_exponential = RealExponential(SAMPLING_FREQUENCY,
                                               NUM_SAMPLES,
                                               amplitude=3,
                                               alpha=0,
                                               params=params,
                                               snr=np.inf)
        self.assertIsNone(
            np.testing.assert_allclose(decaying_exponential.samples,
                                       np.array([2, 1, 0.5, 0.25])))


if __name__ == "__main__":
    absltest.main()
