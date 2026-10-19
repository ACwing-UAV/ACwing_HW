set -e
cd /home/claude/outGPSD
python3 /home/claude/genGPSD/gen_sch_gps.py ACwing_GPS_D.kicad_sch
kicad-cli sch export netlist -o /tmp/claude-0/ngd.xml --format kicadxml ACwing_GPS_D.kicad_sch >/dev/null
python3 /home/claude/genGPSD/check_net.py /tmp/claude-0/ngd.xml ACwing_GPS_D.kicad_sch.expected.json ACwing_GPS_D.kicad_sch.nc.json
kicad-cli sch export pdf -o ACwing_GPS_D_schematic.pdf ACwing_GPS_D.kicad_sch >/dev/null
pdftoppm -r 90 -png ACwing_GPS_D_schematic.pdf /tmp/claude-0/gsch
