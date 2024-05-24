import numpy as np
from absl.testing import absltest

from simulation.estimator.complex_exponential import ComplexExponential

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 1  # Hz

# Number of samples.
NUM_SAMPLES = 4


class ComplexExponentialTestCase(absltest.TestCase):

    def test_dc(self):
        dc = ComplexExponential(SAMPLING_FREQUENCY,
                                NUM_SAMPLES,
                                frequency=0,
                                phase=0,
                                amplitude=2,
                                alpha=0,
                                snr=np.inf)
        self.assertIsNone(
            np.testing.assert_array_equal(dc.samples, np.array([2, 2, 2, 2])))

    def test_sinusoid(self):
        sinusoid = ComplexExponential(SAMPLING_FREQUENCY,
                                      NUM_SAMPLES,
                                      frequency=0.25,
                                      phase=np.pi / 2,
                                      amplitude=0.5,
                                      alpha=0,
                                      snr=np.inf)
        self.assertIsNone(
            np.testing.assert_allclose(sinusoid.samples,
                                       0.5 * np.array([1j, -1, -1j, 1])))

    def test_decaying_exponential(self):
        decaying_exponential = ComplexExponential(SAMPLING_FREQUENCY,
                                                  NUM_SAMPLES,
                                                  frequency=0,
                                                  phase=0,
                                                  amplitude=2,
                                                  alpha=np.log(0.5),
                                                  snr=np.inf)
        self.assertIsNone(
            np.testing.assert_allclose(decaying_exponential.samples,
                                       np.array([2, 1, 0.5, 0.25])))


if __name__ == "__main__":
    absltest.main()
