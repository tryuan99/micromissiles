"""Explores non-uniform sampling."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app


def _generate_quadratic_if_samples(t_axis: np.ndarray, a: float) -> np.ndarray:
    """Generates the samples of a quadratic chirp's IF samples.

    Args:
        t_axis: Time axis.
        a: Quadratic coefficient.

    Returns:
        The samples of a quadratic chirp's IF along the given time axis.
    """
    return np.exp(1j * 2 * np.pi * a * t_axis**2)


def plot_non_uniform_sampling_quadratic() -> None:
    """Plots the quadratically uniform samples as non-uniform samples."""
    a = 560
    LENGTH = 8
    fs = 100  # Hz
    t = np.linspace(0, LENGTH / fs, 10000)
    x = _generate_quadratic_if_samples(t, a)
    n = np.arange(LENGTH) / fs
    samples = _generate_quadratic_if_samples(n, a)

    fig, ax = plt.subplots(1, 2, figsize=(8, 4), sharey=True)
    ax[0].plot(t, np.real(x))
    ax[0].stem(n, np.real(samples), "r")
    ax[0].set_xlabel("Time in s")
    ax[0].set_title("Uniform samples of a quadratic chirp's IF")

    t_non_uniform = np.linspace(0, (LENGTH / fs)**2, 10000)
    x_non_uniform = _generate_quadratic_if_samples(np.sqrt(t_non_uniform), a)
    ax[1].plot(t_non_uniform, np.real(x_non_uniform))
    ax[1].stem(n**2, np.real(samples), "r")
    ax[1].set_xlabel("Time in s")
    ax[1].set_title("Non-uniform samples of a sinusoid")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    plot_non_uniform_sampling_quadratic()


if __name__ == "__main__":
    app.run(main)
