# DimaQuadFC rev C - power copper, planes, fan-out and Freerouting DSN
#   In1  GND solid (minus antenna keep-out)
#   In2  VBAT ring along the perimeter + lobes under each motor stage, OPEN at the front corner
#        (FL fed along the left side, FR along the right side); the interior is a VDD pour that
#        also carries signals
#   F.Cu motor stages: M-n pour (Q drain - D anode - pad 2), VBAT pour (pad 1 - D cathode - C+),
#        GND pours (C- and Q sources) with via clusters; battery entry J2 / C1
#   bottom pogo pads: 1 mm free of foreign copper, each tied by a short B.Cu stub to a via
import sys, math, re, os
import pcbnew
from shapely.geometry import Polygon, box, Point, LineString, MultiPoint
from shapely.ops import unary_union
from shapely.affinity import rotate as srot

BOARD = sys.argv[1]
WORK = os.path.dirname(os.path.abspath(BOARD))
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

for t in list(b.GetTracks()):
    b.Delete(t)
for z in list(b.Zones()):
    if not z.GetIsRuleArea():
        b.Delete(z)
ANT = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName() == 'ANTENNA_AE1'][0]
ANT = polyset(ANT.Outline())

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
        for (x, y) in list(pg.exterior.coords)[:-1]:
            v = P(x, y); ol.Append(v.x, v.y)
        for hole in pg.interiors:
            ol.NewHole()
            for (x, y) in list(hole.coords)[:-1]:
                v = P(x, y); ol.Append(v.x, v.y, 0, ol.HoleCount(0) - 1)
        b.Add(z)

VIAS = []
def via(netname, x, y, d=0.45, drill=0.2):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(P(x, y)); v.SetWidth(pcbnew.FromMM(d)); v.SetDrill(pcbnew.FromMM(drill))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net(netname)); v.SetLocked(True)
    b.Add(v); VIAS.append((x, y))
def track(netname, a, c, L, w=0.25):
    t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(L)
    t.SetNet(net(netname)); t.SetLocked(True); b.Add(t)
    ADDED[L].append((netname, LineString([a, c]).buffer(w / 2)))
ADDED = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}

# ------------------------------------------------------------------ geometry shared by the checks
HOLES = [(8, 8), (-8, 8), (-8, -8), (8, -8)]
TPS = {f.GetReference(): B(f.GetPosition()) for f in b.GetFootprints() if f.GetReference().startswith('TP')}
NO_VIA = unary_union([ANT] + [Point(h).buffer(2.75 + 0.25) for h in HOLES])     # vias: antenna, grommet flange
INNER = BOARD_POLY.buffer(-0.45)
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            INNER = INNER.difference(Point(*B(p.GetPosition())).buffer(pcbnew.ToMM(p.GetDrillSize().x) / 2 + 0.3))
PADS = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        for L in (pcbnew.F_Cu, pcbnew.B_Cu):
            if p.IsOnLayer(L) and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                PADS.append((fp.GetReference(), p.GetNumber(), p.GetNetname(), L, pad_poly(p, L), B(p.GetPosition())))
_FC = {}
def foreign(netname, L):
    k = (netname, L, len(ADDED[L]))             # cached: the union only changes when copper is added
    if k not in _FC:
        _FC[k] = unary_union([pp for (_, _, n, l, pp, _) in PADS if l == L and n != netname] +
                             [g for (n, g) in ADDED[L] if n != netname])
    return _FC[k]
def tp_ok(q, netname, r=0.225):
    # foreign copper must stay 1 mm from the pogo pads (pad r 0.5)
    return all(math.dist(q, c) >= 0.5 + 1.0 + r for t, c in TPS.items() if pad(t, '1').GetNetname() != netname)
def via_ok(q, netname, spacing=0.7):
    if not INNER.contains(Point(q).buffer(0.225)) or Point(q).buffer(0.225).intersects(NO_VIA):
        return False
    if any(math.dist(q, v) < spacing for v in VIAS):
        return False
    vb = Point(q).buffer(0.225 + 0.2)
    if vb.intersects(foreign(netname, pcbnew.F_Cu)) or vb.intersects(foreign(netname, pcbnew.B_Cu)):
        return False
    return tp_ok(q, netname)

