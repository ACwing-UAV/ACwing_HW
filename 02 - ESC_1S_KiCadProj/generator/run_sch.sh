set -e
cd /home/claude/outESCB
python3 /home/claude/genESCB/gen_sch_esc.py ACwing_ESC1S_A.kicad_sch
python3 -c "
import sys; sys.path.insert(0,'/home/claude/genESCB'); import custom_syms; custom_syms.write_lib('/home/claude/outESCB/ACwing.kicad_sym')"
printf '(sym_lib_table\n  (version 7)\n  (lib (name "ACwing")(type "KiCad")(uri "${KIPRJMOD}/ACwing.kicad_sym")(options "")(descr "ACwing project symbols"))\n)\n' > sym-lib-table
kicad-cli sch export netlist -o /tmp/claude-0/nescb.xml --format kicadxml ACwing_ESC1S_A.kicad_sch >/dev/null
python3 /home/claude/genESCB/check_net.py /tmp/claude-0/nescb.xml ACwing_ESC1S_A.kicad_sch.expected.json ACwing_ESC1S_A.kicad_sch.nc.json
kicad-cli sch export pdf -o ACwing_ESC1S_A_schematic.pdf ACwing_ESC1S_A.kicad_sch >/dev/null
pdftoppm -r 90 -png ACwing_ESC1S_A_schematic.pdf /tmp/claude-0/eschb
