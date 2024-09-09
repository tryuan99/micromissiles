// The micromissile class represents the dynamics of a single micromissile.

#pragma once

#include <Eigen/Dense>
#include <string>

#include "simulation/swarm/missiles/missile.h"
#include "simulation/swarm/proto/missile_config.pb.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/utils.h"

namespace swarm::missile {

// Micromissile.
class Micromissile : public Missile {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/missiles/micromissile.pbtxt";

  Micromissile() = default;

  explicit Micromissile(const MissileConfig& config) : Missile(config) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }
  Micromissile(const MissileConfig& config, const double t_creation,
               const bool ready)
      : Missile(config, t_creation, ready) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }

  Micromissile(const Micromissile&) = default;
  Micromissile& operator=(const Micromissile&) = default;

 protected:
  // Update the agent's state in the midcourse flight phase.
  void UpdateMidCourse(double t) override;

 private:
  // Calculate the acceleration input to the sensor output.
  Eigen::Vector3d CalculateAccelerationInput(
      const auto& SensorOutput sensor_output) const;
};

}  // namespace swarm::missile
