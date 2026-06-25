#include "pico/x/dory/vco.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "hardware/gpio.h"
#include "pico/common/spi.h"

// VCO SPI baudrate.
#define VCO_SPI_BAUDRATE 1000000

// Number of VCO registers.
#define VCO_NUM_REGISTERS 6

// The VCO reference frequency is fixed at 50 MHz.
#define VCO_REFERENCE_FREQUENCY 50000000

// Fixed VCO frequency modulus.
#define VCO_FREQUENCY_MODULUS 2500

// VCO prescaler enumeration.
typedef enum {
  VCO_FREQUENCY_PRESCALAR_INVALID = -1,
  VCO_FREQUENCY_PRESCALAR_FOUR_FIVE = 0,
  VCO_FREQUENCY_PRESCALAR_EIGHT_NINE = 1,
} vco_frequency_prescaler_e;

// VCO mode enumeration.
typedef enum {
  VCO_MODE_INVALID = -1,
  VCO_MODE_LOW_NOISE = 0,
  VCO_MODE_LOW_SPUR = 3,
} vco_mode_e;

// VCO multiplexer output enumeration..
typedef enum {
  VCO_MULTIPLEXER_OUTPUT_INVALID = -1,
  VCO_MULTIPLEXER_OUTPUT_THREE_STATE_OUTPUT = 0,
  VCO_MULTIPLEXER_OUTPUT_DVDD = 1,
  VCO_MULTIPLEXER_OUTPUT_DGND = 2,
  VCO_MULTIPLEXER_OUTPUT_R_DIVIDER_OUTPUT = 3,
  VCO_MULTIPLEXER_OUTPUT_N_DIVIDER_OUTPUT = 4,
  VCO_MULTIPLEXER_OUTPUT_ANALOG_LOCK_DETECT = 5,
  VCO_MULTIPLEXER_OUTPUT_DIGITAL_LOCK_DETECT = 6,
} vco_multiplexer_output_e;

// VCO charge pump current setting enumeration.
typedef enum {
  VCO_CHARGE_PUMP_CURRENT_INVALID = -1,
  VCO_CHARGE_PUMP_CURRENT_0_31 = 0,
  VCO_CHARGE_PUMP_CURRENT_0_63 = 1,
  VCO_CHARGE_PUMP_CURRENT_0_94 = 2,
  VCO_CHARGE_PUMP_CURRENT_1_25 = 3,
  VCO_CHARGE_PUMP_CURRENT_1_56 = 4,
  VCO_CHARGE_PUMP_CURRENT_1_88 = 5,
  VCO_CHARGE_PUMP_CURRENT_2_19 = 6,
  VCO_CHARGE_PUMP_CURRENT_2_50 = 7,
  VCO_CHARGE_PUMP_CURRENT_2_81 = 8,
  VCO_CHARGE_PUMP_CURRENT_3_13 = 9,
  VCO_CHARGE_PUMP_CURRENT_3_44 = 10,
  VCO_CHARGE_PUMP_CURRENT_3_75 = 11,
  VCO_CHARGE_PUMP_CURRENT_4_06 = 12,
  VCO_CHARGE_PUMP_CURRENT_4_38 = 13,
  VCO_CHARGE_PUMP_CURRENT_4_69 = 14,
  VCO_CHARGE_PUMP_CURRENT_5_00 = 15,
} vco_charge_pump_current_e;

// VCO auxiliary output select enumeration.
typedef enum {
  VCO_AUX_OUTPUT_INVALID = -1,
  VCO_AUX_OUTPUT_DIVIDED = 0,
  VCO_AUX_OUTPUT_FUNDAMENTAL = 1,
} vco_aux_output_select_e;

// VCO lock detect function enumeration.
typedef enum {
  VCO_LOCK_DETECT_INVALID = -1,
  VCO_LOCK_DETECT_FRAC_N = 0,
  VCO_LOCK_DETECT_INT_N = 1,
} vco_lock_detect_e;

// VCO lock detect pin operation enumeration.
typedef enum {
  VCO_LOCK_DETECT_PIN_INVALID = -1,
  VCO_LOCK_DETECT_PIN_LOW = 0,
  VCO_LOCK_DETECT_PIN_DIGITAL_LOCK_DETECT = 1,
  VCO_LOCK_DETECT_PIN_LOW_2 = 2,
  VCO_LOCK_DETECT_PIN_HIGH = 3,
} vco_lock_detect_pin_e;

// VCO static configuration struct.
typedef struct {
  // VCO mode.
  vco_mode_e mode;

  // Multiplexer output.
  vco_multiplexer_output_e multiplexer_output;

  // Charge pump current setting.
  vco_charge_pump_current_e charge_pump_current;

  // RF output enable.
  bool rf_output_enable;

  // Auxiliary output enable.
  bool aux_output_enable;

  // Auxiliary output select.
  vco_aux_output_select_e aux_output_select;

  // Lock detect pin.
  vco_lock_detect_pin_e lock_detect_pin;
} vco_static_config_t;

