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
        # Create the data matrix.
        data = np.array([point.coordinates() for point in self.points])

        # Run k-means clustering.
        codebook, distortion = scipy.cluster.vq.kmeans(
            data,
            self.k,
            thresh=K_MEANS_DISTORTION_THRESHOLD,
        )
        self.clusters = [Cluster(*centroid) for centroid in codebook]

        # Find the closest centroid for each point.
        for point in self.points:
            centroid_distances_to_point = np.linalg.norm(
                codebook - point.coordinates(),
                axis=1,
            )
            cluster_idx = np.argmin(centroid_distances_to_point)
            self.clusters[cluster_idx].add_point(point)


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
            codebook, distortion = scipy.cluster.vq.kmeans(
                point_coordinates,
                num_clusters,
                thresh=K_MEANS_DISTORTION_THRESHOLD,
            )
            # The k-means implementation may remove clusters that have no
            # points assigned to them.
            num_clusters = codebook.shape[0]

            # Find the closest centroid for each point.
            cluster_indices = np.zeros(len(self.points))
            for point_idx, point in enumerate(self.points):
                centroid_distances_to_point = np.linalg.norm(
                    codebook - point.coordinates(),
                    axis=1,
                )
                cluster_idx = np.argmin(centroid_distances_to_point)
                cluster_indices[point_idx] = cluster_idx

            # Find the cluster sizes and radii.
            cluster_radii = np.zeros(num_clusters)
            cluster_sizes = np.zeros(num_clusters)
            for cluster_idx in range(num_clusters):
                cluster_point_coordinates = (
                    point_coordinates[cluster_indices == cluster_idx])
                cluster_sizes[cluster_idx] = len(cluster_point_coordinates)
                point_distances_to_centroid = np.linalg.norm(
                    cluster_point_coordinates - codebook[cluster_idx],
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

        self.clusters = [Cluster(*coordinates) for coordinates in codebook]
        for cluster_idx, cluster in enumerate(self.clusters):
            cluster.add_points([
                self.points[point_idx]
                for point_idx in np.where(cluster_indices == cluster_idx)[0]
            ])
