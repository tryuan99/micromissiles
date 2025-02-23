"""The antenna array optimization problem finds the Pareto front between the
main lobe width and the sidelobe level by formulating it as a multi-objective
optimization problem.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayBeamSteer,
                                              AntennaArrayElement)
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from simulation.antenna.proto.geometry_pb2 import (CartesianCoordinates,
                                                   Quaternion)
from utils.optimization.problem import Problem


class Line(ABC):
    """Interface for a line."""

    @abstractmethod
    def evaluate(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the y-coordinates corresponding to the given
        x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The y-coordinates corresponding to the given x-coordinates.
        """

    @abstractmethod
    def evaluate_slope(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the slope at each of the given x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The slopes of the normal line at each of the given x-coordinates.
        """

    def evaluate_normal(self, x: float | np.ndarray) -> float | np.ndarray:
        """Evaluates the slope of the normal line at each of the given
        x-coordinates.

        Args:
            x: x-coordinates.

        Returns:
            The slopes of the normal line at each of the given x-coordinates.
        """
        slope = self.evaluate_slope(x)
        return -1 / slope


class Surface(ABC):
    """Interface for a surface."""

    @abstractmethod
    def evaluate(
        self,
        x: float | np.ndarray,
        y: float | np.ndarray,
    ) -> float | np.ndarray:
        """Evaluates the y-coordinates corresponding to the given
        x-coordinates and y-coordinates.

        Args:
            x: x-coordinates.
            y: y-coordinates.

        Returns:
            The z-coordinates corresponding to the given x-coordinates.
        """

    @abstractmethod
    def evaluate_gradient(
        self,
        x: float | np.ndarray,
        y: float | np.ndarray,
    ) -> np.ndarray:
        """Evaluates the gradient at each of the given x-coordinates and
        y-coordinates.

        Args:
            x: x-coordinates.
            y: y-coordinates.

        Returns:
            The gradients at each of the given x-coordinates and y-coordinates.
        """


class AntennaArrayOptimizationProblem(Problem):
    """Antenna array optimization problem.

    Attributes:
        antenna_array_config: Antenna array configuration.
    """

    def __init__(self, antenna_array_config: AntennaArrayConfig) -> None:
        self.antenna_array_config = antenna_array_config

    def num_antenna_elements(self) -> int:
        """Returns the number of antenna elements."""
        return len(self.antenna_array_config.antenna_array_element_configs)

    @abstractmethod
    def num_variables_per_element(self) -> int:
        """Returns the number of design variables per antenna array element."""

    def num_variables(self) -> int:
        """Returns the number of design variables."""
        return self.num_antenna_elements() * self.num_variables_per_element()

    def lower_bound(self) -> np.ndarray:
        """Returns the lower bound on the design variables."""
        return np.tile(self._lower_bound(), self.num_antenna_elements())

    @abstractmethod
    def _lower_bound(self) -> np.ndarray:
        """Returns the lower bound on the design variables for a single
        antenna array element.
        """

    def upper_bound(self) -> np.ndarray:
        """Returns the upper bound on the design variables."""
        return np.tile(self._upper_bound(), self.num_antenna_elements())

    @abstractmethod
    def _upper_bound(self) -> np.ndarray:
        """Returns the upper bound on the design variables for a single
        antenna array element.
        """

    def num_objectives(self) -> int:
        """Returns the number of objectives."""
        # The two objectives are the main lobe width and the sidelobe level.
        return 2

    def evaluate_objectives(self, x: np.ndarray) -> list[float]:
        """Evaluates the objective(s) on the given design variable values.

        Args:
            x: Design variable values.

        Returns:
            The objective(s) evaluated on the given design variable values.
        """
        # Evaluate the maximum main lobe width and the highest sidelobe level.
        antenna_array = self._create_antenna_array(x)
        max_main_lobe_width = self._evaluate_max_main_lobe_width(antenna_array)
        highest_sidelobe_level = (
            self._evaluate_highest_sidelobe_level(antenna_array))
        return [max_main_lobe_width, highest_sidelobe_level]

    def _create_antenna_array(self, x: np.ndarray) -> AntennaArray:
        """Creates the antenna array from the design variable values.

        Args:
            x: Design variable values.

        Returns:
            The antenna array associated with the design variable values.
        """
        positions = self._evaluate_positions(x)
        orientations = self._evaluate_orientations(x)

        # Copy the base antenna array configuration.
        antenna_array_config = AntennaArrayConfig()
        antenna_array_config.CopyFrom(self.antenna_array_config)

        # Set the position and orientation for each antenna array element.
        for i in range(self.num_antenna_elements()):
            antenna_array_config.antenna_array_element_configs[
                i].position.CopyFrom(positions[i])
            antenna_array_config.antenna_array_element_configs[
                i].orientation.CopyFrom(orientations[i])

        antenna_array = AntennaArray.create(antenna_array_config)
        return antenna_array

    @abstractmethod
    def _evaluate_positions(self, x: np.ndarray) -> list[CartesianCoordinates]:
        """Evaluates the positions of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The positions of the antenna array elements.
        """

    @abstractmethod
    def _evaluate_orientations(self, x: np.ndarray) -> list[Quaternion]:
        """Evaluates the orientations of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The orientations of the antenna array elements.
        """

    @abstractmethod
    def _evaluate_max_main_lobe_width(
        self,
        antenna_array: AntennaArray,
    ) -> float:
        """Evaluates the maximum main lobe width of the antenna array.

        Args:
            antenna_array: Antenna array.

        Returns:
            The maximum main lobe width.
        """

    @abstractmethod
    def _evaluate_highest_sidelobe_level(
        self,
        antenna_array: AntennaArray,
    ) -> float:
        """Evaluates the highest sidelobe level of the antenna array.

        Args:
            antenna_array: Antenna array.

        Returns:
            The highest sidelobe level.
        """


class AntennaArray1DOptimizationProblem(AntennaArrayOptimizationProblem):
    """Antenna array 1D optimization problem.

    Attributes:
        max_azimuth: Maximum azimuth in radians for which to evaluate the
          objectives.
    """

    def __init__(
        self,
        antenna_array_config: AntennaArrayConfig,
        max_azimuth: float,
    ) -> None:
        super().__init__(antenna_array_config)
        self.max_azimuth = max_azimuth

    def _evaluate_max_main_lobe_width(
        self,
        antenna_array: AntennaArray,
    ) -> float:
        """Evaluates the maximum main lobe width of the antenna array.

        Args:
            antenna_array: Antenna array.

        Returns:
            The maximum main lobe width.
        """
        # For antenna arrays lying on a horizontal plane, fix the elevation at 0.
        azimuth_sweep = np.linspace(
            -self.max_azimuth,
            self.max_azimuth,
            180,
            endpoint=False,
        )
        azimuth_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)

        main_lobe_widths = np.zeros(azimuth_sweep.shape)
        for azimuth_index, azimuth in enumerate(azimuth_sweep):
            beam_steer = AntennaArrayBeamSteer(
                azimuth=azimuth,
                elevation=0,
            )
            radiation_pattern = antenna_array.calculate_radiation_pattern(
                beam_steer,
                azimuth=azimuth_values,
                elevation=0,
            )
            azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
            main_lobe_width = (
                radiation_pattern.main_lobe_width(azimuth_peak_index))
            main_lobe_widths[azimuth_index] = main_lobe_width
        return np.max(main_lobe_widths)

    def _evaluate_highest_sidelobe_level(
        self,
        antenna_array: AntennaArray,
    ) -> float:
        """Evaluates the highest sidelobe level of the antenna array.

        Args:
            antenna_array: Antenna array.

        Returns:
            The highest sidelobe level.
        """
        # For antenna arrays lying on a horizontal plane, fix the elevation at 0.
        azimuth_sweep = np.linspace(
            -self.max_azimuth,
            self.max_azimuth,
            180,
            endpoint=False,
        )
        azimuth_values = np.linspace(
            -self.max_azimuth,
            self.max_azimuth,
            360,
            endpoint=False,
        )

        sidelobe_levels = np.zeros(azimuth_sweep.shape)
        for azimuth_index, azimuth in enumerate(azimuth_sweep):
            beam_steer = AntennaArrayBeamSteer(
                azimuth=azimuth,
                elevation=0,
            )
            radiation_pattern = antenna_array.calculate_radiation_pattern(
                beam_steer,
                azimuth=azimuth_values,
                elevation=0,
            )
            azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
            sidelobe_level = (
                radiation_pattern.sidelobe_level(azimuth_peak_index))
            sidelobe_levels[azimuth_index] = sidelobe_level
        return np.max(sidelobe_levels)


class AntennaArray1DApertureOptimizationProblem(
        AntennaArray1DOptimizationProblem):
    """Antenna array 1D aperture optimization problem.

    The antenna array elements lie on a horizontal plane and are constrained to
    a maximum aperture.

    The design variables are ordered as follows:
     - x-coordinate of antenna array element 0
     - z-coordinate of antenna array element 0
     - theta rotation around the y-axis of antenna array element 0
     - x-coordinate of antenna array element 1
     - z-coordinate of antenna array element 1
     - theta rotation around the y-axis of antenna array element 1
     - ...

    Attributes:
        x_min: Minimum x-coordinate.
        x_max: Maximum x-coordinate.
        z_min: Minimum z-coordinate.
        z_max: Maximum z-coordinate.
    """

    def __init__(
        self,
        antenna_array_config: AntennaArrayConfig,
        max_azimuth: float,
        x_min: float,
        x_max: float,
        z_min: float,
        z_max: float,
    ) -> None:
        super().__init__(antenna_array_config, max_azimuth)
        self.x_min = x_min
        self.x_max = x_max
        self.z_min = z_min
        self.z_max = z_max

    def num_variables_per_element(self) -> int:
        """Returns the number of design variables per antenna array element."""
        return 3

    def _lower_bound(self) -> np.ndarray:
        """Returns the lower bound on the design variables for a single
        antenna array element.
        """
        return np.array([self.x_min, self.z_min, -np.pi / 2])

    def _upper_bound(self) -> np.ndarray:
        """Returns the upper bound on the design variables for a single
        antenna array element.
        """
        return np.array([self.x_max, self.z_max, np.pi / 2])

    def _evaluate_positions(self, x: np.ndarray) -> list[CartesianCoordinates]:
        """Evaluates the positions of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The positions of the antenna array elements.
        """
        x_coordinates = x[::self.num_variables_per_element()]
        z_coordinates = x[1::self.num_variables_per_element()]

        # Set the position of each antenna array element.
        positions = [
            CartesianCoordinates() for _ in range(self.num_antenna_elements())
        ]
        for i in range(self.num_antenna_elements()):
            positions[i].x = x_coordinates[i]
            positions[i].z = z_coordinates[i]
        return positions

    def _evaluate_orientations(self, x: np.ndarray) -> list[Quaternion]:
        """Evaluates the orientations of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The orientations of the antenna array elements.
        """
        thetas = x[2::self.num_variables_per_element()]

        # Set the orientation of each antenna array element.
        orientations = [
            Quaternion() for _ in range(self.num_antenna_elements())
        ]
        for i in range(self.num_antenna_elements()):
            orientations[i].theta = thetas[i]
            orientations[i].y = 1
        return orientations


class AntennaArray1DLineOptimizationProblem(AntennaArray1DOptimizationProblem):
    """Antenna array 1D line optimization problem.

    The antenna array elements are constrained to lie on a line.

    The design variables are ordered as follows:
     - x-coordinate of antenna array element 0
     - x-coordinate of antenna array element 1
     - ...

    Attributes:
        line: Line on which the antenna array elements lie.
        x_min: Minimum x-coordinate.
        x_max: Maximum x-coordinate.
    """

    def __init__(
        self,
        antenna_array_config: AntennaArrayConfig,
        max_azimuth: float,
        line: Line,
        x_min: float,
        x_max: float,
    ) -> None:
        super().__init__(antenna_array_config, max_azimuth)
        self.line = line
        self.x_min = x_min
        self.x_max = x_max

    def num_variables_per_element(self) -> int:
        """Returns the number of design variables per antenna array element."""
        return 1

    def _lower_bound(self) -> float:
        """Returns the lower bound on the design variables for a single
        antenna array element.
        """
        return self.x_min

    def _upper_bound(self) -> float:
        """Returns the upper bound on the design variables for a single
        antenna array element.
        """
        return self.x_max

    def _evaluate_positions(self, x: np.ndarray) -> list[CartesianCoordinates]:
        """Evaluates the positions of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The positions of the antenna array elements.
        """
        x_coordinates = x
        z_coordinates = self.line.evaluate(x_coordinates)

        # Set the position of each antenna array element.
        positions = [
            CartesianCoordinates() for _ in range(self.num_antenna_elements())
        ]
        for i in range(self.num_antenna_elements()):
            positions[i].x = x_coordinates[i]
            positions[i].z = z_coordinates[i]
        return positions

    def _evaluate_orientations(self, x: np.ndarray) -> list[Quaternion]:
        """Evaluates the orientations of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The orientations of the antenna array elements.
        """
        normal_slopes = self.line.evaluate_normal(x)
        angles_to_right = np.arctan(normal_slopes)
        positive_angle_mask = angles_to_right >= 0
        thetas = np.zeros(angles_to_right.shape)
        thetas[positive_angle_mask] = (np.pi / 2 -
                                       angles_to_right[positive_angle_mask])
        thetas[~positive_angle_mask] = (-np.pi / 2 -
                                        angles_to_right[~positive_angle_mask])

        # Set the orientation of each antenna array element.
        orientations = [
            Quaternion() for _ in range(self.num_antenna_elements())
        ]
        for i in range(self.num_antenna_elements()):
            orientations[i].theta = thetas[i]
            orientations[i].y = 1
        return orientations


class AntennaArray2DOptimizationProblem(AntennaArrayOptimizationProblem):
    """Antenna array 2D optimization problem.

    Attributes:
        max_azimuth: Maximum azimuth in radians for which to evaluate the
          objectives.
        max_elevation: Maximum elevation in radians for which to evaluate the
          objectives.
    """

    def __init__(
        self,
        antenna_array_config: AntennaArrayConfig,
        max_azimuth: float,
        max_elevation: float,
    ) -> None:
        super().__init__(antenna_array_config)
        self.max_azimuth = max_azimuth
        self.max_elevation = max_elevation

    def _evaluate_max_main_lobe_width(
        self,
        antenna_array: AntennaArray,
    ) -> float:
        """Evaluates the maximum main lobe width of the antenna array.

        Args:
            antenna_array: Antenna array.

        Returns:
            The maximum main lobe width.
        """
        azimuth_sweep = np.linspace(
            -self.max_azimuth,
            self.max_azimuth,
            5,
        )
        azimuth_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)
        elevation_sweep = np.linspace(
            -self.max_elevation,
            self.max_elevation,
            5,
        )
        elevation_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)
        azimuth_mesh, elevation_mesh = np.meshgrid(
            azimuth_values,
            elevation_values,
            indexing="ij",
        )

        main_lobe_widths = np.zeros(
            (*azimuth_sweep.shape, *elevation_sweep.shape))
        for azimuth_index, azimuth in enumerate(azimuth_sweep):
            for elevation_index, elevation in enumerate(elevation_sweep):
                beam_steer = AntennaArrayBeamSteer(azimuth, elevation)
                radiation_pattern = antenna_array.calculate_radiation_pattern(
                    beam_steer,
                    azimuth_mesh,
                    elevation_mesh,
                )
                azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
                elevation_peak_index = np.argmin(
                    np.abs(elevation_values - elevation))
                main_lobe_width = radiation_pattern.main_lobe_width([
                    azimuth_peak_index,
                    elevation_peak_index,
                ])
                # Choose the higher main lobe width between the azimuth and
                # elevation dimensions.
                main_lobe_widths[azimuth_index,
                                 elevation_index] = max(main_lobe_width)
        return np.max(main_lobe_widths)

    def _evaluate_highest_sidelobe_level(
        self,
        antenna_array: AntennaArray,
    ) -> float:
        """Evaluates the highest sidelobe level of the antenna array.

        Args:
            antenna_array: Antenna array.

        Returns:
            The highest sidelobe level.
        """
        azimuth_sweep = np.linspace(
            -self.max_azimuth,
            self.max_azimuth,
            5,
        )
        azimuth_values = np.linspace(
            -self.max_azimuth,
            self.max_azimuth,
            360,
            endpoint=False,
        )
        elevation_sweep = np.linspace(
            -self.max_elevation,
            self.max_elevation,
            5,
        )
        elevation_values = np.linspace(
            -self.max_elevation,
            self.max_elevation,
            360,
            endpoint=False,
        )
        azimuth_mesh, elevation_mesh = np.meshgrid(
            azimuth_values,
            elevation_values,
            indexing="ij",
        )

        sidelobe_levels = np.zeros(
            (*azimuth_sweep.shape, *elevation_sweep.shape))
        for azimuth_index, azimuth in enumerate(azimuth_sweep):
            for elevation_index, elevation in enumerate(elevation_sweep):
                beam_steer = AntennaArrayBeamSteer(azimuth, elevation)
                radiation_pattern = antenna_array.calculate_radiation_pattern(
                    beam_steer,
                    azimuth_mesh,
                    elevation_mesh,
                )
                azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
                elevation_peak_index = np.argmin(
                    np.abs(elevation_values - elevation))
                sidelobe_level = (radiation_pattern.sidelobe_level([
                    azimuth_peak_index,
                    elevation_peak_index,
                ]))
                sidelobe_levels[azimuth_index, elevation_index] = sidelobe_level
        return np.max(sidelobe_levels)


class AntennaArray2DSurfaceOptimizationProblem(AntennaArray2DOptimizationProblem
                                              ):
    """Antenna array 2D surface optimization problem.

    The antenna array elements are constrained to lie on a surface.

    The design variables are ordered as follows:
     - x-coordinate of antenna array element 0
     - y-coordinate of antenna array element 0
     - x-coordinate of antenna array element 1
     - y-coordinate of antenna array element 1
     - ...

    Attributes:
        surface: Surface on which the antenna array elements lie.
        x_min: Minimum x-coordinate.
        x_max: Maximum x-coordinate.
        y_min: Minimum y-coordinate.
        y_max: Maximum y-coordinate.
    """

    def __init__(
        self,
        antenna_array_config: AntennaArrayConfig,
        max_azimuth: float,
        max_elevation: float,
        surface: Surface,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> None:
        super().__init__(antenna_array_config, max_azimuth, max_elevation)
        self.surface = surface
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def num_variables_per_element(self) -> int:
        """Returns the number of design variables per antenna array element."""
        return 2

    def _lower_bound(self) -> np.ndarray:
        """Returns the lower bound on the design variables for a single
        antenna array element.
        """
        return np.array([self.x_min, self.y_min])

    def _upper_bound(self) -> np.ndarray:
        """Returns the upper bound on the design variables for a single
        antenna array element.
        """
        return np.array([self.x_max, self.y_max])

    def _evaluate_positions(self, x: np.ndarray) -> list[CartesianCoordinates]:
        """Evaluates the positions of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The positions of the antenna array elements.
        """
        x_coordinates = x[::self.num_variables_per_element()]
        y_coordinates = x[1::self.num_variables_per_element()]
        z_coordinates = self.surface.evaluate(x_coordinates, y_coordinates)

        # Set the position of each antenna array element.
        positions = [
            CartesianCoordinates() for _ in range(self.num_antenna_elements())
        ]
        for i in range(self.num_antenna_elements()):
            positions[i].x = x_coordinates[i]
            positions[i].y = y_coordinates[i]
            positions[i].z = z_coordinates[i]
        return positions

    def _evaluate_orientations(self, x: np.ndarray) -> list[Quaternion]:
        """Evaluates the orientations of the antenna array elements.

        Args:
            x: Design variable values.

        Returns:
            The orientations of the antenna array elements.
        """
        x_coordinates = x[::self.num_variables_per_element()]
        y_coordinates = x[1::self.num_variables_per_element()]
        z_coordinates = self.surface.evaluate(x_coordinates, y_coordinates)
        gradient = self.surface.evaluate_gradient(x_coordinates, y_coordinates)
        forward = gradient / np.linalg.norm(gradient, axis=0)

        # To create a orientation, we assume that the right direction of the
        # antenna array element points orthogonal to the gradient and to the
        # position vector.
        position = np.array([x_coordinates, y_coordinates, z_coordinates])
        right = np.cross(position, gradient, axis=0)
        right /= np.linalg.norm(right, axis=0)
        up = np.cross(right, forward, axis=0)

        # Set the orientation of each antenna array element.
        orientations = [
            Quaternion() for _ in range(self.num_antenna_elements())
        ]
        # Find the default orientation of an antenna array element.
        default_antenna_array_element = AntennaArrayElement()
        default_rotation = np.array([
            default_antenna_array_element.boresight(),
            default_antenna_array_element.right(),
            default_antenna_array_element.vertical(),
        ]).T
        for i in range(self.num_antenna_elements()):
            # The rotation matrix rotates from the antenna array element's
            # default orientation to the calculated orientation.
            orientation_rotation = np.array([
                forward[:, i],
                right[:, i],
                up[:, i],
            ]).T
            rotation_matrix = orientation_rotation @ default_rotation.T
            theta = np.arccos((np.trace(rotation_matrix) - 1) / 2)
            rotation_axis = 1 / (2 * np.sin(theta)) * np.array([
                rotation_matrix[2, 1] - rotation_matrix[1, 2],
                rotation_matrix[0, 2] - rotation_matrix[2, 0],
                rotation_matrix[1, 0] - rotation_matrix[0, 1],
            ])
            orientations[i].theta = theta
            (
                orientations[i].x,
                orientations[i].y,
                orientations[i].z,
            ) = rotation_axis
        return orientations
