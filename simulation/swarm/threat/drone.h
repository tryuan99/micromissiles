// The drone class represents the dynamics of a single drone.

#pragma once

#include <string>

#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "simulation/swarm/threat/threat.h"
#include "utils/protobuf.h"

namespace swarm::threat {

// Drone.
class Drone : public Threat {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/threat/drone.pbtxt";

  Drone() = default;

  explicit Drone(const AgentConfig& config) : Threat(config) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }
  Drone(const AgentConfig& config, const double t_creation, const bool ready)
      : Threat(config, t_creation, ready) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }

  Drone(const Drone&) = default;
  Drone& operator=(const Drone&) = default;
};

}  // namespace swarm::threat
