"""The TI radar subframe data aggregator is a radar data handler that
aggregates the received bytes belonging to each subframe and parses the
subframe data into the individual radar subframe data types.
"""

from enum import Enum, auto

from absl import logging

from radar.ti.ti_radar_data_handler import TiRadarDataHandler
from radar.ti.ti_radar_subframe_data import (
    TI_RADAR_SUBFRAME_DATA_HEADER_MAGIC_WORD,
    TI_RADAR_SUBFRAME_MAX_NUM_DETECTED_OBJECTS, TiRadarSubframeDataHeader)
from radar.ti.ti_radar_subframe_data_handler import TiRadarSubframeDataHandler
from radar.ti.ti_radar_subframe_data_parser import TiRadarSubframeDataParser


class TiRadarSubframeDataAggregatorState(Enum):
    """TI radar subframe data aggregator state enumeration."""
    WAITING_FOR_HEADER = auto()
    RECEIVING_HEADER = auto()
    RECEIVING_SUBFRAME_DATA = auto()
    FINISHED_SUBFRAME = auto()


class TiRadarSubframeDataAggregator(TiRadarDataHandler):
    """TI radar subframe data aggregator.

    Attributes:
        buffer: A bytearray containing the received bytes for the subframe
          data.
        state: The current aggregator state.
        remaining_header_length: An integer denoting the number of remaining
          bytes for the header.
        remaining_subframe_data_length: An integer denoting the number of
          remaining bytes for the subframe data.
        subframe_data_handlers: A list of TI radar subframe handlers to handle
          the received subframe data.
    """

    def __init__(self) -> None:
        self.buffer: bytearray = None
        self.state: TiRadarSubframeDataAggregatorState = None
        self._reset_for_next_subframe()

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
                        self._reset_for_next_subframe()
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
                        try:
                            self._validate_header(header)
                        except Exception as e:
                            logging.exception("Failed to validate header: %s",
                                              e)
                            self._reset_for_the_next_subframe()
                        else:
                            if self.remaining_subframe_data_length > 0:
                                self.state = (TiRadarSubframeDataAggregatorState
                                              .RECEIVING_SUBFRAME_DATA)
                            else:
                                self.state = (TiRadarSubframeDataAggregatorState
                                              .FINISHED_SUBFRAME)
                case TiRadarSubframeDataAggregatorState.RECEIVING_SUBFRAME_DATA:
                    if self.remaining_subframe_data_length == 0:
                        # The entire subframe data was received.
                        self.state = (TiRadarSubframeDataAggregatorState.
                                      FINISHED_SUBFRAME)

            if self.state == TiRadarSubframeDataAggregatorState.FINISHED_SUBFRAME:
                # Parse the subframe data.
                parser = TiRadarSubframeDataParser(self.buffer)
                subframe_data = parser.subframe_data

                # Handle the subframe data.
                # TODO(titan): This can be multithreaded for better performance.
                for handler in self.subframe_data_handlers:
                    try:
                        handler.handle_subframe_data(subframe_data)
                    except Exception as e:
                        logging.exception("Failed to handle subframe data: %s",
                                          e)

                # Reset for the next subframe.
                self._reset_for_next_subframe()

    def _reset_for_next_subframe(self) -> None:
        """Resets for the next subframe."""
        self.buffer = bytearray()
        self.state = TiRadarSubframeDataAggregatorState.WAITING_FOR_HEADER

    @staticmethod
    def _validate_header(header: TiRadarSubframeDataHeader) -> None:
        """Validates the radar subframe data header.

        Raises:
            ValueError: If the header fails validation.
        """
        # Maximum packet length in bytes.
        MAX_PACKET_LENGTH = 921600 / 8

        # Maximum number of TLVs.
        MAX_NUM_TLVS = 8

        # Maximum subframe number.
        MAX_SUBFRAME_NUMBER = 10

        packet_length = header.get("packet_length")
        if packet_length > MAX_PACKET_LENGTH:
            raise ValueError(
                f"Packet length of {packet_length} exceeds the maximum packet "
                f"length of {MAX_PACKET_LENGTH}.")
        num_detected_objects = header.get("num_detected_objects")
        if num_detected_objects > TI_RADAR_SUBFRAME_MAX_NUM_DETECTED_OBJECTS:
            raise ValueError(
                f"Number of detected objects {num_detected_objects} exceeds "
                f"the maximum number of detected objects "
                f"{TI_RADAR_SUBFRAME_MAX_NUM_DETECTED_OBJECTS}.")
        num_tlvs = header.get("num_tlvs")
        if num_tlvs > MAX_NUM_TLVS:
            raise ValueError(
                f"Number of TLVs {num_tlvs} exceeds the maximum number of TLVs "
                f"{MAX_NUM_TLVS}.")
        subframe_number = header.get("subframe_number")
        if subframe_number > MAX_SUBFRAME_NUMBER:
            raise ValueError(
                f"Subframe number {subframe_number} exceeds the maximum "
                f"subframe number {MAX_SUBFRAME_NUMBER}.")
