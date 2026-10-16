# Imports a Freerouting .ses into the board (standalone: pcbnew.ImportSpecctraSES needs the GUI),
# adds the B.Cu GND pour, refills every zone and saves.
import sys, re
import pcbnew
sys.path.insert(0, '/home/claude/gen')
from sexp import parse, find, find1

BOARD, SES = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(BOARD)
doc = parse(open(SES).read())[0]
routes = find1(doc, 'routes')
res = find1(routes, 'resolution')
unit, div = str(res[1]), float(res[2])
scale_nm = {'um': 1000.0, 'mm': 1e6, 'mil': 25400.0, 'inch': 2.54e7}[unit] / div

def pt(x, y):
    return pcbnew.VECTOR2I(int(round(float(x) * scale_nm)), int(round(-float(y) * scale_nm)))

LAYERS = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu, 'In1.Cu': pcbnew.In1_Cu, 'In2.Cu': pcbnew.In2_Cu}
# via padstacks: "Via[0-3]_450:200_um"
vias_def = {}
lib = find1(routes, 'library_out')
if lib:
    for ps in find(lib, 'padstack'):
        m = re.search(r'_(\d+):(\d+)_um', ps[1])
        if m:
            vias_def[ps[1]] = (int(m.group(1)) * 1000, int(m.group(2)) * 1000)

locked = set()
for t in [t for t in b.GetTracks()]:
    if t.IsLocked() and t.GetClass() == 'PCB_VIA':
        locked.add((t.GetPosition().x // 1000, t.GetPosition().y // 1000))
    elif not t.IsLocked():
        b.Delete(t)
# fixed (locked) wires come back from Freerouting rounded to its grid: snap SES points within 5 um onto the
# locked track ends / pad centres so KiCad sees them connected
anchors = []
for t in b.GetTracks():
    if t.IsLocked() and t.GetClass() == 'PCB_TRACK':
        anchors += [t.GetStart(), t.GetEnd()]
for fp in b.GetFootprints():
    anchors += [p.GetPosition() for p in fp.Pads()]
locked_segs = [t for t in b.GetTracks() if t.IsLocked() and t.GetClass() == 'PCB_TRACK']
def snap(v):
    for a in anchors:
        if abs(a.x - v.x) <= 5000 and abs(a.y - v.y) <= 5000:
            return pcbnew.VECTOR2I(a.x, a.y)
    # T onto the middle of a locked wire: split the wire there so both pieces end on the new point
    for t in list(locked_segs):
        sx, sy, ex, ey = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
        dx, dy = ex - sx, ey - sy; L2 = float(dx * dx + dy * dy)
        if L2 == 0:
            continue
        k = ((v.x - sx) * dx + (v.y - sy) * dy) / L2
        if not 0 < k < 1:
            continue
        qx, qy = int(round(sx + k * dx)), int(round(sy + k * dy))
        if (qx - v.x) ** 2 + (qy - v.y) ** 2 > 5000 ** 2:
            continue
        q = pcbnew.VECTOR2I(qx, qy)
        t2 = pcbnew.PCB_TRACK(b); t2.SetStart(q); t2.SetEnd(t.GetEnd()); t2.SetWidth(t.GetWidth())
        t2.SetLayer(t.GetLayer()); t2.SetNet(t.GetNet()); t2.SetLocked(True); b.Add(t2)
        t.SetEnd(q)
        locked_segs.append(t2); anchors.append(q)
        return q
    return v
n_tr = n_via = 0
for netnode in find(find1(routes, 'network_out'), 'net'):
    name = netnode[1]
    ni = b.FindNet(name)
    if ni is None:
        print('unknown net', name); continue
    for w in find(netnode, 'wire'):
        path = find1(w, 'path')
        if path is None:
            continue
        layer, width = path[1], float(path[2]) * scale_nm
        coords = path[3:]
        pts = [snap(pt(coords[i], coords[i + 1])) for i in range(0, len(coords) - 1, 2)]
        for a, c in zip(pts, pts[1:]):
            if a == c:
                continue
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(a); t.SetEnd(c); t.SetWidth(int(width)); t.SetLayer(LAYERS[layer]); t.SetNet(ni)
            b.Add(t); n_tr += 1
    for v in find(netnode, 'via'):
        d, dr = vias_def.get(v[1], (450000, 200000))
        pos = pt(v[2], v[3])
        if (pos.x // 1000, pos.y // 1000) in locked:
            continue
        pv = pcbnew.PCB_VIA(b)
        pv.SetPosition(pt(v[2], v[3])); pv.SetWidth(d); pv.SetDrill(dr)
        pv.SetViaType(pcbnew.VIATYPE_THROUGH); pv.SetNet(ni)
        b.Add(pv); n_via += 1
print('imported tracks', n_tr, 'vias', n_via)

# B.Cu GND pour (around the bottom signals, outside the antenna rule area automatically)
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
for oz in [z for z in b.Zones()]:
    if oz.GetZoneName() == 'GND_Bot':
        b.Delete(oz)
z = pcbnew.ZONE(b)
z.SetLayer(pcbnew.B_Cu); z.SetNet(b.FindNet('GND')); z.SetZoneName('GND_Bot'); z.SetAssignedPriority(0)
z.SetLocalClearance(pcbnew.FromMM(0.25)); z.SetMinThickness(pcbnew.FromMM(0.2))
z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
z.SetThermalReliefGap(pcbnew.FromMM(0.25)); z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
o = ps.Outline(0); ol = z.Outline(); ol.NewOutline()
for j in range(o.PointCount()):
    ol.Append(o.CPoint(j).x, o.CPoint(j).y)
b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD, b)
pcbnew.WriteDRCReport(b, sys.argv[3] if len(sys.argv) > 3 else '/tmp/claude-0/drc.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True)
print('saved')
