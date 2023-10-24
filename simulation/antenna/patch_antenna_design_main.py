"""Designs a patch antenna."""

import numpy as np
from absl import app, flags, logging

FLAGS = flags.FLAGS

# Speed of light in free space in m/s.
c = 299792458  # m/s

# Characteristic impedance in Ohms.
Z0 = 50  # Ohms


def design_patch_antenna(
    f: float,
    h: float,
    er: float,
) -> None:
    """Designs a patch antenna with the given parameters.

    Args:
        f: Frequency in GHz.
        h: Dielectric height in mm.
        er: Relative dielectric constant of the substrate.
    """
    f *= 1e9
    h /= 1e3
    W = c / (2 * f) * np.sqrt(2 / (er + 1))
    ereff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h / W)**(-1 / 2)
    L_delta_over_h = 0.412 * (ereff + 0.3) * (W / h + 0.264) / (
        (ereff - 0.258) * (W / h + 0.8))
    L_delta = L_delta_over_h * h
    L = c / (2 * f * np.sqrt(ereff)) - 2 * L_delta
    Rin = 90 * er**2 / (er - 1) * L / W
    x0 = np.arccos(np.sqrt(Z0 / Rin)) * L / np.pi
    logging.info("f = %f GHz, h = %f mm, er = %f", f / 1e9, h * 1e3, er)
    logging.info("ereff = %f, L_delta_over_h = %f, L_delta = %f mm", ereff,
                 L_delta_over_h, L_delta * 1e3)
    logging.info("W = %f mm, L = %f mm, Rin = %f Ohms, x0 = %f mm", W * 1e3,
                 L * 1e3, Rin, x0 * 1e3)


def main(argv):
    assert len(argv) == 1, argv
    design_patch_antenna(
        FLAGS.f,
        FLAGS.h,
        FLAGS.er,
    )


if __name__ == "__main__":
    flags.DEFINE_float("f", 82.5, "Frequency in GHz.", lower_bound=0.0)
    flags.DEFINE_float("h",
                       0.07849,
                       "Dielectric height in mm.",
                       lower_bound=0.0)
    flags.DEFINE_float("er",
                       3.91,
                       "Relative dielectric constant of the substrate.",
                       lower_bound=0.0)

    app.run(main)
