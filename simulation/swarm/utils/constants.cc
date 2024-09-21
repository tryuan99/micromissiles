#include "simulation/swarm/utils/constants.h"

#include <cmath>

namespace swarm::constants {

double CalculateAirDensityAtAltitude(const double altitude) {
  return kAirDensity * std::exp(-altitude / (kAirDensityScaleHeight * 1000));
}

double CalculateGravityAtAltitude(const double altitude) {
  return kGravity *
         std::pow(kEarthMeanRadius / (kEarthMeanRadius + altitude), 2);
}

}  // namespace swarm::constants
