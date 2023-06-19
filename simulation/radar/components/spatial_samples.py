"""The spatial samples encode the phase information of the target at each
virtual antenna.

The spatial samples are generated after range and Doppler processing by selecting
the range-Doppler values corresponding to the target for each virtual antenna.
They are then stored in a 2D array corresponding to the location of the virtual
antenna.
"""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from simulation.radar.processors.range_doppler_processor import \
    RangeDopplerProcessor


class SpatialSamples(Samples):
    """Represents spatial samples."""

    def __init__(self, radar: Radar, target: Target,
                 range_doppler_map: RangeDopplerProcessor):
        range_bin_index, doppler_bin_index = radar.get_range_doppler_bin_indices(
            target)
        spatial_samples = np.zeros(
            (
                np.max(radar.d_tx_ver[:radar.N_tx]) +
                np.max(radar.d_rx_ver[:radar.N_rx]) + 1,
                np.max(radar.d_tx_hor[:radar.N_tx]) +
                np.max(radar.d_rx_hor[:radar.N_rx]) + 1,
            ),
            dtype=range_doppler_map.samples.dtype,
        )
        spatial_samples[
            radar.d_rx_ver[:radar.N_rx],
            radar.d_rx_hor[:radar.N_rx]] = range_doppler_map.samples[
                range(radar.N_rx), doppler_bin_index, range_bin_index]
        super().__init__(spatial_samples)
