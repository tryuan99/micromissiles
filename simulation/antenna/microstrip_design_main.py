"""Designs a microstrip transmission line."""

import numpy as np
from absl import app, flags, logging

FLAGS = flags.FLAGS

# Copper thickness conversion.
# 1 oz/ft^2 = 34.79 microns.
COPPER_OZ_PER_SQ_FT_TO_METERS = 34.79e-6

# Maximum number of iterations to calculate the microstrip trace width.
MAX_NUM_ITERATIONS = 100

# Minimum and maximum trace width factors as a function of the dielectric
# height to search over.
MIN_TRACE_WIDTH_FACTOR = 1e-3
MAX_TRACE_WIDTH_FACTOR = 100
TRACE_WIDTH_TOLERANCE_FACTOR = 1e-9


def _calculate_microstrip_impedance(
    w: float,
    h: float,
    er: float,
    t: float,
) -> float:
    """Calculates the characteristic impedance of a microstrip line using the
    Hammerstad and Jensen approximation.

    Args:
        w: Trace width in m.
        h: Dielectric height in m.
        er: Relative dielectric constant.
        t: Copper thickness in m.

    Returns:
        The characteristic impedance in Ohms.
    """
    # Width correction due to conductor thickness.
    # Set to zero if the thickness correction is ignored.
    if t > 0:
        delta_w = (t / np.pi) * np.log(1 + (4 * np.e) / (t / h)**2)
    else:
        delta_w = 0

    weff = w + delta_w
    u = weff / h

    # Calcualate the effective dielectric constant.
    ereff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 / u)**(-0.5)

    # Calculate the characteristic impedance.
    if u <= 1:
        z0 = (60 / np.sqrt(ereff)) * np.log(8 / u + 0.25 * u)
    else:
        z0 = (120 * np.pi) / (np.sqrt(ereff) *
                              (u + 1.393 + 0.667 * np.log(u + 1.444)))
    return z0


def _calculate_microstrip_width(
    z0_target: float,
    h: float,
    er: float,
    t: float,
) -> float:
    """Calculates the microstrip trace width using binary search.

    Args:
        z0_target: Desired characteristic impedance in Ohms.
        h: Dielectric height in m.
        er: Relative dielectric constant.
        t: Copper thickness in m.

    Returns:
        The microstrip trace width in m.
    """
    w_low = MIN_TRACE_WIDTH_FACTOR * h
    w_high = MAX_TRACE_WIDTH_FACTOR * h

    for _ in range(MAX_NUM_ITERATIONS):
        w_mid = (w_low + w_high) / 2
        z0 = _calculate_microstrip_impedance(w_mid, h, er, t)
        if z0 > z0_target:
            w_low = w_mid
        else:
            w_high = w_mid

        # End the iteration early once the width interval becomes
        # sufficiently small.
        if w_high - w_low <= TRACE_WIDTH_TOLERANCE_FACTOR * h:
            break
    return w_mid


def design_microstrip(
    z0: float,
    h: float,
    er: float,
    t: float,
) -> None:
    """Designs a microstrip line.

    Args:
        z0: Desired characteristic impedance in Ohms.
        h: Dielectric height in m.
        er: Relative dielectric constant.
        t_oz: Copper thickness in m.
    """
    w = _calculate_microstrip_width(z0, h, er, t)
    z0_actual = _calculate_microstrip_impedance(w, h, er, t)
    logging.info("Z0 = %f Ohms, h = %f mm, er = %f, t = %f oz/ft^2", z0,
                 h * 1e3, er, t / COPPER_OZ_PER_SQ_FT_TO_METERS)
    logging.info("Width = %f mm, estimated Z0 = %f Ohms", w * 1e3, z0_actual)


def main(argv):
    assert len(argv) == 1, argv
    design_microstrip(
        FLAGS.z0,
        FLAGS.h / 1e3,
        FLAGS.er,
        FLAGS.t * COPPER_OZ_PER_SQ_FT_TO_METERS,
    )


if __name__ == "__main__":
    flags.DEFINE_float("z0",
                       50,
                       "Target characteristic impedance in Ohms.",
                       lower_bound=0.0)
    flags.DEFINE_float("h", 1.524, "Dielectric height in mm.", lower_bound=0.0)
    flags.DEFINE_float("er",
                       3.48,
                       "Relative dielectric constant.",
                       lower_bound=0.0)
    flags.DEFINE_float("t", 1, "Copper thickness in oz/ft^2.", lower_bound=0.0)

    app.run(main)
