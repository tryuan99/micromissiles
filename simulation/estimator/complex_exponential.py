"""The complex exponential represents the samples of a complex exponential
given by A * exp(jtheta) * exp((alpha + j * 2pi * f) * t).
"""

import numpy as np

from simulation.radar.components.noise import GaussianNoise
from simulation.radar.components.samples import Samples
from utils import constants


class ComplexExponentialParams:
    """Complex exponential parameters."""

    def __init__(self,
                 frequency: float = 0,
                 phase: float = 0,
                 amplitude: float = 1,
                 alpha: float = 0) -> None:
        self.frequency = frequency
        self.phase = phase
        self.amplitude = amplitude
        self.alpha = alpha


class ComplexExponential(Samples):
    """Complex exponential of the form
    A * exp(jtheta) * exp((alpha + j * 2pi * f) * t).
    """

    def __init__(self,
                 fs: float,
                 num_samples: int,
                 frequency: float = 0,
                 phase: float = 0,
                 amplitude: float = 1,
                 alpha: float = 0,
                 params: ComplexExponentialParams = None,
                 snr: float = np.inf) -> None:
        super().__init__(
            self.generate_signal(fs, num_samples, frequency, phase, amplitude,
                                 alpha, params, snr))

    @staticmethod
    def generate_signal(fs: float,
                        num_samples: int,
                        frequency: float = 0,
                        phase: float = 0,
                        amplitude: float = 1,
                        alpha: float = 0,
                        params: ComplexExponentialParams = None,
                        snr: float = np.inf,
                        real: bool = False) -> np.ndarray:
        """Generates the signal.

        Args:
            fs: Sampling frequency in Hz.
            num_samples: Number of samples.
            frequency: Complex exponential frequency in Hz (f).
            phase: Complex exponential phase in rad (theta).
            amplitude: Complex exponential amplitude (A).
            alpha: Complex exponential damping factor (alpha).
            snr: SNR in dB.
            real: If true, generate only real samples.

        Returns:
            The samples of the complex sinusoid.

        The SNR is the signal-to-noise ratio at the initial amplitude of the
        signal.
        """
        if params is not None:
            frequency = params.frequency
            phase = params.phase
            amplitude = params.amplitude
            alpha = params.alpha

        if snr == np.inf:
            noise_amplitude = 0
        else:
            noise_amplitude = amplitude / constants.db2mag(snr)
        noise = GaussianNoise.generate_noise_samples(num_samples,
                                                     noise_amplitude, real)
        samples = amplitude * np.exp(1j * phase) * np.exp(
            (alpha + 1j * 2 * np.pi * frequency) * np.arange(num_samples) /
            fs) + noise
        if real:
            return np.real(samples)
        return samples
