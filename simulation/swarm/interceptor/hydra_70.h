// The Hydra-70 class represents the dynamics of a single unguided Hydra-70
// rocket.

#pragma once

#include <cstdbool>
#include <memory>
#include <string>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/interceptor/interceptor.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "utils/protobuf.h"

namespace swarm::interceptor {

// Hydra-70.
class Hydra70 : public Interceptor {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/interceptor/hydra_70.pbtxt";

  Hydra70() = default;

  explicit Hydra70(const AgentConfig& config) : Interceptor(config) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }
  Hydra70(const AgentConfig& config, const double t_creation, const bool ready)
      : Interceptor(config, t_creation, ready) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }

  Hydra70(const Hydra70&) = delete;
  Hydra70& operator=(const Hydra70&) = delete;

  // Return whether a threat can be assigned to the interceptor.
  bool assignable() const override { return false; }

  // Spawn the submunitions.
  std::vector<std::unique_ptr<agent::Agent>> Spawn(double t) override;

 protected:
  // Update the agent's state in the midcourse flight phase.
  void UpdateMidCourse(double t) override;

 private:
  // Create a submunition based on its type.
  template <typename... Args>
  static std::unique_ptr<Interceptor> CreateSubmunition(
      const InterceptorType type, Args&&... args);

  // If true, the Hydra-70 rocket has spawned its submunitions.
  bool has_spawned_ = false;
};

}  // namespace swarm::interceptor
