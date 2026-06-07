"""HFSS local design variables for optimization and fixed constants."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DesignVariable(ABC):
    """An HFSS local design variable.

    Attributes:
        name: HFSS local variable name.
        initial_value: Initial numeric value.
    """

    name: str

    def format(self, value: float) -> str:
        """Formats the given numeric value."""
        return f"{value:.12g}{self.unit}"


@dataclass(frozen=True)
class FixedVariable(DesignVariable):
    """An HFSS local design variable held constant at its initial value.

    Attributes:
        name: HFSS local variable name.
        initial_value: Constant numeric value.
        unit: HFSS unit suffix. Use an empty string for unitless variables.
    """

    value: float
    unit: str = ""


@dataclass(frozen=True)
class OptimizerVariable(DesignVariable):
    """A bounded HFSS local design variable optimized numerically.

    Attributes:
        name: HFSS local variable name.
        initial_value: Initial numeric value.
        lower_bound: Lower numeric bound.
        upper_bound: Upper numeric bound.
        unit: HFSS unit suffix. Use an empty string for unitless variables.
    """

    initial_value: float
    lower_bound: float
    upper_bound: float
    unit: str = ""
