#include "simulation/swarm/controller/apn_controller.h"

#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::controller {

void ApnController::PlanImpl(const SensorOutput& sensor_output) {
  PnController::PlanImpl(sensor_output);

  // Project the target's acceleration vector to be normal to the roll axis.
  const auto target_acceleration = agent_->target().GetAcceleration();
  const auto principal_axes = agent_->GetNormalizedPrincipalAxes();
  const auto normal_target_acceleration =
      target_acceleration -
      target_acceleration.dot(principal_axes.roll) * principal_axes.roll;

  // Add a feedforward term to the desired acceleration vector.
  acceleration_input_ +=
      kProportionalNavigationGain / 2 * normal_target_acceleration;
}

}  // namespace swarm::controller
