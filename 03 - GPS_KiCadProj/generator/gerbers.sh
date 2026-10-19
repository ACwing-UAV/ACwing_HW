set -e
cd /home/claude/outGPSD
rm -rf gerber && mkdir gerber
kicad-cli pcb export gerbers -l F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o gerber/ DimaQuadGPS_D.kicad_pcb >/dev/null
kicad-cli pcb export drill --drill-origin plot --excellon-separate-th -u mm -o gerber/ DimaQuadGPS_D.kicad_pcb >/dev/null
(cd gerber && rm -f ../DimaQuadGPS_D_gerber.zip && zip -q ../DimaQuadGPS_D_gerber.zip *)
kicad-cli pcb export step -f -o DimaQuadGPS_D.step DimaQuadGPS_D.kicad_pcb 2>&1 | tail -1
kicad-cli sch export pdf -o DimaQuadGPS_D_schematic.pdf DimaQuadGPS_D.kicad_sch >/dev/null
ls gerber
