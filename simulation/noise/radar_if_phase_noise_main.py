"""Plots the IF phase noise spectrum."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.noise.phase_noise import IFPhaseNoise, PhaseNoise
from simulation.radar.components.radar import Radar, Target
from utils import constants

FLAGS = flags.FLAGS

# Number of noise samples to generate.
NUM_PHASE_NOISE_SAMPLES = 256

# FFT length factor.
PHASE_NOISE_FFT_LENGTH_FACTOR = 1024


def plot_if_phase_noise_psd(rnge: float) -> None:
    """Plots the IF phase noise PSD for a target at the given range.

    Args:
        rnge: Range in m.
    """
    radar = Radar()
    target = Target(rnge=rnge)

    # Calculate the LO phase noise levels.
    lo_phase_noise = PhaseNoise(radar=radar)
    lo_offsets, lo_phase_noise_level = (
        lo_phase_noise.calculate_phase_noise_level())

    # Calculate the IF phase noise levels at the given range.
    if_phase_noise = IFPhaseNoise(radar=radar, target=target)
    if_offsets, if_phase_noise_level = (
        if_phase_noise.calculate_phase_noise_level())

    # Plot the phase noise level.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.semilogx(lo_offsets, lo_phase_noise_level, label="LO")
    ax.semilogx(if_offsets, if_phase_noise_level, label=f"IF")
    ax.set_xlabel("Frequency offset [Hz]")
    ax.set_ylabel("Phase noise level [dBc/Hz]")
    ax.legend()
    plt.show()


def plot_generated_phase_noise_spectrum(rnge: float) -> None:
    """Plots the generated IF phase noise spectrum for a target at the given
    range.

    Args:
        rnge: Range in m.
    """
    radar = Radar()
    target = Target(rnge=rnge)

    # Generate IF phase noise for a target at the given range.
    if_phase_noise = IFPhaseNoise(radar=radar, target=target)
    noise_samples = if_phase_noise.generate_noise_samples(
        amplitude=1, length=NUM_PHASE_NOISE_SAMPLES)

    # Plot the generated phase noise.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(np.abs(noise_samples))
    ax.set_xlabel("Noise sample index")
    ax.set_ylabel("Phase noise magnitude")
    plt.show()

    # Calculate the spectrum of the generated noise.
    noise_autocorrelation = np.correlate(noise_samples,
                                         noise_samples,
                                         mode="same")
    fft_length = len(noise_autocorrelation) * PHASE_NOISE_FFT_LENGTH_FACTOR
    noise_spectrum = np.fft.fft(noise_autocorrelation, fft_length)
    noise_spectrum_abs = np.abs(noise_spectrum)

    # Plot the spectrum of the generated phase noise.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    frequency_axis = np.linspace(0, radar.fs, fft_length, endpoint=False)
    ax.semilogx(frequency_axis,
                constants.power2db(noise_spectrum_abs),
                label="Generated phase noise")
    if_offsets, if_phase_noise_level = (
        if_phase_noise.calculate_phase_noise_level())
    resolution_bandwidth = radar.fs / len(noise_autocorrelation)
    ax.semilogx(if_offsets,
                if_phase_noise_level + constants.power2db(resolution_bandwidth),
                label="Expected phase noise")
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Noise power [dBc]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_if_phase_noise_psd(FLAGS.range)
    plot_generated_phase_noise_spectrum(FLAGS.range)


if __name__ == "__main__":
    flags.DEFINE_float("range", 1, "Range in m.", lower_bound=0.0)

    app.run(main)
