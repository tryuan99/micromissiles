#include "pico/x/bailey/adc.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "hardware/gpio.h"
#include "pico/common/spi.h"

// ADC SPI baudrate.
#define ADC_SPI_BAUDRATE 1000000

// ADC ADDR15 bit.
#define ADC_ADDR15_BIT0 0

// Number of bytes in the address of an ADC SPI packet.
#define ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET 2

// Number of bytes per ADC SPI packet.
#define ADC_NUM_BYTES_PER_SPI_PACKET 2

// DDS SPI command enumeration.
typedef enum {
  ADC_SPI_COMMAND_INVALID = -1,
  ADC_SPI_COMMAND_WRITE = 0,
  ADC_SPI_COMMAND_READ = 1,
} adc_spi_command_e;

typedef enum {
  ADC_REGISTER_INVALID = -1,
  ADC_REGISTER_CLK_CTRL = 0x000,
  ADC_REGISTER_PLL_DEN = 0x001,
  ADC_REGISTER_PLL_NUM = 0x002,
  ADC_REGISTER_PLL_CTRL = 0x003,
  ADC_REGISTER_PLL_LOCK = 0x005,
  ADC_REGISTER_MASTER_ENABLE = 0x040,
  ADC_REGISTER_ADC_ENABLE = 0x041,
  ADC_REGISTER_POWER_ENABLE = 0x042,
  ADC_REGISTER_ASIL_CLEAR = 0x080,
  ADC_REGISTER_ASIL_MASK = 0x081,
  ADC_REGISTER_ASIL_FLAG = 0x082,
  ADC_REGISTER_ASIL_ERROR = 0x083,
  ADC_REGISTER_CRC_VALUE_L = 0x084,
  ADC_REGISTER_CRC_VALUE_H = 0x085,
  ADC_REGISTER_RM_CRC_ENABLE = 0x086,
  ADC_REGISTER_RM_CRC_DONE = 0x087,
  ADC_REGISTER_RM_CRC_VALUE_L = 0x088,
  ADC_REGISTER_RM_CRC_VALUE_H = 0x089,
  ADC_REGISTER_LNA_GAIN = 0x100,
  ADC_REGISTER_PGA_GAIN = 0x101,
  ADC_REGISTER_ADC_ROUTING1_4 = 0x102,
  ADC_REGISTER_DECIM_RATE = 0x140,
  ADC_REGISTER_HIGH_PASS = 0x141,
  ADC_REGISTER_ACK_MODE = 0x143,
  ADC_REGISTER_TRUNCATE_MODE = 0x144,
  ADC_REGISTER_SERIAL_MODE = 0x1C0,
  ADC_REGISTER_PARALLEL_MODE = 0x1C1,
  ADC_REGISTER_OUTPUT_MODE = 0x1C2,
  ADC_REGISTER_ADC_READ0 = 0x200,
  ADC_REGISTER_ADC_READ1 = 0x201,
  ADC_REGISTER_ADC_SPEED = 0x210,
  ADC_REGISTER_ADC_MODE = 0x211,
  ADC_REGISTER_MP0_MODE = 0x250,
  ADC_REGISTER_MP1_MODE = 0x251,
  ADC_REGISTER_MP0_WRITE = 0x260,
  ADC_REGISTER_MP1_WRITE = 0x261,
  ADC_REGISTER_MP0_READ = 0x270,
  ADC_REGISTER_MP1_READ = 0x271,
  ADC_REGISTER_SPI_CLK_PIN = 0x280,
  ADC_REGISTER_MISO_PIN = 0x281,
  ADC_REGISTER_SS_PIN = 0x282,
  ADC_REGISTER_MOSI_PIN = 0x283,
  ADC_REGISTER_ADDR15_PIN = 0x284,
  ADC_REGISTER_FAULT_PIN = 0x285,
  ADC_REGISTER_FS_ADC_PIN = 0x286,
  ADC_REGISTER_CS_PIN = 0x287,
  ADC_REGISTER_SCLK_ADC_PIN = 0x288,
  ADC_REGISTER_ADC_DOUT0_PIN = 0x289,
  ADC_REGISTER_ADC_DOUT1_PIN = 0x28A,
  ADC_REGISTER_ADC_DOUT2_PIN = 0x28B,
  ADC_REGISTER_ADC_DOUT3_PIN = 0x28C,
  ADC_REGISTER_ADC_DOUT4_PIN = 0x28D,
  ADC_REGISTER_ADC_DOUT5_PIN = 0x28E,
  ADC_REGISTER_DATA_READY_PIN = 0x291,
  ADC_REGISTER_XTAL_CTRL = 0x292,
  ADC_REGISTER_ADC_SETTING1 = 0x301,
  ADC_REGISTER_ADC_SETTING2 = 0x308,
  ADC_REGISTER_ADC_SETTING3 = 0x30A,
  ADC_REGISTER_DEJITTER_WINDOW = 0x30E,
  ADC_REGISTER_CRC_EN = 0xFD00,
} adc_register_e;

