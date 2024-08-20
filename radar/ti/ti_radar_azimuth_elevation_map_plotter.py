"""The TI radar azimuth-elevation map plotter is a radar subframe data handler
that parses the spatial samples and plots the azimuth-elevation map.
"""

from abc import ABC, abstractmethod
from threading import Lock

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from matplotlib import animation, artist

from radar.ti.ti_radar_config import TiRadarConfig
from radar.ti.ti_radar_subframe_data import (TiRadarSubframeData,
                                             TiRadarSubframeDataDetectedObject,
                                             TiRadarSubframeDataType)
from radar.ti.ti_radar_subframe_data_handler import TiRadarSubframeDataHandler
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS


class TiRadarAzimuthElevationMapPlotter(TiRadarSubframeDataHandler, ABC):
    """TI radar azimuth-elevation map plotter."""

    def __init__(self, config: TiRadarConfig, rnge: float,
                 num_azimuth_bins: int, num_elevation_bins: int,
                 animation_interval: float, mark_detections: bool,
                 mark_peak: bool) -> None:
        super().__init__()
        self.config = config
        self.range = rnge
        self.num_azimuth_bins = num_azimuth_bins
        self.num_elevation_bins = num_elevation_bins
        self.animation_interval = animation_interval
        self.mark_detections = mark_detections
        self.mark_peak = mark_peak

        self.detected_object: TiRadarSubframeDataDetectedObject = None
        self.azimuth_elevation_map = (np.zeros(
            (self.num_elevation_bins, self.num_azimuth_bins)))
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
            self.detected_object = detected_object
            self.azimuth_elevation_map = azimuth_elevation_map
            self.azimuth_elevation_map_has_updated = True

    @abstractmethod
    def plot(self) -> None:
        """Plots the azimuth-elevation map.

        This function blocks and should be called from the main thread.
        """


