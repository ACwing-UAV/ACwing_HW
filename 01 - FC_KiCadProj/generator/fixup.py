# Post-route fix-up: closes the connections the autorouter left open (plane stitching vias for GND/VDD/VBAT
# islands, short F.Cu/B.Cu routes for the few signals), trims hair-line clearance excesses, removes dangling stubs.
import sys, math
import pcbnew
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union

BOARD = sys.argv[1]
OX, OY = 150.0, 100.0
b = pcbnew.LoadBoard(BOARD)
def mm(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def P(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY - y))

CLR = 0.12            # margin used by the fix-up (above the 0.1 rule)
VIA_D, VIA_DR, W = 0.45, 0.2, 0.2
ANT = box(-23, -5.6, -13.3, 5.6)
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
o = ps.Outline(0)
INNER = Polygon([mm(o.CPoint(j)) for j in range(o.PointCount())]).buffer(-0.4)
for k in range(ps.HoleCount(0)):
    h = ps.Hole(0, k)
    INNER = INNER.difference(Polygon([mm(h.CPoint(j)) for j in range(h.PointCount())]).buffer(0.4))
for fp in b.GetFootprints():            # NPTH (M2, Tag-Connect) holes
    for p in fp.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            INNER = INNER.difference(Point(*mm(p.GetPosition())).buffer(pcbnew.ToMM(p.GetDrillSize().x) / 2 + 0.3))

LAYERS = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu, 'I1': pcbnew.In1_Cu, 'I2': pcbnew.In2_Cu}

def pad_shape(p, layer):
    poly = pcbnew.SHAPE_POLY_SET()
    p.TransformShapeToPolygon(poly, layer, 0, pcbnew.FromMM(0.005))
    out = []
    for i in range(poly.OutlineCount()):
        ol = poly.Outline(i)
        out.append(Polygon([mm(ol.CPoint(j)) for j in range(ol.PointCount())]))
    return unary_union(out)

