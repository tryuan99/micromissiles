from abc import ABC, abstractmethod

import numpy as np
from absl.testing import absltest

from simulation.radar.components.peak_selector import PeakSelector
from simulation.radar.components.samples import Samples


class PeakSelectorTestCase(ABC):

    def test_get_largest_peak_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_largest_peak_index(),
                self.peak_selector.get_kth_largest_peak_index(0)))

    def test_get_largest_peak_magnitude(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_largest_peak_magnitude(),
                self.peak_selector.get_kth_largest_peak_magnitude(0)))

    @abstractmethod
    def test_get_kth_largest_peak_index(self):
        pass

    @abstractmethod
    def test_get_kth_largest_peak_magnitude(self):
        pass

    @abstractmethod
    def test_get_k_largest_peaks_index(self):
        pass

    @abstractmethod
    def test_get_k_largest_peaks_magnitude(self):
        pass


class OneDimensionalPeakSelectorTestCase(PeakSelectorTestCase,
                                         absltest.TestCase):

    samples = Samples(
        np.array([1 - 1j, 2 + 2j, 5 - 3j, 4 + 3j, 2 + 2j, 4 - 4j, 3 + 3j]))
    peak_selector = PeakSelector(samples)

    def test_get_kth_largest_peak_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(0),
                np.array([2])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(1),
                np.array([5])))

    def test_get_kth_largest_peak_magnitude(self):
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(0),
            np.abs(5 - 3j))
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(1),
            np.abs(4 + 4j))

    def test_get_k_largest_peaks_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(0),
                (np.array([]),)))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(1),
                (np.array([2]),)))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(3),
                (np.array([2, 5, 3]),)))

    def test_get_k_largest_peaks_magnitude(self):
        self.assertIsNone(
            np.testing.assert_allclose(
                self.peak_selector.get_k_largest_peaks_magnitude(0),
                np.array([])))
        self.assertIsNone(
            np.testing.assert_allclose(
                self.peak_selector.get_k_largest_peaks_magnitude(1),
                np.abs(np.array([5 - 3j]))))
        self.assertIsNone(
            np.testing.assert_allclose(
                self.peak_selector.get_k_largest_peaks_magnitude(3),
                np.abs(np.array([5 - 3j, 4 + 4j, 4 - 3j]))))


class MultiDimensionalPeakSelectorTestCase(PeakSelectorTestCase,
                                           absltest.TestCase):

    samples = Samples(
        np.array([
            [4 + 1j, 6, 4 + 1j, 1 + 1j, 6 - 1j, 9 - 1j, 3, 5 + 1j],
            [2 + 1j, 4 - 1j, 2 - 2j, 5 + 1j, 7 - 1j, 7, 9, 3 + 2j],
            [3 + 2j, 2, 1 + 1j, 4, 3 - 1j, 2 - 1j, 4 + 1j, 6 - 2j],
        ]))
    peak_selector = PeakSelector(samples)

    def test_get_kth_largest_peak_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(0),
                np.array([0, 5])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(1),
                np.array([1, 6])))

    def test_get_kth_largest_peak_magnitude(self):
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(0),
            np.abs(9 - 1j))
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(1), np.abs(9))

    def test_get_k_largest_peaks_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(0),
                (np.array([]), np.array([]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(1),
                (np.array([0]), np.array([5]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(3),
                (np.array([0, 1, 1]), np.array([5, 6, 4]))))

    def test_get_k_largest_peaks_magnitude(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(0),
                np.array([])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(1),
                np.abs(np.array([9 - 1j]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(3),
                np.abs(np.array([9 - 1j, 9, 7 - 1j]))))


class MultiDimensionalPeakSelectorWithGuardLengthTestCase(
        PeakSelectorTestCase, absltest.TestCase):

    samples = Samples(
        np.array([
            [4 + 1j, 6, 4 + 1j, 1 + 1j, 6 - 1j, 9 - 1j, 3, 5 + 1j],
            [2 + 1j, 4 - 1j, 2 - 2j, 5 + 1j, 7 - 1j, 7, 9, 3 + 2j],
            [3 + 2j, 2, 1 + 1j, 4, 3 - 1j, 2 - 1j, 4 + 1j, 6 - 2j],
        ]))
    peak_selector = PeakSelector(samples, guard_length=1)

    def test_get_kth_largest_peak_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(0),
                np.array([0, 5])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(1),
                np.array([2, 7])))

    def test_get_kth_largest_peak_magnitude(self):
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(0),
            np.abs(9 - 1j))
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(1),
            np.abs(6 - 2j))

    def test_get_k_largest_peaks_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(0),
                (np.array([]), np.array([]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(1),
                (np.array([0]), np.array([5]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(3),
                (np.array([0, 2, 0]), np.array([5, 7, 1]))))

    def test_get_k_largest_peaks_magnitude(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(0),
                np.array([])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(1),
                np.abs(np.array([9 - 1j]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(3),
                np.abs(np.array([9 - 1j, 6 - 2j, 6]))))


class MultiDimensionalPeakSelectorWithGuardLengthNoWrapTestCase(
        PeakSelectorTestCase, absltest.TestCase):

    samples = Samples(
        np.array([
            [4 + 1j, 6, 4 + 1j, 1 + 1j, 6 - 1j, 9 - 1j, 3, 5 + 1j],
            [2 + 1j, 4 - 1j, 2 - 2j, 5 + 1j, 7 - 1j, 7, 9, 3 + 2j],
            [3 + 2j, 2, 1 + 1j, 4, 3 - 1j, 2 - 1j, 4 + 1j, 6 - 2j],
        ]))
    peak_selector = PeakSelector(samples, guard_length=1, wrap=False)

    def test_get_kth_largest_peak_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(0),
                np.array([0, 5])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_kth_largest_peak_index(1),
                np.array([2, 7])))

    def test_get_kth_largest_peak_magnitude(self):
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(0),
            np.abs(9 - 1j))
        self.assertAlmostEqual(
            self.peak_selector.get_kth_largest_peak_magnitude(1),
            np.abs(6 - 2j))

    def test_get_k_largest_peaks_index(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(0),
                (np.array([]), np.array([]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(1),
                (np.array([0]), np.array([5]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_index(3),
                (np.array([0, 2, 0]), np.array([5, 7, 1]))))

    def test_get_k_largest_peaks_magnitude(self):
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(0),
                np.array([])))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(1),
                np.abs(np.array([9 - 1j]))))
        self.assertIsNone(
            np.testing.assert_array_equal(
                self.peak_selector.get_k_largest_peaks_magnitude(3),
                np.abs(np.array([9 - 1j, 6 - 2j, 6]))))


if __name__ == "__main__":
    absltest.main()
