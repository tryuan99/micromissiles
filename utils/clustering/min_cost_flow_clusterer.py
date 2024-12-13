"""The min-cost flow clustering algorithm formulates the cluster assignment
problem as a min-cost flow network optimization problem to satisfy the cluster
size constraint. If the range constraint is not satisfied, the number of
clusters is increased for the next iteration, where the centroids of the new
clusters are placed at the points that are farthest away from their assigned
clusters' centroids.
"""

import numpy as np
from k_means_constrained import KMeansConstrained

from utils.clustering.clusterer import (Cluster, Point,
                                        SizeAndRadiusConstrainedClusterer)


class MinClostFlowClusterer(SizeAndRadiusConstrainedClusterer):
    """Min-cost flow clustering algorithm."""

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

        iteration = 0
        converged = False
        while not converged:
            iteration += 1

            # Run constrained k-means clustering on the points.
            clusterer = KMeansConstrained(
                n_clusters=num_clusters,
                size_max=self.max_size,
                init="k-means++" if iteration == 1 else cluster_coordinates,
                n_init=20 if iteration == 1 else 1,
            )
            cluster_indices = clusterer.fit_predict(point_coordinates)
            cluster_coordinates = clusterer.cluster_centers_

            # Find the maximum cluster radius.
            cluster_radii = np.zeros(num_clusters)
            for cluster_idx in range(num_clusters):
                cluster_point_coordinates = (
                    point_coordinates[cluster_indices == cluster_idx])
                point_distances_to_centroid = np.linalg.norm(
                    cluster_point_coordinates -
                    cluster_coordinates[cluster_idx],
                    axis=1,
                )
                cluster_radii[cluster_idx] = np.max(point_distances_to_centroid)
            max_cluster_radius = np.max(cluster_radii)

            # Check whether the radius constraint is satisfied, in which case
            # the algorithm has converged.
            if max_cluster_radius <= self.max_radius:
                converged = True
                break

            # Increase the number of clusters if the size and radius
            # constraints are not satisfied. The new centroids are placed at
            # the points that are farthest away from their assigned clusters'
            # centroids.
            num_oversized_clusters = np.sum(cluster_radii > self.max_radius)
            # Adding a smaller number of new clusters at every iteration
            # provides a better solution at the expense of more iterations and
            # a longer runtime.
            num_new_clusters = int(np.ceil(num_oversized_clusters / 2))
            new_cluster_coordinates = np.zeros(
                (num_new_clusters, cluster_coordinates.shape[1]))
            largest_cluster_indices = np.flip(np.argsort(cluster_radii))
            for new_cluster_idx, cluster_idx in enumerate(
                    largest_cluster_indices[:num_new_clusters]):
                # Find the point that is farthest away from the centroid within
                # the cluster.
                cluster_point_coordinates = (
                    point_coordinates[cluster_indices == cluster_idx])
                point_distances_to_centroid = np.linalg.norm(
                    cluster_point_coordinates -
                    cluster_coordinates[cluster_idx],
                    axis=1,
                )
                farthest_point_idx = np.argmax(point_distances_to_centroid)
                farthest_point = cluster_point_coordinates[farthest_point_idx]

                # Place a new centroid at the farthest point from its currently
                # assigned cluster's centroid.
                new_cluster_coordinates[new_cluster_idx] = farthest_point

            # Update the number of clusters and their centroids.
            num_clusters += num_new_clusters
            cluster_coordinates = np.vstack(
                (cluster_coordinates, new_cluster_coordinates))

        self.clusters = [
            Cluster(*coordinates) for coordinates in cluster_coordinates
        ]
        for cluster_idx, cluster in enumerate(self.clusters):
            cluster.add_points([
                self.points[point_idx]
                for point_idx in np.where(cluster_indices == cluster_idx)[0]
            ])
