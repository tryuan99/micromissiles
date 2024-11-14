#include "simulation/swarm/controller/mpc_controller.h"

#include <Eigen/Dense>

#include "base/commandlineflags.h"
#include "base/logging.h"
#include "mpc/NLMPC.hpp"
#include "simulation/swarm/controls/mpc_controller.h"
#include "simulation/swarm/proto/transformation.pb.h"
#include "simulation/swarm/utils/constants.h"

DEFINE_bool(log_mpc, false,
            "If true, log verbose messages for the MPC controller.");

namespace swarm::controller {

namespace {
// Number of state variables.
constexpr int kNumStateVariables = 7;

// Number of input variables.
constexpr int kNumInputVariables = 2;

// Position cost factor.
constexpr double kPositionCostFactor = 0;

// Lost speed cost factor.
constexpr double kLostSpeedCostFactor = 1;

// Prediction horizon in number of time steps.
constexpr int kPredictionHorizon = 5;

// Control horizon in number of time steps.
constexpr int kControlHorizon = 5;

// Sampling time in seconds.
constexpr double kSamplingTime = 0.01;  // seconds

// Number of inequality constraints.
constexpr int kNumInequalityConstraints = kPredictionHorizon + 1;

// Number of equality constraints.
constexpr int kNumEqualityConstraints = 0;

// Tolerance.
constexpr double kTolerance = 0.01;

// Type aliases.
using StateVector = Eigen::Vector<double, kNumStateVariables>;
using StateMatrix =
    Eigen::Matrix<double, kNumStateVariables, kNumStateVariables>;
using InputVector = Eigen::Vector<double, kNumInputVariables>;

// Calculate the normal vectors.
Eigen::Matrix<double, 3, 2> CalculateNormalVectors(const Eigen::Vector3d& u) {
  Eigen::Matrix<double, 3, 2> normal_vectors;
  normal_vectors.col(0) = Eigen::Vector3d{0, 0, 1}.cross(u).normalized();
  normal_vectors.col(1) = normal_vectors.col(0).cross(u).normalized();
  return normal_vectors;
}
}  // namespace

void MpcController::PlanImpl(const Transformation& relative_transformation) {
  // Initialize the nonlinear model-predictive control controller.
  mpc::NLMPC<kNumStateVariables, kNumInputVariables, kNumStateVariables,
             kPredictionHorizon, kControlHorizon, kNumInequalityConstraints,
             kNumEqualityConstraints>
      controller;
  controller.setLoggerLevel(FLAGS(log_mpc) ? mpc::Logger::log_level::NORMAL
                                           : mpc::Logger::log_level::ALERT);

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
        // Define helper variables.
        // Assume that the altitude does not change by much during the planning
        // horizon, so use the initial altitude to calculate the gravity and air
        // density for the entire horizon.
        const auto position = agent_->GetPosition();
        const auto altitude = position(2);
        const auto gravity = constants::CalculateGravityAtAltitude(altitude);
        const auto air_density =
            constants::CalculateAirDensityAtAltitude(altitude);

        const auto velocity = x.segment(3, 3);
        const auto normal_vectors = CalculateNormalVectors(velocity);

        // Calculate the drag acceleration.
        const auto air_drag_acceleration =
            air_density *
            agent_->static_config().lift_drag_config().drag_coefficient() *
            agent_->static_config().body_config().cross_sectional_area() /
            (2 * agent_->static_config().body_config().mass()) *
            std::pow(velocity.norm(), 2);
        const auto input_acceleration =
            normal_vectors * u - Eigen::Vector3d{0, 0, gravity};
        const auto lift_induced_drag_acceleration =
            (input_acceleration - input_acceleration.dot(velocity) /
                                      std::pow(velocity.norm(), 2) * velocity)
                .norm() /
            agent_->static_config().lift_drag_config().lift_drag_ratio();
        const auto drag_acceleration =
            air_drag_acceleration + lift_induced_drag_acceleration;

        // Define the state vector at the next time step.
        StateVector x_delta;
        // The distance to target changes with the agent's velocity and the
        // target's velocity.
        x_delta.head(3) = velocity - agent_->target_model().GetVelocity();
        x_delta.segment(3, 3) = normal_vectors * u -
                                Eigen::Vector3d{0, 0, gravity} -
                                drag_acceleration * velocity / velocity.norm();
        x_delta(6) = drag_acceleration;
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
        // TODO(titan): Figure out why the distance to target cost must be
        // negative for the correct behavior to emerge. The speed cost remains
        // positive.
        return -(x.row(x.rows() - 1).array() *
                 StateVector{std::sqrt(kPositionCostFactor),
                             std::sqrt(kPositionCostFactor),
                             std::sqrt(kPositionCostFactor), 0, 0, 0, 0}
                     .transpose()
                     .array())
                    .square()
                    .sum() +
               kLostSpeedCostFactor *
                   std::pow(x.coeff(x.rows() - 1, kNumStateVariables - 1), 2);
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

  // Define the initial state vector.
  const auto velocity = agent_->GetVelocity();
  const StateVector initial_state{
      relative_transformation.position_cartesian().x(),
      relative_transformation.position_cartesian().y(),
      relative_transformation.position_cartesian().z(),
      velocity(0),
      velocity(1),
      velocity(2),
      0};

  // Run the optimizer.
  const auto normal_vectors = CalculateNormalVectors(velocity);
  mpc::Result<kNumInputVariables> result =
      controller.optimize(initial_state, InputVector::Zero());
  const Eigen::Vector3d acceleration_input = normal_vectors * result.cmd;
  LOG_IF(INFO, FLAGS(log_mpc)) << "Optimal input: " << acceleration_input;
  LOG_IF(INFO, FLAGS(log_mpc))
      << "Feasible: " << result.is_feasible << ", status: " << result.status;

  // Extract the normal acceleration input only.
  const auto normalized_velocity = velocity.normalized();
  acceleration_input_ =
      acceleration_input -
      acceleration_input.dot(normalized_velocity) * normalized_velocity;
}

}  // namespace swarm::controller