// VCO PFD configuration struct.
typedef struct {
  // Doubler bit.
  uint8_t D;

  // Divide-by-2 bit.
  uint8_t T;

  // Preset divide ratio of the binary 10-bit programmable reference counter.
  uint16_t R;
} vco_pfd_config_t;

// VCO frequency configuration struct.
typedef struct {
  // 16-bit integer divide ratio.
  uint16_t integer;

  // 12-bit fractional modulus.
  uint16_t modulus;

  // 12-bit numerator of the fractional division.
  uint16_t fraction;

  // Prescaler.
  vco_frequency_prescaler_e prescaler;

  // 12-bit phase value from 0 degrees to 360 degrees.
  uint16_t phase;

  // Lock detect function.
  vco_lock_detect_e lock_detect;
} vco_frequency_config_t;

// VCO output configuration struct.
typedef struct {
  // Output power.
  vco_output_power_e output_power;

  // Auxiliary output power.
  vco_output_power_e aux_output_power;
} vco_output_config_t;

// VCO SPI communication configuration.
static const spi_comms_config_t g_vco_spi_comms_config = (spi_comms_config_t){
    .baudrate = VCO_SPI_BAUDRATE,
    .data_bits = 8,
    .cpol = SPI_CPOL_1,
    .cpha = SPI_CPHA_1,
    .order = SPI_MSB_FIRST,
};

// VCO configuration.
static vco_config_t g_vco_config;

// VCO register data.
static vco_static_config_t g_vco_static_config = (vco_static_config_t){
    .mode = VCO_MODE_LOW_NOISE,
    .multiplexer_output = VCO_MULTIPLEXER_OUTPUT_THREE_STATE_OUTPUT,
    .charge_pump_current = VCO_CHARGE_PUMP_CURRENT_2_50,
    .rf_output_enable = true,
    .aux_output_enable = true,
    .aux_output_select = VCO_AUX_OUTPUT_FUNDAMENTAL,
    .lock_detect_pin = VCO_LOCK_DETECT_PIN_DIGITAL_LOCK_DETECT,
};

// VCO PFD configuration.
static vco_pfd_config_t g_vco_pfd_config;

// VCO frequency configuration.
static vco_frequency_config_t g_vco_frequency_config;

// VCO output configuration.
static vco_output_config_t g_vco_output_config;

// VCO register data.
static uint32_t g_vco_registers[VCO_NUM_REGISTERS];

// Get the PFD frequency.
static inline double vco_get_pfd_frequency(
    const vco_pfd_frequency_e pfd_frequency) {
  switch (pfd_frequency) {
    case VCO_PFD_FREQUENCY_25_MHZ: {
      return 25000000;
    }
    default: {
      printf("Failed to get PFD frequency.");
      return 0;
    }
  }
}

// Get the PFD configuration.
static inline vco_pfd_config_t vco_get_pfd_config(
    const vco_pfd_frequency_e pfd_frequency) {
  switch (pfd_frequency) {
    case VCO_PFD_FREQUENCY_25_MHZ: {
      return (vco_pfd_config_t){
          .D = 0,
          .R = 0,
          .T = 1,
      };
    }
    default: {
      printf("Failed to get PFD frequency.");
      return (vco_pfd_config_t){0};
    }
  }
}

// Get the frequency configuration.
static inline vco_frequency_config_t vco_get_frequency_config(
    const double rf_frequency, const double pfd_frequency) {
  vco_frequency_config_t frequency_config =
      (vco_frequency_config_t){.modulus = VCO_FREQUENCY_MODULUS};
  frequency_config.integer = rf_frequency / pfd_frequency;
  const double remainder_frequency =
      rf_frequency - frequency_config.integer * pfd_frequency;
  frequency_config.fraction =
      ((uint16_t)(remainder_frequency * VCO_FREQUENCY_MODULUS /
                  pfd_frequency)) &
      0xFFF;
  // If the frequency is greater than 3 GHz, the prescaler must be set to 8/9.
  if (rf_frequency > 3000000000) {
    frequency_config.prescaler = VCO_FREQUENCY_PRESCALAR_EIGHT_NINE;
    // The minimum INT value is 23.
    if (frequency_config.integer < 23) {
      printf("When the prescaler is set to 4/5, the minimum INT is 23: %u.",
             frequency_config.integer);
    }
  } else {
    frequency_config.prescaler = VCO_FREQUENCY_PRESCALAR_FOUR_FIVE;
    // The minimum INT value is 75.
    if (frequency_config.integer < 75) {
      printf("When the prescaler is set to 8/9, the minimum INT is 75: %u.",
             frequency_config.integer);
    }
  }
  // A phase value of 1 is recommended.
  frequency_config.phase = 1 & 0xFFF;
  return frequency_config;
}

// Initialize the VCO GPIO pins.
static inline void vco_init_gpios(void) {
  // Enable pin.
  gpio_init(g_vco_config.gpio_enable);
  gpio_set_dir(g_vco_config.gpio_enable, GPIO_OUT);

  // RF enable pin.
  gpio_init(g_vco_config.gpio_rf_enable);
  gpio_set_dir(g_vco_config.gpio_rf_enable, GPIO_OUT);

  // Multiplexer output pin.
  gpio_init(g_vco_config.gpio_muxout);

  // Lock detect pin.
  gpio_init(g_vco_config.gpio_ld);
}

