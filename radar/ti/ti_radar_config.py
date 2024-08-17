"""The TI radar config specifies the radar configuration, including the chirp
parameters, frame parameters, and the data output.
"""

from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum
from typing import Any

import numpy as np
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_integer("frame_periodicity", 500,
                     "Frame periodicity in milliseconds.")
flags.DEFINE_boolean("range_doppler_map_output", False,
                     "If true, enable the range-Doppler map output.")

# TI CLI subframe index for all subframes.
TI_CLI_SUBFRAME_INDEX_ALL = -1

# TI CLI reserved value.
TI_CLI_RESERVED_VALUE = 0


class TiCliCommandString(StrEnum):
    """TI command-line interface command string enumeration."""
    CONFIG_DATA_PORT = "configDataPort"
    SENSOR_START = "sensorStart"
    SENSOR_STOP = "sensorStop"
    FLUSH_CONFIG = "flushCfg"
    DIGITAL_FRONTEND_DATA_OUTPUT_MODE = "dfeDataOutputMode"
    CHANNEL_CONFIG = "channelCfg"
    ADC_CONFIG = "adcCfg"
    ADC_BUFFER_CONFIG = "adcbufCfg"
    LOW_POWER = "lowPower"
    PROFILE_CONFIG = "profileCfg"
    CHIRP_CONFIG = "chirpCfg"
    FRAME_CONFIG = "frameCfg"
    GUI_MONITOR = "guiMonitor"
    CFAR_CONFIG = "cfarCfg"
    MULTI_OBJECT_BEAM_FORMING = "multiObjBeamForming"
    CLUTTER_REMOVAL = "clutterRemoval"
    DC_RANGE_SIGNATURE_CALIBRATION = "calibDcRangeSig"
    EXTENDED_MAX_VELOCITY = "extendedMaxVelocity"
    BPM_CONFIG = "bpmCfg"
    LVDS_STREAM_CONFIG = "lvdsStreamCfg"
    RANGE_BIAS_AND_RX_CHANNEL_PHASE_COMPENSATION = "compRangeBiasAndRxChanPhase"
    RANGE_BIAS_AND_RX_CHANNEL_PHASE_MEASUREMENT = "measureRangeBiasAndRxChanPhase"
    CQ_SIGNAL_IMAGE_BAND_MONITOR = "CQSigImgMonitor"
    CQ_RX_SATURATION_MONITOR = "CQRxSatMonitor"
    ANALOG_MONITOR = "analogMonitor"
    AOA_FIELD_OF_VIEW_CONFIG = "aoaFovCfg"
    CFAR_FIELD_OF_VIEW_CONFIG = "cfarFovCfg"
    CALIBRATION_DATA = "calibData"


class TiCliCommand:
    """TI CLI command."""

    def __init__(self,
                 command: TiCliCommandString,
                 args: list[Any] = None) -> None:
        self.command = command
        self.args = args or []

    def __str__(self) -> str:
        args_str = [str(arg) for arg in self.args]
        command_str = f"{self.command} {' '.join(args_str)}"
        return command_str


class TiDigitalFrontEndDataOutputMode(IntEnum):
    """TI digital front-end data output mode enumeration."""
    FRAME = 1
    CONTINUOUS = 2
    ADVANCED_FRAME = 3


class TiChannelBitMask(IntEnum):
    """TI antenna bit mask enumeration."""
    TX_CHANNEL_0 = 1 << 0
    TX_CHANNEL_1 = 1 << 1
    TX_CHANNEL_2 = 1 << 2
    RX_CHANNEL_0 = 1 << 0
    RX_CHANNEL_1 = 1 << 1
    RX_CHANNEL_2 = 1 << 2
    RX_CHANNEL_3 = 1 << 3


class TiCascading(IntEnum):
    """TI cascading enumeration."""
    SINGLE_CHIP = 0
    MULTICHIP_MASTER = 1
    MULTICHIP_SLAVE = 2


