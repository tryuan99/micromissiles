"""Optimizes the antenna array, such that the antenna array elements lie along
a given line.
"""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
import pymoo.operators.sampling.lhs
import scienceplots
from absl import app, flags, logging

from simulation.antenna.antenna_array_optimization import (
    AntennaArray1DLineOptimizationProblem, Line)
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils.optimization.nsga2_multi_objective_optimizer import \
    Nsga2MultiObjectiveOptimizer

FLAGS = flags.FLAGS


class Parabola(Line):
    """Parabola.

    Attributes:
        scale: Scaling factor of the parabola.
    """

    def __init__(self, scale: float = 1) -> None:
        self.scale = scale

    def evaluate(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the y-coordinates corresponding to the given
        x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The y-coordinates corresponding to the given x-coordinates.
        """
        return -self.scale * x**2

    def evaluate_slope(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the slope at each of the given x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The slopes of the normal line at each of the given x-coordinates.
        """
        return -2 * self.scale * x


class HyperbolicCosine(Line):
    """Hyperbolic cosine.

    Attributes:
        scale: Scaling factor of the hyperbolic cosine.
    """

    def __init__(self, scale: float = 1) -> None:
        self.scale = scale

    def evaluate(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the y-coordinates corresponding to the given
        x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The y-coordinates corresponding to the given x-coordinates.
        """
        return -np.cosh(self.scale * x) + 1

    def evaluate_slope(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the slope at each of the given x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The slopes of the normal line at each of the given x-coordinates.
        """
        return -self.scale * np.sinh(self.scale * x)


def optimize_antenna_array_along_parabola(
    antenna_array_config: AntennaArrayConfig,
    max_azimuth: float,
    parabola: Line,
    x_min: float,
    x_max: float,
    population_size: int,
    num_generations: int,
    seed: float = None,
) -> None:
    """Optimizes the antenna array along the given parabola.

    Args:
        antenna_array_config: Antenna array configuration.
        max_azimuth: Maximum azimuth in radians for the objectives.
        parabola: Parabola along which the antenna array elements lie.
        x_min: Minimum x-coordinate in lambda.
        x_max: Maximum x-coordinate in lambda.
        population_size: Population size.
        num_generations: Number of generations.
        seed: Random seed.
    """
    problem = AntennaArray1DLineOptimizationProblem(
        antenna_array_config,
        max_azimuth,
        parabola,
        x_min,
        x_max,
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

    # Output the optimal values and objective values in a CSV format.
    sorted_order = np.argsort(optimizer.objective_values[:, 0])
    for values_index in sorted_order:
        logging.info(
            "%s,%s",
            ",".join([
                str(objective_value)
                for objective_value in optimizer.objective_values[values_index]
            ]),
            ",".join([
                str(optimal_value)
                for optimal_value in optimizer.optimal_values[values_index]
            ]),
        )

    # Plot the Pareto front.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(
        optimizer.objective_values[:, 0],
        optimizer.objective_values[:, 1],
    )
    # Plot the -3 dB threshold.
    ax.axhline(-3, color="red", linestyle="--", label=r"$-3$ dB threshold")
    ax.set_xlabel("Main lobe width [rad]")
    ax.set_ylabel("Sidelobe level [dB]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configuration.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())

    optimize_antenna_array_along_parabola(
        antenna_array_config,
        FLAGS.max_azimuth,
        HyperbolicCosine(FLAGS.scale),
        FLAGS.x_min,
        FLAGS.x_max,
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
    flags.DEFINE_float("scale", 0.5, "Line scaling factor.")
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
