import numpy as np
from absl.testing import absltest

from simulation.estimator.fft_frequency_estimator import (
    FftJacobsenFrequencyEstimator, FftParabolicInterpolationFrequencyEstimator,
    FftPeakFrequencyEstimator, FftTwoPointDtftFrequencyEstimator, FftWindow,
    FftWindowedJacobsenFrequencyEstimator)

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 128  # Hz

# Number of samples.
NUM_SAMPLES = 64

# FFT length.
FFT_LENGTH = 256


class FftPeakFrequencyEstimatorSingleTestCase(absltest.TestCase):

    frequency = 37
    phase = 0
    samples = np.exp(
        1j *
        (2 * np.pi * frequency / SAMPLING_FREQUENCY * np.arange(NUM_SAMPLES) +
         phase))
    frequency_estimator = FftPeakFrequencyEstimator(samples,
                                                    SAMPLING_FREQUENCY,
                                                    FFT_LENGTH,
                                                    window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertEqual(self.frequency_estimator.estimate_single_frequency(),
                         self.frequency)


class FftPeakFrequencyEstimatorMultipleTestCase(absltest.TestCase):

    frequencies = np.array([5, 37])
    phases = np.array([0, 1.4])
    amplitudes = np.array([1, 0.7])
    samples = np.sum(
        amplitudes[:, np.newaxis] *
        np.exp(1j *
               (2 * np.pi * frequencies[:, np.newaxis] / SAMPLING_FREQUENCY *
                np.arange(NUM_SAMPLES) + phases[:, np.newaxis])),
        axis=0)
    frequency_estimator = FftPeakFrequencyEstimator(samples,
                                                    SAMPLING_FREQUENCY,
                                                    FFT_LENGTH,
                                                    window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertEqual(self.frequency_estimator.estimate_single_frequency(),
                         self.frequencies[np.argmax(self.amplitudes)])

    def test_estimate_multiple_frequencies(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.frequency_estimator.estimate_multiple_frequencies(
                    len(self.frequencies)),
                self.frequencies[np.argsort(self.amplitudes)[::-1]]))


class FftParabolicInterpolationFrequencyEstimatorSingleTestCase(
        absltest.TestCase):

    frequency = 37
    phase = 0
    samples = np.exp(
        1j *
        (2 * np.pi * frequency / SAMPLING_FREQUENCY * np.arange(NUM_SAMPLES) +
         phase))
    frequency_estimator = FftParabolicInterpolationFrequencyEstimator(
        samples, SAMPLING_FREQUENCY, FFT_LENGTH, window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequency))


class FftParabolicInterpolationFrequencyEstimatorMultipleTestCase(
        absltest.TestCase):

    frequencies = np.array([5, 37])
    phases = np.array([0, 1.4])
    amplitudes = np.array([1, 0.7])
    samples = np.sum(
        amplitudes[:, np.newaxis] *
        np.exp(1j *
               (2 * np.pi * frequencies[:, np.newaxis] / SAMPLING_FREQUENCY *
                np.arange(NUM_SAMPLES) + phases[:, np.newaxis])),
        axis=0)
    frequency_estimator = FftParabolicInterpolationFrequencyEstimator(
        samples, SAMPLING_FREQUENCY, FFT_LENGTH, window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequencies[np.argmax(self.amplitudes)],
                rtol=0.005))

    def test_estimate_multiple_frequencies(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_multiple_frequencies(
                    len(self.frequencies)),
                self.frequencies[np.argsort(self.amplitudes)[::-1]],
                rtol=0.005))


class FftJacobsenFrequencyEstimatorSingleTestCase(absltest.TestCase):

    frequency = 37
    phase = 0
    samples = np.exp(
        1j *
        (2 * np.pi * frequency / SAMPLING_FREQUENCY * np.arange(NUM_SAMPLES) +
         phase))
    frequency_estimator = FftJacobsenFrequencyEstimator(
        samples, SAMPLING_FREQUENCY, FFT_LENGTH, window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequency))


