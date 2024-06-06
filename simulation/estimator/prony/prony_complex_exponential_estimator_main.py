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
    "frequency": np.linspace(-0.0025, 0.0025, 1000),
    "amplitude": np.linspace(-0.025, 0.025, 1000),
    "alpha": np.linspace(-0.05, 0.05, 1000),
}


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
                frequency = np.random.uniform(-0.5, 0.5)
                phase = np.random.uniform(0, 2 * np.pi)
                # At least 10 samples are needed before decaying by 3tau.
                damping_factor = np.random.uniform(-3 / 10, 0)
                params = ComplexExponentialParams(frequency=frequency,
                                                  phase=phase,
                                                  amplitude=1,
                                                  alpha=damping_factor)
                # Maximum 1000 samples per complex exponential.
                num_samples = min(int(-3 / damping_factor), 1000)
                complex_exponential = ComplexExponential(
                    fs=1, num_samples=num_samples, params=params, snr=snr)
                # Estimate the parameters of the complex exponential.
                estimator = complex_exponential_estimator_cls(
                    complex_exponential, fs=1)
                estimated_params = estimator.estimate_single_exponential()
                for param in COMPLEX_EXPONENTIAL_PARAMETERS:
                    params_errors[param][i] = (
                        getattr(estimated_params, param) -
                        getattr(params, param))
                    params_normalized_errors[param][
                        snr_index * num_iterations +
                        i] = (getattr(estimated_params, param) -
                              getattr(params, param)) / getattr(params, param)
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
                    alpha=0.5,
                    density=True)
        ax.set_xlabel(f"Normalized {COMPLEX_EXPONENTIAL_PARAMETERS[param]} "
                      f"RMS error")
        ax.set_ylabel("PDF")
        ax.set_title(f"PDF of normalized complex exponential estimator "
                     f"{COMPLEX_EXPONENTIAL_PARAMETERS[param]} RMS error")
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
