# ACwing ESC1S rev A - planes, motor-stage pours, battery entry / shunt, fixed short tracks, GND/VBAT fan-out.
#   In1  GND solid           In2  VBAT solid (fed from the shunt output, feeds the four stages through via clusters)
#   F.Cu stage pours (rev E FC geometry): M-n (Q drain, D anode, motor pad 2), VBAT (motor pad 1, D cathode, C+),
#        GND (C-, Q sources); battery entry J2 / C1; GND fill on the rest
#   B.Cu shunt R9 with local VBAT_RAW / VBAT pours, Kelvin pair to U1, GND fill on the rest
#   python3 esc_power.py <board>
import sys, math, os
import pcbnew
from shapely.geometry import Polygon, box, Point, LineString, MultiPoint
from shapely.ops import unary_union
from shapely.affinity import rotate as srot

BOARD = sys.argv[1]
OX, OY = 150.0, 100.0
b = pcbnew.LoadBoard(BOARD)
def P(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(float(OX + x)), pcbnew.FromMM(float(OY - y)))
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def net(n): return b.FindNet(n)
def polyset(ps):
    return unary_union([Polygon([B(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())]) for i in range(ps.OutlineCount())])
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
BOARD_POLY = polyset(ps)
FPS = {f.GetReference(): f for f in b.GetFootprints()}
def pad(ref, num): return [p for p in FPS[ref].Pads() if p.GetNumber() == num][0]
def padxy(ref, num): return B(pad(ref, num).GetPosition())
def pad_poly(p, layer, grow=0.0):
    s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, layer, pcbnew.FromMM(grow), pcbnew.FromMM(0.005))
    return polyset(s)
def cyard(ref):
    fp = FPS[ref]; fp.BuildCourtyardCaches()
    return polyset(fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd))

for t in list(b.GetTracks()):
    b.Delete(t)
for z in list(b.Zones()):
    b.Delete(z)

def zone(netname, layer, poly, prio=0, name='', thermal=True, clearance=0.25):
    if poly.is_empty:
        return
    for pg in (list(poly.geoms) if poly.geom_type == 'MultiPolygon' else [poly]):
        if pg.area < 0.3:
            continue
        z = pcbnew.ZONE(b)
        z.SetLayer(layer); z.SetNet(net(netname)); z.SetAssignedPriority(prio); z.SetZoneName(name or netname)
        z.SetLocalClearance(pcbnew.FromMM(clearance)); z.SetMinThickness(pcbnew.FromMM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.25)); z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline(); ol.NewOutline()
        for (x, y) in list(pg.simplify(0.01).exterior.coords)[:-1]:
            v = P(x, y); ol.Append(v.x, v.y)
        b.Add(z)
def rule_area(poly, layer, name, pour=True, tracks=False, vias=False):
    rz = pcbnew.ZONE(b); rz.SetLayer(layer); rz.SetIsRuleArea(True); rz.SetDoNotAllowCopperPour(pour)
    rz.SetDoNotAllowTracks(tracks); rz.SetDoNotAllowVias(vias); rz.SetDoNotAllowPads(False); rz.SetDoNotAllowFootprints(False)
    rz.SetZoneName(name); ol = rz.Outline(); ol.NewOutline()
    for (x, y) in list(poly.exterior.coords)[:-1]:
        v = P(x, y); ol.Append(v.x, v.y)
    b.Add(rz)

VIAS = []
def via(netname, x, y, d=0.5, drill=0.3):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(P(x, y)); v.SetWidth(pcbnew.FromMM(d)); v.SetDrill(pcbnew.FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net(netname)); v.SetLocked(True)
    b.Add(v); VIAS.append((x, y))
ADDED = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
def track(netname, a, c, L, w=0.25):
    t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(L)
    t.SetNet(net(netname)); t.SetLocked(True); b.Add(t)
    ADDED[L].append((netname, LineString([a, c]).buffer(w / 2)))
def path(netname, pts, L, w=0.25):
    for a, c in zip(pts, pts[1:]):
        if a != c:
            track(netname, a, c, L, w)

