import numpy as np
from absl.testing import absltest

from simulation.radar.components.coordinates import (CartesianCoordinates,
                                                     PolarCoordinates)


class CartesianCoordinatesTestCase(absltest.TestCase):

    cartesian_coordinates = CartesianCoordinates(2, -1, 3)

    def test_transform_to_polar(self):
        polar_coordinates = self.cartesian_coordinates.transform_to_polar()
        self.assertAlmostEqual(polar_coordinates.r, np.sqrt(14))
        self.assertAlmostEqual(polar_coordinates.theta, -0.5880026)
        self.assertAlmostEqual(polar_coordinates.phi, -0.2705498)

    def test_transform_to_polar_identity(self):
        polar_coordinates = self.cartesian_coordinates.transform_to_polar()
        transformed_cartesian_coordinates = polar_coordinates.transform_to_cartesian(
        )
        self.assertAlmostEqual(transformed_cartesian_coordinates.x,
                               self.cartesian_coordinates.x)
        self.assertAlmostEqual(transformed_cartesian_coordinates.y,
                               self.cartesian_coordinates.y)
        self.assertAlmostEqual(transformed_cartesian_coordinates.z,
                               self.cartesian_coordinates.z)


class PolarCoordinatesTestCase(absltest.TestCase):

    polar_coordinates = PolarCoordinates(2, np.pi / 6, np.pi / 3)

    def test_transform_to_cartesian(self):
        cartesian_coordinates = self.polar_coordinates.transform_to_cartesian()
        self.assertAlmostEqual(cartesian_coordinates.x, -1 / 2)
        self.assertAlmostEqual(cartesian_coordinates.y, np.sqrt(3))
        self.assertAlmostEqual(cartesian_coordinates.z, np.sqrt(3) / 2)

    def test_transform_to_cartesian_identity(self):
        cartesian_coordinates = self.polar_coordinates.transform_to_cartesian()
        transformed_polar_coordinates = cartesian_coordinates.transform_to_polar(
        )
        self.assertAlmostEqual(transformed_polar_coordinates.r,
                               self.polar_coordinates.r)
        self.assertAlmostEqual(transformed_polar_coordinates.theta,
                               self.polar_coordinates.theta)
        self.assertAlmostEqual(transformed_polar_coordinates.phi,
                               self.polar_coordinates.phi)


if __name__ == "__main__":
    absltest.main()
