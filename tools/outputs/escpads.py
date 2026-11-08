# ESC 1S: battery pads J2 side by side across the rear-left corner, rotated 45 deg (leads leave parallel along the diagonal)
import pcbnew, math, sys
PLUS = (-18.6, -11.9); MINUS = (-16.7, -19.0)
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
P = '/work/acwing_hw/02 - ESC_1S_KiCadProj/ACwing_ESC1S_A.kicad_pcb'
b = pcbnew.LoadBoard(P)
V = lambda u, v: pcbnew.VECTOR2I(int(round((150 + u) * 1e6)), int(round((100 - v) * 1e6)))
U = lambda p: (p.x / 1e6 - 150, 100 - p.y / 1e6)
f = b.FindFootprintByReference('J2')
f.SetOrientationDegrees(-45); f.SetPosition(V(-15.90, -15.90))   # symmetric on the corner diagonal, pads 0.85 mm from the edge
def padpoly(pd):
    s = pd.GetEffectivePolygon(pcbnew.F_Cu); o = s.Outline(0)
    return Polygon([U(o.CPoint(i)) for i in range(o.PointCount())])
pads = {pd.GetNetname(): padpoly(pd) for pd in f.Pads()}
PV, PG = pads['VBAT_RAW'], pads['GND']
print('pads', {k: tuple(round(c, 2) for c in v.centroid.coords[0]) for k, v in pads.items()})
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps, True); o = ps.Outline(0)
BOARD = Polygon([U(o.CPoint(i)) for i in range(o.PointCount())]); INNER = BOARD.buffer(-0.35)
# 1. old VBAT_RAW stub to the old pad, vias inside / between the new pads
dele = []
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        c = Point(U(t.GetPosition())); r = t.GetWidth(pcbnew.F_Cu) / 2e6
        if any(c.buffer(r).intersects(p.buffer(0.1)) for p in pads.values()) or c.distance(Point(-15.76, -15.76)) < 1.2:
            dele.append(t); print('del via', t.GetNetname(), [round(x, 2) for x in c.coords[0]])
    elif t.GetNetname() == 'VBAT_RAW' and t.GetLayer() == pcbnew.F_Cu:
        a = U(t.GetStart())
        if a[1] < -11.0 and a[0] < -13.0: dele.append(t); print('del track', [round(x, 2) for x in a], [round(x, 2) for x in U(t.GetEnd())])
for t in dele: b.Delete(t)
# 2. zone outlines
def zone(name): return [z for z in b.Zones() if z.GetZoneName() == name][0]
def zpoly(z):
    o = z.Outline().Outline(0); return Polygon([U(o.CPoint(i)) for i in range(o.PointCount())])
def setpoly(z, g):
    g = g.simplify(0.02)
    if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda x: x.area)
    sp = pcbnew.SHAPE_POLY_SET(); sp.NewOutline()
    for x, y in list(g.exterior.coords)[:-1]: sp.Append(V(x, y))
    sp.thisown = False; z.SetOutline(sp)
zr, zrb, zg = zone('VBAT_RAW_top'), zone('VBAT_RAW_bot'), zone('GND_J2')
shf = unary_union([zpoly(zone('VBAT_SH_top'))]).buffer(0.3)
c1 = zpoly(zone('VBAT_C1')).buffer(0.35)
rt = unary_union([zpoly(zr), PV.buffer(0.3)]).difference(PG.buffer(0.6)).difference(shf).intersection(INNER)
setpoly(zr, rt)
corner = unary_union([PG.buffer(0.3), box(-20, -20, -12.9, -17.6), Point(-17, -17).buffer(2.9)]).intersection(INNER)
gt = corner.difference(PV.buffer(0.6)).difference(c1).difference(rt.buffer(0.3))
setpoly(zg, gt)
# 3. replacement VBAT_RAW vias (inside both VBAT_RAW zones, outside the pad) and GND vias around the GND pad
rb = zpoly(zrb)
vias = [Point(U(t.GetPosition())) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
def place(net, region, n, d, drill, avoid):
    got = 0
    cands = sorted(((x / 10, y / 10) for x in range(-195, -110) for y in range(-195, -110)), key=lambda q: Point(q).distance(avoid))
    for q in cands:
        p = Point(q)
        if got >= n: break
        if not region.buffer(-d / 2 - 0.05).contains(p): continue
        if any(p.distance(v) < d + 0.35 for v in vias): continue
        if p.distance(Point(-15.90, -15.90)) < 1.6: continue   # nothing in the gap between the battery pads
        if any(p.buffer(d / 2).distance(pp) < (0.3 if k != net else 0.15) for k, pp in pads.items()): continue
        v = pcbnew.PCB_VIA(b); v.SetPosition(V(*q)); v.SetWidth(int(d * 1e6)); v.SetDrill(int(drill * 1e6))
        v.SetNet(b.FindNet(net)); b.Add(v); vias.append(p); got += 1; print('add via', net, q)
place('VBAT_RAW', rt.intersection(rb), 3, 0.6, 0.3, PV)
place('GND', gt, 3, 0.5, 0.3, PG)
print('step4', flush=True)
# 4. silkscreen polarity marks
for d in b.GetDrawings():
    if d.GetClass() != 'PCB_TEXT': continue
    q = U(d.GetPosition())
    if d.GetText() == '+' and abs(q[0] + 11.86) < 0.05 and abs(q[1] + 12.12) < 0.05: d.SetPosition(V(*PLUS)); print('moved +')
    if d.GetText() == '-' and abs(q[0] + 18.2) < 0.05 and abs(q[1] + 18.1) < 0.05: d.SetPosition(V(*MINUS)); print('moved -')

print('saving', flush=True)
pcbnew.SaveBoard(P, b)
print('saved')
