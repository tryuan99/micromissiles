import numpy as np
from absl.testing import absltest

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayArrival,
                                              AntennaArrayElement)


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
