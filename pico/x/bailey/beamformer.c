#include "pico/x/bailey/beamformer.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "hardware/gpio.h"
#include "pico/common/spi.h"
#include "pico/time.h"

// Beamformer SPI baudrate.
#define BEAMFORMER_SPI_BAUDRATE 1000000

// Beamformer SPI address.
#define BEAMFORMER_SPI_ADDRESS 0

// Number of bytes in the address of a beamformer SPI packet.
#define BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET 2

// Number of bytes per beamformer SPI packet.
#define BEAMFORMER_NUM_BYTES_PER_SPI_PACKET 1

// DDS SPI command enumeration.
typedef enum {
  BEAMFORMER_SPI_COMMAND_INVALID = -1,
  BEAMFORMER_SPI_COMMAND_WRITE = 0,
  BEAMFORMER_SPI_COMMAND_READ = 1,
} beamformer_spi_command_e;

// DDS SPI register enumeration.
typedef enum {
  BEAMFORMER_REGISTER_INVALID = -1,
  BEAMFORMER_REGISTER_INTERFACE_CONFIG_A = 0x000,
  BEAMFORMER_REGISTER_INTERFACE_CONFIG_B = 0x001,
  BEAMFORMER_REGISTER_CHIP_TYPE = 0x003,
  BEAMFORMER_REGISTER_PRODUCT_ID_H = 0x004,
  BEAMFORMER_REGISTER_PRODUCT_ID_L = 0x005,
  BEAMFORMER_REGISTER_SCRATCH_PAD = 0x00A,
  BEAMFORMER_REGISTER_SPI_REV = 0x00B,
  BEAMFORMER_REGISTER_VENDOR_ID_H = 0x00C,
  BEAMFORMER_REGISTER_VENDOR_ID_L = 0x00D,
  BEAMFORMER_REGISTER_TRANSFER_REG = 0x00F,
  BEAMFORMER_REGISTER_CH1_RX_GAIN = 0x010,
  BEAMFORMER_REGISTER_CH2_RX_GAIN = 0x011,
  BEAMFORMER_REGISTER_CH3_RX_GAIN = 0x012,
  BEAMFORMER_REGISTER_CH4_RX_GAIN = 0x013,
  BEAMFORMER_REGISTER_CH1_RX_PHASE_I = 0x014,
  BEAMFORMER_REGISTER_CH1_RX_PHASE_Q = 0x015,
  BEAMFORMER_REGISTER_CH2_RX_PHASE_I = 0x016,
  BEAMFORMER_REGISTER_CH2_RX_PHASE_Q = 0x017,
  BEAMFORMER_REGISTER_CH3_RX_PHASE_I = 0x018,
  BEAMFORMER_REGISTER_CH3_RX_PHASE_Q = 0x019,
  BEAMFORMER_REGISTER_CH4_RX_PHASE_I = 0x01A,
  BEAMFORMER_REGISTER_CH4_RX_PHASE_Q = 0x01B,
  BEAMFORMER_REGISTER_CH1_TX_GAIN = 0x01C,
  BEAMFORMER_REGISTER_CH2_TX_GAIN = 0x01D,
  BEAMFORMER_REGISTER_CH3_TX_GAIN = 0x01E,
  BEAMFORMER_REGISTER_CH4_TX_GAIN = 0x01F,
  BEAMFORMER_REGISTER_CH1_TX_PHASE_I = 0x020,
  BEAMFORMER_REGISTER_CH1_TX_PHASE_Q = 0x021,
  BEAMFORMER_REGISTER_CH2_TX_PHASE_I = 0x022,
  BEAMFORMER_REGISTER_CH2_TX_PHASE_Q = 0x023,
  BEAMFORMER_REGISTER_CH3_TX_PHASE_I = 0x024,
  BEAMFORMER_REGISTER_CH3_TX_PHASE_Q = 0x025,
  BEAMFORMER_REGISTER_CH4_TX_PHASE_I = 0x026,
  BEAMFORMER_REGISTER_CH4_TX_PHASE_Q = 0x027,
  BEAMFORMER_REGISTER_LD_WRK_REGS = 0x028,
  BEAMFORMER_REGISTER_CH1_PA_BIAS_ON = 0x029,
  BEAMFORMER_REGISTER_CH2_PA_BIAS_ON = 0x02A,
  BEAMFORMER_REGISTER_CH3_PA_BIAS_ON = 0x02B,
  BEAMFORMER_REGISTER_CH4_PA_BIAS_ON = 0x02C,
  BEAMFORMER_REGISTER_LNA_BIAS_ON = 0x02D,
  BEAMFORMER_REGISTER_RX_ENABLES = 0x02E,
  BEAMFORMER_REGISTER_TX_ENABLES = 0x02F,
  BEAMFORMER_REGISTER_MISC_ENABLES = 0x030,
  BEAMFORMER_REGISTER_SW_CTRL = 0x031,
  BEAMFORMER_REGISTER_ADC_CTRL = 0x032,
  BEAMFORMER_REGISTER_ADC_OUTPUT = 0x033,
  BEAMFORMER_REGISTER_BIAS_CURRENT_RX_LNA = 0x034,
  BEAMFORMER_REGISTER_BIAS_CURRENT_RX = 0x035,
  BEAMFORMER_REGISTER_BIAS_CURRENT_TX = 0x036,
  BEAMFORMER_REGISTER_BIAS_CURRENT_TX_DRV = 0x037,
  BEAMFORMER_REGISTER_MEM_CTRL = 0x038,
  BEAMFORMER_REGISTER_RX_CHX_MEM = 0x039,
  BEAMFORMER_REGISTER_TX_CHX_MEM = 0x03A,
  BEAMFORMER_REGISTER_RX_CH1_MEM = 0x03D,
  BEAMFORMER_REGISTER_RX_CH2_MEM = 0x03E,
  BEAMFORMER_REGISTER_RX_CH3_MEM = 0x03F,
  BEAMFORMER_REGISTER_RX_CH4_MEM = 0x040,
  BEAMFORMER_REGISTER_TX_CH1_MEM = 0x041,
  BEAMFORMER_REGISTER_TX_CH2_MEM = 0x042,
  BEAMFORMER_REGISTER_TX_CH3_MEM = 0x043,
  BEAMFORMER_REGISTER_TX_CH4_MEM = 0x044,
  BEAMFORMER_REGISTER_REV_ID = 0x045,
  BEAMFORMER_REGISTER_CH1_PA_BIAS_OFF = 0x046,
  BEAMFORMER_REGISTER_CH2_PA_BIAS_OFF = 0x047,
  BEAMFORMER_REGISTER_CH3_PA_BIAS_OFF = 0x048,
  BEAMFORMER_REGISTER_CH4_PA_BIAS_OFF = 0x049,
  BEAMFORMER_REGISTER_LNA_BIAS_OFF = 0x04A,
  BEAMFORMER_REGISTER_TX_TO_RX_DELAY_CTRL = 0x04B,
  BEAMFORMER_REGISTER_RX_TO_TX_DELAY_CTRL = 0x04C,
  BEAMFORMER_REGISTER_TX_BEAM_STEP_START = 0x04D,
  BEAMFORMER_REGISTER_TX_BEAM_STEP_STOP = 0x04E,
  BEAMFORMER_REGISTER_RX_BEAM_STEP_START = 0x04F,
  BEAMFORMER_REGISTER_RX_BEAM_STEP_STOP = 0x050,
  BEAMFORMER_REGISTER_RX_BIAS_RAM_CTL = 0x051,
  BEAMFORMER_REGISTER_TX_BIAS_RAM_CTL = 0x052,
  BEAMFORMER_REGISTER_LDO_TRIM_CTL_0 = 0x400,
  BEAMFORMER_REGISTER_LDO_TRIM_CTL_1 = 0x401,
} beamformer_register_e;

