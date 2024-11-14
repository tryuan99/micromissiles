#include "simulation/swarm/sensor/ideal_sensor.h"

#include <cmath>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::sensor {

SensorOutput IdealSensor::Sense(const agent::Agent& target) const {
  SensorOutput target_sensor_output;

  // Adapt the relative transformation to the target for the sensor output.
  const auto relative_transformation =
      agent_->GetRelativeTransformation(target);

  // Sense the target's position.
  target_sensor_output.mutable_position()->CopyFrom(
      relative_transformation.position());
  target_sensor_output.mutable_position_cartesian()->CopyFrom(
      relative_transformation.position_cartesian());

  // Sense the target's velocity.
  target_sensor_output.mutable_velocity()->CopyFrom(
      relative_transformation.velocity());

  return target_sensor_output;
}

}  // namespace swarm::sensor
