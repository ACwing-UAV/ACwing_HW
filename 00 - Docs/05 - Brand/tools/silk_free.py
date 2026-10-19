# Free silkscreen area finder: largest logo box on a board side (no pads, courtyards, silk, holes).
import sys, math, pcbnew
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
OX, OY = 150.0, 100.0
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def polyset(ps):
    return unary_union([Polygon([B(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())]) for i in range(ps.OutlineCount())])
def bbox_poly(bb):
    a = B(pcbnew.VECTOR2I(bb.GetLeft(), bb.GetBottom())); c = B(pcbnew.VECTOR2I(bb.GetRight(), bb.GetTop()))
    return box(min(a[0], c[0]), min(a[1], c[1]), max(a[0], c[0]), max(a[1], c[1]))
def blocked(b, bottom, ignore=()):
    cu, silk, crt = (pcbnew.B_Cu, pcbnew.B_SilkS, pcbnew.B_CrtYd) if bottom else (pcbnew.F_Cu, pcbnew.F_SilkS, pcbnew.F_CrtYd)
    mask = pcbnew.B_Mask if bottom else pcbnew.F_Mask
    obs = []
    for f in b.GetFootprints():
        if f.GetReference() in ignore:
            continue
        for p in f.Pads():
            if p.IsOnLayer(mask) or p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, cu if p.IsOnLayer(cu) else pcbnew.F_Cu, pcbnew.FromMM(0.25), pcbnew.FromMM(0.02))
                obs.append(polyset(s))
        if f.IsFlipped() == bottom:
            f.BuildCourtyardCaches()
            c = polyset(f.GetCourtyard(crt))
            if not c.is_empty:
                obs.append(c.buffer(0.1))
        for it in list(f.GraphicalItems()) + [f.Reference(), f.Value()]:
            if it.GetLayer() == silk and (not hasattr(it, 'IsVisible') or it.IsVisible()):
                obs.append(bbox_poly(it.GetBoundingBox()).buffer(0.2))
    for d in b.GetDrawings():
        if d.GetLayer() == silk:
            obs.append(bbox_poly(d.GetBoundingBox()).buffer(0.2))
    return unary_union(obs)
def free_area(b, bottom, ignore=()):
    ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
    return polyset(ps).buffer(-0.5).difference(blocked(b, bottom, ignore))
def best_box(free, aspect, hmin=3.0, hmax=12.0, step=0.25, prefer=(0, 0)):
    """largest box w = aspect * h inside 'free'; ties -> nearest to 'prefer'."""
    x0, y0, x1, y1 = free.bounds
    h = hmax
    while h >= hmin:
        w = aspect * h; best = None
        y = y0 + h / 2
        while y <= y1 - h / 2:
            x = x0 + w / 2
            while x <= x1 - w / 2:
                if free.contains(box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)):
                    d = math.dist((x, y), prefer)
                    if best is None or d < best[0]:
                        best = (d, x, y)
                x += step
            y += step
        if best:
            return h, best[1], best[2]
        h -= 0.5
    return None
if __name__ == '__main__':
    b = pcbnew.LoadBoard(sys.argv[1])
    for bottom in (False, True):
        fr = free_area(b, bottom)
        for kind, asp in (('Full', 1.154), ('Mark', 1.535), ('Full+text', 1.154 * 0.72)):
            print('bottom' if bottom else 'top', kind, best_box(fr, asp))
