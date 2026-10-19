"""Sweeps the VGA gain or the phase of a single beamformer channel while
capturing the S-parameters from the FieldFox VNA.
"""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from absl import app, flags, logging

from utils.devices.fieldfox_interface import FieldFoxInterface
from utils.serial.serial_interface import SerialInterface

FLAGS = flags.FLAGS

# Pico USB serial baudrate.
PICO_BAUDRATE = 115200

# Number of VGA gain codes and phases.
NUM_VGA_GAINS = 128
NUM_PHASES = 128


class SweepType(StrEnum):
    """Sweep type enumeration."""
    VGA_GAIN = "vga_gain"
    PHASE = "phase"


@dataclass
class SweepPoint:
    """Sweep point.

    Attributes:
        vga_gain: VGA gain code.
        phase: Phase index.
    """
    vga_gain: int
    phase: int


def _beamformer_configure(
    pico: SerialInterface,
    channel: int,
    vga_gain: int,
    phase: int,
) -> None:
    """Configures the beamformer channel.

    Args:
        pico: Pico serial interface.
        channel: Beamformer channel.
        vga_gain: VGA gain code.
        phase: Phase index.
    """
    command = f"{channel} {vga_gain} {phase}"
    pico.write(command.encode("ascii"))
    response = pico.read().decode("ascii").strip()
    if response != f"Channel {channel}: VGA gain = {vga_gain}, phase index = {phase}":
        raise RuntimeError(
            f"Pico responded with '{response}' to input '{command}'.")


def main(argv):
    assert len(argv) == 1

    field_fox = FieldFoxInterface(FLAGS.fieldfox_ip_address)
    pico = SerialInterface(
        FLAGS.pico_serial_port,
        PICO_BAUDRATE,
        write_terminator=b"\n",
    )

    match FLAGS.sweep:
        case SweepType.VGA_GAIN:
            sweep_points = [
                SweepPoint(vga_gain, FLAGS.phase)
                for vga_gain in range(NUM_VGA_GAINS)
            ]
        case SweepType.PHASE:
            sweep_points = [
                SweepPoint(FLAGS.vga_gain, phase) for phase in range(NUM_PHASES)
            ]

    output_dir_path = Path(FLAGS.output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    for point in sweep_points:
        logging.info("Capturing channel %d with VGA gain %d and phase %d.",
                     FLAGS.channel, point.vga_gain, point.phase)
        _beamformer_configure(pico, FLAGS.channel, point.vga_gain, point.phase)
        output_path = (
            output_dir_path /
            (f"{FLAGS.output_prefix}_channel_{FLAGS.channel}_vga_gain_"
             f"{point.vga_gain}_phase_{point.phase}.s2p"))
        logging.info("Capturing S2P to %s.", output_path)
        field_fox.capture_sp(output_path)


if __name__ == "__main__":
    flags.DEFINE_string("fieldfox_ip_address", "192.168.1.2",
                        "FieldFox IP address.")
    flags.DEFINE_string("pico_serial_port", "/dev/cu.usbmodem1101",
                        "Pico serial port.")
    flags.DEFINE_integer("channel",
                         1,
                         "Beamformer channel.",
                         lower_bound=1,
                         upper_bound=4)
    flags.DEFINE_enum("sweep", None,
                      [sweep_type.value for sweep_type in SweepType],
                      "Swept parameter.")
    flags.DEFINE_integer("vga_gain",
                         NUM_VGA_GAINS - 1,
                         "VGA gain code during a phase sweep.",
                         lower_bound=0,
                         upper_bound=NUM_VGA_GAINS - 1)
    flags.DEFINE_integer("phase",
                         0,
                         "Phase index during a VGA gain sweep.",
                         lower_bound=0,
                         upper_bound=NUM_PHASES - 1)
    flags.DEFINE_string("output_dir", None, "Output directory.")
    flags.DEFINE_string("output_prefix", "beamformer_sweep",
                        "Output file prefix.")
    flags.mark_flags_as_required(["sweep", "output_dir"])

    app.run(main)
