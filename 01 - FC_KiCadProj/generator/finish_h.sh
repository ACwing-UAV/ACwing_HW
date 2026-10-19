# DimaQuadFC rev H - outputs after routing (silkscreen, project library, DRC, BoM, CPL, Gerber, STEP, renders)
set -e
cd /home/claude/outH
python3 /home/claude/genH/silk_refs.py DimaQuadFC_H.kicad_pcb DimaQuadFC_H.kicad_sch.parts.json | grep labels
python3 /home/claude/genH/silk_labels_h.py DimaQuadFC_H.kicad_pcb
python3 /home/claude/genH/silk_fix.py DimaQuadFC_H.kicad_pcb
python3 /home/claude/genH/silk_edge_fix.py DimaQuadFC_H.kicad_pcb
python3 /home/claude/genH/make_projlib.py /home/claude/outH
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('/home/claude/outH/DimaQuadFC_H.kicad_pcb')
pcbnew.WriteDRCReport(b,'/home/claude/outH/DimaQuadFC_H_DRC.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)" 2>/dev/null
grep Found DimaQuadFC_H_DRC.rpt
python3 /home/claude/genH/bom_detail.py DimaQuadFC_H.kicad_sch.parts.json DimaQuadFC_H.kicad_pcb DimaQuadFC_H_BoM.xlsx
python3 /home/claude/genH/costing.py DimaQuadFC_H_BoM.xlsx
python3 /mnt/skills/public/xlsx/scripts/recalc.py DimaQuadFC_H_BoM.xlsx > /dev/null
python3 /home/claude/genH/jlc_bom.py DimaQuadFC_H.kicad_sch.parts.json DimaQuadFC_H_BoM_JLCPCB.xlsx
python3 /home/claude/genH/cpl.py DimaQuadFC_H.kicad_pcb DimaQuadFC_H.kicad_sch.parts.json DimaQuadFC_H_CPL.xlsx
bash /home/claude/genH/gerbers_h.sh
kicad-cli pcb export dxf -l Edge.Cuts --ou mm --exclude-refdes --exclude-value -o DimaQuadFC_H_outline.dxf DimaQuadFC_H.kicad_pcb > /dev/null 2>&1 || kicad-cli pcb export dxf -l Edge.Cuts -o DimaQuadFC_H_outline.dxf DimaQuadFC_H.kicad_pcb > /dev/null
kicad-cli sch export pdf -o DimaQuadFC_H_schematic.pdf DimaQuadFC_H.kicad_sch > /dev/null
python3 /home/claude/genH/step_mesh.py DimaQuadFC_H.step /tmp/claude-0/meshH.npz > /dev/null
python3 /home/claude/genH/render_3d.py
PCB=/home/claude/outH/DimaQuadFC_H.kicad_pcb python3 /home/claude/genH/plot_routing.py F,In2,B DimaQuadFC_H_routing.png
