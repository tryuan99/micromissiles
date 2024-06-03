"""The TI radar data logger is a radar data handler that logs data received
from the radar.
"""

from absl import logging

from radar.ti.ti_radar_data_handler import TiRadarDataHandler


class TiRadarDataLogger(TiRadarDataHandler):
    """TI radar data logger.

    The radar data logger logs all received data.
    """

    def receive_data(self, data: bytes) -> None:
        """Receives data from the radar.

        Args:
            data: Received data.
        """
        try:
            logging.info(data.decode().strip())
        except:
            logging.info(data)
