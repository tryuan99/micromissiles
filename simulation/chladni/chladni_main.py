"""Writes the amplitude and phase of a driven Chladni plate to a CSV file."""

import csv

from absl import app, flags, logging

from simulation.chladni.material import MATERIALS, Material
from simulation.chladni.plate import ChladniPlate
from simulation.chladni.shape import SHAPES, ShapeFactory

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1

    shape_args = {
        "circle": (FLAGS.diameter,),
        "rectangle": (FLAGS.width, FLAGS.height),
        "square": (FLAGS.width,),
    }
    shape = ShapeFactory.create(FLAGS.shape, *shape_args[FLAGS.shape])
    base_material = MATERIALS[FLAGS.material]
    material = Material(
        base_material.E,
        base_material.nu,
        base_material.density,
        FLAGS.thickness,
    )
    plate = ChladniPlate(shape, material, (FLAGS.drive_x, FLAGS.drive_y))
    logging.info("Resonances excitable from the drive point: %s Hz.",
                 plate.resonances(10, 10000)[0])
    response = plate.steady_state(
        FLAGS.frequency,
        FLAGS.amplitude,
        FLAGS.num_points_per_side,
    )

    with open(FLAGS.output, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["x [m]", "y [m]", "Amplitude [m]", "Phase [rad]"])
        mask = response.mask
        writer.writerows(
            zip(
                response.x[mask],
                response.y[mask],
                response.amplitude[mask],
                response.phase[mask],
            ))


if __name__ == "__main__":
    flags.DEFINE_enum("shape", "square", list(SHAPES.keys()), "Plate shape.")
    flags.DEFINE_float(
        "diameter",
        0.24,
        "Diameter in m for a circular plate.",
        lower_bound=0.0,
    )
    flags.DEFINE_float(
        "width",
        0.24,
        "Width in m for a rectangular or square plate.",
        lower_bound=0.0,
    )
    flags.DEFINE_float(
        "height",
        0.24,
        "Height in m for a rectangular plate.",
        lower_bound=0.0,
    )
    flags.DEFINE_enum("material", "aluminum", list(MATERIALS.keys()),
                      "Plate material.")
    flags.DEFINE_float(
        "thickness",
        1e-3,
        "Plate thickness in m.",
        lower_bound=0.0,
    )
    flags.DEFINE_float(
        "frequency",
        268.5,
        "Drive frequency in Hz.",
        lower_bound=0.0,
    )
    flags.DEFINE_float(
        "amplitude",
        1e-4,
        "Drive amplitude in m.",
        lower_bound=0.0,
    )
    flags.DEFINE_float("drive_x", 0,
                       "x-coordinate in m of the drive point from the center.")
    flags.DEFINE_float("drive_y", 0,
                       "y-coordinate in m of the drive point from the center.")
    flags.DEFINE_integer(
        "num_points_per_side",
        401,
        "Number of grid points per side.",
        lower_bound=0,
    )
    flags.DEFINE_string("output", None, "Output CSV file.")
    flags.mark_flag_as_required("output")

    app.run(main)
