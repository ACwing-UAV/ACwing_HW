# DimaQuad stack interference check: DimaQuadESC rev B (bottom) + DimaQuadFC rev H (grommets) + DimaQuadGPS rev C (standoffs).
# Every footprint becomes a prism (courtyard polygon x height); connectors also get the envelope of a mated plug in
# front of their mouth; holes get the mounting hardware. Prisms of different boards are checked pairwise.
# Output: JSON (objects + findings) for the 3D viewer, and a text report.
import json, math, sys
import pcbnew
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity

OX, OY = 150.0, 100.0
T_ESC, GAP, T_FC, STANDOFF, T_GPS = 1.0, 5.0, 1.0, float(sys.argv[1]) if len(sys.argv) > 1 else 6.0, 1.0
TAG = sys.argv[2] if len(sys.argv) > 2 else ''
Z = {'ESC': 0.0, 'FC': T_ESC + GAP, 'GPS': T_ESC + GAP + T_FC + STANDOFF}
THK = {'ESC': T_ESC, 'FC': T_FC, 'GPS': T_GPS}
BOARDS = {'ESC': '/home/claude/outESCB/DimaQuadESC_B.kicad_pcb', 'FC': '/home/claude/outH/DimaQuadFC_H.kicad_pcb',
          'GPS': '/home/claude/outGPSC/DimaQuadGPS_C.kicad_pcb'}
H = {   # body height above the board surface (mm, max from datasheets)
 'JST_SH_SM08B': 2.9, 'JST_SH_SM04B': 2.9, 'USB_C_Receptacle_HRO': 3.26, 'L_Sunlord_SWPA5040S': 4.0, 'CP_EIA-7343-31': 3.1,
 'D_SMAflat': 1.08, 'Vishay_PowerPAK': 1.04, 'C_1206': 1.8, 'R_1206': 0.6, 'C_1210': 1.0, 'C_0805': 1.45, 'C_0603': 0.9,
 'R_0603': 0.5, 'L_0805': 1.0, 'C_0402': 0.55, 'R_0402': 0.4, 'L_0402': 0.55, 'LED_0402': 0.45, 'TSOT-23-5': 1.0,
 'SOT-23-6': 1.45, 'SOT-23': 1.12, 'SOT-363': 1.1, 'D_SOD-523': 0.7, 'D_SOD-123F': 1.08, 'LED_WS2812B-2020': 0.84,
 'QFN-48': 0.6, 'LGA-14': 0.86, 'LGA-12': 0.7, 'ST_HLGA-10': 0.8, 'DFN-6': 0.6, 'Texas_DRC0010J': 1.0, 'WSON-8-1EP_6x5': 0.8,
 'Crystal_SMD_2016': 0.5, 'Johanson_2450AT18': 1.0, 'ST_MLPF': 0.65, 'ublox_SAM-M8Q': 6.3,
 'TestPoint': 0.05, 'BattPads': 1.6, 'MotorPads': 1.6,        # pads: solder joint + lead insulation
}
SKIP = ('MountingHole', 'Grommet')
def height(name):
    for k, v in H.items():
        if name.startswith(k):
            return v
    raise SystemExit('no height for ' + name)
# mated plugs: (length beyond the mouth, z range above the board surface, width margin), JLC / vendor drawings
PLUG = {'JST_SH': (7.0, (0.0, 3.3), -0.6, 0.8),   # SHR housing ~2.5 mm out of the receptacle + wire bend
        'USB_C': (25.0, (-1.7, 4.9), 1.7, -1.0)}  # overmold 12.4 x 6.6 mm centred 1.6 mm above the board, from 1 mm past the mouth

objs, out = [], []
def poly_of(shape_poly_set):
    return unary_union([Polygon([(pcbnew.ToMM(sp.CPoint(j).x) - OX, OY - pcbnew.ToMM(sp.CPoint(j).y)) for j in range(sp.PointCount())])
                        for sp in [shape_poly_set.Outline(i) for i in range(shape_poly_set.OutlineCount())]])
