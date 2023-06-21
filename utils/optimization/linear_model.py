"""The linear model library contains various linear models."""

from abc import ABC, abstractmethod

import cvxpy as cp
import numpy as np
from sklearn import linear_model


class LinearModel(ABC):
    """Interface for a linear model.

    The linear model tries to solve Xw = y.
    X has dimensions (number of samples) x (number of features).
    """

    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = X
        self.y = y

    @abstractmethod
    def solve(self) -> None:
        """Solves the linear model."""

    @abstractmethod
    def get_coefficients(self) -> np.ndarray:
        """Returns the coefficients of the best linear fit."""


class LinearRegression(LinearModel):
    """Linear regression minimzing the residual sum of squares.

    The optimization objective is ||y - Xw||_2^2.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray):
        super().__init__(X, y)
        self.model = linear_model.LinearRegression(fit_intercept=False)

    def solve(self) -> None:
        """Solves the linear model with L1 regularization (LASSO)."""
        self.model.fit(self.X, self.y)

    def get_coefficients(self) -> np.ndarray:
        """Returns the coefficients of the best linear fit."""
        return self.model.coef_


class LassoModel(LinearModel):
    """Linear model with L1 regularization (LASSO).

    The optimization objective is:
    (1 / (2 * num_samples)) * ||y - Xw||_2^2 + alpha * ||w||_1.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray, alpha: float):
        super().__init__(X, y)
        self.model = linear_model.Lasso(alpha=alpha, fit_intercept=False)

    def solve(self) -> None:
        """Solves the linear model with L1 regularization (LASSO)."""
        self.model.fit(self.X, self.y)

    def get_coefficients(self) -> np.ndarray:
        """Returns the coefficients of the best linear fit."""
        return self.model.coef_


class ComplexLassoModel(LinearModel):
    """Linear model with L1 regularization (LASSO) that supports complex values.

    The optimization objective is:
    (1 / (2 * num_samples)) * ||y - Xw||_2^2 + alpha * ||w||_1.

    To support complex values, we split all matrices and vectors into real and
    imaginary components and formulate the problem as a second-order cone problem.
    See https://stats.stackexchange.com/a/469660 for more details.
    """

    def __init__(self, X: np.ndarray, y: np.ndarray, alpha: float):
        super().__init__(X, y)
        # Number of features.
        self.n = self.X.shape[-1]
        # X is a block matrix of dimensions (2 * number of samples) x (2 *
        # number of features).
        self.X = np.block([
            [np.real(self.X), -np.imag(self.X)],
            [np.imag(self.X), np.real(self.X)],
        ])
        # y has dimensions (2 * number of samples) x 1.
        self.y = np.block([np.real(self.y), np.imag(self.y)])

        # The imaginary component is stacked below the real component, so w has
        # dimensions (2 * number of features) x 1.
        self.w = cp.Variable(2 * self.n)
        # There is one slack variable for each feature.
        self.t = cp.Variable(self.n)
        constraints = [
            # |w_k| = sqrt(wr_k^2 + wi_k^2) = ||[wr_k \\ wi_k]||_2 <= t_k.
            cp.SOC(self.t[k], cp.vstack((self.w[k], self.w[k + self.n])))
            for k in range(self.n)
        ]
        self.problem = cp.Problem(
            cp.Minimize(1 / (2 * self.n) *
                        cp.sum_squares(self.y - self.X @ self.w) +
                        alpha * cp.sum(self.t)), constraints)

    def solve(self) -> None:
        """Solves the linear model with L1 regularization (LASSO)."""
        self.problem.solve()

    def get_coefficients(self) -> np.ndarray:
        """Returns the coefficients of the best linear fit."""
        return self.w.value[:self.n] + 1j * self.w.value[self.n:]
