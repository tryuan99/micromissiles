import numpy as np
from absl.testing import absltest

from simulation.estimator.complex_exponential import ComplexExponential
from simulation.estimator.prony.prony_polynomial_complex_exponential_estimator import \
    PronyPolynomialComplexExponentialEstimator

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 100  # Hz

# Number of samples.
NUM_SAMPLES = 1000


class PronyPolynomialComplexExponentialEstimatorTestCase(absltest.TestCase):

    def test_decaying_exponential(self):
        decaying_exponential = ComplexExponential(SAMPLING_FREQUENCY,
                                                  NUM_SAMPLES,
                                                  frequency=0,
                                                  phase=0,
                                                  amplitude=2,
                                                  alpha=np.log(0.5),
                                                  snr=np.inf)
        estimator = PronyPolynomialComplexExponentialEstimator(
            decaying_exponential, SAMPLING_FREQUENCY)
        params = estimator.estimate_single_exponential()
        self.assertIsNone(np.testing.assert_allclose(params.frequency, 0))
        self.assertIsNone(np.testing.assert_allclose(params.phase, 0))
        self.assertIsNone(np.testing.assert_allclose(params.amplitude, 2))
        self.assertIsNone(np.testing.assert_allclose(params.alpha, np.log(0.5)))

    def test_sinusoid(self):
        sinusoid = ComplexExponential(SAMPLING_FREQUENCY,
                                      NUM_SAMPLES,
                                      frequency=20,
                                      phase=np.pi / 4,
                                      amplitude=2,
                                      alpha=0,
                                      snr=np.inf)
        estimator = PronyPolynomialComplexExponentialEstimator(
            sinusoid, SAMPLING_FREQUENCY)
        params = estimator.estimate_single_exponential()
        self.assertIsNone(np.testing.assert_allclose(params.frequency, 20))
        self.assertIsNone(np.testing.assert_allclose(params.phase, np.pi / 4))
        self.assertIsNone(np.testing.assert_allclose(params.amplitude, 2))
        self.assertIsNone(
            np.testing.assert_allclose(params.alpha, 0, atol=1e-12))

    def test_damped_sinusoid(self):
        sinusoid = ComplexExponential(SAMPLING_FREQUENCY,
                                      NUM_SAMPLES,
                                      frequency=20,
                                      phase=np.pi / 4,
                                      amplitude=2,
                                      alpha=np.log(0.8),
                                      snr=np.inf)
        estimator = PronyPolynomialComplexExponentialEstimator(
            sinusoid, SAMPLING_FREQUENCY)
        params = estimator.estimate_single_exponential()
        self.assertIsNone(np.testing.assert_allclose(params.frequency, 20))
        self.assertIsNone(np.testing.assert_allclose(params.phase, np.pi / 4))
        self.assertIsNone(np.testing.assert_allclose(params.amplitude, 2))
        self.assertIsNone(np.testing.assert_allclose(params.alpha, np.log(0.8)))

    def test_multiple_decaying_exponentials(self):
        decaying_exponential1 = ComplexExponential(SAMPLING_FREQUENCY,
                                                   NUM_SAMPLES,
                                                   frequency=0,
                                                   phase=0,
                                                   amplitude=3,
                                                   alpha=np.log(0.5),
                                                   snr=np.inf)
        decaying_exponential2 = ComplexExponential(SAMPLING_FREQUENCY,
                                                   NUM_SAMPLES,
                                                   frequency=0,
                                                   phase=np.pi / 2,
                                                   amplitude=2,
                                                   alpha=np.log(0.8),
                                                   snr=np.inf)
        estimator = PronyPolynomialComplexExponentialEstimator(
            decaying_exponential1 + decaying_exponential2, SAMPLING_FREQUENCY)
        params = estimator.estimate_multiple_exponentials(num_exponentials=2)
        self.assertIsNone(
            np.testing.assert_allclose(params[0].frequency, 0, atol=1e-10))
        self.assertIsNone(
            np.testing.assert_allclose(params[0].phase, 0, atol=1e-10))
        self.assertIsNone(np.testing.assert_allclose(params[0].amplitude, 3))
        self.assertIsNone(
            np.testing.assert_allclose(params[0].alpha, np.log(0.5)))
        self.assertIsNone(
            np.testing.assert_allclose(params[1].frequency, 0, atol=1e-10))
        self.assertIsNone(np.testing.assert_allclose(params[1].phase,
                                                     np.pi / 2))
        self.assertIsNone(np.testing.assert_allclose(params[1].amplitude, 2))
        self.assertIsNone(
            np.testing.assert_allclose(params[1].alpha, np.log(0.8)))


if __name__ == "__main__":
    absltest.main()
