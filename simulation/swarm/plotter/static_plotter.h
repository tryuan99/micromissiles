// The static plotter plots the trajectories of the agents as a static image.

#pragma once

#include <cstdbool>
#include <memory>
#include <vector>

#include "opencv2/viz.hpp"
#include "simulation/swarm/agent.h"
#include "simulation/swarm/plotter/plotter.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/state_history.h"

namespace swarm::plotter {

// Static plotter.
class StaticPlotter : public Plotter {
 public:
  StaticPlotter() = default;

  StaticPlotter(const StaticPlotter&) = delete;
  StaticPlotter& operator=(const StaticPlotter&) = delete;

 protected:
  // Plot the trajectories of the agents.
  void PlotImpl(
      double t_step, const std::vector<std::unique_ptr<agent::Agent>>& missiles,
      const std::vector<std::unique_ptr<agent::Agent>>& targets) override;

 private:
  // Generate a missile widget.
  static std::unique_ptr<cv::viz::Widget3D> GenerateMissileWidget(
      const State& state, bool hit);

  // Generate a target widget.
  static std::unique_ptr<cv::viz::Widget3D> GenerateTargetWidget(
      const State& state, bool hit);

  // Generate a trajectory widget.
  static std::unique_ptr<cv::viz::Widget3D> GenerateTrajectoryWidget(
      const state::StateHistory& history);
};

}  // namespace swarm::plotter
