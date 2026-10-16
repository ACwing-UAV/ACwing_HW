# Reference designators on the silkscreen: each label is placed next to its part, on the part's side, so that it
#   - stays inside the board (0.3 mm from the edge and from the holes),
#   - does not touch any pad (mask opening) or another part's courtyard on the same side,
#   - does not touch another label or another part's silk outline.
# Parts with no free spot keep their reference on the Fab layer only (assembly drawing) and are listed.
# Also syncs the footprint values with the schematic (parts.json).
import sys, json, math, pcbnew
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely.affinity import translate, rotate as srot

BOARD, PARTS = sys.argv[1], sys.argv[2]
H_TXT, T_TXT = 0.8, 0.15          # text height / stroke (mm)
OX, OY = 150.0, 100.0
b = pcbnew.LoadBoard(BOARD)
def mm(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def P(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY - y))
def polyset(ps):
    return unary_union([Polygon([mm(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())]) for i in range(ps.OutlineCount())])


from shapely.geometry import LineString
def shape_poly(it):
    w = max(pcbnew.ToMM(it.GetWidth()), 0.05) / 2
    st = it.GetShape()
    if st == pcbnew.SHAPE_T_SEGMENT:
        return LineString([mm(it.GetStart()), mm(it.GetEnd())]).buffer(w)
    if st == pcbnew.SHAPE_T_RECT:
        a, c = mm(it.GetStart()), mm(it.GetEnd())
        r = box(min(a[0], c[0]), min(a[1], c[1]), max(a[0], c[0]), max(a[1], c[1]))
        return r.buffer(w) if it.IsFilled() else r.exterior.buffer(w)
    if st == pcbnew.SHAPE_T_CIRCLE:
        c = Point(mm(it.GetCenter())); r = pcbnew.ToMM(it.GetRadius())
        return c.buffer(r + w) if it.IsFilled() else c.buffer(r).exterior.buffer(w)
    if st == pcbnew.SHAPE_T_ARC:
        pts = [mm(it.GetStart()), mm(it.GetArcMid()), mm(it.GetEnd())]
        return LineString(pts).buffer(w)
    bb = it.GetBoundingBox()
    return box(*mm(pcbnew.VECTOR2I(bb.GetLeft(), bb.GetBottom())), *mm(pcbnew.VECTOR2I(bb.GetRight(), bb.GetTop())))

parts = json.load(open(PARTS))
nval = 0
for fp in b.GetFootprints():
    v = parts.get(fp.GetReference(), {}).get('value')
    if v and fp.GetValue() != v:
        fp.SetValue(v); nval += 1

ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
OK_AREA = polyset(ps).buffer(-0.3)
SIDE = {False: pcbnew.F_SilkS, True: pcbnew.B_SilkS}
CU = {False: pcbnew.F_Cu, True: pcbnew.B_Cu}
pads, crt, silk = {False: [], True: []}, {False: {}, True: {}}, {False: {}, True: {}}
for fp in b.GetFootprints():
    bot = fp.IsFlipped()
    ref = fp.GetReference()
    for p in fp.Pads():
        for side in (False, True):
            if p.IsOnLayer(CU[side]) or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, CU[side], 0, pcbnew.FromMM(0.01))
                pads[side].append((ref, polyset(s).buffer(0.12 if p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH else 0.3)))
    fp.BuildCourtyardCaches()
    c = fp.GetCourtyard(pcbnew.B_CrtYd if bot else pcbnew.F_CrtYd)
    if c.OutlineCount():
        crt[bot][ref] = polyset(c)
    g = []
    for it in fp.GraphicalItems():
        if it.GetLayer() == SIDE[bot] and it.GetClass() in ('FP_SHAPE', 'PCB_SHAPE', 'MGRAPHIC'):
            g.append(shape_poly(it))
    if g:
        silk[bot][ref] = unary_union(g)

