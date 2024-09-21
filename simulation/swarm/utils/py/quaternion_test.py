import numpy as np
from absl.testing import absltest

from simulation.swarm.utils.py.quaternion import (PointQuaternion, Quaternion,
                                                  RotationQuaternion)


class QuaternionTestCase(absltest.TestCase):

    def test_add(self):
        p = Quaternion(s=1, v=np.array([1, 2, 3]))
        q = Quaternion(s=-5, v=np.array([1, 5, -3]))
        r = p.add(q)
        self.assertAlmostEqual(r.s, -4)
        np.testing.assert_allclose(r.v, np.array([2, 7, 0]))

    def test_multiply(self):
        p = PointQuaternion(x=2, y=0, z=0)
        q = Quaternion(
            s=np.cos(np.pi / 4),
            v=np.sin(np.pi / 4) *
            np.array([np.sqrt(2) / 2, 0, np.sqrt(2) / 2]))
        r = q.multiply(p)
        self.assertAlmostEqual(r.s, -1)
        np.testing.assert_allclose(r.v, np.array([np.sqrt(2), 1, 0]))

    def test_norm(self):
        q = Quaternion(s=1, v=np.array([1, 2, 3]))
        self.assertAlmostEqual(q.norm(), np.sqrt(15))

    def test_inverse(self):
        q = RotationQuaternion(theta=np.pi / 4, x=1, y=1, z=0)
        r = q.inverse()
        self.assertAlmostEqual(r.s, q.s)
        np.testing.assert_allclose(r.v, -q.v)

    def test_dot(self):
        p = Quaternion(s=1, v=np.array([1, 2, 3]))
        q = Quaternion(s=-5, v=np.array([1, 5, -3]))
        self.assertAlmostEqual(p.dot(q), -3)

    def test_rotate(self):
        p = PointQuaternion(x=1, y=1, z=0)
        q = RotationQuaternion(theta=np.pi / 2, x=1, y=0, z=0)
        r = p.rotate(q)
        self.assertAlmostEqual(r.s, 0)
        np.testing.assert_allclose(r.v, np.array([1, 0, 1]), atol=1e-12)

    def test_compose(self):
        p = PointQuaternion(x=1, y=1, z=0)
        q = RotationQuaternion(theta=np.pi / 2, x=1, y=0, z=0)
        r = RotationQuaternion(theta=3 * np.pi / 2, x=0, y=0, z=1)
        s = p.rotate(q).rotate(r)
        t = p.rotate(q.compose(r))
        self.assertAlmostEqual(s.s, t.s)
        np.testing.assert_allclose(s.v, t.v, atol=1e-12)


if __name__ == "__main__":
    absltest.main()
