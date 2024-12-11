"""Runs the agglomerative clustering algorithm and plots the clusters and the
points.
"""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags, logging

from utils.clustering.agglomerative_clusterer import AgglomerativeClusterer
from utils.clustering.clusterer import Point

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


def run_agglomerative_clustering(num_points: int, max_size: int,
                                 threshold: float) -> None:
    """Runs agglomerative clustering.

    Args:
        num_points: Number of points.
        max_size: Maximum cluster size.
        threshold: Distance threshold for convergence.
    """
    # Cluster the points.
    points = _generate_random_points(num_points)
    clusterer = AgglomerativeClusterer(points, max_size, threshold)
    clusterer.cluster()

    logging.info("Number of clusters: %d", len(clusterer.clusters))

    # Log the mean and maximum radii of the clusters.
    cluster_radii = [cluster.radius() for cluster in clusterer.clusters]
    logging.info(
        "Cluster mean radius: %f, max radius: %f",
        np.mean(cluster_radii),
        np.max(cluster_radii),
    )

    # Log the mean and maximum sizes of the clusters.
    cluster_sizes = [cluster.size() for cluster in clusterer.clusters]
    logging.info(
        "Cluster mean size: %f, max size: %f",
        np.mean(cluster_sizes),
        np.max(cluster_sizes),
    )

    # Plot the clusters and the points.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    for cluster_idx, cluster in enumerate(clusterer.clusters):
        for point in cluster.points:
            ax.scatter(
                point.x,
                point.y,
                c=f"C{cluster_idx}",
            )
        ax.scatter(
            cluster.x,
            cluster.y,
            s=300,
            c=f"C{cluster_idx}",
            marker="*",
        )
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    run_agglomerative_clustering(FLAGS.num_points, FLAGS.max_size,
                                 FLAGS.threshold)


if __name__ == "__main__":
    flags.DEFINE_integer("num_points", 500, "Number of points.")
    flags.DEFINE_integer("max_size", 7, "Maximum cluster size.")
    flags.DEFINE_float("threshold", 1, "Distance threshold for convergence.")

    app.run(main)
