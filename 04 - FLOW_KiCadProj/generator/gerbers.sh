set -e
cd /home/claude/outFlow
rm -rf gerber && mkdir gerber
kicad-cli pcb export gerbers -l F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o gerber/ DimaQuadFlow_A.kicad_pcb >/dev/null
kicad-cli pcb export drill --drill-origin plot --excellon-separate-th -u mm -o gerber/ DimaQuadFlow_A.kicad_pcb >/dev/null
(cd gerber && rm -f ../DimaQuadFlow_A_gerber.zip && zip -q ../DimaQuadFlow_A_gerber.zip *)
kicad-cli pcb export step -f -o DimaQuadFlow_A.step DimaQuadFlow_A.kicad_pcb 2>&1 | tail -1
kicad-cli sch export pdf -o DimaQuadFlow_A_schematic.pdf DimaQuadFlow_A.kicad_sch >/dev/null
ls gerber
