import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags, logging

from simulation.swarm.py import constants

FLAGS = flags.FLAGS

# Micromissile initial speed in m/s.
MICROMISSILE_INITIAL_SPEED = 1000

# Micromissile normal acceleration in m/s^2.
MICROMISSILE_NORMAL_ACCELERATION = 100

# Micromissile mass in kg.
MICROMISSILE_MASS = 0.37

# Micromissile drag coefficient.
MICROMISSILE_DRAG_COEFFICIENT = 0.7

# Micromissile lift-drag ratio.
MICROMISSILE_LIFT_DRAG_RATIO = 5

# Micromissile cross-sectional area in m^2.
MICROMISSILE_CROSS_SECTIONAL_AREA = 3e-4


def plot_speed_vs_time(data: str) -> None:
    """Plots the micromissile speed over time as it turns.

    Args:
        data: Data filename.
    """
    # Open the speed vs. azimuth data file.
    df = pd.read_csv(data, comment="#")
    time_column, azimuth_column, speed_column = df.columns
    logging.info(df.describe())

    # Calculate the expected speed.
    k0 = MICROMISSILE_NORMAL_ACCELERATION / MICROMISSILE_LIFT_DRAG_RATIO
    k2 = ((constants.AIR_DENSITY * MICROMISSILE_DRAG_COEFFICIENT *
           MICROMISSILE_CROSS_SECTIONAL_AREA) / (2 * MICROMISSILE_MASS))
    C = -(np.arctan(np.sqrt(k2 / k0) * MICROMISSILE_INITIAL_SPEED) /
          np.sqrt(k0 * k2))
    speed = -(np.sqrt(k0 / k2) *
              np.tan(np.sqrt(k0 * k2) * (df[time_column] + C)))

    # Plot the speed as a function of the azimuth.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df[time_column], df[speed_column], label="Simulated")
    ax.plot(df[time_column], speed, label="Theoretical", linestyle="--")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Speed [m/s]")
    ax.legend()
    plt.show()


def plot_speed_vs_azimuth(data: str) -> None:
    """Plots the micromissile speed over its azimuth as it turns.

    Args:
        data: Data filename.
    """
    # Open the speed vs. azimuth data file.
    df = pd.read_csv(data, comment="#")
    time_column, azimuth_column, speed_column = df.columns
    logging.info(df.describe())

    # Calculate the expected speed.
    k = ((constants.AIR_DENSITY * MICROMISSILE_DRAG_COEFFICIENT *
          MICROMISSILE_CROSS_SECTIONAL_AREA) /
         (2 * MICROMISSILE_MASS * MICROMISSILE_NORMAL_ACCELERATION))
    k_LD = MICROMISSILE_LIFT_DRAG_RATIO * k
    speed = (np.sqrt(
        1 / (np.exp(2 / MICROMISSILE_LIFT_DRAG_RATIO * df[azimuth_column]) *
             (1 / MICROMISSILE_INITIAL_SPEED**2 + k_LD) - k_LD)))

    # Plot the speed as a function of the azimuth.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df[azimuth_column], df[speed_column], label="Simulated")
    ax.plot(df[azimuth_column], speed, label="Theoretical", linestyle="--")
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Speed [m/s]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    plot_speed_vs_time(FLAGS.data)
    plot_speed_vs_azimuth(FLAGS.data)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data", "simulation/swarm/results/data/total_drag_turning_data.csv",
        "Data filename.")

    app.run(main)
