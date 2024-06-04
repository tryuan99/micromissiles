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

    @staticmethod
    def _parse_data(data: bytes) -> TiRadarSubframeData:
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
            try:
                TiRadarSubframeDataParser._validate_tlv(data_type, length,
                                                        index, len(data))
            except Exception as e:
                logging.exception("Failed to parse TLV: %s", e)
                break

            # Parse the corresponding data.
            subframe_data.add_data(TiRadarSubframeDataType(data_type),
                                   data[index:index + length])
            index += length
        return subframe_data

    @staticmethod
    def _validate_tlv(data_type: int, length: int, index: int,
                      data_length: int) -> None:
        """Validates the data type and the length.

        Args:
            data_type: Subframe data type.
            length: Length of the data type.
            index: Index within the data buffer.
            data_length: Data buffer length.

        Raises:
            ValueError: If the data type or the length fails validation.
        """
        # Validate the data type.
        # TODO(titan): In Python 3.12, use the in statement.
        try:
            TiRadarSubframeDataType(data_type)
        except ValueError as e:
            raise ValueError(
                f"TLV contains an invalid data type: {data_type}.") from e
        if (TiRadarSubframeDataType(data_type) == (
                TiRadarSubframeDataType.HEADER)):
            raise ValueError(f"TLV contains an invalid data type: {data_type}.")

        # Validate the length.
        if index + length > data_length:
            raise ValueError(f"TLV contains an invalid length: {length}.")