# ------------------------------------------------------------------ planes
# stage frame: motor 1 (bottom edge) as drawn, the others rotated CCW about the centre
STAGE_ROT = {1: 0, 2: 90, 4: 180, 3: 270}
def S(n, geom): return srot(geom, STAGE_ROT[n], origin=(0, 0))
def Sp(n, x, y):
    a = math.radians(STAGE_ROT[n]); return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
hull = lambda *pp: MultiPoint([c for p_ in pp for c in p_.exterior.coords]).convex_hull
j2v, j2g = pad_poly(pad('J2', '1'), pcbnew.F_Cu), pad_poly(pad('J2', '2'), pcbnew.F_Cu)
c1v, c1g = pad_poly(pad('C1', '1'), pcbnew.F_Cu), pad_poly(pad('C1', '2'), pcbnew.F_Cu)
ENTRY = hull(j2v, c1v)
RING = BOARD_POLY.difference(BOARD_POLY.buffer(-3.2))
LOBES = unary_union([S(n, box(-3.5, -20.5, -0.05, -12.45)) for n in STAGE_ROT])
CONNECT = box(-17.3, 7.0, -14.6, 20.5).union(box(-20.5, 7.0, -14.6, 9.0))    # rev C2: around the chip-antenna keep-out, under the MCU west side
FRONT_GAP = box(5.5, 5.5, 25, 25)                  # ring open at the front corner (magnetometer)
CHG = box(11.6, -8.6, 20.5, -3.4)                  # charger U6.3 (BAT) and R7 (RC) reach the ring
VBAT_IN2 = unary_union([RING, LOBES, ENTRY.buffer(1.2), CONNECT, CHG]).intersection(BOARD_POLY).difference(ANT).difference(FRONT_GAP)
print('VBAT In2 pieces:', [round(g.area, 1) for g in getattr(VBAT_IN2, 'geoms', [VBAT_IN2])])
VBAT_IN2 = max(VBAT_IN2.geoms, key=lambda g: g.area) if VBAT_IN2.geom_type == 'MultiPolygon' else VBAT_IN2
zone('GND', pcbnew.In1_Cu, BOARD_POLY.difference(ANT), 0, 'GND_In1')
zone('VBAT', pcbnew.In2_Cu, VBAT_IN2, 1, 'VBAT_ring')
VDD_IN2 = BOARD_POLY.difference(ANT).difference(VBAT_IN2.buffer(0.3))
# VDD on In2: only the main pieces (small leftovers between the VBAT ring and the edge would be unconnected islands)
if VDD_IN2.geom_type == 'MultiPolygon':
    VDD_IN2 = unary_union([g for g in VDD_IN2.geoms if g.area > 5.0])
zone('VDD', pcbnew.In2_Cu, VDD_IN2, 0, 'VDD_In2')

# ------------------------------------------------------------------ motor stages (F.Cu)
STAGE_VIAS = {'VBAT': [(-3.1, -16.52), (-2.0, -16.52), (-0.9, -16.52), (-2.54, -13.0)],
              'GND': [(-2.75, -9.25), (-3.05, -10.0), (-2.0, -9.2), (1.2, -8.55), (2.0, -8.55), (2.8, -8.55)]}
for n in STAGE_ROT:
    zone('M%d_N' % n, pcbnew.F_Cu, S(n, box(0.2, -19.7, 3.3, -10.35)).intersection(BOARD_POLY), 3, 'M%d_N_pour' % n, thermal=False)
    zone('VBAT', pcbnew.F_Cu, S(n, box(-3.3, -19.7, -0.3, -11.2)).intersection(BOARD_POLY), 2, 'VBAT_st%d' % n, thermal=False)
    zone('GND', pcbnew.F_Cu, S(n, box(-3.3, -10.9, -0.35, -7.7)), 2, 'GND_C_st%d' % n, thermal=False)
    zone('GND', pcbnew.F_Cu, S(n, box(0.8, -10.25, 3.4, -8.2)), 2, 'GND_Q_st%d' % n, thermal=False)
    for nn, pts in STAGE_VIAS.items():
        for (x, y) in pts:
            via(nn, *Sp(n, x, y))
    # gate node Rg(2) - Rpd(1) - Q(G) drawn explicitly
    rg, rpd, q = 'R%d' % (19 + n), 'R%d' % (23 + n), 'Q%d' % n
    g_net = pad(q, '4').GetNetname()
    track(g_net, padxy(rg, '2'), padxy(rpd, '1'), pcbnew.F_Cu, 0.2)
    track(g_net, padxy(rg, '2'), padxy(q, '4'), pcbnew.F_Cu, 0.2)

