"""Mixes a TX chirp with an RX chirp to verify the IF signal."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

from simulation.radar.components.chirp import CHIRP_MAP, ChirpType
from simulation.radar.components.radar import Radar

FLAGS = flags.FLAGS


def compare_chirp_if_signals(
    rnge: float,
    chirp_type: ChirpType,
) -> None:
    """Compares the mixed IF signal with the generated IF signal.

    Args:
        rnge: Range in m.
        chirp_type: Chirp type.
    """
    radar = Radar()
    chirp = CHIRP_MAP[chirp_type](radar)
    tau = 2 * rnge / radar.c

    # Mix the TX and RX chirp for the IF signal.
    tx_signal = chirp.get_signal()
    rx_signal = chirp.get_signal(tau)
    mixed_if_signal = tx_signal * np.conjugate(rx_signal)

    # Generate the IF signal using the chirp.
    if_signal = chirp.get_if_signal(tau)

    # Calculate the real and imaginary differences between the IF signals.
    real_diff = np.real(if_signal - mixed_if_signal)
    imag_diff = np.imag(if_signal - mixed_if_signal)

    # Calculate the maximum real and imaginary differences.
    max_real_diff = np.linalg.norm(real_diff, np.inf)
    max_imag_diff = np.linalg.norm(imag_diff, np.inf)
    logging.info("Maximum real difference: %e", max_real_diff)
    logging.info("Maximum imaginary difference: %e", max_imag_diff)

    # Plot the real and imaginary differences between the IF signals.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(real_diff, label="Real")
    plt.plot(imag_diff, label="Imaginary")
    ax.set_title("Differences between the mixed and generated IF signals")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Difference")
    plt.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    compare_chirp_if_signals(
        FLAGS.range,
        FLAGS.chirp_type,
    )


if __name__ == "__main__":
    flags.DEFINE_float("range", 50, "Range in m.", lower_bound=0.0)
    flags.DEFINE_enum("chirp_type", ChirpType.LINEAR, ChirpType.values(),
                      "Chirp type.")

    app.run(main)