// Beamformer SPI transmit/receive control enumeration.
typedef enum {
  BEAMFORMER_SPI_TR_INVALID = -1,
  BEAMFORMER_SPI_TR_RX = 0,
  BEAMFORMER_SPI_TR_TX = 1,
} beamformer_spi_tr_e;

// Beamformer transmit/receive source enumeration.
typedef enum {
  BEAMFORMER_TR_SOURCE_INVALID = -1,
  BEAMFORMER_TR_SOURCE_SPI = 0,
  BEAMFORMER_TR_SOURCE_PIN = 1,
} beamformer_spi_tr_source_e;

// DDS SPI packet.
typedef struct {  // SPI command.
  beamformer_spi_command_e command;

  // Address.
  beamformer_register_e address;

  // Data bytes.
  uint8_t data[BEAMFORMER_NUM_BYTES_PER_SPI_PACKET];
} beamformer_spi_packet_t;

// Beamformer phase IQ setting struct.
typedef struct {
  uint8_t i;
  uint8_t q;
} beamformer_phase_iq_setting_t;

// DDS SPI communication configuration.
static const spi_comms_config_t g_beamformer_spi_comms_config =
    (spi_comms_config_t){
        .baudrate = BEAMFORMER_SPI_BAUDRATE,
        .data_bits = 8,
        .cpol = SPI_CPOL_0,
        .cpha = SPI_CPHA_0,
        .order = SPI_MSB_FIRST,
    };

