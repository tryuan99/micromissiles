import matplotlib.pyplot as plt
import pymoo.algorithms.moo.nsga2
import pymoo.optimize
import pymoo.problems
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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(
        result.F[:, 0],
        result.F[:, 1],
    )
    pareto_front = problem.pareto_front()
    ax.plot(
        pareto_front[:, 0],
        pareto_front[:, 1],
        color="red",
    )
    ax.set_xlabel(r"$f_1$")
    ax.set_ylabel(r"$f_2$")
    plt.show()

    # Print the design space values.
    logging.info(result.X)


if __name__ == "__main__":
    app.run(main)
