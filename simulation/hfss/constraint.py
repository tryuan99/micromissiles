"""The constraint is an interface for simulation constraints. When evaluated,
the constraint returns a constraint evaluation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Constraint(ABC):
    """Interface for a constraint over simulation data."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Constraint name."""

    @abstractmethod
    def evaluate(self, data: Any) -> ConstraintEvaluation:
        """Evaluates this constraint against the data."""


class ConstraintEvaluation(ABC):
    """Interface for constraint evaluation results."""

    @property
    @abstractmethod
    def satisfied(self) -> bool:
        """Whether the evaluated constraint is satisfied."""
