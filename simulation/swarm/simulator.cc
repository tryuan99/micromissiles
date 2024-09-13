#include "simulation/swarm/simulator.h"

#include <cstdbool>
#include <memory>
#include <utility>

#include "base/logging.h"
#include "simulation/swarm/assignment/distance_assignment.h"
#include "simulation/swarm/missile/missile_factory.h"
#include "simulation/swarm/plotter/plotter_factory.h"
#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/target/target_factory.h"
#include "utils/thread_pool.h"

namespace swarm::simulator {

namespace {
// Number of threads.
constexpr int kNumThreads = 8;
}  // namespace

Simulator::Simulator(const SimulatorConfig& simulator_config)
    : t_step_(simulator_config.step_time()),
      assignment_(std::make_unique<assignment::DistanceAssignment>()),
      thread_pool_(::utils::ThreadPool(kNumThreads)) {
  missiles_.reserve(simulator_config.missile_configs_size());
  missile::MissileFactory missile_factory;
  for (const auto& missile_config : simulator_config.missile_configs()) {
    missiles_.emplace_back(missile_factory.CreateMissile(
        missile_config.missile_type(), missile_config, /*t_creation=*/0,
        /*ready=*/false));
  }
  targets_.reserve(simulator_config.target_configs_size());
  target::TargetFactory target_factory;
  for (const auto& target_config : simulator_config.target_configs()) {
    targets_.emplace_back(
        target_factory.CreateTarget(target_config.target_type(), target_config,
                                    /*t_creation=*/0, /*ready=*/false));
  }
  thread_pool_.Start();
}

void Simulator::Run(const double t_end) {
  for (double t = 0; t < t_end; t += t_step_) {
    LOG_EVERY_N(INFO, 1000) << "Simulating time t=" << t << ".";

    // Have all missiles check their targets.
    for (auto& missile : missiles_) {
      missile->CheckTarget();
    }

    // Allow agents to spawn new instances.
    std::vector<std::unique_ptr<agent::Agent>> spawned_missiles;
    std::vector<std::unique_ptr<agent::Agent>> spawned_targets;
    for (auto& missile : missiles_) {
      auto spawned = missile->Spawn(t);
      spawned_missiles.reserve(spawned_missiles.size() + spawned.size());
      std::move(spawned.begin(), spawned.end(),
                std::back_inserter(spawned_missiles));
    }
    for (auto& target : targets_) {
      auto spawned = target->Spawn(t);
      spawned_targets.reserve(spawned_targets.size() + spawned.size());
      std::move(spawned.begin(), spawned.end(),
                std::back_inserter(spawned_targets));
    }
    missiles_.reserve(missiles_.size() + spawned_missiles.size());
    std::move(spawned_missiles.begin(), spawned_missiles.end(),
              std::back_inserter(missiles_));
    targets_.reserve(targets_.size() + spawned_targets.size());
    std::move(spawned_targets.begin(), spawned_targets.end(),
              std::back_inserter(targets_));

    // Assign the targets to the missiles.
    assignment_->Assign(missiles_, targets_);
    for (const auto& [missile_index, target_index] :
         assignment_->assignments()) {
      missiles_[missile_index]->AssignTarget(targets_[target_index].get());
    }

    // Update the acceleration vector of each agent.
    for (auto& missile : missiles_) {
      if (!missile->has_terminated()) {
        missile->Update(t);
      }
    }
    for (auto& target : targets_) {
      if (!target->has_terminated()) {
        target->Update(t);
      }
    }

    // Step to the next time step.
    for (auto& missile : missiles_) {
      if (missile->has_launched() && !missile->has_terminated()) {
        thread_pool_.QueueJob([&]() { missile->Step(t, t_step_); });
      }
    }
    for (auto& target : targets_) {
      if (target->has_launched() && !target->has_terminated()) {
        thread_pool_.QueueJob([&]() { target->Step(t, t_step_); });
      }
    }
    thread_pool_.Wait();
  }
}

// Plot the agent trajectories over time.
void Simulator::Plot(const bool animate,
                     const std::string& animation_file) const {
  plotter::PlotterFactory plotter_factory;
  const auto plotter = plotter_factory.CreatePlotter(animate);
  plotter->Plot(t_step_, missiles_, targets_);
}

}  // namespace swarm::simulator
