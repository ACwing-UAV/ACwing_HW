set -e
cd /work/acwing_hw
D=("00 - FC_Docs" "01 - ESC_1S_Docs" "02 - GPS_Docs" "03 - FLOW_Docs")
P=("01 - FC_KiCadProj/ACwing_FC_A" "02 - ESC_1S_KiCadProj/ACwing_ESC1S_A" "03 - GPS_KiCadProj/ACwing_GPS_A" "04 - FLOW_KiCadProj/ACwing_Flow_A")
for i in ${IDX:-0 1 2 3}; do
  p="${P[$i]}"; d="00 - Docs/${D[$i]}"; n=$(basename "$p"); dir=$(dirname "$p")
  echo "== $n"
  kicad-cli pcb drc -o "$d/${n}_DRC.rpt" "$p.kicad_pcb" >/dev/null 2>&1; grep "^\*\* Found" "$d/${n}_DRC.rpt" | tr '\n' ' '; echo
  kicad-cli sch erc -o /tmp/$n.erc.rpt "$p.kicad_sch" >/dev/null 2>&1; grep -E "^\*\* ERC|Errors|Warnings" /tmp/$n.erc.rpt | tail -2 | tr '\n' ' '; echo
  layers="F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
  grep -q '"In1.Cu"' "$p.kicad_pcb" && layers="F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
  rm -rf /tmp/g_$n && mkdir /tmp/g_$n
  kicad-cli pcb export gerbers -l $layers --subtract-soldermask --use-drill-file-origin -o /tmp/g_$n/ "$p.kicad_pcb" >/dev/null
  kicad-cli pcb export drill --drill-origin plot --excellon-separate-th -u mm -o /tmp/g_$n/ "$p.kicad_pcb" >/dev/null
  (cd /tmp/g_$n && rm -f "/work/acwing_hw/$d/${n}_gerber.zip" && zip -q "/work/acwing_hw/$d/${n}_gerber.zip" *) ; ls /tmp/g_$n | wc -l
  kicad-cli pcb export step -f -o "$d/${n}.step" "$p.kicad_pcb" 2>&1 | tail -1
  kicad-cli sch export pdf -o "$d/${n}_schematic.pdf" "$p.kicad_sch" >/dev/null 2>&1
  kicad-cli pcb export pos --format csv --units mm --side both --use-drill-file-origin -o /tmp/$n.pos.csv "$p.kicad_pcb" >/dev/null 2>&1
done
