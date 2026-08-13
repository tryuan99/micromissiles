#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/common/led.h"
#include "pico/stdlib.h"
#include "pico/x/dory/attenuator.h"
#include "pico/x/dory/config.h"
#include "pico/x/dory/dds.h"
#include "pico/x/dory/mixer.h"
#include "pico/x/dory/vco.h"

// VCO RF frequency.
#define VCO_RF_FREQUENCY 3500000000

// DDS profile.
#define DDS_PROFILE 0

// Maximum chirp time in microseconds.
#define MAX_CHIRP_TIME_US 1000

// DDS FMCW configuration for a FMCW signal from 8.5 GHz to 9.5 GHz.
// The hardware quantizes the ramp step interval to 3 SYNC_CLK periods
// (~20.571 ns), and the driver scales the frequency step to preserve the
// requested chirp slope of 5 MHz/us for a total chirp time of 100 us.
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

  // Initialize the VCO.
  vco_init(&g_vco_config, VCO_PFD_FREQUENCY_25_MHZ, VCO_RF_FREQUENCY);
  vco_set_output_power(VCO_OUTPUT_POWER_FIVE_DBM,
                       /*aux_output_power=*/VCO_OUTPUT_POWER_FIVE_DBM);
  vco_enable();
  vco_configure();
  vco_rf_enable();
  while (!vco_locked()) {}

  // Initialize the mixer and the attenuator.
  mixer_init(&g_mixer_config);
  mixer_enable();
  attenuator_init(&g_attenuator_config);
  attenuator_set_gain_attenuation(/*gain_attenuation=*/8);

  // Initialize the DDS.
  g_dds_config.mode = DDS_MODE_FMCW;
  dds_init(&g_dds_config);
  dds_configure_fmcw(DDS_PROFILE, &g_dds_fmcw_config);
  dds_output_enable();

  led_on();
  while (true) {
#ifdef CONTROLLER_PICO
    // Enable the output before triggering the chirp.
    dds_output_enable();
    dds_start_fmcw();

    // Wait for the ramp to complete with a bounded wait time.
    const uint64_t deadline_us = time_us_64() + MAX_CHIRP_TIME_US;
    while (!dds_ramp_over() && time_us_64() < deadline_us) {
      sleep_us(/*us=*/1);
    }

    // Disable the output to blank the CW output emitted while the digital
    // ramp generator is parked at the lower limit between chirps.
    dds_output_disable();
    sleep_us(/*us=*/5);
#endif  // CONTROLLER_PICO
  }
  return EXIT_SUCCESS;
}
