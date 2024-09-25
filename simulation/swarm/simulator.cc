#include "simulation/swarm/simulator.h"

#include <cstdbool>
#include <memory>
#include <utility>

#include "base/logging.h"
#include "simulation/swarm/assignment/distance_assignment.h"
#include "simulation/swarm/interceptor/interceptor_factory.h"
#include "simulation/swarm/plotter/plotter_factory.h"
#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/threat/threat_factory.h"
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
  interceptors_.reserve(simulator_config.interceptor_configs_size());
  interceptor::InterceptorFactory interceptor_factory;
  for (const auto& interceptor_config :
       simulator_config.interceptor_configs()) {
    interceptors_.emplace_back(interceptor_factory.CreateInterceptor(
        interceptor_config.interceptor_type(), interceptor_config,
        /*t_creation=*/0,
        /*ready=*/false));
  }
  threats_.reserve(simulator_config.threat_configs_size());
  threat::ThreatFactory threat_factory;
  for (const auto& threat_config : simulator_config.threat_configs()) {
    threats_.emplace_back(
        threat_factory.CreateThreat(threat_config.threat_type(), threat_config,
                                    /*t_creation=*/0, /*ready=*/false));
  }
  thread_pool_.Start();
}

void Simulator::Run(const double t_end) {
  for (double t = 0; t < t_end; t += t_step_) {
    LOG_EVERY_N(INFO, 1000) << "Simulating time t=" << t << ".";

    // Have all interceptors check their threats.
    for (auto& interceptor : interceptors_) {
      interceptor->CheckTarget();
    }

    // Allow agents to spawn new instances.
    std::vector<std::unique_ptr<agent::Agent>> spawned_interceptors;
    std::vector<std::unique_ptr<agent::Agent>> spawned_threats;
    for (auto& interceptor : interceptors_) {
      auto spawned = interceptor->Spawn(t);
      spawned_interceptors.reserve(spawned_interceptors.size() +
                                   spawned.size());
      std::move(spawned.begin(), spawned.end(),
                std::back_inserter(spawned_interceptors));
    }
    for (auto& threat : threats_) {
      auto spawned = threat->Spawn(t);
      spawned_threats.reserve(spawned_threats.size() + spawned.size());
      std::move(spawned.begin(), spawned.end(),
                std::back_inserter(spawned_threats));
    }
    interceptors_.reserve(interceptors_.size() + spawned_interceptors.size());
    std::move(spawned_interceptors.begin(), spawned_interceptors.end(),
              std::back_inserter(interceptors_));
    threats_.reserve(threats_.size() + spawned_threats.size());
    std::move(spawned_threats.begin(), spawned_threats.end(),
              std::back_inserter(threats_));

    // Assign the threats to the interceptors.
    assignment_->Assign(interceptors_, threats_);
    for (const auto& [interceptor_index, threat_index] :
         assignment_->assignments()) {
      interceptors_[interceptor_index]->AssignTarget(
          threats_[threat_index].get());
    }

    // Update the acceleration vector of each agent.
    for (auto& interceptor : interceptors_) {
      if (!interceptor->has_terminated()) {
        interceptor->Update(t);
      }
    }
    for (auto& threat : threats_) {
      if (!threat->has_terminated()) {
        threat->Update(t);
      }
    }

    // Step to the next time step.
    for (auto& interceptor : interceptors_) {
      if (interceptor->has_launched() && !interceptor->has_terminated()) {
        thread_pool_.QueueJob([&]() { interceptor->Step(t, t_step_); });
      }
    }
    for (auto& threat : threats_) {
      if (threat->has_launched() && !threat->has_terminated()) {
        thread_pool_.QueueJob([&]() { threat->Step(t, t_step_); });
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
  plotter->Plot(t_step_, interceptors_, threats_);
}

}  // namespace swarm::simulator
