// The missile class represents the dynamics of a single missile.

#pragma once

#include <string>

#include "absl/strings/str_format.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "simulation/swarm/threat/threat.h"
#include "utils/protobuf.h"

namespace swarm::threat {

// Missile.
class Missile : public Threat {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/threat/missile.pbtxt";

  Missile() = default;

  explicit Missile(const AgentConfig& config) : Threat(config) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }
  Missile(const AgentConfig& config, const double t_creation, const bool ready)
      : Threat(config, t_creation, ready) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }

  Missile(const Missile&) = default;
  Missile& operator=(const Missile&) = default;
};

}  // namespace swarm::threat
