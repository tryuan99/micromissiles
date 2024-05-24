"""The solver class is an interface for solving matrix-matrix or matrix-vector
equations.
"""

from abc import ABC, abstractmethod

import numpy as np


class Solver(ABC):
    """Interface for a matrix-matrix or matrix-vector solver."""

    def __init__(self, A: np.ndarray) -> None:
        self.A = A
        self._solve()

    @property
    @abstractmethod
    def solution(self) -> np.ndarray:
        """Returns the solution."""

    @abstractmethod
    def _solve(self) -> None:
        """Solves the matrix-matrix or matrix-vector equation."""


class MatrixMatrixSolver(Solver):
    """Interface for a matrix-matrix solver."""

    def __init__(self, A: np.ndarray, Y: np.ndarray) -> None:
        self.Y = Y
        self.X: np.ndarray = None
        if A.shape[0] != Y.shape[0]:
            raise ValueError("Incompatible matrix dimensions.")
        super().__init__(A)

    @property
    def solution(self) -> np.ndarray:
        """Returns the solution."""
        return self.X

    def _solve(self) -> None:
        """Solves the matrix-matrix equation."""
        self.X = np.linalg.solve(self.A, self.Y)


class MatrixVectorSolver(Solver):
    """Interface for a matrix-vector solver."""

    def __init__(self, A: np.ndarray, b: np.ndarray) -> None:
        self.b = b
        self.x: np.ndarray = None
        if A.shape[0] != b.shape[0]:
            raise ValueError("Incompatible matrix and vector dimensions.")
        super().__init__(A)

    @property
    def solution(self) -> np.ndarray:
        """Returns the solution."""
        return self.x

    def _solve(self) -> None:
        """Solves the matrix-vector equation."""
        self.x = np.linalg.solve(self.A, self.b)
