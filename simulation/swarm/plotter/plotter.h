// The plotter class is an interface for plotting the trajectories of the
// agents.

#pragma once

#include <memory>
#include <vector>

#include "opencv2/viz.hpp"
#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::plotter {

// Plotter interface.
class Plotter {
 public:
  Plotter() : window_(cv::viz::Viz3d("Micromissiles")) {}

  Plotter(const Plotter&) = delete;
  Plotter& operator=(const Plotter&) = delete;

  virtual ~Plotter() = default;

  // Plot the trajectories of the agents.
  void Plot(double t_step,
            const std::vector<std::unique_ptr<agent::Agent>>& missiles,
            const std::vector<std::unique_ptr<agent::Agent>>& targets);

 protected:
  // Get the visualization color corresponding to the color enumeration.
  static cv::viz::Color GetColor(Color color);

  // Plot the missile at the given state.
  static void PlotMissile(const State& state);

  // Plot the target at the given state.
  static void PlotTarget(const State& state);

  // Plot the trajectories of the agents.
  virtual void PlotImpl(
      double t_step, const std::vector<std::unique_ptr<agent::Agent>>& missiles,
      const std::vector<std::unique_ptr<agent::Agent>>& targets) = 0;

  // 3D visualization window.
  cv::viz::Viz3d window_;
};

}  // namespace swarm::plotter
