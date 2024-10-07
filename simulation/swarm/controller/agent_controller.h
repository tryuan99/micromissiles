// The agent controller is the interface between the agent and its control law.

#pragma once

#include <Eigen/Dense>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/sensor/ideal_sensor.h"

namespace swarm::controller {

// Agent controller interface.
class AgentController {
 public:
  AgentController(const agent::Agent& agent, const agent::Agent& target)
      : agent_(&agent), target_(&target), sensor_(sensor::IdealSensor(agent)) {}

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
  virtual void PlanImpl(const SensorOutput& sensor_output) = 0;

  // Agent to be controlled.
  const agent::Agent* agent_ = nullptr;

  // Target assigned to the agent.
  const agent::Agent* target_ = nullptr;

  // Optimal control.
  Eigen::Vector3d acceleration_input_;

 private:
  // Ideal sensor to sense the target.
  sensor::IdealSensor sensor_;
};

}  // namespace swarm::controller
