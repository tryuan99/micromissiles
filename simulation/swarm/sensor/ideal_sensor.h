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

  // Sense the position of a target, including the range, the azimuth, and the
  // elevation.
  SensorOutput SensePosition(const agent::Agent& target) const;

  // Sense the velocity of a target, including the range rate, the azimuth rate
  // of change, and the elevation rate of change.
  SensorOutput SenseVelocity(const agent::Agent& target) const;
};

}  // namespace swarm::sensor
