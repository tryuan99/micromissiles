"""Designs a U-slot patch antenna.

See https://ieeexplore.ieee.org/document/8787772.
"""

import numpy as np
from absl import app, flags, logging

FLAGS = flags.FLAGS

# Speed of light in free space in m/s.
c = 299792458  # m/s

# Characteristic impedance in Ohms.
Z0 = 50  # Ohms

# Optimized resonant frequency separation at Z0 = 50 Ohms.
yopt = 2.25

# Optimized resonant conductanceat Z0 = 50 Ohms is between 40 and 50 mS.
Gopt = 45e-3


def design_u_slot_patch_antenna(
    f: float,
    fractional_bandwidth: float,
    h: float,
    er: float,
    w_patch: float,
) -> None:
    """Designs a patch antenna with the given parameters.

    Args:
        f: Frequency in Hz.
        fractional_bandwidth: Fractional bandwidth.
        h: Dielectric height in m.
        er: Relative dielectric constant of the substrate.
        w_patch: Patch width in m.
    """
    # Kappa ≈ BW / f0 = yopt / Q
    kappa = fractional_bandwidth
    Q = yopt / kappa

    # K ≈ f0 * kappa / 2
    K = f * kappa / 2

    # f+- = f0 +- sqrt(((f2 - f1) / 2)^2 + |K|^2)
    f1 = f * (1 - fractional_bandwidth / 2)
    f2 = f * (1 + fractional_bandwidth / 2)
    logging.info("f1 = %f Hz, f2 = %f Hz", f1, f2)

    ereff = (1 + er) / 2
    lambda0 = c / f / np.sqrt(ereff)
    # Total length of the slot: l_slot = w_slot + 2 * h_slot.
    # If the slot resonance is too high, increase the slot length.
    l_slot = lambda0 / 2
    w_slot = kappa * w_patch
    h_slot = (l_slot - w_slot) / 2
    t_slot = l_slot / 20
    logging.info(
        "Slot height = %f mm, slot width = %f mm, slot thickness = %f mm",
        h_slot * 1e3, w_slot * 1e3, t_slot * 1e3)


def main(argv):
    assert len(argv) == 1, argv
    design_u_slot_patch_antenna(
        FLAGS.f,
        FLAGS.fractional_bandwidth,
        FLAGS.h / 1e3,
        FLAGS.er,
        FLAGS.w_patch / 1e3,
    )


if __name__ == "__main__":
    flags.DEFINE_float("f", 9e9, "Frequency in Hz.", lower_bound=0.0)
    flags.DEFINE_float("fractional_bandwidth",
                       1 / 9,
                       "Fractional bandwidth.",
                       lower_bound=0.0)
    flags.DEFINE_float("h", 1.524, "Dielectric height in mm.", lower_bound=0.0)
    flags.DEFINE_float("er",
                       3.48,
                       "Relative dielectric constant of the substrate.",
                       lower_bound=0.0)
    flags.DEFINE_float("w_patch",
                       11.1281,
                       "Patch width in mm.",
                       lower_bound=0.0)

    app.run(main)
