"""Simulates engagements to generate a lookup table of the engagement results.

The following parameters are swept in the lookup table:
- Interceptor speed
- Range from the interceptor to the threat
- Relative azimuth and elevation from the interceptor to the threat
- Threat speed
- Threat heading (azimuth and elevation)

The interceptor initially moves in the +z direction.
"""

import csv
import itertools
import multiprocessing

import google.protobuf
import numpy as np
from absl import app, flags

from simulation.swarm.reachability.engagement_runner import EngagementRunner
from simulation.swarm.reachability.interceptor import Interceptor
from simulation.swarm.reachability.proto.engagement_config_pb2 import \
    EngagementConfig
from simulation.swarm.reachability.proto.static_config_pb2 import StaticConfig
from simulation.swarm.reachability.termination import TerminationReason
from simulation.swarm.reachability.threat import Threat

FLAGS = flags.FLAGS


def _sweep_values(minimum: float, maximum: float, step: float) -> np.ndarray:
    """Returns grid samples within the requested inclusive bounds.

    The result is a one-dimensional array starting at minimum with no values
    exceeding maximum. The upper bound is included when it lies on the grid.

    Args:
        minimum: Smallest allowed sample value.
        maximum: Largest allowed sample value.
        step: Positive spacing between adjacent samples.
    """
    intervals = (maximum - minimum) / step
    nearest = round(intervals)
    tolerance = 8 * np.finfo(float).eps * max(1, abs(intervals))
    count = nearest if abs(intervals -
                           nearest) <= tolerance else int(np.floor(intervals))
    return np.minimum(minimum + step * np.arange(count + 1), maximum)


def main(argv):
    assert len(argv) == 1

    with open(FLAGS.interceptor_config, "r") as interceptor_config_file:
        interceptor_config = google.protobuf.text_format.Parse(
            interceptor_config_file.read(), StaticConfig())
    with open(FLAGS.threat_config, "r") as threat_config_file:
        threat_config = google.protobuf.text_format.Parse(
            threat_config_file.read(), StaticConfig())
    with open(FLAGS.engagement_config, "r") as engagement_config_file:
        engagement_config = google.protobuf.text_format.Parse(
            engagement_config_file.read(), EngagementConfig())

    interceptor = Interceptor(interceptor_config)
    threat = Threat(threat_config)

    interceptor_speeds = _sweep_values(
        FLAGS.min_interceptor_speed,
        FLAGS.max_interceptor_speed,
        FLAGS.interceptor_speed_step,
    )
    ranges = _sweep_values(
        FLAGS.min_range,
        FLAGS.max_range,
        FLAGS.range_step,
    )
    relative_azimuths = _sweep_values(
        FLAGS.min_relative_azimuth,
        FLAGS.max_relative_azimuth,
        FLAGS.relative_azimuth_step,
    )
    relative_elevations = _sweep_values(
        FLAGS.min_relative_elevation,
        FLAGS.max_relative_elevation,
        FLAGS.relative_elevation_step,
    )
    threat_speeds = _sweep_values(
        FLAGS.min_threat_speed,
        FLAGS.max_threat_speed,
        FLAGS.threat_speed_step,
    )
    threat_heading_azimuths = _sweep_values(
        FLAGS.min_threat_heading_azimuth,
        FLAGS.max_threat_heading_azimuth,
        FLAGS.threat_heading_azimuth_step,
    )
    threat_heading_elevations = _sweep_values(
        FLAGS.min_threat_heading_elevation,
        FLAGS.max_threat_heading_elevation,
        FLAGS.threat_heading_elevation_step,
    )

    samples = itertools.product(
        interceptor_speeds,
        ranges,
        relative_azimuths,
        relative_elevations,
        threat_speeds,
        threat_heading_azimuths,
        threat_heading_elevations,
    )
    runner = EngagementRunner(interceptor, threat, engagement_config)

    with (
            open(FLAGS.output, "w", newline="") as f,
            multiprocessing.Pool(FLAGS.num_workers) as pool,
    ):
        writer = csv.writer(f)
        writer.writerow([
            "Interceptor speed [m/s]",
            "Range [m]",
            "Relative azimuth [deg]",
            "Relative elevation [deg]",
            "Threat speed [m/s]",
            "Threat heading azimuth [deg]",
            "Threat heading elevation [deg]",
            "Success",
            "Minimum separation [m]",
            "Time of minimum separation [s]",
            "Reason for ending engagement",
        ])

        for sample, result in pool.imap(
                runner,
                samples,
                chunksize=1,
        ):
            if result is None:
                continue
            success = result.reason == TerminationReason.INTERCEPT
            writer.writerow([
                *sample,
                success,
                result.min_separation,
                result.time_of_min_separation,
                result.reason,
            ])


