// The controller is an interface for determining the controls for the next time
// step given the current agent state and the target state.

#pragma once

#include <Eigen/Dense>

namespace swarm::controls {

// Controller interface.
class Controller {
 public:
  Controller() = default;

  Controller(const Controller&) = default;
  Controller& operator=(const Controller&) = default;

  virtual ~Controller() = default;

  // Plan the next optimal control(s).
  virtual void Plan(const Eigen::MatrixXd& initial_state) = 0;

  // Get the optimal control.
  virtual Eigen::MatrixXd GetOptimalControl(
      const Eigen::MatrixXd& input_bias_point) const = 0;
};

}  // namespace swarm::controls
