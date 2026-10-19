# Second Freerouting pass: the DSN carries the routed (unlocked) wires, Freerouting rips up and completes the rest.
set -e
cd /home/claude/outH
python3 /home/claude/genH/dsn_h.py DimaQuadFC_H.kicad_pcb
rm -f DimaQuadFC_H.ses; timeout 1200 xvfb-run -a java -jar /home/claude/tools/freerouting-1.9.0.jar -de DimaQuadFC_H.dsn -do DimaQuadFC_H.ses -mp 120 -mt 1 -oit 0.5 > /tmp/claude-0/frF2.log 2>&1 || true
test -s DimaQuadFC_H.ses
python3 /home/claude/genE/finish.py DimaQuadFC_H.kicad_pcb DimaQuadFC_H.ses /tmp/claude-0/hdrc2.rpt | tail -2
python3 /home/claude/genE/cleanup.py DimaQuadFC_H.kicad_pcb | tail -1
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('/home/claude/outH/DimaQuadFC_H.kicad_pcb')
pcbnew.WriteDRCReport(b,'/tmp/claude-0/hdrc2.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)" 2>/dev/null
grep -E "^\[|Found" /tmp/claude-0/hdrc2.rpt | grep -v silk | sed 's/(.*//' | sort | uniq -c
grep -A3 "^\[unconnected" /tmp/claude-0/hdrc2.rpt | grep "@" | head
