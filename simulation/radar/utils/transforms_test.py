import numpy as np
from absl.testing import absltest

from simulation.radar.utils import transforms


class TransformsTestCase(absltest.TestCase):

    def test_czt(self):
        x = np.array([2, 0, -1, 0])
        M = 4
        A = 1
        W = np.exp(-1j * 2 * np.pi / M)
        X_z_expected = np.array([1, 3, 1, 3])

        X_z = transforms.czt(x, M, A, W)
        self.assertIsNone(np.testing.assert_allclose(X_z, X_z_expected))

    def test_dft(self):
        x = np.array([2, 0, -1, 0])
        M = 8
        X_k_expected = np.array([1, 2 + 1j, 3, 2 - 1j, 1, 2 + 1j, 3, 2 - 1j])

        X_k = transforms.dft(x, M)
        self.assertIsNone(np.testing.assert_allclose(X_k, X_k_expected))

    def test_z(self):
        x = np.array([2, 0, -1, 0])
        z_k = np.array(
            [1, np.exp(1j * np.pi / 2), 0.25 * np.exp(1j * np.pi / 3)])
        X_z_expected = np.array([1, 3, 2 - 16 * np.exp(-1j * 2 * np.pi / 3)])

        X_z = transforms.z(x, z_k)
        self.assertIsNone(np.testing.assert_allclose(X_z, X_z_expected))


if __name__ == "__main__":
    absltest.main()
