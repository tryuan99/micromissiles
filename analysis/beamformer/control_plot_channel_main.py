"""Plots the VGA gain and phase control of multiple beamformer channels at a
single frequency from measured S2P files.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

import utils.visualization.mpl_config
from utils import constants
from utils.network.sparam_viewer import SParamViewer

FLAGS = flags.FLAGS

# Number of VGA gain codes and phases.
NUM_VGA_GAINS = 128
NUM_PHASES = 128

# Phase step per phase index in degrees.
PHASE_STEP = 2.825


def _plot(
    channels: list[int],
    labels: list[str] | None,
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str,
    ylabel: str,
    ideal: np.ndarray | None = None,
) -> None:
    """Plots one trace per frequency.

    Args:
        channels: List of channels to plot.
        labels: List of plot labels.
        x: x-axis values.
        y: y-axis values with shape (number of channels, len(x)).
        xlabel: x-axis label.
        ylabel: y-axis label.
        ideal: Optional ideal y-axis values.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    for channel_index in range(len(channels)):
        ax.plot(
            x,
            y[channel_index],
            color=f"C{channel_index}",
            label=labels[channel_index] if labels else None,
            marker="^",
        )
    if ideal is not None:
        ax.plot(x, ideal, color="black", linestyle="--")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if labels:
        ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    gains = np.arange(NUM_VGA_GAINS)
    phases = np.arange(NUM_PHASES)
    gain_s21 = np.empty(
        (len(FLAGS.channels), NUM_VGA_GAINS),
        dtype=complex,
    )
    phase_s21 = np.empty((len(FLAGS.channels), NUM_PHASES), dtype=complex)
    sweeps = [
        (gain_s21, gains, np.full_like(gains, FLAGS.phase)),
        (phase_s21, np.full_like(phases, FLAGS.vga_gain), phases),
    ]
    for s21, sweep_gains, sweep_phases in sweeps:
        for channel_index, channel in enumerate(FLAGS.channels):
            for data_index, (gain,
                             phase) in enumerate(zip(sweep_gains,
                                                     sweep_phases)):
                data_path = (Path(FLAGS.data_dir) /
                             (f"{FLAGS.data_prefix}_channel_{channel}_vga_gain_"
                              f"{gain}_phase_{phase}.s2p"))

                sparam_data = SParamViewer(data_path)
                index = np.abs(sparam_data.frequency() -
                               FLAGS.frequency).argmin()
                s21[channel_index, data_index] = sparam_data.s(2, 1)[index]

    gain_abs = np.abs(gain_s21)
    gain_abs_step = np.diff(gain_abs, axis=1)
    gain_phase = constants.rad2deg(np.angle(gain_s21))
    gain_db = constants.mag2db(gain_abs)

    for channel_index, channel in enumerate(FLAGS.channels):
        logging.info(
            "Channel %d: gain range = %.3f dB (%.3f dB to %.3f dB), gain-dependent "
            "phase shift range = %.3f deg (%.3f deg to %.3f deg).", channel,
            np.ptp(gain_db[channel_index]),
            gain_db[channel_index].min(), gain_db[channel_index].max(),
            np.ptp(gain_phase[channel_index]), gain_phase[channel_index].min(),
            gain_phase[channel_index].max())

    _plot(
        FLAGS.channels,
        FLAGS.labels,
        gains,
        gain_abs,
        "VGA gain",
        "S21 Magnitude",
    )
    _plot(
        FLAGS.channels,
        FLAGS.labels,
        gains[1:],
        gain_abs_step,
        "VGA gain",
        "S21 Magnitude Step",
    )
    _plot(
        FLAGS.channels,
        FLAGS.labels,
        gains,
        gain_phase,
        "VGA gain",
        "S21 Relative Phase [deg]",
    )

    phases_deg = phases * PHASE_STEP
    phase_error = (constants.rad2deg(np.angle(phase_s21 / phase_s21[:, :1])) -
                   phases_deg + 180) % 360 - 180
    phase = phase_error + phases_deg
    phase_gain = constants.mag2db(np.abs(phase_s21))

    for channel_index, channel in enumerate(FLAGS.channels):
        logging.info(
            "Channel %d: RMS phase error = %.3f deg, peak phase error = %.3f deg, "
            "magnitude variation = %.3f dB.", channel,
            np.sqrt(np.mean(phase_error[channel_index]**2)),
            np.abs(phase_error[channel_index]).max(),
            np.ptp(phase_gain[channel_index]))

    _plot(
        FLAGS.channels,
        FLAGS.labels,
        phases_deg,
        phase,
        "Phase [deg]",
        "Normalized S21 Phase [deg]",
        ideal=phases_deg,
    )
    _plot(
        FLAGS.channels,
        FLAGS.labels,
        phases_deg,
        phase_error,
        "Phase [deg]",
        "S21 Phase Error [deg]",
    )
    _plot(
        FLAGS.channels,
        FLAGS.labels,
        phases_deg,
        phase_gain,
        "Phase [deg]",
        "S21 Magnitude [dB]",
    )


if __name__ == "__main__":
    flags.DEFINE_string("data_dir", None, "Data directory.")
    flags.DEFINE_string("data_prefix", "beamformer_sweep", "Data file prefix.")
    flags.DEFINE_multi_integer("channels",
                               None,
                               "Beamformer channels.",
                               lower_bound=1,
                               upper_bound=4)
    flags.DEFINE_integer("vga_gain",
                         NUM_VGA_GAINS - 1,
                         "VGA gain code during the phase sweep.",
                         lower_bound=0,
                         upper_bound=NUM_VGA_GAINS - 1)
    flags.DEFINE_integer("phase",
                         0,
                         "Phase index during the VGA gain sweep.",
                         lower_bound=0,
                         upper_bound=NUM_PHASES - 1)
    flags.DEFINE_float("frequency",
                       9e9,
                       "Frequency to plot in Hz.",
                       lower_bound=0.0)
    flags.DEFINE_multi_string("labels", None, "Labels for the plot.")
    flags.mark_flags_as_required(["data_dir", "channels"])

    app.run(main)
