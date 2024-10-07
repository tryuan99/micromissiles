#include "simulation/swarm/interceptor/micromissile.h"

#include <Eigen/Dense>
#include <cmath>

#include "simulation/swarm/controller/pn_controller.h"
#include "utils/random.h"

namespace swarm::interceptor {

void Micromissile::UpdateMidCourse(const double t) {
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

    // Calculate the acceleration input by sensing the target model.
    acceleration_input = CalculateAccelerationInput();
  }

  // Calculate and set the total acceleration.
  const auto acceleration = CalculateAcceleration(
      acceleration_input, /*compensate_for_gravity=*/true);
  state_.mutable_acceleration()->set_x(acceleration(0));
  state_.mutable_acceleration()->set_y(acceleration(1));
  state_.mutable_acceleration()->set_z(acceleration(2));
}

Eigen::Vector3d Micromissile::CalculateAccelerationInput() const {
  // The micromissile uses proportional navigation.
  controller::PnController controller(*this);
  controller.Plan();
  auto acceleration_input = controller.GetOptimalControl();

  // Clamp the acceleration vector.
  const auto max_acceleration = CalculateMaxAcceleration();
  if (acceleration_input.norm() > max_acceleration) {
    return acceleration_input.normalized() * max_acceleration;
  }
  return acceleration_input;
}

}  // namespace swarm::interceptor
