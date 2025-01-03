"""The agglomerative clusterer greedily aggregates clusters that are closest to
each other assuming that the resulting cluster satisfies the size constraint
and radius constraints.
"""

import numpy as np
import scipy.spatial

from utils.clustering.cluster import Cluster, Point
from utils.clustering.clusterer import SizeAndRadiusConstrainedClusterer


class AgglomerativeClusterer(SizeAndRadiusConstrainedClusterer):
    """Agglomerative clustering algorithm."""

    def __init__(
        self,
        points: list[Point],
        max_size: int,
        max_radius: float,
    ) -> None:
        super().__init__(points, max_size, max_radius)

    def cluster(self) -> None:
        """Clusters the points."""
        self.clusters = [Cluster(point=point) for point in self.points]
        valid_cluster_indices = list(range(len(self.clusters)))

        # Find the pairwise distances between all clusters.
        cluster_coordinates = np.array(
            [cluster.coordinates() for cluster in self.clusters])
        distances_vector = scipy.spatial.distance.pdist(cluster_coordinates)
        distances = scipy.spatial.distance.squareform(distances_vector)
        # Zero out the upper triangular half of the distances matrix.
        distances *= np.tri(*distances.shape)
        # Set all zero distances to infinite distances.
        distances[distances == 0] = np.inf

        while True:
            cluster_idx_1, cluster_idx_2 = np.unravel_index(
                np.argmin(distances), distances.shape)

            # Check whether the minimum distance exceeds the maximum cluster
            # radius, in which case the algorithm has converged.
            # This produces a conservative solution because the radius of a
            # merged cluster is less than or equal to the sum of the original
            # cluster radii.
            if distances[cluster_idx_1, cluster_idx_2] >= self.max_radius:
                break

            # Check whether merging the two clusters would violate the size
            # constraint.
            if (self.clusters[cluster_idx_1].size() +
                    self.clusters[cluster_idx_2].size()) > self.max_size:
                distances[cluster_idx_1, cluster_idx_2] = np.inf
                continue

            # Merge the two clusters together.
            min_cluster_idx = min(cluster_idx_1, cluster_idx_2)
            max_cluster_idx = max(cluster_idx_1, cluster_idx_2)
            self.clusters[min_cluster_idx].merge_cluster(
                self.clusters[max_cluster_idx])
            self.clusters[min_cluster_idx].recenter()
            valid_cluster_indices.remove(max_cluster_idx)

            # Update the distances matrix using the distance between the
            # cluster centroids.
            # TODO(titan): Change the distance metric to use average or maximum
            # linkage.
            valid_cluster_coordinates = np.array([
                self.clusters[cluster_idx].coordinates()
                for cluster_idx in valid_cluster_indices
            ])
            distances_to_valid_clusters = np.linalg.norm(
                valid_cluster_coordinates -
                self.clusters[min_cluster_idx].coordinates(),
                axis=1,
            )

            infinite_mask = np.isinf(distances)
            distances[min_cluster_idx,
                      valid_cluster_indices] = distances_to_valid_clusters
            distances[valid_cluster_indices,
                      min_cluster_idx] = distances_to_valid_clusters
            distances[infinite_mask] = np.inf
            distances[max_cluster_idx, :] = np.inf
            distances[:, max_cluster_idx] = np.inf

        # Select only the valid clusters.
        self.clusters = [
            self.clusters[cluster_idx] for cluster_idx in valid_cluster_indices
        ]
