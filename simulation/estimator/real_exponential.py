"""The real exponential represents the samples of a real exponential given by
A * exp(alpha * t).
"""

import numpy as np

from simulation.estimator.complex_exponential import (ComplexExponential,
                                                      ComplexExponentialParams)


class RealExponentialParams(ComplexExponentialParams):
    """Real exponential parameters."""

    def __init__(self, amplitude: float = 1, alpha: float = 0) -> None:
        super().__init__(frequency=0, phase=0, amplitude=amplitude, alpha=alpha)


class RealExponential(ComplexExponential):
    """Real exponential of the form A * exp(alpha * t).
    """

    def __init__(self,
                 fs: float,
                 num_samples: int,
                 amplitude: float = 1,
                 alpha: float = 0,
                 params: RealExponentialParams = None,
                 snr: float = np.inf) -> None:
        super().__init__(fs=fs,
                         num_samples=num_samples,
                         frequency=0,
                         phase=0,
                         amplitude=amplitude,
                         alpha=alpha,
                         params=params,
                         snr=snr)

    @staticmethod
    def generate_signal(fs: float,
                        num_samples: int,
                        frequency: float = 0,
                        phase: float = 0,
                        amplitude: float = 1,
                        alpha: float = 0,
                        params: ComplexExponentialParams = None,
                        snr: float = np.inf) -> np.ndarray:
        """Generates the signal.

        Args:
            fs: Sampling frequency in Hz.
            num_samples: Number of samples.
            amplitude: Complex exponential amplitude (A).
            alpha: Complex exponential damping factor (alpha).
            snr: SNR in dB.

        Returns:
            The samples of the real sinusoid.

        The SNR is the signal-to-noise ratio at the initial amplitude of the
        signal.
        """
        return super(RealExponential,
                     RealExponential).generate_signal(fs=fs,
                                                      num_samples=num_samples,
                                                      frequency=0,
                                                      phase=0,
                                                      amplitude=amplitude,
                                                      alpha=alpha,
                                                      params=params,
                                                      snr=snr,
                                                      real=True)
