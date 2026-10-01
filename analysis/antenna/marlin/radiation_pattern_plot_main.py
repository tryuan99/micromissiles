"""Plots the radiation pattern from measured S2P files."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config
from analysis.antenna.marlin.common import (RadiationPatternSlice,
                                            prune_hfss_simulation_result)
from utils import constants
from utils.network.sparam_viewer import SParamViewer

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1

    if FLAGS.simulation:
        hfss_df = pd.read_csv(FLAGS.simulation)
        simulation_df = prune_hfss_simulation_result(hfss_df, FLAGS.slice)
        (
            simulation_frequency_column,
            simulation_angle_column,
            simulation_gain_db_column,
        ) = simulation_df.columns

    positions = np.arange(FLAGS.start, FLAGS.stop + FLAGS.step, FLAGS.step)
    gain = np.empty((len(FLAGS.frequencies), len(positions)))

    data_dir_path = Path(FLAGS.data_dir)
    for data_index, position in enumerate(positions):
        position_str = f"{position:.6f}".rstrip("0").rstrip(".")
        data_path = data_dir_path / f"{FLAGS.data_prefix}_{position_str}deg.s2p"

        sparam_data = SParamViewer(data_path)
        indices = np.abs(sparam_data.frequency()[:, None] -
                         FLAGS.frequencies).argmin(axis=0)
        gain[:,
             data_index] = (constants.mag2db(np.abs(sparam_data.s(2,
                                                                  1)))[indices])

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(FLAGS.frequencies):
        if FLAGS.simulation:
            simulation_frequency_df = simulation_df[np.isclose(
                simulation_df[simulation_frequency_column] * 1e9,
                frequency,
            )]
        has_simulation = FLAGS.simulation and len(simulation_frequency_df) > 0

        ax.plot(
            positions,
            gain[frequency_index],
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
                gain[frequency_index].max(),
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
            simulation_frequency_df = simulation_df[np.isclose(
                simulation_df[simulation_frequency_column] * 1e9,
                frequency,
            )]
        has_simulation = FLAGS.simulation and len(simulation_frequency_df) > 0

        ax.plot(
            constants.deg2rad(positions),
            gain[frequency_index],
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
                gain[frequency_index].max(),
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
    flags.DEFINE_string("simulation", None,
                        "HFSS gain simulation result CSV file.")
    flags.DEFINE_enum("slice", None, [
        radiation_pattern_slice.value
        for radiation_pattern_slice in RadiationPatternSlice
    ], "Radiation pattern slice.")
    flags.mark_flags_as_required(
        ["start", "stop", "step", "data_dir", "frequencies", "slice"])

    app.run(main)
