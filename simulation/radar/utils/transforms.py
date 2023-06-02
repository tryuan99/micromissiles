"""Collection of various transforms."""

import numpy as np


def czt(x: np.ndarray, M: int, A: np.complex128,
        W: np.complex128) -> np.ndarray:
    """Performs the chirp z-transform.

    https://en.wikipedia.org/wiki/Chirp_Z-transform
    https://krex.k-state.edu/dspace/bitstream/handle/2097/7844/LD2668R41972S43.pdf

    Args:
        x: Input samples.
        M: Number of output samples.
        A: Complex starting point.
        W: Complex ratio between points.

    Returns:
        Output samples after the chirp z-transform.
    """
    # z_k = A * W^(-k), k = 0, 1, ..., M-1.
    z_k = A * W**(-np.arange(M))
    return z(x, z_k)


def dft(x: np.ndarray, M: int = -1) -> np.ndarray:
    """Performs the discrete Fourier transform.

    Args:
        x: Input samples.
        M: Number of output samples.

    Returns:
        Output samples after the discrete Fourier transform.
    """
    if M == -1:
        M = len(x)
    # W_M is the Mth root of unity.
    W_M = np.exp(-1j * 2 * np.pi / M)
    return czt(x, M, 1, W_M)


def z(x: np.ndarray, z_k: np.ndarray) -> np.ndarray:
    """Performs the z-transform.

    Args:
        x: Input samples.
        z: Complex values for which to calculate the z-transform.

    Returns:
        Output samples after the z-transform.
    """
    z_k_matrix = z_k[:, np.newaxis]**(-np.arange(len(x)))
    return z_k_matrix @ x
