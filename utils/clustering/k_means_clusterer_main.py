"""Runs the k-means clustering algorithm and plots the clusters and the
points.
"""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags, logging

from utils.clustering.cluster import Point
from utils.clustering.k_means_clusterer import KMeansClusterer

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


def run_k_means_clustering(num_points: int, num_clusters: int) -> None:
    """Runs k-means clustering.

    Args:
        num_points: Number of points.
        num_clusters: Number of clusters.
    """
    # Cluster the points.
    points = _generate_random_points(num_points)
    clusterer = KMeansClusterer(points, num_clusters)
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
                alpha=0.25,
            )
        ax.scatter(
            cluster.x,
            cluster.y,
            s=100,
            c=f"C{cluster_idx}",
            marker="*",
        )
    ax.set_aspect("equal", adjustable="box")
    plt.show()

    # Plot a histogram of the cluster radii.
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(
        cluster_radii,
        bins=np.arange(
            np.min(cluster_radii),
            np.max(cluster_radii),
            0.005,
        ),
    )
    plt.show()

    # Plot a histogram of the cluster sizes.
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(
        cluster_sizes,
        bins=np.arange(
            np.min(cluster_sizes) - 0.5,
            np.max(cluster_sizes) + 1,
        ),
    )
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    run_k_means_clustering(FLAGS.num_points, FLAGS.num_clusters)


if __name__ == "__main__":
    flags.DEFINE_integer("num_points", 1000, "Number of points.")
    flags.DEFINE_integer("num_clusters", 250, "Number of clusters.")

    app.run(main)
