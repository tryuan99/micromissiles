"""The HFSS optimizer implements a derivative-free optimizer to satisfy
constraints.
"""

import csv
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import scipy.optimize
from absl import logging

from simulation.hfss.constraint import Constraint, ConstraintEvaluation
from simulation.hfss.design_variable import FixedVariable, OptimizerVariable
from simulation.hfss.hfss_runner import HfssRunner
from simulation.hfss.s_parameter_constraint import SParameterData


@dataclass(frozen=True)
class HfssProjectConfig:
    """HFSS project/report execution configuration.

    Attributes:
        project_path: Path to the AEDT project.
        design_name: HFSS design name inside the project.
        report_name: Existing report to export, typically a rectangular plot
            containing S-parameter traces.
        output_dir: Directory for exported CSVs and history.
        aedt_version: Optional AEDT version passed to PyAEDT.
        analyze_setup_name: Optional setup name. If unset, `AnalyzeAll()` runs.
        cleanup_variations: Whether to delete solved variations after each run.
    """

    project_path: Path | str
    design_name: str
    report_name: str
    output_dir: Path | str
    aedt_version: str | None = None
    analyze_setup_name: str | None = None
    cleanup_variations: bool = False


@dataclass(frozen=True)
class OptimizationConfig:
    """Numerical optimizer configuration.

    Attributes:
        max_iterations: Maximum number of optimizer iterations.
        x_tolerance: Termination tolerance for design variable changes.
        function_tolerance: Termination tolerance for objective changes.
        initial_simplex_scale: Fraction of each variable's bounded span used to
            construct the initial Nelder-Mead simplex.
    """

    max_iterations: int = 100
    x_tolerance: float = 1e-3
    function_tolerance: float = 1e-3
    initial_simplex_scale: float = 0.05


@dataclass(frozen=True)
class HfssRunResult:
    """Result from one HFSS simulation run.

    Attributes:
        run_index: One-based run index within the optimizer session.
        values: Fixed and optimized design variable values used for this run.
        objective_value: Scalar optimizer objective. Positive values indicate
            the largest constraint violation while non-positive values are
            feasible.
        constraint_evaluations: Constraint evaluations computed from the data.
        data_csv: Path to the HFSS-exported CSV.
    """

    run_index: int
    values: dict[str, float]
    objective_value: float
    constraint_evaluations: tuple[ConstraintEvaluation, ...]
    data_csv: Path

    @property
    def feasible(self) -> bool:
        return all(
            evaluation.satisfied for evaluation in self.constraint_evaluations)


@dataclass(frozen=True)
class HfssOptimizationResult:
    """Final optimizer result.

    Attributes:
        optimal_values: Final design variable values.
        objective_value: Final scalar optimizer objective.
        feasible: Whether all final constraints are satisfied.
        final_run: HFSS run result associated with the final design values.
        scipy_result: Raw SciPy optimizer result.
        history_csv: Path to the optimizer history CSV.
    """

    optimal_values: dict[str, float]
    objective_value: float
    feasible: bool
    final_run: HfssRunResult
    scipy_result: scipy.optimize.OptimizeResult
    history_csv: Path


