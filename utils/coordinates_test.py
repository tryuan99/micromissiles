import numpy as np
from absl.testing import absltest

from utils.coordinates import CartesianCoordinates, SphericalCoordinates


class CartesianCoordinatesTestCase(absltest.TestCase):

    cartesian_coordinates = CartesianCoordinates(2, -1, 3)

    def test_transform_to_spherical(self):
        spherical_coordinates = (
            self.cartesian_coordinates.transform_to_spherical())
        self.assertAlmostEqual(spherical_coordinates.range, np.sqrt(14))
        self.assertAlmostEqual(spherical_coordinates.azimuth, -0.5880026)
        self.assertAlmostEqual(spherical_coordinates.elevation, -0.2705498)

    def test_transform_to_spherical_identity(self):
        spherical_coordinates = (
            self.cartesian_coordinates.transform_to_spherical())
        transformed_cartesian_coordinates = (
            spherical_coordinates.transform_to_cartesian())
        self.assertAlmostEqual(transformed_cartesian_coordinates.x,
                               self.cartesian_coordinates.x)
        self.assertAlmostEqual(transformed_cartesian_coordinates.y,
                               self.cartesian_coordinates.y)
        self.assertAlmostEqual(transformed_cartesian_coordinates.z,
                               self.cartesian_coordinates.z)

    def test_signed_azimuth(self):
        cartesian_coordinates = CartesianCoordinates(0,
                                                     np.sqrt(2) / 2,
                                                     -np.sqrt(2) / 2)
        spherical_coordinates = cartesian_coordinates.transform_to_spherical()
        self.assertAlmostEqual(spherical_coordinates.range, 1)
        self.assertAlmostEqual(spherical_coordinates.azimuth, -np.pi)
        self.assertAlmostEqual(spherical_coordinates.elevation, np.pi / 4)


class SphericalCoordinatesTestCase(absltest.TestCase):

    spherical_coordinates = SphericalCoordinates(2, np.pi / 6, np.pi / 3)

    def test_transform_to_cartesian(self):
        cartesian_coordinates = (
            self.spherical_coordinates.transform_to_cartesian())
        self.assertAlmostEqual(cartesian_coordinates.x, -1 / 2)
        self.assertAlmostEqual(cartesian_coordinates.y, np.sqrt(3))
        self.assertAlmostEqual(cartesian_coordinates.z, np.sqrt(3) / 2)

    def test_transform_to_cartesian_identity(self):
        cartesian_coordinates = (
            self.spherical_coordinates.transform_to_cartesian())
        transformed_spherical_coordinates = (
            cartesian_coordinates.transform_to_spherical())
        self.assertAlmostEqual(transformed_spherical_coordinates.range,
                               self.spherical_coordinates.range)
        self.assertAlmostEqual(transformed_spherical_coordinates.azimuth,
                               self.spherical_coordinates.azimuth)
        self.assertAlmostEqual(transformed_spherical_coordinates.elevation,
                               self.spherical_coordinates.elevation)


if __name__ == "__main__":
    absltest.main()
