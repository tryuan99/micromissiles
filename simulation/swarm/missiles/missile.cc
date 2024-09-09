#include "simulation/swarm/missiles/missile.h"

#include <Eigen/Dense>
#include <cmath>
#include <cstdbool>

#include "simulation/swarm/constants.h"
#include "simulation/swarm/proto/missile_config.pb.h"
#include "simulation/swarm/sensors/sensor_factory.h"

namespace swarm::missile {

Missile::Missile(const MissileConfig& config) : Agent<MissileConfig>(config) {
  SensorFactory sensor_factory;
  sensor_ = sensor_factory.CreateSensor(dynamic_config().sensor_config().type(),
                                        this);
}

Missile::Missile(const MissileConfig& config, const double t_creation,
                 const bool ready)
    : Agent<MissileConfig>(config, t_creation, ready) {
  SensorFactory sensor_factory;
  sensor_ = sensor_factory.CreateSensor(dynamic_config().sensor_config().type(),
                                        this);
}

bool Missile::HasHitTarget() const {
  if (!has_assigned_target()) {
    return false;
  }

  // Calculate the distance to the target.
  const auto position = GetPosition();
  const auto target_position = target_->GetPosition();
  const auto distance = (target_position - position).norm();

  // A hit is recorded if the target is within the missile's hit radius.
  const auto hit_radius = static_config().hit_config().hit_radius();
  return distance <= hit_radius;
}

void Missile::UpdateReady(const double t) override {
  // The missile is subject to gravity and drag with zero input acceleration.
  Eigen::Vector3d acceleration_input = Eigen::Vector3d::Zero();

  // Calculate and set the total acceleration.
  const auto acceleration = CalculateAcceleration(acceleration_input);
  state_.mutable_acceleration()->set_x(acceleration(0));
  state_.mutable_acceleration()->set_y(acceleration(1));
  state_.mutable_acceleration()->set_z(acceleration(2));
}

void Missile::UpdateBoost(const double t) override {
  // The missile only accelerates along its roll axis.
  const auto principal_axes = GetNormalizedPrincipalAxes();
  const auto boost_acceleration =
      static_config().boost_config().boost_acceleration() * constants::kGravity;
  const auto acceleration_input = boost_acceleration * principal_axes.roll;

  // Calculate and set the total acceleration.
  const auto acceleration = CalculateAcceleration(acceleration_input);
  state_.mutable_acceleration()->set_x(acceleration(0));
  state_.mutable_acceleration()->set_y(acceleration(1));
  state_.mutable_acceleration()->set_z(acceleration(2));
}

Eigen::Vector3d Missile::CalculateAcceleration(
    const Eigen::Vector3d& acceleration_input,
    const bool compensate_for_gravity) const {
  // Determine the gravity and compensate for it.
  const auto gravity = GetGravity();
  Eigen::Vector3d compensated_acceleration_input(acceleration_input);
  if (compensate_for_gravity) {
    const auto gravity_projection_on_pitch_and_yaw =
        CalculateGravityProjectionOnPitchAndYaw();
    compensated_acceleration_input -= gravity_projection_on_pitch_and_yaw;
  }

  // Calculate the air drag.
  const auto air_drag_acceleration = CalculateDrag();
  // Calculate the lift-induced drag.
  const auto lift_induced_drag_acceleration =
      CalculateLiftInducedDrag(compensated_acceleration_input);
  // Calculate the total drag acceleration.
  const auto principal_axes = GetNormalizedPrincipalAxes();
  const auto drag_acceleration =
      -(air_drag_acceleration + lift_induced_drag_acceleration) *
      principal_axes.roll;

  // Calculate the total acceleration vector.
  return compensated_acceleration_input + gravity + drag_acceleration;
}

double Missile::CalculateMaxAcceleration() const {
  const auto max_reference_acceleration =
      static_config().acceleration_config().max_reference_acceleration() *
      constants::kGravity;
  const auto reference_speed =
      static_config().acceleration_config().reference_speed();

  // The maximum acceleration scales with the squared speed.
  return std::pow(GetSpeed() / reference_speed, 2) * max_reference_acceleration;
}

Eigen::Vector3d Missile::CalculateGravityProjectionOnPitchAndYaw() const {
  const auto principal_axes = GetNormalizedPrincipalAxes();
  const auto gravity = GetGravity();

  // Project the gravity onto the pitch and yaw axes.
  const auto gravity_projection_pitch_coefficient =
      gravity.dot(principal_axes.pitch);
  const auto gravity_projection_yaw_coefficient =
      gravity.dot(principal_axes.yaw);
  return gravity_projection_pitch_coefficient * principal_axes.pitch +
         gravity_projection_yaw_coefficient * principal_axes.yaw;
}

double Missile::CalculateDrag() const {
  const auto drag_coefficient =
      static_config().lift_drag_config().drag_coefficient();
  const auto cross_section_area =
      static_config().body_config().cross_sectional_area();
  const auto mass = static_config().body_config().mass();

  const auto dynamic_pressure = GetDynamicPressure();
  const auto drag_force =
      drag_coefficient * dynamic_pressure * cross_sectional_area;
  return drag_force / mass;
}

double Missile::CalculateLiftInducedDrag(
    const Eigen::Vector3d& acceleration_input) const {
  // Project the acceleration input onto the yaw axis.
  const auto principal_axes = GetNormalizedPrincipalAxes();
  const auto lift_acceleration = acceleration_input.dot(principal_axes.yaw);

  // Calculate the drag acceleration from the lift acceleration.
  const auto lift_drag_ratio = static_config().drag_config().lift_drag_ratio();
  return std::abs(lift_acceleration / lift_drag_ratio);
}

}  // namespace swarm::missile
