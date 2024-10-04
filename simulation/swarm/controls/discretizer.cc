#include "simulation/swarm/controls/discretizer.h"

#include <Eigen/Dense>
#include <utility>

namespace swarm::controls {

std::pair<Eigen::MatrixXd, Eigen::MatrixXd> ForwardEulerDiscretizer::Discretize(
    const double sampling_time) const {
  auto A_d =
      Eigen::MatrixXd::Identity(A_.rows(), A_.cols()) + A_ * sampling_time;
  auto B_d = B_ * sampling_time;
  return std::make_tuple(std::move(A_d), std::move(B_d));
}

std::pair<Eigen::MatrixXd, Eigen::MatrixXd>
BackwardEulerDiscretizer::Discretize(const double sampling_time) const {
  auto A_d =
      (Eigen::MatrixXd::Identity(A_.rows(), A_.cols()) - A_ * sampling_time)
          .inverse();
  auto B_d = sampling_time * A_d * B_;
  return std::make_tuple(std::move(A_d), std::move(B_d));
}

std::pair<Eigen::MatrixXd, Eigen::MatrixXd> TrapezoidalDiscretizer::Discretize(
    const double sampling_time) const {
  auto A_temp =
      (Eigen::MatrixXd::Identity(A_.rows(), A_.cols()) - A_ * sampling_time / 2)
          .inverse();
  auto A_d = A_temp * (Eigen::MatrixXd::Identity(A_.rows(), A_.cols()) +
                       A_ * sampling_time / 2);
  auto B_d = sampling_time * A_temp * B_;
  return std::make_tuple(std::move(A_d), std::move(B_d));
}

}  // namespace swarm::controls
