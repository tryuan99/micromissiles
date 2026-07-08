"""Plots timem domain waveforms exported from an oscilloscope."""

from itertools import zip_longest

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config

FLAGS = flags.FLAGS


def _trim_waveform(
    df: pd.DataFrame,
    start_time: float,
    end_time: float,
) -> pd.DataFrame:
    """Trims the waveform to the given start and end time.

    Args:
        df: Waveform dataframe.
        start_time: Start times.
        end_time: End times.
    """
    time_column, _ = df.columns
    if start_time is not None:
        df = df[df[time_column] >= start_time]
    if end_time is not None:
        df = df[df[time_column] <= end_time]
    return df


def plot_waveforms(dfs: list[pd.DataFrame], labels: list[str]) -> None:
    """Plots the waveforms exported from an oscilloscope.

    Args:
        dfs: Waveform dataframes.
        labels: Data labels.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    for df, label in zip(dfs, labels or [""] * len(dfs)):
        time_column, voltage_column = df.columns
        ax.plot(df[time_column], df[voltage_column], label=label)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Voltage [V]")
    ax.grid(visible=True, which="both")
    if labels:
        ax.legend()
    fig.tight_layout()
    plt.show()


def plot_spectra(dfs: list[pd.DataFrame], labels: list[str]) -> None:
    """Plots the spectra of the waveforms exported from an oscilloscope.

    Args:
        dfs: Waveform dataframes.
        labels: Data labels.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    for df, label in zip(dfs, labels or [""] * len(dfs)):
        time_column, voltage_column = df.columns
        voltage_fft = np.fft.fft(df[voltage_column])
        voltage_fft_abs = np.abs(voltage_fft)

        sampling_period = df[time_column].diff().mean()
        frequencies = np.fft.fftfreq(len(voltage_fft), d=sampling_period)
        fft_onesided_length = (len(voltage_fft) + 1) // 2

        ax.plot(
            frequencies[:fft_onesided_length],
            20 * np.log10(voltage_fft_abs)[:fft_onesided_length],
            label=label,
        )
        print(frequencies[np.argmax(voltage_fft_abs)])
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("FFT magnitude [dB]")
    ax.grid(visible=True, which="both")
    if labels:
        ax.legend()
    fig.tight_layout()
    plt.show()


def main(argv):
    assert len(argv) == 1

    dfs = [
        _trim_waveform(pd.read_csv(data, comment="#"), start_time, end_time)
        for data, start_time, end_time in zip_longest(
            FLAGS.data,
            FLAGS.start or [],
            FLAGS.end or [],
        )
    ]
    plot_waveforms(dfs, FLAGS.labels)
    plot_spectra(dfs, FLAGS.labels)


if __name__ == "__main__":
    flags.DEFINE_multi_string("data", None, "Data filenames.")
    flags.DEFINE_multi_string("labels", None, "Data labels")
    flags.DEFINE_multi_float("start", None, "Start times.")
    flags.DEFINE_multi_float("end", None, "End times.")
    flags.mark_flag_as_required("data")

    app.run(main)
