cd /work/acwing_hw
mkdir -p /tmp/rend
for p in ${BOARDS:-"01 - FC_KiCadProj/ACwing_FC_A" "02 - ESC_1S_KiCadProj/ACwing_ESC1S_A" "03 - GPS_KiCadProj/ACwing_GPS_A" "04 - FLOW_KiCadProj/ACwing_Flow_A"}; do
 n=$(basename "$p")
 R="xvfb-run -a -s \"-screen 0 1920x1080x24\" kicad-cli pcb render --quality high --floor"
 eval $R --side top -w 1000 -h 1000 --zoom 0.97 -o /tmp/rend/${n}_top.png \"$p.kicad_pcb\" >/dev/null 2>&1
 eval $R --side bottom -w 1000 -h 1000 --zoom 0.97 -o /tmp/rend/${n}_bot.png \"$p.kicad_pcb\" >/dev/null 2>&1
 eval $R --side top --perspective --rotate \"-50,0,-30\" --zoom 0.75 -w 1000 -h 1000 -o /tmp/rend/${n}_iso.png \"$p.kicad_pcb\" >/dev/null 2>&1
 ls /tmp/rend | grep $n | tr "\n" " "; echo
done
