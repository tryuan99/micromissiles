"""The sinusoid represents a single frequency along with noise."""

import numpy as np

from simulation.radar.components.noise import GaussianNoise
from simulation.radar.components.samples import Samples
from utils import constants


class Sinusoid(Samples):
    """Complex sinusoid signal at a single frequency."""

    def __init__(self,
                 fs: float,
                 num_samples: int,
                 frequency: float,
                 phase: float,
                 amplitude: float = 1,
                 snr: float = np.inf) -> None:
        super().__init__(
            self.generate_signal(fs, num_samples, frequency, phase, amplitude,
                                 snr))

    @staticmethod
    def generate_signal(fs: float,
                        num_samples: int,
                        frequency: float,
                        phase: float,
                        amplitude: float = 1,
                        snr: float = np.inf) -> np.ndarray:
        """Generates the signal.

        Args:
            fs: Sampling frequency in Hz.
            num_samples: Number of samples.
            frequency: Sinusoid frequency in Hz.
            phase: Sinusoid phase in rad.
            amplitude: Sinusoid amplitude.
            snr: SNR in dB.

        Returns:
            The samples of the complex sinusoid.
        """
        if snr == np.inf:
            noise_amplitude = 0
        else:
            noise_amplitude = amplitude / constants.db2mag(snr)
        noise = GaussianNoise.generate_noise_samples(num_samples,
                                                     noise_amplitude)
        return amplitude * np.exp(1j * (2 * np.pi * frequency / fs *
                                        np.arange(num_samples) + phase)) + noise
