"""Compares the complex exponential estimators using Prony's method."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.estimator.complex_exponential import (ComplexExponential,
                                                      ComplexExponentialParams)
from simulation.estimator.prony.prony_mpm_complex_exponential_estimator import (
    PronyMpmComplexExponentialEstimator,
    PronyMpmNoiseComplexExponentialEstimator)
from simulation.estimator.prony.prony_polynomial_complex_exponential_estimator import \
    PronyPolynomialComplexExponentialEstimator
from utils.solver.least_squares_solver import \
    TotalLeastSquaresMatrixVectorSolver

FLAGS = flags.FLAGS

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 1

# Maximum number of samples of the complex exponential.
COMPLEX_EXPONENTIAL_MAX_NUM_SAMPLES = 1000

# Prony complex exponential estimators.
PRONY_COMPLEX_EXPONENTIAL_ESTIMATORS = {
    "Prony Polynomial Least Squares":
        PronyPolynomialComplexExponentialEstimator,
    "Prony Polynomial Total Least Squares":
        lambda samples, fs: PronyPolynomialComplexExponentialEstimator(
            samples, fs, TotalLeastSquaresMatrixVectorSolver),
    "Prony Matrix Pencil Method":
        PronyMpmComplexExponentialEstimator,
    "Prony Matrix Pencil Method with Noise":
        PronyMpmNoiseComplexExponentialEstimator,
}

# Complex exponential parameters.
COMPLEX_EXPONENTIAL_PARAMETERS = {
    "frequency": "frequency",
    "amplitude": "amplitude",
    "alpha": "damping factor",
}

# Histogram bins of complex exponential parameters.
COMPLEX_EXPONENTIAL_PARAMETER_HISTOGRAM_BINS = {
    "frequency": np.linspace(-0.001, 0.001, 1000),
    "amplitude": np.linspace(-0.025, 0.025, 1000),
    "alpha": np.linspace(-0.05, 0.05, 1000),
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


def compare_prony_complex_exponential_estimators(snrs: np.ndarray,
                                                 num_iterations: int) -> None:
    """Compares the RMS estimation error of the complex exponential estimators.

    Args:
        snrs: SNRs to simulate.
        num_iterations: Number of iterations per SNR.
    """
    params_errors_over_estimator = {}
    params_normalized_errors_over_estimator = {}
    for (complex_exponential_estimator_label, complex_exponential_estimator_cls
        ) in PRONY_COMPLEX_EXPONENTIAL_ESTIMATORS.items():
        params_rms_errors_over_snr = {
            param: np.zeros(len(snrs))
            for param in COMPLEX_EXPONENTIAL_PARAMETERS
        }
        params_normalized_errors = {
            param: np.zeros(len(snrs) * num_iterations)
            for param in COMPLEX_EXPONENTIAL_PARAMETERS
        }
        for snr_index, snr in enumerate(snrs):
            # Simulate the estimation error for each parameter.
            params_errors = {
                param: np.zeros(num_iterations)
                for param in COMPLEX_EXPONENTIAL_PARAMETERS
            }
            for i in range(num_iterations):
                # Generate a complex exponential with a random frequency, phase,
                # and damping factor.
                frequency = np.random.uniform(-SAMPLING_FREQUENCY / 2,
                                              SAMPLING_FREQUENCY / 2)
                phase = np.random.uniform(0, 2 * np.pi)
                # At least 10 samples are needed before decaying by 3tau.
                damping_factor = np.random.uniform(-3 / 10, 0)
                params = ComplexExponentialParams(frequency=frequency,
                                                  phase=phase,
                                                  amplitude=1,
                                                  alpha=damping_factor)
                num_samples = min(int(-3 / damping_factor),
                                  COMPLEX_EXPONENTIAL_MAX_NUM_SAMPLES)
                complex_exponential = ComplexExponential(
                    fs=SAMPLING_FREQUENCY,
                    num_samples=num_samples,
                    params=params,
                    snr=snr)
                # Estimate the parameters of the complex exponential.
                estimator = complex_exponential_estimator_cls(
                    complex_exponential, SAMPLING_FREQUENCY)
                estimated_params = estimator.estimate_single_exponential()
                for param in COMPLEX_EXPONENTIAL_PARAMETERS:
                    estimated_param = getattr(estimated_params, param)
                    actual_param = getattr(params, param)
                    if param == "frequency":
                        param_error = _calculate_frequency_error(
                            SAMPLING_FREQUENCY, estimated_param, actual_param)
                    else:
                        param_error = estimated_param - actual_param
                    params_errors[param][i] = param_error
                    params_normalized_errors[param][
                        snr_index * num_iterations +
                        i] = param_error / actual_param
            # Calculate the RMS error for each parameter for the SNR.
            for param in COMPLEX_EXPONENTIAL_PARAMETERS:
                params_rms_errors_over_snr[param][snr_index] = np.sqrt(
                    np.mean(params_errors[param]**2))
        params_errors_over_estimator[
            complex_exponential_estimator_label] = params_rms_errors_over_snr
        params_normalized_errors_over_estimator[
            complex_exponential_estimator_label] = params_normalized_errors

    for param in COMPLEX_EXPONENTIAL_PARAMETERS:
        plt.style.use(["science", "grid"])

        # Plot the RMS error over SNR.
        fig, ax = plt.subplots(figsize=(12, 8))
        for complex_exponential_estimator_label, marker in zip(
                PRONY_COMPLEX_EXPONENTIAL_ESTIMATORS.keys(), "o^sv"):
            ax.plot(snrs,
                    params_errors_over_estimator[
                        complex_exponential_estimator_label][param],
                    label=complex_exponential_estimator_label,
                    marker=marker)
        ax.set_xlabel("SNR [dB]")
        ax.set_ylabel(f"{COMPLEX_EXPONENTIAL_PARAMETERS[param].capitalize()} "
                      f"RMS error")
        ax.set_title(f"Complex exponential estimator "
                     f"{COMPLEX_EXPONENTIAL_PARAMETERS[param]} RMS error")
        ax.legend()
        plt.show()

        # Plot a histogram of the normalized estimation error.
        fig, ax = plt.subplots(figsize=(12, 8))
        bins = COMPLEX_EXPONENTIAL_PARAMETER_HISTOGRAM_BINS[param]
        for complex_exponential_estimator_label in PRONY_COMPLEX_EXPONENTIAL_ESTIMATORS:
            ax.hist(params_normalized_errors_over_estimator[
                complex_exponential_estimator_label][param],
                    bins=bins,
                    label=complex_exponential_estimator_label,
                    alpha=0.4,
                    density=True)
        ax.set_xlabel(f"Normalized {COMPLEX_EXPONENTIAL_PARAMETERS[param]} "
                      f"error")
        ax.set_ylabel("PDF")
        ax.set_title(f"PDF of normalized complex exponential estimator "
                     f"{COMPLEX_EXPONENTIAL_PARAMETERS[param]} error")
        ax.legend()
        plt.show()


def main(argv):
    assert len(argv) == 1, argv

    snrs = np.arange(FLAGS.min_snr, FLAGS.max_snr + 1)
    compare_prony_complex_exponential_estimators(snrs, FLAGS.num_iterations)


if __name__ == "__main__":
    flags.DEFINE_float("min_snr", 30, "Minimum SNR in dB.")
    flags.DEFINE_float("max_snr", 60, "Maximum SNR in dB.")
    flags.DEFINE_integer("num_iterations",
                         10000,
                         "Number of iterations per SNR.",
                         lower_bound=0)

    app.run(main)
