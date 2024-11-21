from absl import app, flags

from simulation.swarm.results.characterization.trajectories_viewer import \
    TrajectoriesViewer

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1

    trajectories_viewer = TrajectoriesViewer(FLAGS.csv_file)
    # trajectories_viewer.plot_all_trajectories()
    # trajectories_viewer.plot_trajectories_with_dispense_time(
    #     FLAGS.submunition_dispense_time)
    # trajectories_viewer.plot_reachability_at_time(FLAGS.time)
    # trajectories_viewer.plot_reachability_around_position_before_time_color_speed(
    #     FLAGS.x_start,
    #     FLAGS.x_end,
    #     FLAGS.y_start,
    #     FLAGS.y_end,
    #     FLAGS.time,
    # )
    # trajectories_viewer.plot_reachability_around_position_before_time_color_time(
    #     FLAGS.x_start,
    #     FLAGS.x_end,
    #     FLAGS.y_start,
    #     FLAGS.y_end,
    #     FLAGS.time,
    # )
    trajectories_viewer.find_optimal_trajectories(
        FLAGS.x_start,
        FLAGS.x_end,
        FLAGS.x_step,
        FLAGS.y_start,
        FLAGS.y_end,
        FLAGS.y_step,
    )


if __name__ == "__main__":
    flags.DEFINE_string("csv_file", None, "Trajectories CSV file.")
    flags.DEFINE_float("submunition_dispense_time", 6,
                       "Submunition dispense time in seconds.")
    flags.DEFINE_float("time", 8, "Time in seconds.")
    flags.DEFINE_float("x_start", 0, "x-position range start in meters.")
    flags.DEFINE_float("x_end", 10000, "x-position range end in meters.")
    flags.DEFINE_float("y_start", 0, "y-position range start in meters.")
    flags.DEFINE_float("y_end", 10000, "y-position range end in meters.")
    flags.DEFINE_float("x_step", 1000, "x-position range step in meters.")
    flags.DEFINE_float("y_step", 1000, "y-position range step in meters.")
    flags.mark_flag_as_required("csv_file")

    app.run(main)
