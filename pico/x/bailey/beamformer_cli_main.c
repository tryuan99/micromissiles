#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/common/cli.h"
#include "pico/common/led.h"
#include "pico/stdlib.h"
#include "pico/x/bailey/beamformer.h"
#include "pico/x/bailey/config.h"

// Beamformer TX configuration.
static beamformer_tx_config_t g_beamformer_tx_config;

// Beamformer CLI valid.
static bool g_beamformer_cli_valid = false;

// Beamformer channel.
static uint8_t g_beamformer_channel = 0;

// Beamformer VGA gain.
static uint8_t g_beamformer_vga_gain = 0;

// Beamformer phase index into the phase enumeration.
static uint8_t g_beamformer_phase_index = 0;

static inline void beamformer_configure(void) {
  for (size_t i = 0; i < BEAMFORMER_NUM_CHANNELS; ++i) {
    g_beamformer_tx_config.channel_configs[i] =
        (beamformer_tx_channel_config_t){
            .enabled = i == g_beamformer_channel - 1,
            .attenuator = BEAMFORMER_ATTENUATOR_BYPASS,
            .vga_gain = g_beamformer_vga_gain,
            .phase = (beamformer_phase_e)g_beamformer_phase_index,
        };
  }
  beamformer_configure_tx(&g_beamformer_tx_config);
  beamformer_load_tx();
}

static void beamformer_cli_callback(const char* input) {
  // Parse the input.
  g_beamformer_cli_valid =
      sscanf(input, "%u %u %u %c", &g_beamformer_channel,
             &g_beamformer_vga_gain, &g_beamformer_phase_index) == 3;
  if (g_beamformer_channel < 1 ||
      g_beamformer_channel > BEAMFORMER_NUM_CHANNELS) {
    g_beamformer_cli_valid = false;
  }
}

int main(int argc, char** argv) {
  stdio_init_all();
  led_init();
  cli_register_callback(beamformer_cli_callback);

  // Initialize the beamformer with all channels disabled.
  beamformer_init(&g_beamformer_config);
  beamformer_configure_tx(&g_beamformer_tx_config);
  beamformer_load_tx();

  led_on();
  while (true) {
    cli_read_input();
    if (g_beamformer_cli_valid) {
      printf("Channel %u: VGA gain = %u, phase index = %u\n",
             g_beamformer_channel, g_beamformer_vga_gain,
             g_beamformer_phase_index);
    } else {
      printf("Failed to parse input.");
    }
  }
  return EXIT_SUCCESS;
}
