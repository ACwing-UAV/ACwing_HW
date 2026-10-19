# ACwing Flow rev A: board from the netlist. 21 x 25 mm, R1.5 corners, 2 layers, 1.0 mm, all parts on the sensor
# side (KiCad top = the side facing the ground once mounted). Fixed: J1/J2 (Qwiic, left/right edge), U1 (PMW3901),
# U3 (VL53L1X), holes. The other parts move from a target to the nearest legal spot.
import sys, json, math, uuid
import xml.etree.ElementTree as ET
import pcbnew
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union

OUT, NETXML = sys.argv[1], sys.argv[2]
PROJECT = 'ACwing_Flow_A'
LIBN = 'ACwing_Flow'
OX, OY = 150.0, 100.0
HX, HY, RC = 10.5, 12.5, 1.5
HOLES = [(-8.0, 0.4), (8.0, 0.4)]
HOLE_KEEP = 2.4
def P(u, v): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + u), pcbnew.FromMM(OY - v))
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
NS = uuid.UUID('6f1c2d1e-3b7a-4c55-9a0e-1d2c3b4a5f60')
def uid(*k): return str(uuid.uuid5(NS, '/'.join(map(str, k))))

board = pcbnew.BOARD()
board.SetCopperLayerCount(2)
ds = board.GetDesignSettings()
ds.SetBoardThickness(pcbnew.FromMM(1.0))
ds.SetAuxOrigin(P(-HX, -HY)); ds.SetGridOrigin(P(-HX, -HY))

def seg(a, b_):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(P(*a)); s.SetEnd(P(*b_)); s.SetWidth(pcbnew.FromMM(0.1)); board.Add(s)
def arc(a, mid, b_):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetArcGeometry(P(*a), P(*mid), P(*b_)); s.SetWidth(pcbnew.FromMM(0.1)); board.Add(s)
r = RC; k = r * (1 - math.sqrt(0.5))
seg((-HX + r, HY), (HX - r, HY)); seg((HX, HY - r), (HX, -HY + r)); seg((HX - r, -HY), (-HX + r, -HY)); seg((-HX, -HY + r), (-HX, HY - r))
arc((HX - r, HY), (HX - k, HY - k), (HX, HY - r)); arc((HX, -HY + r), (HX - k, -HY + k), (HX - r, -HY))
arc((-HX + r, -HY), (-HX + k, -HY + k), (-HX, -HY + r)); arc((-HX, HY - r), (-HX + k, HY - k), (-HX + r, HY))

root = ET.parse(NETXML).getroot()
nets, pin_net = {}, {}
for n in root.find('nets').findall('net'):
    name = n.get('name').lstrip('/')
    if name.startswith('unconnected'):
        continue
    ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); nets[name] = ni
    for nd in n.findall('node'):
        pin_net[(nd.get('ref'), nd.get('pin'))] = ni
parts = json.load(open(OUT + '/%s.kicad_sch.parts.json' % PROJECT))
def fp_dir(lib):
    return OUT + '/%s.pretty' % LIBN if lib == LIBN else '/usr/share/kicad/footprints/%s.pretty' % lib
FPD = {}
for ref, info in sorted(parts.items()):
    lib, name = info['fp'].split(':')
    fp = pcbnew.FootprintLoad(fp_dir(lib), name)
    if fp is None:
        raise SystemExit('footprint not found ' + info['fp'])
    fp.SetReference(ref); fp.SetValue(info['value']); fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetPath(pcbnew.KIID_PATH('/' + uid('sym', ref, 1)))
    board.Add(fp); FPD[ref] = fp
    for pad in fp.Pads():
        ni = pin_net.get((ref, pad.GetNumber()))
        if ni is not None:
            pad.SetNet(ni)
    if info.get('dnp'):
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)

def put(ref, u, v, rot):
    fp = FPD[ref]; fp.SetOrientationDegrees(rot); fp.SetPosition(P(u, v))
def cyard(fp):
    fp.BuildCourtyardCaches()
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    return unary_union([Polygon([B(c.Outline(i).CPoint(j)) for j in range(c.Outline(i).PointCount())]) for i in range(c.OutlineCount())])

for i, (u, v) in enumerate(HOLES):
    put('H%d' % (i + 1), u, v, 0)
