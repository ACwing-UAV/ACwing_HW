# DimaQuadFC rev C2 - full regeneration (KiCad 7 + pcbnew, Freerouting 1.9 with xvfb, shapely/numpy/pillow/ezdxf)
# paths: /home/claude/genC2 (scripts), /home/claude/outC2 (project), /home/claude/inC (mechanical handoff)
set -e
bash /home/claude/genC2/run.sh                 # schematic + netlist + check_net
bash /home/claude/genC2/prep.sh                # PCB from DXF/CSV, mech checks, planes/pours/fan-out, USB (A*), DSN
bash /home/claude/genC2/routeall.sh            # Freerouting -> import -> A* leftovers -> cleanup -> DRC
# if A* leaves MAG_C1 or a single connection open, rerun routeall.sh (Freerouting is not deterministic)
cd /home/claude/outC2
python3 /home/claude/genC2/silk_refs.py DimaQuadFC_C2.kicad_pcb DimaQuadFC_C2.kicad_sch.parts.json   # silkscreen labels (+ leader lines) + values
python3 /home/claude/genC2/make_projlib.py /home/claude/outC2   # every footprint into DimaQuad.pretty, links DimaQuad:<name>
python3 /home/claude/genC2/make_3d_c2.py /home/claude/outC2/3d   # MLPF, crystals
cp /usr/share/kicad/3dmodels/Package_DFN_QFN.3dshapes/QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm.step 3d/QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm.step
python3 /home/claude/genC2/assign_3d.py /home/claude/outC2
kicad-cli pcb export step -f -o DimaQuadFC_C2.step DimaQuadFC_C2.kicad_pcb
python3 /home/claude/genC2/bom_detail.py DimaQuadFC_C2.kicad_sch.parts.json DimaQuadFC_C2.kicad_pcb DimaQuadFC_C2_BoM.xlsx   # assembly BoM with MPNs
python3 /home/claude/genC2/step_mesh.py DimaQuadFC_C2.step /tmp/claude-0/meshC2.npz && python3 /home/claude/genC2/render_3d.py   # 3D views
python3 /home/claude/genC2/plot_routing.py F,In2,B DimaQuadFC_C2_routing.png
kicad-cli sch export pdf -o DimaQuadFC_C2_schematic.pdf DimaQuadFC_C2.kicad_sch
python3 /home/claude/genC2/costing.py DimaQuadFC_C2_BoM.xlsx   # costing sheet (prices in the script)
python3 /home/claude/genC2/cpl.py DimaQuadFC_C2.kicad_pcb DimaQuadFC_C2.kicad_sch.parts.json DimaQuadFC_C2_CPL.xlsx   # JLC CPL
rm -rf gerber && mkdir gerber
kicad-cli pcb export gerbers -l F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o gerber/ DimaQuadFC_C2.kicad_pcb
kicad-cli pcb export drill --drill-origin plot --excellon-separate-th -u mm -o gerber/ DimaQuadFC_C2.kicad_pcb
(cd gerber && rm -f ../DimaQuadFC_C2_gerber.zip && zip -q ../DimaQuadFC_C2_gerber.zip *)
