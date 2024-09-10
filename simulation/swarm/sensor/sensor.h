// The sensor class is an interface for a missile's sensing system.

#pragma once

#include <algorithm>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::sensor {

// Sensor interface.
class Sensor {
 public:
  explicit Sensor(const agent::Agent& agent) : agent_(&agent) {}

  Sensor(const Sensor&) = default;
  Sensor& operator=(const Sensor&) = default;

  virtual ~Sensor() = default;

  // Sense the target.
  virtual SensorOutput Sense(const agent::Agent& target) const = 0;
  std::vector<SensorOutput> Sense(
      const std::vector<agent::Agent>& targets) const {
    std::vector<SensorOutput> sensor_outputs(targets.size());
    std::transform(
        targets.cbegin(), targets.cend(), sensor_outputs.begin(),
        [this](const agent::Agent& target) { return Sense(target); });
    return sensor_outputs;
  }

 protected:
  // Agent on which the sensor is mounted.
  const agent::Agent* agent_ = nullptr;
};

}  // namespace swarm::sensor
