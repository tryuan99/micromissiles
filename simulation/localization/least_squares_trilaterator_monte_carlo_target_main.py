"""Runs a Monte Carlo simulation on the target distance for the least squares
trilaterator.
"""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags, logging

from simulation.localization.least_squares_trilaterator import \
    LeastSquaresTrilaterator
from utils.coordinates import CartesianCoordinates

FLAGS = flags.FLAGS


def _generate_sensor_positions(
    num_measurements: int,
    radius: float,
) -> list[CartesianCoordinates]:
    """Generates equally spaced sensors at a specified radius from the origin
    in the x-y plane.

    Args:
        num_measurements: Number of measurements.
        radius: Radius from the origin.

    Returns:
        A list of the sensor positions.
    """
    return [
        CartesianCoordinates(
            x=radius * np.cos(2 * np.pi * i / num_measurements),
            y=radius * np.sin(2 * np.pi * i / num_measurements),
            z=0,
        ) for i in range(num_measurements)
    ]


def simulate_monte_carlo(
    num_trials: int,
    radius: float,
    distance: float,
    standard_deviation: float,
) -> None:
    """Performs a Monte Carlo simulation on the target distance for the least
    squares trilaterator.

    Args:
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        distance: Distance to the target.
        standard_deviation: Standard deviation of the target distance noise.
    """
    sensor_positions = _generate_sensor_positions(
        num_measurements=4,
        radius=radius,
    )
    sensor_coordinates = np.array(
        [position.coordinates() for position in sensor_positions])
    target_position = np.array([0, 0, distance])
    results = np.zeros((num_trials, 3))
    for i in range(num_trials):
        ranges = (np.linalg.norm(
            target_position - sensor_coordinates,
            axis=1,
        ))
        ranges += np.random.normal(scale=standard_deviation, size=ranges.shape)
        trilaterator = LeastSquaresTrilaterator(sensor_positions, ranges)
        results[i] = trilaterator.trilaterate()
    result_standard_deviations = np.std(results, axis=0)
    logging.info("Standard deviation for [x, y, z]: %s",
                 result_standard_deviations)
    logging.info("Lateral standard deviation: %f",
                 np.linalg.norm(result_standard_deviations[:2]))
    logging.info("Overall standard deviation: %f",
                 np.linalg.norm(result_standard_deviations))


def simulate_monte_carlo_over_distance(
    num_trials: int,
    radius: float,
    min_distance: float,
    max_distance: float,
    standard_deviation: float,
) -> None:
    """Performs a Monte Carlo simulation on the target distance while sweeping
    the distance to the target for the least squares trilaterator.

    Args:
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        min_distance: Minimum target distance.
        max_distance: Maximum target distance.
        standard_deviation: Standard deviation of the target distance noise.
    """
    sensor_positions = _generate_sensor_positions(
        num_measurements=4,
        radius=radius,
    )
    sensor_coordinates = np.array(
        [position.coordinates() for position in sensor_positions])
    target_distances = np.arange(min_distance, max_distance + 10, 10)
    target_standard_deviations = np.zeros((len(target_distances), 3))
    for target_distance_index, target_distance in enumerate(target_distances):
        target_position = np.array([0, 0, target_distance])
        results = np.zeros((num_trials, 3))
        for i in range(num_trials):
            ranges = (np.linalg.norm(
                target_position - sensor_coordinates,
                axis=1,
            ))
            ranges += np.random.normal(
                scale=standard_deviation,
                size=ranges.shape,
            )
            trilaterator = LeastSquaresTrilaterator(sensor_positions, ranges)
            results[i] = trilaterator.trilaterate()
        target_standard_deviations[target_distance_index] = np.std(
            results,
            axis=0,
        )

    # Plot the x, y, and z standard deviations, the lateral standard deviation,
    # and the overall standard deviation over the target distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        target_distances,
        target_standard_deviations[:, 0],
        label=r"Standard deviation in $x$",
    )
    ax.plot(
        target_distances,
        target_standard_deviations[:, 1],
        label=r"Standard deviation in $y$",
    )
    ax.plot(
        target_distances,
        target_standard_deviations[:, 2],
        label=r"Standard deviation in $z$",
    )
    ax.plot(
        target_distances,
        np.linalg.norm(target_standard_deviations[:, :2], axis=1),
        label="Lateral standard deviation",
    )
    ax.plot(
        target_distances,
        np.linalg.norm(target_standard_deviations, axis=1),
        label="Overall standard deviation",
    )
    ax.set_xlabel("Target distance [m]")
    ax.set_ylabel("Standard deviation [m]")
    ax.legend()
    plt.show()


