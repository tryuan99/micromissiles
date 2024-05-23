import numpy as np
from absl.testing import absltest

from simulation.estimator.sinusoid import Sinusoid

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 1  # Hz

# Number of samples.
NUM_SAMPLES = 4


class SinusoidTestCase(absltest.TestCase):

    def test_dc(self):
        sinusoid = Sinusoid(SAMPLING_FREQUENCY,
                            NUM_SAMPLES,
                            frequency=0,
                            phase=0,
                            amplitude=1,
                            snr=np.inf)
        self.assertIsNone(
            np.testing.assert_array_equal(sinusoid.samples,
                                          np.array([1, 1, 1, 1])))

    def test_frequency_without_noise(self):
        sinusoid = Sinusoid(SAMPLING_FREQUENCY,
                            NUM_SAMPLES,
                            frequency=0.25,
                            phase=np.pi / 2,
                            amplitude=0.5,
                            snr=np.inf)
        self.assertIsNone(
            np.testing.assert_allclose(sinusoid.samples,
                                       0.5 * np.array([1j, -1, -1j, 1])))


if __name__ == "__main__":
    absltest.main()
