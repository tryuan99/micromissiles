import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags, logging

from simulation.swarm.utils.py import constants

FLAGS = flags.FLAGS

# Micromissile initial speed in m/s.
MICROMISSILE_INITIAL_SPEED = 1000

# Micromissile mass in kg.
MICROMISSILE_MASS = 0.37

# Micromissile drag coefficient.
MICROMISSILE_DRAG_COEFFICIENT = 0.7

# Micromissile cross-sectional area in m^2.
MICROMISSILE_CROSS_SECTIONAL_AREA = 3e-4


def plot_speed_vs_distance(data: str) -> None:
    """Plots the micromissile speed over its distance as it approaches terminal
    velocity.

    Args:
        data: Data filename.
    """
    # Open the speed vs. distance data file.
    df = pd.read_csv(data, comment="#")
    distance_column, speed_column = df.columns
    logging.info(df.describe())

    # Plot the speed as a function of the distance travelled.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df[distance_column], df[speed_column], label="Simulated")
    ax.plot(df[distance_column],
            MICROMISSILE_INITIAL_SPEED *
            np.exp(-1 / (2 * MICROMISSILE_MASS) * constants.AIR_DENSITY *
                   MICROMISSILE_DRAG_COEFFICIENT *
                   MICROMISSILE_CROSS_SECTIONAL_AREA * df[distance_column]),
            label="Theoretical",
            linestyle="--")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Speed [m/s]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    plot_speed_vs_distance(FLAGS.data)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data",
        "simulation/swarm/results/data/air_drag_terminal_velocity_data.csv",
        "Data filename.")

    app.run(main)
