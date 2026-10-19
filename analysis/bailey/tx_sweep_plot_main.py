"""Plots a Bailey TX channel sweep captured by
//utils/devices:bailey_tx_sweep_main.

A VGA gain sweep plots the S21 magnitude, the gain step between adjacent codes,
and the S21 phase shift relative to code 0 against the VGA gain code.

A phase sweep plots the measured phase relative to phase index 0, the phase
error from the commanded phase, and the S21 magnitude against the commanded
phase.

Absolute magnitudes require a FieldFox calibration at the cable ends.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from absl import app, flags, logging

import utils.visualization.mpl_config
from utils import constants

FLAGS = flags.FLAGS

# Number of phases and the phase step in degrees.
NUM_PHASES = 128
PHASE_STEP = 360 / NUM_PHASES


def wrap_phase(phase: np.ndarray) -> np.ndarray:
    """Wraps the phase in degrees to [-180, 180)."""
    return (phase + 180) % 360 - 180


def angle(s21: pd.DataFrame) -> pd.DataFrame:
    """Returns the phase of the complex S21 in degrees."""
    return pd.DataFrame(np.rad2deg(np.angle(s21.values)),
                        index=s21.index,
                        columns=s21.columns)


def select_frequencies(df: pd.DataFrame,
                       frequencies: list[float]) -> pd.DataFrame:
    """Selects the measured frequency points closest to the given frequencies.

    Args:
        df: Sweep dataframe.
        frequencies: Frequencies in Hz.

    Returns:
        A dataframe indexed by the swept code with one complex S21 column per
        frequency.

    Raises:
        ValueError: If a frequency lies outside the measured frequency grid.
    """
    measured_frequencies = np.sort(df["frequency"].unique())
    frequency_step = (np.diff(measured_frequencies).max()
                      if len(measured_frequencies) > 1 else 0)
    swept_column = "vga_gain" if df["vga_gain"].nunique() > 1 else "phase"
    s21 = {}
    for frequency in frequencies:
        measured_frequency = measured_frequencies[np.abs(measured_frequencies -
                                                         frequency).argmin()]
        if np.abs(measured_frequency - frequency) > frequency_step:
            raise ValueError(f"{frequency} Hz was not measured.")
        frequency_df = df[df["frequency"] == measured_frequency]
        s21[frequency] = pd.Series(
            (frequency_df["s21_real"] + 1j * frequency_df["s21_imag"]).values,
            index=frequency_df[swept_column].values,
        )
    return pd.DataFrame(s21)


def plot_vga_gain_sweep(s21: pd.DataFrame) -> None:
    """Plots a VGA gain sweep.

    Args:
        s21: Complex S21 indexed by the VGA gain code with one column per
            frequency.
    """
    vga_gains = s21.index.values
    magnitude = constants.mag2db(np.abs(s21))
    phase = wrap_phase(angle(s21 / s21.loc[vga_gains.min()]))

    for frequency in s21.columns:
        logging.info(
            "%g GHz: gain range %.2f dB, maximum step %.2f dB, "
            "phase shift range %.2f deg.", frequency / 1e9,
            np.ptp(magnitude[frequency]),
            np.diff(magnitude[frequency]).max(), np.ptp(phase[frequency]))

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(s21.columns):
        ax.plot(
            vga_gains,
            magnitude[frequency],
            color=f"C{frequency_index}",
            label=f"{frequency / 1e9:g} GHz",
        )
    ax.set_xlabel("VGA gain code")
    ax.set_ylabel("S21 magnitude [dB]")
    ax.legend()
    plt.show()

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(s21.columns):
        ax.plot(
            vga_gains[1:],
            np.diff(magnitude[frequency]),
            color=f"C{frequency_index}",
            label=f"{frequency / 1e9:g} GHz",
        )
    ax.set_xlabel("VGA gain code")
    ax.set_ylabel("Gain step [dB]")
    ax.legend()
    plt.show()

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(s21.columns):
        ax.plot(
            vga_gains,
            phase[frequency],
            color=f"C{frequency_index}",
            label=f"{frequency / 1e9:g} GHz",
        )
    ax.set_xlabel("VGA gain code")
    ax.set_ylabel("S21 phase relative to code 0 [deg]")
    ax.legend()
    plt.show()


def plot_phase_sweep(s21: pd.DataFrame) -> None:
    """Plots a phase sweep.

    Args:
        s21: Complex S21 indexed by the phase index with one column per
            frequency.
    """
    commanded_phase = s21.index.values * PHASE_STEP
    # Reconstruct the measured phase from the wrapped phase error, so that a
    # measured phase slightly below 0 deg does not wrap to 360 deg.
    phase_error = wrap_phase(
        angle(s21 / s21.loc[0]) - commanded_phase[:, np.newaxis])
    measured_phase = phase_error + commanded_phase[:, np.newaxis]
    magnitude = constants.mag2db(np.abs(s21))

    for frequency in s21.columns:
        logging.info(
            "%g GHz: RMS phase error %.2f deg, peak phase error %.2f deg, "
            "magnitude range %.2f dB.", frequency / 1e9,
            np.sqrt(np.mean(phase_error[frequency]**2)),
            np.abs(phase_error[frequency]).max(), np.ptp(magnitude[frequency]))

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(
        commanded_phase,
        commanded_phase,
        color="black",
        linestyle="--",
        label="Ideal",
    )
    for frequency_index, frequency in enumerate(s21.columns):
        ax.plot(
            commanded_phase,
            measured_phase[frequency],
            color=f"C{frequency_index}",
            label=f"{frequency / 1e9:g} GHz",
        )
    ax.set_xlabel("Commanded phase [deg]")
    ax.set_ylabel("Measured phase relative to phase 0 [deg]")
    ax.legend()
    plt.show()

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(s21.columns):
        ax.plot(
            commanded_phase,
            phase_error[frequency],
            color=f"C{frequency_index}",
            label=f"{frequency / 1e9:g} GHz",
        )
    ax.set_xlabel("Commanded phase [deg]")
    ax.set_ylabel("Phase error [deg]")
    ax.legend()
    plt.show()

    fig, ax = plt.subplots(figsize=(6, 6))
    for frequency_index, frequency in enumerate(s21.columns):
        ax.plot(
            commanded_phase,
            magnitude[frequency],
            color=f"C{frequency_index}",
            label=f"{frequency / 1e9:g} GHz",
        )
    ax.set_xlabel("Commanded phase [deg]")
    ax.set_ylabel("S21 magnitude [dB]")
    ax.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1

    df = pd.read_csv(FLAGS.data, comment="#")
    s21 = select_frequencies(df, FLAGS.frequencies)
    if df["vga_gain"].nunique() > 1:
        plot_vga_gain_sweep(s21)
    else:
        plot_phase_sweep(s21)


if __name__ == "__main__":
    flags.DEFINE_string("data", None, "Sweep CSV file.")
    flags.DEFINE_multi_float("frequencies", None, "Frequencies to plot in Hz.")
    flags.mark_flags_as_required(["data", "frequencies"])

    app.run(main)
