"""Plots the radiation pattern from measured S2P files."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

import utils.visualization.mpl_config
from utils import constants
from utils.network.sparam_viewer import SParamViewer

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1

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
    for frequency_index in range(len(FLAGS.frequencies)):
        ax.plot(
            positions,
            data[frequency_index],
            label=FLAGS.labels[frequency_index] if FLAGS.labels else None,
            marker="^",
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
    ax.set_theta_zero_location("N")
    for frequency_index in range(len(FLAGS.frequencies)):
        pattern = data[frequency_index] - np.max(data[frequency_index])
        ax.plot(
            constants.deg2rad(positions),
            pattern,
            label=FLAGS.labels[frequency_index] if FLAGS.labels else None,
            marker="^",
        )
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
    flags.mark_flags_as_required(
        ["start", "stop", "step", "data_dir", "frequencies"])

    app.run(main)
