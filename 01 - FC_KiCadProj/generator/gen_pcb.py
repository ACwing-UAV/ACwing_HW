# DimaQuadFC rev C (frame C): builds DimaQuadFC_C.kicad_pcb from the mechanical handoff
#   outline  DimaQuadFC_C_Edge_Cuts.dxf   (board frame, Y up, origin at the board centre)
#   keepouts DimaQuadFC_C_Keepouts.dxf    (same frame) -> User.1 drawing + rule areas
#   placement DimaQuadFC_C_Placement.csv  (KiCad X/Y, bottom parts with the rotation before the flip)
import sys, math, csv, json, re, xml.etree.ElementTree as ET
import ezdxf, pcbnew
sys.path.insert(0, '/home/claude/genC2')
from kisch import uid

OUTDIR, EDGE, KEEP, CSVF, NETXML = sys.argv[1:6]
PROJECT = 'DimaQuadFC_C2'
OX, OY = 150.0, 100.0

def P(x, y):                     # board frame (mm, Y up) -> KiCad internal units
    return pcbnew.VECTOR2I(pcbnew.FromMM(float(OX + x)), pcbnew.FromMM(float(OY - y)))
def PK(X, Y):                    # KiCad mm -> internal
    return pcbnew.VECTOR2I(pcbnew.FromMM(X), pcbnew.FromMM(Y))

board = pcbnew.NewBoard(OUTDIR + '/%s.kicad_pcb' % PROJECT)
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetAuxOrigin(P(-20, -20)); ds.SetGridOrigin(P(0, 0))   # drill/place origin = board lower-left corner (CPL, Gerber, drill)
board.SetLayerName(pcbnew.User_1, 'User.Keepout')

def shape(kind, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(kind); s.SetLayer(layer); s.SetWidth(pcbnew.FromMM(w))
    board.Add(s)
    return s

def add_dxf(path, layer_of):
    n = 0
    for e in ezdxf.readfile(path).modelspace():
        L = layer_of(e.dxf.layer)
        if L is None:
            continue
        t = e.dxftype()
        if t == 'LINE':
            s = shape(pcbnew.SHAPE_T_SEGMENT, L)
            s.SetStart(P(e.dxf.start.x, e.dxf.start.y)); s.SetEnd(P(e.dxf.end.x, e.dxf.end.y))
        elif t == 'CIRCLE':
            c, r = e.dxf.center, e.dxf.radius
            s = shape(pcbnew.SHAPE_T_CIRCLE, L)
            s.SetCenter(P(c.x, c.y)); s.SetEnd(P(c.x + r, c.y))
        elif t == 'ARC':
            c, r = e.dxf.center, e.dxf.radius
            a0, a1 = e.dxf.start_angle, e.dxf.end_angle
            sweep = (a1 - a0) % 360 or 360
            pt = lambda a: (c.x + r * math.cos(math.radians(a)), c.y + r * math.sin(math.radians(a)))
            s = shape(pcbnew.SHAPE_T_ARC, L)
            s.SetArcGeometry(P(*pt(a0)), P(*pt(a0 + sweep / 2)), P(*pt(a0 + sweep)))
        elif t == 'LWPOLYLINE':
            pts = [(p[0], p[1]) for p in e.get_points()]
            if e.closed and pts[0] != pts[-1]:
                pts.append(pts[0])
            for a, b in zip(pts, pts[1:]):
                s = shape(pcbnew.SHAPE_T_SEGMENT, L)
                s.SetStart(P(*a)); s.SetEnd(P(*b))
        else:
            continue
        n += 1
    return n

n_edge = add_dxf(EDGE, lambda l: pcbnew.Edge_Cuts)
# keep-out drawing for reference (the grommet holes come from the H1..H4 footprints)
n_keep = add_dxf(KEEP, lambda l: None if l in ('OUTLINE_REF', 'GROMMET_HOLES') else pcbnew.User_1)

def rule_area(name, pts, layers, tracks=True, vias=True, pour=True, fps=False):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True); z.SetZoneName(name)
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowCopperPour(pour)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(fps)
    ls = pcbnew.LSET()
    for L in layers:
        ls.AddLayer(L)
    z.SetLayerSet(ls)
    o = z.Outline(); o.NewOutline()
    for (x, y) in pts:
        v = P(x, y); o.Append(v.x, v.y)
    board.Add(z)

def circle_pts(cx, cy, r, n=40):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]

ALLCU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
doc = ezdxf.readfile(KEEP).modelspace()
# rev C2: chip antenna AE1 at the left edge, top-left corner. No pour and no vias on any layer; tracks allowed
# (the only track is the 0.7 mm feed from the tuning resistor to the antenna pad)
rule_area('ANTENNA_AE1', [(-20.5, 9.0), (-17.5, 9.0), (-17.5, 20.5), (-20.5, 20.5)], ALLCU, tracks=False)
HOLES = [(e.dxf.center.x, e.dxf.center.y) for e in doc if e.dxf.layer == 'GROMMET_HOLES']
for i, (x, y) in enumerate(HOLES):
    # the grommet flange clamps the board: no tracks / vias on the outer layers within r 2.75 (pour allowed)
    rule_area('GROMMET_CU_%d' % (i + 1), circle_pts(x, y, 2.75), [pcbnew.F_Cu, pcbnew.B_Cu], pour=False)
    # component keep-outs r 3.0 (top) / 3.6 (bottom): drawn on User.Keepout and checked by check_mech.py

# ------------------------------------------------------------------ nets
root = ET.parse(NETXML).getroot()
nets, pin_net = {}, {}
for n in root.find('nets'):
    name = n.get('name').lstrip('/')
    if name.startswith('unconnected'):
        continue
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    nets[name] = ni
    for nd in n.findall('node'):
        pin_net[(nd.get('ref'), nd.get('pin'))] = ni

