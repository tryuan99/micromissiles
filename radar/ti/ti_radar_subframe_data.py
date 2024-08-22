"""The TI radar subframe data encapsulates the radar data outputted from the
radar for a single subframe.
"""

from enum import IntEnum
from typing import Any

from utils.struct import Struct, StructFields, StructFieldType

# TI radar subframe data header magic word. The magic word signifies the start
# of the header.
TI_RADAR_SUBFRAME_DATA_HEADER_MAGIC_WORD = b"\x02\x01\x04\x03\x06\x05\x08\x07"

# Maximum number of detected objects within a subframe.
TI_RADAR_SUBFRAME_MAX_NUM_DETECTED_OBJECTS = 50


class TiRadarSubframeDataType(IntEnum):
    """TI radar subframe data type enumeration."""
    HEADER = 0
    DETECTED_OBJECTS = 1
    RANGE_PROFILE = 2
    NOISE_FLOOR_PROFILE = 3
    AZIMUTH_MAP = 4
    RANGE_DOPPLER_MAP = 5
    STATS = 6
    DETECTED_OBJECTS_INFO = 7
    AZIMUTH_ELEVATION_MAP = 8
    TEMPERATURE = 9


class TiRadarSubframeData:
    """TI radar subframe data.

    Attributes:
        data: A map from the TI radar subframe data type to the corresponding
          data struct.
    """

    def __init__(self) -> None:
        self.data: dict[TiRadarSubframeDataType, Any] = {}
        # Initialize all radar subframe data types.
        for data_type in TiRadarSubframeDataType:
            self.data[data_type] = TI_RADAR_SUBFRAME_DATA_TYPE_TO_OUTPUT_TYPE[
                data_type]()

    def add_data(self, data_type: TiRadarSubframeDataType,
                 data: bytearray | bytes) -> None:
        """Adds data to the given radar subframe data type.

        Args:
            data_type: Radar subframe data type.
            data: Bytes to add.

        Raises:
            KeyError: If the given radar subframe data type cannot be found.
        """
        self._validate_key(data_type)
        self.data[data_type] = TI_RADAR_SUBFRAME_DATA_TYPE_TO_OUTPUT_TYPE[
            data_type](data)

    def get_data(self, data_type: TiRadarSubframeDataType) -> Any:
        """Returns the data for the given radar subframe data type.

        Args:
            data_type: Radar subframe data type.

        Raises:
            KeyError: If the given radar subframe data type cannot be found.
        """
        self._validate_key(data_type)
        return self.data[data_type]

    def _validate_key(self, data_type: TiRadarSubframeDataType) -> None:
        """Validates the radar subframe data type key.

        Args:
            data_type: Radar subframe data type.

        Raises:
            KeyError: If the given radar subframe data type cannot be found.
        """
        if data_type not in self.data:
            raise KeyError(f"Radar subframe data type {data_type} not found.")


class TiRadarComplexRealImaginary32(Struct):
    """TI radar complex number struct with 32-bit real and imaginary
    components.
    """

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "real": (StructFieldType.INT32, 1),
            "imaginary": (StructFieldType.INT32, 1),
        }


class TiRadarSubframeDataHeader(Struct):
    """TI radar subframe data header."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "magic_word": (StructFieldType.UINT16, 4),
            "version": (StructFieldType.UINT32, 1),
            "packet_length": (StructFieldType.UINT32, 1),
            "platform": (StructFieldType.UINT32, 1),
            "frame_number": (StructFieldType.UINT32, 1),
            "time_cpu_cycles": (StructFieldType.UINT32, 1),
            "num_detected_objects": (StructFieldType.UINT32, 1),
            "num_tlvs": (StructFieldType.UINT32, 1),
            "subframe_number": (StructFieldType.UINT32, 1),
        }


class TiRadarSubframeDataTypeLength(Struct):
    """TI radar subframe data type and length."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "type": (StructFieldType.UINT32, 1),
            "length": (StructFieldType.UINT32, 1),
        }


class TiRadarSubframeDataDetectedObjectCartesian(Struct):
    """TI radar subframe data detected object in Cartesian coordinates."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "x": (StructFieldType.FLOAT, 1),
            "y": (StructFieldType.FLOAT, 1),
            "z": (StructFieldType.FLOAT, 1),
            "doppler": (StructFieldType.FLOAT, 1),
        }


class TiRadarSubframeDataDetectedObjectSpherical(Struct):
    """TI radar subframe data detected object in spherical coordinates."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "range": (StructFieldType.FLOAT, 1),
            "azimuth": (StructFieldType.FLOAT, 1),
            "elevation": (StructFieldType.FLOAT, 1),
            "doppler": (StructFieldType.FLOAT, 1),
        }


