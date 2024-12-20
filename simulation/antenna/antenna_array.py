"""The antenna array class simulates the behavior and performance of an antenna
array.

The boresight of the antenna array is in the positive z-direction while a
planar antenna array will lie in the x-y plane.
"""

import numpy as np

from simulation.antenna.antenna import Antenna
from simulation.antenna.isotropic_antenna import IsotropicAntenna
from utils.coordinates import CartesianCoordinates, SphericalCoordinates
from utils.quaternion import RotationQuaternion


class AntennaArrayElement:
    """Antenna array element.

    Attributes:
        cartesian_coordinates: Cartesian coordinates.
        orientation: Orientation of the antenna element.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        coordinates: CartesianCoordinates = None,
        antenna: Antenna = None,
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
        if self.antenna is None:
            self.antenna = IsotropicAntenna()
        self.orientation = orientation

    def coordinates(self) -> np.ndarray:
        """Returns the Cartesian coordinates."""
        return self.cartesian_coordinates.coordinates()


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
                rnge=1,
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
        return self.spherical_coordinates.transform_to_cartesian().coordinates()


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
                rnge=1,
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
        return self.spherical_coordinates.transform_to_cartesian().coordinates()


class AntennaArray:
    """Antenna array.

    Attributes:
        elements: Array elements.
    """

    def __init__(self, elements: list[AntennaArrayElement]) -> None:
        self.elements = elements

    def calculate_radiation_pattern(
        self,
        beam_steer: AntennaArrayBeamSteer,
        azimuth: np.ndarray,
        elevation: np.ndarray,
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
        pattern_directions = np.moveaxis(
            SphericalCoordinates.transform_to_cartesian_arrays(
                np.ones(np.broadcast_shapes(azimuth.shape, elevation.shape)),
                azimuth,
                elevation,
            ), 0, -1)
        return np.sum(
            [
                element.antenna.calculate_pattern(azimuth, elevation) *
                np.exp(-1j * 2 * np.pi *
                       np.dot(element.coordinates(), direction)) *
                np.exp(1j * 2 * np.pi *
                       np.dot(pattern_directions, element.coordinates()))
                for element in self.elements
            ],
            axis=0,
        )

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
            spatial_samples = np.zeros(
                len(self.elements),
                dtype=np.complex128,
            )
            for arrival in arrivals:
                spatial_samples += self._get_spatial_samples_for_arrival(
                    arrival,
                    amplitude,
                )
            return spatial_samples
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
        return (amplitude * arrival.amplitude * np.array([
            element.antenna.calculate_pattern(
                arrival.azimuth,
                arrival.elevation,
            ) * np.exp(-1j *
                       (2 * np.pi * np.dot(element.coordinates(), direction) +
                        arrival.offset)) for element in self.elements
        ]))
