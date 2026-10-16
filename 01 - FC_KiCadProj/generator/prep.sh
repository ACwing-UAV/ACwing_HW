cd /home/claude/outC2
python3 /home/claude/genC2/gen_pcb.py /home/claude/outC2 /home/claude/inC/DimaQuadFC_C_Edge_Cuts.dxf /home/claude/inC/DimaQuadFC_C_Keepouts.dxf /home/claude/outC2/DimaQuadFC_C2_Placement.csv /tmp/claude-0/n.xml
python3 /home/claude/genC2/check_mech.py DimaQuadFC_C2.kicad_pcb /home/claude/outC2/DimaQuadFC_C2_Placement.csv
python3 /home/claude/genC2/route.py DimaQuadFC_C2.kicad_pcb
python3 /home/claude/genC2/astar.py DimaQuadFC_C2.kicad_pcb USB_DM USB_DP | grep "A\*"
python3 /home/claude/genC2/lock_usb.py DimaQuadFC_C2.kicad_pcb
python3 /home/claude/genC2/dsn.py DimaQuadFC_C2.kicad_pcb
