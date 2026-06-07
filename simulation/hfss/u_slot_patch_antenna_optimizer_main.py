"""Optimizes the HFSS design variables for a U-slot patch antenna."""

from absl import app, flags, logging

from simulation.hfss import constants
from simulation.hfss.design_variable import FixedVariable, OptimizerVariable
from simulation.hfss.hfss_optimizer import (HfssProjectConfig,
                                            OptimizationConfig,
                                            SParameterHfssOptimizer)
from simulation.hfss.s_parameter_constraint import \
    SParameterUpperBoundConstraint

FLAGS = flags.FLAGS

# Design variables.
FIXED_VARIABLES = [
    FixedVariable("w_dielectric", value=25, unit="mm"),
    FixedVariable("l_dielectric", value=25, unit="mm"),
    FixedVariable("h_prepreg", value=7.496, unit="mm"),
    FixedVariable("h_dielectric_microstrip", value=10, unit="mm"),
    FixedVariable("h_dielectric_antenna", value=40, unit="mm"),
    FixedVariable("w_microstrip", value=0.5105, unit="mm"),
    FixedVariable("h_copper", value=1, unit="copper_oz_per_ft2"),
    FixedVariable("r_via", value=0.3, unit="mm"),
]
OPTIMIZER_VARIABLES = [
    OptimizerVariable(
        "w_patch",
        initial_value=11.7,
        lower_bound=8,
        upper_bound=15,
        unit="mm",
    ),
    OptimizerVariable(
        "l_patch",
        initial_value=7.9,
        lower_bound=7,
        upper_bound=9.5,
        unit="mm",
    ),
    OptimizerVariable(
        "y_feed",
        initial_value=0,
        lower_bound=-2,
        upper_bound=2,
        unit="mm",
    ),
    OptimizerVariable(
        "w_slot",
        initial_value=3,
        lower_bound=2,
        upper_bound=5,
        unit="mm",
    ),
    OptimizerVariable(
        "l_slot",
        initial_value=4.6,
        lower_bound=3,
        upper_bound=6,
        unit="mm",
    ),
    OptimizerVariable(
        "t_slot",
        initial_value=1,
        lower_bound=0.8,
        upper_bound=1.1,
        unit="mm",
    ),
    OptimizerVariable(
        "y_slot",
        initial_value=1,
        lower_bound=0,
        upper_bound=2,
        unit="mm",
    ),
]

# Constraints.
CONSTRAINTS = [
    SParameterUpperBoundConstraint(
        s_parameter="S11",
        upper_bound_db=-10.0,
        lower_frequency_hz=constants.ghz(8.5),
        upper_frequency_hz=constants.ghz(9.5),
    ),
]

# Optimization configuration.
OPTIMIZATION_CONFIG = OptimizationConfig(
    max_iterations=100,
    max_function_evaluations=200,
    x_tolerance=1e-3,
    function_tolerance=1e-3,
    initial_simplex_scale=0.05,
)


def run_patch_antenna_optimizer(project_config: HfssProjectConfig) -> None:
    """Configures and runs the patch antenna HFSS optimizer.
    
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
    logging.info("Objective value: %.6g", result.objective_value)
    logging.info("Feasible: %s", result.feasible)
    logging.info("History CSV: %s", result.history_csv)
    for evaluation in result.final_run.constraint_evaluations:
        logging.info(
            "%s: violation %.6g dB, worst %.6g dB at %.6g GHz",
            evaluation.name,
            evaluation.violation,
            evaluation.worst_value_db,
            evaluation.worst_frequency_hz / 1e9,
        )


def main(argv: list[str]) -> None:
    assert len(argv) == 1, argv

    project_config = HfssProjectConfig(
        hfss=FLAGS.hfss,
        hfss_install_dir=FLAGS.hfss_install_dir,
        hfss_desktop_plugin_dir=FLAGS.hfss_desktop_plugin_dir,
        project_name=FLAGS.project_name,
        design_name=FLAGS.design_name,
        report_name=FLAGS.report_name,
        output_dir=FLAGS.output_dir,
        extra_hfss_args=tuple(FLAGS.extra_hfss_args),
        analyze_setup_name=FLAGS.analyze_setup_name,
        cleanup_variations=FLAGS.cleanup_variations,
    )
    run_patch_antenna_optimizer(project_config)


if __name__ == "__main__":
    flags.DEFINE_string(
        "hfss",
        r"C:\Program Files\AnsysEM\v232\Win64\ansysedt.exe",
        "Path to ansysedt.exe.",
    )
    flags.DEFINE_string(
        "hfss_install_dir",
        r"C:\Program Files\AnsysEM\v232\Win64",
        "Ansys Electronics Desktop installation directory.",
    )
    flags.DEFINE_string(
        "hfss_desktop_plugin_dir",
        r"C:\Program Files\AnsysEM\v232\Win64\PythonFiles\DesktopPlugin",
        "Directory containing ScriptEnv.py.",
    )
    flags.DEFINE_string("project_name", "MARLIN", "HFSS project name.")
    flags.DEFINE_string("design_name", "u_slot_patch_antenna_ro4350b",
                        "HFSS design name.")
    flags.DEFINE_string("report_name", "SParams", "HFSS report name to export.")
    flags.DEFINE_string(
        "output_dir",
        None,
        "Directory for generated HFSS scripts, S-parameter CSVs, and history.",
    )
    flags.DEFINE_multi_string(
        "extra_hfss_args",
        [],
        "Additional command-line argument passed to ansysedt.exe.",
    )
    flags.DEFINE_string(
        "analyze_setup_name",
        None,
        "Optional HFSS setup name. If unset, AnalyzeAll is used.",
    )
    flags.DEFINE_bool(
        "cleanup_variations",
        False,
        "Delete full solved variations after each run.",
    )
    flags.mark_flag_as_required("output_dir")

    app.run(main)
