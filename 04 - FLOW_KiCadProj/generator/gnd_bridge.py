# Join isolated GND groups: a via where an isolated group's pour on one layer overlaps the main group's pour on the other.
import sys, pcbnew
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
BOARD = sys.argv[1]
def mm(v): return (pcbnew.ToMM(v.x), pcbnew.ToMM(v.y))
def run():
    b = pcbnew.LoadBoard(BOARD); NET = 'GND'
    items = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != NET: continue
        for L in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not z.IsOnLayer(L): continue
            fp = z.GetFilledPolysList(L)
            for i in range(fp.OutlineCount()):
                o = fp.Outline(i); g = Polygon([mm(o.CPoint(j)) for j in range(o.PointCount())])
                holes = [Polygon([mm(fp.Hole(i, h).CPoint(j)) for j in range(fp.Hole(i, h).PointCount())]) for h in range(fp.HoleCount(i))]
                if holes: g = g.difference(unary_union(holes))
                items.append(('Z', {L}, g))
    for t in b.GetTracks():
        if t.GetNetname() != NET: continue
        if t.GetClass() == 'PCB_VIA':
            items.append(('V', {pcbnew.F_Cu, pcbnew.B_Cu}, Point(mm(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2)))
        else:
            items.append(('T', {t.GetLayer()}, LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2)))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != NET: continue
            Ls = {L for L in (pcbnew.F_Cu, pcbnew.B_Cu) if p.IsOnLayer(L)}
            sp = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(sp, list(Ls)[0], 0, pcbnew.FromMM(0.005))
            items.append(('P', Ls, Polygon([mm(sp.Outline(0).CPoint(j)) for j in range(sp.Outline(0).PointCount())])))
    par = list(range(len(items)))
    def f_(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][1] & items[j][1] and items[i][2].buffer(0.001).intersects(items[j][2]):
                par[f_(i)] = f_(j)
    groups = {}
    for i in range(len(items)): groups.setdefault(f_(i), []).append(i)
    gs = sorted(groups.values(), key=lambda g: sum(items[k][2].area for k in g), reverse=True)
    if len(gs) == 1:
        return b, 0, 0
    main = gs[0]
    mainZ = {L: unary_union([items[k][2] for k in main if items[k][0] == 'Z' and L in items[k][1]]) for L in (pcbnew.F_Cu, pcbnew.B_Cu)}
    vias = [Point(mm(t.GetPosition())) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    # obstacles for a new 0.45 mm via: foreign copper on any layer, no-via rule areas, the board edge
    obs = []
    for t in b.GetTracks():
        if t.GetNetname() == NET: continue
        if t.GetClass() == 'PCB_VIA':
            obs.append(Point(mm(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2))
        else:
            obs.append(LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == NET and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH: continue
            if not (p.IsOnLayer(pcbnew.F_Cu) or p.IsOnLayer(pcbnew.B_Cu)) and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH: continue
            sp = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(sp, pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu, 0, pcbnew.FromMM(0.005))
            obs.append(Polygon([mm(sp.Outline(0).CPoint(j)) for j in range(sp.Outline(0).PointCount())]))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias():
            o = z.Outline().Outline(0); obs.append(Polygon([mm(o.CPoint(j)) for j in range(o.PointCount())]))
    OBS = unary_union(obs).buffer(0.225 + 0.2)
    ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
    EDGE_OK = Polygon([mm(ps.Outline(0).CPoint(j)) for j in range(ps.Outline(0).PointCount())]).buffer(-0.6)
    added = 0
    for g in gs[1:]:
        done = False
        for L, O in ((pcbnew.F_Cu, pcbnew.B_Cu), (pcbnew.B_Cu, pcbnew.F_Cu)):
            iso = unary_union([items[k][2] for k in g if items[k][0] == 'Z' and L in items[k][1]])
            ov = iso.buffer(-0.3).intersection(mainZ[O].buffer(-0.3))
            if ov.is_empty: continue
            x0, y0, x1, y1 = ov.bounds
            cands = [Point(x0 + 0.05 * i, y0 + 0.05 * j) for i in range(int((x1 - x0) / 0.05) + 1) for j in range(int((y1 - y0) / 0.05) + 1)]
            cands = [c for c in cands if ov.contains(c) and EDGE_OK.contains(c) and not OBS.contains(c) and all(c.distance(v) > 0.6 for v in vias)]
            if not cands: continue
            q = max(cands, key=lambda c: ov.boundary.distance(c))
            pv = pcbnew.PCB_VIA(b); pv.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(q.x), pcbnew.FromMM(q.y)))
            pv.SetWidth(pcbnew.FromMM(0.45)); pv.SetDrill(pcbnew.FromMM(0.2)); pv.SetViaType(pcbnew.VIATYPE_THROUGH)
            pv.SetNet(b.FindNet(NET)); b.Add(pv); vias.append(q); added += 1; done = True
            print('bridge via at (%.2f, %.2f)' % (q.x, q.y))
            break
        if not done:
            print('no bridge for group near', [round(v, 2) for v in unary_union([items[k][2] for k in g]).centroid.coords[0]])
    return b, len(gs) - 1, added
for it in range(4):
    b, niso, added = run()
    print('round', it, 'isolated groups', niso, 'vias added', added)
    if niso == 0 or added == 0: break
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(BOARD, b)
