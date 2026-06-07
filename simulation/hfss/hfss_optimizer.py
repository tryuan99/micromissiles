"""The HFSS optimizer implements a derivative-free optimizer to satisfy
constraints.
"""

import csv
import subprocess
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
from simulation.hfss.s_parameter_constraint import SParameterData


@dataclass(frozen=True)
class HfssProjectConfig:
    """HFSS project/report execution configuration.

    Attributes:
        hfss: Path to `ansysedt.exe` or the executable name if it is available
            on PATH.
        hfss_install_dir: Ansys Electronics Desktop installation directory for
            importing `ScriptEnv.py` inside the generated script.
        hfss_desktop_plugin_dir: Directory containing `ScriptEnv.py`.
        project_name: Already-open or loadable HFSS project name.
        design_name: HFSS design name inside the project.
        report_name: Existing report to export, typically a rectangular plot
            containing S-parameter traces.
        output_dir: Directory for generated scripts, exported CSVs, and
            history.
        run_script_flag: AEDT command-line flag used to run the script.
        extra_hfss_args: Additional AEDT command-line arguments.
        analyze_setup_name: Optional setup name. If unset, `AnalyzeAll()` runs.
        cleanup_variations: Whether to delete solved variations after each run.
    """

    hfss: str
    hfss_install_dir: str
    hfss_desktop_plugin_dir: str
    project_name: str
    design_name: str
    report_name: str
    output_dir: str | Path
    run_script_flag: str = "-RunScriptAndExit"
    extra_hfss_args: tuple[str, ...] = ()
    analyze_setup_name: str | None = None
    cleanup_variations: bool = False


@dataclass(frozen=True)
class OptimizationConfig:
    """Numerical optimizer configuration.

    Attributes:
        max_iterations: Maximum number of optimizer iterations.
        max_function_evaluations: Maximum number of HFSS objective evaluations.
        x_tolerance: Termination tolerance for design variable changes.
        function_tolerance: Termination tolerance for objective changes.
        initial_simplex_scale: Fraction of each variable's bounded span used to
            construct the initial Nelder-Mead simplex.
    """

    max_iterations: int = 100
    max_function_evaluations: int = 200
    x_tolerance: float = 1e-3
    function_tolerance: float = 1e-3
    initial_simplex_scale: float = 0.05


