"""Optimizes the HFSS design variables for a grounded coplanar waveguide."""

from absl import app, flags, logging

from simulation.hfss import constants
from simulation.hfss.design_variable import FixedVariable, OptimizerVariable
from simulation.hfss.hfss_optimizer import (HfssProjectConfig,
                                            OptimizationConfig,
                                            SParameterHfssOptimizer)
from simulation.hfss.s_parameter_constraint import (
    SParameterLowerBoundConstraint, SParameterUpperBoundConstraint)

FLAGS = flags.FLAGS

# Design variables.
FIXED_VARIABLES = [
    FixedVariable("w_dielectric", value=50, unit="mm"),
    FixedVariable("l_dielectric", value=20, unit="mm"),
    FixedVariable("h_prepreg", value=18, unit="mil"),
    FixedVariable("h_dielectric_antenna", value=60, unit="mil"),
    FixedVariable("h_dielectric_microstrip", value=10, unit="mil"),
    FixedVariable("w_cpw_ground", value=2, unit="mm"),
    FixedVariable("h_copper", value=1, unit="copper_oz_per_ft2"),
    FixedVariable("r_via", value=0.2, unit="mm"),
    FixedVariable("x_via_offset", value=0.5, unit="mm"),
    FixedVariable("y_via_offset", value=0, unit="mm"),
    FixedVariable("y_via", value=1, unit="mm"),
]
OPTIMIZER_VARIABLES = [
    OptimizerVariable(
        "w_cpw",
        initial_value=0.49,
        lower_bound=0.2,
        upper_bound=1,
        unit="mm",
    ),
    OptimizerVariable(
        "w_cpw_gap",
        initial_value=0.256,
        lower_bound=0.05,
        upper_bound=0.5,
        unit="mm",
    ),
]

# Constraints.
CONSTRAINTS = [
    SParameterUpperBoundConstraint(
        s_parameter="S11",
        upper_bound_db=-25,
        lower_frequency_hz=constants.ghz(4),
        upper_frequency_hz=constants.ghz(14),
    ),
    SParameterLowerBoundConstraint(
        s_parameter="S21",
        lower_bound_db=-0.75,
        lower_frequency_hz=constants.ghz(4),
        upper_frequency_hz=constants.ghz(14),
    ),
]

# Optimization configuration.
OPTIMIZATION_CONFIG = OptimizationConfig(
    max_iterations=100,
    x_tolerance=1e-3,
    function_tolerance=1e-3,
    initial_simplex_scale=0.05,
)


def run_s_parameter_hfss_optimizer(project_config: HfssProjectConfig) -> None:
    """Configures and runs the S-parameter HFSS optimizer.

    Args:
        project_config: Project configuration.
    """

    optimizer = SParameterHfssOptimizer(
        project_config,
        FIXED_VARIABLES,
        OPTIMIZER_VARIABLES,
        CONSTRAINTS,
        OPTIMIZATION_CONFIG,
    )
    result = optimizer.run()

    logging.info("Optimal values: %s", result.optimal_values)
    logging.info("Objective value: %g", result.objective_value)
    logging.info("Feasible: %s", result.feasible)
    logging.info("History CSV: %s", result.history_csv)
    for evaluation in result.final_run.constraint_evaluations:
        logging.info(
            "%s: violation %g dB, worst %g dB at %g GHz",
            evaluation.name,
            evaluation.violation,
            evaluation.worst_value_db,
            evaluation.worst_frequency_hz / 1e9,
        )


def main(argv: list[str]) -> None:
    assert len(argv) == 1, argv

    project_config = HfssProjectConfig(
        project_path=FLAGS.project_path,
        design_name=FLAGS.design_name,
        report_name=FLAGS.report_name,
        output_dir=FLAGS.output_dir,
        aedt_version=FLAGS.aedt_version,
        analyze_setup_name=FLAGS.analyze_setup_name,
        cleanup_variations=FLAGS.cleanup_variations,
    )
    run_s_parameter_hfss_optimizer(project_config)


if __name__ == "__main__":
    flags.DEFINE_string(
        "project_path",
        r"C:\Users\tryua\Documents\Ansoft\MARLIN1.aedt",
        "Path to the AEDT project file to optimize.",
    )
    flags.DEFINE_string("design_name", "gcpw_ro4350b_4L", "HFSS design name.")
    flags.DEFINE_string("report_name", "S Parameter Plot 1",
                        "HFSS report name to export.")
    flags.DEFINE_string(
        "output_dir",
        None,
        "Directory for exported S-parameter CSVs and optimizer history.",
    )
    flags.DEFINE_string(
        "aedt_version",
        None,
        "Optional AEDT version for PyAEDT, for example, 2026.1 or 261.",
    )
    flags.DEFINE_string(
        "analyze_setup_name",
        None,
        "Optional HFSS setup name. If unset, AnalyzeAll is used.",
    )
    flags.DEFINE_bool(
        "cleanup_variations",
        False,
        "If true, full solved variations are deleted after each run.",
    )
    flags.mark_flag_as_required("output_dir")

    app.run(main)
