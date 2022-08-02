#!/usr/bin/python3

# Create makefile dependencies for VHDL files, looking for "use work" and
# "entity work" declarations

import sys
import re
import os
from collections import defaultdict

if len(sys.argv) == 1 and sys.argv[1] == '--help':
    print("Usage: dependencies.py [--synth]")
    sys.exit(1)

synth = False
args = sys.argv[1:]
if sys.argv[1] == '--synth':
    synth = True
    args = sys.argv[2:]

# Look at what a file provides
entity = re.compile('entity (.*) is')
package = re.compile('package (.*) is')

# Look at what a file depends on
work = re.compile('use work\.([^.]+)\.')
entity_work = re.compile('entity work\.([^;]+)')

# Synthesis targets
synth_provides = {
    "dmi_dtm" : "dmi_dtm_dummy.vhdl",
    "clock_generator" : "fpga/clk_gen_bypass.vhd",
    "main_bram" : "fpga/main_bram.vhdl",
    "pp_soc_uart" : "fpga/pp_soc_uart.vhd"
}

# Simulation targets
sim_provides = {
    "dmi_dtm" : "dmi_dtm_xilinx.vhdl",
    "clock_generator" : "fpga/clk_gen_bypass.vhd",
    "main_bram" : "sim_bram.vhdl",
    "pp_soc_uart" : "sim_pp_uart.vhdl"
}

provides = synth_provides if synth else sim_provides
dependencies = defaultdict(set)

for filename in args:
    with open(filename, 'r') as f:
        for line in f:
            l = line.rstrip(os.linesep)
            if m := entity.search(l):
                p = m[1]
                if p not in provides:
                    provides[p] = filename

            if m := package.search(l):
                p = m[1]
                if p not in provides:
                    provides[p] = filename

            if m := work.search(l):
                dependency = m[1]
                dependencies[filename].add(dependency)

            if m := entity_work.search(l):
                dependency = m[1]
                dependencies[filename].add(dependency)


emitted = set()
def chase_dependencies(filename):
    if filename in dependencies:
        for dep in dependencies[filename]:
            f = provides[dep]
            chase_dependencies(f)
            if f not in emitted:
                print(f"{f} ", end="")
                emitted.add(f)

    elif filename not in emitted:
        print(f"{filename} ", end="")
        emitted.add(filename)


if synth:
    chase_dependencies("fpga/toplevel.vhdl")
    print("fpga/toplevel.vhdl")
else:
    for filename in dependencies:
        (basename, suffix) = filename.split('.')
        print(f"{basename}.o:", end="")
        for dependency in dependencies[filename]:
            p = provides[dependency]
            (basename2, suffix2) = p.split('.')
            print(f" {basename2}.o", end="")
        print("")
