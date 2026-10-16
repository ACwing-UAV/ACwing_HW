set -e
cd /home/claude/outC2
timeout 3000 xvfb-run -a java -jar /home/claude/tools/freerouting-1.9.0.jar -de DimaQuadFC_C2.dsn -do DimaQuadFC_C2.ses -mp 40 -mt 1 > /tmp/claude-0/frC2.log 2>&1
grep completed /tmp/claude-0/frC2.log
python3 /home/claude/genC2/finish.py DimaQuadFC_C2.kicad_pcb DimaQuadFC_C2.ses | tail -1
python3 /home/claude/genC2/astar.py DimaQuadFC_C2.kicad_pcb | grep "A\*"
python3 /home/claude/genC2/cleanup.py DimaQuadFC_C2.kicad_pcb | tail -1
bash /home/claude/genC2/drcC.sh | grep -v "^ *[0-9]* \[silk"
