"""Simulates the windowing loss."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, logging


def _calculate_amplitude(samples: np.ndarray) -> float:
    """Calculates the amplitude of the samples."""
    return np.sqrt(np.mean(np.abs(samples)**2))


def _mag2db(samples: np.ndarray) -> np.ndarray:
    """Converts magnitude to dB."""
    return 20 * np.log10(samples)


def simulate_windowing_loss() -> None:
    """Simulates the windowing loss."""
    SIGNAL_LENGTH = 512

    # Generate the signal.
    time = np.arange(SIGNAL_LENGTH) / 1e3
    signal = np.exp(1j * 2 * np.pi * SIGNAL_LENGTH / 2 * time)

    WINDOWS = [
        ("Uniform", np.ones),
        ("Hann", np.hanning),
        ("Blackman", np.blackman),
    ]

    fig, ax = plt.subplots(figsize=(12, 8))
    for window_name, window_function in WINDOWS:
        # Generate a normalized window.
        window = window_function(SIGNAL_LENGTH + 2)[1:-1]
        window /= np.linalg.norm(window)

        # Apply the window and perform the FFT.
        windowed_signal = signal * window
        windowed_signal_fft = np.fft.fft(windowed_signal)

        windowed_signal_fft_abs = np.abs(windowed_signal_fft)
        windowed_signal_fft_abs_db = _mag2db(windowed_signal_fft_abs)
        plt.plot(time,
                 windowed_signal_fft_abs_db,
                 label=f"{window_name} window")

        logging.info(
            "%s window: amplitude: %f, peak: %f dB",
            window_name,
            _calculate_amplitude(windowed_signal),
            np.max(windowed_signal_fft_abs_db),
        )
    plt.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    simulate_windowing_loss()


if __name__ == "__main__":
    app.run(main)
