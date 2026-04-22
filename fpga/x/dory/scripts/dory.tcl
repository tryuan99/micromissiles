# Run synthesis, implementation and bitstream generation.

set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir board.tcl]
source [file join $script_dir files.tcl]

set out_dir [file normalize [file join $script_dir ../build]]
set part $fpga_part
set top "dory"

set timing_summary_file [file join $out_dir timing_summary.rpt]
set utilization_file [file join $out_dir utilization.rpt]

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
report_timing_summary -file $timing_summary_file
report_utilization -file $utilization_file

# Check timing closure.
proc get_worst_slack {delay_type} {
    set timing_paths [get_timing_paths -delay_type $delay_type -max_paths 1 -nworst 1]
    if {[llength $timing_paths] == 0} {
        error "No timing paths found for delay type: $delay_type"
    }

    return [get_property SLACK [lindex $timing_paths 0]]
}

set worst_setup_slack [get_worst_slack max]
set worst_hold_slack [get_worst_slack min]

puts [format "Worst setup slack: %.3f ns" $worst_setup_slack]
puts [format "Worst hold slack: %.3f ns" $worst_hold_slack]

if {$worst_setup_slack < 0 || $worst_hold_slack < 0} {
    error [format \
        "Timing closure failed (setup WNS=%.3f ns, hold WHS=%.3f ns). See %s." \
        $worst_setup_slack \
        $worst_hold_slack \
        $timing_summary_file]
}

# Bitstream.
puts "Generating bitstream..."
write_bitstream -force [file join $out_dir ${top}.bit]
puts "Bitstream generation complete."

exit
