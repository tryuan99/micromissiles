#include "simulation/swarm/controller/mpc_controller.h"

#include <Eigen/Dense>

#include "simulation/swarm/controls/mpc_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/utils/constants.h"

namespace swarm::controller {

void MpcController::PlanImpl(const SensorOutput& sensor_output) {
  // Define helper variables.
  const auto position = agent_->GetPosition();
  const auto velocity = agent_->GetVelocity();
  const auto normalized_velocity = velocity.normalized();
  const auto acceleration = agent_->GetAcceleration();

  const auto g = constants::CalculateGravityAtAltitude(position(2));
  const auto temp = std::sqrt(std::pow(acceleration.norm(), 2) +
                              2 * g * acceleration(2) + std::pow(g, 2) -
                              std::pow(acceleration.dot(normalized_velocity) +
                                           g * normalized_velocity(2),
                                       2));

  // Define the initial state vector.
  Vector6d initial_state{sensor_output.position_cartesian().x(),
                         sensor_output.position_cartesian().y(),
                         sensor_output.position_cartesian().z(),
                         velocity(0),
                         velocity(1),
                         velocity(2)};

  // Define the A matrix.
  Matrix6d A = Matrix6d::Zero();
  A.block(0, 3, 3, 3) = Eigen::Matrix3d::Identity();
  auto df_over_dv =
      -(normalized_velocity.dot(acceleration) * Eigen::Matrix3d::Identity() +
        normalized_velocity * acceleration.transpose() -
        2 * normalized_velocity.dot(acceleration) * normalized_velocity *
            normalized_velocity.transpose()) /
          velocity.norm() -
      constants::CalculateAirDensityAtAltitude(position(2)) *
          agent_->static_config().lift_drag_config().drag_coefficient() *
          agent_->static_config().body_config().cross_sectional_area() /
          (2 * agent_->static_config().body_config().mass()) * velocity.norm() *
          (Eigen::Matrix3d::Identity() +
           normalized_velocity * normalized_velocity.transpose()) +
      temp * (Eigen::Matrix3d::Identity() -
              normalized_velocity * normalized_velocity.transpose()) +
      (-(acceleration.dot(normalized_velocity) + g * normalized_velocity(2)) *
           (acceleration + Eigen::Vector3d{0, 0, g}) +
       std::pow(
           (acceleration.dot(normalized_velocity) + g * normalized_velocity(2)),
           2) *
           normalized_velocity) *
          normalized_velocity.transpose() /
          (velocity.norm() *
           agent_->static_config().lift_drag_config().lift_drag_ratio() * temp);
  A.block(3, 3, 3, 3) = df_over_dv;

  // Define the B matrix.
  Eigen::Matrix<double, 6, 3> B = Eigen::Matrix<double, 6, 3>::Zero();
  auto df_over_da =
      Eigen::Matrix3d::Identity() -
      normalized_velocity * normalized_velocity.transpose() +
      normalized_velocity *
          (acceleration.transpose() + Eigen::RowVector3d{0, 0, g} -
           (acceleration.dot(normalized_velocity) +
            g * normalized_velocity(2)) *
               normalized_velocity.transpose()) /
          (agent_->static_config().lift_drag_config().lift_drag_ratio() * temp);
  B.block(3, 0, 3, 3) = df_over_da;

  // Define the LQR cost matrices.
  const auto Q = Matrix6d::Zero();
  const auto R = kInputCostFactor * Eigen::Matrix3d::Identity();
  Matrix6d Qf = Matrix6d::Identity();
  Qf.block(0, 0, 3, 3) *= kPositionCostFactor;
  Qf.block(3, 3, 3, 3) *= -1;

  // Run the LQR solver.
  controls::MpcController controller(A, B, kLqrSamplingTime, Q, R, Qf,
                                     kLqrHorizon);
  controller.Plan(initial_state);
  const Eigen::Vector3d& acceleration_input =
      controller.GetOptimalControl(acceleration);

  // Extract the normal acceleration input only.
  acceleration_input_ =
      acceleration_input -
      acceleration_input.dot(normalized_velocity) * normalized_velocity;
}

}  // namespace swarm::controller
