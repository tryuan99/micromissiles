"""The multiple objective optimizer class is an interface for an optimization
algorithm to find the Pareto front for a problem with two or three objectives.
"""

from abc import ABC, abstractmethod

import numpy as np

from utils.optimization.problem import Problem


class MultiObjectiveOptimizer(ABC):
    """Interface for a multi-objective optimizer.

    Attributes:
        problem: Optimization problem.
        optimal_values: Design space values.
        objective_values: Objective values.
    """

    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.optimal_values: np.ndarray = None
        self.objective_values: np.ndarray = None

    @abstractmethod
    def run(self) -> None:
        """Solves the optimization problem."""