HOLES = [(10, 10), (-10, 10), (-10, -10), (10, -10)]
NO_VIA = unary_union([Point(h).buffer(2.6 + 0.3) for h in HOLES])
INNER = BOARD_POLY.buffer(-0.5)
PADS = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        for L in (pcbnew.F_Cu, pcbnew.B_Cu):
            if p.IsOnLayer(L) and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                PADS.append((fp.GetReference(), p.GetNumber(), p.GetNetname(), L, pad_poly(p, L), B(p.GetPosition())))
_FC = {}
def foreign(netname, L):
    k = (netname, L, len(ADDED[L]))
    if k not in _FC:
        _FC[k] = unary_union([pp for (_, _, n, l, pp, _) in PADS if l == L and n != netname] +
                             [g for (n, g) in ADDED[L] if n != netname])
    return _FC[k]
def via_ok(q, netname, spacing=0.75, r=0.25):
    if not INNER.contains(Point(q).buffer(r)) or Point(q).buffer(r).intersects(NO_VIA):
        return False
    if any(math.dist(q, v) < spacing for v in VIAS):
        return False
    vb = Point(q).buffer(r + 0.2)
    return not (vb.intersects(foreign(netname, pcbnew.F_Cu)) or vb.intersects(foreign(netname, pcbnew.B_Cu)))

# ------------------------------------------------------------------ planes
zone('GND', pcbnew.In1_Cu, BOARD_POLY, 0, 'GND_In1')
zone('VBAT', pcbnew.In2_Cu, BOARD_POLY, 0, 'VBAT_In2')

# ------------------------------------------------------------------ motor stages (F.Cu), rev E geometry
STAGE_ROT = {1: 0, 2: 90, 4: 180, 3: 270}
def S(n, geom): return srot(geom, STAGE_ROT[n], origin=(0, 0))
def Sp(n, x, y):
    a = math.radians(STAGE_ROT[n]); return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
STAGE_VIAS = {'VBAT': [(-3.1, -16.52), (-2.0, -16.52), (-0.9, -16.52), (-2.54, -13.0)],
              'GND': [(-2.75, -9.25), (-3.05, -10.0), (-2.0, -9.2), (1.2, -8.55), (2.0, -8.55), (2.8, -8.55)]}
STAGE_AREA = []
for n in STAGE_ROT:
    zone('M%d_N' % n, pcbnew.F_Cu, S(n, box(0.2, -19.7, 3.3, -10.35)).intersection(BOARD_POLY), 3, 'M%d_N_pour' % n, thermal=False)
    zone('VBAT', pcbnew.F_Cu, S(n, box(-3.3, -19.7, -0.3, -11.2)).intersection(BOARD_POLY), 2, 'VBAT_st%d' % n, thermal=False)
    zone('GND', pcbnew.F_Cu, S(n, box(-3.3, -10.9, -0.35, -7.7)), 2, 'GND_C_st%d' % n, thermal=False)
    zone('GND', pcbnew.F_Cu, S(n, box(0.8, -10.25, 3.4, -8.2)), 2, 'GND_Q_st%d' % n, thermal=False)
    STAGE_AREA.append(S(n, box(-3.5, -20.5, 3.5, -7.5)))
    for nn, pts in STAGE_VIAS.items():
        for (x, y) in pts:
            for dx in (0, 0.1, 0.2, 0.3, 0.4):            # nudge along the stage axis if a foreign pad is too close
                q = Sp(n, x + dx, y)
                g = Point(q).buffer(0.225 + 0.2)
                if not (g.intersects(foreign(nn, pcbnew.F_Cu)) or g.intersects(foreign(nn, pcbnew.B_Cu))):
                    break
            via(nn, *q, d=0.45, drill=0.2)
    # gate node Rg(2) - Rpd(1) - Q(G)
    rg, rpd, q = 'R%d' % n, 'R%d' % (4 + n), 'Q%d' % n
    g_net = pad(q, '4').GetNetname()
    track(g_net, padxy(rg, '2'), padxy(rpd, '1'), pcbnew.F_Cu, 0.2)
    track(g_net, padxy(rg, '2'), padxy(q, '4'), pcbnew.F_Cu, 0.2)

