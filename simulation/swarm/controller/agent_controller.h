// The agent controller is the interface between the agent and its control law.

#pragma once

#include <Eigen/Dense>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/transformation.pb.h"

namespace swarm::controller {

// Agent controller interface.
class AgentController {
 public:
  AgentController(const agent::Agent& agent) : agent_(&agent) {}

  AgentController(AgentController&) = default;
  AgentController& operator=(AgentController&) = default;

  virtual ~AgentController() = default;

  // Plan the next optimal control(s).
  void Plan();

  // Get the optimal control.
  const Eigen::Vector3d& GetOptimalControl() const {
    return acceleration_input_;
  };

 protected:
  // Plan the next optimal control(s).
  virtual void PlanImpl(const Transformation& relative_transformation) = 0;

  // Agent to be controlled.
  const agent::Agent* agent_ = nullptr;

  // Optimal control.
  Eigen::Vector3d acceleration_input_;
};

}  // namespace swarm::controller
