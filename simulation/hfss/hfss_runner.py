"""PyAEDT runner for opening HFSS, solving, and exporting reports."""

from pathlib import Path

from absl import logging
from ansys.aedt.core import Hfss


class HfssRunner:
    """Runs HFSS simulations for already-formatted design variable values.
    
    Attributes:
        hfss: HFSS instance.
    """

    def __init__(
        self,
        project_path: Path | str,
        design_name: str,
        aedt_version: str | None = None,
    ) -> None:
        """Opens one non-graphical AEDT session.

        Args:
            project_path: Path to the AEDT project.
            design_name: HFSS design name inside the project.
            aedt_version: Optional AEDT version passed to PyAEDT.

        Raises:
            FileNotFoundError: If the project does not exist.
            RuntimeError: If the HFSS design cannot be opened.
        """
        project_path = Path(project_path).expanduser().resolve()
        if not project_path.exists():
            raise FileNotFoundError(
                f"HFSS project does not exist: {project_path}.")

        logging.info("Opening HFSS design %s in project %s.", design_name,
                     project_path)
        self.hfss = Hfss(
            project=str(project_path),
            design=design_name,
            version=aedt_version,
            non_graphical=True,
            new_desktop=True,
            close_on_exit=True,
        )
        if not self.hfss.valid_design:
            self.close()
            raise RuntimeError(
                f"Failed to open HFSS design {design_name!r} in {project_path}."
            )

    def close(self) -> None:
        """Closes the project and AEDT session opened by this runner."""
        if self.hfss is None:
            return
        try:
            logging.info("Closing HFSS.")
            self.hfss.release_desktop(
                close_projects=True,
                close_desktop=True,
            )
        finally:
            self.hfss = None

    def run(
        self,
        design_variables: dict[str, str],
        report_name: str,
        output_dir: Path | str,
        analyze_setup_name: str | None = None,
        cleanup_variations: bool = False,
    ) -> Path:
        """Runs HFSS and exports the configured report.

        Args:
            design_variables: Map from the HFSS design variable names to the
                formatted values, including unit suffixes where needed.
            report_name: Existing report to export.
            output_dir: Directory for this run's exported files.
            analyze_setup_name: Optional HFSS setup name. If unset, AnalyzeAll
                is used.
            cleanup_variations: Whether to delete solved variations after this
                run.

        Returns:
            The path to the exported CSV data.

        Raises:
            RuntimeError: If HFSS is not open or failed to save, analyze, export,
                or clean up the simulation.
        """
        if self.hfss is None:
            raise RuntimeError("HFSS is not open.")

        for name, value in design_variables.items():
            self.hfss[name] = value

        if not self.hfss.save_project():
            raise RuntimeError(
                f"Failed to save HFSS project for {design_variables}.")
        if not self.hfss.analyze(setup=analyze_setup_name):
            raise RuntimeError(
                f"HFSS simulation failed for {design_variables}.")

        available_reports = self.hfss.get_oo_name(self.hfss.oreportsetup) or []
        if report_name not in available_reports:
            raise ValueError(
                f"HFSS report {report_name!r} does not exist. Available "
                f"reports: {available_reports}.")

        data_csv = (Path(output_dir) /
                    f"{report_name.lower().replace(' ', '_')}.csv")
        logging.info("Exporting HFSS report %s to %s.", report_name, data_csv)
        self.hfss.oreportsetup.ExportToFile(
            report_name,
            str(data_csv),
            False,
        )
        if cleanup_variations:
            if not self.hfss.cleanup_solution(variations="All"):
                raise RuntimeError("Failed to clean up HFSS solution data for "
                                   f"{design_variables}.")
        return data_csv
