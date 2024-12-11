"""The k-means clusterer performs the k-means clustering algorithm on the given
points.
"""

import numpy as np

from utils.clustering.clusterer import Clusterer, Point


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
        points_coordinates = np.array(
            [[point.x, point.y] for point in self.points])
        self.centroids = [
            Point(
                np.random.uniform(
                    np.min(points_coordinates[:, 0]),
                    np.max(points_coordinates[:, 0]),
                ),
                np.random.uniform(
                    np.min(points_coordinates[:, 1]),
                    np.max(points_coordinates[:, 1]),
                ),
            ) for _ in range(self.k)
        ]

        converged = False
        while not converged:
            # Determine the closest centroid to each point.
            for point_idx, point in enumerate(self.points):
                distances = [
                    centroid.calculate_distance(point)
                    for centroid in self.centroids
                ]
                self.centroid_indices[point_idx] = np.argmin(distances)

            # Calculate the new centroids as the mean of all assigned points.
            converged = True
            for centroid_idx in range(self.k):
                if centroid_idx in self.centroid_indices:
                    new_centroid = Point(*np.mean(
                        [[
                            self.points[point_idx].x,
                            self.points[point_idx].y,
                        ]
                         for point_idx in range(len(self.points))
                         if (self.centroid_indices[point_idx] == centroid_idx)],
                        axis=0,
                    ))
                else:
                    new_centroid = Point(
                        np.random.uniform(
                            np.min(points_coordinates[:, 0]),
                            np.max(points_coordinates[:, 0]),
                        ),
                        np.random.uniform(
                            np.min(points_coordinates[:, 1]),
                            np.max(points_coordinates[:, 1]),
                        ),
                    )

                # Check whether the algorithm has converged by checking whether
                # the centroid has moved.
                if new_centroid.calculate_distance(
                        self.centroids[centroid_idx]) > epsilon:
                    converged = False

                self.centroids[centroid_idx] = new_centroid
