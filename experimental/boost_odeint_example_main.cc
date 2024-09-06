#include <Eigen/Dense>
#include <boost/numeric/odeint.hpp>
#include <boost/numeric/odeint/external/eigen/eigen.hpp>
#include <cmath>
#include <cstdlib>
#include <numbers>

#include "base/base.h"

// Gravity acceleration in m/s^2.
constexpr double kGravity = 9.81;

// Length of the pendulum in m.
// Set the pendulum length, so that the oscillation period is 1 s.
constexpr double kPendulumLength =
    1 / (4 * std::numbers::pi * std::numbers::pi) * kGravity;

int main(int argc, char** argv) {
  base::Init(argc, argv);

  // Integrate a state-space representation of a system.
  // For a pendulum, let the state vector consist of the angular position and
  // the angular velocity, i.e., x1 = theta, x2 = theta_dot.
  // The state-space representation is as follows:
  //  x1_dot = x2
  //  x2_dot = -g/l * sin(x1)

  // Define the initial conditions.
  Eigen::Vector2d x{1, 0};

  // Define the state-space equations.
  const auto pendulum = [&](const Eigen::Vector2d& x, Eigen::Vector2d& x_dot,
                            const double t) {
    x_dot(0) = x(1);
    x_dot(1) = -kGravity / kPendulumLength * std::sin(x(0));
  };

  // Define the observer function for each time step.
  const auto observer = [&](const Eigen::Vector2d& x, const double t) {
    LOG(INFO) << "Time = " << t << ": " << x;
  };

  // Integrate the state-space equations.
  boost::numeric::odeint::integrate(pendulum, x, /*start_time=*/0.0,
                                    /*end_time=*/2.0, /*dt=*/0.2, observer);
  return EXIT_SUCCESS;
}
