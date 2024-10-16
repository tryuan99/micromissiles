// The interceptor class is an interface for the dynamics of a single
// interceptor.

#pragma once

#include <Eigen/Dense>
#include <cstdbool>
#include <limits>
#include <memory>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/sensor/sensor.h"

namespace swarm::interceptor {

// Interceptor interface.
class Interceptor : public agent::Agent {
 public:
  Interceptor() = default;

  explicit Interceptor(const AgentConfig& config);
  Interceptor(const AgentConfig& config, double t_creation, bool ready);

  Interceptor(const Interceptor&) = delete;
  Interceptor& operator=(const Interceptor&) = delete;

  virtual ~Interceptor() = default;

  // Return whether a target can be assigned to the interceptor.
  virtual bool assignable() const override {
    return has_launched() && !has_assigned_target();
  }

 protected:
  // Update the interceptor's state in the ready phase.
  void UpdateReady(double t) override;

  // Update the interceptor's state in the boost phase.
  void UpdateBoost(double t) override;

  // Calculate the total acceleration vector, including gravity and drag.
  Eigen::Vector3d CalculateAcceleration(
      const Eigen::Vector3d& acceleration_input) const;

  // Calculate the maximum acceleration of the interceptor based on its
  // velocity.
  double CalculateMaxAcceleration() const;

  // Sensor mounted on the interceptor.
  std::unique_ptr<sensor::Sensor> sensor_;

  // Time of the last sensor update.
  double sensor_update_time_ = std::numeric_limits<double>::min();

 private:
  // Calculate the gravity projection on the pitch and yaw axes.
  Eigen::Vector3d CalculateGravityProjectionOnPitchAndYaw() const;

  // Calculate the air drag.
  double CalculateDrag() const;

  // Calculate the lift-induced drag.
  double CalculateLiftInducedDrag(
      const Eigen::Vector3d& acceleration_input) const;
};

}  // namespace swarm::interceptor
