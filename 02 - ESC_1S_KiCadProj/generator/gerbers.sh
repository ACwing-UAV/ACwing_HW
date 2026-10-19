set -e
cd /home/claude/outESCB
rm -rf gerber && mkdir gerber
kicad-cli pcb export gerbers -l F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o gerber/ DimaQuadESC_B.kicad_pcb >/dev/null
kicad-cli pcb export drill --drill-origin plot --excellon-separate-th -u mm -o gerber/ DimaQuadESC_B.kicad_pcb >/dev/null
(cd gerber && rm -f ../DimaQuadESC_B_gerber.zip && zip -q ../DimaQuadESC_B_gerber.zip *)
kicad-cli pcb export step -f -o DimaQuadESC_B.step DimaQuadESC_B.kicad_pcb 2>&1 | tail -1
kicad-cli sch export pdf -o DimaQuadESC_B_schematic.pdf DimaQuadESC_B.kicad_sch >/dev/null
ls gerber