# ------------------------------------------------------------------ battery entry (rear-left corner) and shunt
# J2+ (F.Cu, VBAT_RAW) -> vias -> R9 pad 1 (B.Cu) -> shunt -> R9 pad 2 (B.Cu, VBAT) -> vias -> In2 VBAT.
j2v, j2g = pad_poly(pad('J2', '1'), pcbnew.F_Cu), pad_poly(pad('J2', '2'), pcbnew.F_Cu)
c1v, c1g = pad_poly(pad('C1', '1'), pcbnew.F_Cu), pad_poly(pad('C1', '2'), pcbnew.F_Cu)
r9a, r9b = pad_poly(pad('R9', '1'), pcbnew.B_Cu), pad_poly(pad('R9', '2'), pcbnew.B_Cu)
pa, pb = padxy('R9', '1'), padxy('R9', '2')
u = {n: padxy('U1', n) for n in '123456'}
# Kelvin pair (B.Cu, 0.15 mm): R9.1 -> U1.4 (VIN+), R9.2 -> U1.5 (VIN-)
xk = pa[0] + 1.3
ka = [pa, (xk, pa[1]), (xk, u['4'][1] - 0.5), (u['4'][0], u['4'][1] - 0.02)]
kb = [pb, (pb[0], u['5'][1] - 0.57), (pb[0] + 0.6, u['5'][1]), u['5']]
path('VBAT_RAW', ka, pcbnew.B_Cu, 0.15)
path('VBAT_SH', kb, pcbnew.B_Cu, 0.15)
# U1: OUT -> R10 -> C6 (CUR filter node); VCC pin 3 -> C7; GND pins 1-2 tied
path(pad('U1', '6').GetNetname(), [u['6'], (u['6'][0], padxy('R10', '1')[1]), padxy('R10', '1')], pcbnew.B_Cu, 0.15)
path('CUR', [padxy('R10', '2'), padxy('C6', '1')], pcbnew.B_Cu, 0.15)
# CUR to the ESC link: J1.3 (top) -> via -> B.Cu diagonal to the filter node C6.1 (Freerouting found no way out of the
# connector row on its own)
j3, c6c = padxy('J1', '3'), padxy('C6', '1')
cv = (j3[0], j3[1] + 1.6)
path('CUR', [j3, cv], pcbnew.F_Cu, 0.25); via('CUR', *cv)
path('CUR', [cv, (c6c[0] + 8.0, c6c[1]), c6c], pcbnew.B_Cu, 0.25)
c7a = padxy('C7', '1')
path('VBAT', [u['3'], (c7a[0], u['3'][1]), c7a], pcbnew.B_Cu, 0.2)
path('GND', [u['1'], u['2']], pcbnew.B_Cu, 0.2)
KELVIN = unary_union([LineString(ka).buffer(0.4), LineString(kb[1:]).buffer(0.4)])
NOPOUR = unary_union([KELVIN, cyard('U1').buffer(0.3), cyard('R10').buffer(0.2), cyard('C6').buffer(0.2),
                      cyard('C7').buffer(0.2)]).convex_hull
rule_area(NOPOUR, pcbnew.B_Cu, 'KELVIN_U1')

def big_vias(netname, region, n, spacing=0.95):
    got = []
    minx, miny, maxx, maxy = region.bounds
    cands = [(minx + 0.1 * i, miny + 0.1 * j) for i in range(int((maxx - minx) / 0.1) + 1) for j in range(int((maxy - miny) / 0.1) + 1)]
    cx, cy_ = region.centroid.x, region.centroid.y
    for q in sorted(cands, key=lambda q: math.dist(q, (cx, cy_))):
        if len(got) >= n:
            break
        if not region.contains(Point(q)) or not via_ok(q, netname, spacing, 0.3):
            continue
        via(netname, *q, d=0.6, drill=0.3); got.append(q)
    return got