class TiAdcNumBits(IntEnum):
    """TI ADC number of bits enumeration."""
    ADC_12_BITS = 0
    ADC_14_BITS = 1
    ADC_16_BITS = 2


class TiAdcFormat(IntEnum):
    """TI ADC format enumeration."""
    REAL = 0
    COMPLEX = 1
    COMPLEX_WITH_IMAGE_BAND = 2
    PSEUDO_REAL = 3


class TiAdcBufferFormat(IntEnum):
    """TI ADC buffer format enumeration."""
    COMPLEX = 0
    REAL = 1


class TiAdcBufferIQSwapSelection(IntEnum):
    """TI ADC buffer IQ swap selection enumeration."""
    LSB_I_MSB_Q = 0
    LSB_Q_MSB_I = 1


class TiAdcBufferChannelInterleave(IntEnum):
    """TI ADC buffer channel interleave enumeration."""
    INTERLEAVED = 0
    NON_INTERLEAVED = 1


class TiHighPassFilter1CornerFrequency(IntEnum):
    """TI high-pass filter 1 corner frequency enumeration."""
    CORNER_FREQUENCY_175_KHZ = 0
    CORNER_FREQUENCY_235_KHZ = 1
    CORNER_FREQUENCY_350_KHZ = 2
    CORNER_FREQUENCY_700_KHZ = 3


class TiHighPassFilter2CornerFrequency(IntEnum):
    """TI high-pass filter 2 corner frequency enumeration."""
    CORNER_FREQUENCY_350_KHZ = 0
    CORNER_FREQUENCY_700_KHZ = 1
    CORNER_FREQUENCY_1_4_MHZ = 2
    CORNER_FREQUENCY_2_8_MHZ = 3


class TiRfGainTarget(IntEnum):
    """TI RF gain target enumeration."""
    GAIN_30_DB = 0
    GAIN_33_DB = 1
    GAIN_36_DB = 2
    GAIN_26_DB = 3


class TiTriggerSelect(IntEnum):
    """TI trigger select enumeration."""
    SOFTWARE_TRIGGER = 1
    HARDWARE_TRIGGER = 2


class TiLowPowerAdcMode(IntEnum):
    """TI low power ADC mode enumeration."""
    REGULAR_MODE = 0
    LOW_POWER_MODE = 1


class TiGuiSelect(IntEnum):
    """TI GUI select enumeration."""
    DISABLED = 0
    ENABLED = 1
    LIMITED = 2


class TiCfarProcessingDirection(IntEnum):
    """TI CFAR processing direction enumeration."""
    RANGE = 0
    DOPPLER = 1


class TiCfarAveragingMode(IntEnum):
    """TI CFAR averaging mode enumeration."""
    CFAR_CA = 0
    CFAR_CAGO = 1
    CFAR_CASO = 2


