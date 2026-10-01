"""Plots the beamformed radiation pattern from measured S2P files."""

from pathlib import Path

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config
from analysis.antenna.marlin.common import (RadiationPatternSlice,
                                            prune_hfss_simulation_result)
from analysis.antenna.marlin.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils import constants
from utils.network.sparam_viewer import SParamViewer

FLAGS = flags.FLAGS

# Simulation rE columns.
SIMULATION_RE_PHI_COLUMN = "rE_phi"
SIMULATION_RE_THETA_COLUMN = "rE_theta"


def main(argv):
    assert len(argv) == 1

    # Parse the antenna array configuration.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())

    x = np.array([
        element.position.x
        for element in antenna_array_config.antenna_array_element_configs
    ])
    y = np.array([
        element.position.y
        for element in antenna_array_config.antenna_array_element_configs
    ])
    feed_signs = 1 - 2 * np.array(
        [
            element.inverted
            for element in antenna_array_config.antenna_array_element_configs
        ],
        dtype=int,
    )

    # Calculate the beamforming weights as a function of the azimuth and the elevation.
    azimuth = constants.deg2rad(FLAGS.azimuth)
    elevation = constants.deg2rad(FLAGS.elevation)
    # Positive azimuth points toward -x.
    u = -np.cos(elevation) * np.sin(azimuth)
    v = np.sin(elevation)
    phases = -2 * np.pi * (x * u + y * v)
    weights = np.exp(1j * phases)

    if FLAGS.simulations and len(FLAGS.data_dirs) != len(FLAGS.simulations):
        raise ValueError(
            "Number of data directories does not match the number of simulation files."
        )
    if len(FLAGS.data_dirs) != len(
            antenna_array_config.antenna_array_element_configs):
        raise ValueError(
            "Number of data directories does not match the number of antenna array elements."
        )

    simulation_dfs: list[pd.DataFrame] = []
    for simulation_index, simulation in enumerate(FLAGS.simulations):
        hfss_df = pd.read_csv(simulation)
        simulation_df = prune_hfss_simulation_result(hfss_df, FLAGS.slice)
        (
            simulation_frequency_column,
            simulation_angle_column,
            simulation_rE_phi_real_column,
            simulation_rE_phi_imag_column,
            simulation_rE_theta_real_column,
            simulation_rE_theta_imag_column,
        ) = simulation_df.columns
        simulation_df[SIMULATION_RE_PHI_COLUMN] = simulation_df[
            simulation_rE_phi_real_column] + 1j * simulation_df[
                simulation_rE_phi_imag_column]
        simulation_df[SIMULATION_RE_THETA_COLUMN] = simulation_df[
            simulation_rE_theta_real_column] + 1j * simulation_df[
                simulation_rE_theta_imag_column]
        simulation_df[SIMULATION_RE_PHI_COLUMN] *= weights[simulation_index]
        simulation_df[SIMULATION_RE_THETA_COLUMN] *= weights[simulation_index]
        simulation_dfs.append(simulation_df[[
            simulation_frequency_column,
            simulation_angle_column,
            SIMULATION_RE_PHI_COLUMN,
            SIMULATION_RE_THETA_COLUMN,
        ]])
    if simulation_dfs:
        simulation_df = pd.concat(simulation_dfs).groupby(
            [
                simulation_frequency_column,
                simulation_angle_column,
            ],
            as_index=False,
        ).sum()

    positions = np.arange(FLAGS.start, FLAGS.stop + FLAGS.step, FLAGS.step)
    s21 = np.zeros((len(FLAGS.frequencies), len(positions)),
                   dtype=np.complex128)

    for data_dir_index, data_dir in enumerate(FLAGS.data_dirs):
        data_dir_path = Path(data_dir)
        for data_index, position in enumerate(positions):
            position_str = f"{position:.6f}".rstrip("0").rstrip(".")
            data_path = data_dir_path / f"{FLAGS.data_prefix}_{position_str}deg.s2p"

            sparam_data = SParamViewer(data_path)
            indices = np.abs(sparam_data.frequency()[:, None] -
                             FLAGS.frequencies).argmin(axis=0)
            s21[:, data_index] += (feed_signs[data_dir_index] *
                                   weights[data_dir_index] *
                                   sparam_data.s(2, 1)[indices])
    gain = constants.mag2db(np.abs(s21))

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(FLAGS.frequencies):
        if FLAGS.simulations:
            simulation_frequency_df = simulation_df[np.isclose(
                simulation_df[simulation_frequency_column] * 1e9,
                frequency,
            )]
        has_simulation = FLAGS.simulations and len(simulation_frequency_df) > 0

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
            simulated_gain = constants.mag2db(
                np.linalg.norm(
                    [
                        simulation_frequency_df[SIMULATION_RE_PHI_COLUMN],
                        simulation_frequency_df[SIMULATION_RE_THETA_COLUMN]
                    ],
                    axis=0,
                ))
            ax.plot(
                simulation_frequency_df[simulation_angle_column],
                simulated_gain - simulated_gain.max() +
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
        if FLAGS.simulations:
            simulation_frequency_df = simulation_df[np.isclose(
                simulation_df[simulation_frequency_column] * 1e9,
                frequency,
            )]
        has_simulation = FLAGS.simulations and len(simulation_frequency_df) > 0

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
            simulated_gain = constants.mag2db(
                np.linalg.norm(
                    [
                        simulation_frequency_df[SIMULATION_RE_PHI_COLUMN],
                        simulation_frequency_df[SIMULATION_RE_THETA_COLUMN],
                    ],
                    axis=0,
                ))
            ax.plot(
                constants.deg2rad(
                    simulation_frequency_df[simulation_angle_column]),
                simulated_gain - simulated_gain.max() +
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
    flags.DEFINE_string("config", None, "Antenna array configuration.")
    flags.DEFINE_float("start", None, "Start position in degrees.")
    flags.DEFINE_float("stop", None, "Stop position in degrees.")
    flags.DEFINE_float(
        "step",
        None,
        "Step position in degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_multi_string("data_dirs", None, "Data directories.")
    flags.DEFINE_string("data_prefix", "antenna_sweep", "Data file prefix.")
    flags.DEFINE_multi_float("frequencies", None, "Frequencies to plot in Hz.")
    flags.DEFINE_multi_string("labels", None, "Labels for the plot.")
    flags.DEFINE_multi_string("simulations", [],
                              "HFSS rE simulation result CSV files.")
    flags.DEFINE_enum("slice", None, [
        radiation_pattern_slice.value
        for radiation_pattern_slice in RadiationPatternSlice
    ], "Radiation pattern slice.")
    flags.DEFINE_float("azimuth", 0, "Azimuth in degrees.")
    flags.DEFINE_float("elevation", 0, "Elevation in degrees.")
    flags.mark_flags_as_required([
        "config",
        "start",
        "stop",
        "step",
        "data_dirs",
        "frequencies",
        "slice",
    ])

    app.run(main)
