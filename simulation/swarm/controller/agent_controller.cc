#include "simulation/swarm/controller/agent_controller.h"

namespace swarm::controller {

void AgentController::Plan() {
  // Sense the target.
  const auto sensor_output = sensor_.Sense(agent_->target_model());
  PlanImpl(sensor_output);
}

}  // namespace swarm::controller
