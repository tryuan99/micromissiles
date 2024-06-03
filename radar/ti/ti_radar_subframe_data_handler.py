"""The TI radar subframe data handler defines the interface for handling the
radar subframe data.
"""

from abc import ABC, abstractmethod

from radar.ti.ti_radar_subframe_data import TiRadarSubframeData


class TiRadarSubframeDataHandler(ABC):
    """Interface for a radar subframe data handler."""

    @abstractmethod
    def handle_subframe_data(self, subframe_data: TiRadarSubframeData) -> None:
        """Handles the radar subframe data.

        Args:
            subframe_data: Radar subframe data.
        """
