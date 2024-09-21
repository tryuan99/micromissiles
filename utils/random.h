// This file defines some useful utilities to generate random numbers.

#pragma once

namespace utils {

// Generate a random number normally distributed with the given mean and
// standard deviation.
double GenerateRandomNormal(double mean, double standard_deviation);

// Generate a random number uniformly distributed over the interval.
double GenerateRandomUniform(double a, double b);

}  // namespace utils
