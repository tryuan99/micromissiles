import numpy as np
from absl.testing import absltest

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.chirp_processor import (
    LinearChirpFftProcessor, LinearChirpMatchedFilterProcessor)


class ChirpProcessorTestCase(absltest.TestCase):

    radar = Radar()
    radar.N_r = 2
    radar.N_bins_r = 4

    all_ones_samples = Samples(np.ones(radar.N_r))
    samples = Samples(np.array([1, -1]))


class LinearChirpFftProcessorTestCase(ChirpProcessorTestCase):

    def test_apply_window(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.all_ones_samples,
                                                      self.radar)
        self.assertIsNone(
            np.testing.assert_allclose(chirp_fft_processor.get_window(),
                                       self.radar.window_r))
        chirp_fft_processor.apply_window()
        self.assertIsNone(
            np.testing.assert_allclose(chirp_fft_processor.samples,
                                       self.radar.window_r))

    def test_get_output_axis(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.samples, self.radar)
        self.assertIsNone(
            np.testing.assert_allclose(chirp_fft_processor.get_output_axis(),
                                       self.radar.r_axis))

    def test_get_output_shape(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.samples, self.radar)
        self.assertTupleEqual(chirp_fft_processor.get_output_shape(),
                              (self.radar.N_bins_r,))

    def test_r_max(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.samples, self.radar)
        self.assertAlmostEqual(chirp_fft_processor.r_max, self.radar.r_max)

    def test_r_res(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.samples, self.radar)
        self.assertAlmostEqual(chirp_fft_processor.r_res, self.radar.r_res)

    def test_process_samples(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.samples, self.radar)
        chirp_fft_processor.process_samples()
        self.assertIsNone(
            np.testing.assert_allclose(chirp_fft_processor.samples,
                                       np.array([0, 1 + 1j, 2, 1 - 1j])))

    def test_estimate_peak(self):
        chirp_fft_processor = LinearChirpFftProcessor(self.samples, self.radar)
        chirp_fft_processor.process_samples()
        self.assertIsNone(
            np.testing.assert_allclose(chirp_fft_processor.estimate_peak(),
                                       (self.radar.r_max / 2)))


class LinearChirpMatchedFilterProcessorTestCase(ChirpProcessorTestCase):

    def test_process_samples(self):
        linear_chirp_processor = LinearChirpMatchedFilterProcessor(
            self.samples, self.radar)
        linear_chirp_processor.process_samples()
        self.assertIsNone(
            np.testing.assert_allclose(linear_chirp_processor.samples,
                                       np.array([0, 1 + 1j, 2, 1 - 1j])))


if __name__ == "__main__":
    absltest.main()
