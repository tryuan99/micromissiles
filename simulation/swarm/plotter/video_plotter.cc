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
    const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
    const std::vector<std::unique_ptr<agent::Agent>>& threats) {
  // Determine the time span to plot.
  int t_end = 0;
  for (const auto& interceptor : interceptors) {
    if (interceptor->history().back().t > t_end) {
      t_end = std::ceil(interceptor->history().back().t);
    }
  }
  for (const auto& threat : threats) {
    if (threat->history().back().t > t_end) {
      t_end = std::ceil(threat->history().back().t);
    }
  }

  // Generate widgets for the interceptors and the threats.
  std::vector<std::unique_ptr<cv::viz::Widget3D>> interceptor_widgets(
      interceptors.size());
  std::transform(interceptors.cbegin(), interceptors.cend(),
                 interceptor_widgets.begin(),
                 [](const std::unique_ptr<agent::Agent>& interceptor) {
                   return GenerateWidget(interceptor->history().front().state,
                                         cv::viz::Color::blue());
                 });
  std::vector<std::unique_ptr<cv::viz::Widget3D>> threat_widgets(
      threats.size());
  std::transform(threats.cbegin(), threats.cend(), threat_widgets.begin(),
                 [](const std::unique_ptr<agent::Agent>& threat) {
                   return GenerateWidget(threat->history().front().state,
                                         cv::viz::Color::red());
                 });

  // Add the widgets to the window.
  for (int interceptor_index = 0;
       interceptor_index < interceptor_widgets.size(); ++interceptor_index) {
    window_.showWidget(absl::StrFormat("Interceptor %d", interceptor_index),
                       *interceptor_widgets[interceptor_index]);
  }
  for (int threat_index = 0; threat_index < threat_widgets.size();
       ++threat_index) {
    window_.showWidget(absl::StrFormat("Threat %d", threat_index),
                       *threat_widgets[threat_index]);
  }

  // Maintain an iterator for each interceptor and threat.
  std::vector<state::StateHistory::const_iterator> interceptor_iterators(
      interceptors.size());
  std::transform(interceptors.cbegin(), interceptors.cend(),
                 interceptor_iterators.begin(),
                 [](const std::unique_ptr<agent::Agent>& interceptor) {
                   return interceptor->history().cbegin();
                 });
  std::vector<state::StateHistory::const_iterator> threat_iterators(
      threats.size());
  std::transform(threats.cbegin(), threats.cend(), threat_iterators.begin(),
                 [](const std::unique_ptr<agent::Agent>& threat) {
                   return threat->history().cbegin();
                 });

  // Plot each frame at a time.
  const double t_plot_interval = 1 / kAnimationFps;
  for (double t_plot = 0; t_plot < t_end; t_plot += t_plot_interval) {
    // Update the interceptors.
    for (int interceptor_index = 0; interceptor_index < interceptors.size();
         ++interceptor_index) {
      while (interceptor_iterators[interceptor_index]->t < t_plot &&
             interceptor_iterators[interceptor_index] !=
                 interceptors[interceptor_index]->history().cend()) {
        ++interceptor_iterators[interceptor_index];
      }
      cv::Affine3d pose(
          cv::Mat::eye(3, 3, CV_64F),
          cv::Vec3d(
              interceptor_iterators[interceptor_index]->state.position().x(),
              interceptor_iterators[interceptor_index]->state.position().y(),
              interceptor_iterators[interceptor_index]->state.position().z()));
      interceptor_widgets[interceptor_index]->setPose(pose);
    }

    // Update the threats.
    for (int threat_index = 0; threat_index < threats.size(); ++threat_index) {
      while (threat_iterators[threat_index]->t < t_plot &&
             threat_iterators[threat_index] !=
                 threats[threat_index]->history().cend()) {
        ++threat_iterators[threat_index];
      }
      cv::Affine3d pose(
          cv::Mat::eye(3, 3, CV_64F),
          cv::Vec3d(threat_iterators[threat_index]->state.position().x(),
                    threat_iterators[threat_index]->state.position().y(),
                    threat_iterators[threat_index]->state.position().z()));
      threat_widgets[threat_index]->setPose(pose);
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
