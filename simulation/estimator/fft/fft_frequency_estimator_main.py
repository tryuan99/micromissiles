"""Compares the FFT frequency estimators."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.estimator.complex_exponential import ComplexExponential
from simulation.estimator.fft.fft_frequency_estimator import (
    FftJacobsenFrequencyEstimator, FftParabolicInterpolationFrequencyEstimator,
    FftPeakFrequencyEstimator, FftTwoPointDtftFrequencyEstimator)
from utils import constants

FLAGS = flags.FLAGS

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 1

# FFT frequency estimators.
FFT_FREQUENCY_ESTIMATORS = {
    "FFT Peak": FftPeakFrequencyEstimator,
    "FFT Parabolic Interpolation": FftParabolicInterpolationFrequencyEstimator,
    "FFT Jacobsen": FftJacobsenFrequencyEstimator,
    "FFT Two-Point DTFT": FftTwoPointDtftFrequencyEstimator,
}


def _calculate_frequency_error(fs: float, estimated_frequency: float,
                               actual_frequency: float) -> float:
    """Calculates the frequency error.

    Args:
        fs: Sampling frequency in Hz.
        estimated_frequency: Estimated frequency in Hz.
        actual_frequency: Actual frequency in HZ.

    Returns:
        The frequency error in Hz.
    """
    # Account for possible wraparound.
    estimated_frequency_aliases = (estimated_frequency +
                                   np.array([-1, 0, 1]) * fs)
    frequency_errors = estimated_frequency_aliases - actual_frequency
    return min(frequency_errors, key=np.abs)


def compare_fft_frequency_estimators(num_samples: int, fft_length: int,
                                     snrs: np.ndarray,
                                     num_iterations: int) -> None:
    """Compares the RMS estimation error of the FFT frequency estimators.

    Args:
        num_samples: Number of samples.
        fft_length: FFT length.
        snrs: SNRs to simulate.
        num_iterations: Number of iterations per SNR.
    """
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    for (fft_frequency_estimator_label,
         fft_frequency_estimator_cls), marker in zip(
             FFT_FREQUENCY_ESTIMATORS.items(), "o^sv"):
        rms_error_over_snr = np.zeros(len(snrs))
        for snr_index, snr in enumerate(snrs):
            # Simulate the estimation error in units of FFT bins.
            errors = np.zeros(num_iterations)
            for i in range(num_iterations):
                # Generate a sinusoid with a random frequency.
                frequency = np.random.uniform(-SAMPLING_FREQUENCY / 2,
                                              SAMPLING_FREQUENCY / 2)
                phase = np.random.uniform(0, 2 * np.pi)
                sinusoid = ComplexExponential(fs=SAMPLING_FREQUENCY,
                                              num_samples=num_samples,
                                              frequency=frequency,
                                              phase=phase,
                                              amplitude=1,
                                              alpha=0,
                                              snr=snr)
                # Estimate the frequency.
                estimator = fft_frequency_estimator_cls(
                    sinusoid,
                    SAMPLING_FREQUENCY,
                    fft_length,
                    window=np.ones(num_samples))
                estimated_frequency = estimator.estimate_single_frequency()
                frequency_error = _calculate_frequency_error(
                    SAMPLING_FREQUENCY, estimated_frequency, frequency)
                # Convert from units of Hz to units of FFT bins.
                errors[i] = frequency_error * fft_length
            # Calculate the RMS error for the SNR.
            rms_error_over_snr[snr_index] = np.sqrt(np.mean(errors**2))
        # Plot the RMS error over SNR for the estimator.
        ax.plot(snrs,
                rms_error_over_snr,
                label=fft_frequency_estimator_label,
                marker=marker)
    ax.set_xlabel("SNR [dB]")
    ax.set_ylabel("Frequency estimator RMS error [FFT bin]")
    ax.set_title(
        f"Frequency estimator RMS error (number of samples={num_samples}, "
        f"FFT length={fft_length})")
    ax.legend()
    plt.show()


def plot_normalized_estimation_error_histogram() -> None:
    """Plots the histogram of the normalized frequency estimation error.

    See Fig. 3 of https://ieeexplore.ieee.org/document/10313215.
    """
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    num_iterations = 1000000
    bins = np.linspace(-10, 10, 1000)
    for (fft_frequency_estimator_label,
         fft_frequency_estimator) in FFT_FREQUENCY_ESTIMATORS.items():
        normalized_frequency_errors = np.zeros(num_iterations)
        for i in range(num_iterations):
            # Generate a sinusoid with a random frequency.
            num_samples = np.random.randint(10, 1000 + 1)
            frequency = np.random.uniform(-SAMPLING_FREQUENCY / 2,
                                          SAMPLING_FREQUENCY / 2)
            phase = np.random.uniform(0, 2 * np.pi)
            snr = np.random.randint(-40, 5 + 1)
            sinusoid = ComplexExponential(fs=SAMPLING_FREQUENCY,
                                          num_samples=num_samples,
                                          frequency=frequency,
                                          phase=phase,
                                          amplitude=1,
                                          alpha=0,
                                          snr=snr)
            # Estimate the frequency.
            estimator = fft_frequency_estimator(sinusoid,
                                                SAMPLING_FREQUENCY,
                                                num_samples,
                                                window=np.ones(num_samples))
            estimated_frequency = estimator.estimate_single_frequency()
            frequency_error = _calculate_frequency_error(
                SAMPLING_FREQUENCY, estimated_frequency, frequency)
            # Convert from units of Hz to units of radians.
            frequency_error_rad = 2 * np.pi * frequency_error
            crlb = np.sqrt(12) / (num_samples**(3 / 2) * constants.db2mag(snr))
            normalized_frequency_error = frequency_error_rad / crlb
            normalized_frequency_errors[i] = normalized_frequency_error
        # Plot a histogram of the normalized frequency errors.
        ax.hist(normalized_frequency_errors,
                bins=bins,
                label=fft_frequency_estimator_label,
                alpha=0.4,
                density=True)
    ax.set_xlabel("Normalized frequency estimator error")
    ax.set_ylabel("PDF")
    ax.set_title("PDF of normalized frequency estimator error")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    snrs = np.arange(FLAGS.min_snr, FLAGS.max_snr + 1)
    compare_fft_frequency_estimators(FLAGS.num_samples, FLAGS.fft_length, snrs,
                                     FLAGS.num_iterations)
    # plot_normalized_estimation_error_histogram()


if __name__ == "__main__":
    flags.DEFINE_integer("num_samples", 64, "Number of samples.", lower_bound=0)
    flags.DEFINE_integer("fft_length", 256, "FFT length.", lower_bound=0)
    flags.DEFINE_float("min_snr", -10, "Minimum SNR in dB.")
    flags.DEFINE_float("max_snr", 10, "Maximum SNR in dB.")
    flags.DEFINE_integer("num_iterations",
                         10000,
                         "Number of iterations per SNR.",
                         lower_bound=0)

    app.run(main)
