# ACwing ESC1S rev A: Freerouting round trip for the signal nets (PWM_M1-4, CUR) on F.Cu / B.Cu only,
# GND stitching vias, zone fill.  python3 route_esc.py <board> <work dir>
# GND, VBAT and VBAT_RAW are complete from esc_power.py (planes, pours, fan-out): they are not routed.
import sys, os, re, subprocess, math
import pcbnew
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union
sys.path.insert(0, '/home/claude/genD')
from sexp import parse, find, find1

BOARD, WORK = sys.argv[1], sys.argv[2]
OX, OY = 150.0, 100.0
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def P(u, v): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + u), pcbnew.FromMM(OY - v))

# ---------------------------------------------------------------- 1. DSN (GND is left to the pours)
b = pcbnew.LoadBoard(BOARD)
for t in list(b.GetTracks()):
    if not t.IsLocked():
        b.Delete(t)
pcbnew.SaveBoard(BOARD, b)
b = pcbnew.LoadBoard(BOARD)
dsn = os.path.join(WORK, 'ACwing_ESC1S_B.dsn'); ses = dsn[:-4] + '.ses'
pcbnew.ExportSpecctraDSN(b, dsn)
s = open(dsn).read()
s = re.sub(r'\n\s*\(plane [^\s]+ \(polygon[^)]*\)\)', '', s)
DROP = ('GND', 'VBAT', 'VBAT_RAW', 'VBAT_SH', 'M1_N', 'M2_N', 'M3_N', 'M4_N')
for nn in DROP:
    s = re.sub(r'\n\s*\(net %s\s*\n?\s*\(pins[^)]*\)\s*\)' % nn, '', s)
    s = re.sub(r'\n[^\n]*\(net %s\)[^\n]*' % nn, '', s)
    s = re.sub(r'(\(class [^\n]*?) %s(?=[\s)])' % nn, r'\1', s)
# rev B: the charger BAT pin joins the battery at the J2+ pad (VBAT_RAW is otherwise complete from the pours), and the
# TSC213 VCC (U1.3) joins VBAT_SH at its VIN- pin (U1.5, Kelvin tap; the VCC current is a few uA)
k_net = s.index('(net ', s.index('(network'))
s = s[:k_net] + '(net VBAT_RAW (pins J2-1 U2-3 R16-1))\n      ' + s[k_net:]
s = re.sub(r'(\(class Power[^\n]*?)(\s*\(circuit)', r'\1 VBAT_RAW\2', s, count=1)
s = re.sub(r'(\(use_via [^)]*\))', r'\1\n        (use_layer F.Cu B.Cu)', s)
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
BP = Polygon([B(ps.Outline(0).CPoint(j)) for j in range(ps.Outline(0).PointCount())])
def dsnpts(coords): return ' '.join('%d %d' % (round((x + OX) * 1000), round(-(OY - y) * 1000)) for x, y in coords)
import json
ko = ''
# the locked GND stubs/vias are dropped with the GND net: give Freerouting their copper as keep-outs instead
for t in b.GetTracks():
    if t.IsLocked() and t.GetNetname() in DROP:
        if t.GetClass() == 'PCB_VIA':
            g = Point(B(t.GetPosition())).buffer(pcbnew.ToMM(t.GetWidth()) / 2, 8)
            for L in ('F.Cu', 'B.Cu'):
                ko += '    (keepout "" (polygon %s 0 %s))\n' % (L, dsnpts(list(g.exterior.coords)))
        else:
            g = LineString([B(t.GetStart()), B(t.GetEnd())]).buffer(pcbnew.ToMM(t.GetWidth()) / 2, 4)
            ko += '    (wire_keepout "" (polygon %s 0 %s))\n' % ('F.Cu' if t.GetLayer() == pcbnew.F_Cu else 'B.Cu', dsnpts(list(g.exterior.coords)))
# rev B: the power pours (motor stages, battery entry, charge switch) are not exported: keep the router off them
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() in ('GND', 'VBAT_RAW') or z.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu):
        continue
    ol = z.Outline()
    for i in range(ol.OutlineCount()):
        pts = [B(ol.Outline(i).CPoint(j)) for j in range(ol.Outline(i).PointCount())]
        g = Polygon(pts).buffer(0.1)
        ko += '    (wire_keepout "" (polygon %s 0 %s))\n' % ('F.Cu' if z.GetLayer() == pcbnew.F_Cu else 'B.Cu', dsnpts(list(g.exterior.coords)))
k_ = s.index('(keepout') if '(keepout' in s else s.index('(via ')
s = s[:k_] + ko.lstrip() + '    ' + s[k_:]
inner = BP.buffer(-0.4).simplify(0.02)
s = re.sub(r'\(boundary\s*\(path pcb 0[^)]*\)\s*\)', '(boundary (path pcb 0 %s))' % dsnpts(list(inner.exterior.coords)), s, count=1)
open(dsn, 'w').write(s)
print('keepouts in DSN:', s.count('(keepout'))
subprocess.run('timeout 900 xvfb-run -a java -jar /home/claude/tools/freerouting-1.9.0.jar -de %s -do %s -mp 30 -mt 1 > /tmp/claude-0/frESC.log 2>&1' % (dsn, ses), shell=True)
print(open('/tmp/claude-0/frESC.log').read().count('completed'), 'freerouting phases completed')

