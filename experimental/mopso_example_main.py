import jmetal.algorithm.multiobjective
import jmetal.operator
import jmetal.problem
import jmetal.util
import jmetal.util.solution
import matplotlib.pyplot as plt
import numpy as np
from absl import app, logging

import utils.visualization.mpl_config


def main(argv):
    assert len(argv) == 1, argv

    # Define the problem.
    problem = jmetal.problem.ZDT1()

    # Use the optimized multi-objective particle swarm optimization algorithm.
    swarm_size = 100
    mutation_probability = 1 / problem.number_of_variables()
    max_num_evaluations = 25000
    algorithm = jmetal.algorithm.multiobjective.omopso.OMOPSO(
        problem=problem,
        swarm_size=swarm_size,
        epsilon=0.005,
        uniform_mutation=jmetal.operator.mutation.UniformMutation(
            probability=mutation_probability,
            perturbation=0.5,
        ),
        non_uniform_mutation=jmetal.operator.mutation.NonUniformMutation(
            mutation_probability,
            perturbation=0.5,
            max_iterations=max_num_evaluations // swarm_size,
        ),
        leaders=jmetal.util.archive.CrowdingDistanceArchive(100),
        termination_criterion=jmetal.util.termination_criterion.
        StoppingByEvaluations(max_evaluations=max_num_evaluations),
    )

    # Solve the problem.
    algorithm.run()
    result = algorithm.get_result()
    solutions = jmetal.util.solution.get_non_dominated_solutions(result)

    # Get the objective values.
    objective_values = np.array([solution.objectives for solution in solutions])

    # Get the variable values.
    variable_values = np.array([solution.variables for solution in solutions])

    # Plot the Pareto front.
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(
        objective_values[:, 0],
        objective_values[:, 1],
    )
    ax.set_xlabel(r"$f_1$")
    ax.set_ylabel(r"$f_2$")
    plt.show()

    # Print the variable values.
    logging.info(variable_values)


if __name__ == "__main__":
    app.run(main)
