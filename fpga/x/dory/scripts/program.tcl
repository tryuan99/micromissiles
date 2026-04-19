# Write the bitstream to the FPGA.

set script_dir [file dirname [file normalize [info script]]]

set bitfile [file normalize [file join $script_dir ../build/dory.bit]]

if {![file exists $bitfile]} {
    error "Bitstream not found: $bitfile"
}

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

# Program FPGA.
set_property PROGRAM.FILE $bitfile $device
program_hw_devices $device

puts "FPGA programmed successfully."
exit
