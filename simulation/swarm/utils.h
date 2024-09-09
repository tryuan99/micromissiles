// This file defines some useful utilities.

#pragma once

#include <string>

#include "simulation/swarm/proto/static_config.pb.h"

namespace swarm::utils {

// Load the static configuration from a file.
StaticConfig LoadStaticConfigFromFile(const std::string& file);

// Generate a random number uniformly distributed over the interval.
double GenerateRandomUniform(double a, double b);

}  // namespace swarm::utils
