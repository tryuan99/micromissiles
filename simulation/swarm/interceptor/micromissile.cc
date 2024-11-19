#include "simulation/swarm/interceptor/micromissile.h"

#include <Eigen/Dense>
#include <cmath>
#include <memory>

#include "simulation/swarm/controller/agent_controller.h"
#include "simulation/swarm/controller/mpc_controller.h"
#include "simulation/swarm/controller/pn_controller.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/sensor/ideal_sensor.h"
#include "utils/random.h"

namespace swarm::interceptor {

std::unique_ptr<controller::AgentController> Micromissile::GetController()
    const {
  sensor::IdealSensor sensor(*this);
  const auto sensor_output = sensor.Sense(*target_model_);
  if (sensor_output.position().range() <
      static_config_.controller_config()
          .proportional_navigation_range_threshold()) {
    return std::make_unique<controller::PnController>(*this);
  }
  return std::make_unique<controller::MpcController>(*this);
}

}  // namespace swarm::interceptor