static const beamformer_phase_iq_setting_t
    g_beamformer_phase_iq_settings[BEAMFORMER_NUM_PHASES] = {
        // Quadrant 1.
        {.i = 0x3F, .q = 0x20},  // 0°
        {.i = 0x3F, .q = 0x21},  // 2.8125°
        {.i = 0x3F, .q = 0x23},  // 5.625°
        {.i = 0x3F, .q = 0x24},  // 8.4375°
        {.i = 0x3F, .q = 0x26},  // 11.25°
        {.i = 0x3E, .q = 0x27},  // 14.0625°
        {.i = 0x3E, .q = 0x28},  // 16.875°
        {.i = 0x3D, .q = 0x2A},  // 19.6875°
        {.i = 0x3D, .q = 0x2B},  // 22.5°
        {.i = 0x3C, .q = 0x2D},  // 25.3125°
        {.i = 0x3C, .q = 0x2E},  // 28.125°
        {.i = 0x3B, .q = 0x2F},  // 30.9375°
        {.i = 0x3A, .q = 0x30},  // 33.75°
        {.i = 0x39, .q = 0x31},  // 36.5625°
        {.i = 0x38, .q = 0x33},  // 39.375°
        {.i = 0x37, .q = 0x34},  // 42.1875°
        {.i = 0x36, .q = 0x35},  // 45°
        {.i = 0x35, .q = 0x36},  // 47.8125°
        {.i = 0x34, .q = 0x37},  // 50.625°
        {.i = 0x33, .q = 0x38},  // 53.4375°
        {.i = 0x32, .q = 0x38},  // 56.25°
        {.i = 0x30, .q = 0x39},  // 59.0625°
        {.i = 0x2F, .q = 0x3A},  // 61.875°
        {.i = 0x2E, .q = 0x3A},  // 64.6875°
        {.i = 0x2C, .q = 0x3B},  // 67.5°
        {.i = 0x2B, .q = 0x3C},  // 70.3125°
        {.i = 0x2A, .q = 0x3C},  // 73.125°
        {.i = 0x28, .q = 0x3C},  // 75.9375°
        {.i = 0x27, .q = 0x3D},  // 78.75°
        {.i = 0x25, .q = 0x3D},  // 81.5625°
        {.i = 0x24, .q = 0x3D},  // 84.375°
        {.i = 0x22, .q = 0x3D},  // 87.1875°

        // Quadrant 2.
        {.i = 0x21, .q = 0x3D},  // 90°
        {.i = 0x01, .q = 0x3D},  // 92.8125°
        {.i = 0x03, .q = 0x3D},  // 95.625°
        {.i = 0x04, .q = 0x3D},  // 98.4375°
        {.i = 0x06, .q = 0x3D},  // 101.25°
        {.i = 0x07, .q = 0x3C},  // 104.0625°
        {.i = 0x08, .q = 0x3C},  // 106.875°
        {.i = 0x0A, .q = 0x3C},  // 109.6875°
        {.i = 0x0B, .q = 0x3B},  // 112.5°
        {.i = 0x0D, .q = 0x3A},  // 115.3125°
        {.i = 0x0E, .q = 0x3A},  // 118.125°
        {.i = 0x0F, .q = 0x39},  // 120.9375°
        {.i = 0x11, .q = 0x38},  // 123.75°
        {.i = 0x12, .q = 0x38},  // 126.5625°
        {.i = 0x13, .q = 0x37},  // 129.375°
        {.i = 0x14, .q = 0x36},  // 132.1875°
        {.i = 0x16, .q = 0x35},  // 135°
        {.i = 0x17, .q = 0x34},  // 137.8125°
        {.i = 0x18, .q = 0x33},  // 140.625°
        {.i = 0x19, .q = 0x31},  // 143.4375°
        {.i = 0x19, .q = 0x30},  // 146.25°
        {.i = 0x1A, .q = 0x2F},  // 149.0625°
        {.i = 0x1B, .q = 0x2E},  // 151.875°
        {.i = 0x1C, .q = 0x2D},  // 154.6875°
        {.i = 0x1C, .q = 0x2B},  // 157.5°
        {.i = 0x1D, .q = 0x2A},  // 160.3125°
        {.i = 0x1E, .q = 0x28},  // 163.125°
        {.i = 0x1E, .q = 0x27},  // 165.9375°
        {.i = 0x1E, .q = 0x26},  // 168.75°
        {.i = 0x1F, .q = 0x24},  // 171.5625°
        {.i = 0x1F, .q = 0x23},  // 174.375°
        {.i = 0x1F, .q = 0x21},  // 177.1875°

        // Quadrant 3.
        {.i = 0x1F, .q = 0x20},  // 180°
        {.i = 0x1F, .q = 0x01},  // 182.8125°
        {.i = 0x1F, .q = 0x03},  // 185.625°
        {.i = 0x1F, .q = 0x04},  // 188.4375°
        {.i = 0x1F, .q = 0x06},  // 191.25°
        {.i = 0x1E, .q = 0x07},  // 194.0625°
        {.i = 0x1E, .q = 0x08},  // 196.875°
        {.i = 0x1D, .q = 0x0A},  // 199.6875°
        {.i = 0x1D, .q = 0x0B},  // 202.5°
        {.i = 0x1C, .q = 0x0D},  // 205.3125°
        {.i = 0x1C, .q = 0x0E},  // 208.125°
        {.i = 0x1B, .q = 0x0F},  // 210.9375°
        {.i = 0x1A, .q = 0x10},  // 213.75°
        {.i = 0x19, .q = 0x11},  // 216.5625°
        {.i = 0x18, .q = 0x13},  // 219.375°
        {.i = 0x17, .q = 0x14},  // 222.1875°
        {.i = 0x16, .q = 0x15},  // 225°
        {.i = 0x15, .q = 0x16},  // 227.8125°
        {.i = 0x14, .q = 0x17},  // 230.625°
        {.i = 0x13, .q = 0x18},  // 233.4375°
        {.i = 0x12, .q = 0x18},  // 236.25°
        {.i = 0x10, .q = 0x19},  // 239.0625°
        {.i = 0x0F, .q = 0x1A},  // 241.875°
        {.i = 0x0E, .q = 0x1A},  // 244.6875°
        {.i = 0x0C, .q = 0x1B},  // 247.5°
        {.i = 0x0B, .q = 0x1C},  // 250.3125°
        {.i = 0x0A, .q = 0x1C},  // 253.125°
        {.i = 0x08, .q = 0x1C},  // 255.9375°
        {.i = 0x07, .q = 0x1D},  // 258.75°
        {.i = 0x05, .q = 0x1D},  // 261.5625°
        {.i = 0x04, .q = 0x1D},  // 264.375°
        {.i = 0x02, .q = 0x1D},  // 267.1875°

        // Quadrant 4.
        {.i = 0x01, .q = 0x1D},  // 270°
        {.i = 0x21, .q = 0x1D},  // 272.8125°
        {.i = 0x23, .q = 0x1D},  // 275.625°
        {.i = 0x24, .q = 0x1D},  // 278.4375°
        {.i = 0x26, .q = 0x1D},  // 281.25°
        {.i = 0x27, .q = 0x1C},  // 284.0625°
        {.i = 0x28, .q = 0x1C},  // 286.875°
        {.i = 0x2A, .q = 0x1C},  // 289.6875°
        {.i = 0x2B, .q = 0x1B},  // 292.5°
        {.i = 0x2D, .q = 0x1A},  // 295.3125°
        {.i = 0x2E, .q = 0x1A},  // 298.125°
        {.i = 0x2F, .q = 0x19},  // 300.9375°
        {.i = 0x31, .q = 0x18},  // 303.75°
        {.i = 0x32, .q = 0x18},  // 306.5625°
        {.i = 0x33, .q = 0x17},  // 309.375°
        {.i = 0x34, .q = 0x16},  // 312.1875°
        {.i = 0x36, .q = 0x15},  // 315°
        {.i = 0x37, .q = 0x14},  // 317.8125°
        {.i = 0x38, .q = 0x13},  // 320.625°
        {.i = 0x39, .q = 0x11},  // 323.4375°
        {.i = 0x39, .q = 0x10},  // 326.25°
        {.i = 0x3A, .q = 0x0F},  // 329.0625°
        {.i = 0x3B, .q = 0x0E},  // 331.875°
        {.i = 0x3C, .q = 0x0D},  // 334.6875°
        {.i = 0x3C, .q = 0x0B},  // 337.5°
        {.i = 0x3D, .q = 0x0A},  // 340.3125°
        {.i = 0x3E, .q = 0x08},  // 343.125°
        {.i = 0x3E, .q = 0x07},  // 345.9375°
        {.i = 0x3E, .q = 0x06},  // 348.75°
        {.i = 0x3F, .q = 0x04},  // 351.5625°
        {.i = 0x3F, .q = 0x03},  // 354.375°
        {.i = 0x3F, .q = 0x01},  // 357.1875°
};

