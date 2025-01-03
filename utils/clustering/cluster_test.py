import numpy as np
from absl.testing import absltest

from utils.clustering.cluster import Cluster, Point


class PointTestCase(absltest.TestCase):

    def test_coordinates(self):
        point = Point(x=1, y=2, z=3)
        np.testing.assert_allclose(point.coordinates(), np.array([1, 2, 3]))

    def test_calculate_distance(self):
        point = Point(x=1, y=2, z=3)
        other = Point(x=3, y=-2, z=0)
        self.assertAlmostEqual(
            point.calculate_distance(other),
            np.linalg.norm(np.array([3, -2, 0]) - np.array([1, 2, 3])))


class ClusterTestCase(absltest.TestCase):

    @staticmethod
    def generate_cluster(points: list[Point]) -> Cluster:
        cluster = Cluster()
        cluster.add_points(points)
        cluster.recenter()
        return cluster

    def test_size(self):
        size = 10
        cluster = self.generate_cluster([Point(x=0, y=i) for i in range(size)])
        self.assertEqual(cluster.size(), size)

    def test_empty(self):
        cluster = Cluster()
        self.assertTrue(cluster.empty())
        cluster.add_point(Point(x=0, y=0))
        self.assertFalse(cluster.empty())

    def test_radius(self):
        radius = 5
        cluster = self.generate_cluster(
            [Point(x=0, y=radius), Point(x=0, y=-radius)])
        self.assertAlmostEqual(cluster.radius(), radius)

    def test_centroid(self):
        radius = 3
        cluster = self.generate_cluster([
            Point(x=x * radius, y=y * radius) for x in [-1, 1] for y in [-1, 1]
        ])
        np.testing.assert_allclose(cluster.centroid(), np.zeros(3))

    def test_recenter(self):
        radius = 3
        cluster = self.generate_cluster([
            Point(x=x * radius, y=y * radius) for x in [-1, 1] for y in [-1, 1]
        ])
        cluster.add_point(Point(x=5, y=-5))
        cluster.recenter()
        np.testing.assert_allclose(cluster.centroid(), np.array([1, -1, 0]))

    def test_merge_cluster(self):
        size = 10
        cluster1 = self.generate_cluster([Point(x=0, y=i) for i in range(size)])
        size1 = cluster1.size()
        centroid1 = cluster1.centroid()
        cluster2 = self.generate_cluster([Point(x=i, y=0) for i in range(size)])
        size2 = cluster2.size()
        centroid2 = cluster2.centroid()
        cluster1.merge_cluster(cluster2)
        cluster1.recenter()
        self.assertEqual(cluster1.size(), size1 + size2)
        np.testing.assert_allclose(cluster1.centroid(),
                                   np.mean([centroid1, centroid2], axis=0))


if __name__ == "__main__":
    absltest.main()
