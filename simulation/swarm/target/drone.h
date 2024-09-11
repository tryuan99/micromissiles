// The drone class represents the dynamics of a single drone.

#pragma once

#include <string>

#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "simulation/swarm/target/target.h"
#include "simulation/swarm/utils.h"

namespace swarm::target {

// Drone.
class Drone : public Target {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/target/drone.pbtxt";

  Drone() = default;

  explicit Drone(const AgentConfig& config) : Target(config) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }
  Drone(const AgentConfig& config, const double t_creation, const bool ready)
      : Target(config, t_creation, ready) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }

  Drone(const Drone&) = default;
  Drone& operator=(const Drone&) = default;
};

}  // namespace swarm::target
