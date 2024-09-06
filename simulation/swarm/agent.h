// The agent class is an interface for a missile or a target.

#pragma once

#include <Eigen/Dense>
#include <cstdbool>
#include <cstdlib>
#include <vector>

#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/dynamic_config.pb.h"
#include "simulation/swarm/proto/missile_config.pb.h"
#include "simulation/swarm/proto/plotting_config.pb.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "simulation/swarm/proto/target_config.pb.h"
#include "simulation/swarm/state_history.h"

namespace swarm::agent {

// Agent.
template <typename T>
class Agent {
 public:
  // Principal axes.
  struct PrincipalAxes {
    // Roll axis.
    // The roll axis is assumed to be aligned with the agent's velocity vector.
    Eigen::Vector3d roll;

    // Pitch axis.
    // The pitch axis is to the agent's starboard.
    Eigen::Vector3d pitch;

    // Yaw axis.
    // The yaw axis points upwards relative to the agent's roll-pitch plane.
    Eigen::Vector3d yaw;
  };

  Agent() = default;

  // Construct the agent with a full configuration.
  Agent(const T& config) : Agent(config, /*t_creation=*/0, /*ready=*/true) {}
  Agent(const T& config, double t_creation, bool ready);

  // Construct the agent with partial configurations. These constructors should
  // only be used for testing.
  Agent(State initial_state)
      : Agent(std::move(initial_state), /*t_creation=*/0, /*ready=*/true) {}
  Agent(State initial_state, double t_creation, bool ready);

  Agent(const Agent&) = default;
  Agent& operator=(const Agent&) = default;

  virtual ~Agent() = default;

  // Return the static configuration of the agent.
  virtual const StaticConfig& static_config() const = 0;

  // Return whether the agent has launched.
  bool has_launched() const {
    return flight_phase_ != FlightPhase::INITIALIZED &&
           flight_phase_ != FlightPhase::READY;
  }

  // Return the agent's flight has terminated.
  bool has_terminated() const {
    return flight_phase_ == FlightPhase::TERMINATED;
  }

  // Mark the agent as having hit the target or been hit.
  void MarkAsHit();

  // Set the state of the agent.
  void SetState(const State& state);

  // Return the principal axes of the agent.
  PrincipalAxes GetPrincipalAxes() const;

  // Return the normalized principal axes of the agent.
  PrincipalAxes GetNormalizedPrincipalAxes() const;

  // Return the position vector of the agent.
  Eigen::Vector3d GetPosition() const;

  // Return the velocity vector of the agent.
  Eigen::Vector3d GetVelocity() const;

  // Return the speed of the agent.
  double GetSpeed() const;

  // Return the gravity acceleration vector.
  Eigen::Vector3d GetGravity() const;

  // Return the dynamic air pressure around the agent.
  double GetDynamicPressure() const;

  // Update the agent's state according to the environment.
  void Update(double t);

  // Step forward the simulation by simulating the dynamics of the agent.
  void Step(double t_start, double t_step);

 protected:
  // Spawn new agents.
  virtual std::vector<Agent> Spawn(const double t) {
    return std::vector<Agent>();
  }

  // Update the agent's state in the ready flight phase.
  virtual void UpdateReady(const double t) {}

  // Update the agent's state in the boost flight phase.
  virtual void UpdateBoost(const double t) {}

  // Update the agent's state in the midcourse flight phase.
  virtual void UpdateMidCourse(const double t) {}

  // Creation time in s.
  double t_creation_ = 0.0;

  // Current state.
  State state_;

  // Time of the last state update in s.
  double state_update_time_ = 0.0;

  // Flight phase of the agent.
  FlightPhase flight_phase_ = FlightPhase::INITIALIZED;

  // Dynamic configuration of the agent.
  DynamicConfig dynamic_config_;

  // Plotting configuration of the agent.
  PlottingConfig plotting_config_;

  // Submunitions configuration of the agent.
  T::SubmunitionsConfig submunitions_config_;

  // History of the agent.
  state::StateHistory state_history_;

  // Boolean indicating whether the agent has hit or been hit.
  bool hit_ = false;
};

}  // namespace swarm::agent