placed = {False: [], True: []}
# polarity marks '+' / '-' of the motor and battery pads: next to their own pad, same rules as the labels
marks = []
for fp in b.GetFootprints():
    if not fp.GetFPID().GetLibItemName().wx_str().startswith(('MotorPads', 'BattPads')):
        continue
    bot = fp.IsFlipped()
    for it in fp.GraphicalItems():
        if it.GetClass() == 'FP_TEXT' and it.GetText() in ('+', '-'):
            pad_ = [p for p in fp.Pads() if p.GetNumber() == ('1' if it.GetText() == '+' else '2')][0]
            pc = mm(pad_.GetPosition())
            sp = pcbnew.SHAPE_POLY_SET(); pad_.TransformShapeToPolygon(sp, CU[bot], 0, pcbnew.FromMM(0.01))
            pp = polyset(sp)
            it.SetTextAngleDegrees(0); it.SetPosition(P(0, 0)); bb = it.GetBoundingBox()
            w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
            tb = box(-w / 2, -h / 2, w / 2, h / 2).buffer(-0.08)
            pad_all = unary_union([g for r, g in pads[bot]])
            oc = unary_union([g for r, g in crt[bot].items() if r != fp.GetReference()])
            osk = unary_union(list(silk[bot].values()))
            lab = unary_union(placed[bot])
            ok = None
            other = [p for p in fp.Pads() if p.GetNumber() != pad_.GetNumber()][0]
            oc_ = mm(other.GetPosition())
            eo = (pc[0] - oc_[0], pc[1] - oc_[1]); n_ = math.hypot(*eo); eo = (eo[0] / n_, eo[1] / n_)
            ei = (-eo[1], eo[0]) if (pc[0] * -eo[1] + pc[1] * eo[0]) < 0 else (eo[1], -eo[0])   # perpendicular, toward the centre
            hw = abs((pp.bounds[2] - pp.bounds[0]) * eo[0]) + abs((pp.bounds[3] - pp.bounds[1]) * eo[1])
            hh = abs((pp.bounds[2] - pp.bounds[0]) * ei[0]) + abs((pp.bounds[3] - pp.bounds[1]) * ei[1])
            cand = []
            for r_ in [0.15 + 0.1 * k for k in range(20)]:
                cand.append((pc[0] + eo[0] * (hw / 2 + w / 2 + r_), pc[1] + eo[1] * (hw / 2 + w / 2 + r_)))           # beside, outward
                for f_ in (0.0, 0.4):
                    cand.append((pc[0] + ei[0] * (hh / 2 + h / 2 + r_) + eo[0] * f_, pc[1] + ei[1] * (hh / 2 + h / 2 + r_) + eo[1] * f_))  # inboard
            for q in cand:
                g = translate(tb, *q)
                if OK_AREA.contains(g) and not g.intersects(pad_all) and not g.intersects(osk) \
                        and (lab.is_empty or not g.buffer(0.1).intersects(lab)):
                    ok = (q, g); break
            if ok:
                it.SetPosition(P(*ok[0])); placed[bot].append(ok[1]); marks.append(fp.GetReference() + it.GetText())
            else:
                it.SetLayer(pcbnew.B_Fab if bot else pcbnew.F_Fab); it.SetPosition(pad_.GetPosition())
fab_only, done = [], []
LEADER_W = 0.12
leaders = []
for d_ in list(b.GetDrawings()):                    # remove the leader lines of a previous run
    if d_.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and d_.GetClass() == 'PCB_SHAPE' and abs(pcbnew.ToMM(d_.GetWidth()) - LEADER_W) < 1e-6:
        b.Delete(d_)
# ---- reference labels: candidate positions around each part, then a global greedy assignment with repair.
# Hard rules: inside the board (0.3 mm), off every pad (+0.12), off the BODY of any other part (courtyard - 0.2),
# off the own body for small parts, off all silk outlines, 0.15 mm from other labels / polarity marks.
# Readability rule: the label must be nearer to its own part than to any other part (no ambiguous labels).
from shapely.prepared import prep
from shapely.strtree import STRtree
GAP_LAB = 0.15
import os
DEBUG = set(os.environ.get('SILK_DEBUG', '').split(',')) - {''}
DBG = {}
FP = {f.GetReference(): f for f in b.GetFootprints()}
for f in FP.values():                                # holes: no label
    if f.GetReference().startswith('H'):
        f.Reference().SetLayer(pcbnew.B_Fab if f.IsFlipped() else pcbnew.F_Fab)
body = {False: {}, True: {}}
for side in (False, True):
    for r, g in crt[side].items():
        sh = g.buffer(-0.2)
        body[side][r] = sh if not sh.is_empty else g
def own_shape(f):
    bot = f.IsFlipped(); r = f.GetReference()
    pp = unary_union([g for rr, g in pads[bot] if rr == r] or [Point(mm(f.GetPosition())).buffer(0.3)])
    return unary_union([pp, body[bot].get(r, pp)])
