// The video plotter plots the trajectories of the agents over time.

#pragma once

#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/plotter/plotter.h"

namespace swarm::plotter {

// Video plotter.
class VideoPlotter : public Plotter {
 public:
  // Animation interval in fps.
  static constexpr double kAnimationFps = 50;

  VideoPlotter() = default;

  VideoPlotter(const VideoPlotter&) = delete;
  VideoPlotter& operator=(const VideoPlotter&) = delete;

 protected:
  // Plot the trajectories of the agents.
  void PlotImpl(
      double t_step, const std::vector<std::unique_ptr<agent::Agent>>& missiles,
      const std::vector<std::unique_ptr<agent::Agent>>& targets) override;
};

}  // namespace swarm::plotter