# ------------------------------------------------------------------ battery entry (rear corner)
zone('VBAT', pcbnew.F_Cu, ENTRY.buffer(0.3).intersection(BOARD_POLY.buffer(-0.3)), 3, 'VBAT_entry', thermal=False)
zone('GND', pcbnew.F_Cu, j2g.buffer(0.9).intersection(BOARD_POLY.buffer(-0.3)), 3, 'GND_J2', thermal=False)
zone('GND', pcbnew.F_Cu, c1g.buffer(0.7).intersection(BOARD_POLY.buffer(-0.3)), 3, 'GND_C1', thermal=False)
def auto_vias(netname, region, n, spacing=0.8):
    got = 0
    minx, miny, maxx, maxy = region.bounds
    cands = [(minx + 0.1 * i, miny + 0.1 * j) for i in range(int((maxx - minx) / 0.1) + 1) for j in range(int((maxy - miny) / 0.1) + 1)]
    cx, cy = region.centroid.x, region.centroid.y
    for q in sorted(cands, key=lambda q: math.dist(q, (cx, cy))):
        if got >= n:
            break
        if region.buffer(-0.3).contains(Point(q)) and via_ok(q, netname, spacing):
            # inside its own pour, but not on top of a pad of its own net either (no via-in-pad here)
            if not Point(q).buffer(0.25).intersects(unary_union([pp for (_, _, nn, l, pp, _) in PADS if nn == netname and l == pcbnew.F_Cu])):
                via(netname, *q); got += 1
    return got
print('entry vias VBAT', auto_vias('VBAT', ENTRY.buffer(0.3).difference(j2v.buffer(0.1)).difference(c1v.buffer(0.1)), 6),
      'GND J2', auto_vias('GND', j2g.buffer(0.9), 4), 'GND C1', auto_vias('GND', c1g.buffer(0.7), 3))

# ------------------------------------------------------------------ pogo pads: B.Cu stub to a via, outward
tp_log = []
for t, c in sorted(TPS.items()):
    nn = pad(t, '1').GetNetname()
    best = None
    for r in [1.0 + 0.1 * k for k in range(31)]:
        for k in range(48):
            a = 2 * math.pi * k / 48
            q = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
            if not via_ok(q, nn, 0.75):
                continue
            if nn == 'VDD' and not VDD_IN2.buffer(-0.45).contains(Point(q)):
                continue
            seg = LineString([c, q])
            if any(seg.distance(Point(c2)) < 0.5 + 1.0 + 0.075 for t2, c2 in TPS.items()
                   if t2 != t and pad(t2, '1').GetNetname() != nn):
                continue
            if seg.buffer(0.075 + 0.15).intersects(foreign(nn, pcbnew.B_Cu)):
                continue
            best = q; break
        if best:
            break
    if best is None:
        tp_log.append(t + ' FAILED'); continue
    track(nn, c, best, pcbnew.B_Cu, 0.2)
    via(nn, *best)
    tp_log.append('%s %s -> via (%.2f, %.2f)' % (t, nn, best[0], best[1]))
print('pogo stubs:', '; '.join(tp_log))

