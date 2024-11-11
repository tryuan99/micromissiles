// The augmented proportional navigation controller controls the agent, such
// that the normal acceleration vector consists of a term proportional to the
// rate of change of the bearing and a feedforward term proportional to the
// target's acceleration.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/controller/pn_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::controller {

// Augmented proportional navigation controller.
class ApnController : public PnController {
 public:
  ApnController(const agent::Agent& agent) : PnController(agent) {}

  ApnController(ApnController&) = default;
  ApnController& operator=(ApnController&) = default;

 protected:
  // Plan the next optimal control(s).
  void PlanImpl(const SensorOutput& sensor_output) override;
};

}  // namespace swarm::controller
