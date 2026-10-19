set -e
cd /home/claude/outFlow
python3 /home/claude/genFlow/gen_sch_flow.py DimaQuadFlow_A.kicad_sch
kicad-cli sch export netlist -o /tmp/claude-0/nf.xml --format kicadxml DimaQuadFlow_A.kicad_sch >/dev/null
python3 /home/claude/genFlow/check_net.py /tmp/claude-0/nf.xml DimaQuadFlow_A.kicad_sch.expected.json DimaQuadFlow_A.kicad_sch.nc.json
kicad-cli sch export pdf -o DimaQuadFlow_A_schematic.pdf DimaQuadFlow_A.kicad_sch >/dev/null
pdftoppm -r 90 -png DimaQuadFlow_A_schematic.pdf /tmp/claude-0/fsch
