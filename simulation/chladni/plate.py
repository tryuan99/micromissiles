"""The Chladni plate class simulates a free plate driven at one point."""

import numpy as np

from simulation.chladni.material import Material
from simulation.chladni.modes import Modes
from simulation.chladni.response import Response
from simulation.chladni.ritz_model import RitzModel
from simulation.chladni.shape import Shape


class ChladniPlate:
    """Plate driven at one point and at a single frequency.

    Attributes:
        shape: Plate shape.
        model: Stiffness and mass matrices.
        modes: Natural frequencies and vibration shapes.
        drive_point: Drive point.
        drive_mass: Moving mass of the wave driver attached at the drive point
            in kg.
        damping_ratio: How strongly each mode is damped, e.g., 0.005 = 0.5%.
        drive_mode_coefficients: How much each mode moves at the drive point.
    """

    def __init__(
        self,
        shape: Shape,
        material: Material,
        drive_point: tuple[float, float] = (0.0, 0.0),
        drive_mass: float = 0.0,
        degree: int = 14,
        num_integration_points_per_side: int = 160,
        damping_ratio: float = 0.005,
    ) -> None:
        if not shape.contains(*drive_point):
            raise ValueError(f"Drive point {drive_point} is not on the plate.")

        self.shape = shape
        self.model = RitzModel(shape, material, degree,
                               num_integration_points_per_side)
        self.modes = Modes(self.model.stiffness, self.model.mass)
        self.drive_point = drive_point
        self.drive_mass = drive_mass
        self.damping_ratio = damping_ratio
        # Calculate the coefficients of the drive in terms of the basis
        # functions and then transform it into the eigenmode basis.
        self.drive_mode_coefficients = (
            self.modes.modes.T @ self.model.basis.evaluate(*drive_point)[0])

    def responses(self, angular_frequency: float | np.ndarray) -> np.ndarray:
        """Returns how much each mode moves for a 1 N force applied to the plate
        at the drive point at the given frequencies.

        Args:
            angular_frequency: Drive frequency or frequencies in rad/s.

        Returns:
            The complex amplitude of each mode in m/N with one row per
            frequency and one column per mode.
        """
        angular_frequency = np.asarray(angular_frequency)
        natural_frequencies = self.modes.angular_frequencies
        free_responses = self.drive_mode_coefficients / (
            natural_frequencies**2 - angular_frequency[..., None]**2 +
            2j * self.damping_ratio * natural_frequencies *
            angular_frequency[..., None])
        # The drive mass and the plate move together according to F_plate =
        # F_driver - m * (-omega^2) * w_0, where w_0 = deflection at drive point
        # * F_plate. Thus, F_plate = F_driver / (1 - * omega^2 * deflection).
        deflection_at_drive_point = free_responses @ self.drive_mode_coefficients
        return free_responses / (1 - self.drive_mass * angular_frequency**2 *
                                 deflection_at_drive_point)[..., None]

    def resonances(
        self,
        min_frequency: float,
        max_frequency: float,
        num_steps: int = 10001,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Returns the resonances in the frequency band.

        If a drive mass is present, the resonances are of the coupled plate and
        driver.

        Args:
            min_frequency: Lower frequency in Hz.
            max_frequency: Upper frequency in Hz.
            num_steps: Number of frequency steps.

        Returns:
            The resonant frequencies in Hz and their response magnitudes m/N.
        """
        frequencies = np.linspace(min_frequency, max_frequency, num_steps)
        response_magnitudes = np.abs(
            self.responses(2 * np.pi * frequencies)
            @ self.drive_mode_coefficients)
        middle = response_magnitudes[1:-1]
        peaks = np.where((middle > response_magnitudes[:-2]) &
                         (middle > response_magnitudes[2:]))[0] + 1
        return frequencies[peaks], response_magnitudes[peaks]

    def steady_state(
        self,
        frequency: float,
        amplitude: float,
        num_points_per_side: int = 201,
    ) -> Response:
        """Returns the steady-state motion of the plate sampled on a square grid.

        Args:
            frequency: Drive frequency in Hz.
            amplitude: Amplitude of the drive point in m.
            num_points_per_side: Number of grid points per side.

        Returns:
            The complex deflection on the grid, with NaN at points that are
            not on the plate.
        """
        x_min, x_max, y_min, y_max = self.shape.bounding_box
        x, y = np.meshgrid(
            np.linspace(x_min, x_max, num_points_per_side),
            np.linspace(y_min, y_max, num_points_per_side),
            indexing="ij",
        )
        mask = self.shape.contains(x, y)
        responses = self.responses(2 * np.pi * frequency)
        # Calculate the force that generates the drive amplitude.
        force = amplitude / (self.drive_mode_coefficients @ responses)
        # Calculate the steady-state response in the eigenmode basis, transform
        # into the model basis and then into the grid points, and scale the
        # response by the force.
        response = self.model.basis.evaluate(
            x, y) @ (self.modes.modes @ responses) * force
        return Response(
            x,
            y,
            np.where(
                mask,
                response.reshape((num_points_per_side, num_points_per_side)),
                np.nan,
            ),
            amplitude,
            frequency,
        )
