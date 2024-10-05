// The model-predictive controller performs trajectory optimization with a
// linearized, receding finite horizon LQR as a feedback policy.

#pragma once

#include <Eigen/Dense>

#include "simulation/swarm/controls/controller.h"
#include "simulation/swarm/controls/solver/finite_horizon_discrete_time_lqr_solver.h"

namespace swarm::controls {

// Model-predictive controller.
class MpcController : public Controller {
 public:
  MpcController(Eigen::MatrixXd A, Eigen::MatrixXd B, double sampling_time,
                Eigen::MatrixXd Q, Eigen::MatrixXd R, Eigen::MatrixXd Qf,
                int horizon);

  MpcController(const MpcController&) = default;
  MpcController& operator=(const MpcController&) = default;

  // Plan the next optimal control(s).
  void Plan(const Eigen::MatrixXd& initial_state) override;

  // Get the optimal control.
  Eigen::MatrixXd GetOptimalControl(
      const Eigen::MatrixXd& input_bias_point) const override;

 private:
  // Finite-horizon, discrete-time LQR solver.
  solver::FiniteHorizonDiscreteTimeLqrSolver lqr_solver_;

  // Optimal control.
  Eigen::MatrixXd optimal_control_;
};

}  // namespace swarm::controls
