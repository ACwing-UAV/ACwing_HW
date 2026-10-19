set -e
cd /home/claude/outESCB
python3 /home/claude/genESCB/esc_power.py DimaQuadESC_B.kicad_pcb | tail -2
python3 /home/claude/genESCB/route_esc.py DimaQuadESC_B.kicad_pcb /home/claude/outESCB 2>&1 | grep -v "^$" | tail -4
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('/home/claude/outESCB/DimaQuadESC_B.kicad_pcb')
pcbnew.WriteDRCReport(b,'/tmp/claude-0/edrcb.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep -E "^\[|Found" /tmp/claude-0/edrcb.rpt | sed 's/(.*//' | sort | uniq -c | grep -v "lib_foot\|silk"
python3 - <<'PY'
import re
t=open('/tmp/claude-0/edrcb.rpt').read()
for bl in re.split(r'\n(?=\[)', t):
    if bl.startswith(('[unconnected','[clearance','[copper_edge','[starved','[hole','[items_not','[track_dang','[via_dang','[isolated')):
        items=[re.sub(r'\s+',' ',l.strip()) for l in bl.splitlines() if '@(' in l]
        print(bl.split(']')[0][1:],':',' <-> '.join(items)[:230])
PY
