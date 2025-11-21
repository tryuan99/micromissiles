"""Runs the size and radius-constrained clustering algorithm on 2D points and
plots the clusters and the points.
"""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

import utils.visualization.mpl_config
from utils.clustering.agglomerative_clusterer import AgglomerativeClusterer
from utils.clustering.cluster import Point
from utils.clustering.k_means_clusterer import ConstrainedKMeansClusterer
from utils.clustering.min_cost_flow_clusterer import MinClostFlowClusterer

FLAGS = flags.FLAGS

# Dictionary of size and radius-constrained clustering algorithms.
CLUSTERERS = {
    "k_means": ConstrainedKMeansClusterer,
    "agglomerative": AgglomerativeClusterer,
    "min_cost_flow": MinClostFlowClusterer,
}


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


def run_size_and_radius_constrained_clustering(
    clusterer_type: str,
    num_points: int,
    max_size: int,
    max_radius: float,
) -> None:
    """Runs the size and radius-constrained clustering algorithm.

    Args:
        clusterer_type: Clustering algorithm.
        num_points: Number of points.
        max_size: Maximum cluster size.
        max_radius: Maximum cluster radius.
    """
    # Cluster the points.
    points = _generate_random_points(num_points)

    # Plot the clusters and the points.
    fig, ax = plt.subplots(figsize=(6, 3))
    point_coordinates = np.array([point.coordinates() for point in points])
    ax.scatter(
        point_coordinates[:, 0],
        point_coordinates[:, 1],
        s=20,
        alpha=0.2,
        linewidths=0,
    )
    ax.set_aspect("equal", adjustable="box")
    plt.show()

    fig, ax = plt.subplots(figsize=(5, 4))
    for clusterer_index, clusterer_type in enumerate(CLUSTERERS):
        clusterer = CLUSTERERS[clusterer_type](points, max_size, max_radius)
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

        # Plot a histogram of the cluster sizes.
        ax.hist(
            cluster_sizes,
            bins=np.arange(
                np.min(cluster_sizes) - 0.5,
                np.max(cluster_sizes) + 1,
            ),
            color=f"C{clusterer_index}",
            alpha=0.4,
        )
    ax.legend([
        r"Constrained $k$-means",
        "Agglomerative",
        "Min-cost flow",
    ])
    ax.axvline(
        max_size,
        color="red",
        linestyle="--",
        linewidth=2,
    )
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    np.random.seed(5)
    run_size_and_radius_constrained_clustering(
        FLAGS.clusterer,
        FLAGS.num_points,
        FLAGS.max_size,
        FLAGS.max_radius,
    )


if __name__ == "__main__":
    flags.DEFINE_enum("clusterer", None, CLUSTERERS.keys(),
                      "Clustering algorithm.")
    flags.DEFINE_integer("num_points", 1000, "Number of points.")
    flags.DEFINE_integer("max_size", 7, "Maximum cluster size.")
    flags.DEFINE_float("max_radius", 0.5, "Maximum cluster radius.")
    flags.mark_flag_as_required("clusterer")

    app.run(main)
