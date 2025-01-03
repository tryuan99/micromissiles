"""The clusterer class is an interface for a clustering algorithm."""

from abc import ABC, abstractmethod

from utils.clustering.cluster import Cluster, Point


class Clusterer(ABC):
    """Interface for a clustering algorithm.

    Attributes:
        points: List of points to cluster.
        clusters: List of clusters.
    """

    def __init__(self, points: list[Point]) -> None:
        self.points = points
        self.clusters: list[Cluster] = []

    @abstractmethod
    def cluster(self) -> None:
        """Clusters the points."""


class SizeAndRadiusConstrainedClusterer(Clusterer):
    """Interface for a clustering algorithm with size and radius constraints.

    Attributes:
        max_size: Maximum cluster size.
        max_radius: Maximum cluster radius.
    """

    def __init__(
        self,
        points: list[Point],
        max_size: int,
        max_radius: float,
    ) -> None:
        super().__init__(points)
        self.max_size = max_size
        self.max_radius = max_radius
