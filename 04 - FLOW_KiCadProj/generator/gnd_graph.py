# GND connectivity check: union-find over filled fragments, vias, pads and tracks (both layers)
import sys, pcbnew
from shapely.geometry import Polygon, Point, LineString
b = pcbnew.LoadBoard(sys.argv[1]); NET = sys.argv[2] if len(sys.argv) > 2 else 'GND'
def mm(v): return (pcbnew.ToMM(v.x), pcbnew.ToMM(v.y))
items = []   # (label, layerset, geom)
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() != NET: continue
    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
        if not z.IsOnLayer(L): continue
        fp = z.GetFilledPolysList(L)
        for i in range(fp.OutlineCount()):
            o = fp.Outline(i); g = Polygon([mm(o.CPoint(j)) for j in range(o.PointCount())])
            items.append(('zone%s#%d@%.2f,%.2f' % ('F' if L == pcbnew.F_Cu else 'B', i, g.centroid.x, g.centroid.y), {L}, g))
for t in b.GetTracks():
    if t.GetNetname() != NET: continue
    if t.GetClass() == 'PCB_VIA':
        items.append(('via@%.2f,%.2f' % mm(t.GetPosition()), {pcbnew.F_Cu, pcbnew.B_Cu}, Point(mm(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2)))
    else:
        items.append(('trk', {t.GetLayer()}, LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2)))
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() != NET: continue
        Ls = {L for L in (pcbnew.F_Cu, pcbnew.B_Cu) if p.IsOnLayer(L)}
        sp = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(sp, list(Ls)[0], 0, pcbnew.FromMM(0.005))
        items.append(('%s.%s' % (f.GetReference(), p.GetNumber()), Ls, Polygon([mm(sp.Outline(0).CPoint(j)) for j in range(sp.Outline(0).PointCount())])))
par = list(range(len(items)))
def f_(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        if items[i][1] & items[j][1] and items[i][2].buffer(0.001).intersects(items[j][2]):
            par[f_(i)] = f_(j)
groups = {}
for i in range(len(items)): groups.setdefault(f_(i), []).append(items[i][0])
gs = sorted(groups.values(), key=len, reverse=True)
print(NET, 'groups', len(gs))
for g in gs[1:]: print('  isolated:', [x for x in g if x != 'trk'])