RAW_REG = unary_union([Point(pa).buffer(2.0), Point(-15.8, -13.0).buffer(1.4)]).difference(j2v.buffer(0.35)).difference(
    r9a.buffer(0.15)).difference(r9b.buffer(0.6)).difference(NOPOUR.buffer(0.2)).intersection(box(-30, -30, -12.0, -10.6))
raw_v = big_vias('VBAT_RAW', RAW_REG.intersection(BOARD_POLY.buffer(-0.8)), 7)
# rev B: R9.2 -> VBAT_SH (B.Cu pour) -> 7 vias -> F.Cu pour -> Q5 source pins (top); Q5 drain -> F.Cu pour -> 7 vias -> In2 VBAT
q5s = unary_union([pad_poly(pad('Q5', n), pcbnew.F_Cu) for n in '123'])
q5d = unary_union([pad_poly(p_, pcbnew.F_Cu) for p_ in FPS['Q5'].Pads() if p_.GetNetname() == 'VBAT'])
q5g = pad_poly(pad('Q5', '4'), pcbnew.F_Cu)
sb = q5s.bounds
BAT_REG = box(-19.4, -10.9, -15.5, sb[1] - 0.45).difference(NOPOUR.buffer(0.2)).difference(RAW_REG.buffer(0.5)).difference(r9a.buffer(0.6))
bat_v = big_vias('VBAT_SH', BAT_REG.intersection(BOARD_POLY.buffer(-0.8)), 7, spacing=0.9)
SH_F = unary_union([q5s.buffer(0.15)] + [Point(q).buffer(0.55) for q in bat_v]).convex_hull.difference(q5g.buffer(0.35)).difference(q5d.buffer(0.35))
zone('VBAT_SH', pcbnew.F_Cu, SH_F.intersection(BOARD_POLY.buffer(-0.3)), 4, 'VBAT_SH_top', thermal=False)
db = q5d.bounds
DR_REG = box(-19.4, db[3] + 0.4, -15.3, -3.75).union(box(-19.45, db[1], db[0] - 0.4, db[3]))
dr_v = big_vias('VBAT', DR_REG.intersection(BOARD_POLY.buffer(-0.8)), 7, spacing=0.9)
DR_F = unary_union([q5d.buffer(0.15)] + [Point(q).buffer(0.55) for q in dr_v]).convex_hull.difference(q5g.buffer(0.35)).difference(q5s.buffer(0.35)).difference(SH_F.buffer(0.3))
zone('VBAT', pcbnew.F_Cu, DR_F.intersection(BOARD_POLY.buffer(-0.3)), 4, 'VBAT_Q5_top', thermal=False)
print('Q5 vias: VBAT_SH', len(bat_v), 'VBAT', len(dr_v))
RAW_F = unary_union([j2v.buffer(0.3)] + [Point(q).buffer(0.55) for q in raw_v]).convex_hull
zone('VBAT_RAW', pcbnew.F_Cu, RAW_F.intersection(BOARD_POLY.buffer(-0.3)).difference(c1v.buffer(0.5)).difference(j2g.buffer(0.5)), 4, 'VBAT_RAW_top', thermal=False)
RAW_B = unary_union([r9a.buffer(0.2)] + [Point(q).buffer(0.55) for q in raw_v]).convex_hull.difference(NOPOUR).difference(r9b.buffer(0.35))
zone('VBAT_RAW', pcbnew.B_Cu, RAW_B.intersection(BOARD_POLY.buffer(-0.3)), 4, 'VBAT_RAW_bot', thermal=False)
BAT_B = unary_union([r9b.buffer(0.2)] + [Point(q).buffer(0.55) for q in bat_v]).convex_hull.difference(NOPOUR).difference(r9a.buffer(0.35)).difference(RAW_B.buffer(0.3))
zone('VBAT_SH', pcbnew.B_Cu, BAT_B.intersection(BOARD_POLY.buffer(-0.3)), 4, 'VBAT_SH_bot', thermal=False)
zone('GND', pcbnew.F_Cu, j2g.buffer(0.9).intersection(BOARD_POLY.buffer(-0.3)).difference(RAW_F.buffer(0.3)), 3, 'GND_J2', thermal=False)
zone('GND', pcbnew.F_Cu, c1g.buffer(0.7).intersection(BOARD_POLY.buffer(-0.3)), 3, 'GND_C1', thermal=False)
zone('VBAT', pcbnew.F_Cu, c1v.buffer(0.7).intersection(BOARD_POLY.buffer(-0.3)).difference(RAW_F.buffer(0.3)), 3, 'VBAT_C1', thermal=False)
def auto_vias(netname, region, n, spacing=0.8):
    got = 0
    minx, miny, maxx, maxy = region.bounds
    cands = [(minx + 0.1 * i, miny + 0.1 * j) for i in range(int((maxx - minx) / 0.1) + 1) for j in range(int((maxy - miny) / 0.1) + 1)]
    own = unary_union([pp for (_, _, nn, l, pp, _) in PADS if nn == netname and l == pcbnew.F_Cu])
    for q in sorted(cands, key=lambda q: math.dist(q, (region.centroid.x, region.centroid.y))):
        if got >= n:
            break
        if region.buffer(-0.3).contains(Point(q)) and via_ok(q, netname, spacing) and not Point(q).buffer(0.3).intersects(own):
            via(netname, *q); got += 1
    return got