class FftJacobsenFrequencyEstimatorMultipleTestCase(absltest.TestCase):

    frequencies = np.array([5, 37])
    phases = np.array([0, 1.4])
    amplitudes = np.array([1, 0.7])
    samples = np.sum(
        amplitudes[:, np.newaxis] *
        np.exp(1j *
               (2 * np.pi * frequencies[:, np.newaxis] / SAMPLING_FREQUENCY *
                np.arange(NUM_SAMPLES) + phases[:, np.newaxis])),
        axis=0)
    frequency_estimator = FftJacobsenFrequencyEstimator(
        samples, SAMPLING_FREQUENCY, FFT_LENGTH, window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequencies[np.argmax(self.amplitudes)],
                rtol=0.002))

    def test_estimate_multiple_frequencies(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_multiple_frequencies(
                    len(self.frequencies)),
                self.frequencies[np.argsort(self.amplitudes)[::-1]],
                rtol=0.002))


class FftWindowedJacobsenFrequencyEstimatorSingleTestCase(absltest.TestCase):

    frequency = 37
    phase = 0
    samples = np.exp(
        1j *
        (2 * np.pi * frequency / SAMPLING_FREQUENCY * np.arange(NUM_SAMPLES) +
         phase))
    frequency_estimator = FftWindowedJacobsenFrequencyEstimator(
        samples,
        SAMPLING_FREQUENCY,
        FFT_LENGTH,
        window=np.hanning(NUM_SAMPLES + 2)[1:-1],
        window_type=FftWindow.HANN)

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequency))


class FftWindowedJacobsenFrequencyEstimatorMultipleTestCase(absltest.TestCase):

    frequencies = np.array([5, 37])
    phases = np.array([0, 1.4])
    amplitudes = np.array([1, 0.7])
    samples = np.sum(
        amplitudes[:, np.newaxis] *
        np.exp(1j *
               (2 * np.pi * frequencies[:, np.newaxis] / SAMPLING_FREQUENCY *
                np.arange(NUM_SAMPLES) + phases[:, np.newaxis])),
        axis=0)
    frequency_estimator = FftWindowedJacobsenFrequencyEstimator(
        samples,
        SAMPLING_FREQUENCY,
        FFT_LENGTH,
        window=np.hanning(NUM_SAMPLES + 2)[1:-1],
        window_type=FftWindow.HANN)

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequencies[np.argmax(self.amplitudes)],
                rtol=1e-6))

    def test_estimate_multiple_frequencies(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_multiple_frequencies(
                    len(self.frequencies)),
                self.frequencies[np.argsort(self.amplitudes)[::-1]],
                rtol=1e-6))


class FftTwoPointDtftFrequencyEstimatorSingleTestCase(absltest.TestCase):

    frequency = 37
    phase = 0
    samples = np.exp(
        1j *
        (2 * np.pi * frequency / SAMPLING_FREQUENCY * np.arange(NUM_SAMPLES) +
         phase))
    frequency_estimator = FftTwoPointDtftFrequencyEstimator(
        samples, SAMPLING_FREQUENCY, FFT_LENGTH, window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequency))


class FftTwoPointDtftFrequencyEstimatorMultipleTestCase(absltest.TestCase):

    frequencies = np.array([5, 37])
    phases = np.array([0, 1.4])
    amplitudes = np.array([1, 0.7])
    samples = np.sum(
        amplitudes[:, np.newaxis] *
        np.exp(1j *
               (2 * np.pi * frequencies[:, np.newaxis] / SAMPLING_FREQUENCY *
                np.arange(NUM_SAMPLES) + phases[:, np.newaxis])),
        axis=0)
    frequency_estimator = FftTwoPointDtftFrequencyEstimator(
        samples, SAMPLING_FREQUENCY, FFT_LENGTH, window=np.ones(NUM_SAMPLES))

    def test_estimate_single_frequency(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_single_frequency(),
                self.frequencies[np.argmax(self.amplitudes)],
                rtol=0.0005))

    def test_estimate_multiple_frequencies(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.frequency_estimator.estimate_multiple_frequencies(
                    len(self.frequencies)),
                self.frequencies[np.argsort(self.amplitudes)[::-1]],
                rtol=0.0005))


if __name__ == "__main__":
    absltest.main()
