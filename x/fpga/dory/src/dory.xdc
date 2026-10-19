# Source: https://github.com/Digilent/digilent-xdc/blob/master/Arty-A7-35-Master.xdc

# Clock signal.
set_property -dict { PACKAGE_PIN E3    IOSTANDARD LVCMOS33 } [get_ports { CLK }];
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports { CLK }];

# Switches.
set_property -dict { PACKAGE_PIN A8    IOSTANDARD LVCMOS33 } [get_ports { SWITCHES[0] }];
set_property -dict { PACKAGE_PIN C11   IOSTANDARD LVCMOS33 } [get_ports { SWITCHES[1] }];
set_property -dict { PACKAGE_PIN C10   IOSTANDARD LVCMOS33 } [get_ports { SWITCHES[2] }];
set_property -dict { PACKAGE_PIN A10   IOSTANDARD LVCMOS33 } [get_ports { SWITCHES[3] }];

# LEDs.
set_property -dict { PACKAGE_PIN H5    IOSTANDARD LVCMOS33 } [get_ports { LEDS[0] }];
set_property -dict { PACKAGE_PIN J5    IOSTANDARD LVCMOS33 } [get_ports { LEDS[1] }];
set_property -dict { PACKAGE_PIN T9    IOSTANDARD LVCMOS33 } [get_ports { LEDS[2] }];
set_property -dict { PACKAGE_PIN T10   IOSTANDARD LVCMOS33 } [get_ports { LEDS[3] }];

# Buttons.
set_property -dict { PACKAGE_PIN C2    IOSTANDARD LVCMOS33 } [get_ports { RESET }];
set_property -dict { PACKAGE_PIN D9    IOSTANDARD LVCMOS33 } [get_ports { BUTTONS[0] }];
set_property -dict { PACKAGE_PIN C9    IOSTANDARD LVCMOS33 } [get_ports { BUTTONS[1] }];
set_property -dict { PACKAGE_PIN B9    IOSTANDARD LVCMOS33 } [get_ports { BUTTONS[2] }];
set_property -dict { PACKAGE_PIN B8    IOSTANDARD LVCMOS33 } [get_ports { BUTTONS[3] }];

# USB-UART interface.
set_property -dict { PACKAGE_PIN D10   IOSTANDARD LVCMOS33 } [get_ports { UART_RXD_OUT }];
set_property -dict { PACKAGE_PIN A9    IOSTANDARD LVCMOS33 } [get_ports { UART_TXD_IN }];

# PMOD header JA.
set_property -dict { PACKAGE_PIN G13   IOSTANDARD LVCMOS33 } [get_ports { DDS_DRCTL }];
set_property -dict { PACKAGE_PIN B11   IOSTANDARD LVCMOS33 } [get_ports { DDS_DRHOLD }];
set_property -dict { PACKAGE_PIN A11   IOSTANDARD LVCMOS33 } [get_ports { DDS_DROVER }];
set_property -dict { PACKAGE_PIN D12   IOSTANDARD LVCMOS33 } [get_ports { DDS_OSK }];
set_property -dict { PACKAGE_PIN D13   IOSTANDARD LVCMOS33 } [get_ports { VCO_RF_EN }];
set_property -dict { PACKAGE_PIN B18   IOSTANDARD LVCMOS33 } [get_ports { MIXER_EN }];

set_property BITSTREAM.CONFIG.CONFIGRATE 33 [current_design]
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
