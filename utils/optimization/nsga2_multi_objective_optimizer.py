"""The non-dominated sorting genetic algorithm is a multi-objective
optimization problem solver.
"""

import pymoo.algorithms.moo.nsga2
import pymoo.optimize

from utils.optimization.multi_objective_optimizer import \
    MultiObjectiveOptimizer
from utils.optimization.problem import Problem, ProblemWrapper


class Nsga2MultiObjectiveOptimizer(MultiObjectiveOptimizer):
    """Non-dominated sorting genetic algorithm.

    Attributes:
        population_size: Population size.
        num_generations: Number of generations to run.
        seed: Random seed.
    """

    def __init__(self,
                 problem: Problem,
                 population_size: int = 100,
                 num_generations: int = 200,
                 seed: float = None) -> None:
        super().__init__(problem)
        self.population_size = population_size
        self.num_generations = num_generations
        self.seed = seed

    def run(self, *args, **kwargs) -> None:
        """Solves the optimization problem.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        algorithm = pymoo.algorithms.moo.nsga2.NSGA2(
            pop_size=self.population_size,
            *args,
            **kwargs,
        )
        result = pymoo.optimize.minimize(
            ProblemWrapper(self.problem),
            algorithm,
            termination=("n_gen", self.num_generations),
            seed=self.seed,
            verbose=True,
        )
        self.optimal_values = result.X
        self.objective_values = result.F
