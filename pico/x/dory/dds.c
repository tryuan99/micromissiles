#include "pico/x/dory/dds.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "hardware/gpio.h"
#include "pico/common/spi.h"
#include "pico/time.h"

// DDS system clock frequency.
#define DDS_SYSCLK_FREQUENCY 3500000000

// DDS clock frequency.
#define DDS_CLK_FREQUENCY (DDS_SYSCLK_FREQUENCY / 24)

// DDS SPI baudrate.
#define DDS_SPI_BAUDRATE 1000000

// Number of bytes per DDS SPI packet.
#define DDS_NUM_BYTES_PER_SPI_PACKET 4

// DDS SPI command enumeration.
typedef enum {
  DDS_SPI_COMMAND_INVALID = -1,
  DDS_SPI_COMMAND_WRITE = 0,
  DDS_SPI_COMMAND_READ = 1,
} dds_spi_command_e;

// DDS SPI register enumeration.
typedef enum {
  DDS_REGISTER_INVALID = -1,
  DDS_REGISTER_CFR_1 = 0,
  DDS_REGISTER_CFR_2 = 1,
  DDS_REGISTER_CFR_3 = 2,
  DDS_REGISTER_CFR_4 = 3,
  DDS_REGISTER_RAMP_LOWER_LIMIT = 4,
  DDS_REGISTER_RAMP_UPPER_LIMIT = 5,
  DDS_REGISTER_RAMP_RISING_STEP_SIZE = 6,
  DDS_REGISTER_RAMP_FALLING_STEP_SIZE = 7,
  DDS_REGISTER_RAMP_RATE = 8,
  DDS_REGISTER_LOWER_FREQUENCY_JUMP = 9,
  DDS_REGISTER_UPPER_FREQUENCY_JUMP = 10,
  DDS_REGISTER_P0_FTW = 11,
  DDS_REGISTER_P0_PHASE_AMPLITUDE = 12,
  DDS_REGISTER_P1_FTW = 13,
  DDS_REGISTER_P1_PHASE_AMPLITUDE = 14,
  DDS_REGISTER_P2_FTW = 15,
  DDS_REGISTER_P2_PHASE_AMPLITUDE = 16,
  DDS_REGISTER_P3_FTW = 17,
  DDS_REGISTER_P3_PHASE_AMPLITUDE = 18,
  DDS_REGISTER_P4_FTW = 19,
  DDS_REGISTER_P4_PHASE_AMPLITUDE = 20,
  DDS_REGISTER_P5_FTW = 21,
  DDS_REGISTER_P5_PHASE_AMPLITUDE = 22,
  DDS_REGISTER_P6_FTW = 23,
  DDS_REGISTER_P6_PHASE_AMPLITUDE = 24,
  DDS_REGISTER_P7_FTW = 25,
  DDS_REGISTER_P7_PHASE_AMPLITUDE = 26,
  DDS_REGISTER_USR0 = 27,
} dds_spi_register_e;

// DDS digital ramp destination.
typedef enum {
  DDS_RAMP_INVALID = -1,
  DDS_RAMP_FREQUENCY = 0,
  DDS_RAMP_PHASE = 1,
  DDS_RAMP_AMPLITUDE = 2,
} dds_ramp_e;

// DDS SPI packet.
typedef struct {
  // SPI command.
  dds_spi_command_e command;

  // Address.
  dds_spi_register_e address;

  // Data bytes.
  uint8_t data[DDS_NUM_BYTES_PER_SPI_PACKET];
} dds_spi_packet_t;

// DDS SPI communication configuration.
static const spi_comms_config_t g_dds_spi_comms_config = (spi_comms_config_t){
    .baudrate = DDS_SPI_BAUDRATE,
    .data_bits = 8,
    .cpol = SPI_CPOL_1,
    .cpha = SPI_CPHA_1,
    .order = SPI_MSB_FIRST,
};

// DDS configuration.
static dds_config_t g_dds_config;

// DDS SPI packet.
static dds_spi_packet_t g_dds_spi_packet;

