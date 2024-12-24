"""The antenna array class simulates the behavior and performance of an antenna
array.

The boresight of the antenna array is in the positive z-direction while a
planar antenna array will lie in the x-y plane.
"""

from typing import Self

import numpy as np

from simulation.antenna.antenna import Antenna
from simulation.antenna.antenna_factory import AntennaFactory
from simulation.antenna.isotropic_antenna import IsotropicAntenna
from simulation.antenna.proto.antenna_array_config_pb2 import (
    AntennaArrayConfig, AntennaArrayElementConfig)
from utils.coordinates import CartesianCoordinates, SphericalCoordinates
from utils.quaternion import RotationQuaternion


class AntennaArrayElement:
    """Antenna array element.

    Attributes:
        cartesian_coordinates: Cartesian coordinates.
        antenna: Antenna of the element.
        orientation: Orientation of the antenna element.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        coordinates: CartesianCoordinates = None,
        antenna: Antenna = IsotropicAntenna(),
        orientation: RotationQuaternion = RotationQuaternion(
            theta=0,
            axis=np.array([0, 0, 1]),
        ),
    ) -> None:
        self.cartesian_coordinates = coordinates
        if self.cartesian_coordinates is None:
            self.cartesian_coordinates = CartesianCoordinates(
                x=x,
                y=y,
                z=z,
            )
        self.antenna = antenna
        self.orientation = orientation

    @classmethod
    def create(
        cls,
        antenna_array_element_config: AntennaArrayElementConfig,
    ) -> Self:
        """Creates an antenna array element according to the configuration.

        Args:
            antenna_array_element_config: Antenna array element configuration.

        Returns:
            The antenna array element instance.
        """
        antenna = (AntennaFactory.create_antenna(
            antenna_array_element_config.antenna_config))
        position = CartesianCoordinates(
            x=antenna_array_element_config.position.x,
            y=antenna_array_element_config.position.y,
            z=antenna_array_element_config.position.z,
        )
        orientation = RotationQuaternion(
            theta=antenna_array_element_config.orientation.theta,
            x=antenna_array_element_config.orientation.x,
            y=antenna_array_element_config.orientation.y,
            z=antenna_array_element_config.orientation.z,
        )
        return cls(
            coordinates=position,
            antenna=antenna,
            orientation=orientation,
        )

    def coordinates(self) -> np.ndarray:
        """Returns the Cartesian coordinates."""
        return self.cartesian_coordinates.coordinates()

    def boresight(self) -> np.ndarray:
        """Returns the boresight direction."""
        return self._orient(np.array([0, 0, 1]))

    def vertical(self) -> np.ndarray:
        """Returns the vertical direction."""
        return self._orient(np.array([0, 1, 0]))

    def right(self) -> np.ndarray:
        """Returns the right direction, which corresponds to an azimuth of 90
        degrees.
        """
        return self._orient(np.array([-1, 0, 0]))

    def calculate_pattern(
        self,
        azimuth: float | np.ndarray,
        elevation: float | np.ndarray,
    ) -> float | np.ndarray:
        """Calculates the oriented radiation pattern of the antenna element.

        The azimuth and elevation are in the global coordinate system.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        # Transform the direction vectors from spherical coordinates to
        # Cartesian coordinates.
        coordinates = np.array(
            SphericalCoordinates.transform_to_cartesian_arrays(
                range=1,
                azimuth=azimuth,
                elevation=elevation,
            ))
        # Transform the direction vectors from the coordinate system of the
        # antenna element to the global coordinate system.
        transformed = self._orient(coordinates)
        # Transform the transformed direction vectors from Cartesian
        # coordinates to spherical coordinates.
        _, transformed_azimuth, transformed_elevation = (
            CartesianCoordinates.transform_to_spherical_arrays(
                x=transformed[0],
                y=transformed[1],
                z=transformed[2],
            ))
        return self.antenna.calculate_pattern(
            transformed_azimuth,
            transformed_elevation,
        )

    def _orient(self, vectors: np.ndarray) -> np.ndarray:
        """Transform the vectors according to the orientation of the antenna
        element.

        This operation corresponds to transforming the vector from the
        coordinate system of the antenna element to the global coordinate
        system.

        Args:
            vectors: Vectors to be transformed.

        Returns:
            The transformed vectors.
        """
        rotation_matrix = self.orientation.rotation_matrix()
        return np.tensordot(rotation_matrix, vectors, axes=((1), (0)))


