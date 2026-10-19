# DimaQuadESC rev B (from rev A): board from the netlist. Rev B: charge port USB-C at a new 45 deg chamfer at the
#   front-left corner (mirror of the FC USB corner), charger on the top next to it, charge switch Q5 on the bottom next
#   to the shunt.
#   Frame C outline (same Edge.Cuts as DimaQuadFC rev E, 40 x 40 mm, chamfered rear-right corner), centred on (150, 100).
#   4 layers, 1.0 mm: In1 GND solid, In2 VBAT solid (distribution to the four stages), signals on F.Cu / B.Cu.
#   Motor stages copied from the rev E FC (validated hot-loop layout): stage 1 at the rear-right edge midpoint (bottom
#   edge in KiCad), the others rotated about the centre. M2 holes on the 20 x 20 pattern, hard mount to the frame.
#   Battery pads J2 at the rear-left corner, current shunt R9 + TSC213 on the bottom under them.
#   ESC link J1 (JST SH 8-pin) on the top at the rear edge, right of motor 1, mouth toward the rear (-v).
import sys, json, math, uuid
import xml.etree.ElementTree as ET
import pcbnew
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union

OUT, NETXML = sys.argv[1], sys.argv[2]
PROJECT = 'DimaQuadESC_B'
OX, OY = 150.0, 100.0
HOLES = [(10, 10), (-10, 10), (-10, -10), (10, -10)]
HOLE_KEEP = 2.6
def P(u, v): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + u), pcbnew.FromMM(OY - v))
def K(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))       # KiCad absolute mm
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
NS = uuid.UUID('9a3e51c2-77d0-4b1e-8c55-2f4d6b8e0a11')
def uid(*k): return str(uuid.uuid5(NS, '/'.join(map(str, k))))

board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(pcbnew.FromMM(1.0))
ds.SetAuxOrigin(K(130, 120)); ds.SetGridOrigin(K(130, 120))

# ---------------------------------------------------------------- outline: copy of the FC rev E Edge.Cuts
src = pcbnew.LoadBoard('/home/claude/outE/DimaQuadFC_E.kicad_pcb')
for d in src.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        a_, c_ = B(d.GetStart()), B(d.GetEnd())
        if d.GetShape() == pcbnew.SHAPE_T_ARC and abs(a_[0] + 20) < 0.01 and abs(c_[1] - 20) < 0.01:
            continue                                   # front-left R3 corner: replaced by the charge-port chamfer
        if d.GetShape() == pcbnew.SHAPE_T_SEGMENT and abs(a_[1] - 20) < 0.01 and abs(c_[1] - 20) < 0.01:
            continue                                   # front edge: redrawn
        if d.GetShape() == pcbnew.SHAPE_T_SEGMENT and abs(a_[0] + 20) < 0.01 and abs(c_[0] + 20) < 0.01:
            continue                                   # left edge: redrawn
        board.Add(d.Duplicate())
del src
def seg(a, c):
    s_ = pcbnew.PCB_SHAPE(board); s_.SetShape(pcbnew.SHAPE_T_SEGMENT); s_.SetLayer(pcbnew.Edge_Cuts)
    s_.SetStart(P(*a)); s_.SetEnd(P(*c)); s_.SetWidth(pcbnew.FromMM(0.1)); board.Add(s_)
# charge-port corner = the FC rev F-H USB corner mirrored about u = v: chamfer v - u = 36.2, 0.8 mm steps at the edges
CORNER = [(17, 20), (-11.5, 20), (-12.3, 20.8), (-15.4, 20.8), (-20.8, 15.4), (-20.8, 12.3), (-20, 11.5), (-20, -17)]
for a_, c_ in zip(CORNER, CORNER[1:]):
    seg(a_, c_)

# ---------------------------------------------------------------- nets and footprints
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
    return '/home/claude/outE/DimaQuad.pretty' if lib == 'DimaQuad' else '/usr/share/kicad/footprints/%s.pretty' % lib
FPD = {}
for ref, info in sorted(parts.items()):
    lib, name = info['fp'].split(':')
    fp = pcbnew.FootprintLoad(fp_dir(lib), name)
    if fp is None:
        fp = pcbnew.FootprintLoad('/home/claude/outE/DimaQuad.pretty', name)
    if fp is None:
        raise SystemExit('footprint not found ' + info['fp'])
    fp.SetReference(ref); fp.SetValue(info['value']); fp.SetFPID(pcbnew.LIB_ID('DimaQuad', name))
    fp.SetPath(pcbnew.KIID_PATH('/' + uid('sym', ref, 1)))
    board.Add(fp); FPD[ref] = fp
    for pad in fp.Pads():
        ni = pin_net.get((ref, pad.GetNumber()))
        if ni is not None:
            pad.SetNet(ni)

