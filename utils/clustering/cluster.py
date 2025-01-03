"""The cluster class represents a collection of points."""

from typing import Self

import numpy as np


class Point:
    """Point in Cartesian coordinates.

    Attributes:
        x: x-coordinate.
        y: y-coordinate.
        z: z-coordinate.
    """

    def __init__(self, x: float, y: float, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def coordinates(self) -> np.ndarray:
        """Returns the coordinates of the point."""
        return np.array([
            self.x,
            self.y,
            self.z,
        ])

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
    """Cluster of points.

    Attributes:
        points: List of points belonging to this cluster.
    """

    def __init__(self,
                 x: float = None,
                 y: float = None,
                 z: float = 0,
                 point: Point = None) -> None:
        if point is not None:
            x, y, z = point.coordinates()
            self.points = [point]
        else:
            self.points: list[Point] = []
        super().__init__(x, y, z)

    def size(self) -> int:
        """Returns the size of the cluster."""
        return len(self.points)

    def empty(self) -> bool:
        """Returns whether the cluster is emtpy."""
        return self.size() == 0

    def radius(self) -> float:
        """Returns the radius of the cluster.

        The radius is defined as the maximum distance from the centroid to a
        point belonging to the cluster.
        """
        point_coordinates = np.array(
            [point.coordinates() for point in self.points])
        distances_to_points = np.linalg.norm(
            point_coordinates - self.coordinates(),
            axis=1,
        )
        return np.max(distances_to_points)

    def centroid(self) -> np.ndarray:
        """Returns the coordinates of the centroid."""
        if self.empty():
            return self.coordinates()
        return np.mean(
            [point.coordinates() for point in self.points],
            axis=0,
        )

    def recenter(self) -> None:
        """Recenters the centroid to be the mean of all points."""
        self.x, self.y, self.z = self.centroid()

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

    def merge_cluster(self, cluster: Self) -> None:
        """Merges another cluster into this cluster.

        Args:
            cluster: Cluster to merge with.
        """
        self.add_points(cluster.points)
