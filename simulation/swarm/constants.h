// This file defines some useful constants and conversions.

#pragma once

#include <cmath>

namespace swarm::constants {

// Air density in kg/m^3.
constexpr double kAirDensity = 1.204;

// Air density scale height in km.
constexpr double kAirDensityScaleHeight = 10.4;

// Standard gravity in m/s^2.
constexpr double kGravity = 9.80665;

// Earth mean radius in meters.
constexpr double kEarthMeanRadius = 6378137;

// Calculate the air density at the given altitude.
double CalculateAirDensityAtAltitude(const double altitude) {
  return kAirDensity * std::exp(-altitude / (kAirDensityScaleHeight * 1000));
}

// Calculate the gravity at the given altitude.
double CalculateGravityAtAltitude(const double altitude) {
  return kGravity *
         std::pow(kEarthMeanRadius / (kEarthMeanRadius + altitude), 2);
}

}  // namespace swarm::constants
