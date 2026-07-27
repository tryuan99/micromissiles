#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/common/led.h"
#include "pico/stdlib.h"
#include "pico/x/bailey/adc.h"
#include "pico/x/bailey/beamformer.h"
#include "pico/x/bailey/config.h"
#include "pico/x/bailey/mixer.h"

// Beamformer TX configuration.
// All four channels are enabled with a zero phase shift.
static beamformer_tx_config_t g_beamformer_tx_config = (beamformer_tx_config_t){
    .channel_configs =
        {
            (beamformer_tx_channel_config_t){
                .enabled = true,
                .attenuator = BEAMFORMER_ATTENUATOR_BYPASS,
                .vga_gain = 0x7F,
                .phase = BEAMFORMER_PHASE_0,
            },
            (beamformer_tx_channel_config_t){
                .enabled = true,
                .attenuator = BEAMFORMER_ATTENUATOR_BYPASS,
                .vga_gain = 0x7F,
                .phase = BEAMFORMER_PHASE_0,
            },
            (beamformer_tx_channel_config_t){
                .enabled = true,
                .attenuator = BEAMFORMER_ATTENUATOR_BYPASS,
                .vga_gain = 0x7F,
                .phase = BEAMFORMER_PHASE_0,
            },
            (beamformer_tx_channel_config_t){
                .enabled = true,
                .attenuator = BEAMFORMER_ATTENUATOR_BYPASS,
                .vga_gain = 0x7F,
                .phase = BEAMFORMER_PHASE_0,
            },
        },
};

int main(int argc, char** argv) {
  stdio_init_all();
  led_init();

  // Initialize the beamformer, mixer, and ADC.
  beamformer_init(&g_beamformer_config);
  mixer_init(&g_mixer_config);
  adc_init(&g_adc_config);

  // Enable the mixer.
  mixer_enable();

  // Configure and enable the beamformer.
  beamformer_configure_tx(&g_beamformer_tx_config);
  beamformer_load_tx();

  led_on();
  while (true) {}
  return EXIT_SUCCESS;
}
