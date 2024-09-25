#include "simulation/swarm/plotter/static_plotter.h"

#include <Eigen/Dense>
#include <algorithm>
#include <cstdbool>
#include <memory>
#include <vector>

#include "opencv2/core/eigen.hpp"
#include "opencv2/viz.hpp"
#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/state_history.h"

namespace swarm::plotter {

void StaticPlotter::PlotImpl(
    const double t_step,
    const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
    const std::vector<std::unique_ptr<agent::Agent>>& threats) {
  // Plot the interceptors and their trajectories.
  cv::viz::WWidgetMerger interceptor_widgets;
  cv::viz::WWidgetMerger interceptor_trajectory_widgets;
  for (const auto& interceptor : interceptors) {
    interceptor_widgets.addWidget(
        *GenerateInterceptorWidget(interceptor->state(), interceptor->hit()));
    interceptor_trajectory_widgets.addWidget(
        *GenerateTrajectoryWidget(interceptor->history()));
  }
  interceptor_widgets.finalize();
  interceptor_trajectory_widgets.finalize();
  window_.showWidget("Interceptors", interceptor_widgets);
  window_.showWidget("Interceptor Trajectories",
                     interceptor_trajectory_widgets);

  // Plot the threats and their trajectories.
  cv::viz::WWidgetMerger threat_widgets;
  cv::viz::WWidgetMerger threat_trajectory_widgets;
  for (const auto& threat : threats) {
    threat_widgets.addWidget(
        *GenerateThreatWidget(threat->state(), threat->hit()));
    threat_trajectory_widgets.addWidget(
        *GenerateTrajectoryWidget(threat->history()));
  }
  threat_widgets.finalize();
  threat_trajectory_widgets.finalize();
  window_.showWidget("Threats", threat_widgets);
  window_.showWidget("Threat Trajectories", threat_trajectory_widgets);
}

std::unique_ptr<cv::viz::Widget3D> StaticPlotter::GenerateInterceptorWidget(
    const State& state, const bool hit) {
  const Eigen::Vector3d center{state.position().x(), state.position().y(),
                               state.position().z()};
  cv::Mat center_matrix;
  cv::eigen2cv(center, center_matrix);
  cv::Point3d center_point(center_matrix);
  if (hit) {
    return std::make_unique<cv::viz::WSphere>(center_point, /*radius=*/100,
                                              /*sphere_resolution=*/10,
                                              cv::viz::Color::green());
  }

  const Eigen::Vector3d velocity{state.velocity().x(), state.velocity().y(),
                                 state.velocity().z()};
  Eigen::Vector3d tip = center + velocity.normalized() * 200;
  cv::Mat tip_matrix;
  cv::eigen2cv(tip, tip_matrix);
  cv::Point3d tip_point(tip_matrix);
  return std::make_unique<cv::viz::WCone>(
      /*radius=*/100, center_point, tip_point, /*sphere_resolution=*/10,
      cv::viz::Color::blue());
}

std::unique_ptr<cv::viz::Widget3D> StaticPlotter::GenerateThreatWidget(
    const State& state, const bool hit) {
  const Eigen::Vector3d center{state.position().x(), state.position().y(),
                               state.position().z()};
  cv::Mat center_matrix;
  cv::eigen2cv(center, center_matrix);
  cv::Point3d center_point(center_matrix);
  if (hit) {
    return std::make_unique<cv::viz::WSphere>(center_point, /*radius=*/1,
                                              /*sphere_resolution=*/100,
                                              cv::viz::Color::pink());
  }

  const Eigen::Vector3d velocity{state.velocity().x(), state.velocity().y(),
                                 state.velocity().z()};
  Eigen::Vector3d tip = center + velocity.normalized() * 200;
  cv::Mat tip_matrix;
  cv::eigen2cv(tip, tip_matrix);
  cv::Point3d tip_point(tip_matrix);
  return std::make_unique<cv::viz::WCone>(
      /*radius=*/100, center_point, tip_point, /*sphere_resolution=*/10,
      cv::viz::Color::red());
}

std::unique_ptr<cv::viz::Widget3D> StaticPlotter::GenerateTrajectoryWidget(
    const state::StateHistory& history) {
  std::vector<cv::Affine3d> trajectory(history.size());
  std::transform(history.cbegin(), history.cend(), trajectory.begin(),
                 [](const state::StateHistory::Record& record) {
                   return cv::Affine3d(cv::Mat::eye(3, 3, CV_64F),
                                       cv::Vec3d(record.state.position().x(),
                                                 record.state.position().y(),
                                                 record.state.position().z()));
                 });
  return std::make_unique<cv::viz::WTrajectory>(trajectory);
}

}  // namespace swarm::plotter
