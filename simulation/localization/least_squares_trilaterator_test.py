import numpy as np
from absl.testing import absltest

from simulation.localization.least_squares_trilaterator import \
    LeastSquaresTrilaterator
from utils.coordinates import CartesianCoordinates


class LeastSquaresTrilateratorTestCase(absltest.TestCase):

    def test_trilaterate_around_origin(self):
        positions = [
            CartesianCoordinates(x=-1, y=-1, z=0),
            CartesianCoordinates(x=-1, y=1, z=0),
            CartesianCoordinates(x=1, y=-1, z=0),
            CartesianCoordinates(x=1, y=1, z=0),
        ]
        ranges = np.ones(4) * np.sqrt(2)
        trilaterator = LeastSquaresTrilaterator(positions, ranges)
        result = trilaterator.trilaterate()
        expected_result = np.array([0, 0, 0])
        np.testing.assert_allclose(result, expected_result)

    def test_trilaterate_with_offset(self):
        positions = [
            CartesianCoordinates(x=4, y=2, z=0),
            CartesianCoordinates(x=4, y=4, z=0),
            CartesianCoordinates(x=6, y=2, z=0),
            CartesianCoordinates(x=6, y=4, z=0),
        ]
        ranges = np.ones(4) * np.sqrt(2)
        trilaterator = LeastSquaresTrilaterator(positions, ranges)
        result = trilaterator.trilaterate()
        expected_result = np.array([5, 3, 0])
        np.testing.assert_allclose(result, expected_result)

    def test_trilaterate_noise(self):
        positions = [
            CartesianCoordinates(x=4, y=2, z=0),
            CartesianCoordinates(x=4, y=4, z=0),
            CartesianCoordinates(x=6, y=2, z=0),
            CartesianCoordinates(x=6, y=4, z=0),
        ]
        ranges = np.ones(4) * 2
        trilaterator = LeastSquaresTrilaterator(positions, ranges)
        result = trilaterator.trilaterate()
        expected_result = np.array([5, 3, 0])
        np.testing.assert_allclose(result, expected_result)

    def test_trilaterate_3d(self):
        positions = [
            CartesianCoordinates(x=100, y=20, z=10),
            CartesianCoordinates(x=100, y=-20, z=100),
            CartesianCoordinates(x=50, y=20, z=-10),
            CartesianCoordinates(x=0, y=-20, z=20),
        ]
        ranges = np.array([9990.545531, 9900.752497, 10011.168763, 9982.249246])
        trilaterator = LeastSquaresTrilaterator(positions, ranges)
        result = trilaterator.trilaterate()
        expected_result = np.array([200, 50, 10000])
        np.testing.assert_allclose(result, expected_result, rtol=1e-5)

    def test_trilaterate_3d_symmetric(self):
        positions = [
            CartesianCoordinates(x=-50, y=0, z=0),
            CartesianCoordinates(x=50, y=0, z=0),
            CartesianCoordinates(x=0, y=-50, z=0),
            CartesianCoordinates(x=0, y=50, z=10),
        ]
        ranges = np.array([61.644140, 42.426407, 61.644140, 41.231056])
        trilaterator = LeastSquaresTrilaterator(positions, ranges)
        result = trilaterator.trilaterate()
        expected_result = np.array([10, 10, 10])
        np.testing.assert_allclose(result, expected_result, rtol=1e-5)


if __name__ == "__main__":
    absltest.main()
