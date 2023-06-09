import numpy as np
from absl.testing import absltest

from simulation.radar.components.chirp import (Chirp, ExponentialChirp,
                                               LinearChirp, QuadraticChirp)
from simulation.radar.components.radar import Radar

# Maximum real and imaginary difference between the IF signals.
MAX_IF_EPSILON = 5e-8


class ChirpTestCase(absltest.TestCase):

    def compare_if_signals(self, radar: Radar, chirp: Chirp):
        rnge = 100
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
        self.assertLess(max_real_diff, MAX_IF_EPSILON)
        self.assertLess(max_imag_diff, MAX_IF_EPSILON)


class LinearChirpTestCase(ChirpTestCase):

    def test_if_signal(self):
        radar = Radar()
        chirp = LinearChirp(radar)
        self.compare_if_signals(radar, chirp)


class QuadraticChirpTestCase(ChirpTestCase):

    def test_if_signal(self):
        radar = Radar()
        chirp = QuadraticChirp(radar)
        self.compare_if_signals(radar, chirp)


class ExponentialChirpTestCase(ChirpTestCase):

    def test_if_signal(self):
        radar = Radar()
        chirp = ExponentialChirp(radar)
        self.compare_if_signals(radar, chirp)


if __name__ == "__main__":
    absltest.main()