def copper(layer, exclude_net):
    """Copper of all nets except exclude_net on a layer (pads, tracks, vias, zone fills)."""
    geoms = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(layer) and p.GetNetname() != exclude_net:
                geoms.append(pad_shape(p, layer))
    for t in b.GetTracks():
        if t.GetNetname() == exclude_net:
            continue
        if t.GetClass() == 'PCB_VIA':
            geoms.append(Point(*mm(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2))
        elif t.GetLayer() == layer:
            geoms.append(LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() == exclude_net or not z.IsOnLayer(layer):
            continue
        fp_ = z.GetFilledPolysList(layer)
        for i in range(fp_.OutlineCount()):
            ol = fp_.Outline(i)
            geoms.append(Polygon([mm(ol.CPoint(j)) for j in range(ol.PointCount())]))
    return unary_union(geoms)

def holes():
    pts = [mm(t.GetPosition()) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                pts.append(mm(p.GetPosition()))
    return pts

def zone_fill(netname, layer):
    g = []
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == netname and z.IsOnLayer(layer):
            fp_ = z.GetFilledPolysList(layer)
            for i in range(fp_.OutlineCount()):
                ol = fp_.Outline(i)
                g.append(Polygon([mm(ol.CPoint(j)) for j in range(ol.PointCount())]))
    return unary_union(g)

def add_track(net, a, c, layer, w=W):
    t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(pcbnew.FromMM(w))
    t.SetLayer(layer); t.SetNet(b.FindNet(net)); b.Add(t)

def add_via(net, p):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(*p)); v.SetWidth(pcbnew.FromMM(VIA_D)); v.SetDrill(pcbnew.FromMM(VIA_DR))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(b.FindNet(net)); b.Add(v)

def via_ok(net, p, plane_layer, obstF, obstB, hl):
    c = Point(*p)
    if not INNER.contains(c) or ANT.contains(c):
        return False
    r = VIA_D / 2 + CLR
    if c.buffer(r).intersects(obstF) or c.buffer(r).intersects(obstB):
        return False
    if any(math.dist(p, h) < 0.65 for h in hl):
        return False
    if plane_layer is not None:
        fill = zone_fill(net, plane_layer)
        if not fill.contains(c.buffer(VIA_D / 2 + 0.05)):
            return False
    return True

log = []
import builtins
_p = print
def print(*a, **k): k.setdefault("flush", True); _p(*a, **k)
CACHE = {}
def ctx(net, plane_layer):
    key = (net, plane_layer)
    if key not in CACHE:
        CACHE[key] = dict(F=copper(pcbnew.F_Cu, net), B=copper(pcbnew.B_Cu, net), H=holes(),
                          fill=zone_fill(net, plane_layer) if plane_layer is not None else None)
    return CACHE[key]

def via_ok2(p, cx):
    c = Point(*p)
    if not INNER.contains(c) or ANT.contains(c):
        return False
    r = VIA_D / 2 + CLR
    if c.buffer(r).intersects(cx['F']) or c.buffer(r).intersects(cx['B']):
        return False
    if any(math.dist(p, h) < 0.65 for h in cx['H']):
        return False
    if cx['fill'] is not None and not cx['fill'].contains(c.buffer(VIA_D / 2 + 0.05)):
        return False
    return True

def stitch(net, anchor, plane_layer):
    """via near anchor (on F.Cu item of net) + short F.Cu track"""
    cx = ctx(net, plane_layer); obstF = cx['F']
    for r in (0.55, 0.7, 0.85, 1.0, 1.2, 1.4, 1.7, 2.0):
        for k in range(24):
            t = 2 * math.pi * k / 24
            p = (anchor[0] + r * math.cos(t), anchor[1] + r * math.sin(t))
            seg = LineString([anchor, p]).buffer(W / 2 + CLR)
            if seg.intersects(obstF):
                continue
            if via_ok2(p, cx):
                add_track(net, anchor, p, pcbnew.F_Cu)
                add_via(net, p)
                cx['H'].append(p)
                log.append('stitch %s via at (%.2f, %.2f)' % (net, p[0], p[1])); print(log[-1])
                return True
    log.append('stitch FAILED %s near (%.2f, %.2f)' % (net, anchor[0], anchor[1]))
    return False

def route2(net, a, c):
    """short route a->c: straight or L on F.Cu, else via-B.Cu-via"""
    obstF = copper(pcbnew.F_Cu, net); obstB = copper(pcbnew.B_Cu, net)
    def free(path, obst):
        return not LineString(path).buffer(W / 2 + CLR - 0.04).intersects(obst)
    cands = [[a, c], [a, (c[0], a[1]), c], [a, (a[0], c[1]), c]]
    for path in cands:
        if free(path, obstF):
            for u, v in zip(path, path[1:]):
                if u != v: add_track(net, u, v, pcbnew.F_Cu)
            log.append('route %s on F.Cu' % net); return True
    hl = holes()
    for ra in (0.6, 0.8, 1.0):
        for k in range(16):
            t = 2 * math.pi * k / 16
            va = (a[0] + ra * math.cos(t), a[1] + ra * math.sin(t))
            for kk in range(16):
                tt = 2 * math.pi * kk / 16
                vc = (c[0] + ra * math.cos(tt), c[1] + ra * math.sin(tt))
                if not (free([a, va], obstF) and free([vc, c], obstF)):
                    continue
                if not (via_ok(net, va, None, obstF, obstB, hl) and via_ok(net, vc, None, obstF, obstB, hl)):
                    continue
                for path in ([va, vc], [va, (vc[0], va[1]), vc], [va, (va[0], vc[1]), vc]):
                    if free(path, obstB):
                        add_track(net, a, va, pcbnew.F_Cu); add_via(net, va)
                        for u, v in zip(path, path[1:]):
                            if u != v: add_track(net, u, v, pcbnew.B_Cu)
                        add_via(net, vc); add_track(net, vc, c, pcbnew.F_Cu)
                        log.append('route %s via B.Cu' % net); return True
    log.append('route FAILED %s' % net); return False

def refill():
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())

CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
def groups(netname):
    """copper groups of a net by geometric contact (pads, tracks, vias, zone fills); largest first"""
    from shapely.strtree import STRtree
    items = []      # (layers, geom, kind, anchor)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() != netname:
                continue
            for L in CU:
                if p.IsOnLayer(L):
                    items.append(({L}, pad_shape(p, L), 'pad', mm(p.GetPosition()) if L == pcbnew.F_Cu else None,
                                  fp.GetReference() + '.' + p.GetNumber()))
    for t in b.GetTracks():
        if t.GetNetname() != netname:
            continue
        if t.GetClass() == 'PCB_VIA':
            items.append((set(CU), Point(*mm(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2), 'via', None, ''))
        else:
            g = LineString([mm(t.GetStart()), mm(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2)
            anc = [mm(t.GetStart()), mm(t.GetEnd())] if t.GetLayer() == pcbnew.F_Cu else None
            items.append(({t.GetLayer()}, g, 'track', anc, ''))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != netname:
            continue
        for L in CU:
            if not z.IsOnLayer(L):
                continue
            fp_ = z.GetFilledPolysList(L)
            for i in range(fp_.OutlineCount()):
                ol = fp_.Outline(i)
                items.append(({L}, Polygon([mm(ol.CPoint(j)) for j in range(ol.PointCount())]).buffer(0), 'zone', None, z.GetZoneName()))
    n = len(items)
    parent = list(range(n))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for L in CU:
        idx = [i for i in range(n) if L in items[i][0]]
        geoms = [items[i][1].buffer(0.001) for i in idx]
        if not geoms:
            continue
        tree = STRtree(geoms)
        for k, g in enumerate(geoms):
            for m in tree.query(g, predicate='intersects'):
                ra, rb = find(idx[k]), find(idx[int(m)])
                if ra != rb:
                    parent[ra] = rb
    gr = {}
    for i in range(n):
        gr.setdefault(find(i), []).append(items[i])
    out = sorted(gr.values(), key=lambda g: sum(it[1].area for it in g), reverse=True)
    return out

def anchors_of(grp):
    pts = []
    for it in grp:
        if it[2] == 'pad' and it[3] is not None:
            pts.append(it[3])
        elif it[2] == 'track' and it[3] is not None:
            pts += it[3]
    return pts

# 1. remove dangling track stubs (geometric test: endpoint touching nothing else of its net)
def dangling_pass():
    tracks = [t for t in b.GetTracks()]
    pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
    removed = 0
    for t in tracks:
        if t.GetClass() != 'PCB_TRACK':
            continue
        net = t.GetNetname()
        for end in (t.GetStart(), t.GetEnd()):
            hit = False
            for o2 in tracks:
                if o2 is t or o2.GetNetname() != net:
                    continue
                if o2.GetClass() == 'PCB_VIA':
                    if (o2.GetPosition() - end).EuclideanNorm() <= o2.GetWidth() // 2:
                        hit = True; break
                elif o2.GetLayer() == t.GetLayer() and (o2.GetStart() == end or o2.GetEnd() == end or o2.HitTest(end, 0)):
                    hit = True; break
            if not hit:
                for p in pads:
                    if p.GetNetname() == net and p.IsOnLayer(t.GetLayer()) and p.HitTest(end):
                        hit = True; break
            if not hit:
                for z in b.Zones():
                    if not z.GetIsRuleArea() and z.GetNetname() == net and z.IsOnLayer(t.GetLayer()) and \
                            z.GetFilledPolysList(t.GetLayer()).Contains(end):
                        hit = True; break
            if not hit:
                log.append('removed dangling stub (%s)' % net); b.Delete(t)
                return 1
    return 0
while dangling_pass():
    pass

# 2. plane islands: GND -> In1 (and B), VDD -> In2 island, VBAT -> In2 ring
refill()
for net, plane in (('GND', pcbnew.In1_Cu), ('VDD', pcbnew.In2_Cu), ('VBAT', pcbnew.In2_Cu)):
    for it in range(12):
        gs = groups(net)
        if len(gs) <= 1:
            break
        progress = False
        for grp in gs[1:]:
            if all(it[4] == 'U2.86' for it in grp):
                continue        # VSS pad at the antenna end: no copper allowed there (see notes)
            for a in anchors_of(grp):
                if stitch(net, a, plane):
                    progress = True; break
        CACHE.clear()
        refill()
        if net == 'GND':
            break
        if not progress:
            break

# 3. signals
def pad_xy(ref, num):
    fp = [f for f in b.GetFootprints() if f.GetReference() == ref][0]
    return mm([p for p in fp.Pads() if p.GetNumber() == num][0].GetPosition())

ALLNETS = sorted(str(n) for n in b.GetNetsByName().keys() if str(n) and str(n) not in ('GND', 'VBAT') and not str(n).startswith('M'))
for net in ALLNETS:
    for it in range(4):
        gs = groups(net)
        if len(gs) <= 1:
            break
        # connect the two closest anchors between group 0 and group 1
        A, C = anchors_of(gs[0]), anchors_of(gs[1])
        if not A or not C:
            break
        a, c = min(((x, y) for x in A for y in C), key=lambda q: math.dist(*q))
        if not route2(net, a, c):
            break
        refill()

refill()
pcbnew.SaveBoard(BOARD, b)
print('\n'.join(log))
