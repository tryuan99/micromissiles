"""The single objective optimizer class is an interface for an optimization
algorithm to find the optimal value for a single objective.
"""

from abc import ABC, abstractmethod

import numpy as np

from utils.optimization.problem import Problem


class SingleObjectiveOptimizer(ABC):
    """Interface for a single-objective optimizer.

    Attributes:
        problem: Optimization problem.
        optimal_value: Design space value.
        objective_value: Objective value.
    """

    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.optimal_value: np.ndarray = None
        self.objective_value: np.ndarray = None

    @abstractmethod
    def run(self) -> None:
        """Solves the optimization problem."""
