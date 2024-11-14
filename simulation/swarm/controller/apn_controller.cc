#include "simulation/swarm/controller/apn_controller.h"

#include <Eigen/Dense>

#include "simulation/swarm/proto/transformation.pb.h"

namespace swarm::controller {

void ApnController::PlanImpl(const Transformation& relative_transformation) {
  PnController::PlanImpl(relative_transformation);

  // Project the target's acceleration vector to be normal to the roll axis.
  const Eigen::Vector3d target_acceleration{
      relative_transformation.acceleration_cartesian().x(),
      relative_transformation.acceleration_cartesian().y(),
      relative_transformation.acceleration_cartesian().z()};
  const auto principal_axes = agent_->GetNormalizedPrincipalAxes();
  const auto normal_target_acceleration =
      target_acceleration -
      target_acceleration.dot(principal_axes.roll) * principal_axes.roll;

  // Add a feedforward term to the desired acceleration vector.
  acceleration_input_ +=
      kProportionalNavigationGain / 2 * normal_target_acceleration;
}

}  // namespace swarm::controller
