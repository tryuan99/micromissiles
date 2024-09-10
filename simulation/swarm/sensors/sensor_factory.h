// The sensor factory constructs sensors based on its type.

#pragma once

#include <memory>
#include <stdexcept>
#include <utility>

#include "absl/strings/str_format.h"
#include "simulation/swarm/proto/sensor.pb.h"
#include "simulation/swarm/sensors/ideal_sensor.h"
#include "simulation/swarm/sensors/sensor.h"

namespace swarm::sensor {

// Sensor factory.
class SensorFactory {
 public:
  SensorFactory() = default;

  // Create a missile.
  template <typename... Args>
  std::unique_ptr<Sensor> CreateSensor(const SensorType type, Args&&... args) {
    switch (type) {
      case SensorType::IDEAL: {
        return std::make_unique<IdealSensor>(std::forward<Args>(args)...);
      }
      default: {
        throw std::invalid_argument(
            absl::StrFormat("Invalid sensor type: %d.", type));
      }
    }
  }
};

}  // namespace swarm::sensor