for bn, path in BOARDS.items():
    b = pcbnew.LoadBoard(path)
    ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
    outline = poly_of(ps)
    holes = [((pcbnew.ToMM(f.GetPosition().x) - OX), OY - pcbnew.ToMM(f.GetPosition().y)) for f in b.GetFootprints()
             if str(f.GetFPID().GetLibItemName()).startswith(SKIP)]
    objs.append(dict(board=bn, ref=bn + ' board', kind='board', poly=outline.difference(unary_union([Point(h).buffer(1.1) for h in holes])),
                     z=(Z[bn], Z[bn] + THK[bn])))
    for f in b.GetFootprints():
        name = str(f.GetFPID().GetLibItemName())
        if name.startswith(SKIP):
            continue
        f.BuildCourtyardCaches()
        bot = f.IsFlipped()
        cy = poly_of(f.GetCourtyard(pcbnew.B_CrtYd if bot else pcbnew.F_CrtYd))
        if cy.is_empty:
            continue
        h = height(name)
        z0 = Z[bn] - h if bot else Z[bn] + THK[bn]
        objs.append(dict(board=bn, ref=f.GetReference(), kind='part', name=name, side='bottom' if bot else 'top', poly=cy, z=(z0, z0 + h)))
        for key, (L, (za, zb), wm, inside) in PLUG.items():
            if name.startswith(key) or (key == 'USB_C' and name.startswith('USB_C')):
                # mouth = footprint +Y edge of the unrotated courtyard; plug envelope in front of it
                g = pcbnew.FOOTPRINT(f)
                if g.IsFlipped():
                    g.Flip(g.GetPosition(), False)
                g.SetOrientationDegrees(0); g.SetPosition(pcbnew.VECTOR2I(0, 0)); g.BuildCourtyardCaches()
                lc = affinity.translate(poly_of(g.GetCourtyard(pcbnew.F_CrtYd)), OX, -OY)
                x0, ymin, x1, ymax = lc.bounds                       # board (u, v) of the unrotated copy: v = -y
                # unrotated copy at the origin: KiCad +Y (mouth) is -v here
                mouth_v = ymin
                pl = box(x0 - wm, mouth_v - L, x1 + wm, mouth_v + inside)
                pl = affinity.rotate(pl, f.GetOrientationDegrees(), origin=(0, 0))
                c = (pcbnew.ToMM(f.GetPosition().x) - OX, OY - pcbnew.ToMM(f.GetPosition().y))
                if bot:                                              # KiCad flips about the footprint Y axis, angle mirrored
                    pl = affinity.scale(box(x0 - wm, mouth_v - L, x1 + wm, mouth_v + inside), 1, -1, origin=(0, 0))
                    pl = affinity.rotate(pl, -f.GetOrientationDegrees() if False else f.GetOrientationDegrees(), origin=(0, 0))
                pl = affinity.translate(pl, c[0], c[1])
                zz = (Z[bn] - zb, Z[bn] - za) if bot else (Z[bn] + THK[bn] + za, Z[bn] + THK[bn] + zb)
                objs.append(dict(board=bn, ref=f.GetReference() + ' plug', kind='plug', name=key, poly=pl, z=zz, owner=f.GetReference()))
    if bn == 'FC':   # mounting hardware: spacers / grommets ESC-FC (r 2.5), nylon standoffs FC-GPS (hex 3.5 -> r 2.0)
        for h_ in holes:
            objs.append(dict(board='HW', ref='grommet %+.0f,%+.0f' % h_, kind='hw', poly=Point(h_).buffer(2.5, 16), z=(Z['ESC'] + T_ESC, Z['FC'])))
            objs.append(dict(board='HW', ref='grommet flange %+.0f,%+.0f' % h_, kind='hw', poly=Point(h_).buffer(2.5, 16), z=(Z['FC'] + T_FC, Z['FC'] + T_FC + 1.0)))
            objs.append(dict(board='HW', ref='standoff %+.0f,%+.0f' % h_, kind='hw', poly=Point(h_).buffer(2.0, 6), z=(Z['FC'] + T_FC + 1.0, Z['GPS'])))

findings = []
WARN = 0.5
for i, a in enumerate(objs):
    for bb in objs[i + 1:]:
        if a['board'] == bb['board'] and not ('plug' in (a['kind'], bb['kind'])):
            continue
        if a.get('owner') == bb['ref'] or bb.get('owner') == a['ref'] or (a['kind'] == 'board' and bb['kind'] == 'board'):
            continue
        if a['board'] == bb['board'] and a['kind'] == 'board' or bb['board'] == a['board'] and bb['kind'] == 'board':
            if 'plug' in (a['kind'], bb['kind']):
                continue                                         # a plug always leaves its own board edge
        if a['kind'] == 'plug' and bb['kind'] == 'plug' and a['board'] == bb['board'] and False:
            continue
        ov = a['poly'].intersection(bb['poly']).area if a['poly'].intersects(bb['poly']) else 0.0
        dz = max(a['z'][0], bb['z'][0]) - min(a['z'][1], bb['z'][1])     # > 0: vertical gap, < 0: z ranges overlap
        if ov > 0.01:
            clear = dz
        else:
            d = a['poly'].distance(bb['poly'])
            clear = d if dz < 0 else math.hypot(d, dz)
        if clear < WARN:
            findings.append(dict(a=a['board'] + ' ' + a['ref'], b=bb['board'] + ' ' + bb['ref'], clear=round(clear, 2),
                                 plan_overlap=round(ov, 1), kinds=[a['kind'], bb['kind']],
                                 where=[round(x, 1) for x in (a['poly'].intersection(bb['poly']).centroid.coords[0] if ov > 0.01 else a['poly'].centroid.coords[0])]))
findings.sort(key=lambda f: f['clear'])
for f in findings:
    print('%-6s %6.2f mm  %-32s <-> %-32s  overlap %5.1f mm2  at %s' % ('CLASH' if f['clear'] < 0 else 'tight', f['clear'], f['a'], f['b'], f['plan_overlap'], f['where']))
json.dump(dict(stack=dict(T_ESC=T_ESC, GAP=GAP, T_FC=T_FC, STANDOFF=STANDOFF, T_GPS=T_GPS, Z=Z),
               findings=findings,
               objects=[dict(board=o['board'], ref=o['ref'], kind=o['kind'], z=o['z'],
                             poly=[list(map(lambda p: round(p, 2), xy)) for xy in (o['poly'].exterior.coords if o['poly'].geom_type == 'Polygon' else max(o['poly'].geoms, key=lambda g: g.area).exterior.coords)])
                        for o in objs]), open('/home/claude/stack/stack_check%s.json' % TAG, 'w'))
print(len(objs), 'objects,', len(findings), 'findings')
