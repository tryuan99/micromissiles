#include "simulation/swarm/sensor/ideal_sensor.h"

#include <cmath>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/sensor.pb.h"

namespace swarm::sensor {

SensorOutput IdealSensor::Sense(const agent::Agent& target) const {
  // TODO(titan): The sensor output should be relative to the agent's roll,
  // pitch, and yaw.
  SensorOutput target_sensor_output;

  // Sense the target's position.
  const auto target_position_sensor_output = SensePosition(target);
  target_sensor_output.MergeFrom(target_position_sensor_output);

  // Sense the target's velocity.
  const auto target_velocity_sensor_output = SenseVelocity(target);
  target_sensor_output.MergeFrom(target_velocity_sensor_output);
  return target_sensor_output;
}

SensorOutput IdealSensor::SensePosition(const agent::Agent& target) const {
  SensorOutput position_sensor_output;
  const auto principal_axes = agent_->GetNormalizedPrincipalAxes();

  // Calculate the relative position of the target with respect to the agent.
  const auto position = agent_->GetPosition();
  const auto target_position = target.GetPosition();
  const auto target_relative_position = target_position - position;

  // Set the Cartesian coordinates.
  position_sensor_output.mutable_position_cartesian()->set_x(
      target_relative_position(0));
  position_sensor_output.mutable_position_cartesian()->set_y(
      target_relative_position(1));
  position_sensor_output.mutable_position_cartesian()->set_z(
      target_relative_position(2));

  // Calculate the distance to the target.
  position_sensor_output.mutable_position()->set_range(
      target_relative_position.norm());

  // Project the relative position vector onto the yaw axis.
  const auto relative_position_projection_on_yaw =
      target_relative_position.dot(principal_axes.yaw) * principal_axes.yaw;
  // Project the relative position vector onto the agent's roll-pitch plane.
  const auto relative_position_projection_on_roll_pitch_plane =
      target_relative_position - relative_position_projection_on_yaw;

  // Determine the sign of the elevation.
  const auto elevation_sign =
      relative_position_projection_on_yaw.dot(principal_axes.yaw) >= 0 ? 1 : -1;

  // Calculate the elevation to the target.
  position_sensor_output.mutable_position()->set_elevation(
      elevation_sign *
      std::atan(relative_position_projection_on_yaw.norm() /
                relative_position_projection_on_roll_pitch_plane.norm()));

  // Project the projection onto the roll axis.
  const auto relative_position_projection_on_roll =
      relative_position_projection_on_roll_pitch_plane.dot(
          principal_axes.roll) *
      principal_axes.roll;
  // Find the projection onto the pitch axis.
  const auto relative_position_projection_on_pitch =
      relative_position_projection_on_roll_pitch_plane -
      relative_position_projection_on_roll;

  if (relative_position_projection_on_pitch.norm() > 0 ||
      relative_position_projection_on_roll.norm() > 0) {
    // Determine the sign of the azimuth.
    const auto azimuth_sign =
        relative_position_projection_on_pitch.dot(principal_axes.pitch) >= 0
            ? 1
            : -1;

    // Calculate the azimuth to the target.
    position_sensor_output.mutable_position()->set_azimuth(
        azimuth_sign * std::atan(relative_position_projection_on_pitch.norm() /
                                 relative_position_projection_on_roll.norm()));
  }
  return position_sensor_output;
}

SensorOutput IdealSensor::SenseVelocity(const agent::Agent& target) const {
  SensorOutput velocity_sensor_output;
  const auto principal_axes = agent_->GetNormalizedPrincipalAxes();

  // Calculate the relative position of the target with respect to the agent.
  const auto position = agent_->GetPosition();
  const auto target_position = target.GetPosition();
  const auto target_relative_position = target_position - position;

  // Calculate the relative velocity of the target with respect to the agent.
  const auto velocity = agent_->GetVelocity();
  const auto target_velocity = target.GetVelocity();
  const auto target_relative_velocity = target_velocity - velocity;

  // Project the relative velocity vector onto the relative position vector.
  const auto velocity_projection_on_relative_position =
      target_relative_velocity.dot(target_relative_position) /
      std::pow(target_relative_position.norm(), 2) * target_relative_position;

  // Determine the sign of the range rate.
  const auto range_rate_sign = velocity_projection_on_relative_position.dot(
                                   target_relative_position) >= 0
                                   ? 1
                                   : -1;

  // Calculate the range rate.
  velocity_sensor_output.mutable_velocity()->set_range(
      range_rate_sign * velocity_projection_on_relative_position.norm());

  // Project the relative velocity vector onto the sphere passing through the
  // target.
  const auto velocity_projection_on_azimuth_elevation_sphere =
      target_relative_velocity - velocity_projection_on_relative_position;

  // The target azimuth vector is orthogonal to the relative position vector and
  // points to the starboard of the target along the azimuth-elevation sphere.
  auto target_azimuth = target_relative_position.cross(principal_axes.yaw);
  // The target elevation vector is orthogonal to the relative position vector
  // and points upwards from the target along the azimuth-elevation sphere.
  auto target_elevation = principal_axes.pitch.cross(target_relative_position);
  // If the relative position vector is parallel to the yaw or pitch axis, the
  // target azimuth vector or the target elevation vector will be undefined.
  if (target_azimuth.norm() == 0) {
    target_azimuth = target_relative_position.cross(target_elevation);
  } else if (target_elevation.norm() == 0) {
    target_elevation = target_azimuth.cross(target_relative_position);
  }

  // Project the relative velocity vector on the azimuth-elevation sphere onto
  // the target azimuth vector.
  const auto velocity_projection_on_target_azimuth =
      velocity_projection_on_azimuth_elevation_sphere.dot(target_azimuth) /
      std::pow(target_azimuth.norm(), 2) * target_azimuth;

  // Determine the sign of the azimuth velocity.
  const auto azimuth_velocity_sign =
      velocity_projection_on_target_azimuth.dot(target_azimuth) >= 0 ? 1 : -1;

  // Calculate the time derivative of the azimuth to the target.
  velocity_sensor_output.mutable_velocity()->set_azimuth(
      azimuth_velocity_sign * velocity_projection_on_target_azimuth.norm() /
      target_relative_position.norm());

  // Project the velocity vector on the azimuth-elevation sphere onto the target
  // elevation vector.
  const auto velocity_projection_on_target_elevation =
      velocity_projection_on_azimuth_elevation_sphere -
      velocity_projection_on_target_azimuth;

  // Determine the sign of the elevation velocity.
  const auto elevation_velocity_sign =
      velocity_projection_on_target_elevation.dot(target_elevation) >= 0 ? 1
                                                                         : -1;

  // Calculate the time derivative of the elevation to the target.
  velocity_sensor_output.mutable_velocity()->set_elevation(
      elevation_velocity_sign * velocity_projection_on_target_elevation.norm() /
      target_relative_position.norm());
  return velocity_sensor_output;
}

}  // namespace swarm::sensor
