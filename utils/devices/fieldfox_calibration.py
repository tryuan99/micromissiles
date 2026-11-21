"""User calibration of a Keysight FieldFox VNA applied to raw S-parameter
measurements.

A FieldFox state file (.sta) is a ZIP archive whose CalsetLibrary entry holds
the user calibration. The CalsetLibrary is a little-endian binary file with the
following layout:
- A header with the calibration type, the connectors, and the cal kits.
- The cardinal frequencies as a list of segments. A linear segment consists of
  (num_points, start, stop), and a list segment consists of num_points explicit
  frequencies.
- The error terms, each with the receiver and the source port, its name, and
  num_points complex values stored as pairs of float32.
Strings are prefixed by their length in a single byte.
"""

import io
import struct
import zipfile
from enum import IntEnum

import numpy as np

from utils.devices.vna_calibration import ErrorTerm, VnaCalibration


class FrequencySegmentKind(IntEnum):
    """Frequency segment kind enumeration of a FieldFox calset."""
    LINEAR = 1
    LIST = 3


class FieldFoxCalibration(VnaCalibration):
    """Full two-port user calibration of a Keysight FieldFox VNA.

    Attributes:
        frequencies: Frequencies in Hz.
        error_terms: Dictionary mapping (error term, source port, receiver port)
            to the complex error term at each cardinal frequency.
    """

    HEADER_OFFSET = 13
    TIMESTAMP_BYTES = 8
    CALSET_ENTRY = "CalsetLibrary"

    def __init__(self, path: str) -> None:
        """Loads the calibration.

        Args:
            path: FieldFox state file (.sta).

        Raises:
            ValueError: If the file cannot be parsed.
        """
        with zipfile.ZipFile(path) as archive:
            stream = io.BytesIO(archive.read(self.CALSET_ENTRY))
        self._read_header(stream)
        self.frequencies = self._read_frequencies(stream)
        self.error_terms = self._read_error_terms(stream)

    def error_term(self, error_term: ErrorTerm, frequencies: np.ndarray,
                   source_port: int, receiver_port: int) -> np.ndarray:
        """Interpolates an error term onto the given frequencies.

        Args:
            error_term: Error term.
            frequencies: Frequencies in Hz.
            source_port: Source port.
            receiver_port: Receiver port.

        Returns:
            The complex error term at each frequency.

        Raises:
            ValueError: If a frequency lies outside the calibrated range.
        """
        frequencies = np.asarray(frequencies, dtype=np.float64)
        if (np.min(frequencies) < np.min(self.frequencies) or
                np.max(frequencies) > np.max(self.frequencies)):
            raise ValueError(
                "The frequencies lie outside the calibrated range.")
        values = self.error_terms[(error_term, source_port, receiver_port)]
        return (np.interp(frequencies, self.frequencies, values.real) +
                1j * np.interp(frequencies, self.frequencies, values.imag))

    def _read_header(self, stream: io.BytesIO) -> None:
        """Skips the calibration type, the connectors, and the cal kits.

        Args:
            stream: Binary stream at the start of the calset.
        """
        stream.seek(self.HEADER_OFFSET, io.SEEK_CUR)
        self._read_string(stream)
        stream.seek(self.TIMESTAMP_BYTES, io.SEEK_CUR)
        for _ in range(2):
            for _ in range(self._read_int32(stream)):
                self._read_string(stream)
        self._read_int32(stream)

    def _read_frequencies(self, stream: io.BytesIO) -> np.ndarray:
        """Reads the cardinal frequencies.

        Args:
            stream: Binary stream at the frequency segments.

        Returns:
            The cardinal frequencies in Hz.

        Raises:
            ValueError: If a segment kind is unknown.
        """
        segments = []
        for _ in range(self._read_int32(stream)):
            kind = self._read_int32(stream)
            num_points = self._read_int32(stream)
            match kind:
                case FrequencySegmentKind.LINEAR:
                    segments.append(
                        np.linspace(
                            self._read_float64(stream),
                            self._read_float64(stream),
                            num_points,
                        ))
                case FrequencySegmentKind.LIST:
                    segments.append(
                        np.array([
                            self._read_float64(stream)
                            for _ in range(num_points)
                        ]))
                case _:
                    raise ValueError(f"Unknown frequency segment kind {kind}.")
        return np.concatenate(segments)

    def _read_error_terms(
        self,
        stream: io.BytesIO,
    ) -> dict[tuple[ErrorTerm, int, int], np.ndarray]:
        """Reads the error terms.

        Args:
            stream: Binary stream at the error terms.

        Returns:
            A dictionary mapping (error term, source port, receiver port) to the
            complex error term at each cardinal frequency.

        Raises:
            ValueError: If an error term does not match the frequencies.
        """
        error_terms = {}
        for _ in range(self._read_int32(stream)):
            self._read_int32(stream)
            self._read_int32(stream)
            receiver_port = self._read_int32(stream)
            source_port = self._read_int32(stream)
            error_term = ErrorTerm(self._read_string(stream))
            self._read_string(stream)
            num_points = self._read_int32(stream)
            if num_points != len(self.frequencies):
                raise ValueError(f"The error term {error_term} has "
                                 f"{num_points} points, but there are "
                                 f"{len(self.frequencies)} frequencies.")
            error_terms[(error_term, source_port,
                         receiver_port)] = self._read_complex64(
                             stream,
                             num_points,
                         )
        return error_terms

    @staticmethod
    def _read_int32(stream: io.BytesIO) -> int:
        """Reads a little-endian 32-bit signed integer.

        Args:
            stream: Binary stream.

        Returns:
            The integer.
        """
        (value,) = struct.unpack("<i", stream.read(4))
        return value

    @staticmethod
    def _read_float64(stream: io.BytesIO) -> float:
        """Reads a little-endian 64-bit floating-point number.

        Args:
            stream: Binary stream.

        Returns:
            The floating-point number.
        """
        (value,) = struct.unpack("<d", stream.read(8))
        return value

    @staticmethod
    def _read_string(stream: io.BytesIO) -> str:
        """Reads a string prefixed by its length in a single byte.

        Args:
            stream: Binary stream.

        Returns:
            The string.
        """
        return stream.read(stream.read(1)[0]).decode()

    @staticmethod
    def _read_complex64(stream: io.BytesIO, count: int) -> np.ndarray:
        """Reads complex numbers stored as pairs of little-endian 32-bit floats.

        Args:
            stream: Binary stream.
            count: Number of complex numbers.

        Returns:
            The complex numbers with shape (count,).
        """
        values = np.frombuffer(stream.read(8 * count), "<f4")
        return values[0::2] + 1j * values[1::2]
