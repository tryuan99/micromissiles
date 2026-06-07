"""S-parameter constraints for HFSS optimization."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from simulation.hfss.constraint import Constraint, ConstraintEvaluation

# S-parameter regex pattern.
S_PARAMETER_PATTERN = re.compile(r"S\s*\(\s*(?P<i>[12])\s*,\s*(?P<j>[12])\s*\)",
                                 re.IGNORECASE)
# Numeric regex pattern.
NUMERIC_PATTERN = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
# Supported S-parameters.
SUPPORTED_S_PARAMETERS = frozenset({"S11", "S12", "S21", "S22"})


@dataclass(frozen=True)
class SParameterTrace:
    """A single S-parameter trace exported from HFSS.

    Attributes:
        frequency_hz: Frequency samples in Hz.
        values_db: S-parameter values in dB at each frequency sample.
    """

    frequency_hz: np.ndarray
    values_db: np.ndarray

    def values_between(
            self, lower_frequency_hz: float,
            upper_frequency_hz: float) -> tuple[np.ndarray, np.ndarray]:
        """Returns frequency and value samples inside the inclusive band."""
        mask = ((self.frequency_hz >= lower_frequency_hz) &
                (self.frequency_hz <= upper_frequency_hz))
        if not np.any(mask):
            raise ValueError(
                "No S-parameter samples exist inside the requested interval "
                f"[{lower_frequency_hz}, {upper_frequency_hz}] Hz.")
        return self.frequency_hz[mask], self.values_db[mask]


class SParameterData:
    """HFSS-exported S-parameter traces keyed by S11/S21/S12/S22.

    Attributes:
        traces: Map from S-parameter to its corresponding trace.
    """

    def __init__(self, traces: dict[str, SParameterTrace]) -> None:
        if not traces:
            raise ValueError("At least one S-parameter trace is required.")

        self.traces = dict(traces)

    @classmethod
    def from_csv(cls, path: Path | str) -> "SParameterData":
        """Loads S-parameter traces from an HFSS report CSV.

        The parser accepts typical HFSS report exports with a frequency column
        and one or more dB S-parameter columns, for example,
        `Frequency [GHz], dB(S(1,1)) [], dB(S(2,1)) []`.

        Args:
            cls: S-parameter data class.
            path: Path to the CSV file.

        Returns:
            The S-parameter data.
        """
        path = Path(path)
        raw_csv = cls._read_raw_csv(path)
        if raw_csv.empty:
            raise ValueError(f"{path} is empty.")

        header_index = cls._find_header_index(raw_csv)
        headers = [
            "" if pd.isna(value) else str(value).strip()
            for value in raw_csv.iloc[header_index].to_list()
        ]
        frequency_column = cls._find_frequency_column(headers)
        frequency_scale = cls._frequency_scale_from_header(
            headers[frequency_column])
        trace_columns = cls._find_s_parameter_columns(headers)

        if not trace_columns:
            raise ValueError(
                f"{path} does not contain any supported S-parameter columns.")

        trace_parameters = list(trace_columns.values())
        if len(trace_parameters) != len(set(trace_parameters)):
            raise ValueError(f"{path} contains duplicate S-parameter columns.")

        data = cls._read_data_rows(
            path,
            header_index,
            [frequency_column, *trace_columns],
        )
        if data.empty:
            raise ValueError(f"{path} does not contain numeric data rows.")

        frequency_array = (cls._numeric_array(data[frequency_column], path,
                                              headers[frequency_column]) *
                           frequency_scale)
        traces = {
            parameter:
                SParameterTrace(
                    frequency_array,
                    cls._numeric_array(data[column], path, headers[column]),
                ) for column, parameter in trace_columns.items()
        }
        return cls(traces)

    def trace(self, s_parameter: str) -> SParameterTrace:
        """Returns the trace for the requested S-parameter.

        Args:
            s_parameter: S-parameter.

        Returns:
            The trace corresponding to the given S-parameter.
        """
        normalized_parameter = self.normalize_s_parameter(s_parameter)
        if normalized_parameter not in self.traces:
            raise ValueError(
                f"{normalized_parameter} is not present in exported data. "
                f"Available traces: {sorted(self.traces)}.")
        return self.traces[normalized_parameter]

    @staticmethod
    def normalize_s_parameter(s_parameter: str) -> str:
        """Normalizes an S-parameter name and validates support.

        Args:
            s_parameter: S-parameter.

        Returns:
            The normalized S-parameter name.
        """
        normalized_parameter = re.sub(r"[\s(),]", "", s_parameter.upper())
        if normalized_parameter not in SUPPORTED_S_PARAMETERS:
            raise ValueError(
                f"Unsupported S-parameter {s_parameter!r}. Expected one of "
                f"{sorted(SUPPORTED_S_PARAMETERS)}.")
        return normalized_parameter

    @staticmethod
    def _read_raw_csv(path: Path) -> pd.DataFrame:
        """Reads a raw CSV file.

        Args:
            path: Path to the CSV file.

        Returns:
            A dataframe containing the CSV data.

        Raises:
            ValueError: If the CSV file is empty.
        """
        try:
            return pd.read_csv(
                path,
                header=None,
                dtype=str,
            )
        except pd.errors.EmptyDataError as error:
            raise ValueError(f"{path} is empty.") from error

    @staticmethod
    def _read_data_rows(
        path: Path,
        header_index: int,
        columns: list[int],
    ) -> pd.DataFrame:
        """Reads the data rows from the CSV file.

        Args:
            path: Path to the CSV file.

        Returns:
            A dataframe containing the non-blank rows.
        """
        data = pd.read_csv(
            path,
            header=None,
            skiprows=header_index + 1,
            usecols=columns,
            dtype=str,
        )
        return data.loc[~SParameterData._blank_rows(data)]

    @staticmethod
    def _find_header_index(rows: pd.DataFrame) -> int:
        """Finds the header row.
        
        Args:
            rows: Dataframe containing the CSV data.
        
        Returns:
            The row index of the header row.
        """
        for row_index, row in rows.iterrows():
            headers = [
                "" if pd.isna(value) else str(value).strip()
                for value in row.to_list()
            ]
            if SParameterData._find_s_parameter_columns(headers):
                return row_index
        raise ValueError("Could not find an HFSS S-parameter CSV header row.")

    @staticmethod
    def _find_frequency_column(headers: list[str]) -> int:
        """Finds the frequency column.
        
        Args:
            headers: List of header names.
        
        Returns:
            The index of the frequency column.
        """
        for column_index, header in enumerate(headers):
            if "freq" in header.lower():
                return column_index
        return 0

    @staticmethod
    def _blank_rows(data: pd.DataFrame) -> pd.Series:
        """Finds the blank rows.
        
        Args:
            data: Dataframe containing the CSV data.
        
        Returns:
            A mask whether the corresponding row is blank.
        """
        stripped_data = data.fillna("").astype(str).map(str.strip)
        return stripped_data.eq("").all(axis=1)

    @staticmethod
    def _find_s_parameter_columns(headers: list[str]) -> dict[int, str]:
        """Finds the S-parameter columns.
        
        Args:
            headers: List of header names.
        
        Returns:
            A map from the column index to the S-parameter.
        """
        trace_columns = {}
        for column_index, header in enumerate(headers):
            parameter_match = S_PARAMETER_PATTERN.search(header)
            if parameter_match is None:
                normalized_header = header.upper().replace(" ", "")
                for parameter in SUPPORTED_S_PARAMETERS:
                    if parameter in normalized_header:
                        trace_columns[column_index] = parameter
                        break
                continue

            trace_columns[column_index] = (
                f"S{parameter_match.group('i')}{parameter_match.group('j')}")
        return trace_columns

    @staticmethod
    def _frequency_scale_from_header(header: str) -> float:
        """Parses the frequency scale from the header.
        
        Args:
            header: Header name.
        
        Returns:
            The frequency scale for the header.
        """
        lower_header = header.lower()
        if "ghz" in lower_header:
            return 1e9
        if "mhz" in lower_header:
            return 1e6
        if "khz" in lower_header:
            return 1e3
        return 1

    @staticmethod
    def _numeric_array(
        values: pd.Series,
        path: Path,
        column_name: str,
    ) -> np.ndarray:
        """Parses a numeric array from a column.
        
        Args:
            values: Series values.
            path: Path to the CSV data.
            column_name: Column name.
        
        Returns:
            A numeric array.
        """
        numeric_text = values.fillna("").astype(str).str.extract(
            NUMERIC_PATTERN,
            expand=False,
        )
        numeric_values = pd.to_numeric(numeric_text, errors="coerce")
        if numeric_values.isna().any():
            raise ValueError(
                f"{path} column {column_name!r} contains invalid numeric "
                "S-parameter data.")

        array = numeric_values.to_numpy(dtype=float)
        if not np.isfinite(array).all():
            raise ValueError(f"{path} contains non-finite S-parameter data.")
        return array


@dataclass(frozen=True)
class SParameterConstraint(Constraint):
    """Base class for constraints over HFSS-exported S-parameters.

    Attributes:
        s-parameter: S-parameter.
        lower_frequency_hz: Lower frequency bound in Hz.
        upper_frequency_hz: Upper frequency bound in Hz.
    """

    s_parameter: str
    lower_frequency_hz: float
    upper_frequency_hz: float


@dataclass(frozen=True)
class SParameterUpperBoundConstraint(SParameterConstraint):
    """Requires an S-parameter to stay below a dB limit in a frequency band.

    Attributes:
        upper_bound_db: Upper bound in dB.
    """

    upper_bound_db: float

    @property
    def name(self) -> str:
        parameter = SParameterData.normalize_s_parameter(self.s_parameter)
        return (f"{parameter} <= {self.upper_bound_db:g} dB from "
                f"{self.lower_frequency_hz:g} Hz to "
                f"{self.upper_frequency_hz:g} Hz")

    def evaluate(self, data: SParameterData) -> SParameterConstraintEvaluation:
        trace = data.trace(self.s_parameter)
        frequencies_hz, values_db = trace.values_between(
            self.lower_frequency_hz,
            self.upper_frequency_hz,
        )
        violations = values_db - self.upper_bound_db
        worst_index = int(np.argmax(violations))
        return SParameterConstraintEvaluation(
            name=self.name,
            violation=float(violations[worst_index]),
            worst_frequency_hz=float(frequencies_hz[worst_index]),
            worst_value_db=float(values_db[worst_index]),
            limit_db=self.upper_bound_db,
        )


@dataclass(frozen=True)
class SParameterLowerBoundConstraint(SParameterConstraint):
    """Requires an S-parameter to stay above a dB limit in a frequency band.

    Attributes:
        lower_bound_db: Lower bound in dB.
    """

    lower_bound_db: float

    @property
    def name(self) -> str:
        parameter = SParameterData.normalize_s_parameter(self.s_parameter)
        return (f"{parameter} >= {self.lower_bound_db:g} dB from "
                f"{self.lower_frequency_hz:g} Hz to "
                f"{self.upper_frequency_hz:g} Hz")

    def evaluate(self, data: SParameterData) -> SParameterConstraintEvaluation:
        trace = data.trace(self.s_parameter)
        frequencies_hz, values_db = trace.values_between(
            self.lower_frequency_hz,
            self.upper_frequency_hz,
        )
        violations = self.lower_bound_db - values_db
        worst_index = int(np.argmax(violations))
        return SParameterConstraintEvaluation(
            name=self.name,
            violation=float(violations[worst_index]),
            worst_frequency_hz=float(frequencies_hz[worst_index]),
            worst_value_db=float(values_db[worst_index]),
            limit_db=self.lower_bound_db,
        )


@dataclass(frozen=True)
class SParameterConstraintEvaluation(ConstraintEvaluation):
    """Result from evaluating one S-parameter constraint."""

    name: str
    violation: float
    worst_frequency_hz: float
    worst_value_db: float
    limit_db: float

    @property
    def satisfied(self) -> bool:
        return self.violation <= 0
