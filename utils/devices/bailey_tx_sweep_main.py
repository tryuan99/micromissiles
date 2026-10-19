"""Sweeps the VGA gain code or the phase of a single Bailey TX channel while
capturing S21 with the FieldFox.

The Pico must run //pico/x/bailey:tx_channel_main. The FieldFox port 1 drives
the beamformer RF input, and port 2 receives the TX channel output. The script
configures the FieldFox stimulus and an S21 trace, so the stimulus flags must
match the calibrated stimulus. The FieldFox reports a user calibration as
enabled even when the stimulus has moved outside the calibrated range.

The output CSV file has one row per swept code and frequency with the S21
real and imaginary parts. Comment lines at the top record the instrument and
measurement settings.
"""

from enum import StrEnum
from pathlib import Path

import pandas as pd
from absl import app, flags, logging

from utils.devices.fieldfox_interface import FieldFoxInterface
from utils.serial.serial_interface import SerialInterface

FLAGS = flags.FLAGS

# Pico USB serial baudrate. A baudrate of 1200 reboots the Pico into BOOTSEL.
PICO_BAUDRATE = 115200

# Number of VGA gain codes and phases.
NUM_VGA_GAINS = 128
NUM_PHASES = 128


class SweepType(StrEnum):
    """Sweep type enumeration."""
    VGA_GAIN = "vga_gain"
    PHASE = "phase"


def configure_channel(pico: SerialInterface, channel: int, vga_gain: int,
                      phase: int) -> None:
    """Configures the TX channel and waits for the Pico to acknowledge.

    Args:
        pico: Pico serial interface.
        channel: TX channel in [1, 4].
        vga_gain: VGA gain code in [0, 127].
        phase: Phase index in [0, 127].
    """
    command = f"{channel} {vga_gain} {phase}"
    pico.write(command.encode("ascii"))
    response = pico.read().decode("ascii").strip()
    if response != f"OK {command}":
        raise RuntimeError(
            f"Pico responded with '{response}' to command '{command}'.")


def main(argv):
    assert len(argv) == 1

    field_fox = FieldFoxInterface(FLAGS.fieldfox_ip_address)
    field_fox.write(
        ':INST:SEL "NA"',
        ":CALC:PAR1:DEF S21",
        ":CALC:PAR1:SEL",
        f":SENS:FREQ:STAR {FLAGS.start_frequency}",
        f":SENS:FREQ:STOP {FLAGS.stop_frequency}",
        f":SENS:SWE:POIN {FLAGS.num_points}",
        f":SENS:BWID {FLAGS.if_bandwidth}",
        f":SOUR:POW {FLAGS.source_power}",
    )
    metadata = {
        "instrument": field_fox.query("*IDN?"),
        "calibration": field_fox.query(":SENS:CORR:USER:STAT?"),
        "start_frequency": field_fox.query(":SENS:FREQ:STAR?"),
        "stop_frequency": field_fox.query(":SENS:FREQ:STOP?"),
        "num_points": field_fox.query(":SENS:SWE:POIN?"),
        "if_bandwidth": field_fox.query(":SENS:BWID?"),
        "source_power": field_fox.query(":SOUR:POW?"),
        "channel": FLAGS.channel,
        "sweep": FLAGS.sweep,
    }
    logging.info("Measurement settings: %s", metadata)

    pico = SerialInterface(
        FLAGS.serial_port,
        PICO_BAUDRATE,
        write_terminator=b"\n",
    )
    pico.read_all()

    if FLAGS.sweep == SweepType.VGA_GAIN:
        settings = [(code, FLAGS.phase) for code in range(NUM_VGA_GAINS)]
    else:
        settings = [(FLAGS.vga_gain, code) for code in range(NUM_PHASES)]

    dfs = []
    for vga_gain, phase in settings:
        logging.info("Capturing channel %d with VGA gain %d and phase %d.",
                     FLAGS.channel, vga_gain, phase)
        configure_channel(pico, FLAGS.channel, vga_gain, phase)
        frequencies, s21 = field_fox.capture_trace()
        dfs.append(
            pd.DataFrame({
                "channel": FLAGS.channel,
                "vga_gain": vga_gain,
                "phase": phase,
                "frequency": frequencies,
                "s21_real": s21.real,
                "s21_imag": s21.imag,
            }))

    output_path = Path(FLAGS.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        for key, value in metadata.items():
            f.write(f"# {key}: {value}\n")
        pd.concat(dfs).to_csv(f, index=False)
    logging.info("Saved the sweep to %s.", output_path)


if __name__ == "__main__":
    flags.DEFINE_string("serial_port", None, "Pico serial port.")
    flags.DEFINE_string("fieldfox_ip_address", "192.168.1.1",
                        "FieldFox IP address.")
    flags.DEFINE_integer(
        "channel",
        1,
        "TX channel.",
        lower_bound=1,
        upper_bound=4,
    )
    flags.DEFINE_enum("sweep", None,
                      [sweep_type.value for sweep_type in SweepType],
                      "Swept parameter.")
    flags.DEFINE_integer(
        "vga_gain",
        NUM_VGA_GAINS - 1,
        "VGA gain code during a phase sweep.",
        lower_bound=0,
        upper_bound=NUM_VGA_GAINS - 1,
    )
    flags.DEFINE_integer(
        "phase",
        0,
        "Phase index during a VGA gain sweep.",
        lower_bound=0,
        upper_bound=NUM_PHASES - 1,
    )
    flags.DEFINE_float("start_frequency", None, "Start frequency in Hz.")
    flags.DEFINE_float("stop_frequency", None, "Stop frequency in Hz.")
    flags.DEFINE_integer("num_points", 201, "Number of frequency points.")
    flags.DEFINE_float("if_bandwidth", 1000, "IF bandwidth in Hz.")
    flags.DEFINE_float("source_power", 0, "Source power in dBm.")
    flags.DEFINE_string("output_file", None, "Output CSV file.")
    flags.mark_flags_as_required([
        "serial_port",
        "sweep",
        "start_frequency",
        "stop_frequency",
        "output_file",
    ])

    app.run(main)
