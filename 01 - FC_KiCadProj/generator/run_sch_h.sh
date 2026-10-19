set -e
cd /home/claude/genH && python3 gen_sch_h.py /home/claude/outH/DimaQuadFC_H.kicad_sch && python3 projlib_links.py /home/claude/outH/DimaQuadFC_H.kicad_sch
cd /home/claude/outH
python3 -c "
import sys; sys.path.insert(0,'/home/claude/genH'); import custom_syms; custom_syms.write_lib('/home/claude/outH/DimaQuad.kicad_sym')"
printf '(sym_lib_table\n  (version 7)\n  (lib (name "DimaQuad")(type "KiCad")(uri "${KIPRJMOD}/DimaQuad.kicad_sym")(options "")(descr "DimaQuad project symbols"))\n)\n' > sym-lib-table
kicad-cli sch export netlist -o /tmp/claude-0/nH.xml --format kicadxml DimaQuadFC_H.kicad_sch >/dev/null
python3 /home/claude/genH/check_net.py /tmp/claude-0/nH.xml DimaQuadFC_H.kicad_sch.expected.json DimaQuadFC_H.kicad_sch.nc.json
kicad-cli sch export pdf -o DimaQuadFC_H_schematic.pdf DimaQuadFC_H.kicad_sch >/dev/null
pdftoppm -r ${RES:-80} -png DimaQuadFC_H_schematic.pdf /tmp/claude-0/schH
