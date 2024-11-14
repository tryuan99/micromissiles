#include "simulation/swarm/controller/pn_controller.h"

#include "simulation/swarm/proto/transformation.pb.h"

namespace swarm::controller {

void PnController::PlanImpl(const Transformation& relative_transformation) {
  // In proportional navigation, the acceleration vector should be proportional
  // to the rate of change of the bearing.
  const auto azimuth_velocity = relative_transformation.velocity().azimuth();
  const auto elevation_velocity =
      relative_transformation.velocity().elevation();
  const auto closing_velocity = -relative_transformation.velocity().range();

  // Calculate the desired acceleration vector. The missile cannot accelerate
  // along the roll axis.
  const auto principal_axes = agent_->GetNormalizedPrincipalAxes();
  acceleration_input_ = kProportionalNavigationGain *
                        (azimuth_velocity * principal_axes.pitch +
                         elevation_velocity * principal_axes.yaw) *
                        closing_velocity;
}

}  // namespace swarm::controller
