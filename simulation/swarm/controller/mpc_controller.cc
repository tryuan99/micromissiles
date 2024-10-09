#include "simulation/swarm/controller/mpc_controller.h"

#include <Eigen/Dense>

#include "mpc/NLMPC.hpp"
#include "simulation/swarm/controls/mpc_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/utils/constants.h"

namespace swarm::controller {

namespace {
// Number of state variables.
constexpr int kNumStateVariables = 7;

// Number of input variables.
constexpr int kNumInputVariables = 3;

// Position cost factor.
constexpr double kPositionCostFactor = 2;

// Prediction horizon in number of time steps.
constexpr int kPredictionHorizon = 10;

// Control horizon in number of time steps.
constexpr int kControlHorizon = 5;

// Sampling time in seconds.
constexpr double kSamplingTime = 0.01;  // seconds

// Number of inequality constraints.
constexpr int kNumInequalityConstraints = kPredictionHorizon + 1;

// Number of equality constraints.
constexpr int kNumEqualityConstraints = kPredictionHorizon + 1;

// Type aliases.
using StateVector = Eigen::Vector<double, kNumStateVariables>;
using StateMatrix =
    Eigen::Matrix<double, kNumStateVariables, kNumStateVariables>;
using InputVector = Eigen::Vector<double, kNumInputVariables>;
}  // namespace

void MpcController::PlanImpl(const SensorOutput& sensor_output) {
  // Initialize the nonlinear model-predictive control controller.
  mpc::NLMPC<kNumStateVariables, kNumInputVariables, kNumStateVariables,
             kPredictionHorizon, kControlHorizon, kNumInequalityConstraints,
             kNumEqualityConstraints>
      controller;
  controller.setDiscretizationSamplingTime(kSamplingTime);

  mpc::NLParameters params;
  params.maximum_iteration = 1000;
  controller.setOptimizerParameters(params);

  // Define the state equation.
  controller.setStateSpaceFunction([&](StateVector& dx, const StateVector& x,
                                       const InputVector& u,
                                       const unsigned int& time_step) {
    // Define helper variables.
    const auto position = agent_->GetPosition();
    const auto velocity = x.segment(3, 3);
    const auto g = constants::CalculateGravityAtAltitude(position(2));
    const auto rho = constants::CalculateAirDensityAtAltitude(position(2));

    // Calculate the drag acceleration.
    const auto air_drag_acceleration =
        rho * agent_->static_config().lift_drag_config().drag_coefficient() *
        agent_->static_config().body_config().cross_sectional_area() /
        (2 * agent_->static_config().body_config().mass()) *
        std::pow(velocity.norm(), 2);
    const auto lift_induced_drag_acceleration =
        (u + Eigen::Vector3d{0, 0, g}).norm() /
        agent_->static_config().lift_drag_config().lift_drag_ratio();
    const auto drag_acceleration =
        air_drag_acceleration + lift_induced_drag_acceleration;

    // Define the dx/dt vector.
    dx.head(3) = x.segment(3, 3);
    dx.segment(3, 3) = u - Eigen::Vector3d{0, 0, g} -
                       drag_acceleration * velocity / velocity.norm();
    dx(6) = drag_acceleration;
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
        return std::sqrt(
            (x.row(x.rows() - 1).array() *
             StateVector{std::sqrt(kPositionCostFactor),
                         std::sqrt(kPositionCostFactor),
                         std::sqrt(kPositionCostFactor), 0, 0, 0, 1}
                 .transpose()
                 .array())
                .matrix()
                .norm());
      });

  // Define the maximum acceleration inequality constraints.
  controller.setIneqConFunction(
      [&](Eigen::Vector<double, kNumInequalityConstraints>& inequalities,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& x,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& y,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumInputVariables>& u,
          const double& slack) {
        for (int i = 0; i < kNumInequalityConstraints; ++i) {
          inequalities(i) =
              u.row(i).norm() - std::pow(x.row(i).segment(3, 3).norm() /
                                             agent_->static_config()
                                                 .acceleration_config()
                                                 .reference_speed(),
                                         2) *
                                    agent_->static_config()
                                        .acceleration_config()
                                        .max_reference_acceleration();
        }
      });

  // Define the normal acceleration equality constraints.
  controller.setEqConFunction(
      [&](Eigen::Vector<double, kNumEqualityConstraints>& equalities,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumStateVariables>& x,
          const Eigen::Matrix<double, kPredictionHorizon + 1,
                              kNumInputVariables>& u) {
        for (int i = 0; i < kNumEqualityConstraints; ++i) {
          equalities(i) = u.row(i).dot(x.row(i).segment(3, 3));
        }
      });

  // Define the initial state vector.
  const auto velocity = agent_->GetVelocity();
  const auto normalized_velocity = velocity.normalized();
  const StateVector initial_state{sensor_output.position_cartesian().x(),
                                  sensor_output.position_cartesian().y(),
                                  sensor_output.position_cartesian().z(),
                                  velocity(0),
                                  velocity(1),
                                  velocity(2),
                                  0};

  // Run the optimizer.
  mpc::Result<kNumInputVariables> result =
      controller.optimize(initial_state, InputVector::Zero());
  const Eigen::Vector3d& acceleration_input = result.cmd;

  // Extract the normal acceleration input only.
  acceleration_input_ =
      acceleration_input -
      acceleration_input.dot(normalized_velocity) * normalized_velocity;
}

}  // namespace swarm::controller
