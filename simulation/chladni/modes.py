"""The modes class finds the natural frequencies and vibration shapes."""

import numpy as np


class Modes:
    """Natural frequencies and vibration shapes (modes) of the plate.

    Attributes:
        angular_frequencies: Natural frequencies in rad/s in ascending order,
            zero for modes where the whole plate moves without bending.
        modes: One mode per column, as coefficients of the basis.
        num_rigid_modes: Number of rigid modes.
    """

    # Minimum eigenvalue threshold factor.
    MIN_EIGENVALUE_THRESHOLD_FACTOR = 1e-12

    # Minimum frequency threshold factor.
    MIN_FREQUENCY_THRESHOLD_FACTOR = 1e-10

    def __init__(self, stiffness: np.ndarray, mass: np.ndarray) -> None:
        # Find the modes from the stiffness and mass matrices and solve the
        # generalized symmetric eigenvalue problem K * v = omega^2 * M * v,
        # where K is the stiffness matrix and M is the mass matrix.
        mass_eigenvalues, mass_eigenvectors = np.linalg.eigh(mass)
        # Discard very small modes.
        thresholded_eigenvalues = (mass_eigenvalues
                                   > self.MIN_EIGENVALUE_THRESHOLD_FACTOR *
                                   mass_eigenvalues.max())
        # R = V * Lambda^(-1/2) is the change of coordinates to the generalized
        # eigenbasis, such that R^T * M * R = I.
        R = (mass_eigenvectors[:, thresholded_eigenvalues] /
             np.sqrt(mass_eigenvalues[thresholded_eigenvalues]))
        # Transform K to Khat = R^T * K * R.
        reduced_stiffness = R.T @ stiffness @ R
        # Solve Khat * v = omega^2 * v in the generalized eigenbasis.
        squared_frequencies, eigenvectors = np.linalg.eigh(
            0.5 * (reduced_stiffness + reduced_stiffness.T))
        # Transform the eigenvectors representing the mode shapes back to the
        # original coordinates.
        self.modes = R @ eigenvectors
        # Threshold the rigid modes.
        rigid_frequencies = (np.abs(squared_frequencies)
                             < self.MIN_FREQUENCY_THRESHOLD_FACTOR *
                             squared_frequencies.max())
        squared_frequencies[rigid_frequencies] = 0
        self.angular_frequencies = np.sqrt(squared_frequencies)
        self.num_rigid_modes = int(rigid_frequencies.sum())

    @property
    def frequencies(self) -> np.ndarray:
        """Returns the natural frequencies in Hz."""
        return self.angular_frequencies / (2 * np.pi)
