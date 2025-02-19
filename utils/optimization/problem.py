"""The problem class is an interface for a single-objective or multi-objective optimization problem."""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pymoo.core.problem


class Problem(ABC):
    """Optimization problem."""

    @abstractmethod
    def num_variables(self) -> int:
        """Returns the number of design variables."""

    @abstractmethod
    def num_objectives(self) -> int:
        """Returns the number of objectives."""

    def num_inequality_constraints(self) -> int:
        """Returns the number of inequality constraints."""
        return 0

    @abstractmethod
    def evaluate_objectives(
        self,
        x: float | np.ndarray,
    ) -> float | list[float] | np.ndarray:
        """Evaluates the objective(s) on the given design variable values.

        Args:
            x: Design variable values.

        Returns:
            The objective(s) evaluated on the given design variable values.
        """

    def evaluate_inequality_constraints(
        self,
        x: float | np.ndarray,
    ) -> float | list[float] | np.ndarray:
        """Evaluates the inequality constraint(s) on the given design variable
        values.

        Args:
            x: Design variable values.

        Returns:
            The inequality constraint(s) evaluated on the given design variable
            values.
        """
        return []

    @abstractmethod
    def lower_bound(self) -> float | np.ndarray:
        """Returns the lower bound on the design variables."""

    @abstractmethod
    def upper_bound(self) -> float | np.ndarray:
        """Returns the upper bound on the design variables."""


class ProblemWrapper(pymoo.core.problem.ElementwiseProblem):
    """Wrapper around an optimization problem for pymoo.

    Attributes:
        problem: Optimization problem.
    """

    def __init__(self, problem: Problem) -> None:
        super().__init__(
            n_var=problem.num_variables(),
            n_obj=problem.num_objectives(),
            n_ieq_constr=problem.num_inequality_constraints(),
            xl=problem.lower_bound(),
            xu=problem.upper_bound(),
        )
        self.problem = problem

    def _evaluate(self, x: float | np.ndarray, out: dict[str, Any]) -> None:
        # Evaluate the objectives.
        out["F"] = self.problem.evaluate_objectives(x)

        # Evaluate the inequality constraints.
        out["G"] = self.problem.evaluate_inequality_constraints(x)
