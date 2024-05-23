"""The regression class is an interface for all regressions."""

from abc import ABC, abstractmethod

import numpy as np


class Regression(ABC):
    """Interface for a regression."""

    def __init__(self, x: np.ndarray, y: np.ndarray):
        self.x = np.copy(x)
        self.y = np.copy(y)
        self._perform_regression()

    @property
    def r_squared(self) -> float:
        """Coefficient of determination.

        R squared determines the proportion of variance in the dependent
        variable that can be explained by the variance in the independent
        variable.
        """
        sum_squared_residuals = np.linalg.norm(self.y -
                                               self.evaluate(self.x))**2
        total_sum_squares = np.linalg.norm(self.y - np.mean(self.y))**2
        return 1 - sum_squared_residuals / total_sum_squares

    @abstractmethod
    def evaluate(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the regression at the given x-values.

        Args:
            x: x-values.

        Returns:
            The y-values corresponding to the x-values.
        """

    @abstractmethod
    def _perform_regression(self) -> None:
        """Performs the regression.

        This function should set the regression coefficients.
        """
