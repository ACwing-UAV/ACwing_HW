# DimaQuadGPS rev B - full regeneration (KiCad 7 + pcbnew, Freerouting 1.9 with xvfb, shapely, openpyxl, cadquery)
# paths: /home/claude/genGPSD (scripts), /home/claude/outGPSD (project); uses genD/kisch.py, sexp.py, silk_refs.py, step_mesh.py
set -e
bash /home/claude/genGPSD/run_sch.sh                                                   # schematic + netlist check
cd /home/claude/outGPSD
python3 /home/claude/genGPSD/gen_pcb_gps.py /home/claude/outGPSD /tmp/claude-0/ngd.xml   # outline, placement, zones, U3 escape
bash /home/claude/genGPSD/loop_route.sh                                                 # Freerouting, GND stitching, DRC
python3 /home/claude/genD/silk_refs.py DimaQuadGPS_D.kicad_pcb DimaQuadGPS_D.kicad_sch.parts.json | grep labels
python3 /home/claude/genGPSD/make_3d_gps.py /home/claude/outGPSD/3d
cp /home/claude/models_e/JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal.step 3d/
python3 /home/claude/genGPSD/gps_finish.py /home/claude/outGPSD                         # silk extras, project library, 3D links
python3 -c "
import pcbnew
b=pcbnew.LoadBoard('/home/claude/outGPSD/DimaQuadGPS_D.kicad_pcb')
pcbnew.WriteDRCReport(b,'/home/claude/outGPSD/DimaQuadGPS_D_DRC.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep Found DimaQuadGPS_D_DRC.rpt
python3 /home/claude/genGPSD/gps_bom.py /home/claude/outGPSD
python3 /mnt/skills/public/xlsx/scripts/recalc.py DimaQuadGPS_D_BoM.xlsx > /dev/null
python3 /home/claude/genGPSD/cpl.py DimaQuadGPS_D.kicad_pcb DimaQuadGPS_D.kicad_sch.parts.json DimaQuadGPS_D_CPL.xlsx
bash /home/claude/genGPSD/gerbers.sh > /dev/null
python3 /home/claude/genD/step_mesh.py DimaQuadGPS_D.step /tmp/claude-0/meshGPSD.npz > /dev/null
python3 /home/claude/genGPSD/render_gps.py
