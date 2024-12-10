"""Plots the simulated radiation pattern of an antenna."""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import cm

from simulation.antenna.radiation_pattern import RadiationPattern
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_radiation_pattern_3d_scatter(csv_file: str) -> None:
    """Plots the simulated 3D radiation pattern as a scatter plot.
    
    Args:
        csv_file: Simulated radiation pattern CSV file.
    """
    radiation_pattern = RadiationPattern(csv_file)
    rE = radiation_pattern.df[radiation_pattern.rE_column]

    # Convert from spherical coordinates to Cartesian coordinates.
    r = rE - rE.min()
    x, y, z = radiation_pattern.transform_to_cartesian()

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(vmin=np.min(r), vmax=np.max(r))
    m = cm.ScalarMappable(cmap=COLOR_MAPS["parula"], norm=norm)
    m.set_array([])

    # Plot the radiation pattern.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    ax.scatter(
        x * r,
        y * r,
        z * r,
        c=r,
        cmap=COLOR_MAPS["parula"],
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.set_aspect("equal", adjustable="box")
    ax.view_init(30, -45)
    plt.colorbar(m, ax=ax)
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_radiation_pattern_3d_scatter(FLAGS.data)


if __name__ == "__main__":
    flags.DEFINE_string("data", None, "Simulated radiation pattern CSV file.")
    flags.mark_flag_as_required("data")

    app.run(main)
