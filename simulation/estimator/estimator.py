"""The estimator is an interface for an estimator that, given some
samples of a signal, estimates some parameters in the signal.
"""

from abc import ABC

import numpy as np

from simulation.radar.components.samples import Samples


class Estimator(Samples, ABC):
    """Interface for an estimator."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples)
        self.fs = fs


class Estimator1D(Estimator):
    """Interface for a 1D estimator."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

        if self.ndim != 1:
            raise ValueError("Only signals of dimension 1 are supported.")
