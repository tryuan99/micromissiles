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
            ("Received subframe data for frame number %u and subframe number "
             "%u. Number of detected objects: %u, number of TLVs: %u, packet "
             "length: %u."), header.get("frame_number"),
            header.get("subframe_number"), header.get("num_detected_objects"),
            header.get("num_tlvs"), header.get("packet_length"))

        # Log the detected objects.
        num_detected_objects = header.get("num_detected_objects")
        detected_objects = subframe_data.get_data(
            TiRadarSubframeDataType.DETECTED_OBJECTS)
        for i in range(num_detected_objects):
            detected_object = detected_objects.get("objects", i)
            logging.info(
                ("Detected object %d: range bin: %u, Doppler bin: %u, "
                 "range: %f, Doppler: %f, azimuth: %f, elevation: %f."), i + 1,
                detected_object.get("range_bin"),
                detected_object.get("doppler_bin"),
                detected_object.get("range"), detected_object.get("doppler"),
                detected_object.get("azimuth"),
                detected_object.get("elevation"))
