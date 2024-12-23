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
    plt.style.use(["science", "grid"])
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
        marker="^",
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.view_init(30, -45, vertical_axis="y")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configuration and create the antenna array.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())
    array = AntennaArray.create(antenna_array_config)

    plot_antenna_array_elements(array)


if __name__ == "__main__":
    flags.DEFINE_string("config",
                        "simulation/antenna/configs/ula_4_isotropic.pbtxt",
                        "Antenna array configuration.")

    app.run(main)
