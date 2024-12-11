"""The k-means clusterer performs the k-means clustering algorithm on the given
points.
"""

import numpy as np
import scipy.cluster

from utils.clustering.clusterer import Cluster, Clusterer, Point


class KMeansClusterer(Clusterer):
    """K-means clustering algorithm.

    Attributes:
        k: Number of clusters.
        threshold: Distortion threshold for convergence.
    """

    def __init__(self,
                 points: list[Point],
                 k: int,
                 threshold: float = 1e-3) -> None:
        super().__init__(points)
        self.k = k
        self.threshold = threshold

    def cluster(self) -> None:
        """Clusters the points."""
        # Create the data matrix.
        data = np.array([point.coordinates() for point in self.points])

        # Run k-means clustering.
        codebook, distortion = scipy.cluster.vq.kmeans(
            data,
            self.k,
            thresh=self.threshold,
        )
        self.clusters = [Cluster(*centroid) for centroid in codebook]

        # For each point, find the closest centroid.
        for point_idx, point in enumerate(self.points):
            distance_to_centroids = np.linalg.norm(
                codebook - point.coordinates(),
                axis=1,
            )
            cluster_idx = np.argmin(distance_to_centroids)
            self.clusters[cluster_idx].add_point(point)
