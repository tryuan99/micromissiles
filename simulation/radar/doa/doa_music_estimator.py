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

    def __init__(self, spatial_samples_snapshots: list[SpatialSamples],
                 radar: Radar):
        super().__init__(
            Samples(
                np.array([
                    snapshot.samples for snapshot in spatial_samples_snapshots
                ])), radar)

    def process_2d_samples(self) -> None:
        """Processes the spatial samples by running the MUSIC algorithm."""
        covariance_matrix = self._get_covariance_matrix()
        # Find the noise subspace, which is equivalent to the null subspace of
        # the covariance matrix.
        _, _, Vh = np.linalg.svd(covariance_matrix, hermitian=True)

        # Project the arrival vectors onto the signal subspace, which is
        # orthogonal to the noise subspace.
        signal_subspace_h = Vh[:NUM_TARGETS]
        arrival_vectors = self._get_arrival_vectors()
        arrival_vectors_projection = arrival_vectors @ signal_subspace_h.T
        arrival_vectors_projection_norm_squared = np.linalg.norm(
            arrival_vectors_projection, axis=2)**2
        self.samples = arrival_vectors_projection_norm_squared

    def _get_covariance_matrix(self) -> np.ndarray:
        """Calculates the sensor covariance matrix.

        Returns:
            Sensor covariance matrix.
        """
        covariance_matrices = [
            np.outer(snapshot, np.conjugate(snapshot))
            for snapshot in self.samples
        ]
        return np.mean(covariance_matrices, axis=0)

    def _get_antenna_coordinates(self) -> tuple[np.ndarray]:
        """Gets the azimuth and elevation coordinates of the flattened virtual
        antenna array in units of lambda/2.

        Returns:
            A tuple consisting of two flattened arrays with the (elevation,
            azimuth) coordinates of each virtual antenna in units of lambda/2.
        """
        antenna_azimuth_coordinates, antenna_elevation_coordinates = np.meshgrid(
            np.arange(self.shape[-1]), np.arange(self.shape[-2]))
        antenna_azimuth_coordinates = antenna_azimuth_coordinates.flatten()
        antenna_elevation_coordinates = antenna_elevation_coordinates.flatten()
        return antenna_azimuth_coordinates, antenna_elevation_coordinates

    def _get_direction_vectors(self) -> CartesianCoordinates:
        """Gets the unit direction vectors for every azimuth and elevation
        hypothesis.

        Returns:
            The Cartesian coordinates of the unit direction vectors.
        """
        elevation, azimuth = np.meshgrid(self.get_output_axis1(),
                                         self.get_output_axis2())
        polar_coordinates = PolarCoordinates(1, azimuth, elevation)
        return polar_coordinates.transform_to_cartesian()

    def _get_arrival_vectors(self) -> np.ndarray:
        """Gets the arrival vectors for every azimuth and elevation hypothesis.

        The arrival vector contains the relative theoretical phase offset at
        each virtual antenna of a signal from a target at the given azimuth and
        elevation.

        Returns:
            The arrival vectors for every azimuth and elevation hypothesis and
            every virtual antenna.
        """
        num_antennas = np.multiply.reduce(self.shape[-2:])
        (antenna_azimuth_coordinates,
         antenna_elevation_coordinates) = self._get_antenna_coordinates()
        direction_vectors = self._get_direction_vectors().coordinates
        arrival_vectors = np.zeros((*self.get_output_shape(), num_antennas),
                                   dtype=np.complex128)
        for antenna_index in range(num_antennas):
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
