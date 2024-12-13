"""The k-means clusterer performs the k-means clustering algorithm on the given
points.
"""

import numpy as np
import scipy.cluster

from utils.clustering.clusterer import (Cluster, Clusterer, Point,
                                        SizeAndRadiusConstrainedClusterer)

# Distortion threshold for convergence.
K_MEANS_DISTORTION_THRESHOLD = 1e-3


class KMeansClusterer(Clusterer):
    """K-means clustering algorithm.

    Attributes:
        k: Number of clusters.
        threshold: Distortion threshold for convergence.
    """

    def __init__(self, points: list[Point], k: int) -> None:
        super().__init__(points)
        self.k = k

    def cluster(self) -> None:
        """Clusters the points."""
        point_coordinates = np.array(
            [point.coordinates() for point in self.points])

        # Run k-means clustering.
        centroids, labels = scipy.cluster.vq.kmeans2(
            point_coordinates,
            self.k,
            iter=20,
            thresh=K_MEANS_DISTORTION_THRESHOLD,
            minit="++",
        )

        # Assign each point to the closest centroid.
        self.clusters = [Cluster(*centroid) for centroid in centroids]
        for point_idx, point in enumerate(self.points):
            self.clusters[labels[point_idx]].add_point(point)


class ConstrainedKMeansClusterer(SizeAndRadiusConstrainedClusterer):
    """K-means clustering algorithm with size and radius constraints."""

    def __init__(
        self,
        points: list[Point],
        max_size: int,
        max_radius: float,
    ) -> None:
        super().__init__(points, max_size, max_radius)

    def cluster(self) -> None:
        """Clusters the points."""
        num_clusters = int(np.ceil(len(self.points) / self.max_size))
        point_coordinates = np.array(
            [point.coordinates() for point in self.points])

        converged = False
        while not converged:
            # Run k-means clustering on the points.
            centroids, labels = scipy.cluster.vq.kmeans2(
                point_coordinates,
                num_clusters,
                iter=20,
                thresh=K_MEANS_DISTORTION_THRESHOLD,
                minit="++",
            )

            # Find the cluster sizes and radii.
            cluster_radii = np.zeros(num_clusters)
            cluster_sizes = np.zeros(num_clusters)
            for cluster_idx in range(num_clusters):
                cluster_point_coordinates = (
                    point_coordinates[labels == cluster_idx])
                cluster_sizes[cluster_idx] = len(cluster_point_coordinates)
                point_distances_to_centroid = np.linalg.norm(
                    cluster_point_coordinates - centroids[cluster_idx],
                    axis=1,
                )
                cluster_radii[cluster_idx] = np.max(point_distances_to_centroid)

            # Increase the number of clusters if the size and radius
            # constraints are not satisfied.
            num_overpopulated_clusters = np.sum(cluster_sizes > self.max_size)
            num_oversized_clusters = np.sum(cluster_radii > self.max_radius)
            if num_overpopulated_clusters == 0 and num_oversized_clusters == 0:
                converged = True
                break
            num_clusters += int(
                np.ceil(
                    max(num_overpopulated_clusters, num_oversized_clusters) /
                    2))

        # Assign each point to the closest centroid.
        self.clusters = [Cluster(*coordinates) for coordinates in centroids]
        for point_idx, point in enumerate(self.points):
            self.clusters[labels[point_idx]].add_point(point)
