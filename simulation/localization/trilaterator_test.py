import numpy as np
from absl.testing import absltest

from simulation.localization.trilaterator import Trilaterator
from utils.coordinates import CartesianCoordinates


class MockTrilaterator(Trilaterator):
    """Mock trilaterator."""

    def __init__(
        self,
        positions: list[CartesianCoordinates],
        ranges: np.ndarray | list[float],
    ) -> None:
        super().__init__(positions, ranges)

    def trilaterate(self) -> CartesianCoordinates:
        """Trilaterate the target position.

        Returns:
            The estimated target position.
        """
        return CartesianCoordinates()


class TrilateratorTestCase(absltest.TestCase):

    def test_cramer_rao_lower_bound(self):
        positions = [
            CartesianCoordinates(x=-10, y=0, z=0),
            CartesianCoordinates(x=10, y=0, z=0),
            CartesianCoordinates(x=0, y=-10, z=0),
            CartesianCoordinates(x=0, y=10, z=0),
        ]
        ranges = np.ones(len(positions)) * np.sqrt(2) * 10
        target_position = np.array([0, 0, 10])
        trilaterator = MockTrilaterator(positions, ranges)
        crlb = trilaterator.cramer_rao_lower_bound(
            target_position,
            standard_deviations=np.array([1, 1, 1, 2]),
        )
        expected_crlb = np.linalg.inv(
            np.array([
                [1, 0, 0],
                [0, 0.625, 0.375],
                [0, 0.375, 1.625],
            ]))
        np.testing.assert_allclose(crlb, expected_crlb, atol=1e-12)


if __name__ == "__main__":
    absltest.main()