// DDS SPI buffer for the instruction byte and the data bytes.
static uint8_t g_dds_spi_buffer[DDS_NUM_BYTES_PER_SPI_PACKET + 1];

// Write to a DDS register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void dds_spi_write_register(void) {
  const uint8_t instruction =
      (g_dds_spi_packet.command << 7) | (g_dds_spi_packet.address & 0x3F);
  memset(g_dds_spi_buffer, 0, DDS_NUM_BYTES_PER_SPI_PACKET + 1);
  g_dds_spi_buffer[0] = instruction;
  memcpy(&g_dds_spi_buffer[1], g_dds_spi_packet.data,
         DDS_NUM_BYTES_PER_SPI_PACKET);
  spi_transmit(&g_dds_config.spi_io_config, g_dds_spi_buffer,
               /*length=*/DDS_NUM_BYTES_PER_SPI_PACKET + 1);
}

// Read from a DDS register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void dds_spi_read_register(void) {
  const uint8_t instruction =
      (g_dds_spi_packet.command << 7) | (g_dds_spi_packet.address & 0x3F);
  spi_transmit(&g_dds_config.spi_io_config, &instruction, /*length=*/1);
  spi_receive(&g_dds_config.spi_io_config, g_dds_spi_packet.data,
              DDS_NUM_BYTES_PER_SPI_PACKET);
}

// Convert the frequency to the register value.
static uint32_t dds_frequency_to_register(const double frequency) {
  return (uint32_t)(frequency / DDS_SYSCLK_FREQUENCY * (1LL << 32));
}

// Convert the time to the register value.
static uint16_t dds_time_to_register(const double step_time) {
  return (uint16_t)(step_time * DDS_SYSCLK_FREQUENCY / 24);
}

// Get the register offset for the given profile.
static uint8_t dds_register_offset_for_profile(const uint8_t profile) {
  return 11 + profile * 2;
}

// Initialize the DDS GPIO pins.
static inline void dds_init_gpios(void) {
  // Reset pin.
  gpio_init(g_dds_config.gpio_rst);
  gpio_set_dir(g_dds_config.gpio_rst, GPIO_OUT);

  // IO update pin.
  gpio_init(g_dds_config.gpio_io_update);
  gpio_set_dir(g_dds_config.gpio_io_update, GPIO_OUT);

  // Profile select 0 pin.
  gpio_init(g_dds_config.gpio_ps0);
  gpio_set_dir(g_dds_config.gpio_ps0, GPIO_OUT);

  // Profile select 1 pin.
  gpio_init(g_dds_config.gpio_ps1);
  gpio_set_dir(g_dds_config.gpio_ps1, GPIO_OUT);

  // Profile select 2 pin.
  gpio_init(g_dds_config.gpio_ps2);
  gpio_set_dir(g_dds_config.gpio_ps2, GPIO_OUT);

  // Ramp control pin.
  gpio_init(g_dds_config.gpio_drctl);
  gpio_set_dir(g_dds_config.gpio_drctl, GPIO_OUT);

  // Ramp hold pin.
  gpio_init(g_dds_config.gpio_drhold);
  gpio_set_dir(g_dds_config.gpio_drhold, GPIO_OUT);

  // Ramp over pin.
  gpio_init(g_dds_config.gpio_drover);

  // Output shift keying pin.
  gpio_init(g_dds_config.gpio_osk);
  gpio_set_dir(g_dds_config.gpio_osk, GPIO_OUT);
}

void dds_init(const dds_config_t* config) {
  g_dds_config = *config;
  spi_inst_init(&g_dds_config.spi_io_config, &g_dds_spi_comms_config);
  dds_init_gpios();

  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = DDS_REGISTER_CFR_1;
  memset(g_dds_spi_packet.data, 0, DDS_NUM_BYTES_PER_SPI_PACKET);
  // Disable external power-down control and configure SDIO as input only.
  g_dds_spi_packet.data[0] = 0x02;
  // Enable OSK enable and external OSK enable.
  g_dds_spi_packet.data[1] = 0x03;
  // Enable sine output.
  g_dds_spi_packet.data[2] = 0x01;
  g_dds_spi_packet.data[3] = 0x00;
  dds_spi_write_register();
}