def put_abs(ref, x, y, rot, bottom=False):
    fp = FPD[ref]
    if fp.IsFlipped():
        fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(rot); fp.SetPosition(K(x, y))
    if bottom:
        fp.Flip(fp.GetPosition(), False)
def put(ref, u, v, rot, bottom=False): put_abs(ref, OX + u, OY - v, rot, bottom)
def cyard(fp):
    fp.BuildCourtyardCaches()
    c = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    return unary_union([Polygon([B(c.Outline(i).CPoint(j)) for j in range(c.Outline(i).PointCount())]) for i in range(c.OutlineCount())])
def pp(ref, num): return [B(p.GetPosition()) for p in FPD[ref].Pads() if p.GetNumber() == num][0]

# ---------------------------------------------------------------- fixed parts
for i, (u, v) in enumerate(HOLES):
    put('H%d' % (i + 1), u, v, 0)
# motor stages: exact rev E FC coordinates (rev E refs: D5-D8 -> D1-D4, R20-R23 -> R1-R4, R24-R27 -> R5-R8)
STAGES = {
    'Q1': (151.3, 111.0, -90), 'Q2': (161.0, 98.7, 0), 'Q3': (139.0, 101.3, 180), 'Q4': (148.7, 89.0, 90),
    'D1': (150.0, 114.9, 0), 'D2': (164.9, 100.5, 90), 'D3': (135.1, 100.0, -90), 'D4': (150.0, 85.1, 180),
    'M1': (150.0, 118.3, 0), 'M2': (168.3, 100.0, 90), 'M3': (131.7, 100.0, -90), 'M4': (150.0, 81.7, 180),
    'C2': (148.0, 111.0, 90), 'C3': (161.0, 102.0, 180), 'C4': (139.0, 98.0, 0), 'C5': (152.0, 89.0, -90),
    'R1': (150.35, 107.6, -90), 'R2': (157.6, 99.65, 0), 'R3': (142.4, 100.35, 180), 'R4': (149.65, 92.4, 90),
    'R5': (149.05, 107.6, -90), 'R6': (157.6, 100.95, 0), 'R7': (142.4, 99.05, 180), 'R8': (150.95, 92.4, 90),
    'J2': (134.939, 115.061, -135), 'C1': (142.35, 117.35, 0),
    'J4': (150 - 15.767, 100 - 15.767, 225),          # rev B: charge port, mouth toward the front-left chamfer
}
for ref, (x, y, r) in STAGES.items():
    put_abs(ref, x, y, r)
# J1 (top): mouth (fixing tabs, footprint +Y) toward the rear edge (-v); tabs 0.3 mm inside the outline
put('J1', 0, 0, 0)
mp = [pp('J1', 'MP')][0]; s1 = pp('J1', '1')
assert mp[1] < s1[1], 'J1 orientation'
U_J1 = 9.6
put('J1', U_J1, -20.0 + 0.35 + 0.9 - mp[1], 0)
for f in list(STAGES) + ['J1', 'H1', 'H2', 'H3', 'H4']:
    FPD[f].SetLocked(True)
print('J1 pin 1 at (%.2f, %.2f), pin 8 at (%.2f, %.2f)' % (pp('J1', '1') + pp('J1', '8')))

# ---------------------------------------------------------------- bottom: shunt and amplifier near the battery pads
ps = pcbnew.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
BOARD_POLY = Polygon([B(ps.Outline(0).CPoint(j)) for j in range(ps.Outline(0).PointCount())])
BP = BOARD_POLY.buffer(-0.3)
keep = unary_union([Point(hh).buffer(HOLE_KEEP + 0.05) for hh in HOLES])
# R9 vertical, pad 1 (VBAT_RAW) toward the battery pads. U1 turned so its VIN+/VIN- pins (4, 5) face the shunt
# (short Kelvin pair), OUT (6) leaves north to the RC filter R10/C6; C7 under the VCC pin (3).
def put_dir(ref, u, v, rots, test):
    for rot in rots:
        put(ref, u, v, rot, bottom=True)
        if test():
            return rot
    raise SystemExit('orientation ' + ref)
