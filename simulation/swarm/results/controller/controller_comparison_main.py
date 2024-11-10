import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags, logging

from simulation.swarm.utils.py import constants

FLAGS = flags.FLAGS


def plot_interceptor_speed_over_time(data: list[str],
                                     labels: list[str]) -> None:
    """Plot the interceptor speed over time for each controller.

    Args:
        data: Data filenames.
        labels: Plot labels.
    """
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))

    # Open the controller data files.
    for controller_data, label in zip(data, labels):
        df = pd.read_csv(controller_data, comment="#")
        time_column, distance_to_target_column, speed_column = df.columns
        logging.info(df.describe())

        # Plot the interceptor speed over time.
        ax.plot(df[time_column], df[speed_column], label=label)
    ax.set_xlabel("Time since launch [s]")
    ax.set_ylabel("Interceptor speed [m/s]")
    ax.legend()
    plt.show()


def plot_interceptor_speed_over_distance_to_target(data: list[str],
                                                   labels: list[str]) -> None:
    """Plot the interceptor speed over distance to target for each controller.

    Args:
        data: Data filenames.
        labels: Plot labels.
    """
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))

    # Open the controller data files.
    for controller_data, label in zip(data, labels):
        df = pd.read_csv(controller_data, comment="#")
        time_column, distance_to_target_column, speed_column = df.columns
        logging.info(df.describe())

        # Plot the interceptor speed over distance to target.
        ax.plot(df[distance_to_target_column], df[speed_column], label=label)
    ax.invert_xaxis()
    ax.set_xlabel("Distance to target [m]")
    ax.set_ylabel("Interceptor speed [m/s]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    plot_interceptor_speed_over_time(FLAGS.data, FLAGS.labels)
    plot_interceptor_speed_over_distance_to_target(FLAGS.data, FLAGS.labels)


if __name__ == "__main__":
    flags.DEFINE_multi_string("data", [
        "simulation/swarm/results/controller/data/hybrid_controller_6km_0_data.csv",
        "simulation/swarm/results/controller/data/hybrid_controller_6km_0_25_data.csv",
        "simulation/swarm/results/controller/data/hybrid_controller_6km_1_data.csv",
        "simulation/swarm/results/controller/data/hybrid_controller_6km_4_data.csv",
        "simulation/swarm/results/controller/data/pn_controller_6km_data.csv",
    ], "Data filenames.")
    flags.DEFINE_multi_string("labels", [
        "Hybrid controller (distance cost factor = 0, speed cost factor = 1)",
        "Hybrid controller (distance cost factor = 0.25, speed cost factor = 1)",
        "Hybrid controller (distance cost factor = 1, speed cost factor = 1)",
        "Hybrid controller (distance cost factor = 4, speed cost factor = 1)",
        "PN controller",
    ], "Plot labels.")

    app.run(main)
