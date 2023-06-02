"""Plots the instantaneous frequency and phase of various chirps."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

from simulation.radar.components.chirp import CHIRP_MAP, ChirpType
from simulation.radar.components.radar import Radar

FLAGS = flags.FLAGS


def plot_chirp(
    rnge: float,
    chirp_type: ChirpType,
) -> None:
    """Plots the instantaneous frequency and phase of the chirp and of the IF signal.

    Args:
        rnge: Range in m.
        chirp_type: Chirp type.
    """
    radar = Radar()
    tau = 2 * np.full_like(radar.t_axis_chirp, rnge) / radar.c
    chirp = CHIRP_MAP[chirp_type](radar)

    # Plot the waveform of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(radar.t_axis_chirp, chirp.get_signal(real=True))
    ax.set_title(f"Waveform of a {chirp_type} chirp")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    plt.show()

    # Plot the instantaneous frequency and phase of the chirp.
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    ax1.plot(radar.t_axis_chirp, chirp.get_frequency())
    ax1.set_title(f"Instantaneous frequency of a {chirp_type} chirp")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Frequency [Hz]")
    ax2.plot(radar.t_axis_chirp, chirp.get_phase())
    ax2.set_title(f"Phase of a {chirp_type} chirp")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Phase [rad]")
    plt.show()

    # Plot the waveform of the IF of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(radar.t_axis_chirp, chirp.get_if_signal(tau, real=True))
    ax.set_title(f"Waveform of the IF of a {chirp_type} chirp")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    plt.show()

    # Plot the instantaneous frequency and phase of the IF of the chirp.
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    ax1.plot(radar.t_axis_chirp, chirp.get_if_frequency(tau))
    ax1.set_title(f"Instantaneous frequency of the IF of a {chirp_type} chirp")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Frequency [Hz]")
    ax2.plot(radar.t_axis_chirp, chirp.get_if_phase(tau))
    ax2.set_title(f"Phase of the IF of a {chirp_type} chirp")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Phase [rad]")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    plot_chirp(
        FLAGS.range,
        FLAGS.chirp_type,
    )


if __name__ == "__main__":
    flags.DEFINE_float("range", 50, "Range in m.", lower_bound=0.0)
    flags.DEFINE_enum("chirp_type", ChirpType.LINEAR, ChirpType.values(),
                      "Chirp type.")

    app.run(main)
