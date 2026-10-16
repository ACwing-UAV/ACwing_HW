set -e
cd /home/claude/genC2 && python3 gen_sch.py /home/claude/outC2/DimaQuadFC_C2.kicad_sch && python3 projlib_links.py /home/claude/outC2/DimaQuadFC_C2.kicad_sch
cd /home/claude/outC2
kicad-cli sch export netlist -o /tmp/claude-0/n.xml --format kicadxml DimaQuadFC_C2.kicad_sch >/dev/null
python3 /home/claude/genC2/check_net.py /tmp/claude-0/n.xml DimaQuadFC_C2.kicad_sch.expected.json DimaQuadFC_C2.kicad_sch.nc.json
kicad-cli sch export pdf -o /tmp/claude-0/sch.pdf DimaQuadFC_C2.kicad_sch >/dev/null
pdftoppm -r ${RES:-110} -png /tmp/claude-0/sch.pdf /tmp/claude-0/sch
