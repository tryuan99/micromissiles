"""Optimizes the antenna array within a maximum antenna array aperture."""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
import pymoo.operators.sampling.lhs
import scienceplots
from absl import app, flags, logging

from simulation.antenna.antenna_array_optimization import \
    AntennaArray1DApertureOptimizationProblem
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils.optimization.nsga2_multi_objective_optimizer import \
    Nsga2MultiObjectiveOptimizer

FLAGS = flags.FLAGS


def optimize_antenna_array_within_aperture(
    antenna_array_config: AntennaArrayConfig,
    max_azimuth: float,
    x_min: float,
    x_max: float,
    z_min: float,
    z_max: float,
    population_size: int,
    num_generations: int,
    seed: float = None,
) -> None:
    """Optimizes the antenna array within the given aperture.

    Args:
        antenna_array_config: Antenna array configuration.
        max_azimuth: Maximum azimuth in radians for the objectives.
        x_min: Minimum x-coordinate in lambda.
        x_max: Maximum x-coordinate in lambda.
        z_min: Minimum z-coordinate in lambda.
        z_max: Maximum z-coordinate in lambda.
        population_size: Population size.
        num_generations: Number of generations.
        seed: Random seed.
    """
    problem = AntennaArray1DApertureOptimizationProblem(
        antenna_array_config,
        max_azimuth,
        x_min,
        x_max,
        z_min,
        z_max,
    )
    optimizer = Nsga2MultiObjectiveOptimizer(
        problem,
        population_size,
        num_generations,
        seed,
    )
    optimizer.run(sampling=pymoo.operators.sampling.lhs.LHS())

    # Log the optimal values and objective values.
    logging.info("Optimal values: %s", optimizer.optimal_values)
    logging.info("Objective values: %s", optimizer.objective_values)

    # Plot the Pareto front.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(
        optimizer.objective_values[:, 0],
        -optimizer.objective_values[:, 1],
    )
    ax.set_xlabel("Main lobe width [rad]")
    ax.set_ylabel("Sidelobe level [dB]")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configuration.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())

    optimize_antenna_array_within_aperture(
        antenna_array_config,
        FLAGS.max_azimuth,
        FLAGS.x_min,
        FLAGS.x_max,
        FLAGS.z_min,
        FLAGS.z_max,
        FLAGS.population_size,
        FLAGS.num_generations,
        FLAGS.seed,
    )


if __name__ == "__main__":
    flags.DEFINE_string(
        "config",
        "simulation/antenna/configs/ula_4_patch_antenna_24ghz.pbtxt",
        "Antenna array configuration.",
    )
    flags.DEFINE_float(
        "max_azimuth",
        np.pi / 3,
        "Maximum azimuth in radians for the objectives.",
        lower_bound=0.0,
    )
    flags.DEFINE_float("x_min", -5, "Minimum x-coordinate in lambda.")
    flags.DEFINE_float("x_max", 5, "Maximum x-coordinate in lambda.")
    flags.DEFINE_float("z_min", -10, "Minimum z-coordinate in lambda.")
    flags.DEFINE_float("z_max", 0, "Maximum z-coordinate in lambda.")
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
