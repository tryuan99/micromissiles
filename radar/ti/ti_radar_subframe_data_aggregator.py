"""The TI radar subframe data aggregator is a radar data handler that
aggregates the received bytes belonging to each subframe and parses the
subframe data into the individual radar subframe data types.
"""

from enum import Enum, auto

from absl import logging

from radar.ti.ti_radar_data_handler import TiRadarDataHandler
from radar.ti.ti_radar_subframe_data import (
    TI_RADAR_SUBFRAME_DATA_HEADER_MAGIC_WORD, TiRadarSubframeDataHeader)
from radar.ti.ti_radar_subframe_data_handler import TiRadarSubframeDataHandler
from radar.ti.ti_radar_subframe_data_parser import TiRadarSubframeDataParser


class TiRadarSubframeDataAggregatorState(Enum):
    """TI radar subframe data aggregator state enumeration."""
    WAITING_FOR_HEADER = auto()
    RECEIVING_HEADER = auto()
    RECEIVING_SUBFRAME_DATA = auto()
    FINISHED_SUBFRAME = auto()


class TiRadarSubframeDataAggregator(TiRadarDataHandler):
    """TI radar subframe data aggregator."""

    def __init__(self) -> None:
        self.state = TiRadarSubframeDataAggregatorState.WAITING_FOR_HEADER
        self.buffer = bytearray()
        self.remaining_header_length = 0
        self.remaining_subframe_data_length = 0
        self.subframe_data_handlers: list[TiRadarSubframeDataHandler] = []

    def add_subframe_data_handler(self,
                                  handler: TiRadarSubframeDataHandler) -> None:
        """Adds a radar subframe data handler.

        Args:
            handler: Radar subframe data handler.
        """
        self.subframe_data_handlers.append(handler)

    def receive_data(self, data: bytes) -> None:
        """Receives data from the radar.

        Args:
            data: Received data.
        """
        for byte in data:
            self.buffer.append(byte)
            self.remaining_header_length -= 1
            self.remaining_subframe_data_length -= 1
            match self.state:
                case TiRadarSubframeDataAggregatorState.WAITING_FOR_HEADER:
                    # Look for the magic word in the header.
                    if not TI_RADAR_SUBFRAME_DATA_HEADER_MAGIC_WORD.startswith(
                            self.buffer):
                        self.buffer = bytearray()
                    elif self.buffer == TI_RADAR_SUBFRAME_DATA_HEADER_MAGIC_WORD:
                        # The magic word was received.
                        self.state = (
                            TiRadarSubframeDataAggregatorState.RECEIVING_HEADER)
                        self.remaining_header_length = (
                            TiRadarSubframeDataHeader.size() -
                            len(TI_RADAR_SUBFRAME_DATA_HEADER_MAGIC_WORD))
                case TiRadarSubframeDataAggregatorState.RECEIVING_HEADER:
                    if self.remaining_header_length == 0:
                        # The entire header was received, so parse the header.
                        header = TiRadarSubframeDataHeader(self.buffer)
                        self.remaining_subframe_data_length = (
                            header.get("packet_length") -
                            TiRadarSubframeDataHeader.size())
                        if self.remaining_subframe_data_length > 0:
                            self.state = (TiRadarSubframeDataAggregatorState.
                                          RECEIVING_SUBFRAME_DATA)
                        else:
                            self.state = (TiRadarSubframeDataAggregatorState.
                                          FINISHED_SUBFRAME)
                case TiRadarSubframeDataAggregatorState.RECEIVING_SUBFRAME_DATA:
                    if self.remaining_subframe_data_length == 0:
                        # The entire subframe data was received.
                        self.state = (TiRadarSubframeDataAggregatorState.
                                      FINISHED_SUBFRAME)

            if self.state == TiRadarSubframeDataAggregatorState.FINISHED_SUBFRAME:
                # Parse the subframe data.
                try:
                    parser = TiRadarSubframeDataParser(self.buffer)
                except Exception as e:
                    logging.error("Failed to parse radar subframe data: %s.", e)
                else:
                    subframe_data = parser.subframe_data

                    # Handle the subframe data.
                    # TODO(titan): This can be multithreaded for better performance.
                    for handler in self.subframe_data_handlers:
                        handler.handle_subframe_data(subframe_data)

                # Reset for the next subframe.
                self.buffer = bytearray()
                self.state = TiRadarSubframeDataAggregatorState.WAITING_FOR_HEADER
