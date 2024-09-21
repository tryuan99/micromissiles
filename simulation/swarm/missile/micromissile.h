// The micromissile class represents the dynamics of a single micromissile.

#pragma once

#include <Eigen/Dense>
#include <string>

#include "simulation/swarm/missile/missile.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "utils/protobuf.h"

namespace swarm::missile {

// Micromissile.
class Micromissile : public Missile {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/missile/micromissile.pbtxt";

  // Proportional navigation gain.
  inline static const double kProportionalNavigationGain = 3;

  Micromissile() = default;

  explicit Micromissile(const AgentConfig& config) : Missile(config) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }
  Micromissile(const AgentConfig& config, const double t_creation,
               const bool ready)
      : Missile(config, t_creation, ready) {
    static_config_ =
        utils::LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  }

  Micromissile(const Micromissile&) = delete;
  Micromissile& operator=(const Micromissile&) = delete;

 protected:
  // Update the agent's state in the midcourse flight phase.
  void UpdateMidCourse(double t) override;

 private:
  // Calculate the acceleration input to the sensor output.
  Eigen::Vector3d CalculateAccelerationInput(
      const SensorOutput& sensor_output) const;
};

}  // namespace swarm::missile
