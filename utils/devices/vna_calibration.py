"""Interface for a VNA calibration."""

from abc import ABC, abstractmethod
from enum import StrEnum

import numpy as np


class ErrorTerm(StrEnum):
    """Error term enumeration of a full two-port calibration."""
    DIRECTIVITY = "Directivity"
    REFLECTION_TRACKING = "ReflectionTracking"
    SOURCE_MATCH = "SourceMatch"
    CROSSTALK = "Crosstalk"
    TRANSMISSION_TRACKING = "TransmissionTracking"
    LOAD_MATCH = "LoadMatch"


class VnaCalibration(ABC):
    """Interface for a VNA calibration with frequency-dependent error terms.

    The calibration follows the 12-term error model of a two-port VNA.
    """

    @abstractmethod
    def error_term(self, error_term: ErrorTerm, frequencies: np.ndarray,
                   source_port: int, receiver_port: int) -> np.ndarray:
        """Evaluates an error term at the given frequencies.

        Args:
            error_term: Error term.
            frequencies: Frequencies in Hz.
            source_port: Source port.
            receiver_port: Receiver port.

        Returns:
            The complex error term at each frequency.
        """

    def correct_coefficient(
        self,
        frequencies: float | np.ndarray,
        measured: np.ndarray,
        source_port: int,
        receiver_port: int,
    ) -> np.ndarray:
        """Corrects a single raw S-parameter.

        A reflection coefficient, whose source and receiver ports coincide, is
        corrected with the one-port error model. A transmission coefficient is
        only corrected for the crosstalk and the transmission tracking, so the
        mismatch at both ports is neglected.

        Args:
            frequencies: Frequencies in Hz broadcast against the measurement.
            measured: Raw S-parameter.
            source_port: Source port.
            receiver_port: Receiver port.

        Returns:
            The corrected S-parameter.
        """
        if source_port == receiver_port:
            return self._correct_reflection_coefficient(frequencies, measured,
                                                        source_port)
        return self._correct_transmission_coefficient(frequencies, measured,
                                                      source_port,
                                                      receiver_port)

    def correct_two_port(
        self,
        frequencies: float | np.ndarray,
        measured: np.ndarray,
    ) -> np.ndarray:
        """Corrects raw two-port S-parameters with the 12-term error model.

        Args:
            frequencies: Frequencies in Hz broadcast against the measurement.
            measured: Raw S-parameters with shape (..., 2, 2), where entry
                [..., i, j] is the raw S-parameter from port j + 1 to port
                i + 1.

        Returns:
            The corrected S-parameters with the same shape as the measurement.
        """
        a = self._normalize_reflection(frequencies, measured[..., 0, 0], 1)
        b = self._correct_transmission_coefficient(frequencies,
                                                   measured[..., 1, 0], 1, 2)
        c = self._correct_transmission_coefficient(frequencies,
                                                   measured[..., 0, 1], 2, 1)
        d = self._normalize_reflection(frequencies, measured[..., 1, 1], 2)
        source_match_1 = self._evaluate(ErrorTerm.SOURCE_MATCH, frequencies, 1,
                                        1)
        source_match_2 = self._evaluate(ErrorTerm.SOURCE_MATCH, frequencies, 2,
                                        2)
        load_match_2 = self._evaluate(ErrorTerm.LOAD_MATCH, frequencies, 1, 2)
        load_match_1 = self._evaluate(ErrorTerm.LOAD_MATCH, frequencies, 2, 1)

        denominator = ((1 + a * source_match_1) * (1 + d * source_match_2) -
                       b * c * load_match_2 * load_match_1)
        s11 = (a *
               (1 + d * source_match_2) - load_match_2 * b * c) / denominator
        s21 = b * (1 + d * (source_match_2 - load_match_2)) / denominator
        s12 = c * (1 + a * (source_match_1 - load_match_1)) / denominator
        s22 = (d *
               (1 + a * source_match_1) - load_match_1 * b * c) / denominator
        return np.stack(
            (np.stack((s11, s12), axis=-1), np.stack((s21, s22), axis=-1)),
            axis=-2,
        )

    def _correct_reflection_coefficient(
        self,
        frequencies: float | np.ndarray,
        measured: np.ndarray,
        port: int,
    ) -> np.ndarray:
        """Corrects a raw reflection coefficient with the one-port error model.

        Args:
            frequencies: Frequencies in Hz broadcast against the measurement.
            measured: Raw reflection coefficient.
            port: Port.

        Returns:
            The corrected reflection coefficient.
        """
        normalized = self._normalize_reflection(frequencies, measured, port)
        source_match = self._evaluate(
            ErrorTerm.SOURCE_MATCH,
            frequencies,
            port,
            port,
        )
        return normalized / (1 + source_match * normalized)

    def _correct_transmission_coefficient(
        self,
        frequencies: float | np.ndarray,
        measured: np.ndarray,
        source_port: int,
        receiver_port: int,
    ) -> np.ndarray:
        """Corrects a raw transmission coefficient without the port mismatch.

        Args:
            frequencies: Frequencies in Hz broadcast against the measurement.
            measured: Raw transmission coefficient.
            source_port: Source port.
            receiver_port: Receiver port.

        Returns:
            The transmission coefficient corrected for the crosstalk and the
            transmission tracking.
        """
        crosstalk = self._evaluate(
            ErrorTerm.CROSSTALK,
            frequencies,
            source_port,
            receiver_port,
        )
        tracking = self._evaluate(
            ErrorTerm.TRANSMISSION_TRACKING,
            frequencies,
            source_port,
            receiver_port,
        )
        return (measured - crosstalk) / tracking

    def _normalize_reflection(
        self,
        frequencies: float | np.ndarray,
        measured: np.ndarray,
        port: int,
    ) -> np.ndarray:
        """Removes the directivity and the reflection tracking of a port.

        Args:
            frequencies: Frequencies in Hz broadcast against the measurement.
            measured: Raw reflection coefficient.
            port: Port.

        Returns:
            The reflection coefficient before the source match correction.
        """
        directivity = self._evaluate(
            ErrorTerm.DIRECTIVITY,
            frequencies,
            port,
            port,
        )
        tracking = self._evaluate(
            ErrorTerm.REFLECTION_TRACKING,
            frequencies,
            port,
            port,
        )
        return (measured - directivity) / tracking

    def _evaluate(
        self,
        error_term: ErrorTerm,
        frequencies: float | np.ndarray,
        source_port: int,
        receiver_port: int,
    ) -> np.ndarray:
        """Evaluates an error term with the shape of the frequencies.

        Args:
            error_term: Error term.
            frequencies: Frequencies in Hz with any shape.
            source_port: Source port.
            receiver_port: Receiver port.

        Returns:
            The complex error term with the same shape as the frequencies.
        """
        shape = np.shape(frequencies)
        return self.error_term(
            error_term,
            np.ravel(frequencies),
            source_port,
            receiver_port,
        ).reshape(shape)
