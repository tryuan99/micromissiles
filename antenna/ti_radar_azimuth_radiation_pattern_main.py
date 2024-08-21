"""Plots the radiation pattern of the radar antennas over azimuth."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags

from utils import constants

FLAGS = flags.FLAGS


def plot_azimuth_radiation_pattern(data: str) -> None:
    """Plots the azimuth radiation pattern of the radar antennas.
    
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
    # azimuth.
    for antenna_column in antenna_columns:
        azimuth = df[azimuth_column]
        antenna_radiation_pattern = df[antenna_column]
        antenna_radiation_pattern_abs = np.abs(antenna_radiation_pattern)
        antenna_radiation_pattern_abs_db = (
            constants.mag2db(antenna_radiation_pattern_abs))
        normalized_antenna_radiation_pattern_abs_db = (
            antenna_radiation_pattern_abs_db -
            np.max(antenna_radiation_pattern_abs_db))

        # Plot the magnitude of the spatial samples over azimuth.
        plt.style.use(["science", "grid"])
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.scatter(azimuth, normalized_antenna_radiation_pattern_abs_db)
        ax.set_xlabel("Azimuth [deg]")
        ax.set_ylabel("Normalized magnitude [dB]")
        ax.set_title(f"{antenna_column} azimuth radiation pattern")
        plt.show()


def main(argv):
    assert len(argv) == 1

    plot_azimuth_radiation_pattern(FLAGS.data)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data",
        "antenna/data/ti_iwr6843aopevm_azimuth_radiation_pattern_data_1.csv",
        "Data filename.")

    app.run(main)
