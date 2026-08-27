"""Plots the S-parameters exported from a VNA."""

import matplotlib.pyplot as plt
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config

FLAGS = flags.FLAGS


def plot_s_parameters(dfs: list[pd.DataFrame], labels: list[str]) -> None:
    """Plots the S-parameters exported from a VNA.

    Args:
        dfs: S-parameter dataframes.
        labels: Data labels.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    for df, label in zip(dfs, labels or [""] * len(dfs)):
        frequency_column, sparam_column = df.columns
        ax.semilogx(
            df[frequency_column],
            df[sparam_column],
            label=label or sparam_column,
        )
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Magnitude [dB]")
    ax.grid(visible=True, which="both")
    ax.legend()
    fig.tight_layout()
    plt.show()


def main(argv):
    assert len(argv) == 1

    dfs = [pd.read_csv(data, comment="#") for data in FLAGS.data]
    plot_s_parameters(dfs, FLAGS.labels)


if __name__ == "__main__":
    flags.DEFINE_multi_string("data", None, "Data filenames.")
    flags.DEFINE_multi_string("labels", None, "Data labels")
    flags.mark_flag_as_required("data")

    app.run(main)
