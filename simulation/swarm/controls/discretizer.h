// The discretizer discretizes the continuous-time linear system and returns the
// discretized A and B matrices.

#pragma once

#include <Eigen/Dense>
#include <utility>

namespace swarm::controls {

// Discretizer interface.
class Discretizer {
 public:
  Discretizer(Eigen::MatrixXd A, Eigen::MatrixXd B)
      : A_(std::move(A)), B_(std::move(B)) {}

  Discretizer(const Discretizer&) = default;
  Discretizer& operator=(const Discretizer&) = default;

  virtual ~Discretizer() = default;

  // Discretize the system with the given sampling period.
  virtual std::pair<Eigen::MatrixXd, Eigen::MatrixXd> Discretize(
      double sampling_time) const = 0;

 protected:
  // Continuous-time A matrix.
  Eigen::MatrixXd A_;

  // Continuous-time B matrix.
  Eigen::MatrixXd B_;
};

// Forward-Euler discretizer.
// A_d = I + A*T
// B_d = B*T
class ForwardEulerDiscretizer : public Discretizer {
 public:
  ForwardEulerDiscretizer(Eigen::MatrixXd A, Eigen::MatrixXd B)
      : Discretizer(std::move(A), std::move(B)) {}

  ForwardEulerDiscretizer(const ForwardEulerDiscretizer&) = default;
  ForwardEulerDiscretizer& operator=(const ForwardEulerDiscretizer&) = default;

  // Discretize the system with the given sampling period.
  std::pair<Eigen::MatrixXd, Eigen::MatrixXd> Discretize(
      double sampling_time) const override;
};

// Backward-Euler discretizer.
// A_d = (I - A*T)^-1
// B_d = T * (I - A*T)^-1 * B
class BackwardEulerDiscretizer : public Discretizer {
 public:
  BackwardEulerDiscretizer(Eigen::MatrixXd A, Eigen::MatrixXd B)
      : Discretizer(std::move(A), std::move(B)) {}

  BackwardEulerDiscretizer(const BackwardEulerDiscretizer&) = default;
  BackwardEulerDiscretizer& operator=(const BackwardEulerDiscretizer&) =
      default;

  // Discretize the system with the given sampling period.
  std::pair<Eigen::MatrixXd, Eigen::MatrixXd> Discretize(
      double sampling_time) const override;
};

// Trapezoidal discretizer.
// A_d = (I - 1/2*A*T)^-1 * (I + 1/2*A*T)
// B_d = T * (I - 1/2*A*T)^-1 * B
class TrapezoidalDiscretizer : public Discretizer {
 public:
  TrapezoidalDiscretizer(Eigen::MatrixXd A, Eigen::MatrixXd B)
      : Discretizer(std::move(A), std::move(B)) {}

  TrapezoidalDiscretizer(const TrapezoidalDiscretizer&) = default;
  TrapezoidalDiscretizer& operator=(const TrapezoidalDiscretizer&) = default;

  // Discretize the system with the given sampling period.
  std::pair<Eigen::MatrixXd, Eigen::MatrixXd> Discretize(
      double sampling_time) const override;
};

}  // namespace swarm::controls
