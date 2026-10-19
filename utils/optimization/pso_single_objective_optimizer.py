"""The particle swarm optimization algorithm is a single-objective optimization
problem solver that uses a swarm of particles to guide its search.
"""

import pymoo.algorithms.soo.nonconvex.pso
import pymoo.optimize

from utils.optimization.problem import Problem, ProblemWrapper
from utils.optimization.single_objective_optimizer import \
    SingleObjectiveOptimizer


class PsoSingleObjectiveOptimizer(SingleObjectiveOptimizer):
    """Particle swarm optimization algorithm.

    Attributes:
        population_size: Population size.
        num_generations: Number of generations.
        inertia_weight: Inertia weight.
        cognitive_coefficient: Cognitive coefficient, i.e., the influence of
          each particle's personal best.
        social_coefficient: Social coefficient, i.e., the influence of the
          global best.
        max_velocity_rate: Maximum velocity relative to the design variable
          range.
        seed: Random seed.
    """

    def __init__(
        self,
        problem: Problem,
        population_size: int = 25,
        num_generations: int = 200,
        inertia_weight: float = 0.9,
        cognitive_coefficient: float = 2.0,
        social_coefficient: float = 2.0,
        max_velocity_rate: float = 0.2,
        seed: int = None,
    ) -> None:
        super().__init__(problem)
        self.population_size = population_size
        self.num_generations = num_generations
        self.inertia_weight = inertia_weight
        self.cognitive_coefficient = cognitive_coefficient
        self.social_coefficient = social_coefficient
        self.max_velocity_rate = max_velocity_rate
        self.seed = seed

    def run(self, *args, **kwargs) -> None:
        """Solves the optimization problem.

        Args:
            args: Additional arguments.
            kwargs: Additional keyword arguments.
        """
        algorithm = pymoo.algorithms.soo.nonconvex.pso.PSO(
            pop_size=self.population_size,
            w=self.inertia_weight,
            c1=self.cognitive_coefficient,
            c2=self.social_coefficient,
            max_velocity_rate=self.max_velocity_rate,
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
        self.optimal_value = result.X
        self.objective_value = result.F
