"""The k-means clusterer performs the k-means clustering algorithm on the given
points.
"""

import numpy as np

from utils.clustering.clusterer import Cluster, Clusterer, Point


class KMeansClusterer(Clusterer):
    """K-means clustering algorithm.

    Attributes:
        k: Number of clusters.
    """

    def __init__(self, points: list[Point], k: int) -> None:
        super().__init__(points)
        self.k = k

    def cluster(self, epsilon: float = 1e-3) -> None:
        """Clusters the points.

        Args:
            epsilon: Distance threshold for convergence.
        """
        # Initialize the centroids randomly.
        points_coordinates = np.array([[
            point.x,
            point.y,
            point.z,
        ] for point in self.points])
        self.clusters = [
            Cluster(
                np.random.uniform(
                    np.min(points_coordinates[:, 0]),
                    np.max(points_coordinates[:, 0]),
                ),
                np.random.uniform(
                    np.min(points_coordinates[:, 1]),
                    np.max(points_coordinates[:, 1]),
                ),
                np.random.uniform(
                    np.min(points_coordinates[:, 2]),
                    np.max(points_coordinates[:, 2]),
                ),
            ) for _ in range(self.k)
        ]

        converged = False
        while not converged:
            # Determine the closest centroid to each point.
            for point_idx, point in enumerate(self.points):
                distances = [
                    cluster.calculate_distance(point)
                    for cluster in self.clusters
                ]
                cluster_idx = np.argmin(distances)
                self.cluster_indices[point_idx] = cluster_idx
                self.clusters[cluster_idx].add_point(point)

            # Calculate the new clusters as the mean of all assigned points.
            converged = True
            for cluster_idx, cluster in enumerate(self.clusters):
                if cluster.empty():
                    new_cluster = Cluster(
                        np.random.uniform(
                            np.min(points_coordinates[:, 0]),
                            np.max(points_coordinates[:, 0]),
                        ),
                        np.random.uniform(
                            np.min(points_coordinates[:, 1]),
                            np.max(points_coordinates[:, 1]),
                        ),
                        np.random.uniform(
                            np.min(points_coordinates[:, 2]),
                            np.max(points_coordinates[:, 2]),
                        ),
                    )
                else:
                    new_cluster = Cluster(*np.mean(
                        [[
                            point.x,
                            point.y,
                            point.z,
                        ] for point in cluster.points],
                        axis=0,
                    ))
                    new_cluster.add_points(cluster.points)

                # Check whether the algorithm has converged by checking whether
                # the cluster has moved.
                if new_cluster.calculate_distance(cluster) > epsilon:
                    converged = False

                self.clusters[cluster_idx] = new_cluster
