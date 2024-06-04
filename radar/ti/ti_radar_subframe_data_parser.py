"""The TI radar subframe data parser parses the bytes corresponding to a single
radar subframe to the individual radar subframe data types.
"""

from absl import logging

from radar.ti.ti_radar_subframe_data import (TiRadarSubframeData,
                                             TiRadarSubframeDataHeader,
                                             TiRadarSubframeDataType,
                                             TiRadarSubframeDataTypeLength)

# TI radar subframe data packet length multiple in bytes.
TI_RADAR_SUBFRAME_DATA_PACKET_LENGTH_MULTIPLE = 32  # bytes


class TiRadarSubframeDataParser:
    """TI radar subframe data parser."""

    def __init__(self, data: bytes) -> None:
        self.subframe_data = self._parse_data(data)

    def _parse_data(self, data: bytes) -> TiRadarSubframeData:
        """Parses the bytes into the individual radar subframe data types.

        Args:
            data: Bytes to parse.

        Returns:
            The parsed radar subframe data.
        """
        subframe_data = TiRadarSubframeData()

        # Parse the header.
        subframe_data.add_data(TiRadarSubframeDataType.HEADER,
                               data[:TiRadarSubframeDataHeader.size()])

        # Parse the TLVs.
        index = TiRadarSubframeDataHeader.size()
        while index <= (len(data) -
                        TI_RADAR_SUBFRAME_DATA_PACKET_LENGTH_MULTIPLE):
            # Parse the data type and length.
            data_type_length = TiRadarSubframeDataTypeLength(
                data[index:index + TiRadarSubframeDataTypeLength.size()])
            index += TiRadarSubframeDataTypeLength.size()
            data_type = data_type_length.get("type")
            length = data_type_length.get("length")

            # Validate the data type.
            # TODO(titan): In Python 3.12, use the in statement.
            try:
                TiRadarSubframeDataType(data_type)
            except ValueError:
                logging.warning("TLV contains an invalid data type: %u.",
                                data_type)
                break
            if (TiRadarSubframeDataType(data_type) ==
                    TiRadarSubframeDataType.HEADER):
                logging.warning("TLV contains an invalid data type: %u.",
                                data_type)
                break

            # Validate the length.
            if index + length > len(data):
                logging.warning("TLV contains an invalid length: %u.", length)
                break

            # Parse the corresponding data.
            subframe_data.add_data(TiRadarSubframeDataType(data_type),
                                   data[index:index + length])
            index += length
        return subframe_data