// ADC SPI packet.
typedef struct {
  // SPI command.
  adc_spi_command_e command;

  // Address.
  adc_register_e address;

  // Data bytes.
  uint8_t data[ADC_NUM_BYTES_PER_SPI_PACKET];
} adc_spi_packet_t;

// ADC PLL configuration.
// The PLL output is at a fixed frequency of 115.2 MHz.
typedef struct {
  // Multiplier.
  uint8_t R;

  // Numerator.
  uint16_t N;

  // Denominator.
  uint16_t M;

  // Prescaler.
  uint8_t X;
} adc_pll_config_t;

// ADC SPI communication configuration.
static const spi_comms_config_t g_adc_spi_comms_config = (spi_comms_config_t){
    .baudrate = ADC_SPI_BAUDRATE,
    .data_bits = 8,
    .cpol = SPI_CPOL_0,
    .cpha = SPI_CPHA_0,
    .order = SPI_MSB_FIRST,
};

// ADC PLL configuration.
// The PLL output is at a fixed frequency of 115.2 MHz, and the input frequency
// is 50 MHz.
static const adc_pll_config_t g_adc_pll_config = (adc_pll_config_t){
    .R = 2,
    .N = 38,
    .M = 125,
    .X = 1,
};

// ADC configuration.
static adc_config_t g_adc_config;

// ADC SPI TX packet.
static adc_spi_packet_t g_adc_spi_tx_packet;

// ADC SPI RX packet.
static adc_spi_packet_t g_adc_spi_rx_packet;

// ADC SPI TX buffer for the device address byte, two register address bytes,
// and two data bytes.
static uint8_t g_adc_spi_tx_buffer[ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                                   ADC_NUM_BYTES_PER_SPI_PACKET + 1];

// ADC SPI RX buffer for the device address byte, two register address bytes,
// and two data bytes.
static uint8_t g_adc_spi_rx_buffer[ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                                   ADC_NUM_BYTES_PER_SPI_PACKET + 1];

// Write to an ADC register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void adc_spi_write_register(void) {
  memset(
      g_adc_spi_tx_buffer, 0,
      ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET + ADC_NUM_BYTES_PER_SPI_PACKET + 1);
  g_adc_spi_tx_buffer[0] = (ADC_ADDR15_BIT0 << 1) | ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_buffer[1] = (g_adc_spi_tx_packet.address >> 8) & 0xFF;
  g_adc_spi_tx_buffer[2] = g_adc_spi_tx_packet.address & 0xFF;
  memcpy(&g_adc_spi_tx_buffer[3], g_adc_spi_tx_packet.data,
         ADC_NUM_BYTES_PER_SPI_PACKET);
  spi_transmit(&g_adc_config.spi_io_config, g_adc_spi_tx_buffer,
               /*length=*/ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                   ADC_NUM_BYTES_PER_SPI_PACKET + 1);
}

// Read from an ADC register via SPI. Assume that the SPI instance has been
// initialized already.
static inline void adc_spi_read_register(void) {
  memset(
      g_adc_spi_tx_buffer, 0,
      ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET + ADC_NUM_BYTES_PER_SPI_PACKET + 1);
  g_adc_spi_tx_buffer[0] = (ADC_ADDR15_BIT0 << 1) | ADC_SPI_COMMAND_READ;
  g_adc_spi_tx_buffer[1] = (g_adc_spi_tx_packet.address >> 8) & 0xFF;
  g_adc_spi_tx_buffer[2] = g_adc_spi_tx_packet.address & 0xFF;
  spi_transmit_receive(&g_adc_config.spi_io_config, g_adc_spi_tx_buffer,
                       g_adc_spi_rx_buffer,
                       /*length=*/ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET +
                           ADC_NUM_BYTES_PER_SPI_PACKET + 1);
  memcpy(g_adc_spi_rx_packet.data,
         &g_adc_spi_rx_buffer[ADC_NUM_ADDRESS_BYTES_PER_SPI_PACKET + 1],
         ADC_NUM_BYTES_PER_SPI_PACKET);
}

