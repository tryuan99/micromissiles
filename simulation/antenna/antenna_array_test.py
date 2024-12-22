import numpy as np
from absl.testing import absltest

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayArrival,
                                              AntennaArrayElement)
from utils.quaternion import RotationQuaternion


class AntennaArrayElementTestCase(absltest.TestCase):

    def test_coordinates(self):
        element = AntennaArrayElement(x=1, y=2, z=3)
        np.testing.assert_array_equal(
            element.coordinates(),
            np.array([1, 2, 3]),
        )

    def test_boresight(self):
        element = AntennaArrayElement(x=1, y=2, z=3)
        np.testing.assert_array_equal(
            element.boresight(),
            np.array([0, 0, 1]),
        )
        element = AntennaArrayElement(
            x=1,
            y=2,
            z=3,
            orientation=RotationQuaternion(
                theta=np.pi / 2,
                axis=np.array([0, 1, 0]),
            ),
        )
        np.testing.assert_allclose(
            element.boresight(),
            np.array([1, 0, 0]),
            atol=1e-12,
        )

    def test_vertical(self):
        element = AntennaArrayElement(x=1, y=2, z=3)
        np.testing.assert_array_equal(
            element.vertical(),
            np.array([0, 1, 0]),
        )
        element = AntennaArrayElement(
            x=1,
            y=2,
            z=3,
            orientation=RotationQuaternion(
                theta=np.pi / 2,
                axis=np.array([1, 0, 0]),
            ),
        )
        np.testing.assert_allclose(
            element.vertical(),
            np.array([0, 0, 1]),
            atol=1e-12,
        )

    def test_right(self):
        element = AntennaArrayElement(x=1, y=2, z=3)
        np.testing.assert_array_equal(
            element.right(),
            np.array([-1, 0, 0]),
        )
        element = AntennaArrayElement(
            x=1,
            y=2,
            z=3,
            orientation=RotationQuaternion(
                theta=-np.pi / 2,
                axis=np.array([0, 0, 1]),
            ),
        )
        np.testing.assert_allclose(
            element.right(),
            np.array([0, 1, 0]),
            atol=1e-12,
        )


class AntennaArrayTestCase(absltest.TestCase):

    def compare_spatial_samples(self, arrival: AntennaArrayArrival,
                                spatial_samples: np.ndarray):
        np.testing.assert_allclose(
            self.antenna_array.get_spatial_samples(arrival), spatial_samples)

    def test_horizontal_ula(self):
        elements = [
            AntennaArrayElement(x=0),
            AntennaArrayElement(x=1),
            AntennaArrayElement(x=2)
        ]
        self.antenna_array = AntennaArray(elements)
        self.compare_spatial_samples(AntennaArrayArrival(azimuth=0),
                                     np.exp(1j * np.zeros(len(elements))))
        self.compare_spatial_samples(
            AntennaArrayArrival(azimuth=np.pi / 6),
            np.exp(1j * 2 * np.pi * np.array([0, 1 / 2, 1])))
        self.compare_spatial_samples(
            AntennaArrayArrival(azimuth=-np.pi / 6),
            np.exp(-1j * 2 * np.pi * np.array([0, 1 / 2, 1])))
        self.compare_spatial_samples(AntennaArrayArrival(elevation=np.pi / 2),
                                     np.exp(1j * np.zeros(len(elements))))

    def test_vertical_ula(self):
        elements = [
            AntennaArrayElement(y=0),
            AntennaArrayElement(y=1),
            AntennaArrayElement(y=2)
        ]
        self.antenna_array = AntennaArray(elements)
        self.compare_spatial_samples(AntennaArrayArrival(elevation=0),
                                     np.exp(1j * np.zeros(len(elements))))
        self.compare_spatial_samples(
            AntennaArrayArrival(elevation=np.pi / 6),
            np.exp(-1j * 2 * np.pi * np.array([0, 1 / 2, 1])))
        self.compare_spatial_samples(
            AntennaArrayArrival(elevation=-np.pi / 6),
            np.exp(1j * 2 * np.pi * np.array([0, 1 / 2, 1])))
        self.compare_spatial_samples(AntennaArrayArrival(azimuth=np.pi / 2),
                                     np.exp(1j * np.zeros(len(elements))))

    def test_amplitude(self):
        elements = [
            AntennaArrayElement(x=0),
            AntennaArrayElement(x=1),
            AntennaArrayElement(x=2)
        ]
        self.antenna_array = AntennaArray(elements)
        amplitude = 5
        np.testing.assert_allclose(
            np.abs(
                self.antenna_array.get_spatial_samples(
                    AntennaArrayArrival(amplitude=amplitude))),
            np.ones(len(elements)) * amplitude)
        amplitude = np.hanning(len(elements) + 2)[1:-1]
        np.testing.assert_allclose(
            np.abs(
                self.antenna_array.get_spatial_samples(
                    AntennaArrayArrival(amplitude=amplitude))),
            np.ones(len(elements)) * amplitude)


if __name__ == "__main__":
    absltest.main()