# ------------------------------------------------------------------ LDO U5 (DFN-6, 0.4 mm): VSYS pins tied with 0.2 mm,
# then 0.3 mm to the Q5 drain (VSYS); the autorouter only has to reach Q5 / the 0.3 mm stub
u5 = {p.GetNumber(): B(p.GetPosition()) for p in FPS['U5'].Pads()}
track('VSYS', u5['3'], u5['4'], pcbnew.F_Cu, 0.2)
track('VSYS', u5['3'], padxy('Q5', '2'), pcbnew.F_Cu, 0.3)
track('VSYS', u5['1'], (u5['1'][0] - 0.35, u5['1'][1] - 0.55), pcbnew.F_Cu, 0.2)    # stub for the router
gx, gy = u5['2'][0], u5['2'][1] - 1.03                                                # pad 2 GND: down, then right
track('GND', u5['2'], (gx, gy), pcbnew.F_Cu, 0.15)
track('GND', (gx, gy), (gx + 1.1, gy), pcbnew.F_Cu, 0.15)
via('GND', gx + 1.1, gy)

# ------------------------------------------------------------------ rev C2 RF front end + QFN escape (fanout_c2.py)
#   RF1 (U2.21) -> MLPF IN (A3): straight 0.8 mm, 0.25 mm wide (MCU-side port of the matched filter)
#   MLPF OUT (A1) -> down, west, up -> R34.1; R34.2 -> antenna feed AE1.1 and C36.1 (shunt at the antenna side):
#   0.36 mm (~50 ohm over In1 on the 0.21 mm prepreg). MLPF GND pads tied together and to one via.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fanout_c2
K = lambda xy: (xy[0] - OX, OY - xy[1])          # KiCad absolute -> board frame
rf1, mi, mo = padxy('U2', '21'), padxy('U8', 'A3'), padxy('U8', 'A1')
track('RF_IN', rf1, mi, pcbnew.F_Cu, 0.25)
r1, r2, c1, c2 = padxy('R34', '1'), padxy('R34', '2'), padxy('C36', '1'), padxy('C36', '2')
ON = pad('U8', 'A1').GetNetname(); FN = pad('R34', '2').GetNetname()
pts = [mo, K((133.95, 87.85)), K((133.05, 87.85)), r1]
for a_, c_ in zip(pts, pts[1:]):
    track(ON, a_, c_, pcbnew.F_Cu, 0.36)
track(FN, r2, c1, pcbnew.F_Cu, 0.36)
track(FN, r2, padxy('AE1', '1'), pcbnew.F_Cu, 0.36)
g = {n: padxy('U8', n) for n in ('A2', 'B1', 'B2', 'B3')}
track('GND', g['B1'], g['B3'], pcbnew.F_Cu, 0.2)
track('GND', g['A2'], g['B2'], pcbnew.F_Cu, 0.2)
track('GND', g['B3'], K((133.70, 85.40)), pcbnew.F_Cu, 0.2)
track('GND', c2, K((133.05, 81.55)), pcbnew.F_Cu, 0.25)
for (nn, w, ptsk) in fanout_c2.TRACKS:
    q = [K(p_) for p_ in ptsk]
    for a_, c_ in zip(q, q[1:]):
        track(nn, a_, c_, pcbnew.F_Cu, w)
for (nn, x, y) in fanout_c2.VIAS:
    via(nn, *K((x, y)))
print('RF front end and QFN escape pre-routed')

# ------------------------------------------------------------------ U2 exposed pad: 3 x 3 via array, VSSRF / VSSSMPS tied to the pad
ep = padxy('U2', '49')
for i in (-1, 0, 1):
    for j in (-1, 0, 1):
        via('GND', ep[0] + i * 1.0, ep[1] + j * 1.0)
for n in ('22', '32'):
    c = padxy('U2', n)
    d = (ep[0] - c[0], ep[1] - c[1])
    d = (math.copysign(1, d[0]), 0) if abs(d[0]) > abs(d[1]) else (0, math.copysign(1, d[1]))   # straight inward
    track('GND', c, (c[0] + d[0] * 0.75, c[1] + d[1] * 0.75), pcbnew.F_Cu, 0.2)