// Initialize the PLL.
static inline void adc_init_pll(void) {
  // Use the PLL clock.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_CLK_CTRL;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0x01;
  adc_spi_write_register();

  // Set the PLL denominator.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_PLL_DEN;
  g_adc_spi_tx_packet.data[0] = (g_adc_pll_config.M >> 8) & 0xFF;
  g_adc_spi_tx_packet.data[1] = g_adc_pll_config.M & 0xFF;
  adc_spi_write_register();

  // Set the PLL numerator.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_PLL_NUM;
  g_adc_spi_tx_packet.data[0] = (g_adc_pll_config.N >> 8) & 0xFF;
  g_adc_spi_tx_packet.data[1] = g_adc_pll_config.N & 0xFF;
  adc_spi_write_register();

  // Set the PLL multiplier and prescaler, enable the PLL, and set the PLL to
  // fractional mode.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_PLL_CTRL;
  g_adc_spi_tx_packet.data[0] = (g_adc_pll_config.R & 0x1F) << 3;
  g_adc_spi_tx_packet.data[1] = ((g_adc_pll_config.X & 0xF) << 4) | 0x3;
  adc_spi_write_register();
}

// Initialize the ADC output.
static inline void adc_init_output(void) {
  // Set the ADC to be the SCLK_ADC master, set FS_ADC to be a 50/50 duty cycle
  // clock, set positive polarity for SCLK_ADC and FS_ADC, and output 2 channels
  // per pin.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_SERIAL_MODE;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0b01011100;
  adc_spi_write_register();

  // Output in serial mode and enable CONV_START_N.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_OUTPUT_MODE;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0b00;
  adc_spi_write_register();

  // Disable digital filter synchronization in serial mode.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_DEJITTER_WINDOW;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0b00;
  adc_spi_write_register();
}

void adc_init(const adc_config_t* config) {
  g_adc_config = *config;
  spi_inst_init(&g_adc_config.spi_io_config, &g_adc_spi_comms_config);

  // Initialize the conversion start pin.
  gpio_init(g_adc_config.gpio_conversion_start);

  // Initialize the data ready pin.
  gpio_init(g_adc_config.gpio_data_ready);

  // Initialize the reset pin.
  gpio_init(g_adc_config.gpio_reset);
  gpio_set_dir(g_adc_config.gpio_reset, GPIO_OUT);

  // Initialize the fault pin.
  gpio_init(g_adc_config.gpio_fault);
  gpio_set_dir(g_adc_config.gpio_fault, GPIO_IN);
  // TODO(titan): Add an interrupt listener for the fault pin.

  // Disable the CRC.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_CRC_EN;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0x01;
  adc_spi_write_register();

  adc_init_pll();
  adc_init_output();
}

void adc_configure(const adc_measurement_config_t* config) {
  // Enable the ADC channels and the corresponding LNA and PGA.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_ADC_ENABLE;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0x00;
  for (size_t i = 0; i < ADC_NUM_CHANNELS; ++i) {
    g_adc_spi_tx_packet.data[1] |=
        (config->channel_configs[i].enabled ? 0b10001 : 0) << i;
  }
  adc_spi_write_register();

  // Configure the ADC channel sources.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_ADC_ROUTING1_4;
  g_adc_spi_tx_packet.data[0] =
      ((config->channel_configs[3].source & 0x7) << 4) |
      (config->channel_configs[2].source & 0x7);
  g_adc_spi_tx_packet.data[1] =
      ((config->channel_configs[1].source & 0x7) << 4) |
      (config->channel_configs[0].source & 0x7);
  adc_spi_write_register();

  // Configure the ADC channel LNA gains.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_LNA_GAIN;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0x00;
  for (size_t i = 0; i < ADC_NUM_CHANNELS; ++i) {
    g_adc_spi_tx_packet.data[1] |= (config->channel_configs[i].lna_gain & 0x3)
                                   << (i * 2);
  }
  adc_spi_write_register();

  // Configure the equalizer cutoff frequency.
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_ADC_SETTING1;
  g_adc_spi_tx_packet.data[0] = config->equalizer_cutoff_frequency & 0x3;
  g_adc_spi_tx_packet.data[1] = 0x04;
  adc_spi_write_register();
}

void adc_enable(void) {
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_MASTER_ENABLE;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0x01;
  adc_spi_write_register();
}

void adc_disable(void) {
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_WRITE;
  g_adc_spi_tx_packet.address = ADC_REGISTER_MASTER_ENABLE;
  g_adc_spi_tx_packet.data[0] = 0x00;
  g_adc_spi_tx_packet.data[1] = 0x00;
  adc_spi_write_register();
}

bool adc_pll_locked(void) {
  g_adc_spi_tx_packet.command = ADC_SPI_COMMAND_READ;
  g_adc_spi_tx_packet.address = ADC_REGISTER_PLL_LOCK;
  adc_spi_read_register();
  return (g_adc_spi_tx_packet.data[1] & 0x1) == 0x1;
}
