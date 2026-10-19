import numpy as np
from absl import app, flags, logging

from utils.optimization.problem import Problem
from utils.optimization.pso_single_objective_optimizer import \
    PsoSingleObjectiveOptimizer

FLAGS = flags.FLAGS


class RastriginProblem(Problem):
    """Rastrigin problem.

    See https://pymoo.org/problems/single/rastrigin.html for more details.
    """

    def num_variables(self) -> int:
        """Returns the number of design variables."""
        return 2

    def num_objectives(self) -> int:
        """Returns the number of objectives."""
        return 1

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
        return (10 * self.num_variables() +
                np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))

    def lower_bound(self) -> float | np.ndarray:
        """Returns the lower bound on the design variables."""
        return -5.12

    def upper_bound(self) -> float | np.ndarray:
        """Returns the upper bound on the design variables."""
        return 5.12


def main(argv):
    assert len(argv) == 1, argv

    problem = RastriginProblem()
    optimizer = PsoSingleObjectiveOptimizer(
        problem,
        FLAGS.population_size,
        FLAGS.num_generations,
        FLAGS.inertia_weight,
        FLAGS.cognitive_coefficient,
        FLAGS.social_coefficient,
        FLAGS.max_velocity_rate,
        FLAGS.seed,
    )
    optimizer.run()

    # Log the optimal values and objective values.
    logging.info("Optimal value: %s", optimizer.optimal_value)
    logging.info("Objective value: %s", optimizer.objective_value)


if __name__ == "__main__":
    flags.DEFINE_integer("population_size",
                         25,
                         "Population size.",
                         lower_bound=1)
    flags.DEFINE_integer("num_generations",
                         200,
                         "Number of generations.",
                         lower_bound=1)
    flags.DEFINE_float("inertia_weight", 0.9, "Inertia weight.")
    flags.DEFINE_float("cognitive_coefficient",
                       2.0,
                       "Cognitive coefficient (personal best influence).",
                       lower_bound=0)
    flags.DEFINE_float("social_coefficient",
                       2.0,
                       "Social coefficient (global best influence).",
                       lower_bound=0)
    flags.DEFINE_float(
        "max_velocity_rate",
        0.2,
        "Maximum velocity relative to the design variable range.",
        lower_bound=0)
    flags.DEFINE_integer("seed", None, "Random seed.")

    app.run(main)
