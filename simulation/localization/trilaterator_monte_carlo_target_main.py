"""Runs a Monte Carlo simulation on the target distance for a trilaterator."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags, logging

from simulation.localization.trilaterator_factory import (TrilateratorFactory,
                                                          TrilateratorType)
from utils.coordinates import CartesianCoordinates

FLAGS = flags.FLAGS


def _generate_sensor_positions(
    num_sensors: int,
    radius: float,
    z_offset: float,
) -> list[CartesianCoordinates]:
    """Generates equally spaced sensors at a specified radius from the origin
    in the x-y plane.

    Args:
        num_sensors: Number of sensors.
        radius: Radius from the origin.
        z_offset: z-offset.

    Returns:
        A list of the sensor positions.
    """
    return [
        CartesianCoordinates(
            x=radius * np.cos(2 * np.pi * i / num_sensors),
            y=radius * np.sin(2 * np.pi * i / num_sensors),
            z=-i / num_sensors * z_offset,
        ) for i in range(num_sensors)
    ]


def simulate_monte_carlo(
    trilaterator_type: TrilateratorType,
    num_trials: int,
    radius: float,
    z_offset: float,
    distance: float,
    standard_deviation: float,
) -> None:
    """Performs a Monte Carlo simulation on the target distance for the least
    squares trilaterator.

    Args:
        trilaterator_type: Trilaterator type.
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        z_offset: Sensor z-offset.
        distance: Distance to the target.
        standard_deviation: Standard deviation of the target distance noise.
    """
    num_sensors = 4
    sensor_positions = _generate_sensor_positions(num_sensors, radius, z_offset)
    sensor_coordinates = np.array(
        [position.coordinates() for position in sensor_positions])
    target_position = np.array([0, 0, distance])
    ranges = (np.linalg.norm(
        target_position - sensor_coordinates,
        axis=1,
    ))

    # Trilaterate the target position with range measurement noise.
    results = np.zeros((num_trials, 3))
    for i in range(num_trials):
        noise = np.random.normal(scale=standard_deviation, size=ranges.shape)
        trilaterator = TrilateratorFactory.create_trilaterator(
            trilaterator_type,
            sensor_positions,
            ranges + noise,
        )
        results[i] = trilaterator.trilaterate()
    result_standard_deviations = np.std(results, axis=0)

    # Calculate the Cramér-Rao lower bound.
    trilaterator = TrilateratorFactory.create_trilaterator(
        trilaterator_type,
        sensor_positions,
        ranges,
    )
    crlb = trilaterator.cramer_rao_lower_bound(
        target_position,
        np.ones(num_sensors) * standard_deviation)
    crlb_standard_deviations = np.sqrt(np.diag(crlb))

    logging.info("Standard deviation for [x, y, z]: %s",
                 result_standard_deviations)
    logging.info("CRLB standard deviation for [x, y, z]: %s",
                 crlb_standard_deviations)
    logging.info("Lateral standard deviation: %f",
                 np.linalg.norm(result_standard_deviations[:2]))
    logging.info("CRLB lateral standard deviation: %s",
                 np.linalg.norm(crlb_standard_deviations[:2]))
    logging.info("Total standard deviation: %f",
                 np.linalg.norm(result_standard_deviations))
    logging.info("CRLB total standard deviation: %s",
                 np.linalg.norm(crlb_standard_deviations))


def simulate_monte_carlo_over_distance(
    trilaterator_type: TrilateratorType,
    num_trials: int,
    radius: float,
    z_offset: float,
    min_distance: float,
    max_distance: float,
    standard_deviation: float,
) -> None:
    """Performs a Monte Carlo simulation on the target distance while sweeping
    the distance to the target for the least squares trilaterator.

    Args:
        trilaterator_type: Trilaterator type.
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        z_offset: Sensor z-offset.
        min_distance: Minimum target distance.
        max_distance: Maximum target distance.
        standard_deviation: Standard deviation of the target distance noise.
    """
    num_sensors = 4
    sensor_positions = _generate_sensor_positions(num_sensors, radius, z_offset)
    sensor_coordinates = np.array(
        [position.coordinates() for position in sensor_positions])
    target_distances = np.arange(min_distance, max_distance + 10, 10)
    target_standard_deviations = np.zeros((len(target_distances), 3))
    crlb_standard_deviations = np.zeros((len(target_distances), 3))
    for target_distance_index, target_distance in enumerate(target_distances):
        target_position = np.array([0, 0, target_distance])
        ranges = (np.linalg.norm(
            target_position - sensor_coordinates,
            axis=1,
        ))

        # Trilaterate the target position with range measurement noise.
        results = np.zeros((num_trials, 3))
        for i in range(num_trials):
            noise = np.random.normal(
                scale=standard_deviation,
                size=ranges.shape,
            )
            trilaterator = TrilateratorFactory.create_trilaterator(
                trilaterator_type,
                sensor_positions,
                ranges + noise,
            )
            results[i] = trilaterator.trilaterate()
        target_standard_deviations[target_distance_index] = np.std(
            results,
            axis=0,
        )

        # Calculate the Cramér-Rao lower bound.
        trilaterator = TrilateratorFactory.create_trilaterator(
            trilaterator_type,
            sensor_positions,
            ranges,
        )
        crlb = trilaterator.cramer_rao_lower_bound(
            target_position,
            np.ones(num_sensors) * standard_deviation)
        crlb_standard_deviations[target_distance_index] = np.sqrt(np.diag(crlb))

    # Plot the x, y, and z standard deviations, the lateral standard deviation,
    # and the overall standard deviation over the target distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        target_distances,
        target_standard_deviations[:, 0],
        color="C0",
        label=r"Standard deviation in $x$",
    )
    ax.plot(
        target_distances,
        crlb_standard_deviations[:, 0],
        color="C0",
        linestyle="--",
        label=r"CRLB standard deviation in $x$",
    )
    ax.plot(
        target_distances,
        target_standard_deviations[:, 1],
        color="C1",
        label=r"Standard deviation in $y$",
    )
    ax.plot(
        target_distances,
        crlb_standard_deviations[:, 1],
        color="C1",
        linestyle="--",
        label=r"CRLB standard deviation in $y$",
    )
    ax.plot(
        target_distances,
        target_standard_deviations[:, 2],
        color="C2",
        label=r"Standard deviation in $z$",
    )
    ax.plot(
        target_distances,
        crlb_standard_deviations[:, 2],
        color="C2",
        linestyle="--",
        label=r"CRLB standard deviation in $z$",
    )
    ax.plot(
        target_distances,
        np.linalg.norm(target_standard_deviations[:, :2], axis=1),
        color="C3",
        label="Lateral standard deviation",
    )
    ax.plot(
        target_distances,
        np.linalg.norm(crlb_standard_deviations[:, :2], axis=1),
        color="C3",
        linestyle="--",
        label=r"CRLB lateral standard deviation",
    )
    ax.plot(
        target_distances,
        np.linalg.norm(target_standard_deviations, axis=1),
        color="C4",
        label="Total standard deviation",
    )
    ax.plot(
        target_distances,
        np.linalg.norm(crlb_standard_deviations, axis=1),
        color="C4",
        linestyle="--",
        label=r"CRLB total standard deviation",
    )
    ax.set_xlabel("Target distance [m]")
    ax.set_ylabel("Standard deviation [m]")
    ax.legend()
    plt.show()


def simulate_monte_carlo_over_num_sensors(
    trilaterator_type: TrilateratorType,
    num_trials: int,
    radius: float,
    z_offset: float,
    distance: float,
    standard_deviation: float,
    max_num_sensors: int,
) -> None:
    """Performs a Monte Carlo simulation on the target distance while sweeping
    the number of sensors for the least squares trilaterator.

    Args:
        trilaterator_type: Trilaterator type.
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        z_offset: Sensor z-offset.
        distance: Distance to the target.
        standard_deviation: Standard deviation of the target distance noise.
        max_num_sensors: Maximum number of sensors.
    """
    num_sensors = range(4, max_num_sensors + 1)
    target_standard_deviations = np.zeros((len(num_sensors), 3))
    crlb_standard_deviations = np.zeros((len(num_sensors), 3))
    for num_sensor_index, num_sensor in enumerate(num_sensors):
        sensor_positions = _generate_sensor_positions(
            num_sensor,
            radius,
            z_offset,
        )
        sensor_coordinates = np.array(
            [position.coordinates() for position in sensor_positions])
        target_position = np.array([0, 0, distance])
        ranges = (np.linalg.norm(
            target_position - sensor_coordinates,
            axis=1,
        ))

        # Trilaterate the target position with range measurement noise.
        results = np.zeros((num_trials, 3))
        for i in range(num_trials):
            noise = np.random.normal(
                scale=standard_deviation,
                size=ranges.shape,
            )
            trilaterator = TrilateratorFactory.create_trilaterator(
                trilaterator_type,
                sensor_positions,
                ranges + noise,
            )
            results[i] = trilaterator.trilaterate()
        target_standard_deviations[num_sensor_index] = np.std(
            results,
            axis=0,
        )

        # Calculate the Cramér-Rao lower bound.
        trilaterator = TrilateratorFactory.create_trilaterator(
            trilaterator_type,
            sensor_positions,
            ranges,
        )
        crlb = trilaterator.cramer_rao_lower_bound(
            target_position,
            np.ones(num_sensor) * standard_deviation)
        crlb_standard_deviations[num_sensor_index] = np.sqrt(np.diag(crlb))

    # Plot the x, y, and z standard deviations, the lateral standard deviation,
    # and the overall standard deviation over the number of sensors.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        num_sensors,
        target_standard_deviations[:, 0],
        color="C0",
        label=r"Standard deviation in $x$",
    )
    ax.plot(
        num_sensors,
        crlb_standard_deviations[:, 0],
        color="C0",
        linestyle="--",
        label=r"CRLB standard deviation in $x$",
    )
    ax.plot(
        num_sensors,
        target_standard_deviations[:, 1],
        color="C1",
        label=r"Standard deviation in $y$",
    )
    ax.plot(
        num_sensors,
        crlb_standard_deviations[:, 1],
        color="C1",
        linestyle="--",
        label=r"CRLB standard deviation in $y$",
    )
    ax.plot(
        num_sensors,
        target_standard_deviations[:, 2],
        color="C2",
        label=r"Standard deviation in $z$",
    )
    ax.plot(
        num_sensors,
        crlb_standard_deviations[:, 2],
        color="C2",
        linestyle="--",
        label=r"CRLB standard deviation in $z$",
    )
    ax.plot(
        num_sensors,
        np.linalg.norm(target_standard_deviations[:, :2], axis=1),
        color="C3",
        label="Lateral standard deviation",
    )
    ax.plot(
        num_sensors,
        np.linalg.norm(crlb_standard_deviations[:, :2], axis=1),
        color="C3",
        linestyle="--",
        label=r"CRLB lateral standard deviation",
    )
    ax.plot(
        num_sensors,
        np.linalg.norm(target_standard_deviations, axis=1),
        color="C4",
        label="Total standard deviation",
    )
    ax.plot(
        num_sensors,
        np.linalg.norm(crlb_standard_deviations, axis=1),
        color="C4",
        linestyle="--",
        label=r"CRLB total standard deviation",
    )
    ax.set_xlabel("Number of sensors")
    ax.set_ylabel("Standard deviation [m]")
    ax.legend()
    plt.show()


def simulate_monte_carlo_over_z_offset(
    trilaterator_type: TrilateratorType,
    num_trials: int,
    radius: float,
    min_z_offset: float,
    max_z_offset: float,
    distance: float,
    standard_deviation: float,
) -> None:
    """Performs a Monte Carlo simulation on the target distance while sweeping
    the sensor z-offset for the least squares trilaterator.

    Args:
        trilaterator_type: Trilaterator type.
        num_trials: Number of simulations.
        radius: Sensor radius from the origin.
        min_z_offset: Minimum sensor z-offset.
        max_z_offset: Maximum sensor z-offset.
        distance: Distance to the target.
        standard_deviation: Standard deviation of the target distance noise.
    """
    num_sensors = 4
    z_offsets = np.arange(min_z_offset, max_z_offset + 10, 10)
    target_standard_deviations = np.zeros((len(z_offsets), 3))
    crlb_standard_deviations = np.zeros((len(z_offsets), 3))
    target_position = np.array([0, 0, distance])
    for z_offset_index, z_offset in enumerate(z_offsets):
        sensor_positions = _generate_sensor_positions(
            num_sensors,
            radius,
            z_offset,
        )
        sensor_coordinates = np.array(
            [position.coordinates() for position in sensor_positions])
        ranges = (np.linalg.norm(
            target_position - sensor_coordinates,
            axis=1,
        ))

        # Trilaterate the target position with range measurement noise.
        results = np.zeros((num_trials, 3))
        for i in range(num_trials):
            noise = np.random.normal(
                scale=standard_deviation,
                size=ranges.shape,
            )
            trilaterator = TrilateratorFactory.create_trilaterator(
                trilaterator_type,
                sensor_positions,
                ranges + noise,
            )
            results[i] = trilaterator.trilaterate()
        target_standard_deviations[z_offset_index] = np.std(
            results,
            axis=0,
        )

        # Calculate the Cramér-Rao lower bound.
        trilaterator = TrilateratorFactory.create_trilaterator(
            trilaterator_type,
            sensor_positions,
            ranges,
        )
        crlb = trilaterator.cramer_rao_lower_bound(
            target_position,
            np.ones(num_sensors) * standard_deviation)
        crlb_standard_deviations[z_offset_index] = np.sqrt(np.diag(crlb))

    # Plot the x, y, and z standard deviations, the lateral standard deviation,
    # and the overall standard deviation over the target distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        z_offsets,
        target_standard_deviations[:, 0],
        color="C0",
        label=r"Standard deviation in $x$",
    )
    ax.plot(
        z_offsets,
        crlb_standard_deviations[:, 0],
        color="C0",
        linestyle="--",
        label=r"CRLB standard deviation in $x$",
    )
    ax.plot(
        z_offsets,
        target_standard_deviations[:, 1],
        color="C1",
        label=r"Standard deviation in $y$",
    )
    ax.plot(
        z_offsets,
        crlb_standard_deviations[:, 1],
        color="C1",
        linestyle="--",
        label=r"CRLB standard deviation in $y$",
    )
    ax.plot(
        z_offsets,
        target_standard_deviations[:, 2],
        color="C2",
        label=r"Standard deviation in $z$",
    )
    ax.plot(
        z_offsets,
        crlb_standard_deviations[:, 2],
        color="C2",
        linestyle="--",
        label=r"CRLB standard deviation in $z$",
    )
    ax.plot(
        z_offsets,
        np.linalg.norm(target_standard_deviations[:, :2], axis=1),
        color="C3",
        label="Lateral standard deviation",
    )
    ax.plot(
        z_offsets,
        np.linalg.norm(crlb_standard_deviations[:, :2], axis=1),
        color="C3",
        linestyle="--",
        label=r"CRLB lateral standard deviation",
    )
    ax.plot(
        z_offsets,
        np.linalg.norm(target_standard_deviations, axis=1),
        color="C4",
        label="Total standard deviation",
    )
    ax.plot(
        z_offsets,
        np.linalg.norm(crlb_standard_deviations, axis=1),
        color="C4",
        linestyle="--",
        label=r"CRLB total standard deviation",
    )
    ax.set_xlabel(r"$z$-offset [m]")
    ax.set_ylabel("Standard deviation [m]")
    ax.legend()
    plt.show()


def simulate_monte_carlo_over_radius(
    trilaterator_type: TrilateratorType,
    num_trials: int,
    min_radius: float,
    max_radius: float,
    z_offset: float,
    distance: float,
    standard_deviation: float,
) -> None:
    """Performs a Monte Carlo simulation on the target distance while sweeping
    the sensor radius for the least squares trilaterator.

    Args:
        trilaterator_type: Trilaterator type.
        num_trials: Number of simulations.
        min_radius: Minimum sensor radius from the origin.
        max_radius: Maximum sensor radius from the origin.
        z_offset: Sensor z-offset.
        distance: Distance to the target.
        standard_deviation: Standard deviation of the target distance noise.
    """
    num_sensors = 4
    radii = np.arange(min_radius, max_radius + 10, 10)
    target_standard_deviations = np.zeros((len(radii), 3))
    crlb_standard_deviations = np.zeros((len(radii), 3))
    target_position = np.array([0, 0, distance])
    for radius_index, radius in enumerate(radii):
        sensor_positions = _generate_sensor_positions(
            num_sensors,
            radius,
            z_offset,
        )
        sensor_coordinates = np.array(
            [position.coordinates() for position in sensor_positions])
        ranges = (np.linalg.norm(
            target_position - sensor_coordinates,
            axis=1,
        ))

        # Trilaterate the target position with range measurement noise.
        results = np.zeros((num_trials, 3))
        for i in range(num_trials):
            noise = np.random.normal(
                scale=standard_deviation,
                size=ranges.shape,
            )
            trilaterator = TrilateratorFactory.create_trilaterator(
                trilaterator_type,
                sensor_positions,
                ranges + noise,
            )
            results[i] = trilaterator.trilaterate()
        target_standard_deviations[radius_index] = np.std(
            results,
            axis=0,
        )

        # Calculate the Cramér-Rao lower bound.
        trilaterator = TrilateratorFactory.create_trilaterator(
            trilaterator_type,
            sensor_positions,
            ranges,
        )
        crlb = trilaterator.cramer_rao_lower_bound(
            target_position,
            np.ones(num_sensors) * standard_deviation)
        crlb_standard_deviations[radius_index] = np.sqrt(np.diag(crlb))

    # Plot the x, y, and z standard deviations, the lateral standard deviation,
    # and the overall standard deviation over the target distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        radii,
        target_standard_deviations[:, 0],
        color="C0",
        label=r"Standard deviation in $x$",
    )
    ax.plot(
        radii,
        crlb_standard_deviations[:, 0],
        color="C0",
        linestyle="--",
        label=r"CRLB standard deviation in $x$",
    )
    ax.plot(
        radii,
        target_standard_deviations[:, 1],
        color="C1",
        label=r"Standard deviation in $y$",
    )
    ax.plot(
        radii,
        crlb_standard_deviations[:, 1],
        color="C1",
        linestyle="--",
        label=r"CRLB standard deviation in $y$",
    )
    ax.plot(
        radii,
        target_standard_deviations[:, 2],
        color="C2",
        label=r"Standard deviation in $z$",
    )
    ax.plot(
        radii,
        crlb_standard_deviations[:, 2],
        color="C2",
        linestyle="--",
        label=r"CRLB standard deviation in $z$",
    )
    ax.plot(
        radii,
        np.linalg.norm(target_standard_deviations[:, :2], axis=1),
        color="C3",
        label="Lateral standard deviation",
    )
    ax.plot(
        radii,
        np.linalg.norm(crlb_standard_deviations[:, :2], axis=1),
        color="C3",
        linestyle="--",
        label=r"CRLB lateral standard deviation",
    )
    ax.plot(
        radii,
        np.linalg.norm(target_standard_deviations, axis=1),
        color="C4",
        label="Total standard deviation",
    )
    ax.plot(
        radii,
        np.linalg.norm(crlb_standard_deviations, axis=1),
        color="C4",
        linestyle="--",
        label=r"CRLB total standard deviation",
    )
    ax.set_xlabel("Radius [m]")
    ax.set_ylabel("Standard deviation [m]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    simulate_monte_carlo(
        FLAGS.trilaterator_type,
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.z_offset,
        FLAGS.distance,
        FLAGS.standard_deviation,
    )
    simulate_monte_carlo_over_distance(
        FLAGS.trilaterator_type,
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.z_offset,
        FLAGS.min_distance,
        FLAGS.max_distance,
        FLAGS.standard_deviation,
    )
    simulate_monte_carlo_over_num_sensors(
        FLAGS.trilaterator_type,
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.z_offset,
        FLAGS.distance,
        FLAGS.standard_deviation,
        FLAGS.max_num_sensors,
    )
    simulate_monte_carlo_over_z_offset(
        FLAGS.trilaterator_type,
        FLAGS.num_trials,
        FLAGS.radius,
        FLAGS.min_z_offset,
        FLAGS.max_z_offset,
        FLAGS.distance,
        FLAGS.standard_deviation,
    )
    simulate_monte_carlo_over_radius(
        FLAGS.trilaterator_type,
        FLAGS.num_trials,
        FLAGS.min_radius,
        FLAGS.max_radius,
        FLAGS.z_offset,
        FLAGS.distance,
        FLAGS.standard_deviation,
    )


if __name__ == "__main__":
    flags.DEFINE_enum(
        "trilaterator_type",
        TrilateratorType.NONLINEAR_LEAST_SQUARES,
        TrilateratorType.values(),
        "Trilaterator type.",
    )
    flags.DEFINE_integer("num_trials",
                         100000,
                         "Number of trials.",
                         lower_bound=0)
    flags.DEFINE_float("radius",
                       50,
                       "Sensor radius from the origin.",
                       lower_bound=0.0)
    flags.DEFINE_float("z_offset", 100, "Sensor z-offset.", lower_bound=0.0)
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
    flags.DEFINE_integer("max_num_sensors",
                         20,
                         "Maximum number of sensors.",
                         lower_bound=4)
    flags.DEFINE_float("min_z_offset",
                       10,
                       "Minimum sensor z-offset.",
                       lower_bound=0.0)
    flags.DEFINE_float("max_z_offset",
                       1000,
                       "Maximum sensor z-offset.",
                       lower_bound=0.0)
    flags.DEFINE_float("min_radius", 10, "Minimum radius.", lower_bound=0.0)
    flags.DEFINE_float("max_radius", 1000, "Maximum radius.", lower_bound=0.0)

    app.run(main)
