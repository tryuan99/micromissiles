// The model-predictive control controller controls the agent by optimizing the
// trajectory with a linearized, receding finite horizon LQR as a feedback
// policy.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/controller/agent_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::controller {

// Model-predictive control controller.
class MpcController : public AgentController {
 public:
  // Type aliases.
  using Vector6d = Eigen::Vector<double, 6>;
  using Matrix6d = Eigen::Matrix<double, 6, 6>;

  // Position cost factor.
  inline static const double kPositionCostFactor = 2;

  // Input cost factor.
  inline static const double kInputCostFactor = 1;

  // Sampling time in seconds for the LQR solver.
  inline static const double kLqrSamplingTime = 0.01;

  // LQR horizon in number of time steps.
  inline static const int kLqrHorizon = 100;

  MpcController(const agent::Agent& agent) : AgentController(agent) {}

  MpcController(MpcController&) = default;
  MpcController& operator=(MpcController&) = default;

 protected:
  // Plan the next optimal control(s).
  void PlanImpl(const SensorOutput& sensor_output) override;
};

}  // namespace swarm::controller