# ---------------------------------------------------------------- 2. SES import
b = pcbnew.LoadBoard(BOARD)
doc = parse(open(ses).read())[0]
routes = find1(doc, 'routes')
res = find1(routes, 'resolution')
scale_nm = {'um': 1000.0, 'mm': 1e6, 'mil': 25400.0, 'inch': 2.54e7}[str(res[1])] / float(res[2])
def pt(x, y): return pcbnew.VECTOR2I(int(round(float(x) * scale_nm)), int(round(-float(y) * scale_nm)))
LAYERS = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}
vias_def = {}
lib = find1(routes, 'library_out')
if lib:
    for p_ in find(lib, 'padstack'):
        m = re.search(r'_(\d+):(\d+)_um', p_[1])
        if m:
            vias_def[p_[1]] = (int(m.group(1)) * 1000, int(m.group(2)) * 1000)
anchors = [p.GetPosition() for fp in b.GetFootprints() for p in fp.Pads()]
locked = set()
for t in b.GetTracks():
    if t.IsLocked():
        anchors += [t.GetStart(), t.GetEnd()] if t.GetClass() == 'PCB_TRACK' else [t.GetPosition()]
        if t.GetClass() == 'PCB_VIA':
            locked.add((t.GetPosition().x // 1000, t.GetPosition().y // 1000))
def snap(v):
    for a in anchors:
        if abs(a.x - v.x) <= 5000 and abs(a.y - v.y) <= 5000:
            return pcbnew.VECTOR2I(a.x, a.y)
    return v
n_tr = n_via = 0
for netnode in find(find1(routes, 'network_out'), 'net'):
    ni = b.FindNet(netnode[1])
    for w in find(netnode, 'wire'):
        path = find1(w, 'path')
        if path is None:
            continue
        coords = path[3:]
        pts = [snap(pt(coords[i], coords[i + 1])) for i in range(0, len(coords) - 1, 2)]
        for a, c in zip(pts, pts[1:]):
            if a == c:
                continue
            t = pcbnew.PCB_TRACK(b); t.SetStart(a); t.SetEnd(c); t.SetWidth(int(float(path[2]) * scale_nm))
            t.SetLayer(LAYERS[path[1]]); t.SetNet(ni); b.Add(t); n_tr += 1
    for v in find(netnode, 'via'):
        d, dr = vias_def.get(v[1], (500000, 300000))
        if (pt(v[2], v[3]).x // 1000, pt(v[2], v[3]).y // 1000) in locked:
            continue
        pv = pcbnew.PCB_VIA(b); pv.SetPosition(pt(v[2], v[3])); pv.SetWidth(d); pv.SetDrill(dr)
        pv.SetViaType(pcbnew.VIATYPE_THROUGH); pv.SetNet(ni); b.Add(pv); n_via += 1
print('imported tracks', n_tr, 'vias', n_via)

# ---------------------------------------------------------------- 3. GND stitching vias (0.5/0.3) on a 1.6 mm grid
CLR = 0.2 + 0.25                                 # clearance + via radius
obst = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
for t in b.GetTracks():
    if t.GetNetname() == 'GND':
        continue
    w = pcbnew.ToMM(t.GetWidth()) / 2
    if t.GetClass() == 'PCB_VIA':
        for L in obst:
            obst[L].append(Point(B(t.GetPosition())).buffer(w))
    else:
        obst[t.GetLayer()].append(LineString([B(t.GetStart()), B(t.GetEnd())]).buffer(w))
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname() == 'GND' and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
            continue
        bb = p.GetBoundingBox()
        poly = sbox(*B(pcbnew.VECTOR2I(bb.GetX(), bb.GetBottom())), *B(pcbnew.VECTOR2I(bb.GetRight(), bb.GetY())))
        for L in obst:
            if p.IsOnLayer(L) or p.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH):
                obst[L].append(poly)
rules = []
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetDoNotAllowVias():
        o = z.Outline().Outline(0)
        rules.append(Polygon([B(o.CPoint(j)) for j in range(o.PointCount())]))
    elif z.GetIsRuleArea() or (not z.GetIsRuleArea() and z.GetNetname() != 'GND' and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu)):
        o = z.Outline().Outline(0)
        rules.append(Polygon([B(o.CPoint(j)) for j in range(o.PointCount())]))
O = unary_union(obst[pcbnew.F_Cu] + obst[pcbnew.B_Cu]).buffer(CLR)
R = unary_union(rules).buffer(0.3)
ok_area = BP.buffer(-(0.3 + 0.25 + 0.2))
gnd = b.FindNet('GND')
added = [Point(B(t.GetPosition())) for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']   # keep 1.2 mm from every via
for i in range(-8, 9):
    for j in range(-8, 9):
        q = Point(i * 2.4, j * 2.4)
        if ok_area.contains(q) and not O.contains(q) and not R.contains(q) and all(q.distance(a) > 1.2 for a in added):
            pv = pcbnew.PCB_VIA(b); pv.SetPosition(P(q.x, q.y)); pv.SetWidth(pcbnew.FromMM(0.5)); pv.SetDrill(pcbnew.FromMM(0.3))
            pv.SetViaType(pcbnew.VIATYPE_THROUGH); pv.SetNet(gnd); b.Add(pv); added.append(q)
print('GND stitching vias', sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND'))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD, b)
