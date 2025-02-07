import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from utils.optimization.nsga2_multi_objective_optimizer import \
    Nsga2MultiObjectiveOptimizer
from utils.optimization.problem import Problem

FLAGS = flags.FLAGS


class Zdt1Problem(Problem):
    """ZDT1 problem.

    See https://pymoo.org/problems/multi/zdt.html#ZDT1 for more details.
    """

    def num_variables(self) -> int:
        """Returns the number of design variables."""
        return 30

    def num_objectives(self) -> int:
        """Returns the number of objectives."""
        return 2

    def evaluate_objectives(
            self, x: float | np.ndarray) -> float | list[float] | np.ndarray:
        """Evaluates the objective(s) on the given design variable values.

        Args:
            x: Design variable values.

        Returns:
            The objective(s) evaluated on the given design variable values.
        """
        f = x[0]
        g = 1 + 9 / len(x) * np.sum(x[1:])
        h = 1 - np.sqrt(f / g)
        return [f, h]

    def lower_bound(self) -> float | np.ndarray:
        """Returns the lower bound on the design variables."""
        return 0

    def upper_bound(self) -> float | np.ndarray:
        """Returns the upper bound on the design variables."""
        return 1


def main(argv):
    assert len(argv) == 1, argv

    problem = Zdt1Problem()
    optimizer = Nsga2MultiObjectiveOptimizer(
        problem,
        FLAGS.population_size,
        FLAGS.num_generations,
        FLAGS.seed,
    )
    optimizer.run()

    # Plot the Pareto front.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(
        optimizer.objective_values[:, 0],
        optimizer.objective_values[:, 1],
    )
    ax.set_xlabel(r"$f_1$")
    ax.set_ylabel(r"$f_2$")
    plt.show()


if __name__ == "__main__":
    flags.DEFINE_integer("population_size",
                         100,
                         "Population size.",
                         lower_bound=1)
    flags.DEFINE_integer("num_generations",
                         200,
                         "Number of generations.",
                         lower_bound=1)
    flags.DEFINE_float("seed", None, "Random seed.")

    app.run(main)
