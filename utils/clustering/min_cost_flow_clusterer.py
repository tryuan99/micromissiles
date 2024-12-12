"""The min-cost flow clustering algorithm formulates the cluster assignment
problem as a min-cost flow network optimization problem to satisfy the cluster
size constraint. If the range constraint is not satisfied, an additional
centroid is placed at the point at that is farthest from its assigned cluster's
centroid.
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

        converged = False
        while not converged:
            # Run constrained k-means clustering on the points.
            clusterer = KMeansConstrained(
                n_clusters=num_clusters,
                size_max=self.max_size,
            )
            cluster_indices = clusterer.fit_predict(point_coordinates)
            cluster_coordinates = clusterer.cluster_centers_

            # Find the maximum cluster radius.
            cluster_radii = np.zeros(num_clusters)
            for cluster_idx in range(num_clusters):
                cluster_point_coordinates = point_coordinates[cluster_indices ==
                                                              cluster_idx]
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

            # TODO(titan): Place a centroid at the point that is farthest away
            # from its assigned cluster's centroid.
            num_oversized_clusters = np.sum(cluster_radii > self.max_radius)
            num_clusters += num_oversized_clusters // 2

        self.clusters = [
            Cluster(*coordinates) for coordinates in cluster_coordinates
        ]
        for cluster_idx, cluster in enumerate(self.clusters):
            cluster.add_points([
                self.points[point_idx]
                for point_idx in np.where(cluster_indices == cluster_idx)[0]
            ])
