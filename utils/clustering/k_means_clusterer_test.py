import numpy as np
from absl.testing import absltest

from utils.clustering.cluster import Point
from utils.clustering.k_means_clusterer import (ConstrainedKMeansClusterer,
                                                KMeansClusterer)

# List of points to cluster.
POINTS = [
    Point(x=0, y=0),
    Point(x=0, y=1),
    Point(x=0, y=1.5),
    Point(x=0, y=2.5),
]


class KMeansClustererTestCase(absltest.TestCase):

    def test_single_cluster(self):
        clusterer = KMeansClusterer(POINTS, k=1)
        clusterer.cluster()
        cluster = clusterer.clusters[0]
        self.assertEqual(cluster.size(), len(POINTS))
        np.testing.assert_allclose(cluster.centroid(), np.array([0, 1.25, 0]))


class ConstrainedKMeansClustererTestCase(absltest.TestCase):

    def test_single_cluster(self):
        clusterer = ConstrainedKMeansClusterer(
            POINTS,
            max_size=len(POINTS),
            max_radius=np.inf,
        )
        clusterer.cluster()
        self.assertEqual(len(clusterer.clusters), 1)
        cluster = clusterer.clusters[0]
        self.assertEqual(cluster.size(), len(POINTS))
        np.testing.assert_allclose(cluster.centroid(), np.array([0, 1.25, 0]))

    def test_max_size_one(self):
        clusterer = ConstrainedKMeansClusterer(
            POINTS,
            max_size=1,
            max_radius=np.inf,
        )
        clusterer.cluster()
        self.assertEqual(len(clusterer.clusters), len(POINTS))
        for cluster in clusterer.clusters:
            self.assertEqual(cluster.size(), 1)

    def test_zero_radius(self):
        clusterer = ConstrainedKMeansClusterer(
            POINTS,
            max_size=len(POINTS),
            max_radius=0,
        )
        clusterer.cluster()
        self.assertEqual(len(clusterer.clusters), len(POINTS))
        for cluster in clusterer.clusters:
            self.assertEqual(cluster.size(), 1)

    def test_small_radius(self):
        clusterer = ConstrainedKMeansClusterer(
            POINTS,
            max_size=len(POINTS),
            max_radius=1,
        )
        clusterer.cluster()
        self.assertEqual(len(clusterer.clusters), 2)


if __name__ == "__main__":
    absltest.main()
