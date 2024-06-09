"""Compares the decaying exponential estimators, including the regression
estimators and the Prony complex exponential estimators.
"""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.estimator.exponential.exponential_regression_decaying_exponential_estimator import \
    ExponentialRegressionDecayingExponentialEstimator
from simulation.estimator.exponential.linear_regression_decaying_exponential_estimator import \
    LinearRegressionDecayingExponentialEstimator
from simulation.estimator.exponential.weighted_linear_regression_decaying_exponential_estimator import \
    WeightedLinearRegressionDecayingExponentialEstimator
from simulation.estimator.prony.prony_mpm_complex_exponential_estimator import (
    PronyMpmComplexExponentialEstimator,
    PronyMpmNoiseComplexExponentialEstimator)
from simulation.estimator.real_exponential import (RealExponential,
                                                   RealExponentialParams)

FLAGS = flags.FLAGS

# Sampling frequency in Hz.
SAMPLING_FREQUENCY = 1

# Maximum number of samples of the decaying exponential.
DECAYING_EXPONENTIAL_MAX_NUM_SAMPLES = 1000

# Decaying exponential estimators.
DECAYING_EXPONENTIAL_ESTIMATORS = {
    "Exponential Regression":
        ExponentialRegressionDecayingExponentialEstimator,
    "Linear Regression":
        LinearRegressionDecayingExponentialEstimator,
    "Weighted Linear Regression":
        WeightedLinearRegressionDecayingExponentialEstimator,
    "Prony Matrix Pencil Method":
        PronyMpmComplexExponentialEstimator,
    "Prony Matrix Pencil Method with Noise":
        PronyMpmNoiseComplexExponentialEstimator,
}

# Decaying exponential parameters.
DECAYING_EXPONENTIAL_PARAMETERS = {
    "amplitude": "amplitude",
    "alpha": "damping factor",
}

# Histogram bins of decaying exponential parameters.
DECAYING_EXPONENTIAL_PARAMETER_HISTOGRAM_BINS = {
    "amplitude": np.linspace(-0.03, 0.03, 1000),
    "alpha": np.linspace(-0.04, 0.04, 1000),
}


def compare_decaying_exponential_estimators(snrs: np.ndarray,
                                            num_iterations: int) -> None:
    """Compares the RMS estimation error of the decaying exponential estimators.

    Args:
        snrs: SNRs to simulate.
        num_iterations: Number of iterations per SNR.
    """
    params_errors_over_estimator = {}
    params_normalized_errors_over_estimator = {}
    for (decaying_exponential_estimator_label,
         decaying_exponential_estimator_cls
        ) in DECAYING_EXPONENTIAL_ESTIMATORS.items():
        params_rms_errors_over_snr = {
            param: np.zeros(len(snrs))
            for param in DECAYING_EXPONENTIAL_PARAMETERS
        }
        params_normalized_errors = {
            param: np.zeros(len(snrs) * num_iterations)
            for param in DECAYING_EXPONENTIAL_PARAMETERS
        }
        for snr_index, snr in enumerate(snrs):
            # Simulate the estimation error for each parameter.
            params_errors = {
                param: np.zeros(num_iterations)
                for param in DECAYING_EXPONENTIAL_PARAMETERS
            }
            for i in range(num_iterations):
                # Generate a decaying exponential with a random damping factor.
                # At least 10 samples are needed before decaying by 3tau.
                damping_factor = np.random.uniform(-3 / 10, 0)
                params = RealExponentialParams(amplitude=1,
                                               alpha=damping_factor)
                num_samples = min(int(-5 / damping_factor),
                                  DECAYING_EXPONENTIAL_MAX_NUM_SAMPLES)
                decaying_exponential = RealExponential(fs=SAMPLING_FREQUENCY,
                                                       num_samples=num_samples,
                                                       params=params,
                                                       snr=snr)
                # Estimate the parameters of the decaying exponential.
                estimator = decaying_exponential_estimator_cls(
                    decaying_exponential, SAMPLING_FREQUENCY)
                estimated_params = estimator.estimate_single_exponential()
                for param in DECAYING_EXPONENTIAL_PARAMETERS:
                    estimated_param = getattr(estimated_params, param)
                    actual_param = getattr(params, param)
                    param_error = estimated_param - actual_param
                    params_errors[param][i] = param_error
                    params_normalized_errors[param][
                        snr_index * num_iterations +
                        i] = param_error / actual_param
            # Calculate the RMS error for each parameter for the SNR.
            for param in DECAYING_EXPONENTIAL_PARAMETERS:
                params_rms_errors_over_snr[param][snr_index] = np.sqrt(
                    np.mean(params_errors[param]**2))
        params_errors_over_estimator[
            decaying_exponential_estimator_label] = params_rms_errors_over_snr
        params_normalized_errors_over_estimator[
            decaying_exponential_estimator_label] = params_normalized_errors

    for param in DECAYING_EXPONENTIAL_PARAMETERS:
        plt.style.use(["science", "grid"])

        # Plot the RMS error over SNR.
        fig, ax = plt.subplots(figsize=(12, 8))
        for decaying_exponential_estimator_label, marker in zip(
                DECAYING_EXPONENTIAL_ESTIMATORS.keys(), "o^svD"):
            ax.plot(snrs,
                    params_errors_over_estimator[
                        decaying_exponential_estimator_label][param],
                    label=decaying_exponential_estimator_label,
                    marker=marker)
        ax.set_xlabel("SNR [dB]")
        ax.set_ylabel(f"{DECAYING_EXPONENTIAL_PARAMETERS[param].capitalize()} "
                      f"RMS error")
        ax.set_title(f"Decaying exponential estimator "
                     f"{DECAYING_EXPONENTIAL_PARAMETERS[param]} RMS error")
        ax.legend()
        plt.show()

        # Plot a histogram of the normalized estimation error.
        fig, ax = plt.subplots(figsize=(12, 8))
        bins = DECAYING_EXPONENTIAL_PARAMETER_HISTOGRAM_BINS[param]
        for decaying_exponential_estimator_label in DECAYING_EXPONENTIAL_ESTIMATORS:
            ax.hist(params_normalized_errors_over_estimator[
                decaying_exponential_estimator_label][param],
                    bins=bins,
                    label=decaying_exponential_estimator_label,
                    alpha=0.4,
                    density=True)
        ax.set_xlabel(f"Normalized {DECAYING_EXPONENTIAL_PARAMETERS[param]} "
                      f"error")
        ax.set_ylabel("PDF")
        ax.set_title(f"PDF of normalized decaying exponential estimator "
                     f"{DECAYING_EXPONENTIAL_PARAMETERS[param]} error")
        ax.legend()
        plt.show()


def main(argv):
    assert len(argv) == 1, argv

    snrs = np.arange(FLAGS.min_snr, FLAGS.max_snr + 1)
    compare_decaying_exponential_estimators(snrs, FLAGS.num_iterations)


if __name__ == "__main__":
    flags.DEFINE_float("min_snr", 30, "Minimum SNR in dB.")
    flags.DEFINE_float("max_snr", 60, "Maximum SNR in dB.")
    flags.DEFINE_integer("num_iterations",
                         10000,
                         "Number of iterations per SNR.",
                         lower_bound=0)

    app.run(main)
