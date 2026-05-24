"""Designs a microstrip transmission line."""

import numpy as np
from absl import app, flags, logging

FLAGS = flags.FLAGS

# Copper thickness conversion: 1 oz/ft^2 = 34.79 um.
COPPER_OZ_PER_SQ_FT_TO_METERS = 34.79e-6

# Maximum number of iterations to calculate the microstrip trace width.
MAX_NUM_ITERATIONS = 100

# Minimum and maximum trace width factors as a function of the dielectric
# height to search over.
MIN_TRACE_WIDTH_FACTOR = 1e-6
MAX_TRACE_WIDTH_FACTOR = 1e6
TRACE_WIDTH_TOLERANCE_FACTOR = 1e-9


def _calculate_microstrip_impedance(
    w: float,
    h: float,
    er: float,
    t: float,
) -> float:
    """Calculates microstrip characteristic impedance using the Hammerstad-
    Jensen equations.

    Args:
        w: Trace width in m.
        h: Dielectric height in m.
        er: Relative dielectric constant.
        t: Copper thickness in m.

    Returns:
        The characteristic impedance in Ohms.
    """
    # Normalize the trace width and the copper thickness.
    w_normalized = w / h
    t_normalized = t / h

    # Hammerstad thickness correction.
    if t > 0:
        coth_term = 1 / np.tanh(np.sqrt(6.517 * w_normalized))
        delta_w_normalized_impedance = (t_normalized / np.pi *
                                        np.log(1 + 4 * np.e /
                                               (t_normalized * coth_term**2)))
        delta_w_normalized_dielectric = (delta_w_normalized_impedance *
                                         (1 + 1 / np.cosh(np.sqrt(er - 1))) / 2)
        w_normalized_impedance = w_normalized + delta_w_normalized_impedance
        w_normalized_dielectric = w_normalized + delta_w_normalized_dielectric
    else:
        w_normalized_impedance = w_normalized
        w_normalized_dielectric = w_normalized

    # Hammerstad-Jensen effective dielectric constant.
    a = (1 + (1 / 49) * np.log(
        (w_normalized_dielectric**4 + (w_normalized_dielectric / 52)**2) /
        (w_normalized_dielectric**4 + 0.432)) +
         (1 / 18.7) * np.log(1 + (w_normalized_dielectric / 18.1)**3))
    b = 0.564 * ((er - 0.9) / (er + 3))**0.053
    ereff = ((er + 1) / 2 + (er - 1) / 2 *
             (1 + 10 / w_normalized_dielectric)**(-a * b))

    # Hammerstad impedance equation.
    f = (6 +
         (2 * np.pi - 6) * np.exp(-(30.666 / w_normalized_impedance)**0.7528))
    z_air = (60 * np.log(f / w_normalized_impedance +
                         np.sqrt(1 + (2 / w_normalized_impedance)**2)))
    z0 = z_air / np.sqrt(ereff)
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

        # End the iteration early once the width interval becomes sufficiently
        # small.
        if w_high - w_low <= TRACE_WIDTH_TOLERANCE_FACTOR * h:
            break
    return (w_low + w_high) / 2


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
        t: Copper thickness in m.
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
