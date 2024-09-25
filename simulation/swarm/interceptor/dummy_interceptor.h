// The dummy interceptor class represents the dynamics of a single dummy
// interceptor.

#pragma once

#include "simulation/swarm/interceptor/interceptor.h"
#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {

// Dummy interceptor.
class DummyInterceptor : public Interceptor {
 public:
  DummyInterceptor() = default;

  explicit DummyInterceptor(const AgentConfig& config) : Interceptor(config) {}
  DummyInterceptor(const AgentConfig& config, const double t_creation,
                   const bool ready)
      : Interceptor(config, t_creation, ready) {}

  DummyInterceptor(const DummyInterceptor&) = delete;
  DummyInterceptor& operator=(const DummyInterceptor&) = delete;
};

}  // namespace swarm::interceptor
