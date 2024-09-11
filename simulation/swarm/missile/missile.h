// The missile class is an interface for the dynamics of a single missile.

#pragma once

#include <Eigen/Dense>
#include <cstdbool>
#include <limits>
#include <memory>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/model_agent.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/sensor/sensor.h"

namespace swarm::missile {

// Missile interface.
class Missile : public agent::Agent {
 public:
  Missile() = default;

  explicit Missile(const AgentConfig& config);
  Missile(const AgentConfig& config, double t_creation, bool ready);

  Missile(const Missile&) = delete;
  Missile& operator=(const Missile&) = delete;

  virtual ~Missile() = default;

  // Return whether a target can be assigned to the missile.
  virtual bool assignable() const override {
    return has_launched() && !has_assigned_target();
  }

  // Assign the given target to the missile.
  void AssignTarget(Agent* target) override {
    target_ = target;
    target_model_ = std::make_unique<agent::ModelAgent>(target->state());
  }

  // Unassign the target from the missile.
  void UnassignTarget() override {
    target_ = nullptr;
    target_model_.release();
  }

 protected:
  // Update the missile's state in the ready phase.
  void UpdateReady(double t) override;

  // Update the missile's state in the boost phase.
  void UpdateBoost(double t) override;

  // Calculate the total acceleration vector, including gravity and drag.
  Eigen::Vector3d CalculateAcceleration(
      const Eigen::Vector3d& acceleration_input) const {
    return CalculateAcceleration(acceleration_input,
                                 /*compensate_for_gravity=*/false);
  }
  Eigen::Vector3d CalculateAcceleration(
      const Eigen::Vector3d& acceleration_input,
      bool compensate_for_gravity) const;

  // Calculate the maximum acceleration of the missile based on its velocity.
  double CalculateMaxAcceleration() const;

  // Sensor mounted on the missile.
  std::unique_ptr<sensor::Sensor> sensor_;

  // Time of the last sensor update.
  double sensor_update_time_ = std::numeric_limits<double>::min();

  // Model of the target.
  std::unique_ptr<agent::Agent> target_model_;

 private:
  // Calculate the gravity projection on the pitch and yaw axes.
  Eigen::Vector3d CalculateGravityProjectionOnPitchAndYaw() const;

  // Calculate the air drag.
  double CalculateDrag() const;

  // Calculate the lift-induced drag.
  double CalculateLiftInducedDrag(
      const Eigen::Vector3d& acceleration_input) const;
};

}  // namespace swarm::missile