@dataclass(frozen=True)
class HfssRunResult:
    """Result from one HFSS simulation run.

    Attributes:
        run_index: One-based run index within the optimizer session.
        values: Design variable values used for this run.
        data: Path to the HFSS-exported CSV.
        script_path: Path to the generated HFSS automation script.
        constraint_evaluations: Constraint evaluations computed from the data.
        objective_value: Scalar optimizer objective. Positive values indicate
            the largest constraint violation while non-positive values are
            feasible.
    """

    run_index: int
    values: dict[str, float]
    data: Path
    script_path: Path
    constraint_evaluations: tuple[ConstraintEvaluation, ...]
    objective_value: float

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
        output_dir: Absolute directory for generated scripts, exported
            CSVs, and optimizer history.
        history_csv: CSV file containing the per-run optimizer history.
        runs: HFSS simulation runs evaluated during this optimizer session.
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
        self.output_dir = Path(project_config.output_dir).expanduser().resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_csv = self.output_dir / "hfss_optimization_history.csv"
        self.runs: list[HfssRunResult] = []

    def run(self) -> HfssOptimizationResult:
        """Runs bounded derivative-free optimization.

        Returns:
            The final HFSS optimizer result.
        """
        self._initialize_history()
        initial_values = np.asarray(
            [variable.initial_value for variable in self.optimizer_variables],
            dtype=float,
        )
        bounds = scipy.optimize.Bounds(
            [variable.lower_bound for variable in self.optimizer_variables],
            [variable.upper_bound for variable in self.optimizer_variables],
        )

        optimization_config = self.optimization_config
        result = scipy.optimize.minimize(
            self._objective,
            initial_values,
            method="Nelder-Mead",
            bounds=bounds,
            options={
                "maxiter": optimization_config.max_iterations,
                "maxfev": optimization_config.max_function_evaluations,
                "xatol": optimization_config.x_tolerance,
                "fatol": optimization_config.function_tolerance,
                "initial_simplex": self._initial_simplex(initial_values),
                "disp": True,
            },
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

    def _objective(self, x: np.ndarray) -> float:
        """Evaluates the scalar optimization objective for one set of design values.

        Args:
            x: Design variable values.

        Returns:
            The scalar optimization objective value.
        """
        run_result = self._simulate(x)
        logging.info(
            "Run %d: objective %.6g feasible=%s values=%s",
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
        run_directory = self.output_dir / f"run_{run_index:04d}"
        run_directory.mkdir(parents=True, exist_ok=False)
        data_csv = run_directory / "data.csv"
        script_path = run_directory / "run_hfss.py"

        script_path.write_text(
            self._render_hfss_script(values, data_csv),
            encoding="utf-8",
        )

        start_time = time.monotonic()
        command = [
            self.project_config.hfss,
            *self.project_config.extra_hfss_args,
            self.project_config.run_script_flag,
            str(script_path),
        ]
        completed_process = subprocess.run(
            command,
            cwd=run_directory,
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed_seconds = time.monotonic() - start_time
        if completed_process.returncode != 0:
            logging.error("Command: %s", command)
            logging.error("stdout: %s", completed_process.stdout)
            logging.error("stderr: %s", completed_process.stderr)
            raise RuntimeError(
                f"HFSS simulation failed for {values} after {elapsed_seconds:.1f} seconds."
            )
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
            data=data_csv,
            script_path=script_path,
            constraint_evaluations=evaluations,
            objective_value=objective_value,
        )
        self.runs.append(run_result)
        self._append_history(run_result, elapsed_seconds)
        return run_result

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

    def _initial_simplex(self, initial_values: np.ndarray) -> np.ndarray:
        """Defines the initial simplex.

        Args:
            initial_values: Initial design variable values.

        Returns:
            Initial simplex points.
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
                    evaluation.value
                    for evaluation in run_result.constraint_evaluations
                ],
            ])

    def _render_hfss_script(
        self,
        values: dict[str, float],
        data_csv: Path,
    ) -> str:
        """Renders the HFSS automation script.

        Args:
            values: Design variable values.
            data_csv: Path to the CSV data.

        Returns:
            The HFSS automation script.
        """
        variable_lines = [
            f"set_local_variable({variable.name!r}, "
            f"{variable.format(values[variable.name])!r})"
            for variable in self.fixed_variables + self.optimizer_variables
        ]

        analyze_line = "oDesign.AnalyzeAll()"
        if self.project_config.analyze_setup_name:
            analyze_line = (
                f"oDesign.Analyze({self.project_config.analyze_setup_name!r})")

        cleanup_line = ""
        if self.project_config.cleanup_variations:
            cleanup_line = 'oDesign.DeleteFullVariation("All", False)'

        return "\n".join([
            "import sys",
            f"sys.path.append({self.project_config.hfss_install_dir!r})",
            f"sys.path.append({self.project_config.hfss_desktop_plugin_dir!r})",
            "import ScriptEnv",
            "",
            'ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")',
            "oDesktop.RestoreWindow()",
            f"oProject = oDesktop.SetActiveProject("
            f"{self.project_config.project_name!r})",
            f"oDesign = oProject.SetActiveDesign("
            f"{self.project_config.design_name!r})",
            "",
            "def set_local_variable(name, value):",
            "    oDesign.ChangeProperty(",
            "        [",
            '            "NAME:AllTabs",',
            "            [",
            '                "NAME:LocalVariableTab",',
            '                ["NAME:PropServers", "LocalVariables"],',
            "                [",
            '                    "NAME:ChangedProps",',
            '                    ["NAME:" + name, "Value:=", value],',
            "                ],",
            "            ],",
            "        ]",
            "    )",
            "",
            *variable_lines,
            "",
            "oProject.Save()",
            analyze_line,
            'oModule = oDesign.GetModule("ReportSetup")',
            f"oModule.ExportToFile({self.project_config.report_name!r}, "
            f"{str(data_csv)!r}, False)",
            cleanup_line,
            "",
        ])


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