cand = {}
for side in (False, True):
    pad_all = prep(unary_union([g for r, g in pads[side]]))
    silk_all = prep(unary_union(list(silk[side].values())).buffer(0.03))
    marks_side = unary_union(placed[side]) if placed[side] else None
    for f in FP.values():
        if f.IsFlipped() != side or f.GetReference().startswith('H'):
            continue
        ref = f.GetReference(); t = f.Reference()
        t.SetLayer(SIDE[side]); t.SetMirrored(side); t.SetVisible(True); t.SetKeepUpright(False)
        t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(H_TXT), pcbnew.FromMM(H_TXT))); t.SetTextThickness(pcbnew.FromMM(T_TXT))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        own = own_shape(f)
        big = crt[side].get(ref, own).area > 20
        others = [g for r, g in body[side].items() if r != ref]
        others_p = prep(unary_union(others))                      # legality: other bodies
        others_c = unary_union([g for r, g in crt[side].items() if r != ref] +
                               [g for rr, g in pads[side] if rr != ref])          # readability: other outlines and pads
        own_c = unary_union([own, crt[side].get(ref, own)])
        own_body_p = prep(body[side][ref]) if (ref in body[side] and not big) else None
        minx, miny, maxx, maxy = own.bounds
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        lst = []
        for ang in (0, 90):
            t.SetTextAngleDegrees(ang - f.GetOrientationDegrees() if not side else -(ang) - f.GetOrientationDegrees())
            t.SetPosition(P(0, 0)); bb = t.GetBoundingBox()
            bw, bh = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
            L_, T_ = max(bw, bh) - 0.12, H_TXT + T_TXT + 0.04       # ink box: KiCad's text bbox includes line spacing
            w, h = (L_, T_) if ang == 0 else (T_, L_)
            tb = box(-w / 2, -h / 2, w / 2, h / 2)
            pts = set()
            for d in [0.05 + 0.1 * k for k in range(22)]:
                for k in range(-6, 7):
                    fx = cx + k / 6 * ((maxx - minx) / 2 + w / 2)
                    fy = cy + k / 6 * ((maxy - miny) / 2 + h / 2)
                    pts.add((round(fx, 3), round(maxy + d + h / 2, 3)))
                    pts.add((round(fx, 3), round(miny - d - h / 2, 3)))
                    pts.add((round(maxx + d + w / 2, 3), round(fy, 3)))
                    pts.add((round(minx - d - w / 2, 3), round(fy, 3)))
            if big:                                               # big parts: anywhere on the own body, off pads
                cb = crt[side].get(ref, own).intersection(OK_AREA)
                x0, y0, x1, y1 = cb.bounds
                for gx in [x0 + 0.25 * k for k in range(int((x1 - x0) / 0.25) + 1)]:
                    for gy in [y0 + 0.25 * k for k in range(int((y1 - y0) / 0.25) + 1)]:
                        if cb.contains(Point(gx, gy)):
                            pts.add((round(gx, 3), round(gy, 3)))
            for (px, py) in pts:
                g = translate(tb, px, py)
                why = ('edge' if not OK_AREA.contains(g) else 'pad' if pad_all.intersects(g) else 'silk' if silk_all.intersects(g)
                       else 'body' if others_p.intersects(g) else 'own' if (own_body_p is not None and own_body_p.intersects(g)) else '')
                if DEBUG and ref in DEBUG:
                    DBG.setdefault(ref, {}).setdefault(why or 'ok', 0); DBG[ref][why or 'ok'] += 1
                if why:
                    continue
                if marks_side is not None and g.distance(marks_side) < GAP_LAB:
                    continue
                on_body = big and crt[side].get(ref, own).contains(g)
                d_own = 0.0 if on_body else g.distance(own_c)
                d_oth = g.distance(others_c)
                amb = 0.0 if on_body else max(0.0, d_own - d_oth + 0.3)    # > 0: as close to another part as to its own
                lst.append((d_own + 0.15 * (ang == 90) + 10 * amb + 0.12 * math.hypot(px - cx, py - cy), ang, px, py, g, amb == 0, None))
        lst.sort(key=lambda x: x[0])
        # crowded parts (no unambiguous spot nearby): labels further away in free space, joined by a leader line
        if sum(1 for c in lst[:400] if c[5]) < 120:
            from shapely.ops import nearest_points
            silk_raw = unary_union(list(silk[side].values()))
            pads_u = unary_union([g for r, g in pads[side]])
            for ang in (0, 90):
                L_ = (max(pcbnew.ToMM(t.GetBoundingBox().GetWidth()), pcbnew.ToMM(t.GetBoundingBox().GetHeight())) - 0.12)
                w, h = (L_, H_TXT + T_TXT + 0.04) if ang == 0 else (H_TXT + T_TXT + 0.04, L_)
                tb = box(-w / 2, -h / 2, w / 2, h / 2)
                for ix in range(-20, 21):
                    for iy in range(-20, 21):
                        px, py = cx + 0.4 * ix, cy + 0.4 * iy
                        dist = math.hypot(px - cx, py - cy)
                        if dist < 1.2 or dist > 8.0:
                            continue
                        g = translate(tb, px, py)
                        if not OK_AREA.contains(g) or pad_all.intersects(g) or silk_all.intersects(g) or others_p.intersects(g):
                            continue
                        if g.distance(others_c) < 0.35:                 # free space: not next to another part
                            continue
                        if marks_side is not None and g.distance(marks_side) < GAP_LAB:
                            continue
                        a_, c_ = nearest_points(g, own_c)
                        ln = LineString([(a_.x, a_.y), (c_.x, c_.y)])
                        if ln.length < 0.3:
                            continue
                        lb = ln.buffer(0.06)
                        if others_p.intersects(lb) or lb.distance(pads_u.difference(own_c)) < 0.1 or lb.intersects(silk_raw.difference(own_c.buffer(0.05))):
                            continue
                        lst.append((3.0 + ln.length + 0.15 * (ang == 90), ang, px, py, unary_union([g, lb]), True, ln))
            lst.sort(key=lambda x: x[0])
        cand[ref] = lst[:400]