if __name__ == "__main__":
    flags.DEFINE_string(
        "engagement_config",
        "simulation/swarm/reachability/configs/engagement_config.pbtxt",
        "Engagement configuration.")
    flags.DEFINE_string(
        "interceptor_config",
        "simulation/swarm/reachability/configs/micromissile.pbtxt",
        "Interceptor configuration.")
    flags.DEFINE_string("threat_config",
                        "simulation/swarm/reachability/configs/ucav.pbtxt",
                        "Threat configuration.")
    flags.DEFINE_float("min_interceptor_speed", 1000,
                       "Minimum interceptor speed in m/s.")
    flags.DEFINE_float("max_interceptor_speed", 1000,
                       "Maximum interceptor speed in m/s.")
    flags.DEFINE_float("interceptor_speed_step", 200,
                       "Interceptor speed step in m/s.")
    flags.DEFINE_float("min_range", 1000, "Minimum range in m.")
    flags.DEFINE_float("max_range", 3000, "Maximum range in m.")
    flags.DEFINE_float("range_step", 1000, "Range step in m.")
    flags.DEFINE_float("min_relative_azimuth", -60,
                       "Minimum relative azimuth in degrees.")
    flags.DEFINE_float("max_relative_azimuth", 60,
                       "Maximum relative azimuth in degrees.")
    flags.DEFINE_float("relative_azimuth_step", 20,
                       "Relative azimuth step in degrees.")
    flags.DEFINE_float("min_relative_elevation", -60,
                       "Minimum relative elevation in degrees.")
    flags.DEFINE_float("max_relative_elevation", 60,
                       "Maximum relative elevation in degrees.")
    flags.DEFINE_float("relative_elevation_step", 20,
                       "Relative elevation step in degrees.")
    flags.DEFINE_float("min_threat_speed", 120, "Minimum threat speed in m/s.")
    flags.DEFINE_float("max_threat_speed", 120, "Maximum threat speed in m/s.")
    flags.DEFINE_float("threat_speed_step", 10, "Threat speed step in m/s.")
    flags.DEFINE_float("min_threat_heading_azimuth", 180,
                       "Minimum threat heading azimuth in degrees.")
    flags.DEFINE_float("max_threat_heading_azimuth", 180,
                       "Maximum threat heading azimuth in degrees.")
    flags.DEFINE_float("threat_heading_azimuth_step", 20,
                       "Threat heading azimuth step in degrees.")
    flags.DEFINE_float("min_threat_heading_elevation", 0,
                       "Minimum threat heading elevation in degrees.")
    flags.DEFINE_float("max_threat_heading_elevation", 0,
                       "Maximum threat heading elevation in degrees.")
    flags.DEFINE_float("threat_heading_elevation_step", 20,
                       "Threat heading elevation step in degrees.")
    flags.DEFINE_string("output", None, "Output CSV file.")
    flags.DEFINE_integer("num_workers", 16, "Number of workers.")
    flags.mark_flag_as_required("output")

    app.run(main)
