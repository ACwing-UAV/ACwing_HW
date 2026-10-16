# connects one top pad and one bottom pad of the same net with: F.Cu stub - via - B.Cu stub (searches the via spot)
import sys, math, pcbnew
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
BOARD, REF_T, NUM_T, REF_B, NUM_B = sys.argv[1:6]
W = 0.15; CL = 0.105
OX, OY = 150.0, 100.0
b = pcbnew.LoadBoard(BOARD)
def mm(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def P(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY - y))
def padp(p, L):
    s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, L, 0, pcbnew.FromMM(0.005))
    return unary_union([Polygon([mm(s.Outline(i).CPoint(j)) for j in range(s.Outline(i).PointCount())]) for i in range(s.OutlineCount())])
pt = [p for p in b.FindFootprintByReference(REF_T).Pads() if p.GetNumber() == NUM_T][0]
pb = [p for p in b.FindFootprintByReference(REF_B).Pads() if p.GetNumber() == NUM_B][0]
net = pt.GetNetname()
ob = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}; holes = []
for f in b.GetFootprints():
    for p in f.Pads():
        for L in ob:
            if p.IsOnLayer(L) and p.GetNetname() != net:
                ob[L].append(padp(p, L).buffer(CL + (0.9 if f.GetReference().startswith('TP') else 0)))
for t in b.GetTracks():
    if t.GetNetname() == net: continue
    if t.GetClass() == 'PCB_VIA':
        g = Point(mm(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2 + CL)
        for L in ob: ob[L].append(g)
        holes.append(Point(mm(t.GetPosition())))
    elif t.GetLayer() in ob:
        ob[t.GetLayer()].append(LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2 + CL))
for z in b.Zones():
    if z.GetIsRuleArea() or not z.IsOnLayer(pcbnew.F_Cu) or z.GetNetname() == net: continue
    o = z.Outline()
    ob[pcbnew.F_Cu].append(Polygon([mm(o.Outline(0).CPoint(j)) for j in range(o.Outline(0).PointCount())]).buffer(CL))
OBF, OBB = unary_union(ob[pcbnew.F_Cu]), unary_union(ob[pcbnew.B_Cu])
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
inner = Polygon([mm(ps.Outline(0).CPoint(j)) for j in range(ps.Outline(0).PointCount())]).buffer(-0.5)
ct, cb = mm(pt.GetPosition()), mm(pb.GetPosition())
best = None
for i in range(-60, 61):
    for j in range(-60, 61):
        q = ((ct[0] + cb[0]) / 2 + i * 0.025, (ct[1] + cb[1]) / 2 + j * 0.025)
        v = Point(q).buffer(0.225)
        if not inner.contains(v) or v.intersects(OBF) or v.intersects(OBB): continue
        if any(Point(q).distance(h) < 0.45 + 0.25 for h in holes): continue
        if LineString([ct, q]).buffer(W / 2).intersects(OBF) or LineString([cb, q]).buffer(W / 2).intersects(OBB): continue
        d = math.dist(ct, q) + math.dist(cb, q)
        if best is None or d < best[0]: best = (d, q)
if best is None:
    print('no via spot for', net); sys.exit(1)
q = best[1]
for (a, L) in ((ct, pcbnew.F_Cu), (cb, pcbnew.B_Cu)):
    t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*q)); t.SetWidth(pcbnew.FromMM(W)); t.SetLayer(L); t.SetNet(b.FindNet(net)); b.Add(t)
v = pcbnew.PCB_VIA(b); v.SetPosition(P(*q)); v.SetWidth(pcbnew.FromMM(0.45)); v.SetDrill(pcbnew.FromMM(0.2)); v.SetNet(b.FindNet(net)); b.Add(v)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD, b)
print('%s: via at (%.2f, %.2f), path %.2f mm' % (net, q[0], q[1], best[0]))
