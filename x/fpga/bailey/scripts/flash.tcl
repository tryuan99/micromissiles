# Program the QSPI flash.

set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir board.tcl]

set bitfile [file normalize [file join $script_dir ../build/bailey.bit]]
set mcsfile [file normalize [file join $script_dir ../build/bailey.mcs]]

if {![file exists $bitfile]} {
    error "Bitstream not found: $bitfile"
}

# Create MCS from the generated bitstream.
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

# Reset any prior cfgmem association on the device.
set existing_cfgmem [get_property PROGRAM.HW_CFGMEM $device]
if {$existing_cfgmem ne ""} {
    delete_hw_cfgmem $existing_cfgmem
}

# Create and select the cfgmem object for this device.
set cfgmem_part [lindex [get_cfgmem_parts $cfgmem_part_name] 0]
if {$cfgmem_part eq ""} {
    error "No matching cfgmem part found for: $cfgmem_part_name"
}

create_hw_cfgmem -hw_device $device $cfgmem_part
set cfgmem [current_hw_cfgmem -hw_device $device]

# Configure the programming operation.
set_property PROGRAM.FILE $mcsfile $cfgmem
set_property PROGRAM.ADDRESS_RANGE {use_file} $cfgmem
set_property PROGRAM.BLANK_CHECK 1 $cfgmem
set_property PROGRAM.ERASE 1 $cfgmem
set_property PROGRAM.CFG_PROGRAM 1 $cfgmem
set_property PROGRAM.VERIFY 1 $cfgmem

# Load Vivado's indirect programming bridge bitstream into the FPGA.
set cfgmem_bitfile [get_property PROGRAM.HW_CFGMEM_BITFILE $device]
if {$cfgmem_bitfile eq ""} {
    error "Vivado did not provide a cfgmem bridge bitstream for $device"
}

create_hw_bitstream -hw_device $device $cfgmem_bitfile
program_hw_devices $device

# Program flash.
program_hw_cfgmem $cfgmem

puts "Flash programming complete. Power-cycle or reset FPGA to load from flash."
exit
