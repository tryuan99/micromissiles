"""Plots the antenna array elements."""

import matplotlib.pyplot as plt
import scienceplots
from absl import app, flags

from simulation.antenna.antenna_array import AntennaArray, AntennaArrayElement

FLAGS = flags.FLAGS


def plot_antenna_array_elements(array: AntennaArray) -> None:
    """Plots the antenna array elements.

    Args:
        array: Antenna array.
    """
    # Plot the antenna array elements.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "3d"},
    )
    for element in array.elements:
        ax.scatter(*element.coordinates, s=120, marker="^")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.view_init(30, -135, vertical_axis="y")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Create the antenna array.
    elements = [
        AntennaArrayElement(x=FLAGS.antenna_spacing * i)
        for i in range(FLAGS.num_antennas)
    ]
    array = AntennaArray(elements)
    plot_antenna_array_elements(array)


if __name__ == "__main__":
    flags.DEFINE_integer("num_antennas", 4, "Number of antennas.")
    flags.DEFINE_float("antenna_spacing", 0.5,
                       "Antenna spacing in units of lambda.")

    app.run(main)
