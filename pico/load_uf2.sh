#!/bin/bash

# This script loads a UF2 binary onto the Raspberry Pi Pico assuming that it is in
# BOOTSEL mode.
#
# Usage:
#   bazel-bin/pico/load_uf2 \
#       /path/to/uf2 \
#       /path/to/pico/device
#
# By default, the Pico device path is /Volumes/RP2350.

# Default Pico device.
DEFAULT_PICO_DEVICE="/Volumes/RP2350"

function print_usage() {
  echo "Usage: $0 <uf2_path> [<pico_device_path>]"
}

# Check for at least one argument.
if [ "$#" -lt 1 ]; then
  print_usage
  exit 1
fi

UF2_BINARY=$1
PICO_DEVICE=${2:-$DEFAULT_PICO_DEVICE}

# Check if the UF2 binary exists.
if [ ! -e "$UF2_BINARY" ]; then
  echo "Error: UF2 binary '$UF2_BINARY' does not exist."
  exit 1
fi

# Check if the Pico device exists.
if [ ! -e "$PICO_DEVICE" ]; then
  echo "Error: Pico device '$PICO_DEVICE' does not exist."
  exit 1
fi

# Load the UF2 binary onto the Pico device.
echo "Loading UF2 binary '$UF2_BINARY' onto '$PICO_DEVICE'."
if cp "$UF2_BINARY" "$PICO_DEVICE"; then
  echo "Successfully loaded UF2 binary '$UF2_BINARY' onto '$PICO_DEVICE'."
else
  echo "Error: Failed to load UF2 binary '$UF2_BINARY' onto '$PICO_DEVICE'."
  exit 1
fi
