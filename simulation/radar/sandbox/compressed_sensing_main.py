"""Simulates applying compressed sensing."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app


def _apply_soft_thresholding(array: np.ndarray, lmbda: float) -> np.ndarray:
    """Applies soft thresholding.

    Applies S(x, lambda) = { 0                      , |x| <= lambda
                           { (|x| - lambda)/|x| * x , |x| > lambda.

    Returns:
        The output of applying soft thresholding.
    """
    array_abs = np.abs(array)
    return (array_abs - lmbda) / array_abs * (array_abs > lmbda) * array


def apply_compressed_sensing_fft_pocs() -> None:
    """Simulates applying compressed sensing to a sparse time domain signal.

    This function uses a projection over convex sets (POCS) algorithm.
    See https://people.eecs.berkeley.edu/~mlustig/CS/CS_ex.pdf for more details.

    The signal is sparse in the time domain, and we use the Fourier transform as
    an incoherent basis. We undersample in the frequency domain and estimate the
    signal with min(1/2 * ||F{x} - Y||_2^2 + lambda * ||x||_1).
    """
    # Length of the sparse signal in the time domain.
    LENGTH = 1024

    # Number of non-zero samples in the time domain.
    SPARSITY = 5

    # Number of samples in the frequency domain.
    NUM_SAMPLES = 128

    LAMBDAS = [0.01, 0.05, 0.1]
    NUM_ITERATIONS = 200

    # Generate the sparse signal in the time domain.
    x = np.zeros(LENGTH)
    x[np.random.permutation(LENGTH)[:SPARSITY] -
      1] = (np.arange(SPARSITY) + 1) * 0.2

    # Undersample in the frequency domain.
    X = np.fft.fft(x)
    Xr = np.zeros(LENGTH, dtype=X.dtype)
    random_indices = np.random.permutation(LENGTH) - 1
    Xr[random_indices[:NUM_SAMPLES]] = X[random_indices[:NUM_SAMPLES]]

    # Apply the projection over convex sets (POCS) algorithm.
    fig, ax = plt.subplots(len(LAMBDAS), 2, figsize=(16, 10), sharex="col")
    for j, lmbda in enumerate(LAMBDAS):
        Y = Xr
        Xi = Xr
        error = np.zeros(NUM_ITERATIONS)
        for i in range(NUM_ITERATIONS):
            xi = np.fft.ifft(Xi)
            # Enforce sparsity.
            xi = _apply_soft_thresholding(xi, lmbda)
            Xi = np.fft.fft(xi)
            # Enforce data consistency.
            Xi = Xi * (Y == 0) + Y
            error[i] = np.linalg.norm(X - Xi) / LENGTH

        # Plot the original and the estimated signals.
        ax[j, 0].plot(np.abs(x), label="Original signal")
        ax[j, 0].plot(np.abs(xi), label="Estimated signal")
        ax[j, 0].set_title(f"Estimated signal for lambda={lmbda}")
        ax[j, 0].set_xlabel("Sample")
        ax[j, 0].set_ylabel("Magnitude")
        ax[j, 0].legend()

        # Plot the error.
        ax[j, 1].plot(error)
        ax[j, 1].set_title(f"Estimation error for lambda={lmbda}")
        ax[j, 1].set_xlabel("Iteration")
        ax[j, 1].set_ylabel("Error")
    plt.show()


def apply_compressed_sensing_ifft_pocs_linear() -> None:
    """Simulates applying compressed sensing to a sparse frequency domain signal.

    The signal is sparse in the frequency domain, and we use the inverse Fourier
    transform as an incoherent basis. We undersample in the time domain and
    estimate the signal with min(1/2 * ||F^-1{X} - y||_2^2 + lambda * ||X||_1).
    """
    # Length of the sparse signal in the frequency domain.
    LENGTH = 16384

    # Number of non-zero samples in the frequency domain.
    SPARSITY = 5

    # Number of samples in the time domain.
    NUM_SAMPLES = 128

    LAMBDAS = [0.1, 1, 10]
    NUM_ITERATIONS = 1000

    # Generate the sparse signal in the frequency domain.
    n = np.arange(LENGTH)
    fs = 100  # Hz
    A = np.random.rand(SPARSITY, 1)
    f = np.random.rand(SPARSITY, 1) * fs / 2
    phi = np.random.rand(SPARSITY, 1) * 2 * np.pi
    x = np.sum(A * np.exp(1j * (2 * np.pi * f / fs * n + phi)), axis=0)
    X = np.fft.fft(x)

    # Undersample in the time domain.
    xr = np.zeros(LENGTH, dtype=x.dtype)
    random_indices = np.random.permutation(LENGTH) - 1
    xr[random_indices[:NUM_SAMPLES]] = x[random_indices[:NUM_SAMPLES]]

    # Apply the projection over convex sets (POCS) algorithm.
    fig, ax = plt.subplots(len(LAMBDAS), 2, figsize=(16, 10), sharex="col")
    for j, lmbda in enumerate(LAMBDAS):
        y = xr
        xi = xr
        error = np.zeros(NUM_ITERATIONS)
        for i in range(NUM_ITERATIONS):
            Xi = np.fft.fft(xi)
            # Enforce sparsity.
            Xi = _apply_soft_thresholding(Xi, lmbda)
            xi = np.fft.ifft(Xi)
            # Enforce data consistency.
            xi = xi * (y == 0) + y
            error[i] = np.linalg.norm(x - xi) / LENGTH

        # Plot the original and the estimated signals.
        ax[j, 0].plot(np.abs(X), label="Original signal")
        ax[j, 0].plot(np.abs(Xi), label="Estimated signal")
        ax[j, 0].set_title(f"Estimated signal for lambda={lmbda}")
        ax[j, 0].set_xlabel("Sample")
        ax[j, 0].set_ylabel("Magnitude")
        ax[j, 0].legend()

        # Plot the error.
        ax[j, 1].plot(error)
        ax[j, 1].set_title(f"Estimation error for lambda={lmbda}")
        ax[j, 1].set_xlabel("Iteration")
        ax[j, 1].set_ylabel("Error")
    plt.show()


def apply_compressed_sensing_ifft_pocs_quadratic() -> None:
    """Simulates applying compressed sensing to a sparse frequency domain signal.
    The signal is sampled quadratically in the time domain.

    The signal is sparse in the frequency domain, and we use the inverse Fourier
    transform as an incoherent basis. We undersample in the time domain and estimate
    the signal with min(1/2 * ||F^-1{X} - y||_2^2 + lambda * ||X||_1).
    """
    # Length of the sparse signal in the frequency domain.
    LENGTH = 16384

    # Number of non-zero samples in the frequency domain.
    SPARSITY = 5

    # Number of samples in the time domain.
    NUM_SAMPLES = 128

    LAMBDAS = [10, 20, 40]
    NUM_ITERATIONS = 1000

    # Generate the sparse signal in the frequency domain.
    n = np.arange(LENGTH)
    fs = 100  # Hz
    A = np.random.rand(SPARSITY, 1)
    f = np.random.rand(SPARSITY, 1) * fs / 2
    phi = np.random.rand(SPARSITY, 1) * 2 * np.pi
    x = np.sum(A * np.exp(1j * (2 * np.pi * f / fs * n + phi)), axis=0)
    X = np.fft.fft(x)

    # Undersample in the time domain.
    xr = np.zeros(LENGTH, dtype=x.dtype)
    xr[np.arange(NUM_SAMPLES)**2] = x[np.arange(NUM_SAMPLES)**2]

    # Apply the projection over convex sets (POCS) algorithm.
    fig, ax = plt.subplots(len(LAMBDAS), 2, figsize=(16, 10), sharex="col")
    for j, lmbda in enumerate(LAMBDAS):
        y = xr
        xi = xr
        error = np.zeros(NUM_ITERATIONS)
        for i in range(NUM_ITERATIONS):
            Xi = np.fft.fft(xi)
            # Enforce sparsity.
            Xi = _apply_soft_thresholding(Xi, lmbda)
            xi = np.fft.ifft(Xi)
            # Enforce data consistency.
            xi = xi * (y == 0) + y
            error[i] = np.linalg.norm(x - xi) / LENGTH

        # Plot the original and the estimated signals.
        ax[j, 0].plot(np.abs(X), label="Original signal")
        ax[j, 0].plot(np.abs(Xi), label="Estimated signal")
        ax[j, 0].set_title(f"Estimated signal for lambda={lmbda}")
        ax[j, 0].set_xlabel("Sample")
        ax[j, 0].set_ylabel("Magnitude")
        ax[j, 0].legend()

        # Plot the error.
        ax[j, 1].plot(error)
        ax[j, 1].set_title(f"Estimation error for lambda={lmbda}")
        ax[j, 1].set_xlabel("Iteration")
        ax[j, 1].set_ylabel("Error")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    apply_compressed_sensing_fft_pocs()
    apply_compressed_sensing_ifft_pocs_linear()
    apply_compressed_sensing_ifft_pocs_quadratic()


if __name__ == "__main__":
    app.run(main)
