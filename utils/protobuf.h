// This file defines some useful utilities for Protobuf.

#pragma once

#include <fstream>
#include <stdexcept>
#include <string>

#include "absl/strings/str_format.h"
#include "google/protobuf/io/zero_copy_stream_impl.h"
#include "google/protobuf/text_format.h"

namespace utils {

// Load the Protobuf text file and return the Protobuf message.
template <typename T>
T LoadProtobufTextFile(const std::string& file) {
  std::ifstream ifs(file);
  if (!ifs.is_open()) {
    throw std::runtime_error(
        absl::StrFormat("Failed to open the Protobuf text file: %s.", file));
  }
  google::protobuf::io::IstreamInputStream file_stream(&ifs);
  T message;
  if (!google::protobuf::TextFormat::Parse(&file_stream, &message)) {
    throw std::runtime_error(
        absl::StrFormat("Failed to parse the Protobuf text file: %s.", file));
  }
  return message;
}

}  // namespace utils