// DDS configuration.
static beamformer_config_t g_beamformer_config;

// DDS SPI TX packet.
static beamformer_spi_packet_t g_beamformer_spi_tx_packet;

// DDS SPI RX packet.
static beamformer_spi_packet_t g_beamformer_spi_rx_packet;

// DDS SPI TX buffer for the address bytes and the data byte.
static uint8_t
    g_beamformer_spi_tx_buffer[BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                               BEAMFORMER_NUM_BYTES_PER_SPI_PACKET];

// DDS SPI RX buffer for the address bytes and the data byte.
static uint8_t
    g_beamformer_spi_rx_buffer[BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                               BEAMFORMER_NUM_BYTES_PER_SPI_PACKET];

// Write to a DDS register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void beamformer_spi_write_register(void) {
  memset(g_beamformer_spi_tx_buffer, 0,
         BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
             BEAMFORMER_NUM_BYTES_PER_SPI_PACKET);
  g_beamformer_spi_tx_buffer[0] =
      (BEAMFORMER_SPI_COMMAND_WRITE << 7) |
      ((BEAMFORMER_SPI_ADDRESS & 0x3) << 5) |
      ((g_beamformer_spi_tx_packet.address >> 8) & 0x7);
  g_beamformer_spi_tx_buffer[1] = g_beamformer_spi_tx_packet.address & 0xFF;
  memcpy(
      &g_beamformer_spi_tx_buffer[BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET],
      g_beamformer_spi_tx_packet.data, BEAMFORMER_NUM_BYTES_PER_SPI_PACKET);
  spi_transmit(&g_beamformer_config.spi_io_config, g_beamformer_spi_tx_buffer,
               /*length=*/BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                   BEAMFORMER_NUM_BYTES_PER_SPI_PACKET);
}

