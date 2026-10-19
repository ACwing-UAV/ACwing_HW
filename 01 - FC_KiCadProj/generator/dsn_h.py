# Freerouting DSN for rev F: GND finished (planes + fan-out, removed), routing on F.Cu / In2.Cu / B.Cu,
# pogo pads -> B.Cu wire keep-outs + via keep-outs, RF line -> F.Cu wire keep-out band, boundary 0.35 mm inside
import sys, re, os, pcbnew
from shapely.geometry import Polygon, Point, LineString
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
TPS = {f.GetReference(): B(f.GetPosition()) for f in b.GetFootprints() if f.GetReference().startswith('TP')}
dsn = os.path.join(WORK, 'ACwing_FC_A.dsn')
pcbnew.ExportSpecctraDSN(b, dsn)
s = open(dsn).read()
DONE = ['GND']
s = re.sub(r'\n\s*\(plane [^\s]+ \(polygon[^)]*\)\)', '', s)
for n in DONE:
    s = re.sub(r'\n\s*\(net %s\s*\n?\s*\(pins[^)]*\)\s*\)' % n, '', s)
    s = re.sub(r'(\(class [^\n]*?) %s(?=[\s)])' % n, r'\1', s)
    s = s.replace('(net %s)' % n, '')
def dsnpts(coords): return ' '.join('%d %d' % (round((x + OX) * 1000), round(-(OY - y) * 1000)) for x, y in coords)
ko = ''
for t, c in TPS.items():
    ko += '    (wire_keepout "" (polygon B.Cu 0 %s))\n' % dsnpts(list(Point(c).buffer(1.5 + 0.05, 8).exterior.coords))
    ko += '    (via_keepout "" (polygon signal 0 %s))\n' % dsnpts(list(Point(c).buffer(1.5 + 0.25, 8).exterior.coords))
rf = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and abs(pcbnew.ToMM(t.GetWidth()) - 0.36) < 1e-3]
band = unary_union([LineString([B(t.GetStart()), B(t.GetEnd())]).buffer(0.18 + 0.45) for t in rf])
for g in (list(band.geoms) if band.geom_type == 'MultiPolygon' else [band]):
    ko += '    (wire_keepout "" (polygon F.Cu 0 %s))\n' % dsnpts(list(g.simplify(0.02).exterior.coords))
k = s.index('(keepout') if '(keepout' in s else s.index('(via ')
s = s[:k] + ko.lstrip() + '    ' + s[k:]
s = re.sub(r'(\(use_via [^)]*\))', r'\1\n        (use_layer F.Cu In2.Cu B.Cu)', s)
inner = BOARD_POLY.buffer(-0.35).simplify(0.02)
s = re.sub(r'\(boundary\s*\(path pcb 0[^)]*\)\s*\)', '(boundary (path pcb 0 %s))' % dsnpts(list(inner.exterior.coords)), s, count=1)
open(dsn, 'w').write(s)
print('DSN ready:', dsn, '| RF band segments', len(rf))
