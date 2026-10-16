cd /home/claude/outC2
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('DimaQuadFC_C2.kicad_pcb')
pcbnew.WriteDRCReport(b,'/tmp/claude-0/drc.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)
" 2>&1 | grep -v leak
grep -E "^\[" /tmp/claude-0/drc.rpt | grep -v lib_footprint | sed 's/actual.*//' | sort | uniq -c | sort -rn
python3 - <<'PY'
import re
t=open('/tmp/claude-0/drc.rpt').read()
for bl in re.split(r'\n(?=\[)', t):
    if bl.startswith(('[unconnected_items]','[clearance]','[via_dangling]','[track_dangling]','[shorting','[tracks_crossing','[hole_clearance]','[copper_edge','[items_not_allowed]')):
        items=[re.sub(r'\s+',' ',l.strip()) for l in bl.splitlines() if '@(' in l]
        print(bl.split(']')[0][1:],':',' <-> '.join(i.replace(' mm','') for i in items)[:240])
PY
