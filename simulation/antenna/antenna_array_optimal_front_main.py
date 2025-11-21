"""Analyzes the antenna arrays at the Pareto-optimal front between the main
lobe width and the sidelobe level.
"""

import matplotlib.pyplot as plt
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config

FLAGS = flags.FLAGS


def plot_pareto_optimal_front(df: pd.DataFrame) -> None:
    """Plots the Pareto-optimal front between the main lobe width and the
    sidelobe level.

    Args:
        df: Pareto-optimal front dataframe.
    """
    main_lobe_width_column, sidelobe_level_column = df.columns[:2]
    fig, ax = plt.subplots(figsize=(12, 6))
    df.plot.line(
        main_lobe_width_column,
        sidelobe_level_column,
        ax=ax,
        marker="^",
        label="Pareto-optimal front",
    )
    # Plot the -3 dB threshold.
    ax.axhline(-3, color="red", linestyle="--", label=r"-3 dB threshold")
    ax.set_xlabel("Main lobe width [rad]")
    ax.set_ylabel("Sidelobe level [dB]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Open the antenna array Pareto-optimal front data file.
    df = pd.read_csv(FLAGS.data, comment="#")
    plot_pareto_optimal_front(df)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data",
        "simulation/antenna/data/antenna_array_optimal_front_1d_cosh_4.csv",
        "Antenna array Pareto-optimal front data.",
    )

    app.run(main)