parts = json.load(open(OUTDIR + '/%s.kicad_sch.parts.json' % PROJECT))
place = {r['Ref']: r for r in csv.DictReader(open(CSVF))}
def fp_dir(lib):
    return OUTDIR + '/DimaQuad.pretty' if lib == 'DimaQuad' else '/usr/share/kicad/footprints/%s.pretty' % lib

missing = []
for ref in sorted(parts, key=lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))):
    info = parts[ref]
    lib, name = info['fp'].split(':')
    fp = pcbnew.FootprintLoad(fp_dir(lib), name)
    if fp is None:
        raise SystemExit('footprint not found: ' + info['fp'])
    fp.SetReference(ref); fp.SetValue(info['value']); fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetPath(pcbnew.KIID_PATH('/' + uid('sym', ref, 1)))
    board.Add(fp)
    for pad in fp.Pads():
        ni = pin_net.get((ref, pad.GetNumber()))
        if ni is not None:
            pad.SetNet(ni)
    r = place.get(ref)
    if r is None:
        missing.append(ref); continue
    rot = float(r['Rot_deg'])
    if ref in ('C2', 'C3', 'C4', 'C5'):
        # 10 uF of the motor stage turned 180 deg: + next to the D cathode, - next to the Q sources
        # (as placed, + faced the sources and - the cathode, so the hot loop could not close on F.Cu)
        rot += 180
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(PK(float(r['X_mm']), float(r['Y_mm'])))
    if ref == 'J1':
        # front shell legs were 0.253 mm from the bottom/right edges (rule 0.3): 0.1 mm inboard along the
        # receptacle axis (mouth 0.45 -> 0.35 mm beyond the chamfer flat)
        d = 0.1 / math.sqrt(2)
        fp.SetPosition(PK(float(r['X_mm']) - d, float(r['Y_mm']) - d))
    if r['Side'] == 'bottom':
        fp.Flip(fp.GetPosition(), False)
    fp.SetLocked(r['Status'] == 'FIXED')
    if ref.startswith('TP'):
        for pad in fp.Pads():          # pogo pads: 1 mm free of foreign copper all around
            pad.SetLocalClearance(pcbnew.FromMM(1.0))

# ------------------------------------------------------------------ rev C2: parts without a CSV position -> nearest legal spot
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
def B_(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def cyard(fp):
    fp.BuildCourtyardCaches()
    c = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    return unary_union([Polygon([B_(c.Outline(i).CPoint(j)) for j in range(c.Outline(i).PointCount())]) for i in range(c.OutlineCount())])
ps = pcbnew.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
BP = Polygon([B_(ps.Outline(0).CPoint(j)) for j in range(ps.Outline(0).PointCount())]).buffer(-0.25)
FPD = {f.GetReference(): f for f in board.GetFootprints()}
HOLES_ = [(8, 8), (-8, 8), (-8, -8), (8, -8)]
ANT_ = sbox(-20.5, 9.0, -17.5, 20.5)
POGO_ = sbox(-3.81 - 1.5, -14.27 - 1.5, 3.81 + 1.5, -11.73 + 1.5)
import fanout_c2
VIA_KEEP = unary_union([Point(x - OX, OY - y).buffer(0.225 + 0.12) for (_, x, y) in fanout_c2.VIAS])   # escape vias
TGT = list(csv.DictReader(open(OUTDIR + '/C2_bottom_targets.csv'))) if __import__('os').path.exists(OUTDIR + '/C2_bottom_targets.csv') else []
for t in TGT:
    fp = FPD[t['Ref']]; bot = t['Side'] == 'bottom'
    tx, ty = float(t['X']) - OX, OY - float(t['Y'])
    occ = unary_union([cyard(f) for r, f in FPD.items() if r in place or r in [x['Ref'] for x in TGT[:TGT.index(t)]]
                       if f.IsFlipped() == bot and not r.startswith('H')])
    keep = unary_union([Point(h).buffer(3.6 if bot else 3.0) for h in HOLES_] + [ANT_, VIA_KEEP] + ([POGO_] if bot else []))
    best = None
    for r_ in [0.1 * k for k in range(60)]:
        for k in range(max(1, int(6.28 * r_ / 0.1))):
            a = 2 * math.pi * k / max(1, int(6.28 * r_ / 0.1))
            q = (tx + r_ * math.cos(a), ty + r_ * math.sin(a))
            for rot in ((int(t['Rot']), 90 - int(t['Rot'])) if t.get('Rot') else (0, 90)):
                if fp.IsFlipped():
                    fp.Flip(fp.GetPosition(), False)
                fp.SetOrientationDegrees(rot); fp.SetPosition(P(*q))
                if bot:
                    fp.Flip(fp.GetPosition(), False)
                g = cyard(fp)
                if BP.contains(g) and not g.intersects(occ) and not g.intersects(keep):
                    best = (q, rot); break
            if best: break
        if best: break
    if best is None:
        missing.append(t['Ref'] + '(no spot)')
    else:
        place[t['Ref']] = best
        missing = [m for m in missing if m != t['Ref']]
        print('placed %s %s at (%.2f, %.2f) rot %d' % (t['Ref'], t['Side'], OX + best[0][0], OY - best[0][1], best[1]))

pcbnew.SaveBoard(OUTDIR + '/%s.kicad_pcb' % PROJECT, board)
print('edge', n_edge, 'keepout drawing', n_keep, 'footprints', len(parts), 'nets', len(nets), 'not in CSV:', missing)
