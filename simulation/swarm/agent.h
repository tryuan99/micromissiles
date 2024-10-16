// The agent class is an interface for an interceptor or a threat.
// The model agent models an agent without any configuration.

#pragma once

#include <Eigen/Dense>
#include <cstdbool>
#include <cstdlib>
#include <memory>
#include <vector>

#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/dynamic_config.pb.h"
#include "simulation/swarm/proto/plotting_config.pb.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "simulation/swarm/state_history.h"

namespace swarm::agent {

// Forward declarations.
class ModelAgent;

// Agent interface.
class Agent {
 public:
  // Principal axes.
  struct PrincipalAxes {
    PrincipalAxes() = default;
    PrincipalAxes(Eigen::Vector3d roll, Eigen::Vector3d pitch,
                  Eigen::Vector3d yaw)
        : roll(std::move(roll)), pitch(std::move(pitch)), yaw(std::move(yaw)) {}

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
  explicit Agent(const AgentConfig& config)
      : Agent(config, /*t_creation=*/0, /*ready=*/true) {}
  Agent(const AgentConfig& config, double t_creation, bool ready);

  // Construct the agent with partial configurations. These constructors should
  // only be used for testing.
  explicit Agent(State initial_state)
      : Agent(std::move(initial_state), /*t_creation=*/0, /*ready=*/true) {}
  Agent(State initial_state, double t_creation, bool ready);

  Agent(const Agent&) = delete;
  Agent& operator=(const Agent&) = delete;

  virtual ~Agent() = default;

  // Return the state of the agent.
  const State& state() const { return state_; }

  // Return the time of the last state update.
  double state_update_time() const { return state_update_time_; }

  // Return the static configuration of the agent.
  const StaticConfig& static_config() const { return static_config_; }

  // Return the dynamic configuration of the agent.
  const DynamicConfig& dynamic_config() const { return dynamic_config_; }

  // Return the plotting configuration of the agent.
  const PlottingConfig& plotting_config() const { return plotting_config_; }

  // Return the submunitions configuration of the agent.
  const AgentConfig::SubmunitionsConfig& submunitions_config() const {
    return submunitions_config_;
  }

  // Return whether the agent has launched.
  bool has_launched() const {
    return flight_phase_ != FlightPhase::INITIALIZED;
  }

  // Return the agent's flight has terminated.
  bool has_terminated() const {
    return flight_phase_ == FlightPhase::TERMINATED;
  }

  // Return whether a target can be assigned to the agent.
  virtual bool assignable() const { return true; }

  // Assign the given target to the agent.
  void AssignTarget(Agent* target);

  // Return whether a target is assigned to the agent.
  bool has_assigned_target() const { return target_ != nullptr; }

  // Return the target assigned to the agent.
  const Agent& target() const { return *target_; }

  // Return the target model of the assigned target.
  const Agent& target_model() const { return *target_model_; }

  // Check whether the assigned target has been hit.
  void CheckTarget();

  // Unassign the target from the agent.
  void UnassignTarget();

  // Return the state history of the agent.
  const state::StateHistory& history() const { return state_history_; }

  // Return whether the agent has hit or been hit.
  bool hit() const { return hit_; }

  // Mark the agent as having hit the target or been hit.
  void MarkAsHit();

  // Return whether the agent has hit the assigned target.
  bool HasHitTarget() const;

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

  // Return the acceleration vector of the agent.
  Eigen::Vector3d GetAcceleration() const;

  // Return the gravity acceleration vector.
  Eigen::Vector3d GetGravity() const;

  // Return the dynamic air pressure around the agent.
  double GetDynamicPressure() const;

  // Update the agent's state according to the environment.
  void Update(double t);

  // Step forward the simulation by simulating the dynamics of the agent.
  void Step(double t_start, double t_step);

  // Spawn new agents.
  virtual std::vector<std::unique_ptr<Agent>> Spawn(const double t) {
    return std::vector<std::unique_ptr<Agent>>();
  }

 protected:
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

  // Static configuration of the agent.
  StaticConfig static_config_;

  // Dynamic configuration of the agent.
  DynamicConfig dynamic_config_;

  // Plotting configuration of the agent.
  PlottingConfig plotting_config_;

  // Submunitions configuration of the agent.
  AgentConfig::SubmunitionsConfig submunitions_config_;

  // Model of the target.
  std::unique_ptr<Agent> target_model_;

  // History of the agent.
  state::StateHistory state_history_;

  // Target assigned to the agent.
  Agent* target_ = nullptr;

  // Boolean indicating whether the agent has hit or been hit.
  bool hit_ = false;
};

// Model agent.
class ModelAgent : public Agent {
 public:
  ModelAgent() = default;
  explicit ModelAgent(State initial_state) : Agent(std::move(initial_state)) {}

  ModelAgent(const ModelAgent&) = delete;
  ModelAgent& operator=(const ModelAgent&) = delete;
};

}  // namespace swarm::agent
