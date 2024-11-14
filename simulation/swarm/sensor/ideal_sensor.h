// The ideal sensor class represents an ideal, omniscient sensor with no bias or
// variance.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/sensor/sensor.h"

namespace swarm::sensor {

// Ideal sensor.
class IdealSensor : public Sensor {
 public:
  explicit IdealSensor(const agent::Agent& agent) : Sensor(agent) {}

  IdealSensor(const IdealSensor&) = default;
  IdealSensor& operator=(const IdealSensor&) = default;

  // Sense the target.
  SensorOutput Sense(const agent::Agent& target) const override;
};

}  // namespace swarm::sensor
