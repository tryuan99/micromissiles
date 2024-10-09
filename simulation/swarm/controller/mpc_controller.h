// The model-predictive control controller controls the agent by optimizing the
// trajectory over a receding finite horizon with nonlinear system dynamics.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/controller/agent_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::controller {

// Model-predictive control controller.
class MpcController : public AgentController {
 public:
  MpcController(const agent::Agent& agent) : AgentController(agent) {}

  MpcController(MpcController&) = default;
  MpcController& operator=(MpcController&) = default;

 protected:
  // Plan the next optimal control(s).
  void PlanImpl(const SensorOutput& sensor_output) override;
};

}  // namespace swarm::controller