print('shunt vias VBAT_RAW', len(raw_v), 'VBAT', len(bat_v), '| C1 VBAT', auto_vias('VBAT', c1v.buffer(0.7), 3),
      'GND J2', auto_vias('GND', j2g.buffer(0.9), 4), 'GND C1', auto_vias('GND', c1g.buffer(0.7), 3))

# ------------------------------------------------------------------ fill pours (lowest priority)
zone('GND', pcbnew.F_Cu, BOARD_POLY, 0, 'GND_top')
zone('GND', pcbnew.B_Cu, BOARD_POLY, 0, 'GND_bot')

# ------------------------------------------------------------------ fan-out of the GND / VBAT pads not on a pour of their own net
SKIP = {('U1', '2'), ('U1', '5'), ('R9', '1'), ('R9', '2'), ('U1', '3')} | {('Q5', p_.GetNumber()) for p_ in FPS['Q5'].Pads()}
fan = {'ok': 0, 'fail': []}
def fanout(ref, num, nn, L, c):
    for r in (0.6, 0.75, 0.9, 1.05, 1.25, 1.5, 1.8, 2.1, 2.5):
        for k in range(36):
            a = 2 * math.pi * k / 36
            q = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
            if not via_ok(q, nn):
                continue
            if LineString([c, q]).buffer(0.125 + 0.2).intersects(foreign(nn, L)):
                continue
            if L == pcbnew.B_Cu and nn != 'GND' and Point(q).buffer(0.45).intersects(NOPOUR) is False:
                pass
            track(nn, c, q, L)
            via(nn, *q)
            fan['ok'] += 1
            return
    fan['fail'].append('%s.%s' % (ref, num))
pours = {}
for z in b.Zones():
    if not z.GetIsRuleArea() and z.GetLayer() == pcbnew.F_Cu and z.GetZoneName() != 'GND_top':
        pours.setdefault(z.GetNetname(), []).append(polyset(z.Outline()))
for (ref, num, nn, L, poly, c) in sorted(PADS, key=lambda x: (x[2], x[0], x[1])):
    if nn not in ('GND', 'VBAT') or (ref, num) in SKIP or ref.startswith('H'):
        continue
    if L == pcbnew.F_Cu and any(pp.intersects(poly) for pp in pours.get(nn, [])):
        continue
    fanout(ref, num, nn, L, c)
print('fan-out vias:', fan['ok'], 'failed:', fan['fail'])

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD, b)