# assignment: simulated annealing over the candidate lists (cost = distance + ambiguity; overlaps forbidden)
import random
random.seed(1)
refs_ = [r for r in cand if cand[r]]
for r in refs_:
    cand[r] = [c + (0.0 if c[5] else 15.0,) for c in cand[r]]           # [7]: extra penalty for ambiguous spots
from shapely.geometry import box as _box
def bnd(r):
    x0, y0, x1, y1 = own_shape(FP[r]).bounds
    return _box(x0 - 4, y0 - 4, x1 + 4, y1 + 4)
NB = {r: [r2 for r2 in refs_ if r2 != r and FP[r2].IsFlipped() == FP[r].IsFlipped() and bnd(r).intersects(bnd(r2))] for r in refs_}
UNPLACED = 60.0
state = {r: None for r in refs_}
def ccost(r, k):
    return UNPLACED if k is None else cand[r][k][0] + cand[r][k][7]
def clash(r, k, r2, k2):
    return k is not None and k2 is not None and cand[r][k][4].distance(cand[r2][k2][4]) < GAP_LAB
def delta(r, k_new):
    old = state[r]; d = ccost(r, k_new) - ccost(r, old)
    for r2 in NB[r]:
        k2 = state[r2]
        d += 1000 * (clash(r, k_new, r2, k2) - clash(r, old, r2, k2))
    return d
# greedy start
for r in sorted(refs_, key=lambda r: len(cand[r])):
    for k in range(len(cand[r])):
        if all(not clash(r, k, r2, state[r2]) for r2 in NB[r]):
            state[r] = k; break
T = 3.0
for it in range(60000):
    r = random.choice(refs_)
    n = len(cand[r])
    k_new = None if random.random() < 0.02 else min(int(random.expovariate(1 / 25.0)), n - 1)
    d = delta(r, k_new)
    if d <= 0 or random.random() < math.exp(-d / T):
        state[r] = k_new
    T = max(0.02, T * 0.99993)
# final greedy fill for anything left unplaced
for r in refs_:
    if state[r] is None:
        for k in range(len(cand[r])):
            if all(not clash(r, k, r2, state[r2]) for r2 in NB[r]):
                state[r] = k; break
chosen = {r: cand[r][k][:7] for r, k in state.items() if k is not None and all(not clash(r, k, r2, state[r2]) for r2 in NB[r])}
# polish: slide each label (no leader) along its side toward the centre of its own part while it stays legal
LEG = {}
for side in (False, True):
    LEG[side] = (prep(unary_union([g for r, g in pads[side]])), prep(unary_union(list(silk[side].values())).buffer(0.03)))