# Qwiic: J1 left edge (mouth -u), J2 right edge (mouth +u); MP tabs 0.35 mm inside the outline
for ref, sgn in (('J1', -1), ('J2', 1)):
    for rot in (90, 270):
        put(ref, 0, 7.0, rot)
        mp = [B(p.GetPosition()) for p in FPD[ref].Pads() if p.GetNumber() == 'MP']
        s1 = [B(p.GetPosition()) for p in FPD[ref].Pads() if p.GetNumber() == '1']
        if (mp[0][0] - s1[0][0]) * sgn > 1:
            break
    uu = sgn * (HX - 0.35 - 0.9) - mp[0][0]
    put(ref, uu, 7.0, rot)
put('U1', 0.0, -6.2, 0)          # PMW3901 in the lower half, decoupling to its left
put('U3', 0.0, 0.8, 0)           # VL53L1X above it
for f in ('J1', 'J2', 'U1', 'U3', 'H1', 'H2'):
    FPD[f].SetLocked(True)
T = [('C1', -5.0, -3.6, 90), ('C2', -6.2, -3.6, 90), ('C3', -4.0, -3.9, 90), ('R1', -7.4, -3.6, 90),
     ('C4', -5.0, -6.2, 90), ('C5', -4.0, -6.2, 90), ('C6', -5.0, -8.6, 90), ('C7', -4.0, -8.6, 90),
     ('R4', 4.1, -4.2, 90), ('R2', 5.1, -4.2, 90), ('R3', 6.1, -4.2, 90),
     ('U2', 6.0, -7.8, 0), ('C8', 8.3, -7.8, 90), ('C9', 6.0, -10.0, 0), ('R5', 3.6, -7.6, 270), ('R6', 3.6, -9.6, 270),
     ('C10', 3.6, 1.0, 90), ('C11', -3.8, 1.2, 90), ('R9', 4.6, 3.4, 90), ('R10', 5.6, 3.4, 90),
     ('U4', 0.0, 7.4, 0), ('C12', -2.6, 9.6, 0), ('C13', 2.6, 9.6, 0), ('C14', -2.4, 4.4, 0),
     ('R11', 2.6, 4.4, 0), ('D1', 4.6, 4.4, 0),
     ('TP1', -6.0, -11.2, 0), ('TP2', -3.6, -11.2, 0), ('TP3', 3.6, -11.2, 0), ('TP4', 6.0, -11.2, 0), ('TP5', 8.4, -11.0, 0)]
ps = pcbnew.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
BP = Polygon([B(ps.Outline(0).CPoint(j)) for j in range(ps.Outline(0).PointCount())]).buffer(-0.25)
keep = unary_union([Point(hh).buffer(HOLE_KEEP + 0.05) for hh in HOLES])
placed = {'J1', 'J2', 'U1', 'U3'}
# optical clearance: nothing taller than the sensors in front of them (keep the ToF emitter/receiver side clear)
for ref, tu, tv, trot in T:
    fp = FPD[ref]
    occ = unary_union([cyard(FPD[r_]) for r_ in placed])
    best = None
    for rr in [0.1 * kk for kk in range(80)]:
        nk = max(1, int(6.28 * rr / 0.1))
        for kk in range(nk):
            a = 2 * math.pi * kk / nk
            q = (tu + rr * math.cos(a), tv + rr * math.sin(a))
            for rot in (trot, (trot + 90) % 180):
                put(ref, q[0], q[1], rot)
                g = cyard(fp)
                if BP.contains(g) and not g.intersects(occ) and not g.intersects(keep):
                    best = (q, rot); break
            if best: break
        if best: break
    if best is None:
        raise SystemExit('no spot for ' + ref)
    placed.add(ref)
    if math.hypot(best[0][0] - tu, best[0][1] - tv) > 0.05:
        print('  %s moved %.2f mm' % (ref, math.hypot(best[0][0] - tu, best[0][1] - tv)))

# ---------------------------------------------------------------- PMW3901 GND pad: 4 vias at the pad corners (outside paste)
def via(net, q, d=0.45, dr=0.2):
    v_ = pcbnew.PCB_VIA(board); v_.SetPosition(P(*q)); v_.SetWidth(pcbnew.FromMM(d)); v_.SetDrill(pcbnew.FromMM(dr))
    v_.SetViaType(pcbnew.VIATYPE_THROUGH); v_.SetNet(nets[net]); v_.SetLocked(True); board.Add(v_)