class TiRadarSubframeDataDetectedObject(Struct):
    """TI radar subframe data detected object."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "range_bin": (StructFieldType.UINT16, 1),
            "doppler_bin": (StructFieldType.UINT16, 1),
            "range": (StructFieldType.FLOAT, 1),
            "doppler": (StructFieldType.FLOAT, 1),
            "azimuth": (StructFieldType.FLOAT, 1),
            "elevation": (StructFieldType.FLOAT, 1),
            "spatial_samples":
                (StructFieldType.STRUCT, 12, TiRadarComplexRealImaginary32),
        }


class TiRadarSubframeDataDetectedObjects(Struct):
    """TI radar subframe data detected objects."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "objects": (StructFieldType.STRUCT,
                        TI_RADAR_SUBFRAME_MAX_NUM_DETECTED_OBJECTS,
                        TiRadarSubframeDataDetectedObject),
        }


class TiRadarSubframeDataDetectedObjectInfo(Struct):
    """TI radar subframe data detected object information."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "snr": (StructFieldType.INT16, 1),
            "noise": (StructFieldType.INT16, 1),
        }


class TiRadarSubframeDataDetectedObjectInfos(Struct):
    """TI radar subframe data detected object informations."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "infos": (StructFieldType.STRUCT,
                      TI_RADAR_SUBFRAME_MAX_NUM_DETECTED_OBJECTS,
                      TiRadarSubframeDataDetectedObjectInfo),
        }


class TiRadarSubframeDataStats(Struct):
    """TI radar subframe data statistics."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "interchirp_processing_margin": (StructFieldType.UINT32, 1),
            "frame_start_counter": (StructFieldType.UINT32, 1),
            "frame_start_timestamp": (StructFieldType.UINT32, 1),
            "interframe_start_timestamp": (StructFieldType.UINT32, 1),
            "interframe_end_timestamp": (StructFieldType.UINT32, 1),
            "subframe_preparation_cycles": (StructFieldType.UINT32, 1),
        }


class TiRadarSubframeDataTemperature(Struct):
    """TI radar subframe data temperature."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "valid": (StructFieldType.INT32, 1),
            "time": (StructFieldType.UINT32, 1),
            "temperature_rx_0": (StructFieldType.INT16, 1),
            "temperature_rx_1": (StructFieldType.INT16, 1),
            "temperature_rx_2": (StructFieldType.INT16, 1),
            "temperature_rx_3": (StructFieldType.INT16, 1),
            "temperature_tx_0": (StructFieldType.INT16, 1),
            "temperature_tx_1": (StructFieldType.INT16, 1),
            "temperature_tx_2": (StructFieldType.INT16, 1),
            "temperature_power": (StructFieldType.INT16, 1),
            "temperature_digital_0": (StructFieldType.INT16, 1),
            "temperature_digital_1": (StructFieldType.INT16, 1),
        }


# Map from TI radar subframe data type to output type.
TI_RADAR_SUBFRAME_DATA_TYPE_TO_OUTPUT_TYPE = {
    TiRadarSubframeDataType.HEADER:
        TiRadarSubframeDataHeader,
    TiRadarSubframeDataType.DETECTED_OBJECTS:
        TiRadarSubframeDataDetectedObjects,
    TiRadarSubframeDataType.RANGE_PROFILE:
        bytes,
    TiRadarSubframeDataType.NOISE_FLOOR_PROFILE:
        bytes,
    TiRadarSubframeDataType.AZIMUTH_MAP:
        bytes,
    TiRadarSubframeDataType.RANGE_DOPPLER_MAP:
        bytes,
    TiRadarSubframeDataType.STATS:
        TiRadarSubframeDataStats,
    TiRadarSubframeDataType.DETECTED_OBJECTS_INFO:
        TiRadarSubframeDataDetectedObjectInfos,
    TiRadarSubframeDataType.AZIMUTH_ELEVATION_MAP:
        bytes,
    TiRadarSubframeDataType.TEMPERATURE:
        TiRadarSubframeDataTemperature,
}
