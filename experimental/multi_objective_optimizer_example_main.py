import matplotlib.pyplot as plt
import pymoo.algorithms.moo.nsga2
import pymoo.optimize
import pymoo.problems
import pymoo.visualization.scatter
import scienceplots
from absl import app, logging


def main(argv):
    assert len(argv) == 1, argv

    # Define the problem.
    problem = pymoo.problems.get_problem("zdt1")

    # Use the non-dominated sorting genetic algorithm.
    algorithm = pymoo.algorithms.moo.nsga2.NSGA2(pop_size=100)

    # Solve the problem.
    result = pymoo.optimize.minimize(
        problem,
        algorithm,
        termination=("n_gen", 200),
        seed=1,
        verbose=True,
    )

    # Plot the Pareto front.
    plt.style.use(["science", "grid"])
    plot = pymoo.visualization.scatter.Scatter(
        figsize=(12, 6),
        labels=[r"$f_1$", r"$f_2$"],
    )
    plot.add(
        problem.pareto_front(),
        plot_type="line",
        color="black",
        alpha=0.7,
    )
    plot.add(
        result.F,
        color="red",
    )
    plot.show()

    # Print the design space values.
    logging.info(result.X)


if __name__ == "__main__":
    app.run(main)