for ref in list(chosen):
    cst, ang, px, py, g, clear, ln = chosen[ref]
    if ln is not None:
        continue
    f = FP[ref]; side = f.IsFlipped()
    own = own_shape(f); ox, oy = own.centroid.x, own.centroid.y
    others_p = prep(unary_union([g2 for r2, g2 in body[side].items() if r2 != ref]))
    big = crt[side].get(ref, own).area > 20
    obody = None if big else (prep(body[side][ref]) if ref in body[side] else None)
    # slide axis: along the label's long side
    ax = (1, 0) if ang == 0 else (0, 1)
    tgt = (ox - px) * ax[0] + (oy - py) * ax[1]
    best = 0.0
    for k in range(1, 41):
        sft = tgt * k / 40
        g2 = translate(g, sft * ax[0], sft * ax[1])
        if not OK_AREA.contains(g2) or LEG[side][0].intersects(g2) or LEG[side][1].intersects(g2) or others_p.intersects(g2):
            break
        if obody is not None and obody.intersects(g2):
            break
        if any(r2 != ref and FP[r2].IsFlipped() == side and g2.distance(c2[4]) < GAP_LAB for r2, c2 in chosen.items()):
            break
        if placed[side] and g2.distance(unary_union(placed[side])) < GAP_LAB:      # polarity marks
            break
        best = sft
    if best:
        chosen[ref] = (cst, ang, px + best * ax[0], py + best * ax[1], translate(g, best * ax[0], best * ax[1]), clear, ln)
for ref, f in FP.items():
    if ref.startswith('H'):
        continue
    t = f.Reference(); bot = f.IsFlipped()
    if ref in chosen:
        _, ang, px, py, g, clear, ln = chosen[ref]
        t.SetTextAngleDegrees(ang - f.GetOrientationDegrees() if not bot else -(ang) - f.GetOrientationDegrees())
        t.SetPosition(P(px, py)); done.append(ref + ('' if clear else '?'))
        if ln is not None:                                  # leader line on the board silkscreen
            seg = pcbnew.PCB_SHAPE(b); seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(P(*ln.coords[0])); seg.SetEnd(P(*ln.coords[1]))
            seg.SetLayer(SIDE[bot]); seg.SetWidth(pcbnew.FromMM(LEADER_W)); b.Add(seg); leaders.append(ref)
    else:
        t.SetLayer(pcbnew.B_Fab if bot else pcbnew.F_Fab); t.SetMirrored(bot)
        t.SetTextAngleDegrees(0); t.SetPosition(f.GetPosition())
        fab_only.append(ref)
# J1: drop the library silk segments that run into the edge band at the chamfer
j1 = b.FindFootprintByReference('J1'); nj = 0
for it in list(j1.GraphicalItems()):
    if it.GetLayer() == pcbnew.F_SilkS and it.GetClass() in ('FP_SHAPE', 'PCB_SHAPE', 'MGRAPHIC'):
        if not OK_AREA.contains(shape_poly(it)):
            j1.Remove(it); nj += 1
# passives (R/C/L) packed next to bigger parts: drop their own silk segments that overlap another part's silk
def silk_items(f):
    return [it for it in f.GraphicalItems() if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
            and it.GetClass() in ('FP_SHAPE', 'PCB_SHAPE', 'MGRAPHIC')]
nov = 0
removed_ = set()
fps_ = list(b.GetFootprints())
cnt_ = {}
for g_ in fps_:
    cnt_[str(g_.GetFPID().GetLibItemName())] = cnt_.get(str(g_.GetFPID().GetLibItemName()), 0) + 1
uniq = lambda g_: cnt_[str(g_.GetFPID().GetLibItemName())] == 1
for f in fps_:
    if not f.GetReference()[:1] in 'RCL' or not f.GetReference()[1:].isdigit():
        continue
    for g_ in fps_:
        if g_ is f or g_.IsFlipped() != f.IsFlipped():
            continue
        for it in silk_items(f):
            for it2 in silk_items(g_):
                if shape_poly(it).buffer(0.02).intersects(shape_poly(it2)):
                    # trim the footprint that is used only once on the board, so the shared footprint stays
                    # identical to its library copy (no "footprint does not match library" warning)
                    victim, vit = (g_, it2) if uniq(g_) or not uniq(f) else (f, it)
                    k_ = (victim.GetReference(), str(vit.GetStart()), str(vit.GetEnd()))
                    if k_ not in removed_:
                        removed_.add(k_); victim.Remove(vit); nov += 1
print('passive silk segments removed (overlap):', nov)
pcbnew.SaveBoard(BOARD, b)
print('J1 silk segments removed at the edge:', nj, '| polarity marks placed:', ' '.join(marks))
print('values updated:', nval)
print('labels on silkscreen: %d, Fab only (no free spot): %d %s' % (len(done), len(fab_only), ' '.join(sorted(fab_only))))
print('debug', DBG)
print('labels with a leader line:', ' '.join(leaders))
print('ambiguous (nearer to another part):', ' '.join(r for r in done if r.endswith('?')))
