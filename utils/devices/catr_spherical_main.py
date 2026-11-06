"""Sweeps the Keysight CATR positioner over azimuth and roll while capturing the
FieldFox output.
"""

import itertools
import time
from pathlib import Path

import numpy as np
from absl import app, flags, logging

from utils.devices.catr_interface import CatrInterface
from utils.devices.fieldfox_interface import FieldFoxInterface

FLAGS = flags.FLAGS

# Capture timeout in seconds.
CAPTURE_TIMEOUT = 0.2


def _format_angle(angle: float) -> str:
    """Formats an angle for use in a filename.

    Args:
        angle: Angle in degrees.

    Returns:
        The angle with trailing zeros removed.
    """
    return f"{angle:.6f}".rstrip("0").rstrip(".")


def main(argv):
    assert len(argv) == 1

    output_dir_path = Path(FLAGS.output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    catr = CatrInterface(FLAGS.catr_visa_address)
    if FLAGS.set_zero:
        logging.info("Setting the current position as zero.")
        catr.set_zero()

    field_fox = FieldFoxInterface(FLAGS.fieldfox_ip_address)
    azimuths = np.arange(FLAGS.azimuth_start,
                         FLAGS.azimuth_stop + FLAGS.azimuth_step,
                         FLAGS.azimuth_step)
    rolls = np.arange(FLAGS.roll_start, FLAGS.roll_stop + FLAGS.roll_step,
                      FLAGS.roll_step)
    for azimuth, roll in itertools.product(azimuths, rolls):
        logging.info("Moving the positioner to azimuth %f, roll %f.", azimuth,
                     roll)
        catr.move_to(azimuth, roll)
        time.sleep(CAPTURE_TIMEOUT)

        output_path = output_dir_path / (
            f"{FLAGS.output_prefix}_azimuth_{_format_angle(azimuth)}deg"
            f"_roll_{_format_angle(roll)}deg.s2p")
        logging.info("Capturing S2P to %s.", output_path)
        field_fox.capture_sp(output_path)
    catr.move_to(azimuth=0, roll=0)


if __name__ == "__main__":
    flags.DEFINE_string("fieldfox_ip_address", "192.168.1.1",
                        "FieldFox IP address.")
    flags.DEFINE_string("catr_visa_address",
                        "TCPIP0::127.0.0.1::hislip200::INSTR",
                        "VISA address of the OTA chamber control software.")
    flags.DEFINE_float("azimuth_start", -90, "Azimuth start in degrees.")
    flags.DEFINE_float("azimuth_stop", 90, "Azimuth stop in degrees.")
    flags.DEFINE_float(
        "azimuth_step",
        None,
        "Azimuth step in degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_float("roll_start", 0, "Roll start in degrees.")
    flags.DEFINE_float("roll_stop", 180, "Roll stop in degrees.")
    flags.DEFINE_float(
        "roll_step",
        None,
        "Roll step in degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_boolean("set_zero", False,
                         "If true, set the current position as zero first.")
    flags.DEFINE_string("output_dir", None, "Output directory.")
    flags.DEFINE_string("output_prefix", "catr_spherical",
                        "Output file prefix.")
    flags.mark_flag_as_required("output_dir")

    app.run(main)
