# quick placement map of both sides (courtyards, pads), board frame
import sys, pcbnew
from PIL import Image, ImageDraw
b = pcbnew.LoadBoard(sys.argv[1]); out = sys.argv[2]
S = 24; W = 28 * S
im = Image.new('RGB', (2 * W + 20, W), 'white')
for side in (0, 1):
    d = ImageDraw.Draw(im); ox = side * (W + 20)
    T = lambda x, y: (ox + (x - 136) * S, (y - 86) * S)
    d.rectangle([*T(137, 87), *T(163, 113)], outline='black')
    for hx, hy in ((142, 92), (158, 92), (142, 108), (158, 108)):
        d.ellipse([*T(hx - 2.6, hy - 2.6), *T(hx + 2.6, hy + 2.6)], outline=(180, 180, 255))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_TRACK' and t.GetLayer() == (pcbnew.B_Cu if side else pcbnew.F_Cu):
            d.line([T(t.GetStart().x / 1e6, t.GetStart().y / 1e6), T(t.GetEnd().x / 1e6, t.GetEnd().y / 1e6)], fill=(0, 150, 0), width=max(1, int(t.GetWidth() / 1e6 * S)))
        elif t.GetClass() == 'PCB_VIA':
            x, y = t.GetPosition().x / 1e6, t.GetPosition().y / 1e6
            d.ellipse([*T(x - .25, y - .25), *T(x + .25, y + .25)], fill=(120, 120, 120))
    for f in b.GetFootprints():
        if f.IsFlipped() != bool(side):
            continue
        c = f.GetCourtyard(pcbnew.B_CrtYd if side else pcbnew.F_CrtYd)
        for i in range(c.OutlineCount()):
            o = c.Outline(i); pts = [T(o.CPoint(j).x / 1e6, o.CPoint(j).y / 1e6) for j in range(o.PointCount())]
            d.polygon(pts, outline='red')
        for p in f.Pads():
            bb = p.GetBoundingBox()
            d.rectangle([*T(bb.GetX() / 1e6, bb.GetY() / 1e6), *T(bb.GetRight() / 1e6, bb.GetBottom() / 1e6)], fill=(230, 160, 60))
        d.text(T(f.GetPosition().x / 1e6, f.GetPosition().y / 1e6), f.GetReference(), fill='blue')
    d.text((ox + 5, 5), 'TOP' if side == 0 else 'BOTTOM (seen from the top)', fill='black')
im.save(out)