class HfssOptimizer(ABC):
    """Optimizes HFSS design variables against the given constraints.

    Attributes:
        project_config: HFSS project and execution configuration.
        fixed_variables: Fixed HFSS local variables.
        optimizer_variables: HFSS local variables to optimize.
        constraints: Constraints evaluated after each HFSS run.
        optimization_config: Numerical optimizer configuration.
        hfss_runner: HFSS simulation runner.
        runs: HFSS simulation runs evaluated during this optimizer session.
        output_dir: Absolute directory for exported CSVs and optimizer history.
        history_csv: CSV file containing the per-run optimizer history.
    """

    def __init__(
        self,
        project_config: HfssProjectConfig,
        fixed_variables: list[FixedVariable],
        optimizer_variables: list[OptimizerVariable],
        constraints: list[Constraint],
        optimization_config: OptimizationConfig | None = None,
    ) -> None:
        if not optimizer_variables:
            raise ValueError("At least one optimizer variable is required.")
        if not constraints:
            raise ValueError("At least one constraint is required.")

        self.project_config = project_config
        self.fixed_variables = fixed_variables
        self.optimizer_variables = optimizer_variables
        self.constraints = tuple(constraints)
        self.optimization_config = (optimization_config or OptimizationConfig())

        self.hfss_runner = HfssRunner(
            project_config.project_path,
            project_config.design_name,
            project_config.aedt_version,
        )
        self.runs: list[HfssRunResult] = []
        self.output_dir = Path(project_config.output_dir).expanduser().resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_csv = self.output_dir / "hfss_optimization_history.csv"

    def run(self) -> HfssOptimizationResult:
        """Runs bounded derivative-free optimization.

        Returns:
            The final HFSS optimizer result.
        """
        self._initialize_history()
        try:
            initial_values = np.asarray(
                [
                    variable.initial_value
                    for variable in self.optimizer_variables
                ],
                dtype=float,
            )
            bounds = scipy.optimize.Bounds(
                [variable.lower_bound for variable in self.optimizer_variables],
                [variable.upper_bound for variable in self.optimizer_variables],
            )
            options = {
                "maxiter": self.optimization_config.max_iterations,
                "xatol": self.optimization_config.x_tolerance,
                "fatol": self.optimization_config.function_tolerance,
                "initial_simplex": self._define_initial_simplex(initial_values),
                "disp": True,
            }
            result = scipy.optimize.minimize(
                self._evaluate_objective,
                initial_values,
                method="Nelder-Mead",
                bounds=bounds,
                options=options,
            )

            final_values = np.asarray(result.x, dtype=float)
            final_run = self._simulate(final_values)
            return HfssOptimizationResult(
                optimal_values=final_run.values,
                objective_value=final_run.objective_value,
                feasible=final_run.feasible,
                final_run=final_run,
                scipy_result=result,
                history_csv=self.history_csv,
            )
        finally:
            self.hfss_runner.close()

    def _evaluate_objective(self, x: np.ndarray) -> float:
        """Evaluates the scalar optimization objective for one set of design values.

        Args:
            x: Design variable values.

        Returns:
            The scalar optimization objective value.
        """
        run_result = self._simulate(x)
        logging.info(
            "Completed run %d with objective value %g, feasible %s, and values %s.",
            run_result.run_index,
            run_result.objective_value,
            run_result.feasible,
            run_result.values,
        )
        return run_result.objective_value

    def _simulate(self, x: np.ndarray) -> HfssRunResult:
        """Runs HFSS for one set of design values and evaluates all constraints.

        Args:
            x: Design variable values.

        Returns:
            The HFSS run result for this set of design values.
        """
        cached_run = self._find_run_with_values(x)
        if cached_run is not None:
            return cached_run

        values = {
            **{
                variable.name: float(value) for variable, value in zip(
                    self.optimizer_variables, x)
            },
            **{
                variable.name: variable.value for variable in self.fixed_variables
            }
        }
        run_index = len(self.runs) + 1
        run_dir = self.output_dir / f"run_{run_index:04d}"
        run_dir.mkdir(parents=True, exist_ok=False)

        logging.info("Starting run %d with values %s.", run_index, values)
        start_time = time.monotonic()
        data_csv = self.hfss_runner.run(
            self._format_design_values(values),
            report_name=self.project_config.report_name,
            output_dir=run_dir,
            analyze_setup_name=self.project_config.analyze_setup_name,
            cleanup_variations=self.project_config.cleanup_variations,
        )
        elapsed_seconds = time.monotonic() - start_time
        if not data_csv.exists():
            raise FileNotFoundError(
                f"HFSS completed but did not export {data_csv}.")

        data = self._parse_data(data_csv)
        evaluations = tuple(
            constraint.evaluate(data) for constraint in self.constraints)
        objective_value = max(
            evaluation.violation for evaluation in evaluations)
        run_result = HfssRunResult(
            run_index=run_index,
            values=values,
            objective_value=objective_value,
            constraint_evaluations=evaluations,
            data_csv=data_csv,
        )
        self.runs.append(run_result)
        self._append_history(run_result, elapsed_seconds)
        self._write_run_metadata(run_result, run_dir)
        return run_result

    def _format_design_values(self, values: dict[str, float]) -> dict[str, str]:
        """Formats the design variable values for HFSS.

        Args:
            values: Design variable values.

        Returns:
            A map from the HFSS local variable names to the formatted HFSS values.
        """
        return {
            variable.name: variable.format(values[variable.name])
            for variable in self.fixed_variables + self.optimizer_variables
        }

    @abstractmethod
    def _parse_data(self, data_csv: Path) -> Any:
        """Parses the data CSV file.

        Args:
            data_csv: Path to the CSV data.

        Returns:
            The parsed data.
        """

    def _find_run_with_values(self, x: np.ndarray) -> HfssRunResult | None:
        for run_result in self.runs:
            run_values = np.asarray(
                [
                    run_result.values[variable.name]
                    for variable in self.optimizer_variables
                ],
                dtype=float,
            )
            if np.allclose(run_values, x, rtol=0, atol=1e-12):
                return run_result
        return None

    def _define_initial_simplex(self, initial_values: np.ndarray) -> np.ndarray:
        """Defines the initial simplex.

        Args:
            initial_values: Initial design variable values.

        Returns:
            The initial simplex points.
        """
        settings = self.optimization_config
        simplex = [initial_values]
        for index, variable in enumerate(self.optimizer_variables):
            point = np.array(initial_values, copy=True)
            span = variable.upper_bound - variable.lower_bound
            step = max(span * settings.initial_simplex_scale,
                       settings.x_tolerance)
            point[index] = min(variable.upper_bound,
                               max(variable.lower_bound, point[index] + step))
            if point[index] == initial_values[index]:
                point[index] = min(
                    variable.upper_bound,
                    max(variable.lower_bound, point[index] - step),
                )
            simplex.append(point)
        return np.asarray(simplex, dtype=float)

    def _initialize_history(self) -> None:
        """Initializes the optimizer history."""
        with self.history_csv.open("w", newline="") as history_file:
            writer = csv.writer(history_file)
            writer.writerow([
                "Run index",
                "Objective value",
                "Feasible",
                "Elapsed seconds",
                *[variable.name for variable in self.optimizer_variables],
                *[
                    f"{constraint.name} constraint"
                    for constraint in self.constraints
                ],
            ])

    def _append_history(self, run_result: HfssRunResult,
                        elapsed_seconds: float) -> None:
        """Appends to the optimizer history.

        Args:
            run_result: HFSS run result.
            elapsed_seconds: HFSS run duration in seconds.
        """
        with self.history_csv.open("a", newline="") as history_file:
            writer = csv.writer(history_file)
            writer.writerow([
                run_result.run_index,
                run_result.objective_value,
                run_result.feasible,
                elapsed_seconds,
                *[
                    run_result.values[variable.name]
                    for variable in self.optimizer_variables
                ],
                *[
                    evaluation.violation
                    for evaluation in run_result.constraint_evaluations
                ],
            ])

    def _write_run_metadata(self, run_result: HfssRunResult,
                            run_dir: Path) -> None:
        """Writes run metadata next to the exported HFSS data.

        Args:
            run_result: HFSS run result.
            run_dir: Directory for this run's exported files.
        """
        metadata = {
            "run_index": run_result.run_index,
            "objective_value": run_result.objective_value,
            "feasible": run_result.feasible,
            "design_variables": self._format_design_values(run_result.values),
            "data_csv": run_result.data_csv.name,
        }
        with (run_dir / "metadata.json").open("w") as metadata_file:
            json.dump(metadata, metadata_file, indent=2)
            metadata_file.write("\n")


class SParameterHfssOptimizer(HfssOptimizer):
    """Optimizes HFSS design variables against S-parameter constraints."""

    def _parse_data(self, data_csv: Path) -> Any:
        """Parses the data CSV file.

        Args:
            data_csv: Path to the CSV data.

        Returns:
            The parsed data.
        """
        return SParameterData.from_csv(data_csv)