def simulate_monte_carlo_over_num_measurements(
    num_trials: int,
    radius: float,
    distance: float,
    standard_deviation: float,
    max_num_measurements: int,
) -> None:
    """Performs a Monte Carlo simulation on the target distance while sweeping
    the number of measurements for the least squares trilaterator.

    Args:
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        distance: Distance to the target.
        standard_deviation: Standard deviation of the target distance noise.
        max_num_measurements: Maximum number of measurements.
    """
    num_measurements = range(4, max_num_measurements + 1)
    target_standard_deviations = np.zeros((len(num_measurements), 3))
    for num_measurement_index, num_measurement in enumerate(num_measurements):
        sensor_positions = _generate_sensor_positions(
            num_measurement,
            radius=radius,
        )
        sensor_coordinates = np.array(
            [position.coordinates() for position in sensor_positions])
        target_position = np.array([0, 0, distance])
        results = np.zeros((num_trials, 3))
        for i in range(num_trials):
            ranges = (np.linalg.norm(
                target_position - sensor_coordinates,
                axis=1,
            ))
            ranges += np.random.normal(
                scale=standard_deviation,
                size=ranges.shape,
            )
            trilaterator = LeastSquaresTrilaterator(sensor_positions, ranges)
            results[i] = trilaterator.trilaterate()
        target_standard_deviations[num_measurement_index] = np.std(
            results,
            axis=0,
        )

    # Plot the x, y, and z standard deviations, the lateral standard deviation,
    # and the overall standard deviation over the number of measurements.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        num_measurements,
        target_standard_deviations[:, 0],
        label=r"Standard deviation in $x$",
    )
    ax.plot(
        num_measurements,
        target_standard_deviations[:, 1],
        label=r"Standard deviation in $y$",
    )
    ax.plot(
        num_measurements,
        target_standard_deviations[:, 2],
        label=r"Standard deviation in $z$",
    )
    ax.plot(
        num_measurements,
        np.linalg.norm(target_standard_deviations[:, :2], axis=1),
        label="Lateral standard deviation",
    )
    ax.plot(
        num_measurements,
        np.linalg.norm(target_standard_deviations, axis=1),
        label="Overall standard deviation",
    )
    ax.set_xlabel("Number of measurements")
    ax.set_ylabel("Standard deviation [m]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    simulate_monte_carlo(
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.distance,
        FLAGS.standard_deviation,
    )
    simulate_monte_carlo_over_distance(
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.min_distance,
        FLAGS.max_distance,
        FLAGS.standard_deviation,
    )
    simulate_monte_carlo_over_num_measurements(
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.distance,
        FLAGS.standard_deviation,
        FLAGS.max_num_measurements,
    )


if __name__ == "__main__":
    flags.DEFINE_integer("num_trials",
                         100000,
                         "Number of trials.",
                         lower_bound=0)
    flags.DEFINE_float("radius",
                       50,
                       "Sensor radius from the origin.",
                       lower_bound=0.0)
    flags.DEFINE_float("standard_deviation",
                       1,
                       "Standard deviation of the noise.",
                       lower_bound=0.0)
    flags.DEFINE_float("distance",
                       1000,
                       "Distance to the target",
                       lower_bound=0.0)
    flags.DEFINE_float("min_distance",
                       10,
                       "Minimum distance to the target.",
                       lower_bound=0.0)
    flags.DEFINE_float("max_distance",
                       2000,
                       "Maximum distance to the target.",
                       lower_bound=0.0)
    flags.DEFINE_integer("max_num_measurements",
                         20,
                         "Maximum number of measurements.",
                         lower_bound=4)

    app.run(main)
