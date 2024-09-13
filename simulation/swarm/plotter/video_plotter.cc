#include "simulation/swarm/plotter/video_plotter.h"

#include <algorithm>
#include <cmath>
#include <memory>
#include <vector>

#include "absl/strings/str_format.h"
#include "opencv2/core/eigen.hpp"
#include "opencv2/viz.hpp"
#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/state_history.h"

namespace swarm::plotter {

void VideoPlotter::PlotImpl(
    const double t_step,
    const std::vector<std::unique_ptr<agent::Agent>>& missiles,
    const std::vector<std::unique_ptr<agent::Agent>>& targets) {
  // Determine the time span to plot.
  int t_end = 0;
  for (const auto& missile : missiles) {
    if (missile->history().back().t > t_end) {
      t_end = std::ceil(missile->history().back().t);
    }
  }
  for (const auto& target : targets) {
    if (target->history().back().t > t_end) {
      t_end = std::ceil(target->history().back().t);
    }
  }

  // Generate widgets for the missiles and the targets.
  std::vector<std::unique_ptr<cv::viz::Widget3D>> missile_widgets(
      missiles.size());
  std::transform(missiles.cbegin(), missiles.cend(), missile_widgets.begin(),
                 [](const std::unique_ptr<agent::Agent>& missile) {
                   return GenerateWidget(missile->history().front().state,
                                         cv::viz::Color::blue());
                 });
  std::vector<std::unique_ptr<cv::viz::Widget3D>> target_widgets(
      targets.size());
  std::transform(targets.cbegin(), targets.cend(), target_widgets.begin(),
                 [](const std::unique_ptr<agent::Agent>& target) {
                   return GenerateWidget(target->history().front().state,
                                         cv::viz::Color::red());
                 });

  // Add the widgets to the window.
  for (int missile_index = 0; missile_index < missile_widgets.size();
       ++missile_index) {
    window_.showWidget(absl::StrFormat("Missile %d", missile_index),
                       *missile_widgets[missile_index]);
  }
  for (int target_index = 0; target_index < target_widgets.size();
       ++target_index) {
    window_.showWidget(absl::StrFormat("Target %d", target_index),
                       *target_widgets[target_index]);
  }

  // Maintain an iterator for each missile and target.
  std::vector<state::StateHistory::const_iterator> missile_iterators(
      missiles.size());
  std::transform(missiles.cbegin(), missiles.cend(), missile_iterators.begin(),
                 [](const std::unique_ptr<agent::Agent>& missile) {
                   return missile->history().cbegin();
                 });
  std::vector<state::StateHistory::const_iterator> target_iterators(
      targets.size());
  std::transform(targets.cbegin(), targets.cend(), target_iterators.begin(),
                 [](const std::unique_ptr<agent::Agent>& target) {
                   return target->history().cbegin();
                 });

  // Plot each frame at a time.
  const double t_plot_interval = 1 / kAnimationFps;
  for (double t_plot = 0; t_plot < t_end; t_plot += t_plot_interval) {
    // Update the missiles.
    for (int missile_index = 0; missile_index < missiles.size();
         ++missile_index) {
      while (missile_iterators[missile_index]->t < t_plot &&
             missile_iterators[missile_index] !=
                 missiles[missile_index]->history().cend()) {
        ++missile_iterators[missile_index];
      }
      cv::Affine3d pose(
          cv::Mat::eye(3, 3, CV_64F),
          cv::Vec3d(missile_iterators[missile_index]->state.position().x(),
                    missile_iterators[missile_index]->state.position().y(),
                    missile_iterators[missile_index]->state.position().z()));
      missile_widgets[missile_index]->setPose(pose);
    }

    // Update the targets.
    for (int target_index = 0; target_index < targets.size(); ++target_index) {
      while (target_iterators[target_index]->t < t_plot &&
             target_iterators[target_index] !=
                 targets[target_index]->history().cend()) {
        ++target_iterators[target_index];
      }
      cv::Affine3d pose(
          cv::Mat::eye(3, 3, CV_64F),
          cv::Vec3d(target_iterators[target_index]->state.position().x(),
                    target_iterators[target_index]->state.position().y(),
                    target_iterators[target_index]->state.position().z()));
      target_widgets[target_index]->setPose(pose);
    }

    window_.spinOnce(/*time=*/t_plot_interval, /*force_redraw=*/false);
  }
}

std::unique_ptr<cv::viz::Widget3D> VideoPlotter::GenerateWidget(
    const State& state, const cv::viz::Color color) {
  const Eigen::Vector3d center{state.position().x(), state.position().y(),
                               state.position().z()};
  cv::Mat center_matrix;
  cv::eigen2cv(center, center_matrix);
  cv::Point3d center_point(center_matrix);
  const Eigen::Vector3d velocity{state.velocity().x(), state.velocity().y(),
                                 state.velocity().z()};
  Eigen::Vector3d tip = center + velocity.normalized() * 200;
  cv::Mat tip_matrix;
  cv::eigen2cv(tip, tip_matrix);
  cv::Point3d tip_point(tip_matrix);
  return std::make_unique<cv::viz::WCone>(
      /*radius=*/100, center_point, tip_point, /*sphere_resolution=*/10, color);
}

}  // namespace swarm::plotter
