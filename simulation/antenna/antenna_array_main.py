"""Plots the antenna array elements."""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.antenna.antenna_array import AntennaArray
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig

FLAGS = flags.FLAGS


def plot_antenna_array_elements(array: AntennaArray) -> None:
    """Plots the antenna array elements.

    Args:
        array: Antenna array.
    """
    # Plot the antenna array elements.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    element_coordinates = np.array(
        [element.coordinates() for element in array.elements])
    ax.scatter(
        element_coordinates[:, 0],
        element_coordinates[:, 1],
        element_coordinates[:, 2],
        s=120,
        c="C0",
        marker="^",
        alpha=0.4,
    )
    element_boresights = np.array(
        [element.boresight() for element in array.elements])
    ax.quiver(
        element_coordinates[:, 0],
        element_coordinates[:, 1],
        element_coordinates[:, 2],
        element_boresights[:, 0],
        element_boresights[:, 1],
        element_boresights[:, 2],
        length=0.1,
        normalize=True,
        color="C0",
    )
    element_rights = np.array([element.right() for element in array.elements])
    ax.quiver(
        element_coordinates[:, 0],
        element_coordinates[:, 1],
        element_coordinates[:, 2],
        element_rights[:, 0],
        element_rights[:, 1],
        element_rights[:, 2],
        length=0.1,
        normalize=True,
        color="C1",
    )
    element_verticals = np.array(
        [element.vertical() for element in array.elements])
    ax.quiver(
        element_coordinates[:, 0],
        element_coordinates[:, 1],
        element_coordinates[:, 2],
        element_verticals[:, 0],
        element_verticals[:, 1],
        element_verticals[:, 2],
        length=0.1,
        normalize=True,
        color="C2",
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    zmin, zmax = ax.get_zlim()
    ax.set_xlim(min(xmin, -0.1), xmax)
    ax.set_ylim(ymin, max(ymax, 0.1))
    ax.set_zlim(zmin, max(zmax, 0.1))
    ax.view_init(30, -45, vertical_axis="y")
    plt.show()


def plot_projected_antenna_array_elements(array: AntennaArray) -> None:
    """Plots the antenna array elements projected onto the x-z plane.

    Args:
        array: Antenna array.
    """
    # Plot the antenna array elements projected onto the x-z plane.
    plt.style.use("science")
    fig, ax = plt.subplots(figsize=(12, 6))
    element_coordinates = np.array(
        [element.coordinates() for element in array.elements])
    ax.scatter(
        element_coordinates[:, 0],
        element_coordinates[:, 2],
        s=120,
        c="C0",
        marker="^",
        alpha=0.4,
    )
    element_boresights = np.array(
        [element.boresight() for element in array.elements])
    ax.quiver(
        element_coordinates[:, 0],
        element_coordinates[:, 2],
        element_boresights[:, 0],
        element_boresights[:, 2],
        angles="xy",
        color="C0",
        width=0.002,
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$z$")
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    ax.set_xlim(min(xmin, -0.1), xmax)
    ax.set_ylim(ymin, max(ymax, 0.1))
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configuration and create the antenna array.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())
    array = AntennaArray.create(antenna_array_config)

    plot_antenna_array_elements(array)
    plot_projected_antenna_array_elements(array)


if __name__ == "__main__":
    flags.DEFINE_string(
        "config",
        "simulation/antenna/configs/ula_4_patch_antenna_24ghz.pbtxt",
        "Antenna array configuration.",
    )

    app.run(main)
