"""The antenna array class simulates the behavior and performance of an antenna
array.

The boresight of the antenna array is in the positive z-direction while a
planar antenna array will lie in the x-y plane.
"""

import numpy as np


class AntennaArrayElement:
    """Antenna array element.

    Attributes:
        x: x-coordinate in units of lambda.
        y: y-coordinate in units of lambda.
        z: z-coordinate in units of lambda.
    """

    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    @property
    def coordinates(self) -> np.ndarray:
        """Returns the Cartesian coordiantes."""
        return np.array([self.x, self.y, self.z])


class AntennaArrayArrival:
    """Antenna array arrival.

    Attributes:
        azimuth: Azimuth in radians.
        elevation: Elevation in radians.
        amplitude: Amplitude.
        offset: Phase offset at the origin.
    """

    def __init__(self,
                 azimuth: float = 0,
                 elevation: float = 0,
                 offset: float = 0,
                 amplitude: float = 1) -> None:
        self.azimuth = azimuth
        self.elevation = elevation
        self.offset = offset
        self.amplitude = amplitude


class AntennaArray:
    """Antenna array.

    Attributes:
        elements: Array elements.
    """

    def __init__(self, elements: list[AntennaArrayElement]) -> None:
        self.elements = elements

    def get_spatial_samples(self,
                            arrivals: AntennaArrayArrival |
                            list[AntennaArrayArrival],
                            amplitude: float | np.ndarray = 1) -> np.ndarray:
        """Generates the spatial samples for the given arrivals.

        This function assumes that the far field approximation is valid.

        Args:
            arrivals: Antenna array arrivals.
            amplitude: Amplitude scaling factor.

        Returns:
            The spatial samples for each antenna array element.
        """
        if isinstance(arrivals, list):
            spatial_samples = np.zeros(len(self.elements), dtype=np.complex128)
            for arrival in arrivals:
                spatial_samples += self._get_spatial_samples_for_arrival(
                    arrival, amplitude)
            return spatial_samples
        return self._get_spatial_samples_for_arrival(arrivals, amplitude)

    def _get_spatial_samples_for_arrival(self, arrival: AntennaArrayArrival,
                                         amplitude: float | np.ndarray) -> np.ndarray:
        """Returns the spatial samples for the given arrival.

        Args:
            arrival: Antenna array arrival.
            amplitude: Amplitude scaling factor.

        Returns:
            Spatial samples for each antenna array element.
        """
        # Calculate the unit direction vector.
        z = np.cos(arrival.azimuth) * np.cos(arrival.elevation)
        x = -np.tan(arrival.azimuth) * z
        y = np.tan(arrival.elevation) * np.sqrt(x**2 + z**2)
        direction = np.array([x, y, z])
        return amplitude * arrival.amplitude * np.array([
            np.exp(-1j * (2 * np.pi * np.dot(element.coordinates, direction) +
                          arrival.offset)) for element in self.elements
        ])
