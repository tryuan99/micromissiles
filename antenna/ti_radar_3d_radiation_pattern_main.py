"""Plots the radiation pattern of the radar antennas over azimuth and
elevation.
"""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags
from matplotlib import cm

from utils import constants
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_3d_radiation_pattern(data: str) -> None:
    """Plots the 3D radiation pattern of the radar antennas.
    
    Args:
        data: Data filename.
    """
    # Open the radiation pattern data file.
    df = pd.read_csv(data, comment="#")
    # Pandas cannot read complex numbers from a CSV file, so identify all
    # columns with an object data type and convert their values into complex
    # numbers.
    converters = {}
    for column, dtype in df.dtypes.items():
        if dtype == object:
            converters[column] = np.complex128
    df = pd.read_csv(data, comment="#", converters=converters)
    azimuth_column, elevation_column, *antenna_columns = df.columns

    # For each antenna, plot the magnitude of the spatial samples over
    # azimuth and elevation.
    for antenna_column in antenna_columns:
        azimuth = df[azimuth_column]
        elevation = df[elevation_column]
        antenna_radiation_pattern = df[antenna_column]
        antenna_radiation_pattern_abs = np.abs(antenna_radiation_pattern)
        antenna_radiation_pattern_abs_db = (
            constants.mag2db(antenna_radiation_pattern_abs))
        zeroed_antenna_radiation_pattern_abs_db = (
            antenna_radiation_pattern_abs_db -
            np.min(antenna_radiation_pattern_abs_db))

        # Convert from spherical coordinates to Cartesian coordinates.
        azimuth_rad = constants.deg2rad(azimuth)
        elevation_rad = constants.deg2rad(elevation)
        r = zeroed_antenna_radiation_pattern_abs_db
        x = r * np.sin(azimuth_rad) * np.cos(elevation_rad)
        y = r * np.cos(azimuth_rad) * np.cos(elevation_rad)
        z = r * np.sin(elevation_rad)

        # Generate the face colors.
        norm = matplotlib.colors.Normalize(vmin=np.min(r), vmax=np.max(r))
        m = cm.ScalarMappable(cmap=COLOR_MAPS["parula"], norm=norm)
        m.set_array([])

        # Plot the radiation pattern.
        plt.style.use("science")
        fig, ax = plt.subplots(
            figsize=(12, 8),
            subplot_kw={"projection": "3d"},
        )
        ax.scatter(
            x,
            y,
            z,
            facecolors=COLOR_MAPS["parula"](norm(r)),
            antialiased=False,
        )
        ax.set_xlabel(r"$x$")
        ax.set_ylabel(r"$y$")
        ax.set_zlabel(r"$z$")
        ax.set_title(f"{antenna_column} radiation pattern")
        ax.set_aspect("equal", adjustable="box")
        ax.view_init(30, -45)
        plt.colorbar(m, ax=ax)
        plt.show()


def main(argv):
    assert len(argv) == 1

    plot_3d_radiation_pattern(FLAGS.data)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data", "antenna/data/ti_iwr6843aopevm_3d_radiation_pattern_data_1.csv",
        "Data filename.")

    app.run(main)
