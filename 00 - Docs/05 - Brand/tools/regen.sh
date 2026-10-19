#!/bin/bash
# regenerate fabrication outputs of one board in its project folder: gerbers + drill (zip), STEP, schematic PDF, DRC
set -e
DIR="$1"; N="$2"; LAYERS="$3"
cd "$DIR"
rm -rf gerber && mkdir gerber
kicad-cli pcb export gerbers -l "$LAYERS" --subtract-soldermask --use-drill-file-origin -o gerber/ $N.kicad_pcb >/dev/null
kicad-cli pcb export drill --drill-origin plot --excellon-separate-th -u mm -o gerber/ $N.kicad_pcb >/dev/null
(cd gerber && rm -f ../${N}_gerber.zip && zip -q ../${N}_gerber.zip *)
kicad-cli pcb export step -f --subst-models -o $N.step $N.kicad_pcb 2>&1 | tail -1
kicad-cli sch export pdf -o ${N}_schematic.pdf $N.kicad_sch >/dev/null 2>&1
python3 - $N <<'P' 2>&1 | grep -v leak
import pcbnew, sys, re
n = sys.argv[1]; b = pcbnew.LoadBoard(n + '.kicad_pcb')
pcbnew.WriteDRCReport(b, n + '_DRC.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True)
print('  ' + ' | '.join(re.findall(r'Found [^*\n]*', open(n + '_DRC.rpt').read())))
P
echo "  gerber files: $(ls gerber | wc -l)"
