#include "simulation/swarm/controls/mpc_controller.h"

#include <Eigen/Dense>

#include "simulation/swarm/controls/discretizer.h"
#include "simulation/swarm/controls/solver/finite_horizon_discrete_time_lqr_solver.h"

namespace swarm::controls {

MpcController::MpcController(Eigen::MatrixXd A, Eigen::MatrixXd B,
                             const double sampling_time, Eigen::MatrixXd Q,
                             Eigen::MatrixXd R, Eigen::MatrixXd Qf,
                             const int horizon) {
  // Discretize the continuous-time system.
  TrapezoidalDiscretizer discretizer(std::move(A), std::move(B));
  auto discretized_system = discretizer.Discretize(sampling_time);

  // Initialize the LQR solver.
  lqr_solver_ = solver::FiniteHorizonDiscreteTimeLqrSolver(
      std::move(discretized_system.first), std::move(discretized_system.second),
      std::move(Q), std::move(R), std::move(Qf), horizon);
}

void MpcController::Plan(const Eigen::MatrixXd& initial_state) {
  lqr_solver_.Solve();
  optimal_control_ =
      -lqr_solver_.GetFeedbackMatrix(/*time_step=*/0) * initial_state;
}

Eigen::MatrixXd MpcController::GetOptimalControl(
    const Eigen::MatrixXd& input_bias_point) const {
  return optimal_control_ + input_bias_point;
}

}  // namespace swarm::controls
