# ACwing ESC 1S rev A: silkscreen legend (top), project footprint library (ACwing.pretty) with project 3D models.
#   python3 esc_finish.py <out dir>
import sys, os, re, json, shutil, math
import pcbnew
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

OUT = sys.argv[1]
PROJECT = 'ACwing_ESC1S_A'
BOARD = os.path.join(OUT, PROJECT + '.kicad_pcb')
SCH = os.path.join(OUT, PROJECT + '.kicad_sch')
OX, OY = 150.0, 100.0
LIB = 'ACwing'
LIB3D = '/usr/share/kicad/3dmodels'
D3 = os.path.join(OUT, '3d')
def P(u, v): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + u), pcbnew.FromMM(OY - v))
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def polyset(ps):
    return unary_union([Polygon([B(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())]) for i in range(ps.OutlineCount())])

b = pcbnew.LoadBoard(BOARD)
# ---------------------------------------------------------------- 1. silkscreen legend
for d in list(b.GetDrawings()):
    if d.GetLayer() == pcbnew.F_SilkS:
        b.Delete(d)
def text(s, u, v, size=0.8, rot=0, just=None):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(pcbnew.F_SilkS); t.SetPosition(P(u, v))
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size))); t.SetTextThickness(pcbnew.FromMM(0.15))
    t.SetTextAngleDegrees(rot)
    if just == 'left':
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    elif just == 'right':
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    b.Add(t); return t
def line(a, c):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.F_SilkS)
    s.SetStart(P(*a)); s.SetEnd(P(*c)); s.SetWidth(pcbnew.FromMM(0.151)); b.Add(s)
# board centre is free of parts (signals only): name, front arrow, motor legend next to each stage
text('ACwing ESC1S B', 0, 1.2, 0.8)
text('1S power board', 0, -0.3, 0.8)
ax, ay = 3.6, 3.6                                  # front = +u +v corner (as the FC)
line((ax - 0.9, ay - 0.9), (ax + 0.9, ay + 0.9))
line((ax + 0.9, ay + 0.9), (ax + 0.9, ay + 0.1)); line((ax + 0.9, ay + 0.9), (ax + 0.1, ay + 0.9))
text('FRONT', ax - 1.0, ay + 0.6, 0.8, just='right')
ROT = {'M1': ('CW', 0), 'M2': ('CCW', 90), 'M3': ('CCW', 270), 'M4': ('CW', 180)}
for m, (dirn, r) in ROT.items():
    rad = 4.7 if m == 'M1' else 5.4                 # M1: clear of the R1 / R5 references
    a = math.radians(r); q = (rad * math.sin(a), -rad * math.cos(a))
    text('%s %s' % (m, dirn), q[0], q[1], 0.8, rot=(r if r <= 90 else r - 180) if r != 270 else 90)
# polarity marks: "+" next to each motor pad 1 (VBAT) and battery pad 1, on a free spot (no pad, no courtyard, no silk)
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
EDGE_OK = polyset(ps).buffer(-0.35)
mask = unary_union([polyset((lambda s_: (p.TransformShapeToPolygon(s_, pcbnew.F_Mask, pcbnew.FromMM(0.15), pcbnew.FromMM(0.01)), s_)[1])(pcbnew.SHAPE_POLY_SET()))
                    for f in b.GetFootprints() for p in f.Pads() if p.IsOnLayer(pcbnew.F_Mask)] +
                   [Point(B(f.GetPosition())).buffer(1.4) for f in b.GetFootprints() if f.GetReference().startswith('H')])
silk = []
for f in b.GetFootprints():
    for it in list(f.GraphicalItems()) + [f.Reference()]:
        if it.GetLayer() == pcbnew.F_SilkS and it.IsVisible() if hasattr(it, 'IsVisible') else it.GetLayer() == pcbnew.F_SilkS:
            bb = it.GetBoundingBox()
            silk.append(box(*B(pcbnew.VECTOR2I(bb.GetLeft(), bb.GetBottom())), *B(pcbnew.VECTOR2I(bb.GetRight(), bb.GetTop()))))
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.F_SilkS:
        bb = d.GetBoundingBox()
        silk.append(box(*B(pcbnew.VECTOR2I(bb.GetLeft(), bb.GetBottom())), *B(pcbnew.VECTOR2I(bb.GetRight(), bb.GetTop()))))
