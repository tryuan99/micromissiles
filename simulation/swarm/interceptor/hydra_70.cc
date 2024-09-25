#include "simulation/swarm/interceptor/hydra_70.h"

#include <Eigen/Dense>
#include <memory>
#include <stdexcept>
#include <utility>
#include <vector>

#include "absl/strings/str_format.h"
#include "simulation/swarm/agent.h"
#include "simulation/swarm/interceptor/micromissile.h"
#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {

std::vector<std::unique_ptr<agent::Agent>> Hydra70::Spawn(const double t) {
  if (has_spawned_) {
    return std::vector<std::unique_ptr<agent::Agent>>();
  }

  const auto num_submunitions = submunitions_config().num_submunitions();
  const auto launch_time = dynamic_config().launch_config().launch_time();
  const auto submunitions_launch_time =
      submunitions_config().launch_config().launch_time();
  if (t >= t_creation_ + launch_time + submunitions_launch_time) {
    // Define the interceptor configuration for the submunitions.
    const auto submunitions_type =
        submunitions_config().agent_config().interceptor_type();
    AgentConfig submunitions_interceptor_config(
        submunitions_config().agent_config());
    submunitions_interceptor_config.mutable_initial_state()->CopyFrom(state());

    // Create the interceptors for the submunitions.
    std::vector<std::unique_ptr<agent::Agent>> spawned_interceptors;
    spawned_interceptors.reserve(num_submunitions);
    for (int i = 0; i < num_submunitions; ++i) {
      spawned_interceptors.emplace_back(
          CreateSubmunition(submunitions_type, submunitions_interceptor_config,
                            t, /*ready=*/true));
    }
    has_spawned_ = true;
    return spawned_interceptors;
  }
  return std::vector<std::unique_ptr<agent::Agent>>();
}

void Hydra70::UpdateMidCourse(const double t) {
  // The Hydra-70 rocket is unguided, so only consider gravity and drag.
  Eigen::Vector3d acceleration_input = Eigen::Vector3d::Zero();

  // Calculate and set the total acceleration.
  const auto acceleration = CalculateAcceleration(acceleration_input);
  state_.mutable_acceleration()->set_x(acceleration(0));
  state_.mutable_acceleration()->set_y(acceleration(1));
  state_.mutable_acceleration()->set_z(acceleration(2));
}

template <typename... Args>
std::unique_ptr<Interceptor> Hydra70::CreateSubmunition(
    const InterceptorType type, Args&&... args) {
  switch (type) {
    case InterceptorType::MICROMISSILE: {
      return std::make_unique<Micromissile>(std::forward<Args>(args)...);
    }
    default: {
      throw std::invalid_argument(
          absl::StrFormat("Invalid submunition type: %d.", type));
    }
  }
}

}  // namespace swarm::interceptor
