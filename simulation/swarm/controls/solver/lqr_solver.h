// The LQR solver is an interface for finite-horizon or infinite-horizon and
// discrete-time or continuous-time LQR solvers.
//
// The system is given by dx/dt = Ax + Bu or x[k + 1] = Ax[k] + Bu[k].
// The objective function is given by:
//  - \min_u \sum_{k = 0}^{N - 1} (x[k]^TQx[k] + u[k]^TRu[k]) + x[N]^TQfx[N].
//  - \min_u \sum_{k = 0}^{\infty} (x[k]^TQx[k] + u[k]^TRu[k]).
//  - \min_u \int_0^T (x(t)^TQx(t) + u(t)^TRu(t)) + x(T)^TQfx(T).
//  - \min_u \int_0^\infty (x(t)^TQx(t) + u(t)^TRu(t)).

#pragma once

#include <Eigen/Dense>

namespace swarm::controls::solver {

// LQR solver interface.
class LqrSolver {
 public:
  LqrSolver() = default;
  LqrSolver(Eigen::MatrixXd A, Eigen::MatrixXd B, Eigen::MatrixXd Q,
            Eigen::MatrixXd R)
      : LqrSolver(std::move(A), std::move(B), std::move(Q), std::move(R),
                  Eigen::MatrixXd::Zero(Q.rows(), Q.cols())) {}
  LqrSolver(Eigen::MatrixXd A, Eigen::MatrixXd B, Eigen::MatrixXd Q,
            Eigen::MatrixXd R, Eigen::MatrixXd Qf)
      : A_(std::move(A)),
        B_(std::move(B)),
        Q_(std::move(Q)),
        R_(std::move(R)),
        Qf_(std::move(Qf)) {}

  LqrSolver(const LqrSolver&) = default;
  LqrSolver& operator=(const LqrSolver&) = default;

  virtual ~LqrSolver() = default;

  // Solve for the optimal feedback matrix.
  virtual void Solve() = 0;

  // Get the feedback matrix K at the given time step.
  // The feedback control is given by u = -K * x.
  virtual Eigen::MatrixXd GetFeedbackMatrix(int time_step) const = 0;

  // Get the cost-to-go matrix P at the given time step.
  virtual Eigen::MatrixXd GetCostToGoMatrix(int time_step) const = 0;

 protected:
  // A matrix of the system.
  Eigen::MatrixXd A_;

  // B matrix of the system.
  Eigen::MatrixXd B_;

  // State cost matrix.
  Eigen::MatrixXd Q_;

  // Control cost matrix.
  Eigen::MatrixXd R_;

  // Terminal cost matrix.
  Eigen::MatrixXd Qf_;
};

// Discrete-time LQR solver.
class DiscreteTimeLqrSolver : public LqrSolver {
 public:
  DiscreteTimeLqrSolver() = default;
  DiscreteTimeLqrSolver(Eigen::MatrixXd A, Eigen::MatrixXd B, Eigen::MatrixXd Q,
                        Eigen::MatrixXd R, Eigen::MatrixXd Qf)
      : LqrSolver(std::move(A), std::move(B), std::move(Q), std::move(R)),
        Qf_(std::move(Qf)) {}

  DiscreteTimeLqrSolver(const DiscreteTimeLqrSolver&) = default;
  DiscreteTimeLqrSolver& operator=(const DiscreteTimeLqrSolver&) = default;

  virtual ~DiscreteTimeLqrSolver() = default;

 protected:
  // Terminal cost matrix.
  Eigen::MatrixXd Qf_;
};

// Continuous-time LQR solver.
class ContinuousTimeLqrSolver : public LqrSolver {
 public:
  ContinuousTimeLqrSolver() = default;
  ContinuousTimeLqrSolver(Eigen::MatrixXd A, Eigen::MatrixXd B,
                          Eigen::MatrixXd Q, Eigen::MatrixXd R)
      : LqrSolver(std::move(A), std::move(B), std::move(Q), std::move(R)) {}

  ContinuousTimeLqrSolver(const ContinuousTimeLqrSolver&) = default;
  ContinuousTimeLqrSolver& operator=(const ContinuousTimeLqrSolver&) = default;

  virtual ~ContinuousTimeLqrSolver() = default;
};

}  // namespace swarm::controls::solver
