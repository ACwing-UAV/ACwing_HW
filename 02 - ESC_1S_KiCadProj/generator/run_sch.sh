set -e
cd /home/claude/outESCB
python3 /home/claude/genESCB/gen_sch_esc.py DimaQuadESC_B.kicad_sch
python3 -c "
import sys; sys.path.insert(0,'/home/claude/genESCB'); import custom_syms; custom_syms.write_lib('/home/claude/outESCB/DimaQuad.kicad_sym')"
printf '(sym_lib_table\n  (version 7)\n  (lib (name "DimaQuad")(type "KiCad")(uri "${KIPRJMOD}/DimaQuad.kicad_sym")(options "")(descr "DimaQuad project symbols"))\n)\n' > sym-lib-table
kicad-cli sch export netlist -o /tmp/claude-0/nescb.xml --format kicadxml DimaQuadESC_B.kicad_sch >/dev/null
python3 /home/claude/genESCB/check_net.py /tmp/claude-0/nescb.xml DimaQuadESC_B.kicad_sch.expected.json DimaQuadESC_B.kicad_sch.nc.json
kicad-cli sch export pdf -o DimaQuadESC_B_schematic.pdf DimaQuadESC_B.kicad_sch >/dev/null
pdftoppm -r 90 -png DimaQuadESC_B_schematic.pdf /tmp/claude-0/eschb
