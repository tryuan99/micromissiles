#include "simulation/swarm/utils.h"

#include <fcntl.h>

#include <random>
#include <stdexcept>
#include <string>

#include "google/protobuf/io/zero_copy_stream_impl.h"
#include "google/protobuf/text_format.h"
#include "simulation/swarm/proto/static_config.pb.h"

namespace swarm::utils {

StaticConfig LoadStaticConfigFromFile(const std::string& file) {
  const int fd = open(file.c_str(), O_RDONLY);
  if (fd < 0) {
    throw std::runtime_error(absl::StrFormat(
        "Unable to open the static configuration file: %s", file));
  }
  google::protobuf::io::FileInputStream static_config_file_stream(fd);
  StaticConfig static_config;
  if (!google::protobuf::TextFormat::Parse(&static_config_file_stream,
                                           &static_config)) {
    throw std::runtime_error(absl::StrFormat(
        "Failed to parse the static configuration file: %s.", file));
  }
  static_config_file_stream.Close();
  return static_config;
}

double GenerateRandomUniform(const double a, const double b) {
  std::random_device random_device;
  std::mt19937 generator(random_device());
  std::uniform_real_distribution<double> distribution(a, b);
  return distribution(generator);
}

}  // namespace swarm::utils
