"""The 1D antenna array spectrum calculates the azimuth spectrum of an antenna
array on a horizontal plane.
"""

import numpy as np

from simulation.antenna.antenna_array import AntennaArray, AntennaArrayArrival
from simulation.antenna.antenna_array_spectrum import AntennaArraySpectrum


class AntennaArray1DSpectrum(AntennaArraySpectrum):
    """1D antenna spectrum."""

    def __init__(self, array: AntennaArray) -> None:
        for element in array.elements:
            if element.y != 0:
                raise ValueError(
                    "All antenna array elements must lie on a horizontal plane."
                )
        super().__init__(array)

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
        # Calculate the signal.
        spatial_samples = self.array.get_spatial_samples(arrivals)

        # Calculate the DFT matrix.
        dft = np.zeros((len(theta), len(self.array.elements)),
                       dtype=np.complex128)
        for index, azimuth in enumerate(theta):
            dft[index] = self.array.get_spatial_samples(
                AntennaArrayArrival(azimuth=azimuth))
        return np.conj(dft) @ spatial_samples

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
        return np.zeros(len(self.array.elements))