put_dir('R9', -14.8, -9.8, (90, 270), lambda: pp('R9', '1')[1] < pp('R9', '2')[1])
put_dir('U1', -12.3, -6.03, (0, 90, 180, 270), lambda: pp('U1', '4')[0] < pp('U1', '1')[0] and pp('U1', '4')[1] < pp('U1', '6')[1])
put_dir('C7', -9.55, -6.0, (0, 180), lambda: pp('C7', '1')[0] < pp('C7', '2')[0])
put_dir('R10', -11.2, -3.6, (0, 180), lambda: pp('R10', '1')[0] < pp('R10', '2')[0])
put_dir('C6', -9.3, -3.85, (90, 270), lambda: pp('C6', '1')[1] > pp('C6', '2')[1])
occ = [cyard(FPD[r_]) for r_ in ('R9', 'U1', 'C7', 'R10', 'C6')]
for i in range(len(occ)):
    assert BP.contains(occ[i]) and not occ[i].intersects(keep), i
    for j in range(i):
        assert not occ[i].intersects(occ[j]), (i, j)
for r_ in ('R9', 'U1', 'C7', 'R10', 'C6'):
    FPD[r_].SetLocked(True)
# rev B: charge switch Q5 on the TOP, left edge between the battery pads and motor stage 3: source pins (1-3) south
# toward the VBAT_SH via field next to the shunt (bottom), drain pad north (vias to the In2 VBAT plane)
for rot in (0, 90, 180, 270):
    put('Q5', -17.1, -6.5, rot)
    if pp('Q5', '1')[1] < pp('Q5', '5')[1] - 1:
        break
gq = cyard(FPD['Q5'])
assert BP.contains(gq) and not gq.intersects(keep)
FPD['Q5'].SetLocked(True)

# ---------------------------------------------------------------- rev B movable parts: nearest legal spot from a target
T = [
    # charger (top, front-left, next to the charge port); passives on the bottom
    ('U2', -15.6, 7.6, 90, False), ('C8', -17.9, 9.8, 90, False), ('C9', -13.6, 5.2, 0, False), ('D6', -18.6, 5.6, 90, False),
    ('R12', -15.0, 11.6, 0, True), ('R13', -16.4, 12.6, 0, True), ('R14', -14.0, 8.2, 90, True), ('R15', -17.6, 6.6, 90, True),
    ('R16', -13.6, 6.6, 0, True),
    # charge switch gate (bottom, next to Q5)
    ('R11', -13.8, -5.0, 90, False), ('D5', -13.8, -7.3, 90, False),
]
occ_all = {False: [cyard(FPD[r_]) for r_ in FPD if not FPD[r_].IsFlipped() and r_ in list(STAGES) + ['J1', 'Q5']],
           True: [cyard(FPD[r_]) for r_ in ('R9', 'U1', 'C7', 'R10', 'C6')] + [cyard(FPD['J4'])]}
moved = []
for ref, tu, tv, trot, bot in T:
    fp = FPD[ref]; best = None
    for rr in [0.1 * k for k in range(80)]:
        nk = max(1, int(6.28 * rr / 0.1))
        for kk in range(nk):
            a = 2 * math.pi * kk / nk
            q = (tu + rr * math.cos(a), tv + rr * math.sin(a))
            for rot in (trot, (trot + 90) % 360):
                put(ref, q[0], q[1], rot, bottom=bot)
                g = cyard(fp)
                if BP.contains(g) and not g.intersects(keep) and not any(g.intersects(o) for o in occ_all[bot]):
                    best = (q, rot); break
            if best: break
        if best: break
    if best is None:
        raise SystemExit('no spot for ' + ref)
    occ_all[bot].append(cyard(fp))
    if math.dist(best[0], (tu, tv)) > 0.3:
        moved.append('%s %.1f' % (ref, math.dist(best[0], (tu, tv))))
print('moved > 0.3 mm:', ', '.join(moved))

pcbnew.SaveBoard(OUT + '/%s.kicad_pcb' % PROJECT, board)

# ---------------------------------------------------------------- project rules (after SaveBoard)
pro = json.load(open('/home/claude/outE/DimaQuadFC_E.kicad_pro'))
ns = pro['net_settings']
base = [c for c in ns['classes'] if c['name'] == 'Default'][0]
d = dict(base); d.update(clearance=0.2, track_width=0.25, via_diameter=0.5, via_drill=0.3)
pw = dict(d); pw.update(name='Power', track_width=0.5)
ns['classes'] = [d, pw]
ns['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('GND', 'VBAT', 'VBAT_RAW', 'VBAT_SH', 'M*_N', 'VBUS')]
ns['netclass_assignments'] = None
rr = pro['board']['design_settings']['rules']
rr.update(min_clearance=0.15, min_track_width=0.15, min_via_diameter=0.45, min_via_annular_width=0.1,
          min_through_hole_diameter=0.2, min_hole_clearance=0.25, min_copper_edge_clearance=0.3, min_resolved_spokes=1)
pro['meta']['filename'] = PROJECT + '.kicad_pro'
json.dump(pro, open(OUT + '/%s.kicad_pro' % PROJECT, 'w'), indent=2)
print('footprints', len(FPD), 'nets', len(nets))
