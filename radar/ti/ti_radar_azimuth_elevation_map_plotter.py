"""The TI radar azimuth-elevation map plotter is a radar subframe data handler
that parses the spatial samples and plots the azimuth-elevation map.
"""

from threading import Lock

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from matplotlib import animation, artist

from radar.ti.ti_radar_config import TiRadarConfig
from radar.ti.ti_radar_subframe_data import (TiRadarSubframeData,
                                             TiRadarSubframeDataType)
from radar.ti.ti_radar_subframe_data_handler import TiRadarSubframeDataHandler
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS


class TiRadarAzimuthElevationMapPlotter(TiRadarSubframeDataHandler):
    """TI radar azimuth-elevation map plotter."""

    def __init__(self, config: TiRadarConfig, rnge: float,
                 num_azimuth_bins: int, num_elevation_bins: int,
                 animation_interval: float, mark_peak: bool) -> None:
        super().__init__()
        self.config = config
        self.range = rnge
        self.num_azimuth_bins = num_azimuth_bins
        self.num_elevation_bins = num_elevation_bins
        self.animation_interval = animation_interval
        self.mark_peak = mark_peak

        self.azimuth_elevation_map = np.zeros(
            (self.num_elevation_bins, self.num_azimuth_bins))
        self.azimuth_elevation_map_has_updated = False
        self.azimuth_elevation_map_lock = Lock()

    def handle_subframe_data(self, subframe_data: TiRadarSubframeData) -> None:
        """Handles the radar subframe data.

        Args:
            subframe_data: Radar subframe data.
        """
        # Find the detected object that is closest to the target range.
        num_detected_objects = subframe_data.get_data(
            TiRadarSubframeDataType.HEADER).get("num_detected_objects")
        detected_objects = subframe_data.get_data(
            TiRadarSubframeDataType.DETECTED_OBJECTS).get(
                "objects")[:num_detected_objects]
        detected_object = min(
            detected_objects,
            key=lambda obj: np.abs(self.range - obj.get("range")))

        # Re-order the spatial samples according to the virtual antenna array.
        azimuth_coordinates, elevation_coordinates = (
            self.config.virtual_antenna_array())
        spatial_samples_2d = np.zeros(
            (self.num_elevation_bins, self.num_azimuth_bins),
            dtype=np.complex128)
        spatial_samples_structs = detected_object.get("spatial_samples")
        spatial_samples = np.array([
            sample.get("real") + 1j * sample.get("imaginary")
            for sample in spatial_samples_structs
        ])
        spatial_samples_2d[elevation_coordinates,
                           azimuth_coordinates] = spatial_samples

        # Perform the azimuth-elevation FFT.
        azimuth_elevation_map = np.fft.fft2(
            spatial_samples_2d,
            (self.num_elevation_bins, self.num_azimuth_bins))

        with self.azimuth_elevation_map_lock:
            self.azimuth_elevation_map = azimuth_elevation_map
            self.azimuth_elevation_map_has_updated = True

    def plot(self) -> None:
        """Plots the azimuth-elevation map.

        This function blocks and should be called from the main thread.
        """
        plt.style.use("science")
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlabel("Azimuth bin")
        ax.set_ylabel("Elevation bin")
        ax.set_title("Azimuth-elevation map")

        extent = (
            -0.5 - self.num_azimuth_bins / 2,
            self.num_azimuth_bins - 0.5 - self.num_azimuth_bins / 2,
            -0.5 - self.num_elevation_bins / 2,
            self.num_elevation_bins - 0.5 - self.num_elevation_bins / 2,
        )
        heatmap = ax.imshow(
            np.zeros((self.num_elevation_bins, self.num_azimuth_bins)),
            cmap=COLOR_MAPS["parula"],
            aspect="auto",
            origin="lower",
            extent=extent,
        )
        peak = ax.scatter([], [], color="red", marker="D")

        def update_azimuth_elevation_map(
                frame: int) -> tuple[artist.Artist, artist.Artist]:
            """Updates the azimuth-elevation map.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            with self.azimuth_elevation_map_lock:
                has_updated = self.azimuth_elevation_map_has_updated
                if has_updated:
                    azimuth_elevation_map_abs = np.abs(
                        self.azimuth_elevation_map)
                    self.azimuth_elevation_map_has_updated = False

            if has_updated:
                azimuth_elevation_map_abs_db = constants.mag2db(
                    azimuth_elevation_map_abs)
                azimuth_elevation_map_abs_db_shifted = np.fft.fftshift(
                    azimuth_elevation_map_abs_db)
                heatmap.set_data(azimuth_elevation_map_abs_db_shifted)
                heatmap.autoscale()
                if self.mark_peak:
                    peak_elevation_index, peak_azimuth_index = (
                        np.unravel_index(
                            np.argmax(azimuth_elevation_map_abs_db),
                            azimuth_elevation_map_abs_db.shape))
                    if peak_elevation_index >= self.num_elevation_bins // 2:
                        peak_elevation_index -= self.num_elevation_bins
                    if peak_azimuth_index >= self.num_azimuth_bins // 2:
                        peak_azimuth_index -= self.num_azimuth_bins
                    peak.set_offsets([peak_azimuth_index, peak_elevation_index])
            return heatmap, peak

        anim = animation.FuncAnimation(
            fig,
            update_azimuth_elevation_map,
            interval=self.animation_interval,
            blit=True,
            cache_frame_data=False,
        )
        plt.show()
