#include <Eigen/Dense>

#include "base/base.h"
#include "mpc/NLMPC.hpp"

namespace {
// Number of state variables.
constexpr int kNumStateVariables = 7;

// Number of input variables.
constexpr int kNumInputVariables = 3;

// Prediction horizon in number of time steps.
constexpr int kPredictionHorizon = 10;

// Control horizon in number of time steps.
constexpr int kControlHorizon = 10;

// Sampling time in seconds.
constexpr double kSamplingTime = 0.01;  // seconds

// Number of inequality constraints.
constexpr int kNumInequalityConstraints = 2 * (kPredictionHorizon + 1);

// Number of equality constraints.
constexpr int kNumEqualityConstraints = 0;

// Tolerance.
constexpr double kTolerance = 0.01;

// Type aliases.
using StateVector = Eigen::Vector<double, kNumStateVariables>;
using StateMatrix =
    Eigen::Matrix<double, kNumStateVariables, kNumStateVariables>;
using InputVector = Eigen::Vector<double, kNumInputVariables>;
}  // namespace

int main(int argc, char** argv) {
  base::Init(argc, argv);

  // Initialize the nonlinear model-predictive control controller.
  mpc::NLMPC<kNumStateVariables, kNumInputVariables, kNumStateVariables,
             kPredictionHorizon, kControlHorizon, kNumInequalityConstraints,
             kNumEqualityConstraints>
      controller;
  controller.setLoggerLevel(mpc::Logger::LogLevel::NORMAL);

  mpc::NLParameters params;
  params.relative_ftol = kTolerance;
  params.relative_xtol = kTolerance;
  params.absolute_ftol = kTolerance;
  params.absolute_xtol = kTolerance;
  params.maximum_iteration = 10000;
  controller.setOptimizerParameters(params);

  // Define the state equation.
  controller.setStateSpaceFunction(
      [&](StateVector& x_next, const StateVector& x, const InputVector& u,
          const unsigned int& time_step) {
        // Define the state vector at the next time step.
        StateVector x_delta;
        x_delta.head(3) = x.segment(3, 3);
        x_delta.segment(3, 3) = u;
        x_delta(6) = u.norm();
        x_next = x + kSamplingTime * x_delta;
      });

  // Define the objective function.
  controller.setObjectiveFunction(
      [&](const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& x,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& y,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumInputVariables>& u,
          const double& slack) {
        return (x.row(x.rows() - 1).array() *
                StateVector{0, 0, 0, 0, 0, 0, 1}.transpose().array())
            .square()
            .sum();
      });

  // Define the inequality constraints.
  controller.setIneqConFunction(
      [&](Eigen::Vector<double, kNumInequalityConstraints>& inequalities,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& x,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& y,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumInputVariables>& u,
          const double& slack) {
        for (int i = 0; i < kNumInequalityConstraints / 2; ++i) {
          inequalities(2 * i) = u.row(i).norm() - 1;
          inequalities(2 * i + 1) = 1 - u.row(i)(0) - kTolerance;
        }
      });

  // Define the initial state vector.
  const StateVector initial_state{10, 10, 10, 1, 2, 2, 0};

  // Run the optimizer.
  mpc::Result<kNumInputVariables> result =
      controller.optimize(initial_state, InputVector::Zero());
  LOG(INFO) << "Optimal input: " << result.cmd;
  LOG(INFO) << "Feasible: " << result.is_feasible;
  LOG(INFO) << "Status: " << result.status;
}