// Read from a DDS register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void beamformer_spi_read_register(void) {
  memset(g_beamformer_spi_tx_buffer, 0,
         BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
             BEAMFORMER_NUM_BYTES_PER_SPI_PACKET);
  g_beamformer_spi_tx_buffer[0] =
      (BEAMFORMER_SPI_COMMAND_READ << 7) |
      ((BEAMFORMER_SPI_ADDRESS & 0x3) << 5) |
      ((g_beamformer_spi_tx_packet.address >> 8) & 0x7);
  g_beamformer_spi_tx_buffer[1] = g_beamformer_spi_tx_packet.address & 0xFF;
  spi_transmit_receive(&g_beamformer_config.spi_io_config,
                       g_beamformer_spi_tx_buffer, g_beamformer_spi_rx_buffer,
                       /*length=*/BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                           BEAMFORMER_NUM_BYTES_PER_SPI_PACKET);
  memcpy(
      g_beamformer_spi_rx_packet.data,
      &g_beamformer_spi_rx_buffer[BEAMFORMER_NUM_ADDRESS_BYTES_PER_SPI_PACKET],
      BEAMFORMER_NUM_BYTES_PER_SPI_PACKET);
}

// Initialize the transmit/receive control.
static inline void beamformer_init_tr_control(void) {
  g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
  g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_SW_CTRL;
  // Enable TX and set the transmit/receive control to SPI.
  g_beamformer_spi_tx_packet.data[0] =
      (1 << 6) | (BEAMFORMER_TR_SOURCE_SPI << 2) | (BEAMFORMER_SPI_TR_TX << 1);
  beamformer_spi_write_register();
}

