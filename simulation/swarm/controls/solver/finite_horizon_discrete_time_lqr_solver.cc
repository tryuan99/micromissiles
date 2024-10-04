#include "simulation/swarm/controls/solver/finite_horizon_discrete_time_lqr_solver.h"

#include <Eigen/Dense>

namespace swarm::controls::solver {

void FiniteHorizonDiscreteTimeLqrSolver::Solve() {
  Ps_.resize(N_ + 1);
  Ps_[N_] = Qf_;
  for (int k = N_ - 1; k >= 0; --k) {
    const auto& P_kplus1 = Ps_[k + 1];
    Ps_[k] = Q_ + A_.transpose() * P_kplus1 * A_ -
             A_.transpose() * P_kplus1 * B_ *
                 (R_ + B_.transpose() * P_kplus1 * B_).inverse() *
                 B_.transpose() * P_kplus1 * A_;
  }
}

Eigen::MatrixXd FiniteHorizonDiscreteTimeLqrSolver::GetFeedbackMatrix(
    const int time_step) const {
  const auto& P_kplus1 = Ps_[time_step + 1];
  return (R_ + B_.transpose() * P_kplus1 * B_).inverse() * B_.transpose() *
         P_kplus1 * A_;
}

Eigen::MatrixXd FiniteHorizonDiscreteTimeLqrSolver::GetCostToGoMatrix(
    const int time_step) const {
  return Ps_[time_step];
}

}  // namespace swarm::controls::solver
