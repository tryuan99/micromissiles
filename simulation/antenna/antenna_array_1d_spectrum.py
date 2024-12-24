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
            if element.cartesian_coordinates.y != 0:
                raise ValueError(
                    "All antenna array elements must lie on a horizontal plane."
                )
        super().__init__(array)

    def calculate_azimuth_spectrum(
        self,
        arrivals: AntennaArrayArrival | list[AntennaArrayArrival],
        azimuth: np.ndarray,
    ) -> np.ndarray:
        """Calculates the azimuth spectrum of the antenna array.

        Args:
            arrivals: Antenna array arrivals.
            azimuth: Azimuth angles in radians.

        Returns:
            The spectrum of the antenna array.
        """
        # Calculate the signal.
        spatial_samples = self.array.get_spatial_samples(arrivals)

        # Calculate the DFT matrix.
        dft = np.array([
            self.array.get_spatial_samples(AntennaArrayArrival(azimuth=azimuth))
            for azimuth in azimuth
        ])
        return np.conj(dft) @ spatial_samples

    def calculate_elevation_spectrum(
        self,
        arrivals: AntennaArrayArrival | list[AntennaArrayArrival],
        elevation: np.ndarray,
    ) -> np.ndarray:
        """Calculates the elevation spectrum of the antenna array.

        Args:
            arrivals: Antenna array arrivals.
            elevation: Elevation angles in radians.

        Returns:
            The spectrum of the antenna array.
        """
        return np.zeros(len(self.array.elements))
