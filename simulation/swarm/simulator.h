// The simulator class defines all agents and runs the simulation.

#pragma once

#include <cstdbool>
#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/assignment/assignment.h"
#include "simulation/swarm/proto/simulator_config.pb.h"
#include "utils/thread_pool.h"

namespace swarm::simulator {

class Simulator {
 public:
  Simulator(const SimulatorConfig& simulator_config);

  Simulator(const Simulator&) = delete;
  Simulator& operator=(const Simulator&) = delete;

  virtual ~Simulator() { thread_pool_.Stop(); }

  // Run the simulation.
  void Run(double t_end);

  // Plot the agent trajectories over time.
  void Plot(bool animate, const std::string& animation_file) const;

 private:
  // Simulation step time in seconds.
  double t_step_ = 0;

  // Missiles.
  std::vector<std::unique_ptr<agent::Agent>> missiles_;

  // Targets.
  std::vector<std::unique_ptr<agent::Agent>> targets_;

  // Assignment between the missiles and the targets.
  std::unique_ptr<assignment::Assignment> assignment_;

  // Thread pool.
  utils::ThreadPool thread_pool_;
};

}  // namespace swarm::simulator
