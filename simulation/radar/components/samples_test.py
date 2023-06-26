import numpy as np
from absl.testing import absltest

from simulation.radar.components.samples import Samples


class SamplesTestCase(absltest.TestCase):

    raw_samples = np.array([[1 - 1j, 2 + 1j, 2 + 2j], [3, 2j, 1 + 1j]])
    samples = Samples(raw_samples)

    def test_init(self):
        copied_raw_samples = np.copy(self.raw_samples)
        self.raw_samples[0, 0] = 100
        self.assertIsNone(
            np.testing.assert_allclose(self.samples.samples,
                                       copied_raw_samples))

    def test_copy(self):
        copied_samples = Samples(self.samples)
        copied_samples.samples[0, 0] = 100
        self.assertIsNone(
            np.testing.assert_allclose(self.samples.samples, self.raw_samples))

    def test_add_scalar(self):
        added_samples = self.samples + 4
        self.assertIsNone(
            np.testing.assert_allclose(
                added_samples.samples,
                np.array([[5 - 1j, 6 + 1j, 6 + 2j], [7, 4 + 2j, 5 + 1j]])))

    def test_add_samples(self):
        added_samples = (
            self.samples +
            Samples(np.array([[2 - 2j, 3, 1j], [3 - 1j, 2 + 1j, 2]])))
        self.assertIsNone(
            np.testing.assert_allclose(
                added_samples.samples,
                np.array([[3 - 3j, 5 + 1j, 2 + 3j], [6 - 1j, 2 + 3j, 3 + 1j]])))

    def test_mul_scalar(self):
        scaled_samples = self.samples * 3
        self.assertIsNone(
            np.testing.assert_allclose(
                scaled_samples.samples,
                np.array([[3 - 3j, 6 + 3j, 6 + 6j], [9, 6j, 3 + 3j]])))

    def test_mul_samples(self):
        scaled_samples = (self.samples *
                          Samples(np.array([[0, 2, 1], [2, 3, 4]])))
        self.assertIsNone(
            np.testing.assert_allclose(
                scaled_samples.samples,
                np.array([[0, 4 + 2j, 2 + 2j], [6, 6j, 4 + 4j]])))

    def test_shape(self):
        self.assertTupleEqual(self.samples.shape, (2, 3))

    def test_ndim(self):
        self.assertEqual(self.samples.ndim, 2)

    def test_size(self):
        self.assertEqual(self.samples.size, 6)

    def test_get_abs_samples(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.samples.get_abs_samples(),
                np.abs(np.array([[1 - 1j, 2 + 1j, 2 + 2j], [3, 2j, 1 + 1j]]))))

    def test_get_amplitude(self):
        self.assertAlmostEqual(self.samples.get_amplitude(), 2.236068)


if __name__ == "__main__":
    absltest.main()