SILK = unary_union(silk).buffer(0.1)
placed = []
for ref in ('M1', 'M2', 'M3', 'M4', 'J2'):
    pad1 = [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == '1'][0]
    pad2 = [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == '2'][0]
    c = B(pad1.GetPosition()); c2 = B(pad2.GetPosition()); best = None
    for rr in [0.8 + 0.1 * k for k in range(25)]:
        for k in range(36):
            a = 2 * math.pi * k / 36
            q = (c[0] + rr * math.cos(a), c[1] + rr * math.sin(a))
            g = box(q[0] - 0.45, q[1] - 0.45, q[0] + 0.45, q[1] + 0.45)
            if math.dist(q, c) + 1.0 < math.dist(q, c2) and EDGE_OK.contains(g) and not g.intersects(mask) and not g.intersects(SILK) and not any(g.intersects(x) for x in placed):
                best = q; break
        if best: break
    if best is None:
        print('no spot for + of', ref); continue
    placed.append(box(best[0] - 0.5, best[1] - 0.5, best[0] + 0.5, best[1] + 0.5))
    text('+', best[0], best[1], 0.9)
    print('+ for %s at (%.2f, %.2f), %.2f mm from pad 1' % (ref, best[0], best[1], math.dist(best, c)))
pcbnew.SaveBoard(BOARD, b)

# ---------------------------------------------------------------- 2. project library + 3D models
os.makedirs(os.path.join(OUT, LIB + '.pretty'), exist_ok=True)
os.makedirs(D3, exist_ok=True)
b = pcbnew.LoadBoard(BOARD)
parts = json.load(open(SCH + '.parts.json'))
src_lib = {}
for ref, v in parts.items():
    lib, name = v['fp'].split(':')
    src_lib[name] = lib
for name, lib in src_lib.items():
    d_ = '/home/claude/outE/ACwing.pretty' if os.path.exists('/home/claude/outE/ACwing.pretty/%s.kicad_mod' % name) else \
         '/usr/share/kicad/footprints/%s.pretty' % lib
    if not os.path.exists(os.path.join(d_, name + '.kicad_mod')):
        continue                                   # rerun: already in the project library
    pcbnew.FootprintSave(os.path.join(OUT, LIB + '.pretty'), pcbnew.FootprintLoad(d_, name))
for f in b.GetFootprints():
    f.SetFPID(pcbnew.LIB_ID(LIB, str(f.GetFPID().GetLibItemName())))
pcbnew.SaveBoard(BOARD, b)
MODEL_FOR = {'Vishay_PowerPAK_1212-8_Single': 'PowerPAK_1212-8_Single'}
def fix_models(text_):
    def sub(m):
        base = m.group(2)
        dst = MODEL_FOR.get(base, base)
        if not os.path.exists(os.path.join(D3, dst + '.step')):
            for src in (os.path.join('/home/claude/outE/3d', dst + '.step'), os.path.join('/home/claude/models_e', dst + '.step'),
                        os.path.join(LIB3D, m.group(1) + '.3dshapes', base + '.step')):
                if os.path.exists(src):
                    shutil.copy(src, os.path.join(D3, dst + '.step')); break
            else:
                print('NO MODEL', base)
        return '(model "${KIPRJMOD}/3d/%s.step"' % dst
    return re.subn(r'\(model "?\$\{KICAD\d_3DMODEL_DIR\}/([^/"]+)\.3dshapes/([^/" ]+)\.(?:wrl|step)"?', sub, text_)
s, n = fix_models(open(BOARD).read()); open(BOARD, 'w').write(s)
nl = 0
for fn in os.listdir(os.path.join(OUT, LIB + '.pretty')):
    p = os.path.join(OUT, LIB + '.pretty', fn)
    t, k = fix_models(open(p).read()); open(p, 'w').write(t); nl += k
for fn in set(re.findall(r'KIPRJMOD\}/3d/([^"]+\.step)', open(BOARD).read())):     # models already in project form (rev E library)
    if not os.path.exists(os.path.join(D3, fn)):
        shutil.copy(os.path.join('/home/claude/outE/3d', fn), os.path.join(D3, fn))
print('model paths: board %d, library %d; models in 3d/: %s' % (n, nl, ' '.join(sorted(os.listdir(D3)))))
s = open(SCH).read()
s2, k = re.subn(r'\(property "Footprint" "(?!%s:)[^":]+:([^"]+)"' % LIB, r'(property "Footprint" "%s:\1"' % LIB, s)
open(SCH, 'w').write(s2)
for v in parts.values():
    v['fp'] = LIB + ':' + v['fp'].split(':', 1)[1]
json.dump(parts, open(SCH + '.parts.json', 'w'), indent=0)
open(os.path.join(OUT, 'fp-lib-table'), 'w').write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.pretty")(options "")'
    '(descr "ACwing ESC1S project footprints (3D models in ${KIPRJMOD}/3d)"))\n)\n' % (LIB, LIB))
print('library', LIB, 'footprints', len(os.listdir(os.path.join(OUT, LIB + '.pretty'))), '| schematic links', k)
