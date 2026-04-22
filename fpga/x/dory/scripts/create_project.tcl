# Create a Vivado project.

set script_dir [file dirname [file normalize [info script]]]
source [file join $script_dir board.tcl]
source [file join $script_dir files.tcl]

set proj_dir [file normalize [file join $script_dir ../proj]]
set proj_name "dory"
set part $fpga_part
set top "dory"

file mkdir $proj_dir

# Create project.
create_project $proj_name $proj_dir -part $part

# Add source files.
add_files -fileset sources_1 $srcs_files

# Add constraint files.
add_files -fileset constrs_1 $constrs_files

# Set top module.
set_property top $top [get_filesets sources_1]

# Ensure compile order.
update_compile_order -fileset sources_1

puts "Project created successfully at $proj_dir"
exit