class AntennaArrayArrival:
    """Antenna array arrival.

    Attributes:
        spherical_coordinates: Spherical coordinates.
        amplitude: Amplitude.
        offset: Phase offset in radians at the origin.
    """

    def __init__(
        self,
        azimuth: float = 0,
        elevation: float = 0,
        coordinates: SphericalCoordinates = None,
        offset: float = 0,
        amplitude: float = 1,
    ) -> None:
        self.spherical_coordinates = coordinates
        if self.spherical_coordinates is None:
            self.spherical_coordinates = SphericalCoordinates(
                range=1,
                azimuth=azimuth,
                elevation=elevation,
            )
        self.offset = offset
        self.amplitude = amplitude

    @property
    def azimuth(self) -> float:
        """Returns the azimuth in radians."""
        return self.spherical_coordinates.azimuth

    @property
    def elevation(self) -> float:
        """Returns the elevation in radians."""
        return self.spherical_coordinates.elevation

    def direction(self) -> np.ndarray:
        """Returns the unit direction vector."""
        return (
            self.spherical_coordinates.transform_to_cartesian().coordinates())


class AntennaArrayBeamSteer:
    """Antenna array beam steer.

    Attributes:
        coordinates: Spherical coordinates.
    """

    def __init__(
        self,
        azimuth: float = 0,
        elevation: float = 0,
        coordinates: SphericalCoordinates = None,
    ) -> None:
        self.spherical_coordinates = coordinates
        if self.spherical_coordinates is None:
            self.spherical_coordinates = SphericalCoordinates(
                range=1,
                azimuth=azimuth,
                elevation=elevation,
            )

    @property
    def azimuth(self) -> float:
        """Returns the azimuth in radians."""
        return self.spherical_coordinates.azimuth

    @property
    def elevation(self) -> float:
        """Returns the elevation in radians."""
        return self.spherical_coordinates.elevation

    def direction(self) -> np.ndarray:
        """Returns the unit direction vector."""
        return (
            self.spherical_coordinates.transform_to_cartesian().coordinates())


class AntennaArray:
    """Antenna array.

    Attributes:
        elements: Array elements.
    """

    def __init__(self, elements: list[AntennaArrayElement]) -> None:
        self.elements = elements

    @classmethod
    def create(
        cls,
        antenna_array_config: AntennaArrayConfig,
    ) -> Self:
        """Creates an antenna array according to the configuration.

        Args:
            antenna_array_config: Antenna array configuration.

        Returns:
            The antenna array instance.
        """
        elements = [
            AntennaArrayElement.create(antenna_array_element_config)
            for antenna_array_element_config in
            antenna_array_config.antenna_array_element_configs
        ]
        return cls(elements)

    def calculate_radiation_pattern(
        self,
        beam_steer: AntennaArrayBeamSteer,
        azimuth: float | np.ndarray,
        elevation: float | np.ndarray,
    ) -> np.ndarray:
        """Calculates the radiation pattern of the antenna array at the given
        azimuths and elevations.

        Args:
            beam_steer: Antenna array beam steering direction.
            azimuth: Azimuth angles in radians.
            elevation: Elevation angles in radians.

        Returns:
            The radiation pattern of the antenna array.
        """
        direction = beam_steer.direction()
        pattern_directions = np.array(
            SphericalCoordinates.transform_to_cartesian_arrays(
                range=1,
                azimuth=azimuth,
                elevation=elevation,
            ))
        return np.sum(
            [
                np.sqrt(element.calculate_pattern(azimuth, elevation)) *
                np.exp(-1j * 2 * np.pi *
                       np.dot(element.coordinates(), direction)) *
                np.exp(1j * 2 * np.pi * np.tensordot(
                    pattern_directions,
                    element.coordinates(),
                    axes=((0), (0)),
                )) for element in self.elements
            ],
            axis=0,
        )**2

    def get_spatial_samples(
        self,
        arrivals: AntennaArrayArrival | list[AntennaArrayArrival],
        amplitude: float | np.ndarray = 1,
    ) -> np.ndarray:
        """Generates the spatial samples for the given arrivals.

        This function assumes that the far field approximation is valid.

        Args:
            arrivals: Antenna array arrivals.
            amplitude: Amplitude scaling factor.

        Returns:
            The spatial samples for each antenna array element.
        """
        if isinstance(arrivals, list):
            return np.sum(
                [
                    self._get_spatial_samples_for_arrival(
                        arrival,
                        amplitude,
                    ) for arrival in arrivals
                ],
                axis=0,
            )
        return self._get_spatial_samples_for_arrival(arrivals, amplitude)

    def _get_spatial_samples_for_arrival(
        self,
        arrival: AntennaArrayArrival,
        amplitude: float | np.ndarray,
    ) -> np.ndarray:
        """Returns the spatial samples for the given arrival.

        Args:
            arrival: Antenna array arrival.
            amplitude: Amplitude scaling factor.

        Returns:
            Spatial samples for each antenna array element.
        """
        direction = arrival.direction()
        return amplitude * arrival.amplitude * np.array([
            np.sqrt(
                element.calculate_pattern(
                    arrival.azimuth,
                    arrival.elevation,
                )) *
            np.exp(-1j * (2 * np.pi * np.dot(element.coordinates(), direction) +
                          arrival.offset)) for element in self.elements
        ])
