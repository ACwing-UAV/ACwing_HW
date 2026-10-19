# DimaQuadESC rev B - full regeneration (KiCad 7 + pcbnew, Freerouting 1.9 with xvfb, shapely, openpyxl, cadquery)
# paths: /home/claude/genESCB (scripts), /home/claude/outESCB (project). Uses genD/make_3d.py, the rev E footprint library
# (outE/DimaQuad.pretty) and 3D models (outE/3d).
set -e
bash /home/claude/genESCB/run_sch.sh                                                     # schematic + netlist check
cd /home/claude/outESCB
python3 /home/claude/genESCB/gen_pcb_esc.py /home/claude/outESCB /tmp/claude-0/nescb.xml   # outline, placement, rules
bash /home/claude/genESCB/route_all.sh                                                   # planes, pours, pre-routes, Freerouting, DRC
python3 /home/claude/genESCB/make_3d_esc.py /home/claude/outESCB/3d
python3 /home/claude/genESCB/esc_finish.py /home/claude/outESCB                           # silk legend, project library, 3D links
python3 /home/claude/genESCB/silk_refs.py DimaQuadESC_B.kicad_pcb DimaQuadESC_B.kicad_sch.parts.json | grep labels   # references placed around the legend
python3 /home/claude/genESCB/silk_fix_b.py DimaQuadESC_B.kicad_pcb
python3 /home/claude/genESCB/make_projlib_b.py /home/claude/outESCB
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('/home/claude/outESCB/DimaQuadESC_B.kicad_pcb')
pcbnew.WriteDRCReport(b,'/home/claude/outESCB/DimaQuadESC_B_DRC.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep Found DimaQuadESC_B_DRC.rpt
python3 /home/claude/genESCB/esc_bom.py /home/claude/outESCB
python3 /mnt/skills/public/xlsx/scripts/recalc.py DimaQuadESC_B_BoM.xlsx > /dev/null
python3 /home/claude/genESCB/cpl.py DimaQuadESC_B.kicad_pcb DimaQuadESC_B.kicad_sch.parts.json DimaQuadESC_B_CPL.xlsx
bash /home/claude/genESCB/gerbers.sh > /dev/null
python3 /home/claude/genESCB/step_mesh.py DimaQuadESC_B.step /tmp/claude-0/meshESCB.npz > /dev/null
python3 /home/claude/genESCB/render_esc.py
# stack check (needs the FC rev H and GPS rev C boards and meshes)
python3 /home/claude/stack/stack_check.py 6 _s6 && python3 /home/claude/stack/stack_check.py 8 _s8 && python3 /home/claude/stack/build_page_data.py