cu = B(FPD['U1'].GetPosition())
for dx in (-0.93, 0.93):
    for dy in (-0.68, 0.68):
        via('GND', (cu[0] + dx, cu[1] + dy))
for p_ in FPD['U1'].Pads():
    if p_.GetNumber() == '29':
        p_.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

# ---------------------------------------------------------------- U2 (LDK130 DFN-6, 0.4 mm pitch) escape, locked
# Freerouting cannot leave the 0.12 mm pad gaps: short fixed stubs, the IN/EN tie outside pin 5, the GND via.
def _pp(ref, num): return [B(p_.GetPosition()) for p_ in FPD[ref].Pads() if p_.GetNumber() == num][0]
from shapely.geometry import LineString as _LS2
PRE = []
def tr0(net, pts, w=0.15):
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(pcbnew.FromMM(w))
        t.SetLayer(pcbnew.F_Cu); t.SetNet(nets[net]); t.SetLocked(True); board.Add(t)
        PRE.append(_LS2([a, c]).buffer(w / 2 + 0.12))
u = {n: _pp('U2', n) for n in '1234'} | {'6': _pp('U2', '6')}
sx = 1 if u['6'][0] > u['1'][0] else -1                  # +1: pins 4-6 on the +u side
up = 1 if u['1'][1] > u['3'][1] else -1                  # +1: pin 1 above pin 3
xo = u['6'][0] + sx * 0.58
tr0('+3V3', [u['6'], (xo, u['6'][1]), (xo, u['4'][1]), u['4']])
tr0('+3V3', [(xo, u['4'][1]), _pp('C8', '1')], w=0.25)
xi = u['1'][0] - sx * 0.38
r51, r52, r61 = _pp('R5', '1'), _pp('R5', '2'), _pp('R6', '1')
tr0('V2V0', [u['1'], (xi, u['1'][1]), (xi - sx * 0.4, u['1'][1] + up * 0.4), (r51[0] + sx * 0.35, r51[1]), r51])
tr0('Net-(U2-ADJ)', [u['3'], (xi, u['3'][1]), (xi - sx * 0.4, u['3'][1] - up * 0.4), (r52[0] + sx * 0.35, u['3'][1] - up * 0.4), r52])
tr0('Net-(U2-ADJ)', [r52, r61])
gvu = (u['2'][0] - sx * 0.93, u['2'][1])
tr0('GND', [u['2'], gvu], w=0.2)
v_ = pcbnew.PCB_VIA(board); v_.SetPosition(P(*gvu)); v_.SetWidth(pcbnew.FromMM(0.45)); v_.SetDrill(pcbnew.FromMM(0.2))
v_.SetViaType(pcbnew.VIATYPE_THROUGH); v_.SetNet(nets['GND']); v_.SetLocked(True); board.Add(v_)
print('U2 escape: R5.1 %s R5.2 %s R6.1 %s GND via %s' % (r51, r52, r61, gvu))

# ---------------------------------------------------------------- GND fan-out: every GND pad gets its own via (the sensor side
# is crowded and its pour breaks up; the solid B.Cu pour is the real ground)
def tr(net, a, c, w=0.25):
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(pcbnew.FromMM(w))
    t.SetLayer(pcbnew.F_Cu); t.SetNet(nets[net]); t.SetLocked(True); board.Add(t)
def padpoly(p_, grow):
    sp = pcbnew.SHAPE_POLY_SET(); p_.TransformShapeToPolygon(sp, pcbnew.F_Cu, pcbnew.FromMM(grow), pcbnew.FromMM(0.005))
    return unary_union([Polygon([B(sp.Outline(i).CPoint(j)) for j in range(sp.Outline(i).PointCount())]) for i in range(sp.OutlineCount())])
