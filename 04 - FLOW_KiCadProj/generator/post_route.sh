# ACwing Flow rev A - outputs after routing (silk, library + 3D, DRC, BoM, CPL, Gerbers, STEP, renders)
set -e
cd /home/claude/outFlow
python3 /home/claude/genD/silk_refs.py ACwing_Flow_A.kicad_pcb ACwing_Flow_A.kicad_sch.parts.json | grep labels
python3 /home/claude/genFlow/flow_finish.py /home/claude/outFlow
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('/home/claude/outFlow/ACwing_Flow_A.kicad_pcb')
pcbnew.WriteDRCReport(b,'/home/claude/outFlow/ACwing_Flow_A_DRC.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep Found ACwing_Flow_A_DRC.rpt
python3 /home/claude/genFlow/flow_bom.py /home/claude/outFlow
python3 /mnt/skills/public/xlsx/scripts/recalc.py ACwing_Flow_A_BoM.xlsx > /dev/null
python3 /home/claude/genFlow/cpl.py ACwing_Flow_A.kicad_pcb ACwing_Flow_A.kicad_sch.parts.json ACwing_Flow_A_CPL.xlsx
bash /home/claude/genFlow/gerbers.sh > /dev/null
python3 /home/claude/genD/step_mesh.py ACwing_Flow_A.step /tmp/claude-0/meshFlow.npz > /dev/null
python3 /home/claude/genFlow/render_flow.py
