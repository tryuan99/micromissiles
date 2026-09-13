"""Plots the radiation pattern from measured S2P files."""

from enum import StrEnum
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config
from utils import constants
from utils.network.sparam_viewer import SParamViewer

FLAGS = flags.FLAGS


class RadiationPatternSlice(StrEnum):
    """Radiation pattern slice enumeration."""
    AZIMUTH = "azimuth"
    ELEVATION = "elevation"


def _prune_hfss_simulation_result(hfss_df: pd.DataFrame,
                                  slice: RadiationPatternSlice) -> pd.DataFrame:
    """Prunes the HFSS simulation result dataframe.

    Args:
        hfss_df: HFSS simulation result dataframe.
        slice: Radiation pattern slice.

    Returns:
        A dataframe containing the frequency, the angle, and the antenna gain.
    """
    (
        frequency_column,
        azimuth_column,
        elevation_column,
        gain_db_column,
    ) = hfss_df.columns

    # In the HFSS design, the elevation is swept from the boresight from 0
    # degrees to 180 degrees, so to get the full radiation pattern for the
    # forward hemisphere, combine the elevation data from 0 to 90 degrees for
    # opposing azimuths.
    # For azimuth slices, -90 degrees refers to the left while +90 degrees
    # refers to the right relative to the boresight. For elevation slices, -90
    # degrees refers to below the boresight while +90 degrees refers to above
    # the boresight.
    pruned_df = hfss_df.copy()
    match slice:
        case RadiationPatternSlice.AZIMUTH:
            pruned_df = pruned_df[pruned_df[azimuth_column] % 180 == 0]
            pruned_df = pruned_df[pruned_df[elevation_column] <= 90]
            azimuth_0_mask = pruned_df[azimuth_column] == 0
            pruned_df.loc[azimuth_0_mask, elevation_column] *= -1
        case RadiationPatternSlice.ELEVATION:
            pruned_df = pruned_df[pruned_df[azimuth_column] % 180 != 0]
            pruned_df = pruned_df[pruned_df[elevation_column] <= 90]
            azimuth_270_mask = pruned_df[azimuth_column] == -90
            pruned_df.loc[azimuth_270_mask, elevation_column] *= -1
        case _:
            raise ValueError(f"Invalid radiation pattern slice: {slice}.")
    return pruned_df[[frequency_column, elevation_column,
                      gain_db_column]].sort_values(by=elevation_column)


def main(argv):
    assert len(argv) == 1

    if FLAGS.simulation:
        hfss_df = pd.read_csv(FLAGS.simulation)
        simulation_df = _prune_hfss_simulation_result(hfss_df, FLAGS.slice)
        (
            simulation_frequency_column,
            simulation_angle_column,
            simulation_gain_db_column,
        ) = simulation_df.columns

    positions = np.arange(FLAGS.start, FLAGS.stop + FLAGS.step, FLAGS.step)
    data = np.empty((len(FLAGS.frequencies), len(positions)))

    data_dir_path = Path(FLAGS.data_dir)
    for data_index, position in enumerate(positions):
        position_str = f"{position:.6f}".rstrip("0").rstrip(".")
        data_path = data_dir_path / f"{FLAGS.data_prefix}_{position_str}deg.s2p"

        sparam_data = SParamViewer(data_path)
        indices = np.abs(sparam_data.frequency()[:, None] -
                         FLAGS.frequencies).argmin(axis=0)
        data[:,
             data_index] = 20 * np.log10(np.abs(sparam_data.s(2, 1)))[indices]

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(FLAGS.frequencies):
        if FLAGS.simulation:
            simulation_frequency_df = simulation_df[
                simulation_df[simulation_frequency_column] * 1e9 == frequency]
        has_simulation = FLAGS.simulation and len(simulation_frequency_df) > 0

        ax.plot(
            positions,
            data[frequency_index],
            color=f"C{frequency_index}",
            label=((f"{FLAGS.labels[frequency_index]}"
                    f'{" (measured)" if has_simulation else ""}')
                   if FLAGS.labels else None),
            marker="^",
        )

        if has_simulation:
            ax.plot(
                simulation_frequency_df[simulation_angle_column],
                simulation_frequency_df[simulation_gain_db_column] -
                simulation_frequency_df[simulation_gain_db_column].max() +
                data[frequency_index].max(),
                color=
                f"C{frequency_index if len(FLAGS.frequencies) > 1 else frequency_index + len(FLAGS.frequencies)}",
                linestyle="--",
                label=(
                    f"{FLAGS.labels[frequency_index] if FLAGS.labels else None} "
                    f"(simulated)"),
            )
    ax.set_xlabel("Position [deg]")
    ax.set_ylabel("S21 Magnitude [dB]")
    if FLAGS.labels:
        ax.legend()
    plt.show()

    fig, ax = plt.subplots(
        figsize=(6, 6),
        subplot_kw={"projection": "polar"},
    )
    if FLAGS.slice != RadiationPatternSlice.ELEVATION:
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
    for frequency_index, frequency in enumerate(FLAGS.frequencies):
        if FLAGS.simulation:
            simulation_frequency_df = simulation_df[
                simulation_df[simulation_frequency_column] * 1e9 == frequency]
        has_simulation = FLAGS.simulation and len(simulation_frequency_df) > 0

        ax.plot(
            constants.deg2rad(positions),
            data[frequency_index],
            color=f"C{frequency_index}",
            label=((f"{FLAGS.labels[frequency_index]}"
                    f'{" (measured)" if has_simulation else ""}')
                   if FLAGS.labels else None),
            marker="^",
        )

        if has_simulation:
            ax.plot(
                constants.deg2rad(
                    simulation_frequency_df[simulation_angle_column]),
                simulation_frequency_df[simulation_gain_db_column] -
                simulation_frequency_df[simulation_gain_db_column].max() +
                data[frequency_index].max(),
                color=
                f"C{frequency_index if len(FLAGS.frequencies) > 1 else frequency_index + len(FLAGS.frequencies)}",
                linestyle="--",
                label=(
                    f"{FLAGS.labels[frequency_index] if FLAGS.labels else None} "
                    f"(simulated)"),
            )
    ax.set_thetamin(-180)
    ax.set_thetamax(180)
    if FLAGS.labels:
        ax.legend()
    plt.show()


if __name__ == "__main__":
    flags.DEFINE_float("start", None, "Start position in degrees.")
    flags.DEFINE_float("stop", None, "Stop position in degrees.")
    flags.DEFINE_float(
        "step",
        None,
        "Step position in degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_string("data_dir", None, "Data directory.")
    flags.DEFINE_string("data_prefix", "antenna_sweep", "Data file prefix.")
    flags.DEFINE_multi_float("frequencies", None, "Frequencies to plot in Hz.")
    flags.DEFINE_multi_string("labels", None, "Labels for the plot.")
    flags.DEFINE_string("simulation", None, "HFSS simulation result CSV file.")
    flags.DEFINE_enum("slice", None, [
        radiation_pattern_slice.value
        for radiation_pattern_slice in RadiationPatternSlice
    ], "Radiation pattern slice.")
    flags.mark_flags_as_required(
        ["start", "stop", "step", "data_dir", "frequencies", "slice"])

    app.run(main)
