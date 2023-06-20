import numpy as np
from absl.testing import absltest

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.range_doppler_processor import (
    RangeDopplerFftProcessor, RangeDopplerMatchedFilterProcessor)


class RangeDopplerProcessorTestCase(absltest.TestCase):

    radar = Radar()
    radar.N_r = 2
    radar.N_bins_r = 4
    radar.N_v = 4
    radar.N_bins_v = 4

    all_ones_samples = Samples(np.ones((radar.N_v, radar.N_r)))
    samples = Samples(np.array([
        [1, 1],
        [1j, 1j],
        [-1, -1],
        [-1j, -1j],
    ]))


class RangeDopplerFftProcessorTestCase(RangeDopplerProcessorTestCase):

    def test_apply_range_window(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.all_ones_samples, self.radar)
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_fft_processor.get_window_axis2(),
                self.radar.window_r))
        range_doppler_fft_processor.apply_window_axis2()
        for i in range(self.radar.N_v):
            self.assertIsNone(
                np.testing.assert_allclose(
                    range_doppler_fft_processor.samples[i],
                    self.radar.window_r))

    def test_apply_doppler_window(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.all_ones_samples, self.radar)
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_fft_processor.get_window_axis1(),
                self.radar.window_v))
        range_doppler_fft_processor.apply_window_axis1()
        for i in range(self.radar.N_r):
            self.assertIsNone(
                np.testing.assert_allclose(
                    range_doppler_fft_processor.samples[:, i],
                    self.radar.window_v))

    def test_get_range_axis(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.samples, self.radar)
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_fft_processor.get_output_axis2(),
                self.radar.r_axis))

    def test_get_doppler_axis(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.samples, self.radar)
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_fft_processor.get_output_axis1(),
                self.radar.v_axis))

    def test_get_output_shape(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.samples, self.radar)
        self.assertTupleEqual(range_doppler_fft_processor.get_output_shape(),
                              (self.radar.N_bins_v, self.radar.N_bins_r))

    def test_process_2d_samples(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.samples, self.radar)
        range_doppler_fft_processor.process_2d_samples()
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_fft_processor.samples,
                np.array([
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [8, 4 - 4j, 0, 4 + 4j],
                ])))

    def test_estimate_peak_bins(self):
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            self.samples, self.radar)
        range_doppler_fft_processor.process_2d_samples()
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_fft_processor.estimate_peak_bins(),
                (self.radar.v_max / 2, 0)))

    def test_accumulate_log_magnitude(self):
        a = self.samples.samples[np.newaxis, np.newaxis, ...]
        range_doppler_fft_processor = RangeDopplerFftProcessor(
            Samples(self.samples.samples[np.newaxis, np.newaxis, ...]),
            self.radar)
        range_doppler_fft_processor.process_2d_samples()
        accumulated_range_doppler_map = range_doppler_fft_processor.accumulate_log_magnitude(
        )
        self.assertIsNone(
            np.testing.assert_allclose(
                accumulated_range_doppler_map.samples,
                np.array([
                    [-np.inf, -np.inf, -np.inf, -np.inf],
                    [-np.inf, -np.inf, -np.inf, -np.inf],
                    [-np.inf, -np.inf, -np.inf, -np.inf],
                    [3, 2.5, -np.inf, 2.5],
                ])))


class RangeDopplerMatchedFilterProcessorTestCase(RangeDopplerProcessorTestCase):

    def test_process_2d_samples(self):
        range_doppler_matched_filter_processor = RangeDopplerMatchedFilterProcessor(
            self.samples, self.radar)
        range_doppler_matched_filter_processor.process_2d_samples()
        self.assertIsNone(
            np.testing.assert_allclose(
                range_doppler_matched_filter_processor.samples,
                np.array([
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [8, 4 - 4j, 0, 4 + 4j],
                ]),
                rtol=0.01,
                atol=0.05))


if __name__ == "__main__":
    absltest.main()
