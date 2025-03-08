import numpy as np
from absl.testing import absltest

from simulation.localization.least_squares_trilaterator import \
    LeastSquaresTrilaterator
from simulation.localization.nonlinear_least_squares_trilaterator import \
    NonlinearLeastSquaresTrilaterator
from simulation.localization.trilaterator_factory import TrilateratorFactory
from utils.coordinates import CartesianCoordinates


class TrilateratorFactoryTestCase(absltest.TestCase):

    positions = [CartesianCoordinates(x=0, y=0, z=0) for _ in range(4)]
    ranges = np.zeros(len(positions))

    def test_least_squares_trilaterator(self):
        trilaterator = TrilateratorFactory.create_trilaterator(
            "least_squares",
            self.positions,
            self.ranges,
        )
        self.assertIsInstance(trilaterator, LeastSquaresTrilaterator)

    def test_nonlinear_least_squares_trilaterator(self):
        trilaterator = TrilateratorFactory.create_trilaterator(
            "nonlinear_least_squares",
            self.positions,
            self.ranges,
        )
        self.assertIsInstance(trilaterator, NonlinearLeastSquaresTrilaterator)

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            TrilateratorFactory.create_trilaterator(
                "invalid",
                self.positions,
                self.ranges,
            )


if __name__ == "__main__":
    absltest.main()
