"""The direction-of-arrival MUSIC estimator performs direction-of-arrival
estimation using the multiple signal classification (MUSIC) algorithm.

See https://ieeexplore.ieee.org/document/1143830 for the paper and
https://www.mathworks.com/help/phased/ug/music-super-resolution-doa-estimation.html
for more details.
"""

import numpy as np

from simulation.radar.components.coordinates import (CartesianCoordinates,
                                                     PolarCoordinates)
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.spatial_samples import SpatialSamples
from simulation.radar.doa.doa_estimator import DoaEstimator

# Number of targets in the azimuth-elevation spectrum.
NUM_TARGETS = 1


class DoaMusicEstimator(DoaEstimator):
    """Performs direction-of-arrival estimation using the MUSIC algorithm.

    The spatial samples matrix and virtual antenna array are flattened in
    row-major order, so elevation is the slow index and azimuth is the fast
    index.
    """

    def __init__(self,
                 radar: Radar,
                 samples: SpatialSamples,
                 num_snapshots: int = 1):
        super().__init__(radar, samples)
        self.num_snapshots = num_snapshots

    def process_spatial_samples(self) -> None:
        """Processes the spatial samples by running the MUSIC algorithm."""
        covariance_matrix = self._get_covariance_matrix()
        # Find the noise subspace, which is equivalent to the null subspace of
        # the covariance matrix.
        _, _, Vh = np.linalg.svd(covariance_matrix, hermitian=True)
        noise_subspace_h = Vh[NUM_TARGETS:]

        # Project the arrival vectors onto the noise subspace.
        arrival_vectors = self._get_arrival_vectors()
        arrival_vectors_projection = arrival_vectors @ noise_subspace_h.T
        arrival_vectors_projection_norm_squared = np.linalg.norm(
            arrival_vectors_projection, axis=2)**2
        self.samples = Samples(1 / arrival_vectors_projection_norm_squared)

    def estimate_doa(self) -> tuple[float, float]:
        """Estimates the direction-of-arrival.

        Returns:
            A tuple consisting of the estimated (elevation, azimuth) in rad.
        """
        elevation_bin_index, azimuth_bin_index = np.unravel_index(
            np.argmax(self.samples.get_abs_samples()), self.samples.shape)
        return self.radar.el_axis[elevation_bin_index], self.radar.az_axis[
            azimuth_bin_index]

    def _get_covariance_matrix(self) -> np.ndarray:
        """Calculates the sensor covariance matrix.

        Returns:
            Sensor covariance matrix.
        """
        # TODO(titan): Use multiple snapshots to estimate the sensor covariance
        # matrix.
        return np.outer(self.samples.samples,
                        np.conjugate(self.samples.samples))

    def _get_antenna_coordinates(self) -> tuple[np.ndarray]:
        """Gets the azimuth and elevation coordinates of the flattened virtual
        antenna array in units of lambda/2.

        Returns:
            A tuple consisting of two flattened arrays with the (elevation,
            azimuth) coordinates of each virtual antenna in units of lambda/2.
        """
        antenna_azimuth_coordinates, antenna_elevation_coordinates = np.meshgrid(
            np.arange(self.samples.shape[1]), np.arange(self.samples.shape[0]))
        antenna_azimuth_coordinates = antenna_azimuth_coordinates.flatten()
        antenna_elevation_coordinates = antenna_elevation_coordinates.flatten()
        return antenna_azimuth_coordinates, antenna_elevation_coordinates

    def _get_direction_vectors(self) -> CartesianCoordinates:
        """Gets the unit direction vectors for every azimuth and elevation
        hypothesis.

        Returns:
            The Cartesian coordinates of the unit direction vectors.
        """
        elevation, azimuth = np.meshgrid(self.radar.el_axis, self.radar.az_axis)
        polar_coordinates = PolarCoordinates(1, azimuth, elevation)
        return polar_coordinates.transform_to_cartesian()

    def _get_arrival_vectors(self) -> np.ndarray:
        """Gets the arrival vectors for every azimuth and elevation hypothesis.

        Returns:
            The arrival vectors for every azimuth and elevation hypothesis and
            every virtual antenna.

        The arrival vector contains the relative theoretical phase offset at
        each virtual antenna of a signal from a target at the given azimuth and
        elevation.
        """
        (antenna_azimuth_coordinates,
         antenna_elevation_coordinates) = self._get_antenna_coordinates()
        direction_vectors = self._get_direction_vectors().coordinates
        arrival_vectors = np.zeros(
            (len(self.radar.el_axis), len(
                self.radar.az_axis), self.samples.samples.size),
            dtype=np.complex128)
        for antenna_index in range(self.samples.samples.size):
            # Project the position vector of each virtual antenna onto the unit
            # direction vector to find the phase offset at each virtual antenna.
            antenna_azimuth_coordinate = antenna_azimuth_coordinates[
                antenna_index]
            antenna_elevation_coordinate = antenna_elevation_coordinates[
                antenna_index]
            arrival_vectors[:, :, antenna_index] = np.exp(
                -1j * 2 * np.pi * (direction_vectors.T @ np.array([
                    antenna_azimuth_coordinate, antenna_elevation_coordinate, 0
                ]) / 2))
        return arrival_vectors
