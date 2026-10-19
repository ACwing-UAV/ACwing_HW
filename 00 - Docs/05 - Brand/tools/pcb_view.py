# Photo-like PCB views (top and bottom, bottom mirrored as seen from below) from the KiCad board:
# green soldermask, lighter copper under the mask, gold pads (mask openings), white silkscreen, drilled holes.
# python3 pcb_view.py <board.kicad_pcb> <out.png> [title]
import sys, os, subprocess, tempfile, io
import cairosvg, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pcbnew
pcb, out = sys.argv[1], sys.argv[2]; title = sys.argv[3] if len(sys.argv) > 3 else ''
W = 1100
tmp = tempfile.mkdtemp()
def layer(lname, mirror):
    f = os.path.join(tmp, lname.replace('.', '_') + ('_m' if mirror else '') + '.svg')
    # Edge.Cuts in every export so all layers share the same page box
    cmd = ['kicad-cli', 'pcb', 'export', 'svg', '-o', f, '--layers', lname + ',Edge.Cuts', '--black-and-white',
           '--page-size-mode', '2', '--exclude-drawing-sheet'] + (['--mirror'] if mirror else []) + [pcb]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    png = cairosvg.svg2png(url=f, output_width=W, background_color='white')
    return np.array(Image.open(io.BytesIO(png)).convert('L')) < 128
def side(bottom):
    m = bottom
    edge = layer('Edge.Cuts', m)
    cu = layer('B.Cu' if bottom else 'F.Cu', m) & ~edge
    mask = layer('B.Mask' if bottom else 'F.Mask', m) & ~edge
    silk = layer('B.SilkS' if bottom else 'F.SilkS', m) & ~edge
    H = edge.shape[0]
    # mapping board mm -> pixels from the outline extent (edge pixels) and the board edge bounding box
    b = pcbnew.LoadBoard(pcb); bb = b.GetBoardEdgesBoundingBox()
    x0, y0 = pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()); bw = pcbnew.ToMM(bb.GetWidth())
    ys, xs = np.nonzero(edge); px0, px1, py0 = xs.min(), xs.max(), ys.min()
    s = (px1 - px0) / bw
    def M(xmm, ymm):
        u = xmm - x0; v = ymm - y0
        if m: u = bw - u
        return (px0 + u * s, py0 + v * s)
    ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
    bimg = Image.new('L', (W, H), 0); bd = ImageDraw.Draw(bimg)
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i); pts = [M(pcbnew.ToMM(o.CPoint(k).x), pcbnew.ToMM(o.CPoint(k).y)) for k in range(o.PointCount())]
        bd.polygon(pts, fill=255)
    board = (np.array(bimg) > 0) | edge
    rgb = np.zeros((H, W, 3), np.uint8); rgb[:] = (255, 255, 255)
    rgb[board] = (18, 74, 46)
    rgb[board & cu] = (36, 110, 62)
    rgb[board & mask] = (201, 160, 72)
    rgb[board & silk & ~mask] = (245, 245, 240)
    # drills: holes of every pad and via, from the board itself
    im = Image.fromarray(rgb); d = ImageDraw.Draw(im)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            ds = p.GetDrillSize()
            if ds.x <= 0: continue
            q = p.GetPosition(); cx, cy = M(pcbnew.ToMM(q.x), pcbnew.ToMM(q.y))
            rx, ry = pcbnew.ToMM(ds.x) / 2 * s, pcbnew.ToMM(ds.y) / 2 * s
            if abs(p.GetOrientationDegrees()) % 180 == 90: rx, ry = ry, rx
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(255, 255, 255))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            q = t.GetPosition(); cx, cy = M(pcbnew.ToMM(q.x), pcbnew.ToMM(q.y))
            r = pcbnew.ToMM(t.GetDrillValue()) / 2 * s
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 40, 25))
    return im.crop((max(0, px0 - 15), max(0, py0 - 15), min(W, px1 + 15), min(H, ys.max() + 15)))
a, c = side(False), side(True)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
except Exception:
    font = ImageFont.load_default()
pad = 60 if title else 50
im = Image.new('RGB', (a.width + c.width + 60, max(a.height, c.height) + pad + 50), 'white')
im.paste(a, (20, pad)); im.paste(c, (a.width + 40, pad))
d = ImageDraw.Draw(im)
if title: d.text((20, 12), title, fill=(30, 30, 30), font=font)
f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22) if font != ImageFont.load_default() else font
d.text((20 + a.width / 2 - 20, pad + a.height + 12), 'Top', fill=(90, 90, 90), font=f2)
d.text((a.width + 40 + c.width / 2 - 110, pad + c.height + 12), 'Bottom (seen from below)', fill=(90, 90, 90), font=f2)
im.save(out)
print('wrote', out, im.size)
