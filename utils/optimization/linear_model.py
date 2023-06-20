"""The linear model library contains various linear models."""

from abc import ABC, abstractmethod

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
