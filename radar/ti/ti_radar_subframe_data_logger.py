"""The TI radar subframe data logger is a radar subframe data handler that logs
the subframe data received and parsed from the radar.
"""

from absl import logging

from radar.ti.ti_radar_subframe_data import (TiRadarSubframeData,
                                             TiRadarSubframeDataType)
from radar.ti.ti_radar_subframe_data_handler import TiRadarSubframeDataHandler


class TiRadarSubframeDataLogger(TiRadarSubframeDataHandler):
    """TI radar subframe data logger.

    The radar subframe data logger logs a summary of the received subframe
    data.
    """

    def handle_subframe_data(self, subframe_data: TiRadarSubframeData) -> None:
        """Handles the radar subframe data.

        Args:
            subframe_data: Radar subframe data.
        """
        header = subframe_data.get_data(TiRadarSubframeDataType.HEADER)
        logging.info((
            "Received subframe data for frame number %d and subframe number %d. "
            "Number of detected objects: %d, number of TLVs: %d."),
                     header.get("frame_number"), header.get("subframe_number"),
                     header.get("num_detected_objects"), header.get("num_tlvs"))
