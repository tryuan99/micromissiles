"""Simulates the signal-to-noise ratio as a function of the target range."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.radar import Radar
from simulation.radar.components.target import Target
from utils import constants

FLAGS = flags.FLAGS

# Minimum SNR in dB for detecting the target.
MINIMUM_SNR = 15  # dB


def _plot_snr_vs_range(radar: Radar, rcs: float) -> None:
    """Plots the signal and noise amplitudes as a function of the target range.

    Args:
        radar: Radar.
        rcs: Radar cross section in dBsm.
    """
    target = Target(rcs=rcs)
    fft_processing_gain = radar.N_r * radar.N_v

    # Calculate the noise amplitude in dB before and after the 2D FFT.
    noise_amplitude_db = constants.mag2db(
        np.sqrt(radar.N_rx) * radar.get_noise_amplitude())
    noise_fft_magnitude_db = noise_amplitude_db + constants.mag2db(
        radar.get_fft_processing_gain(noise=True))

    # Calculate the signal amplitude and FFT peak magnitude in dB for each range.
    ranges = np.arange(1, int(radar.r_max + 1))
    signal_amplitudes_db = np.zeros(len(ranges))
    for i, range in enumerate(ranges):
        target.range = range
        signal_amplitudes_db[i] = constants.mag2db(
            radar.N_tx * radar.N_rx * AdcData.get_if_amplitude(radar, target))
    signal_fft_peak_magnitudes_db = signal_amplitudes_db + constants.mag2db(
        radar.get_fft_processing_gain())

    # Plot the signal amplitude as a function of the target range.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(ranges, signal_amplitudes_db, label="Signal amplitude")
    plt.axhline(noise_amplitude_db, color="r", label="Noise amplitude")
    ax.set_title("Signal amplitude vs. range")
    ax.set_xlabel("Target range in m")
    ax.set_ylabel("Signal amplitude in dB")
    plt.legend()
    plt.show()

    # Plot the FFT peak magnitude as a function of the target range.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(ranges,
             signal_fft_peak_magnitudes_db,
             label="Signal FFT peak magnitude")
    plt.axhline(noise_fft_magnitude_db, color="r", label="Noise magnitude")
    plt.axhline(
        noise_fft_magnitude_db + MINIMUM_SNR,
        color="g",
        label=f"Noise magnitude + {MINIMUM_SNR} dB",
    )
    ax.set_title("FFT peak magnitude vs. range")
    ax.set_xlabel("Target range in m")
    ax.set_ylabel("FFT magnitude in dB")
    plt.legend()
    plt.show()


def plot_snr_vs_range_siso(
    rcs: float,
    temperature: float,
) -> None:
    """Plots the signal and noise amplitudes as a function of the target range
    for a SISO radar.

    Args:
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
    """
    radar = Radar(temperature=temperature)
    radar.N_tx = 1
    radar.N_rx = 1
    _plot_snr_vs_range(radar, rcs)


def plot_snr_vs_range_phased_array(
    rcs: float,
    temperature: float,
) -> None:
    """Plots the signal and noise amplitudes as a function of the target range
    for a phased array MIMO radar.

    Args:
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
    """
    radar = Radar(temperature=temperature)
    _plot_snr_vs_range(radar, rcs)


def main(argv):
    assert len(argv) == 1, argv
    plot_snr_vs_range_siso(FLAGS.rcs, FLAGS.temperature)
    plot_snr_vs_range_phased_array(FLAGS.rcs, FLAGS.temperature)


if __name__ == "__main__":
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 30, "Temperature in Celsius.")

    app.run(main)
