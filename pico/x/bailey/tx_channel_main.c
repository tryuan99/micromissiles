// Configures a single beamformer TX channel from commands received over USB
// serial for characterization.
//
// Each command is a newline-terminated line "<channel> <vga_gain> <phase>":
//   channel: TX channel in [1, 4].
//   vga_gain: VGA gain code in [0, 127].
//   phase: Phase index in [0, 127], i.e., in units of 2.8125 degrees.
// Only the commanded channel is enabled with the attenuator bypassed. The other
// channels are disabled to prevent their outputs from reflecting into the
// channel under test. The firmware replies with "OK <channel> <vga_gain>
// <phase>" once the new configuration is loaded, or with "ERROR <command>" if
// the command is invalid.

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/common/led.h"
#include "pico/stdlib.h"
#include "pico/x/bailey/beamformer.h"
#include "pico/x/bailey/config.h"

// Maximum VGA gain code.
#define VGA_GAIN_MAX 0x7F

// Maximum command length, including the null terminator.
#define COMMAND_BUFFER_SIZE 32

// Beamformer TX configuration.
// All channels start disabled until the first command.
static beamformer_tx_config_t g_beamformer_tx_config;

// Read a newline-terminated command from USB serial into the buffer. Carriage
// returns are ignored, and characters beyond the buffer size are dropped.
static void read_command(char* buffer, size_t size) {
  size_t length = 0;
  while (true) {
    const int c = getchar();
    if (c == '\n') {
      break;
    }
    if (c != '\r' && length < size - 1) {
      buffer[length++] = (char)c;
    }
  }
  buffer[length] = '\0';
}

// Parse the command into the channel, VGA gain code, and phase. Return false if
// the command is malformed or a value is out of range.
static bool parse_command(const char* command, unsigned* channel,
                          unsigned* vga_gain, unsigned* phase) {
  char trailing;
  if (sscanf(command, "%u %u %u %c", channel, vga_gain, phase, &trailing) !=
      3) {
    return false;
  }
  return *channel >= 1 && *channel <= BEAMFORMER_NUM_CHANNELS &&
         *vga_gain <= VGA_GAIN_MAX && *phase < BEAMFORMER_NUM_PHASES;
}

// Enable only the given channel with the given VGA gain code and phase.
static void configure_channel(unsigned channel, unsigned vga_gain,
                              unsigned phase) {
  for (size_t i = 0; i < BEAMFORMER_NUM_CHANNELS; ++i) {
    g_beamformer_tx_config.channel_configs[i] =
        (beamformer_tx_channel_config_t){
            .enabled = i == channel - 1,
            .attenuator = BEAMFORMER_ATTENUATOR_BYPASS,
            .vga_gain = vga_gain,
            .phase = (beamformer_phase_e)phase,
        };
  }
  beamformer_configure_tx(&g_beamformer_tx_config);
  beamformer_load_tx();
}

int main(int argc, char** argv) {
  stdio_init_all();
  led_init();

  // Initialize the beamformer with all channels disabled.
  beamformer_init(&g_beamformer_config);
  beamformer_configure_tx(&g_beamformer_tx_config);
  beamformer_load_tx();

  led_on();
  char command[COMMAND_BUFFER_SIZE];
  while (true) {
    read_command(command, COMMAND_BUFFER_SIZE);
    unsigned channel, vga_gain, phase;
    if (!parse_command(command, &channel, &vga_gain, &phase)) {
      printf("ERROR %s\n", command);
      continue;
    }
    configure_channel(channel, vga_gain, phase);
    printf("OK %u %u %u\n", channel, vga_gain, phase);
  }
  return EXIT_SUCCESS;
}
