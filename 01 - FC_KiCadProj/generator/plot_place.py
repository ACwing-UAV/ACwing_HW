# placement map of both sides (courtyards, pads, tracks, vias); board 40 x 40 centred on (150, 100); bottom seen from the top
import sys, pcbnew
from PIL import Image, ImageDraw, ImageFont
b = pcbnew.LoadBoard(sys.argv[1]); out = sys.argv[2]
S = 22; W = 42 * S
im = Image.new('RGB', (2 * W + 20, W), 'white')
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
except Exception:
    font = None
for side in (0, 1):
    d = ImageDraw.Draw(im); ox = side * (W + 20)
    T = lambda x, y: (ox + (x - 129) * S, (y - 79) * S)
    for dr in b.GetDrawings():
        if dr.GetLayer() == pcbnew.Edge_Cuts and dr.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            d.line([T(dr.GetStart().x / 1e6, dr.GetStart().y / 1e6), T(dr.GetEnd().x / 1e6, dr.GetEnd().y / 1e6)], fill='black', width=2)
    for hx, hy in ((140, 90), (160, 90), (140, 110), (160, 110)):
        r = 3.6 if side else 3.0
        d.ellipse([*T(hx - r, hy - r), *T(hx + r, hy + r)], outline=(150, 150, 255))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_TRACK' and t.GetLayer() == (pcbnew.B_Cu if side else pcbnew.F_Cu):
            d.line([T(t.GetStart().x / 1e6, t.GetStart().y / 1e6), T(t.GetEnd().x / 1e6, t.GetEnd().y / 1e6)], fill=(0, 150, 0), width=max(1, int(t.GetWidth() / 1e6 * S)))
        elif t.GetClass() == 'PCB_VIA':
            x, y = t.GetPosition().x / 1e6, t.GetPosition().y / 1e6
            d.ellipse([*T(x - .25, y - .25), *T(x + .25, y + .25)], fill=(120, 120, 120))
    for f in b.GetFootprints():
        if f.IsFlipped() != bool(side):
            continue
        f.BuildCourtyardCaches()
        c = f.GetCourtyard(pcbnew.B_CrtYd if side else pcbnew.F_CrtYd)
        for i in range(c.OutlineCount()):
            o = c.Outline(i); pts = [T(o.CPoint(j).x / 1e6, o.CPoint(j).y / 1e6) for j in range(o.PointCount())]
            d.polygon(pts, outline='red')
        for p in f.Pads():
            bb = p.GetBoundingBox()
            d.rectangle([*T(bb.GetX() / 1e6, bb.GetY() / 1e6), *T(bb.GetRight() / 1e6, bb.GetBottom() / 1e6)], fill=(230, 160, 60))
        d.text(T(f.GetPosition().x / 1e6, f.GetPosition().y / 1e6), f.GetReference(), fill='blue', font=font)
    d.text((ox + 5, 5), 'TOP' if side == 0 else 'BOTTOM (seen from the top)', fill='black', font=font)
im.save(out)
