"""Runs the k-means clustering algorithm and plots the clusters and the
points.
"""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from utils.clustering.k_means_clusterer import KMeansClusterer, Point

FLAGS = flags.FLAGS


def _generate_random_point() -> np.ndarray:
    """Generates a random point.
    
    Returns:
        The x and y coordinates of the point.
    """
    direction = np.random.uniform(-np.pi / 2, np.pi / 2)
    distance = np.random.uniform(8, 12)
    return distance * np.array([np.sin(direction), np.cos(direction)])


def _generate_random_points(num_points: int) -> list[Point]:
    """Generates random points.
    
    Returns:
        A list of generated points.
    """
    points = [Point(*_generate_random_point()) for _ in range(num_points)]
    return points


def run_k_means(num_points: int, num_clusters: int) -> None:
    """Plots the antenna array elements.

    Args:
        array: Antenna array.
    """
    # Cluster the points.
    points = _generate_random_points(num_points)
    clusterer = KMeansClusterer(points, FLAGS.num_clusters)
    clusterer.cluster()

    # Plot the clusters and the points.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    for point_idx, point in enumerate(points):
        ax.scatter(
            point.x,
            point.y,
            c=f"C{clusterer.centroid_indices[point_idx]}",
        )
    for centroid_idx, centroid in enumerate(clusterer.centroids):
        ax.scatter(
            centroid.x,
            centroid.y,
            s=300,
            c=f"C{centroid_idx}",
            marker="*",
        )
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    run_k_means(FLAGS.num_points, FLAGS.num_clusters)


if __name__ == "__main__":
    flags.DEFINE_integer("num_points", 20, "Number of points.")
    flags.DEFINE_integer("num_clusters", 4, "Number of clusters.")

    app.run(main)