// Initialize the VCO registers.
static inline void vco_init_registers(void) {
  // Register 0.
  uint8_t* data = (uint8_t*)&g_vco_registers[0];
  data[0] = (g_vco_frequency_config.integer >> 9) & 0x7F;
  data[1] = (g_vco_frequency_config.integer >> 1) & 0xFF;
  data[2] = ((g_vco_frequency_config.integer & 0x1) << 7) |
            ((g_vco_frequency_config.fraction >> 5) & 0x7F);
  data[3] = ((g_vco_frequency_config.fraction & 0x1F) << 3) | (0 & 0x7);

  // Register 1.
  data = (uint8_t*)&g_vco_registers[1];
  data[0] = ((g_vco_frequency_config.prescaler & 0x1) << 3) |
            ((g_vco_frequency_config.phase >> 9) & 0x7);
  data[1] = (g_vco_frequency_config.phase >> 1) & 0xFF;
  data[2] = ((g_vco_frequency_config.phase & 0x1) << 7) |
            ((g_vco_frequency_config.modulus >> 5) & 0x7F);
  data[3] = ((g_vco_frequency_config.modulus & 0x1F) << 3) | (1 & 0x7);

  // Register 2.
  data = (uint8_t*)&g_vco_registers[2];
  data[0] = ((g_vco_static_config.mode & 0x3) << 5) |
            ((g_vco_static_config.multiplexer_output & 0x7) << 2) |
            ((g_vco_pfd_config.D & 0x1) << 1) | (g_vco_pfd_config.T & 0x1);
  data[1] = (g_vco_pfd_config.R >> 2) & 0xFF;
  data[2] = ((g_vco_pfd_config.R & 0x3) << 6) |
            ((g_vco_static_config.charge_pump_current & 0xF) << 1) |
            (g_vco_frequency_config.lock_detect & 0x1);
  data[3] = 2 & 0x7;

  // Register 3.
  data = (uint8_t*)&g_vco_registers[3];
  data[0] = 0;
  data[1] = 0;
  data[2] = 0;
  data[3] = 3 & 0x7;

  // Register 4.
  data = (uint8_t*)&g_vco_registers[4];
  data[0] = 0;
  data[1] = 0;
  data[2] = ((g_vco_static_config.aux_output_select & 0x1) << 1) |
            (g_vco_static_config.aux_output_enable & 0x1);
  data[3] = ((g_vco_output_config.aux_output_power & 0x3) << 6) |
            ((g_vco_static_config.rf_output_enable & 0x1) << 5) |
            ((g_vco_output_config.output_power & 0x3) << 3) | (4 & 0x7);

  // Register 5.
  data = (uint8_t*)&g_vco_registers[5];
  data[0] = 0;
  data[1] = ((g_vco_static_config.lock_detect_pin & 0x3) << 6) | (3 << 3);
  data[2] = 0;
  data[3] = 5 & 0x7;
}

void vco_init(const vco_config_t* config) {
  g_vco_config = *config;
  spi_inst_init(&g_vco_config.spi_io_config, &g_vco_spi_comms_config);
  vco_init_gpios();
}

void vco_set_frequencies(const vco_pfd_frequency_e pfd_frequency,
                         const double rf_frequency) {
  g_vco_pfd_config = vco_get_pfd_config(pfd_frequency);
  g_vco_frequency_config = vco_get_frequency_config(
      rf_frequency, vco_get_pfd_frequency(pfd_frequency));
  if (g_vco_frequency_config.fraction == 0) {
    g_vco_frequency_config.lock_detect = VCO_LOCK_DETECT_INT_N;
  }
}

void vco_set_output_power(const vco_output_power_e output_power,
                          const vco_output_power_e aux_output_power) {
  g_vco_output_config = (vco_output_config_t){
      .output_power = output_power,
      .aux_output_power = aux_output_power,
  };
}

void vco_configure(void) {
  vco_init_registers();

  // Transmit the VCO registers from register 5 down to register 0.
  spi_inst_init(&g_vco_config.spi_io_config, &g_vco_spi_comms_config);
  for (size_t i = 0; i < VCO_NUM_REGISTERS; ++i) {
    int num_tx_bytes = spi_transmit(&g_vco_config.spi_io_config,
                                    &g_vco_registers[VCO_NUM_REGISTERS - 1 - i],
                                    /*length=*/sizeof(uint32_t));
    if (num_tx_bytes != sizeof(uint32_t)) {
      printf("Failed to transmit VCO register %u.\n", i);
    }
  }
}

void vco_enable(void) { gpio_put(g_vco_config.gpio_enable, true); }

void vco_disable(void) { gpio_put(g_vco_config.gpio_enable, false); }

void vco_rf_enable(void) { gpio_put(g_vco_config.gpio_rf_enable, true); }

void vco_rf_disable(void) { gpio_put(g_vco_config.gpio_rf_enable, false); }

bool vco_locked(void) { return gpio_get(g_vco_config.gpio_ld); }
