# Program the QSPI flash.

set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir board.tcl]

set bitfile [file normalize [file join $script_dir ../build/dory.bit]]
set mcsfile [file normalize [file join $script_dir ../build/dory.mcs]]

if {![file exists $bitfile]} {
    error "Bitstream not found: $bitfile"
}

# Create MCS.
write_cfgmem -force -format mcs -interface $cfgmem_interface -size $cfgmem_size_mb \
    -loadbit "up 0x0 $bitfile" $mcsfile

open_hw_manager
connect_hw_server
open_hw_target

# Select device.
set device [lindex [get_hw_devices $hw_device_pattern] 0]
if {$device eq ""} {
    error "No matching FPGA device found"
}

current_hw_device $device
refresh_hw_device $device

# Configure flash.
set existing_cfgmem [get_property PROGRAM.HW_CFGMEM $device]
if {$existing_cfgmem ne ""} {
    delete_hw_cfgmem $existing_cfgmem
}

set cfgmem_part [lindex [get_cfgmem_parts $cfgmem_part_name] 0]
set cfgmem [create_hw_cfgmem -hw_device $device -mem_dev $cfgmem_part]

# Set properties.
set_property PROGRAM.FILES [list $mcsfile] $cfgmem
set_property PROGRAM.ADDRESS_RANGE {use_file} $cfgmem
set_property PROGRAM.UNUSED_PIN_TERMINATION {pull-none} $cfgmem

set_property PROGRAM.BLANK_CHECK 0 $cfgmem
set_property PROGRAM.ERASE 1 $cfgmem
set_property PROGRAM.CFG_PROGRAM 1 $cfgmem
set_property PROGRAM.VERIFY 1 $cfgmem

# Program flash.
startgroup
program_hw_cfgmem -hw_cfgmem $cfgmem
endgroup

puts "Flash programming complete. Power-cycle or reset FPGA to load from flash."
exit
