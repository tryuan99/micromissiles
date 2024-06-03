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
        # Log the header information.
        header = subframe_data.get_data(TiRadarSubframeDataType.HEADER)
        logging.info("Platform: %X, version: %08x", header.get("platform"),
                     header.get("version"))
        logging.info(
            ("Received subframe data for frame number %d and subframe number "
             "%d. Number of detected objects: %d, number of TLVs: %d, packet "
             "length: %d."), header.get("frame_number"),
            header.get("subframe_number"), header.get("num_detected_objects"),
            header.get("num_tlvs"), header.get("packet_length"))

        # Log the detected objects.
        num_detected_objects = header.get("num_detected_objects")
        detected_objects = subframe_data.get_data(
            TiRadarSubframeDataType.DETECTED_OBJECTS)
        for i in range(num_detected_objects):
            detected_object = detected_objects.get("objects", i)
            logging.info(
                "Detected object %d: x: %f, y: %f, z: %f, Doppler: %f.", i + 1,
                detected_object.get("x"), detected_object.get("y"),
                detected_object.get("z"), detected_object.get("doppler"))
