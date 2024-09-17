import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots
from absl import app, flags, logging

FLAGS = flags.FLAGS

# Micromissile initial speed in m/s.
MICROMISSILE_INITIAL_SPEED = 1000

# Micromissile lift-drag ratio.
MICROMISSILE_LIFT_DRAG_RATIO = 5


def plot_speed_vs_azimuth(data: str) -> None:
    """Plots the micromissile speed over its azimuth as it turns.

    Args:
        data: Data filename.
    """
    # Open the speed vs. azimuth data file.
    df = pd.read_csv(data, comment="#")
    azimuth_column, speed_column = df.columns
    logging.info(df.describe())

    # Plot the speed as a function of the azimuth.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df[azimuth_column], df[speed_column], label="Simulated")
    ax.plot(df[azimuth_column],
            MICROMISSILE_INITIAL_SPEED *
            (1 - df[azimuth_column] / MICROMISSILE_LIFT_DRAG_RATIO),
            label="Theoretical (linear)",
            linestyle="--")
    ax.plot(df[azimuth_column],
            MICROMISSILE_INITIAL_SPEED *
            np.exp(-df[azimuth_column] / MICROMISSILE_LIFT_DRAG_RATIO),
            label="Theoretical (exponential)",
            linestyle="--")
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Speed [m/s]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    plot_speed_vs_azimuth(FLAGS.data)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data",
        "simulation/swarm/results/data/lift_induced_drag_turning_data.csv",
        "Data filename.")

    app.run(main)
