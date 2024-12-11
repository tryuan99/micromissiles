"""The clusterer class is an interface for a clustering algorithm."""

from abc import ABC, abstractmethod
from typing import Self

import numpy as np


class Point:
    """Point in Cartesian coordinates.

    Attributes:
        x: x-coordinate.
        y: y-coordinate.
    """

    def __init__(self, x: float, y: float, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = 0

    def calculate_distance(self, point: Self) -> float:
        """Calculates the distance to another point.

        Args:
            point: Point to calcualate the distance to.

        Returns:
            The Euclidean distance to the other point.
        """
        return np.linalg.norm([
            point.x - self.x,
            point.y - self.y,
            point.z - self.z,
        ])


class Cluster(Point):
    """Cluster of points."""

    def __init__(self, x: float, y: float, z: float = 0) -> None:
        super().__init__(x, y, z)
        self.points: list[Point] = []

    def empty(self) -> bool:
        """Returns whether the cluster is emtpy."""
        return len(self.points) == 0

    def add_point(self, point: Point) -> None:
        """Adds a point to the cluster.

        Args:
            point: Point to be added to the cluster.
        """
        self.points.append(point)

    def add_points(self, points: list[Point]) -> None:
        """Adds points to the cluster.

        Args:
            points: List of points to be added to the cluster.
        """
        self.points.extend(points)


class Clusterer(ABC):
    """Interface for a clustering algorithm.

    Attributes:
        points: List of points to cluster.
        clusters: List of clusters.
        cluster_indices: Index of the cluster to which the point belongs.
    """

    def __init__(self, points: list[Point]) -> None:
        self.points = points
        self.clusters: list[Cluster] = []
        self.cluster_indices = np.zeros(len(points), dtype=np.int64)

    @abstractmethod
    def cluster(self, epsilon: float = 1e-3) -> None:
        """Clusters the points.

        Args:
            epsilon: Distance threshold for convergence.
        """
