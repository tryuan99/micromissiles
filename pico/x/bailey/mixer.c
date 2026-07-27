#include "pico/x/bailey/mixer.h"

#include <stdbool.h>
#include <string.h>

#include "hardware/gpio.h"
#include "pico/common/spi.h"
#include "pico/time.h"

// Mixer SPI baudrate.
#define MIXER_SPI_BAUDRATE 1000000

// Number of bytes per mixer SPI packet.
#define MIXER_NUM_BYTES_PER_SPI_PACKET 2

// Mixer SPI command enumeration.
typedef enum {
  MIXER_SPI_COMMAND_INVALID = -1,
  MIXER_SPI_COMMAND_WRITE = 0,
  MIXER_SPI_COMMAND_READ = 1,
} mixer_spi_command_e;

// Mixer divider A enumeration.
typedef enum {
  MIXER_DIV_A_INVALID = -1,
  MIXER_DIV_A_ONE = 0,
  MIXER_DIV_A_TWO = 1,
  MIXER_DIV_A_FOUR = 3,
  MIXER_DIV_A_EIGHT = 7,
  MIXER_DIV_A_SIXTEEN = 2,
} mixer_div_a_divider_e;

// Mixer LO polyphase mode 1 enumeration.
typedef enum {
  MIXER_LO_POLYPHASE_MODE_1_INVALID = -1,
  MIXER_LO_POLYPHASE_MODE_1_INTERNAL_POLY = 0,
  MIXER_LO_POLYPHASE_MODE_1_EXTERNAL = 15,
  MIXER_LO_POLYPHASE_MODE_1_INTERNAL_DIV2 = 19,
} mixer_lo_polyphase_mode_1_e;

// Mixer LO polyphase mode 2 enumeration.
typedef enum {
  MIXER_LO_POLYPHASE_MODE_2_INVALID = -1,
  MIXER_LO_POLYPHASE_MODE_2_POLY = 0,
  MIXER_LO_POLYPHASE_MODE_2_DIV2 = 11,
} mixer_lo_polyphase_mode_2_e;

// Mixer state machine clock driver enumeration.
typedef enum {
  MIXER_STATE_MACHINE_CLOCK_DRIVER_INVALID = -1,
  MIXER_STATE_MACHINE_CLOCK_DRIVER_INTERNAL = 0,
  MIXER_STATE_MACHINE_CLOCK_DRIVER_EXTERNAL = 3,
} mixer_state_machine_clock_driver_e;

// Mixer state machine clock source enumeration.
typedef enum {
  MIXER_STATE_MACHINE_CLOCK_SOURCE_INVALID = -1,
  MIXER_STATE_MACHINE_CLOCK_SOURCE_INTERNAL = 0,
  MIXER_STATE_MACHINE_CLOCK_SOURCE_EXTERNAL = 1,
} mixer_state_machine_clock_source_e;

// Mixer LO quadrature driver enumeration.
typedef enum {
  MIXER_LO_QUADRATURE_DRIVER_INVALID = -1,
  MIXER_LO_QUADRATURE_DRIVER_INTERNAL_POLY = 0,
  MIXER_LO_QUADRATURE_DRIVER_INTERNAL_DIV2 = 1,
  MIXER_LO_QUADRATURE_DRIVER_EXTERNAL = 3,
} mixer_lo_quadrature_driver_e;

// Mixer LO termination enumeration.
typedef enum {
  MIXER_LO_TERMINATION_INVALID = -1,
  MIXER_LO_TERMINATION_200_OHMS = 1,
  MIXER_LO_TERMINATION_100_OHMS = 3,
} mixer_lo_termination_e;

// Mixer multiplexer output select enumeration.
typedef enum {
  MIXER_MUXOUT_SELECT_INVALID = -1,
  MIXER_MUXOUT_SELECT_READBACK = 0,
  MIXER_MUXOUT_SELECT_LOCK_DETECT = 1,
} mixer_muxout_select_e;

// Mixer PLL reset enumeration.
typedef enum {
  MIXER_PLL_RESET_INVALID = -1,
  MIXER_PLL_RESET_NONE = 0,
  MIXER_PLL_RESET_TRIGGER = 1,
} mixer_pll_reset_e;

// Mixer PLL power enumeration.
typedef enum {
  MIXER_PLL_POWER_INVALID = -1,
  MIXER_PLL_POWER_UP = 0,
  MIXER_PLL_POWER_DOWN = 1,
} mixer_pll_power_e;

// Mixer SPI packet.
typedef struct {
  // SPI command.
  mixer_spi_command_e command;

  // Register index.
  uint8_t address;

  // Data bytes.
  uint8_t data[MIXER_NUM_BYTES_PER_SPI_PACKET];
} mixer_spi_packet_t;

// Mixer SPI communication configuration.
static const spi_comms_config_t g_mixer_spi_comms_config = (spi_comms_config_t){
    .baudrate = MIXER_SPI_BAUDRATE,
    .data_bits = 8,
    .cpol = SPI_CPOL_0,
    .cpha = SPI_CPHA_0,
    .order = SPI_MSB_FIRST,
};

// Mixer configuration.
static mixer_config_t g_mixer_config;

// Mixer SPI packet.
static mixer_spi_packet_t g_mixer_spi_packet;

// Mixer SPI buffer for the instruction byte and the data bytes.
static uint8_t g_mixer_spi_buffer[MIXER_NUM_BYTES_PER_SPI_PACKET + 1];

