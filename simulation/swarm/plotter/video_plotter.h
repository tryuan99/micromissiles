// The video plotter plots the trajectories of the agents over time.

#pragma once

#include <memory>
#include <vector>

#include "opencv2/viz.hpp"
#include "simulation/swarm/agent.h"
#include "simulation/swarm/plotter/plotter.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::plotter {

// Video plotter.
class VideoPlotter : public Plotter {
 public:
  // Animation interval in fps.
  static constexpr double kAnimationFps = 10;

  VideoPlotter() = default;

  VideoPlotter(const VideoPlotter&) = delete;
  VideoPlotter& operator=(const VideoPlotter&) = delete;

 protected:
  // Plot the trajectories of the agents.
  void PlotImpl(
      double t_step,
      const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
      const std::vector<std::unique_ptr<agent::Agent>>& threats) override;

  // Generate a widget.
  static std::unique_ptr<cv::viz::Widget3D> GenerateWidget(
      const State& state, cv::viz::Color color);
};

}  // namespace swarm::plotter
