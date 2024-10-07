#include "simulation/swarm/agent.h"

#include <Eigen/Dense>
#include <boost/numeric/odeint.hpp>
#include <boost/numeric/odeint/external/eigen/eigen.hpp>
#include <cmath>
#include <cstdbool>
#include <stdexcept>

#include "absl/strings/str_format.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"
#include "simulation/swarm/utils/constants.h"

namespace swarm::agent {

Agent::Agent(const AgentConfig& config, const double t_creation,
             const bool ready)
    : Agent(config.initial_state(), t_creation, ready) {
  dynamic_config_ = config.dynamic_config();
  plotting_config_ = config.plotting_config();
  submunitions_config_ = config.submunitions_config();
}

Agent::Agent(State initial_state, const double t_creation, const bool ready)
    : t_creation_(t_creation),
      state_(std::move(initial_state)),
      flight_phase_(ready ? FlightPhase::READY : FlightPhase::INITIALIZED) {
  // Add the initial state to the history.
  state_history_.Add(state::StateHistory::Record(t_creation_, hit_, state_));
}

void Agent::AssignTarget(Agent* target) {
  target_ = target;
  target_model_ = std::make_unique<ModelAgent>(target->state());
}

void Agent::CheckTarget() {
  if (has_assigned_target() && target_->hit()) {
    UnassignTarget();
  }
}

void Agent::UnassignTarget() {
  target_ = nullptr;
  target_model_.release();
}

void Agent::MarkAsHit() {
  hit_ = true;
  // Update the latest hit boolean in the history.
  state_history_.back().hit = true;
  flight_phase_ = FlightPhase::TERMINATED;
}

bool Agent::HasHitTarget() const {
  if (!has_assigned_target()) {
    return false;
  }

  // Calculate the distance to the target.
  const auto position = GetPosition();
  const auto target_position = target_->GetPosition();
  const auto distance = (target_position - position).norm();

  // A hit is recorded if the target is within the agent's hit radius.
  const auto hit_radius = static_config().hit_config().hit_radius();
  return distance <= hit_radius;
}

void Agent::SetState(const State& state) {
  state_ = state;
  state_history_.back().state = state;
}

Agent::PrincipalAxes Agent::GetPrincipalAxes() const {
  PrincipalAxes principal_axes;
  // The roll axis is assumed to be aligned with the agent's velocity vector.
  principal_axes.roll = GetVelocity();
  // The pitch axis is to the agent's starboard.
  principal_axes.pitch =
      Eigen::Vector3d{principal_axes.roll(1), -principal_axes.roll(0), 0};
  // The yaw axis points upwards relative to the agent's roll-pitch plane.
  principal_axes.yaw = principal_axes.pitch.cross(principal_axes.roll);
  return principal_axes;
}

Agent::PrincipalAxes Agent::GetNormalizedPrincipalAxes() const {
  auto principal_axes = GetPrincipalAxes();
  principal_axes.roll.normalize();
  principal_axes.pitch.normalize();
  principal_axes.yaw.normalize();
  return principal_axes;
}

Eigen::Vector3d Agent::GetPosition() const {
  return Eigen::Vector3d{
      state_.position().x(),
      state_.position().y(),
      state_.position().z(),
  };
}

Eigen::Vector3d Agent::GetVelocity() const {
  return Eigen::Vector3d{
      state_.velocity().x(),
      state_.velocity().y(),
      state_.velocity().z(),
  };
}

double Agent::GetSpeed() const {
  const auto velocity = GetVelocity();
  return velocity.norm();
}

Eigen::Vector3d Agent::GetGravity() const {
  return Eigen::Vector3d{
      0, 0, -constants::CalculateGravityAtAltitude(state_.position().z())};
}

double Agent::GetDynamicPressure() const {
  const auto air_density =
      constants::CalculateAirDensityAtAltitude(state_.position().z());
  const auto flow_speed = GetSpeed();
  return air_density * std::pow(flow_speed, 2) / 2;
}

void Agent::Update(const double t) {
  const auto launch_time = dynamic_config_.launch_config().launch_time();
  const auto boost_time = static_config().boost_config().boost_time();

  // Determine the flight phase.
  if (t >= t_creation_ + launch_time) {
    flight_phase_ = FlightPhase::BOOST;
  }
  if (t >= t_creation_ + launch_time + boost_time) {
    flight_phase_ = FlightPhase::MIDCOURSE;
  }
  // TODO(titan): Determine when to enter the terminal phase.

  switch (flight_phase_) {
    case FlightPhase::INITIALIZED: {
      return;
    }
    case FlightPhase::READY: {
      UpdateReady(t);
      break;
    }
    case FlightPhase::BOOST: {
      UpdateBoost(t);
      break;
    }
    case FlightPhase::MIDCOURSE:
    case FlightPhase::TERMINAL: {
      UpdateMidCourse(t);
      break;
    }
    default: {
      throw std::runtime_error(
          absl::StrFormat("Invalid flight phase: %d.", flight_phase_));
    }
  }
}

void Agent::Step(const double t_start, const double t_step) {
  // TODO(titan): Evolve the agent's roll, pitch, and yaw.
  using Vector6d = Eigen::Matrix<double, 6, 1>;

  // Update the latest state in the history.
  state_history_.back().t = t_start;
  state_history_.back().state = state_;

  // Check if the step time is zero.
  if (t_step == 0) {
    return;
  }

  const auto position = GetPosition();
  const auto velocity = GetVelocity();

  // The state vector consists of the position and the velocity vectors.
  Vector6d x{
      position(0), position(1), position(2),
      velocity(0), velocity(1), velocity(2),
  };

  // Define the state-space equations.
  const auto kinematics = [&](const Vector6d& x, Vector6d& x_dot,
                              const double t) {
    const auto position_z = x(2);
    const auto velocity_x = x(3);
    const auto velocity_y = x(4);
    const auto velocity_z = x(5);

    // Check if the agent has hit the ground.
    if (position_z < 0) {
      x_dot = Vector6d::Zero();
    } else {
      x_dot = Vector6d{
          // dx/dt = vx
          velocity_x,
          // dy/dt = vy
          velocity_y,
          // dz/dt = vz
          velocity_z,
          // dvx/dt = ax
          state_.acceleration().x(),
          // dvy/dt = ay
          state_.acceleration().y(),
          // dvz/dt = az
          state_.acceleration().z(),
      };
    }
  };

  // Integrate the state-space equations.
  const auto t_end = t_start + t_step;
  boost::numeric::odeint::integrate(kinematics, x, /*start_time=*/t_start,
                                    /*end_time=*/t_end, /*dt=*/t_step / 10);

  // Set the new state.
  const auto position_x = x(0);
  const auto position_y = x(1);
  const auto position_z = x(2);
  const auto velocity_x = x(3);
  const auto velocity_y = x(4);
  const auto velocity_z = x(5);
  state_.mutable_position()->set_x(position_x);
  state_.mutable_position()->set_y(position_y);
  state_.mutable_position()->set_z(position_z);
  state_.mutable_velocity()->set_x(velocity_x);
  state_.mutable_velocity()->set_y(velocity_y);
  state_.mutable_velocity()->set_z(velocity_z);

  // Add the new state to the history.
  state_history_.Add(state::StateHistory::Record(t_end, hit_, state_));
  state_update_time_ = t_end;
}

}  // namespace swarm::agent
