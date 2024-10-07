// The proportional navigation controller controls the agent, such that the
// normal acceleration vector is proportional to the rate of change of the
// bearing.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/controller/agent_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::controller {

// Proportional navigation controller.
class PnController : public AgentController {
 public:
  // Proportional navigation gain.
  inline static const double kProportionalNavigationGain = 3;

  PnController(const agent::Agent& agent) : AgentController(agent) {}

  PnController(PnController&) = default;
  PnController& operator=(PnController&) = default;

 protected:
  // Plan the next optimal control(s).
  void PlanImpl(const SensorOutput& sensor_output) override;
};

}  // namespace swarm::controller