class TiRadarAzimuthElevationMapPlotter2D(TiRadarAzimuthElevationMapPlotter):
    """TI radar 2D azimuth-elevation map plotter."""

    def __init__(self, config: TiRadarConfig, rnge: float,
                 num_azimuth_bins: int, num_elevation_bins: int,
                 animation_interval: float, mark_detections: bool,
                 mark_peak: bool) -> None:
        super().__init__(config, rnge, num_azimuth_bins, num_elevation_bins,
                         animation_interval, mark_detections, mark_peak)

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
            origin="upper",
            extent=extent,
        )
        detection_peak = ax.scatter([], [], color="red", marker="D")
        peak = ax.scatter([], [], color="magenta", marker="^")

        def update_azimuth_elevation_map(
                frame: int) -> tuple[artist.Artist, ...]:
            """Updates the azimuth-elevation map.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            with self.azimuth_elevation_map_lock:
                has_updated = self.azimuth_elevation_map_has_updated
                if has_updated:
                    detection_bin = (
                        int(
                            np.sin(
                                constants.deg2rad(
                                    self.detected_object.get("azimuth"))) *
                            self.num_azimuth_bins // 2),
                        int(
                            np.sin(
                                constants.deg2rad(
                                    self.detected_object.get("elevation"))) *
                            self.num_elevation_bins // 2))
                    azimuth_elevation_map_abs = (np.abs(
                        self.azimuth_elevation_map))
                    self.azimuth_elevation_map_has_updated = False

            if has_updated:
                azimuth_elevation_map_abs_db = (
                    constants.mag2db(azimuth_elevation_map_abs))
                azimuth_elevation_map_abs_db_shifted = (
                    np.fft.fftshift(azimuth_elevation_map_abs_db))
                heatmap.set_data(azimuth_elevation_map_abs_db_shifted)
                heatmap.autoscale()

                if self.mark_detections:
                    detection_peak.set_offsets(detection_bin)
                if self.mark_peak:
                    peak_elevation_index, peak_azimuth_index = (
                        np.unravel_index(
                            np.argmax(azimuth_elevation_map_abs_db),
                            azimuth_elevation_map_abs_db.shape))
                    if peak_elevation_index >= self.num_elevation_bins // 2:
                        peak_elevation_index -= self.num_elevation_bins
                    if peak_azimuth_index >= self.num_azimuth_bins // 2:
                        peak_azimuth_index -= self.num_azimuth_bins
                    peak.set_offsets(
                        [peak_azimuth_index, -peak_elevation_index])
            return heatmap, detection_peak, peak

        anim = animation.FuncAnimation(
            fig,
            update_azimuth_elevation_map,
            interval=self.animation_interval,
            blit=True,
            cache_frame_data=False,
        )
        plt.show()


class TiRadarAzimuthElevationMapPlotter3D(TiRadarAzimuthElevationMapPlotter):
    """TI radar 3D azimuth-elevation map plotter."""

    def __init__(self, config: TiRadarConfig, rnge: float,
                 num_azimuth_bins: int, num_elevation_bins: int,
                 animation_interval: float, mark_detections: bool,
                 mark_peak: bool) -> None:
        super().__init__(config, rnge, num_azimuth_bins, num_elevation_bins,
                         animation_interval, mark_detections, mark_peak)

    def plot(self) -> None:
        """Plots the azimuth-elevation map.

        This function blocks and should be called from the main thread.
        """
        plt.style.use("science")
        fig, ax = plt.subplots(
            figsize=(12, 8),
            subplot_kw={"projection": "3d"},
        )
        ax.set_xlabel("Elevation [deg]")
        ax.set_ylabel("Azimuth [deg]")
        ax.set_title("Azimuth-elevation map")

        elevation_axis = constants.rad2deg(
            np.arcsin(
                np.linspace(-1, 1, self.num_elevation_bins, endpoint=False)))
        azimuth_axis = constants.rad2deg(
            np.arcsin(np.linspace(-1, 1, self.num_azimuth_bins,
                                  endpoint=False)))
        surf = ax.plot_surface(
            *np.meshgrid(-elevation_axis, azimuth_axis, indexing="ij"),
            constants.mag2db(
                np.zeros((self.num_elevation_bins, self.num_azimuth_bins))),
            cmap=COLOR_MAPS["parula"],
            antialiased=False,
        )
        detection_peak, = ax.plot([], [], [], color="red", marker="D")
        peak, = ax.plot([], [], [], color="magenta", marker="^")

        def update_azimuth_elevation_map(
                frame: int) -> tuple[artist.Artist, ...]:
            """Updates the azimuth-elevation map.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            with self.azimuth_elevation_map_lock:
                has_updated = self.azimuth_elevation_map_has_updated
                if has_updated:
                    detection_doa = (self.detected_object.get("elevation"),
                                     self.detected_object.get("azimuth"))
                    detection_bin = (
                        int(
                            np.sin(
                                constants.deg2rad(
                                    -self.detected_object.get("elevation"))) *
                            self.num_elevation_bins // 2),
                        int(
                            np.sin(
                                constants.deg2rad(
                                    self.detected_object.get("azimuth"))) *
                            self.num_azimuth_bins // 2))
                    azimuth_elevation_map_abs = (np.abs(
                        self.azimuth_elevation_map))
                    self.azimuth_elevation_map_has_updated = False

            if has_updated:
                azimuth_elevation_map_abs_db = (
                    constants.mag2db(azimuth_elevation_map_abs))
                azimuth_elevation_map_abs_db_shifted = (
                    np.fft.fftshift(azimuth_elevation_map_abs_db))
                nonlocal surf
                surf.remove()
                surf = ax.plot_surface(
                    *np.meshgrid(-elevation_axis, azimuth_axis, indexing="ij"),
                    azimuth_elevation_map_abs_db_shifted,
                    cmap=COLOR_MAPS["parula"],
                    antialiased=False,
                )

                if self.mark_detections:
                    detection_bin_magnitude_db = (
                        azimuth_elevation_map_abs_db[detection_bin])
                    detection_peak.set_data(*detection_doa)
                    detection_peak.set_3d_properties(detection_bin_magnitude_db)
                if self.mark_peak:
                    peak.set_data(*detection_doa)
                    peak_magnitude_db = np.max(azimuth_elevation_map_abs_db)
                    peak.set_3d_properties(peak_magnitude_db)
            return surf, detection_peak, peak

        anim = animation.FuncAnimation(
            fig,
            update_azimuth_elevation_map,
            interval=self.animation_interval,
            blit=True,
            cache_frame_data=False,
        )
        plt.show()
