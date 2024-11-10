import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags, logging

from simulation.swarm.utils.py import constants

FLAGS = flags.FLAGS


def compare_controllers(data: str, pn_data: str) -> None:
    """Compares the two controllers over time and over distance to target.

    Args:
        data: Controller data filename.
        pn_data: Proportional navigation controller filename.
    """
    # Open the controller data file.
    df = pd.read_csv(data, comment="#")
    time_column, distance_to_target_column, speed_column = df.columns
    logging.info(df.describe())

    # Open the proportional navigation controller data file.
    pn_df = pd.read_csv(pn_data, comment="#")
    pn_time_column, pn_distance_to_target_column, pn_speed_column = pn_df.columns
    logging.info(pn_df.describe())

    # Plot the interceptor speed over time.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df[time_column], df[speed_column], label="Hybrid controller")
    ax.plot(pn_df[pn_time_column],
            pn_df[pn_speed_column],
            label="PN controller")
    ax.set_xlabel("Time since launch [s]")
    ax.set_ylabel("Interceptor speed [m/s]")
    ax.legend()
    plt.show()

    # Plot the interceptor speed distance to target.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df[distance_to_target_column],
            df[speed_column],
            label="Hybrid controller")
    ax.plot(pn_df[pn_distance_to_target_column],
            pn_df[pn_speed_column],
            label="PN controller")
    ax.invert_xaxis()
    ax.set_xlabel("Distance to target [m]")
    ax.set_ylabel("Interceptor speed [m/s]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    compare_controllers(FLAGS.data, FLAGS.pn_data)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data",
        "simulation/swarm/results/controller/data/hybrid_controller_6km_data.csv",
        "Controller data filename.")
    flags.DEFINE_string(
        "pn_data",
        "simulation/swarm/results/controller/data/pn_controller_6km_data.csv",
        "Proportional navigation controller data filename.")

    app.run(main)
