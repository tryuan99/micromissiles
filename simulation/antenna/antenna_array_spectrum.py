"""The antenna array spectrum class is an interface for calculating the
spectrum of an antenna array.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.antenna.antenna_array import AntennaArray, AntennaArrayArrival


class AntennaArraySpectrum(ABC):
    """Interface for an antenna array spectrum.

    Attributes:
        array: Antenna array.
    """

    def __init__(self, array: AntennaArray) -> None:
        self.array = array

    @abstractmethod
    def calculate_azimuth_spectrum(self, arrivals: AntennaArrayArrival |
                                   list[AntennaArrayArrival],
                                   theta: np.ndarray) -> np.ndarray:
        """Calculates the azimuth spectrum of the antenna array.

        Args:
            arrivals: Antenna array arrivals.
            theta: Azimuth angles.

        Returns:
            The spectrum of the antenna array.
        """

    @abstractmethod
    def calculate_elevation_spectrum(self, arrivals: AntennaArrayArrival |
                                     list[AntennaArrayArrival],
                                     phi: np.ndarray) -> np.ndarray:
        """Calculates the elevation spectrum of the antenna array.

        Args:
            arrivals: Antenna array arrivals.
            phi: Elevation angles.

        Returns:
            The spectrum of the antenna array.
        """