class TiCfarCyclicMode(IntEnum):
    """TI CFAR cyclic mode enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiCfarPeakGrouping(IntEnum):
    """TI CFAR peak grouping enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiMultiObjectBeamForming(IntEnum):
    """TI multi-object beam forming enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiClutterRemoval(IntEnum):
    """TI clutter removal enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiDcRangeSignatureCalibration(IntEnum):
    """TI DC range signature calibration enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiExtendedMaxVelocity(IntEnum):
    """TI extended maximum velocity enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiBpm(IntEnum):
    """TI binary phase modulation enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiLvdsStreamHeader(IntEnum):
    """TI LVDS stream header enumeration.

    Only applicable for hardware streaming since software streaming will always
    have an HSI header.
    """
    DISABLED = 0
    ENABLED = 1


class TiLvdsStreamHardware(IntEnum):
    """TI LVDS hardware streaming enumeration."""
    DISABLED = 0
    ADC_DATA = 1
    CHIRP_PARAMETERS_ADC_DATA_CHIRP_QUALITY = 4


class TiLvdsStreamSoftware(IntEnum):
    """TI LVDS software streaming enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiRangeBiasAndRxChannelPhaseMeasurement(IntEnum):
    """TI range bias and RX channel phase measurement enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiCqRxSaturationMonitorSelect(IntEnum):
    """TI CQ RX saturation monitor select enumeration."""
    ADC = 1 << 0
    IF_AMPLIFIER = 1 << 1


class TiAnalogMonitor(IntEnum):
    """TI analog monitor enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiCalibrationDataSave(IntEnum):
    """TI calibration data save enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiCalibrationDataRestore(IntEnum):
    """TI calibration data restore enumeration."""
    DISABLED = 0
    ENABLED = 1


class TiRadarConfig(ABC):
    """Interface for the TI radar configuration."""

    def __init__(self) -> None:
        self.commands = [
            TiCliCommand(TiCliCommandString.FLUSH_CONFIG),
            TiCliCommand(
                TiCliCommandString.DIGITAL_FRONTEND_DATA_OUTPUT_MODE,
                [
                    TiDigitalFrontEndDataOutputMode.FRAME,  # Config mode.
                ]),
            TiCliCommand(
                TiCliCommandString.CHANNEL_CONFIG,
                [
                    TiChannelBitMask.RX_CHANNEL_0 |
                    TiChannelBitMask.RX_CHANNEL_1 |
                    TiChannelBitMask.RX_CHANNEL_2 |
                    TiChannelBitMask.RX_CHANNEL_3,  # RX channel enable.
                    TiChannelBitMask.TX_CHANNEL_0 |
                    TiChannelBitMask.TX_CHANNEL_1 |
                    TiChannelBitMask.TX_CHANNEL_2,  # TX channel enable.
                    TiCascading.SINGLE_CHIP,  # Cascading.
                ]),
            TiCliCommand(
                TiCliCommandString.ADC_CONFIG,
                [
                    TiAdcNumBits.ADC_16_BITS,  # Number of ADC bits.
                    TiAdcFormat.COMPLEX,  # ADC format.
                ]),
            TiCliCommand(
                TiCliCommandString.ADC_BUFFER_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiAdcBufferFormat.COMPLEX,  # ADC buffer format.
                    TiAdcBufferIQSwapSelection.
                    LSB_Q_MSB_I,  # IQ swap selection.
                    TiAdcBufferChannelInterleave.
                    NON_INTERLEAVED,  # Channel interleave.
                    1,  # Chirp threshold.
                ]),
            TiCliCommand(
                TiCliCommandString.PROFILE_CONFIG,
                [
                    0,  # Profile index.
                    60,  # Start frequency in GHz.
                    87,  # Idle time in us.
                    7,  # ADC start time in us.
                    75,  # Ramp end time in us.
                    0 << 16 | 0 << 8 | 0,  # TX output power backoff code.
                    self.translate_phase(0) << 18 |
                    self.translate_phase(0) << 10 |
                    self.translate_phase(0) << 2,  # TX phase shifter.
                    49.97,  # Frequency slope in MHz/us.
                    1,  # TX start time in us.
                    128,  # Number of ADC samples.
                    2000,  # Digital sampling frequency in kHz.
                    TiHighPassFilter1CornerFrequency.
                    CORNER_FREQUENCY_175_KHZ,  # High-pass filter 1 corner frequency.
                    TiHighPassFilter2CornerFrequency.
                    CORNER_FREQUENCY_350_KHZ,  # High-pass filter 2 corner frequency.
                    TiRfGainTarget.GAIN_36_DB << 6 | 30,  # RX gain.
                ]),
            TiCliCommand(
                TiCliCommandString.CHIRP_CONFIG,
                [
                    0,  # Chirp start index.
                    0,  # Chirp end index.
                    0,  # Profile index.
                    0,  # Start frequency in GHz.
                    0,  # Frequency slope in MHz/us.
                    0,  # Idle time in us.
                    0,  # ADC start time in us.
                    TiChannelBitMask.TX_CHANNEL_0,  # TX enable.
                ]),
            TiCliCommand(
                TiCliCommandString.CHIRP_CONFIG,
                [
                    1,  # Chirp start index.
                    1,  # Chirp end index.
                    0,  # Profile index.
                    0,  # Start frequency in GHz.
                    0,  # Frequency slope in MHz/us.
                    0,  # Idle time in us.
                    0,  # ADC start time in us.
                    TiChannelBitMask.TX_CHANNEL_2,  # TX enable.
                ]),
            TiCliCommand(
                TiCliCommandString.CHIRP_CONFIG,
                [
                    2,  # Chirp start index.
                    2,  # Chirp end index.
                    0,  # Profile index.
                    0,  # Start frequency in GHz.
                    0,  # Frequency slope in MHz/us.
                    0,  # Idle time in us.
                    0,  # ADC start time in us.
                    TiChannelBitMask.TX_CHANNEL_1,  # TX enable.
                ]),
            TiCliCommand(
                TiCliCommandString.FRAME_CONFIG,
                [
                    0,  # Chirp start index.
                    2,  # Chirp end index.
                    96,  # Number of loops.
                    0,  # Number of frames.
                    FLAGS.frame_periodicity,  # Frame periodicity in ms.
                    TiTriggerSelect.SOFTWARE_TRIGGER,  # Trigger select.
                    0,  # Trigger delay.
                ]),
            TiCliCommand(
                TiCliCommandString.LOW_POWER,
                [
                    TI_CLI_RESERVED_VALUE,  # Reserved.
                    TiLowPowerAdcMode.REGULAR_MODE,  # Low power ADC mode.
                ]),
            TiCliCommand(
                TiCliCommandString.GUI_MONITOR,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiGuiSelect.ENABLED,  # Detected objects.
                    TiGuiSelect.DISABLED,  # Log magnitude range array.
                    TiGuiSelect.DISABLED,  # Noise floor profile.
                    TiGuiSelect.DISABLED,  # Range-azimuth heat map.
                    TiGuiSelect.ENABLED if FLAGS.range_doppler_map_output else
                    TiGuiSelect.DISABLED,  # Range-Doppler heat map.
                    TiGuiSelect.ENABLED,  # Statistics.
                ]),
            TiCliCommand(
                TiCliCommandString.CFAR_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiCfarProcessingDirection.RANGE,  # Processing direction.
                    TiCfarAveragingMode.CFAR_CASO,  # Averaging mode.
                    8,  # One-sided noise averaging window length.
                    4,  # One-sided guard length.
                    3,  # Noise sum divisor. For CA, this should account for both the left and right noise windows. For CAGO or CASO, this should account for a one-sided window only.
                    TiCfarCyclicMode.DISABLED,  # Cyclic mode.
                    15,  # Threshold in dB.
                    TiCfarPeakGrouping.ENABLED,  # Peak grouping.
                ]),
            TiCliCommand(
                TiCliCommandString.CFAR_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiCfarProcessingDirection.DOPPLER,  # Processing direction.
                    TiCfarAveragingMode.CFAR_CA,  # Averaging mode.
                    4,  # One-sided noise averaging window length.
                    2,  # One-sided guard length.
                    3,  # Noise sum divisor. For CA, this should account for both the left and right noise windows. For CAGO or CASO, this should account for a one-sided window only.
                    TiCfarCyclicMode.ENABLED,  # Cyclic mode.
                    15,  # Threshold in dB.
                    TiCfarPeakGrouping.ENABLED,  # Peak grouping.
                ]),
            TiCliCommand(
                TiCliCommandString.MULTI_OBJECT_BEAM_FORMING,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiMultiObjectBeamForming.DISABLED,  # Enabled.
                    0.5,  # Multiple peak threshold in dB.
                ]),
            TiCliCommand(
                TiCliCommandString.CLUTTER_REMOVAL,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiClutterRemoval.DISABLED,  # Enabled.
                ]),
            TiCliCommand(
                TiCliCommandString.DC_RANGE_SIGNATURE_CALIBRATION,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiDcRangeSignatureCalibration.DISABLED,  # Enabled.
                    -5,  # Negative bin index.
                    8,  # Positive bin index.
                    256,  # Number of chirps to average over.
                ]),
            TiCliCommand(
                TiCliCommandString.EXTENDED_MAX_VELOCITY,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiExtendedMaxVelocity.DISABLED,  # Enabled.
                ]),
            TiCliCommand(
                TiCliCommandString.BPM_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiBpm.DISABLED,  # Enabled.
                    0,  # Chirp index for the first BPM chirp.
                    1,  # Chirp index for the second BPM chirp.
                ]),
            TiCliCommand(
                TiCliCommandString.LVDS_STREAM_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiLvdsStreamHeader.DISABLED,  # Header enabled.
                    TiLvdsStreamHardware.DISABLED,  # Hardware streaming.
                    TiLvdsStreamSoftware.DISABLED,  # Software streaming.
                ]),
            TiCliCommand(
                TiCliCommandString.RANGE_BIAS_AND_RX_CHANNEL_PHASE_COMPENSATION,
                [
                    0.0,  # Range bias in m.
                    *([1, 0, -1, 0, 1, 0, -1, 0] * self.num_tx_antennas(
                    )  # RX2 and RX4 are 180 degrees out of phase with respect to the TX antennas.
                     ),  # Real and imaginary components for RX channel phase compensation.
                ]),
            TiCliCommand(
                TiCliCommandString.RANGE_BIAS_AND_RX_CHANNEL_PHASE_MEASUREMENT,
                [
                    TiRangeBiasAndRxChannelPhaseMeasurement.
                    DISABLED,  # Enabled.
                    1.5,  # Target distance in m.
                    0.2,  # Search window size in m.
                ]),
            TiCliCommand(
                TiCliCommandString.CQ_SIGNAL_IMAGE_BAND_MONITOR,
                [
                    0,  # Profile index.
                    127,  # Number of primary and secondary slices to monitor.
                    6,  # Number of samples per time slice.
                ]),
            TiCliCommand(
                TiCliCommandString.CQ_RX_SATURATION_MONITOR,
                [
                    0,  # Profile inedx.
                    TiCqRxSaturationMonitorSelect.ADC |
                    TiCqRxSaturationMonitorSelect.
                    IF_AMPLIFIER,  # Saturation monitor select.
                    self.translate_slice_duration(
                        3.04),  # Primary slice duration in us.
                    125,  # Number of primary and secondary slices to monitor.
                    0 << 7 | 0 << 6 | 0 << 5 | 0 << 4 | 0 << 3 | 0 << 2 |
                    0 << 1 | 0 <<
                    0,  # RX channel mask. From MSB to LSB, the bits correspond to {RX3Q, RX2Q, RX1Q, RX0Q, RX3I, RX2I, RX1I, RX0I}.
                ]),
            TiCliCommand(
                TiCliCommandString.ANALOG_MONITOR,
                [
                    TiAnalogMonitor.DISABLED,  # Saturation monitor enabled.
                    TiAnalogMonitor.
                    DISABLED,  # Signal image band monitor enabled.
                ]),
            TiCliCommand(
                TiCliCommandString.AOA_FIELD_OF_VIEW_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    -90,  # Minimum azimuth in degrees.
                    90,  # Maximum azimuth in degrees.
                    -90,  # Minimum elevation in degrees.
                    90,  # Maxiamum elevation in degrees.
                ]),
            TiCliCommand(
                TiCliCommandString.CFAR_FIELD_OF_VIEW_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiCfarProcessingDirection.RANGE,  # Processing direction.
                    0.0,  # Minimum value in m for range or m/s for Doppler.
                    12.0,  # Maximum value in m for range or m/s for Doppler.
                ]),
            TiCliCommand(
                TiCliCommandString.CFAR_FIELD_OF_VIEW_CONFIG,
                [
                    TI_CLI_SUBFRAME_INDEX_ALL,  # Subframe index.
                    TiCfarProcessingDirection.DOPPLER,  # Processing direction.
                    -1.0,  # Minimum value in m for range or m/s for Doppler.
                    1.0,  # Maximum value in m for range or m/s for Doppler.
                ]),
            TiCliCommand(
                TiCliCommandString.CALIBRATION_DATA,
                [
                    TiCalibrationDataSave.DISABLED,  # Save enabled.
                    TiCalibrationDataRestore.DISABLED,  # Restore enabled.
                    0,  # Address offset in flash memory.
                ]),
        ]

    @classmethod
    @abstractmethod
    def rf_frequency_scaling_factor(cls) -> float:
        """Returns the device-specific RF frequencying scaling factor."""

    @classmethod
    @abstractmethod
    def num_tx_antennas(cls) -> int:
        """Returns the number of TX antennas."""

    @classmethod
    @abstractmethod
    def num_rx_channels(cls) -> int:
        """Returns the number of RX channels."""

    @classmethod
    def num_virtual_antennas(cls) -> int:
        """Returns the number of virtual antennas."""
        return cls.num_tx_antennas() * cls.num_rx_channels()

    @classmethod
    @abstractmethod
    def virtual_antenna_array(cls) -> tuple[np.ndarray, np.array]:
        """Returns the coordinates of each virtual antenna element in units of
        lambda/2.
        """

    @classmethod
    def translate_frequency(cls, frequency: float) -> int:
        """Translates the frequency to mmWave format.

        Args:
            frequency: Frequency in GHz.
        """
        # Each LSB corresponds to frequency scaling factor * 1e9 / 2^26 Hz.
        return int(frequency * 2**26 / cls.rf_frequency_scaling_factor())

    @classmethod
    def translate_slope(cls, slope: float) -> int:
        """Translates the slope to mmWave format.

        Args:
            slope: Slope in MHz/us.
        """
        # Each LSB corresponds to frequency scaling factor * 1e6 * 900 / 2^26
        # kHz/us.
        return int(slope * 2**26 / (cls.rf_frequency_scaling_factor() * 1000) *
                   900)

    @classmethod
    def translate_time(cls, time: float) -> int:
        """Translates the time to mmWave format.

        Args:
            time: Time in us.
        """
        # Each LSB corresponds to 10 ns.
        return int(time * 1000 / 10)

    @classmethod
    def translate_phase(cls, phase: float) -> int:
        """Translates the phase to mmWave format.

        Args:
            phase: Phase in degrees.
        """
        # Each LSB corresponds to 360 / 2^6 = 5.625 degrees.
        return int(phase / 5.625)

    @classmethod
    def translate_periodicity(cls, period: float) -> int:
        """Translates the periodicity to mmWave format.

        Args:
            period: Period in ms.
        """
        # Each LSB corresponds to 5 ns.
        return int(period * 1000000 / 5)

    @classmethod
    def translate_slice_duration(cls, duration: float) -> int:
        """Translates the slice duration to mmWave format.

        Args:
            duration: Duration in us.
        """
        # Each LSB corresponds to 0.16 us.
        return int(duration / 0.16)


class TiIWR68XXRadarConfig(TiRadarConfig):
    """TI IWR6843 radar configuration."""

    @classmethod
    def rf_frequency_scaling_factor(cls) -> float:
        """Returns the device-specific RF frequencying scaling factor."""
        return 2.7

    @classmethod
    def num_tx_antennas(cls) -> int:
        """Returns the number of TX antennas."""
        return 3

    @classmethod
    def num_rx_channels(cls) -> int:
        """Returns the number of RX channels."""
        return 4

    @classmethod
    def virtual_antenna_array(cls) -> tuple[np.ndarray, np.array]:
        """Returns the coordinates of each virtual antenna element in units of
        lambda/2.
        """
        azimuth_coordinates = np.array([1, 1, 0, 0, 3, 3, 2, 2, 1, 1, 0, 0])
        elevation_coordinates = np.array([2, 3, 2, 3, 0, 1, 0, 1, 0, 1, 0, 1])
        return azimuth_coordinates, elevation_coordinates


# Map from TI radar board to radar config.
RADAR_CONFIGS = {
    "iwr68xx": TiIWR68XXRadarConfig,
}