# ------------------------------------------------------------------ top pad <-> bottom pad of the same net, very close together
# (magnetometer C1 cap under the IIS2MDC corner): F.Cu stub - via - B.Cu stub, placed before the fan-out vias
U3BODY = Point(B(FPS['U3'].GetPosition())).buffer(1.45)
for (rt, nt, rb, nb_) in [('U3', '5', 'C18', '1')]:
    nn = pad(rt, nt).GetNetname(); ct, cb = padxy(rt, nt), padxy(rb, nb_)
    best = None
    for i in range(-50, 51):
        for j in range(-50, 51):
            q = ((ct[0] + cb[0]) / 2 + i * 0.03, (ct[1] + cb[1]) / 2 + j * 0.03)
            if not via_ok(q, nn, 0.7):
                continue
            if LineString([ct, q]).buffer(0.075 + 0.1).intersects(foreign(nn, pcbnew.F_Cu)): continue
            if LineString([cb, q]).buffer(0.075 + 0.1).intersects(foreign(nn, pcbnew.B_Cu)): continue
            d = math.dist(ct, q) + math.dist(cb, q)
            if best is None or d < best[0]: best = (d, q)
    if best:
        track(nn, ct, best[1], pcbnew.F_Cu, 0.15); track(nn, cb, best[1], pcbnew.B_Cu, 0.15); via(nn, *best[1])
    print('%s: %s' % (nn, 'via at (%.2f, %.2f)' % best[1] if best else 'NO SPOT'))
# IIS2MDC GND pins 6 and 8 tied on F.Cu (pin 8 gets the fan-out via; the C1 via sits under the package centre)
_m = ((padxy('U3', '6')[0] + padxy('U3', '8')[0]) / 2 - 0.23, (padxy('U3', '6')[1] + padxy('U3', '8')[1]) / 2)   # bulge inward, clear of pin 7
track('GND', padxy('U3', '6'), _m, pcbnew.F_Cu, 0.15)
track('GND', _m, padxy('U3', '8'), pcbnew.F_Cu, 0.15)

# ------------------------------------------------------------------ module ground pins
SKIP = {('U2', n) for n in ('22', '32', '49')} | {('U8', n) for n in ('A2', 'B1', 'B2', 'B3')} | {('C36', '2'), ('U5', '2'), ('U3', '6')}

# ------------------------------------------------------------------ fan-out of the remaining GND / VBAT pads
pours = {}
for z in b.Zones():
    if not z.GetIsRuleArea() and z.GetLayer() == pcbnew.F_Cu:
        pours.setdefault(z.GetNetname(), []).append(polyset(z.Outline()))
PLANE_OK = {'GND': INNER, 'VBAT': INNER.intersection(VBAT_IN2.buffer(-0.5))}
fan = {'ok': 0, 'fail': []}
def fanout(ref, num, nn, L, poly, c):
    if Point(c).distance(ANT) < 0.3:            # pad on the antenna keep-out edge: start the stub inside it
        c = (c[0] + 0.14, c[1])
    for r in (0.55, 0.7, 0.85, 1.0, 1.2, 1.45, 1.75, 2.1, 2.5):
        for k in range(36):
            a = 2 * math.pi * k / 36
            q = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
            if not PLANE_OK[nn].contains(Point(q).buffer(0.25)) or not via_ok(q, nn):
                continue
            seg = LineString([c, q]).buffer(0.125 + 0.13)
            if seg.intersects(foreign(nn, L)) or LineString([c, q]).buffer(0.125).intersects(ANT):
                continue
            if L == pcbnew.B_Cu and not all(LineString([c, q]).distance(Point(c2)) >= 1.575 for t2, c2 in TPS.items() if pad(t2, '1').GetNetname() != nn):
                continue
            track(nn, c, q, L)
            via(nn, *q)
            fan['ok'] += 1
            return
    fan['fail'].append('%s.%s' % (ref, num))
for (ref, num, nn, L, poly, c) in sorted(PADS, key=lambda x: (x[2], x[0], x[1])):
    if nn not in ('GND', 'VBAT') or (ref, num) in SKIP or ref.startswith(('H', 'TP')):
        continue
    if L == pcbnew.F_Cu and any(pp.intersects(poly) for pp in pours.get(nn, [])):
        continue
    if pad(ref, num).GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
        continue
    fanout(ref, num, nn, L, poly, c)
print('fan-out vias:', fan['ok'], 'failed:', fan['fail'])

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD, b)

