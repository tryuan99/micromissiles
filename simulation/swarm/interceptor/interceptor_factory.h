// The interceptor factory constructs interceptors based on its type.

#pragma once

#include <memory>
#include <stdexcept>
#include <utility>

#include "absl/strings/str_format.h"
#include "simulation/swarm/interceptor/hydra_70.h"
#include "simulation/swarm/interceptor/interceptor.h"
#include "simulation/swarm/interceptor/micromissile.h"
#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {

// Interceptor factory.
class InterceptorFactory {
 public:
  InterceptorFactory() = default;

  // Create a interceptor.
  template <typename... Args>
  std::unique_ptr<Interceptor> CreateInterceptor(const InterceptorType type,
                                                 Args&&... args) {
    switch (type) {
      case InterceptorType::MICROMISSILE: {
        return std::make_unique<Micromissile>(std::forward<Args>(args)...);
      }
      case InterceptorType::HYDRA_70: {
        return std::make_unique<Hydra70>(std::forward<Args>(args)...);
      }
      default: {
        throw std::invalid_argument(
            absl::StrFormat("Invalid interceptor type: %d.", type));
      }
    }
  }
};

}  // namespace swarm::interceptor