// Initialize the memory control.
static inline void beamformer_init_memory(void) {
  g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
  g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_MEM_CTRL;
  // Load beam and bias position settings from the registers.
  g_beamformer_spi_tx_packet.data[0] = (1 << 6) | (1 << 5);
  beamformer_spi_write_register();
}

// Initialize the bias for the TX subcircuits.
static inline void beamformer_init_tx_bias(void) {
  g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
  g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_BIAS_CURRENT_TX;
  // Set the VGA bias and the vector modulator bias to 5 (recommended).
  g_beamformer_spi_tx_packet.data[0] = (5 << 3) | 5;
  beamformer_spi_write_register();

  g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
  g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_BIAS_CURRENT_TX_DRV;
  // Set the TX driver bias to 6 (recommended).
  g_beamformer_spi_tx_packet.data[0] = 6;
  beamformer_spi_write_register();
}

// Set the TX enables.
static inline void beamformer_enable_tx(const beamformer_tx_config_t* config) {
  g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
  g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_TX_ENABLES;
  // Enable all TX channel drivers, vector modulators, and VGAs.
  g_beamformer_spi_tx_packet.data[0] = 0x7;
  // Enable each channel.
  for (size_t i = 0; i < BEAMFORMER_NUM_CHANNELS; ++i) {
    g_beamformer_spi_tx_packet.data[0] |= config->channel_configs[i].enabled
                                          << (6 - i);
  }
  beamformer_spi_write_register();
}

void beamformer_init(const beamformer_config_t* config) {
  g_beamformer_config = *config;
  spi_inst_init(&g_beamformer_config.spi_io_config,
                &g_beamformer_spi_comms_config);

  // Initialize the TX load pin.
  gpio_init(g_beamformer_config.gpio_tx_load);
  gpio_set_dir(g_beamformer_config.gpio_tx_load, GPIO_OUT);

  // Initialize the transmit/receive pin.
  gpio_init(g_beamformer_config.gpio_transmit_receive);
  gpio_set_dir(g_beamformer_config.gpio_transmit_receive, GPIO_OUT);

  beamformer_reset();
  beamformer_init_tr_control();
  beamformer_init_memory();
  beamformer_init_tx_bias();
}

void beamformer_reset(void) {
  g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
  g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_INTERFACE_CONFIG_A;
  // Trigger a soft reset, configure MSB first, enable address ascension, and
  // enable SDO.
  g_beamformer_spi_tx_packet.data[0] = 0b10111101;
  beamformer_spi_write_register();
}

void beamformer_configure_tx(const beamformer_tx_config_t* config) {
  beamformer_enable_tx(config);
  for (size_t i = 0; i < BEAMFORMER_NUM_CHANNELS; ++i) {
    const beamformer_tx_channel_config_t* channel_config =
        &config->channel_configs[i];

    // Set the attenuator and VGA gain.
    g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
    g_beamformer_spi_tx_packet.address = BEAMFORMER_REGISTER_CH1_TX_GAIN + i;
    g_beamformer_spi_tx_packet.data[0] =
        (channel_config->attenuator << 7) | (channel_config->vga_gain & 0x7F);
    beamformer_spi_write_register();

    // Set the vector modulator I input.
    g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
    g_beamformer_spi_tx_packet.address =
        BEAMFORMER_REGISTER_CH1_TX_PHASE_I + 2 * i;
    g_beamformer_spi_tx_packet.data[0] =
        g_beamformer_phase_iq_settings[channel_config->phase].i & 0x3F;
    beamformer_spi_write_register();

    // Set the vector modulator Q input.
    g_beamformer_spi_tx_packet.command = BEAMFORMER_SPI_COMMAND_WRITE;
    g_beamformer_spi_tx_packet.address =
        BEAMFORMER_REGISTER_CH1_TX_PHASE_Q + 2 * i;
    g_beamformer_spi_tx_packet.data[0] =
        g_beamformer_phase_iq_settings[channel_config->phase].q & 0x3F;
    beamformer_spi_write_register();
  }
}

void beamformer_load_tx(void) {
  gpio_put(g_beamformer_config.gpio_tx_load, true);
  sleep_us(/*us=*/10);
  gpio_put(g_beamformer_config.gpio_tx_load, false);
}
