#include "simulation/swarm/missiles/micromissile.h"

#include <Eigen/Dense>
#include <cmath>

#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/utils.h"

namespace swarm::missile {

void Micromissile::UpdateMidCourse(const double t) {
  // The missile uses proportional navigation to intercept the target, i.e., it
  // should maintian a constant azimuth and elevation to the target.
  Eigen::Vector3d acceleration_input = Eigen::Vector3d::Zero(3);
  if (has_assigned_target()) {
    // Update the target model.
    const auto model_step_time = t - target_model_->state_update_time();
    target_model_->Update(t);
    target_model_->Step(target_model_->state_update_time(), model_step_time);

    // Correct the state of the target model at the sensor frequency.
    const auto sensor_update_period =
        1 / dynamic_config().sensor_config().frequency();
    if (t - sensor_update_time_ >= sensor_update_period) {
      // TODO(titan): Use some guidance filter to estimate the state from the
      // sensor output.
      target_model_->SetState(target_->state());
      sensor_update_time_ = t;
    }

    // Sense the target.
    const auto sensor_output = sensor_->Sense(*target_model_);

    // Check whether the target has been hit.
    if (HasHitTarget()) {
      // Consider the kill probability of the target.
      const auto kill_probability =
          target_->static_config().hit_config().kill_probability();
      if (utils::GenerateRandomUniform(0, 1) < kill_probability) {
        MarkAsHit();
        target_->MarkAsHit();
        return;
      }
    }

    // Calculate the acceleration input.
    acceleration_input = CalculateAccelerationInput(sensor_output);
  }

  // Calculate and set the total acceleration.
  const auto acceleration = CalculateAcceleration(
      acceleration_input, /*compensate_for_gravity=*/true);
  state_.mutable_acceleration()->set_x(acceleration(0));
  state_.mutable_acceleration()->set_y(acceleration(1));
  state_.mutable_acceleration()->set_z(acceleration(2));
}

Eigen::Vector3d Micromissile::CalculateAccelerationInput(
    const SensorOutput& sensor_output) const {
  // In proportional navigation, the acceleration vector should be proportional
  // to the rate of change of the bearing.
  const auto azimuth_velocity = sensor_output.velocity().azimuth();
  const auto elevation_velocity = sensor_output.velocity().elevation();

  // Calculate the acceleration components along the axes normal to the roll
  // axis.
  const auto pitch_coefficient =
      std::cos(elevation_velocity) * std::sin(azimuth_velocity);
  const auto yaw_coefficient = std::sin(elevation_velocity);

  // Calculate the desired acceleration vector. The missile cannot accelerate
  // along the roll axis.
  const auto principal_axes = GetNormalizedPrincipalAxes();
  const auto acceleration_input = pitch_coefficient * principal_axes.pitch +
                                  yaw_coefficient * principal_axes.yaw;

  // Limit the acceleration vector.
  return acceleration_input.normalized() * CalculateMaxAcceleration();
}

}  // namespace swarm::missile
