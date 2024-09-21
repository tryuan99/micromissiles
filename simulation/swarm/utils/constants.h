// This file defines some useful constants and conversions.

#pragma once

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
double CalculateAirDensityAtAltitude(double altitude);

// Calculate the gravity at the given altitude.
double CalculateGravityAtAltitude(double altitude);

}  // namespace swarm::constants
