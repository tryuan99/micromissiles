#include "utils/random.h"

#include <random>

namespace utils {

double GenerateRandomNormal(const double mean,
                            const double standard_deviation) {
  std::random_device random_device;
  std::mt19937 generator(random_device());
  std::normal_distribution<double> distribution(mean, standard_deviation);
  return distribution(generator);
}

double GenerateRandomUniform(const double a, const double b) {
  std::random_device random_device;
  std::mt19937 generator(random_device());
  std::uniform_real_distribution<double> distribution(a, b);
  return distribution(generator);
}

}  // namespace utils
