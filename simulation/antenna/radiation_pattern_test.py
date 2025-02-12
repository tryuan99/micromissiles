import numpy as np
from absl.testing import absltest

from simulation.antenna.radiation_pattern import RadiationPattern
from utils import constants


class RadiationPatternTestCase(absltest.TestCase):

    def test_shapes(self):
        azimuth_shape = 6
        elevation_shape = 4
        shape = (azimuth_shape, elevation_shape)
        radiation_pattern = RadiationPattern(np.zeros(shape), 1, 1)
        self.assertEqual(radiation_pattern.radiation_pattern.shape, shape)
        self.assertEqual(radiation_pattern.azimuth.shape, shape)
        self.assertEqual(radiation_pattern.elevation.shape, shape)

    def test_db(self):
        power_magnitude = np.array([[10, 5], [2, 0]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        np.testing.assert_array_equal(
            radiation_pattern.db(),
            constants.power2db(power_magnitude + 1),
        )

    def test_db_without_log_plus_one(self):
        power_magnitude = np.array([[10, 5], [2, 0]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        np.testing.assert_array_equal(
            radiation_pattern.db(log_plus_one=False),
            constants.power2db(power_magnitude),
        )

    def test_normalized_db(self):
        power_magnitude = np.array([[10, 5], [2, 0]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        np.testing.assert_array_equal(
            radiation_pattern.normalized_db(),
            constants.power2db(power_magnitude + 1) -
            radiation_pattern.max_db(),
        )

    def test_max(self):
        power_magnitude = np.array([[10, 5], [2, 0]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        self.assertEqual(radiation_pattern.max(), 10)

    def test_max_db(self):
        power_magnitude = np.array([[10, 5], [2, 0]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        self.assertEqual(
            radiation_pattern.max_db(),
            constants.power2db(10 + 1),
        )

    def test_min(self):
        power_magnitude = np.array([[10, 5], [2, 3]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        self.assertEqual(radiation_pattern.min(), 2)

    def test_min_db(self):
        power_magnitude = np.array([[10, 5], [2, 3]])
        radiation_pattern = RadiationPattern(power_magnitude, 1, 1)
        self.assertEqual(
            radiation_pattern.min_db(),
            constants.power2db(2 + 1),
        )

    def test_main_lobe_width_1d(self):
        power_magnitude = np.array([1, 2, 4, 5, 6, 7, 8, 7, 5, 3, 1])
        azimuth = np.arange(len(power_magnitude))
        radiation_pattern = RadiationPattern(power_magnitude, azimuth, 1)
        self.assertEqual(
            radiation_pattern.main_lobe_width(np.argmax(power_magnitude)),
            7,
        )

    def test_main_lobe_width_1d_wraparound(self):
        power_magnitude = np.array([7, 5, 3, 1, 1, 2, 4, 5, 6, 7, 8])
        azimuth = np.arange(len(power_magnitude))
        radiation_pattern = RadiationPattern(power_magnitude, azimuth, 1)
        self.assertEqual(
            radiation_pattern.main_lobe_width(np.argmax(power_magnitude)),
            7,
        )

    def test_main_lobe_width_1d_flat(self):
        power_magnitude = np.ones(8)
        azimuth = np.arange(len(power_magnitude))
        radiation_pattern = RadiationPattern(power_magnitude, azimuth, 1)
        self.assertEqual(
            radiation_pattern.main_lobe_width(np.argmax(power_magnitude)),
            8,
        )

    def test_main_lobe_width_2d(self):
        power_magnitude = np.array([
            [1, 1, 1, 1],
            [1, 1, 4, 1],
            [1, 1, 6, 1],
            [1, 1, 7, 1],
            [1, 4, 8, 3],
            [1, 1, 2, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
        ])
        azimuth, elevation = np.meshgrid(
            np.arange(power_magnitude.shape[0]),
            np.arange(power_magnitude.shape[1]),
            indexing="ij",
        )
        radiation_pattern = RadiationPattern(
            power_magnitude,
            azimuth,
            elevation,
        )
        np.testing.assert_array_equal(
            radiation_pattern.main_lobe_width(
                np.unravel_index(
                    np.argmax(power_magnitude),
                    power_magnitude.shape,
                )),
            np.array([4, 2]),
        )

    def test_main_lobe_width_2d_wraparound(self):
        power_magnitude = np.array([
            [1, 1, 1, 2],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 4],
            [1, 1, 1, 6],
            [1, 1, 1, 7],
            [3, 1, 4, 8],
        ])
        azimuth, elevation = np.meshgrid(
            np.arange(power_magnitude.shape[0]),
            np.arange(power_magnitude.shape[1]),
            indexing="ij",
        )
        radiation_pattern = RadiationPattern(
            power_magnitude,
            azimuth,
            elevation,
        )
        np.testing.assert_array_equal(
            radiation_pattern.main_lobe_width(
                np.unravel_index(
                    np.argmax(power_magnitude),
                    power_magnitude.shape,
                )),
            np.array([4, 2]),
        )

    def test_main_lobe_width_2d_flat(self):
        power_magnitude = np.ones((8, 4))
        azimuth, elevation = np.meshgrid(
            np.arange(power_magnitude.shape[0]),
            np.arange(power_magnitude.shape[1]),
            indexing="ij",
        )
        radiation_pattern = RadiationPattern(
            power_magnitude,
            azimuth,
            elevation,
        )
        np.testing.assert_array_equal(
            radiation_pattern.main_lobe_width(
                np.unravel_index(
                    np.argmax(power_magnitude),
                    power_magnitude.shape,
                )),
            np.array([8, 4]),
        )


if __name__ == "__main__":
    absltest.main()
