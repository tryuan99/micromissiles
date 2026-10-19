"""The multi-objective particle swarm optimization with crowding distance is a
multi-objective optimization problem solver.
"""

import pymoo.algorithms.moo.mopso_cd
import pymoo.optimize

from utils.optimization.multi_objective_optimizer import MultiObjectiveOptimizer
from utils.optimization.problem import Problem, ProblemWrapper


class MopsoCdMultiObjectiveOptimizer(MultiObjectiveOptimizer):
    """Multi-objective particle swarm optimization with crowding distance.

    Attributes:
        population_size: Population size.
        num_generations: Number of generations to run.
        inertia_weight: Inertia weight.
        cognitive_coefficient: Cognitive coefficient, i.e., the influence of
          each particle's personal best.
        social_coefficient: Social coefficient, i.e., the influence of the
          global best.
        max_velocity_rate: Maximum velocity relative to the design variable
          range.
        archive_size: Maximum size of the external archive.
        seed: Random seed.
    """

    def __init__(
        self,
        problem: Problem,
        population_size: int = 100,
        num_generations: int = 200,
        inertia_weight: float = 0.6,
        cognitive_coefficient: float = 2.0,
        social_coefficient: float = 2.0,
        max_velocity_rate: float = 0.5,
        archive_size: int = 200,
        seed: int = None,
    ) -> None:
        super().__init__(problem)
        self.population_size = population_size
        self.num_generations = num_generations
        self.inertia_weight = inertia_weight
        self.cognitive_coefficient = cognitive_coefficient
        self.social_coefficient = social_coefficient
        self.max_velocity_rate = max_velocity_rate
        self.archive_size = archive_size
        self.seed = seed

    def run(self, *args, **kwargs) -> None:
        """Solves the optimization problem.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        algorithm = pymoo.algorithms.moo.mopso_cd.MOPSO_CD(
            pop_size=self.population_size,
            w=self.inertia_weight,
            c1=self.cognitive_coefficient,
            c2=self.social_coefficient,
            max_velocity_rate=self.max_velocity_rate,
            archive_size=self.archive_size,
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