void dds_reset(void) {
  gpio_put(g_dds_config.gpio_rst, false);
  sleep_us(/*us=*/10);
  gpio_put(g_dds_config.gpio_rst, true);
  sleep_us(/*us=*/10);
}

void dds_io_update(void) {
  gpio_put(g_dds_config.gpio_io_update, true);
  sleep_us(/*us=*/1);
  gpio_put(g_dds_config.gpio_io_update, false);
}

void dds_set_profile(const uint8_t profile) {
  gpio_put(g_dds_config.gpio_ps0, profile & 0x1);
  gpio_put(g_dds_config.gpio_ps1, (profile >> 1) & 0x1);
  gpio_put(g_dds_config.gpio_ps2, (profile >> 2) & 0x1);
}

void dds_configure_cw(const uint8_t profile, const dds_cw_config_t* config) {
  dds_set_profile(profile);

  const dds_spi_register_e frequency_register =
      dds_register_offset_for_profile(profile);
  const uint32_t ftw = dds_frequency_to_register(config->frequency);

  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = frequency_register;
  *(uint32_t*)(g_dds_spi_packet.data) = ftw;
  dds_spi_write_register();

  const dds_spi_register_e phase_amplitude_register = frequency_register + 1;
  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = phase_amplitude_register;
  *(uint16_t*)(g_dds_spi_packet.data) = config->phase;
  *((uint16_t*)(g_dds_spi_packet.data) + 1) = config->amplitude;
  dds_spi_write_register();

  dds_io_update();
}

void dds_configure_fmcw(const uint8_t profile,
                        const dds_fmcw_config_t* config) {
  dds_set_profile(profile);

  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = DDS_REGISTER_CFR_2;
  memset(g_dds_spi_packet.data, 0, DDS_NUM_BYTES_PER_SPI_PACKET);
  g_dds_spi_packet.data[1] = 0x09;
  // Enable the digital ramp with no-dwell high for the frequency.
  g_dds_spi_packet.data[2] = (DDS_RAMP_FREQUENCY << 4) | 0xC;
  dds_spi_write_register();

  const uint32_t start_ftw = dds_frequency_to_register(config->start_frequency);
  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = DDS_REGISTER_RAMP_LOWER_LIMIT;
  *(uint32_t*)(g_dds_spi_packet.data) = start_ftw;
  dds_spi_write_register();

  const uint32_t end_ftw = dds_frequency_to_register(config->end_frequency);
  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = DDS_REGISTER_RAMP_UPPER_LIMIT;
  *(uint32_t*)(g_dds_spi_packet.data) = end_ftw;
  dds_spi_write_register();

  const uint32_t frequency_step =
      dds_frequency_to_register(config->frequency_step);
  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = DDS_REGISTER_RAMP_RISING_STEP_SIZE;
  *(uint32_t*)(g_dds_spi_packet.data) = frequency_step;
  dds_spi_write_register();

  const uint16_t step_time = dds_time_to_register(config->step_time);
  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = DDS_REGISTER_RAMP_RATE;
  *(uint32_t*)(g_dds_spi_packet.data) = step_time;
  dds_spi_write_register();

  const dds_spi_register_e phase_amplitude_register =
      dds_register_offset_for_profile(profile) + 1;
  g_dds_spi_packet.command = DDS_SPI_COMMAND_WRITE;
  g_dds_spi_packet.address = phase_amplitude_register;
  *(uint16_t*)(g_dds_spi_packet.data) = config->phase;
  *((uint16_t*)(g_dds_spi_packet.data) + 1) = config->amplitude;
  dds_spi_write_register();

  dds_io_update();
}

void dds_start_fmcw(void) {
  gpio_put(g_dds_config.gpio_drctl, true);
  sleep_us(/*us=*/1);
  gpio_put(g_dds_config.gpio_drctl, false);
}