// Write to a mixer register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void mixer_spi_write_register(void) {
  const uint8_t instruction =
      (g_mixer_spi_packet.command << 7) | (g_mixer_spi_packet.address & 0x7F);
  memset(g_mixer_spi_buffer, 0, MIXER_NUM_BYTES_PER_SPI_PACKET + 1);
  g_mixer_spi_buffer[0] = instruction;
  memcpy(&g_mixer_spi_buffer[1], g_mixer_spi_packet.data,
         MIXER_NUM_BYTES_PER_SPI_PACKET);
  spi_transmit(&g_mixer_config.spi_io_config, g_mixer_spi_buffer,
               /*length=*/MIXER_NUM_BYTES_PER_SPI_PACKET + 1);
}

// Read from a mixer register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void mixer_spi_read_register(void) {
  const uint8_t instruction =
      (g_mixer_spi_packet.command << 7) | (g_mixer_spi_packet.address & 0x7F);
  spi_transmit(&g_mixer_config.spi_io_config, &instruction, /*length=*/1);
  spi_receive(&g_mixer_config.spi_io_config, g_mixer_spi_packet.data,
              MIXER_NUM_BYTES_PER_SPI_PACKET);
}

// Perform the initial power-up sequence.
static inline void mixer_power_up(void) {
  // Recommended power-up sequence:
  //  1. Program a RESET, which is self-clearing.
  //  2. Program register R127 to value 0x007F0003.
  //  3. Program register R6 to value 0x00060100.
  //  4. Program register R127 to R0 in reverse order.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 0;
  g_mixer_spi_packet.data[0] = 0x00;
  g_mixer_spi_packet.data[1] = (MIXER_PLL_RESET_TRIGGER & 0x1) << 1;
  mixer_spi_write_register();

  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 127;
  g_mixer_spi_packet.data[0] = 0x00;
  g_mixer_spi_packet.data[1] = 0x03;
  mixer_spi_write_register();

  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 6;
  g_mixer_spi_packet.data[0] = 0x01;
  g_mixer_spi_packet.data[1] = 0x00;
  mixer_spi_write_register();

  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 127;
  g_mixer_spi_packet.data[0] = 0x00;
  g_mixer_spi_packet.data[1] = 0x00;
  mixer_spi_write_register();
}

// Initialize the external LO clock.
static inline void mixer_init_external_lo(void) {
  // Set the differential LO termination to 100 Ohms.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 123;
  g_mixer_spi_packet.data[0] = 0x00;
  g_mixer_spi_packet.data[1] = MIXER_LO_TERMINATION_100_OHMS & 0x3;
  mixer_spi_write_register();

  // Set the divider for the DC offset correction.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 84;
  g_mixer_spi_packet.data[0] = (6 >> 2) & 0xFF;
  g_mixer_spi_packet.data[1] = (6 & 0x3) << 6;
  mixer_spi_write_register();

  // Set the dividers for the state machine clock.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 82;
  g_mixer_spi_packet.data[0] = 0x06;
  g_mixer_spi_packet.data[1] = ((MIXER_DIV_A_SIXTEEN & 0x3) << 3) | (3 & 0x3);
  mixer_spi_write_register();

  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 81;
  g_mixer_spi_packet.data[0] = MIXER_LO_POLYPHASE_MODE_1_EXTERNAL & 0xF;
  g_mixer_spi_packet.data[1] =
      ((MIXER_STATE_MACHINE_CLOCK_DRIVER_EXTERNAL & 0x3) << 6) |
      ((MIXER_LO_QUADRATURE_DRIVER_EXTERNAL & 0x3) << 4) |
      ((MIXER_LO_QUADRATURE_DRIVER_EXTERNAL & 0x3) << 1) |
      (MIXER_STATE_MACHINE_CLOCK_SOURCE_EXTERNAL & 0x1);
  mixer_spi_write_register();

  // Set the LO multiplexer.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 80;
  g_mixer_spi_packet.data[0] = 0x00;
  g_mixer_spi_packet.data[1] = 0x22;
  mixer_spi_write_register();

  // Enable lock detect on the multiplexer output pin and power down the PLL.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 0;
  g_mixer_spi_packet.data[0] = 0x00;
  g_mixer_spi_packet.data[1] = ((MIXER_MUXOUT_SELECT_LOCK_DETECT & 0x1) << 2) |
                               (MIXER_PLL_POWER_DOWN & 0x1);
  mixer_spi_write_register();

  // Wait 100 us before performing DC offset correction.
  sleep_us(/*us=*/100);

  // Reset the DC offset correction FSM.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 126;
  g_mixer_spi_packet.data[0] = 0x01;
  g_mixer_spi_packet.data[1] = 0x00;
  mixer_spi_write_register();

  // Enable offset calibration for I and Q channels.
  g_mixer_spi_packet.command = MIXER_SPI_COMMAND_WRITE;
  g_mixer_spi_packet.address = 84;
  g_mixer_spi_packet.data[0] = (6 >> 2) & 0xFF;
  g_mixer_spi_packet.data[1] = ((6 & 0x3) << 6) | 0x3;
  mixer_spi_write_register();
}

void mixer_init(const mixer_config_t* config) {
  g_mixer_config = *config;
  spi_inst_init(&g_mixer_config.spi_io_config, &g_mixer_spi_comms_config);

  // Initialize the enable pin.
  gpio_init(g_mixer_config.gpio_enable);
  gpio_set_dir(g_mixer_config.gpio_enable, GPIO_OUT);

  // Initialize the multiplexer output pin.
  gpio_init(g_mixer_config.gpio_muxout);

  mixer_power_up();
  mixer_init_external_lo();
}

void mixer_enable(void) { gpio_put(g_mixer_config.gpio_enable, true); }

void mixer_disable(void) { gpio_put(g_mixer_config.gpio_enable, false); }
