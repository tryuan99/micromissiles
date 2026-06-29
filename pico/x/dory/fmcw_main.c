#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/common/led.h"
#include "pico/stdlib.h"
#include "pico/x/dory/config.h"
#include "pico/x/dory/dds.h"
#include "pico/x/dory/mixer.h"
#include "pico/x/dory/vco.h"
#include "pico/x/dory/vga.h"

// VCO RF frequency.
#define VCO_RF_FREQUENCY 3500000000

// DDS profile.
#define DDS_PROFILE 0

// DDS FMCW configuration for a FMCW signal from 8.5 GHz to 9.5 GHz.
// The ramp increases every 20 ns for a total chirp time of 100 us.
static dds_fmcw_config_t g_dds_fmcw_config = (dds_fmcw_config_t){
    .start_frequency = 750000000,
    .end_frequency = 1250000000,
    .frequency_step = 100000,
    .step_time = 20e-9,
    .amplitude = (1 << 12) - 1,
    .phase = 0,
};

int main(int argc, char** argv) {
  stdio_init_all();
  led_init();

  // Initialize the VCO, DDS, mixer, and VGA.
  vco_init(&g_vco_config, VCO_PFD_FREQUENCY_25_MHZ, VCO_RF_FREQUENCY);
  g_dds_config.mode = DDS_MODE_FMCW;
  dds_init(&g_dds_config);
  mixer_init(&g_mixer_config);
  vga_init(&g_vga_config);

  // Enable the mixer and VGA.
  mixer_enable();
  vga_set_gain_attenuation(/*gain_attenuation=*/0);

  // Configure the VCO.
  vco_set_output_power(VCO_OUTPUT_POWER_FIVE_DBM,
                       /*aux_output_power=*/VCO_OUTPUT_POWER_FIVE_DBM);
  vco_enable();
  vco_configure();
  vco_rf_enable();

  // Configure the DDS.
  dds_configure_fmcw(DDS_PROFILE, &g_dds_fmcw_config);
  dds_output_enable();

  led_on();
  while (true) {
#if PICO_CONTROLLER
    dds_start_fmcw();
    sleep_us(/*us=*/100);
#endif  // PICO_CONTROLLER
  }
  return EXIT_SUCCESS;
}
