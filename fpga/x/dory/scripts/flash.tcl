# Program the QSPI flash.

set script_dir [file dirname [file normalize [info script]]]

set bitfile [file normalize [file join $script_dir ../build/dory.bit]]
set mcsfile [file normalize [file join $script_dir ../build/dory.mcs]]

if {![file exists $bitfile]} {
    error "Bitstream not found: $bitfile"
}

# Create MCS.
write_cfgmem -force -format mcs -interface spix4 -size 16 \
    -loadbit "up 0x0 $bitfile" $mcsfile

open_hw
connect_hw_server
open_hw_target

# Select device.
set device [lindex [get_hw_devices xc7a100t*] 0]
if {$device eq ""} {
    error "No matching FPGA device found"
}

current_hw_device $device
refresh_hw_device $device

# Configure flash.
set cfgmem_part [lindex [get_cfgmem_parts {mt25ql128-spi-x1_x2_x4}] 0]
create_hw_cfgmem -hw_device $device $cfgmem_part

set cfgmem [lindex [get_hw_cfgmems] 0]

# Set properties.
set_property PROGRAM.FILES [list $mcsfile] $cfgmem
set_property PROGRAM.ADDRESS_RANGE {use_file} $cfgmem
set_property PROGRAM.ERASE 1 $cfgmem
set_property PROGRAM.CFG_PROGRAM 1 $cfgmem
set_property PROGRAM.VERIFY 1 $cfgmem

# Program flash.
startgroup
program_hw_cfgmem -hw_cfgmem $cfgmem
endgroup

puts "Flash programming complete. Power-cycle or reset FPGA to load from flash."
exit
