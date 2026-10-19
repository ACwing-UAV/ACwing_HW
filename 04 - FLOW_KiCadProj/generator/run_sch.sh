set -e
cd /home/claude/outFlow
python3 /home/claude/genFlow/gen_sch_flow.py ACwing_Flow_A.kicad_sch
kicad-cli sch export netlist -o /tmp/claude-0/nf.xml --format kicadxml ACwing_Flow_A.kicad_sch >/dev/null
python3 /home/claude/genFlow/check_net.py /tmp/claude-0/nf.xml ACwing_Flow_A.kicad_sch.expected.json ACwing_Flow_A.kicad_sch.nc.json
kicad-cli sch export pdf -o ACwing_Flow_A_schematic.pdf ACwing_Flow_A.kicad_sch >/dev/null
pdftoppm -r 90 -png ACwing_Flow_A_schematic.pdf /tmp/claude-0/fsch
