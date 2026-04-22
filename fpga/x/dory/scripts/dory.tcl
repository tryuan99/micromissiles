# Run synthesis, implementation and bitstream generation.

set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir board.tcl]
source [file join $script_dir files.tcl]

set out_dir [file normalize [file join $script_dir ../build]]
set part $fpga_part
set top "dory"

file mkdir $out_dir

reset_project -quiet

# Read source files.
read_verilog $srcs_files

# Read constraint files.
read_xdc $constrs_files

# Synthesis.
puts "Starting synthesis..."
synth_design -top $top -part $part -flatten_hierarchy rebuilt
write_checkpoint -force [file join $out_dir post_synth.dcp]
puts "Synthesis complete."

# Implementation.
puts "Starting implementation..."
opt_design
place_design
route_design
write_checkpoint -force [file join $out_dir post_route.dcp]
puts "Implementation complete."

# Reports.
report_timing_summary -file [file join $out_dir timing_summary.rpt]
report_utilization -file [file join $out_dir utilization.rpt]

# Bitstream.
puts "Generating bitstream..."
write_bitstream -force [file join $out_dir ${top}.bit]
puts "Bitstream generation complete."

exit
