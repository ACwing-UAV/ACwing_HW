# Freerouting DSN for rev C: power nets finished (removed), pours -> F.Cu keep-outs, In2 VBAT ring -> wire keep-out,
# pogo pads -> B.Cu wire keep-outs + via keep-outs, routing boundary 0.35 mm inside the outline
import sys, re, os, pcbnew
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
BOARD = sys.argv[1]
WORK = os.path.dirname(os.path.abspath(BOARD))
OX, OY = 150.0, 100.0
b = pcbnew.LoadBoard(BOARD)
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def polyset(ps):
    return unary_union([Polygon([B(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())]) for i in range(ps.OutlineCount())])
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
BOARD_POLY = polyset(ps)
VBAT_IN2 = unary_union([polyset(z.Outline()) for z in b.Zones() if z.GetZoneName() == 'VBAT_ring'])
TPS = {f.GetReference(): B(f.GetPosition()) for f in b.GetFootprints() if f.GetReference().startswith('TP')}
# ------------------------------------------------------------------ Freerouting DSN
dsn = os.path.join(WORK, 'DimaQuadFC_C2.dsn')
pcbnew.ExportSpecctraDSN(b, dsn)
s = open(dsn).read()
DONE = ['GND', 'VBAT', 'M1_N', 'M2_N', 'M3_N', 'M4_N']
s = re.sub(r'\n\s*\(plane [^\s]+ \(polygon[^)]*\)\)', '', s)
for n in DONE:
    s = re.sub(r'\n\s*\(net %s\s*\n?\s*\(pins[^)]*\)\s*\)' % n, '', s)
    s = re.sub(r'(\(class [^\n]*?) %s(?=[\s)])' % n, r'\1', s)
    s = s.replace('(net %s)' % n, '')
def dsnpts(coords): return ' '.join('%d %d' % (round((x + OX) * 1000), round(-(OY - y) * 1000)) for x, y in coords)
ko = ''
for z in b.Zones():
    if not z.GetIsRuleArea() and z.GetLayer() == pcbnew.F_Cu:
        pg = polyset(z.Outline())
        for g in (list(pg.geoms) if pg.geom_type == 'MultiPolygon' else [pg]):
            ko += '    (keepout "" (polygon F.Cu 0 %s))\n' % dsnpts(list(g.exterior.coords))
for g in (list(VBAT_IN2.geoms) if VBAT_IN2.geom_type == 'MultiPolygon' else [VBAT_IN2]):
    ko += '    (wire_keepout "" (polygon In2.Cu 0 %s))\n' % dsnpts(list(g.simplify(0.05).exterior.coords))
for t, c in TPS.items():          # pogo pads: foreign copper >= 1 mm on the bottom (own stub is fixed)
    ko += '    (wire_keepout "" (polygon B.Cu 0 %s))\n' % dsnpts(list(Point(c).buffer(1.5 + 0.05, 8).exterior.coords))
    ko += '    (via_keepout "" (polygon signal 0 %s))\n' % dsnpts(list(Point(c).buffer(1.5 + 0.25, 8).exterior.coords))
k = s.index('(keepout') if '(keepout' in s else s.index('(via ')
s = s[:k] + ko.lstrip() + '    ' + s[k:]
s = re.sub(r'(\(use_via [^)]*\))', r'\1\n        (use_layer F.Cu In2.Cu B.Cu)', s)
s = s.replace('(clearance 100.1)', '(clearance 110)')
inner = BOARD_POLY.buffer(-0.35).simplify(0.02)
s = re.sub(r'\(boundary\s*\(path pcb 0[^)]*\)\s*\)', '(boundary (path pcb 0 %s))' % dsnpts(list(inner.exterior.coords)), s, count=1)
open(dsn, 'w').write(s)
print('DSN ready:', dsn)
