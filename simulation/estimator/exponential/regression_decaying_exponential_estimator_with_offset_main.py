"""Compares the decaying exponential estimators, including the regression
estimators and the Prony complex exponential estimators, where a vertical
offset is present.
"""

from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags, logging

from simulation.estimator.exponential.exponential_regression_decaying_exponential_estimator import \
    ExponentialRegressionDecayingExponentialEstimator
from simulation.estimator.exponential.linear_regression_decaying_exponential_estimator import \
    LinearRegressionDecayingExponentialEstimator
from simulation.estimator.exponential.regression_decaying_exponential_estimator import \
    RegressionDecayingExponentialEstimator
from simulation.estimator.exponential.weighted_linear_regression_decaying_exponential_estimator import \
    WeightedLinearRegressionDecayingExponentialEstimator
from simulation.estimator.prony.prony_complex_exponential_estimator import \
    PronyComplexExponentialEstimator
from simulation.estimator.prony.prony_mpm_complex_exponential_estimator import (
    PronyMpmComplexExponentialEstimator,
    PronyMpmNoiseComplexExponentialEstimator)
from simulation.estimator.real_exponential import (RealExponential,
                                                   RealExponentialParams)

FLAGS = flags.FLAGS

# Maximum number of samples of the decaying exponential.
DECAYING_EXPONENTIAL_MAX_NUM_SAMPLES = 1000

# Decaying exponential parameters.
DECAYING_EXPONENTIAL_PARAMETERS = {
    "amplitude": "amplitude",
    "alpha": "damping factor",
}

# Histogram bins of decaying exponential parameters.
DECAYING_EXPONENTIAL_PARAMETER_HISTOGRAM_BINS = {
    "amplitude": np.linspace(-0.05, 0.05, 1000),
    "alpha": np.linspace(-0.2, 0.2, 1000),
}


def _estimate_decaying_exponential_with_regression(
    estimator_cls: RegressionDecayingExponentialEstimator
) -> Callable[[RealExponential], RealExponentialParams]:
    """Estimates the parameters of the decaying exponential with a regression.

    Args:
        estimator_cls: Regression decaying exponential estimator.

    Returns:
        A function that given the decaying exponential will output its
        estimated parameters.
    """

    def _estimate_decaying_exponential(
            decaying_exponential: RealExponential) -> RealExponentialParams:
        """Estimates the parameters of the decaying exponential.

        Args:
            decaying_exponential: Samples of the decaying exponential.

        Returns:
            The estimated parameters of the decaying exponential.
        """
        estimator = estimator_cls(decaying_exponential, fs=1, offset=True)
        return estimator.estimate_single_exponential()

    return _estimate_decaying_exponential


def _estimate_decaying_exponential_with_prony(
    estimator_cls: PronyComplexExponentialEstimator
) -> Callable[[RealExponential], RealExponentialParams]:
    """Estimates the parameters of the decaying exponential with Prony's method.

    Args:
        estimator_cls: Regression decaying exponential estimator.

    Returns:
        A function that given the decaying exponential will output its
        estimated parameters.
    """

    def _estimate_decaying_exponential(
            decaying_exponential: RealExponential) -> RealExponentialParams:
        """Estimates the parameters of the decaying exponential.

        Args:
            decaying_exponential: Samples of the decaying exponential.

        Returns:
            The estimated parameters of the decaying exponential.
        """
        estimator = estimator_cls(decaying_exponential, fs=1)
        # The offset is treated as the second complex exponential.
        params = estimator.estimate_multiple_exponentials(num_exponentials=2)
        # Return the parameters whose damping factor is more negative.
        return min(params, key=lambda param: param.alpha)

    return _estimate_decaying_exponential


# Decaying exponential estimators.
DECAYING_EXPONENTIAL_ESTIMATORS = {
    "Exponential Regression":
        (ExponentialRegressionDecayingExponentialEstimator,
         _estimate_decaying_exponential_with_regression),
    "Linear Regression": (LinearRegressionDecayingExponentialEstimator,
                          _estimate_decaying_exponential_with_regression),
    "Weighted Linear Regression":
        (WeightedLinearRegressionDecayingExponentialEstimator,
         _estimate_decaying_exponential_with_regression),
    "Prony Matrix Pencil Method": (PronyMpmComplexExponentialEstimator,
                                   _estimate_decaying_exponential_with_prony),
    "Prony Matrix Pencil Method with Noise":
        (PronyMpmNoiseComplexExponentialEstimator,
         _estimate_decaying_exponential_with_prony),
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
         (decaying_exponential_estimator_cls, estimate_decaying_exponential
         )) in DECAYING_EXPONENTIAL_ESTIMATORS.items():
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
                success = False
                while not success:
                    # Generate a decaying exponential with a random damping
                    # factor and vertical offset.
                    # At least 10 samples are needed before decaying by 3tau,
                    # and the exponential should have decayed by 5tau.
                    damping_factor = np.random.uniform(
                        -3 / 10,
                        -1 / (DECAYING_EXPONENTIAL_MAX_NUM_SAMPLES / 5))
                    params = RealExponentialParams(amplitude=1,
                                                   alpha=damping_factor)
                    num_samples = min(int(-5 / damping_factor),
                                      DECAYING_EXPONENTIAL_MAX_NUM_SAMPLES)
                    offset = np.random.uniform(0, 10)
                    decaying_exponential = RealExponential(
                        fs=1,
                        num_samples=num_samples,
                        params=params,
                        snr=snr,
                    ) + RealExponential(
                        fs=1,
                        num_samples=num_samples,
                        amplitude=offset,
                        alpha=0,
                        snr=np.inf,
                    )

                    # Estimate the parameters of the decaying exponential.
                    try:
                        estimated_params = estimate_decaying_exponential(
                            decaying_exponential_estimator_cls)(
                                decaying_exponential)
                    except np.linalg.LinAlgError as e:
                        logging.exception((
                            "Failed to estimate the parameters of the decaying "
                            "exponential: %s"), e)
                    else:
                        success = True

                for param in DECAYING_EXPONENTIAL_PARAMETERS:
                    params_errors[param][i] = (
                        getattr(estimated_params, param) -
                        getattr(params, param))
                    params_normalized_errors[param][
                        snr_index * num_iterations +
                        i] = (getattr(estimated_params, param) -
                              getattr(params, param)) / getattr(params, param)
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
                    alpha=0.5,
                    density=True)
        ax.set_xlabel(f"Normalized {DECAYING_EXPONENTIAL_PARAMETERS[param]} "
                      f"RMS error")
        ax.set_ylabel("PDF")
        ax.set_title(f"PDF of normalized decaying exponential estimator "
                     f"{DECAYING_EXPONENTIAL_PARAMETERS[param]} RMS error")
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
