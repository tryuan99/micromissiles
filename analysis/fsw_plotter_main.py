"""Plots spectrua exported from the Rohde & Schwarz FSW spectrum analyzer."""

import matplotlib.pyplot as plt
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config

FLAGS = flags.FLAGS


def plot_spectra(dfs: list[pd.DataFrame], labels: list[str]) -> None:
    """Plots the spectrua exported from the Rohde & Schwarz FSW spectrum
    analyzer.

    Args:
        dfs: Spectrum dataframes.
        labels: Data labels.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    for df, label in zip(dfs, labels or [""] * len(dfs)):
        frequency_column, power_column = df.columns
        ax.semilogx(df[frequency_column], df[power_column], label=label)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Power [dBm]")
    ax.grid(visible=True, which="both")
    if labels:
        ax.legend()
    fig.tight_layout()
    plt.show()


def main(argv):
    assert len(argv) == 1

    dfs = [pd.read_csv(data, comment="#") for data in FLAGS.data]
    plot_spectra(dfs, FLAGS.labels)


if __name__ == "__main__":
    flags.DEFINE_multi_string("data", None, "Data filenames.")
    flags.DEFINE_multi_string("labels", None, "Data labels")
    flags.mark_flag_as_required("data")

    app.run(main)