allpads = [(f.GetReference(), p_) for f in FPD.values() for p_ in f.Pads() if p_.IsOnLayer(pcbnew.F_Cu)]
vias_at = [B(t.GetPosition()) for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
segs = list(PRE)
holes_k = unary_union([Point(hh).buffer(HOLE_KEEP + 0.3) for hh in HOLES])
nfan, nfail = 0, []
for ref, p_ in allpads:
    if p_.GetNetname() != 'GND' or (ref == 'U1' and p_.GetNumber() == '29') or ref.startswith(('TP', 'H')):
        continue
    c = B(p_.GetPosition()); own = padpoly(p_, 0)
    foreign = unary_union([padpoly(q, 0.15) for r2, q in allpads if q.GetNetname() != 'GND'] + [g for g in segs])
    done = False
    for w_, cl_ in ((0.25, 0.12), (0.15, 0.1)):          # second pass: thin escape for 0.5 mm-pitch QFN/LGA pins
        foreign = unary_union([padpoly(q, cl_ + 0.03) for r2, q in allpads if q.GetNetname() != 'GND'] + [g for g in segs])
        for rr in (0.6, 0.75, 0.9, 1.05, 1.2, 1.4, 1.6, 1.8, 2.0, 2.3):
            for kk in range(36):
                a = 2 * math.pi * kk / 36
                q = (c[0] + rr * math.cos(a), c[1] + rr * math.sin(a))
                vg = Point(q).buffer(0.225 + cl_)
                if not BP.buffer(-0.3).contains(vg) or vg.intersects(foreign) or vg.intersects(holes_k):
                    continue
                if any(math.dist(q, v) < 0.7 for v in vias_at):
                    continue
                ln = __import__('shapely.geometry', fromlist=['LineString']).LineString([c, q]).buffer(w_ / 2 + cl_)
                if ln.intersects(foreign):
                    continue
                tr('GND', c, q, w_); via('GND', q); vias_at.append(q); segs.append(ln); nfan += 1; done = True
                break
            if done: break
        if done: break
    if not done:
        nfail.append('%s.%s' % (ref, p_.GetNumber()))
print('GND fan-out vias', nfan, 'failed', nfail)

# ---------------------------------------------------------------- zones and rule areas
def zone_from(poly, layer, net=None, name='', rule=False, prio=0):
    z = pcbnew.ZONE(board); z.SetLayer(layer)
    if rule:
        z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
        z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    else:
        z.SetNet(nets[net]); z.SetAssignedPriority(prio)
        z.SetLocalClearance(pcbnew.FromMM(0.2)); z.SetMinThickness(pcbnew.FromMM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.25)); z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName(name)
    ol = z.Outline(); ol.NewOutline()
    for (u, v) in list(poly.exterior.coords)[:-1]:
        p_ = P(u, v); ol.Append(p_.x, p_.y)
    board.Add(z)
full = sbox(-HX, -HY, HX, HY)
zone_from(full, pcbnew.F_Cu, 'GND', 'GND_Top')
zone_from(full, pcbnew.B_Cu, 'GND', 'GND_Bot')
for i, hh in enumerate(HOLES):
    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone_from(Point(hh).buffer(HOLE_KEEP, 16), L, name='HOLE_KEEP_%d' % (i + 1), rule=True)
json.dump({}, open(OUT + '/route_keepouts.json', 'w'))
pcbnew.SaveBoard(OUT + '/%s.kicad_pcb' % PROJECT, board)

# ---------------------------------------------------------------- project rules (after SaveBoard)
pro = json.load(open('/home/claude/outE/ACwing_FC_E.kicad_pro'))
ns = pro['net_settings']
base = [c for c in ns['classes'] if c['name'] == 'Default'][0]
d = dict(base); d.update(clearance=0.12, track_width=0.15, via_diameter=0.45, via_drill=0.2)
pw = dict(d); pw.update(name='Power', track_width=0.3)
ns['classes'] = [d, pw]
ns['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('+3V3', 'GND', 'V2V0', 'PMW_VDD')]
ns['netclass_assignments'] = None
rr = pro['board']['design_settings']['rules']
rr.update(min_clearance=0.1, min_track_width=0.1, min_via_diameter=0.4, min_via_annular_width=0.1,
          min_through_hole_diameter=0.2, min_hole_clearance=0.2, min_copper_edge_clearance=0.3, min_resolved_spokes=1)
pro['meta']['filename'] = PROJECT + '.kicad_pro'
json.dump(pro, open(OUT + '/%s.kicad_pro' % PROJECT, 'w'), indent=2)
print('footprints', len(FPD), 'nets', len(nets))
