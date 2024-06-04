"""The TI radar range-Doppler map plotter is a radar subframe data handler that
plots the range-Doppler map over the subframes.
"""

from threading import Lock

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from matplotlib import animation, artist

from radar.ti.ti_radar_subframe_data import (TiRadarSubframeData,
                                             TiRadarSubframeDataType)
from radar.ti.ti_radar_subframe_data_handler import TiRadarSubframeDataHandler
from utils.visualization.color_maps import COLOR_MAPS


class TiRadarRangeDopplerMapPlotter(TiRadarSubframeDataHandler):
    """TI radar range-Doppler map plotter."""

    def __init__(self, num_range_bins: int, num_doppler_bins: int,
                 animation_interval: float, mark_detections: bool) -> None:
        super().__init__()
        self.num_range_bins = num_range_bins
        self.num_doppler_bins = num_doppler_bins
        self.animation_interval = animation_interval
        self.mark_detections = mark_detections

        self.range_doppler_map = np.zeros(
            (self.num_range_bins, self.num_doppler_bins))
        self.detection_range_doppler_bins: np.ndarray = None
        self.range_doppler_map_has_updated = False
        self.range_doppler_map_lock = Lock()

    def handle_subframe_data(self, subframe_data: TiRadarSubframeData) -> None:
        """Handles the radar subframe data.

        Args:
            subframe_data: Radar subframe data.
        """
        range_doppler_map_bytes = subframe_data.get_data(
            TiRadarSubframeDataType.RANGE_DOPPLER_MAP)
        range_doppler_map = np.frombuffer(range_doppler_map_bytes,
                                          dtype=np.uint16).reshape(
                                              (self.num_range_bins,
                                               self.num_doppler_bins))
        detection_range_doppler_bins = None
        if self.mark_detections:
            num_detected_objects = subframe_data.get_data(
                TiRadarSubframeDataType.HEADER).get("num_detected_objects")
            detection_range_doppler_bins = np.array([[
                subframe_data.get_data(
                    TiRadarSubframeDataType.DETECTED_OBJECTS).get(
                        "objects", i).get("doppler_bin"),
                subframe_data.get_data(
                    TiRadarSubframeDataType.DETECTED_OBJECTS).get(
                        "objects", i).get("range_bin")
            ] for i in range(num_detected_objects)])

        with self.range_doppler_map_lock:
            self.range_doppler_map = range_doppler_map
            self.detection_range_doppler_bins = detection_range_doppler_bins
            self.range_doppler_map_has_updated = True

    def plot(self) -> None:
        """Plots the range-Doppler map.

        This function blocks and should be called from the main thread.
        """
        plt.style.use(["science"])
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlabel("Doppler bin")
        ax.set_ylabel("Range bin")
        ax.set_title("Range-Doppler map")

        extent = (
            -0.5 - self.num_doppler_bins / 2,
            self.num_doppler_bins - 0.5 - self.num_doppler_bins / 2,
            -0.5,
            self.num_range_bins - 0.5,
        )
        heatmap = ax.imshow(
            np.zeros((self.num_range_bins, self.num_doppler_bins)),
            cmap=COLOR_MAPS["parula"],
            aspect="auto",
            origin="lower",
            extent=extent,
        )
        detections = ax.scatter([], [], color="red", marker="D")

        def update_range_doppler_map(frame: int) -> tuple[artist.Artist]:
            """Updates the range-Doppler map.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            with self.range_doppler_map_lock:
                has_updated = self.range_doppler_map_has_updated
                if has_updated:
                    range_doppler_map_shifted = np.roll(self.range_doppler_map,
                                                        self.num_doppler_bins //
                                                        2,
                                                        axis=1)
                    detection_range_doppler_bins_signed = (
                        self.detection_range_doppler_bins)
                    self.range_doppler_map_has_updated = False

            if has_updated:
                heatmap.set_data(range_doppler_map_shifted)
                heatmap.autoscale()
                if self.mark_detections:
                    detection_range_doppler_bins_signed[(
                        detection_range_doppler_bins_signed[:, 0] >=
                        self.num_doppler_bins // 2), 0] -= self.num_doppler_bins
                    detections.set_offsets(detection_range_doppler_bins_signed)
            return heatmap, detections

        anim = animation.FuncAnimation(
            fig,
            update_range_doppler_map,
            interval=self.animation_interval,
            blit=True,
            cache_frame_data=False,
        )
        plt.show()
