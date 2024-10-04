// The finite-horizon, discrete-time LQR solver finds the optimal controls at
// every time step to minimize the overall cost.
//
// The system is given by x[k + 1] = Ax[k] + Bu[k].
// The objective function is given by: \min_u \sum_{k = 0}^{N - 1} (x[k]^TQx[k]
// + u[k]^TRu[k]) + x[N]^TQfx[N].

#pragma once

#include <Eigen/Dense>
#include <vector>

#include "simulation/swarm/controls/solver/lqr_solver.h"

namespace swarm::controls::solver {

// Finite-horizon, discrete-time LQR solver.
class FiniteHorizonDiscreteTimeLqrSolver : public DiscreteTimeLqrSolver {
 public:
  FiniteHorizonDiscreteTimeLqrSolver(Eigen::MatrixXd A, Eigen::MatrixXd B,
                                     Eigen::MatrixXd Q, Eigen::MatrixXd R,
                                     Eigen::MatrixXd Qf, const int N)
      : DiscreteTimeLqrSolver(std::move(A), std::move(B), std::move(Q),
                              std::move(R), std::move(Qf)),
        N_(N) {}

  FiniteHorizonDiscreteTimeLqrSolver(
      const FiniteHorizonDiscreteTimeLqrSolver&) = default;
  FiniteHorizonDiscreteTimeLqrSolver& operator=(
      const FiniteHorizonDiscreteTimeLqrSolver&) = default;

  // Solve for the optimal feedback matrix.
  void Solve();

  // Get the feedback matrix K at the given time step.
  Eigen::MatrixXd GetFeedbackMatrix(int time_step) const;

  // Get the cost-to-go matrix P at the given time step.
  Eigen::MatrixXd GetCostToGoMatrix(int time_step) const;

 private:
  // Number of time steps in the horizon.
  int N_;

  // List of cost-to-go matrices. P_{k + 1} is stored at index k.
  std::vector<Eigen::MatrixXd> Ps_;
};

}  // namespace swarm::controls::solver
