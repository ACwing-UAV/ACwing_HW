#!/bin/bash
# silkscreen previews (mask openings + silk + outline) for every board, top and bottom (bottom mirrored)
S=$1; shift; mkdir -p "$S"
for p in "$@"; do n=$(basename "$p" .kicad_pcb)
 kicad-cli pcb export svg -o "$S/${n}_top.svg" --layers F.Mask,F.SilkS,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet "$p" >/dev/null 2>&1
 kicad-cli pcb export svg -o "$S/${n}_bot.svg" --layers B.Mask,B.SilkS,Edge.Cuts --mirror --page-size-mode 2 --exclude-drawing-sheet "$p" >/dev/null 2>&1
done
python3 - "$S" <<'P'
import cairosvg, glob, sys, os
from PIL import Image
S = sys.argv[1]
for f in glob.glob(S + '/*_top.svg') + glob.glob(S + '/*_bot.svg'):
    cairosvg.svg2png(url=f, write_to=f[:-4] + '.png', output_width=900, background_color='white')
for t in glob.glob(S + '/*_top.png'):
    a = Image.open(t); c = Image.open(t.replace('_top', '_bot'))
    im = Image.new('RGB', (a.width + c.width + 20, max(a.height, c.height)), 'white'); im.paste(a, (0, 0)); im.paste(c, (a.width + 20, 0)); im.save(t.replace('_top', '_pair'))
P
