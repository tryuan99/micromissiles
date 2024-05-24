"""The least squares solver uses least squares to solve the matrix-matrix or
matrix-vector equation.
"""

import numpy as np

from utils.solver.solver import MatrixMatrixSolver, MatrixVectorSolver


class LeastSquaresMatrixMatrixSolver(MatrixMatrixSolver):
    """Least squares matrix-matrix solver."""

    def __init__(self,
                 A: np.ndarray,
                 Y: np.ndarray,
                 w: np.ndarray = None) -> None:
        if w is not None:
            self.w = w
        else:
            self.w = np.ones(A.shape[0])
        super().__init__(A, Y)

    def _solve(self) -> None:
        """Solves the matrix-matrix equation."""
        w = np.sqrt(self.w)
        A_weighted = self.A * w[:, np.newaxis]
        Y_weighted = np.diag(w) @ self.Y
        result = np.linalg.lstsq(A_weighted, Y_weighted, rcond=None)[0]
        self.X = result


class LeastSquaresMatrixVectorSolver(MatrixVectorSolver):
    """Least squares matrix-vector solver."""

    def __init__(self,
                 A: np.ndarray,
                 b: np.ndarray,
                 w: np.ndarray = None) -> None:
        if w is not None:
            self.w = w
        else:
            self.w = np.ones(A.shape[0])
        super().__init__(A, b)

    def _solve(self) -> None:
        """Solves the matrix-vector equation."""
        w = np.sqrt(self.w)
        A_weighted = self.A * w[:, np.newaxis]
        b_weighted = self.b * w
        result = np.linalg.lstsq(A_weighted, b_weighted, rcond=None)[0]
        self.x = result


class TotalLeastSquaresMatrixVectorSolver(MatrixVectorSolver):
    """Total least squares matrix-vector solver.

    See "Matrix Computations" by Gene H. Golub and Charles F. Van Loan.
    There may not be a unique solution or a solution at all.
    """

    def __init__(self, A: np.ndarray, b: np.ndarray) -> None:
        super().__init__(A, b)

    def _solve(self) -> None:
        """Solves the matrix-vector equation."""
        augmented_matrix = np.hstack((self.A, self.b[:, np.newaxis]))
        _, _, Vt = np.linalg.svd(augmented_matrix)
        v12 = Vt[-1, :-1]
        v22 = Vt[-1, -1]
        result = -v12 / v22
        self.x = result
