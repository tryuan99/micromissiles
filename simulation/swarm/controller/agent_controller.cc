#include "simulation/swarm/controller/agent_controller.h"

namespace swarm::controller {

void AgentController::Plan() {
  // Find the relative transformation to the target..
  const auto relative_transformation =
      agent_->GetRelativeTransformation(agent_->target_model());
  PlanImpl(relative_transformation);
}

}  // namespace swarm::controller
