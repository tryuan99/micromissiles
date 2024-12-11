"""The clusterer class is an interface for a clustering algorithm."""

from abc import ABC, abstractmethod
from typing import Self

import numpy as np


class Point:
    """2-dimensional point in Cartesian coordinates.
    
    Attributes:
        x: x-coordinate.
        y: y-coordinate.
    """

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def calculate_distance(self, point: Self) -> float:
        """Calculates the distance to another point.
        
        Args:
            point: Point to calcualate the distance to.
        
        Returns:
            The Euclidean distance to the other point.
        """
        return np.linalg.norm([point.x - self.x, point.y - self.y])


class Clusterer(ABC):
    """Interface for a clustering algorithm.
    
    Attributes:
        points: List of points to cluster.
        centroids: List of cluster centroids.
        centroid_indices: Index of the centroid closest to each point.
    """

    def __init__(self, points: list[Point]) -> None:
        self.points = points
        self.centroids: list[Point] = []
        self.centroid_indices = np.zeros(len(points), dtype=np.int64)

    @abstractmethod
    def cluster(self, epsilon: float = 1e-3) -> None:
        """Clusters the points.
        
        Args:
            epsilon: Distance threshold for convergence.
        """
