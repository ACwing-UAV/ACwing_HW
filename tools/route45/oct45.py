# Make every track segment of a (KiCad 7) board a multiple of 45 degrees, keeping all end points, pads and vias.
# usage: oct45.py board.kicad_pcb board.kicad_pro [--only NET,...]
import sys, math, heapq, collections
import numpy as np
from PIL import Image, ImageDraw
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from geo import Board, ang_ok, NM, xy
from shapely.geometry import LineString, Point, box

path, pro = sys.argv[1], sys.argv[2]
B = Board(path, pro)
b = B.b
TOL = 2  # nm

def is45(s, e):
    dx, dy = e[0] - s[0], e[1] - s[1]
    return dx == 0 or dy == 0 or abs(dx) == abs(dy)

def tracks():
    return [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']

def key(p): return (int(p[0]), int(p[1]))

# ---------------------------------------------------------------- 1. split segments at interior T points / vias
def proj_split(s, e, p):
    """split point on segment s-e for an attached point p (exact on the line for 45-degree segments)"""
    dx, dy = e[0] - s[0], e[1] - s[1]
    L2 = dx * dx + dy * dy
    u = ((p[0] - s[0]) * dx + (p[1] - s[1]) * dy) / L2
    if dx == 0: return (s[0], int(round(s[1] + u * dy)))
    if dy == 0: return (int(round(s[0] + u * dx)), s[1])
    if abs(dx) == abs(dy):
        k = int(round(u * abs(dx))); return (s[0] + k * (1 if dx > 0 else -1), s[1] + k * (1 if dy > 0 else -1))
    return (int(round(s[0] + u * dx)), int(round(s[1] + u * dy)))

def split_T():
    n = 0
    tr = tracks()
    by = collections.defaultdict(list)
    for t in tr: by[(t.GetNetname(), t.GetLayer())].append(t)
    vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    padsby = collections.defaultdict(list)
    for Lp, g, nn, pad in B.pads: padsby[(nn, Lp)].append((g, key(pad.GetPosition())))
    for (net, L), ts in by.items():
        att = []   # (point, radius)
        for t in ts:
            att.append((key(t.GetStart()), t.GetWidth() / 2)); att.append((key(t.GetEnd()), t.GetWidth() / 2))
        for v in vias:
            if v.GetNetname() == net and v.IsOnLayer(L): att.append((key(v.GetPosition()), v.GetWidth() / 2))
        for t in ts:
            s, e = key(t.GetStart()), key(t.GetEnd())
            dx, dy = e[0] - s[0], e[1] - s[1]
            L2 = dx * dx + dy * dy
            if L2 == 0: continue
            Ls = math.sqrt(L2)
            inner = []
            for p, rp in att:
                if p == s or p == e: continue
                u = ((p[0] - s[0]) * dx + (p[1] - s[1]) * dy) / L2
                if u * Ls < 1000 or (1 - u) * Ls < 1000: continue     # within 1 um of an end
                if 0 < u < 1:
                    q = (s[0] + u * dx, s[1] + u * dy)
                    if math.hypot(q[0] - p[0], q[1] - p[1]) < t.GetWidth() / 2 + rp - 1000:
                        inner.append((u, proj_split(s, e, p)))
            seg = LineString([(s[0] / NM, s[1] / NM), (e[0] / NM, e[1] / NM)])
            for g, pc in padsby[(net, L)]:
                if g.intersects(seg) and not g.contains(Point(s[0] / NM, s[1] / NM)) and not g.contains(Point(e[0] / NM, e[1] / NM)):
                    u = ((pc[0] - s[0]) * dx + (pc[1] - s[1]) * dy) / L2
                    if 0 < u < 1: inner.append((u, proj_split(s, e, pc)))
            if inner:
                inner.sort()
                chain = [s]
                for _, p in inner:
                    if p != chain[-1]: chain.append(p)
                if chain[-1] != e: chain.append(e)
                for a, c in zip(chain, chain[1:]):
                    add_track(a, c, t.GetWidth(), L, net)
                b.Remove(t); KEEP.append(t); n += 1
    return n

NEW = []
def add_track(s, e, w, L, net):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(int(s[0]), int(s[1]))); t.SetEnd(pcbnew.VECTOR2I(int(e[0]), int(e[1])))
    t.SetWidth(w); t.SetLayer(L); t.SetNet(b.FindNet(net)); b.Add(t); NEW.append(t)
    return t

# ---------------------------------------------------------------- 2. chains
def anchored(p, net, L):
    P = Point(p[0] / NM, p[1] / NM)
    for Lp, g, n, pad in B.pads:
        if Lp == L and n == net and g.buffer(1e-4).contains(P): return True
    for c, v in B.vias:
        if v.GetNetname() == net and v.IsOnLayer(L) and c.distance(P) < v.GetWidth() / NM / 2: return True
    return False

def chains():
    tr = tracks()
    by = collections.defaultdict(list)
    for t in tr:
        if t.GetLength() == 0: continue
        by[(t.GetNetname(), t.GetLayer())].append(t)
    out = []
    for (net, L), ts in by.items():
        adj = collections.defaultdict(list)
        for t in ts:
            adj[key(t.GetStart())].append(t); adj[key(t.GetEnd())].append(t)
        def junction(p):
            a = adj[p]
            if len(a) != 2: return True
            if a[0].GetWidth() != a[1].GetWidth(): return True
            return anchored(p, net, L)
        J = {p: junction(p) for p in adj}
        used = set()
        for t in ts:
            if id(t) in used: continue
            # grow both ways
            seq = [t]; used.add(id(t))
            ends = [key(t.GetStart()), key(t.GetEnd())]
            for side in (0, 1):
                p = ends[side]
                cur = t
                while not J[p]:
                    nxt = [x for x in adj[p] if x is not cur][0]
                    if id(nxt) in used: break
                    used.add(id(nxt))
                    q = key(nxt.GetEnd()) if key(nxt.GetStart()) == p else key(nxt.GetStart())
                    if side == 0: seq.insert(0, nxt)
                    else: seq.append(nxt)
                    cur, p = nxt, q
                ends[side] = p
            # ordered point list
            pts = [ends[0]]
            for s in seq:
                a, c = key(s.GetStart()), key(s.GetEnd())
                pts.append(c if a == pts[-1] else a)
            if pts[-1] != ends[1]:
                continue
            if any(not is45(key(s.GetStart()), key(s.GetEnd())) for s in seq):
                out.append((net, L, seq[0].GetWidth(), seq, pts))
    return out

# ---------------------------------------------------------------- 3. candidates
def doglegs(a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]
    if dx == 0 or dy == 0 or abs(dx) == abs(dy): return [[a, c]]
    m = min(abs(dx), abs(dy)); sx = 1 if dx > 0 else -1; sy = 1 if dy > 0 else -1
    diag = (sx * m, sy * m)
    st = (dx - diag[0], dy - diag[1])
    out = [[a, (a[0] + diag[0], a[1] + diag[1]), c], [a, (a[0] + st[0], a[1] + st[1]), c]]
    h = (st[0] // 2, st[1] // 2)
    out.append([a, (a[0] + h[0], a[1] + h[1]), (a[0] + h[0] + diag[0], a[1] + h[1] + diag[1]), c])
    hd = (diag[0] // 2, diag[1] // 2)
    out.append([a, (a[0] + hd[0], a[1] + hd[1]), (a[0] + hd[0] + st[0], a[1] + hd[1] + st[1]), c])
    for f in (0.25, 0.75):
        h = (int(st[0] * f), int(st[1] * f))
        out.append([a, (a[0] + h[0], a[1] + h[1]), (a[0] + h[0] + diag[0], a[1] + h[1] + diag[1]), c])
    return out

def clean(poly):
    q = [poly[0]]
    for p in poly[1:]:
        if p != q[-1]: q.append(p)
    # merge collinear
    r = [q[0]]
    for k in range(1, len(q) - 1):
        a, p, c = r[-1], q[k], q[k + 1]
        if (p[0] - a[0]) * (c[1] - p[1]) - (p[1] - a[1]) * (c[0] - p[0]) == 0 and \
           (p[0] - a[0]) * (c[0] - p[0]) + (p[1] - a[1]) * (c[1] - p[1]) > 0:
            continue
        r.append(p)
    r.append(q[-1])
    return r

def geom(poly, w):
    pts = [(p[0] / NM, p[1] / NM) for p in poly]
    return LineString(pts).buffer(w / NM / 2) if len(pts) > 1 else Point(pts[0]).buffer(w / NM / 2)

def plen(poly): return sum(math.hypot(c[0] - a[0], c[1] - a[1]) for a, c in zip(poly, poly[1:])) / NM

THR = [0.012]
def thr(orig):
    return min(B.margin, max(orig - 0.0002, 0.0005))

def score(poly, w, net, L):
    g = geom(poly, w)
    if B.slack(g, net, L) < THR[0]: return None
    return plen(poly) + 30 * B.pour_cost(g, net, L) + 0.05 * len(poly)

def best(cands, w, net, L):
    res = []
    for c in cands:
        c = clean(c)
        if not all(is45(a, e) for a, e in zip(c, c[1:])): continue
        s = score(c, w, net, L)
        if s is not None: res.append((s, c))
    return min(res)[1] if res else None

# ---------------------------------------------------------------- 4. octilinear A* on one layer
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
def astar(a, c, w, net, L, res_mm=0.025, pad=2.0):
    r = int(res_mm * NM)
    x0 = min(a[0], c[0]) - int(pad * NM); x1 = max(a[0], c[0]) + int(pad * NM)
    y0 = min(a[1], c[1]) - int(pad * NM); y1 = max(a[1], c[1]) + int(pad * NM)
    i0 = -((a[0] - x0) // r); i1 = (x1 - a[0]) // r
    j0 = -((a[1] - y0) // r); j1 = (y1 - a[1]) // r
    NX, NY = i1 - i0 + 1, j1 - j0 + 1
    def cell_xy(i, j): return ((a[0] + i * r) / NM, (a[1] + j * r) / NM)
    def to_px(x, y): return ((x * NM - a[0]) / r - i0, (y * NM - a[1]) / r - j0)
    img = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(img)
    win = box(x0 / NM, y0 / NM, x1 / NM, y1 / NM)
    extra = w / NM / 2 + B.margin + res_mm * 0.75
    def draw(g):
        for pg in (g.geoms if hasattr(g, 'geoms') else [g]):
            if pg.is_empty or pg.geom_type != 'Polygon': continue
            d.polygon([to_px(*q) for q in pg.exterior.coords], fill=1)
            for h in pg.interiors: d.polygon([to_px(*q) for q in h.coords], fill=0)
    for i in B.tree[L].query(win):
        g, n, kind, obj = B.items[L][i]
        if n == net and n: continue
        draw(g.buffer(extra + B.R.clr(net, n)))
    for k in B.keep[L]: draw(k.buffer(extra).intersection(win))
    for h, n in B.hlist:
        if n == net and n: continue
        if h.intersects(win.buffer(1)): draw(h.buffer(extra + B.R.hole))
    draw(win.difference(B.outline.buffer(-(B.R.edge + extra - w / NM / 2 + w / NM / 2))))
    blocked = np.array(img, dtype=bool).T
    pimg = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(pimg)
    for g, n, name in B.zfill[L]:
        if n != net and not g.is_empty: draw(g.intersection(win))
    pour = np.array(pimg, dtype=bool).T
    si, sj = -i0, -j0
    gi, gj = int(round((c[0] - a[0]) / r)) - i0, int(round((c[1] - a[1]) / r)) - j0
    blocked[si, sj] = False; blocked[gi, gj] = False
    # free the cells close to the start / goal (they sit in own pads)
    INF = 1e18
    start = (si, sj, -1)
    dist = {start: 0}; prev = {}
    pq = [(0, start)]
    def h(i, j):
        dx, dy = abs(i - gi), abs(j - gj)
        return (max(dx, dy) - min(dx, dy)) + 1.41421 * min(dx, dy)
    n = 0
    while pq:
        f, s = heapq.heappop(pq)
        i, j, dr = s
        g0 = dist[s]
        if f - h(i, j) > g0 + 1e-9: continue
        if (i, j) == (gi, gj):
            pts = [(i, j)]
            while s in prev: s = prev[s]; pts.append((s[0], s[1]))
            pts = pts[::-1]
            poly = [(a[0] + (p[0] + i0) * r, a[1] + (p[1] + j0) * r) for p in pts]
            poly[0] = a
            return poly
        n += 1
        if n > 1_500_000: return None
        for k, (di, dj) in enumerate(DIRS):
            ni, nj = i + di, j + dj
            if not (0 <= ni < NX and 0 <= nj < NY) or blocked[ni, nj]: continue
            cost = (1.41421 if di and dj else 1.0)
            if dr >= 0 and dr != k:
                t = min((k - dr) % 8, (dr - k) % 8)
                if t > 2: continue          # no acute turns
                cost += 0.6 * t
            if pour[ni, nj]: cost += 1.5
            ns = (ni, nj, k); ng = g0 + cost
            if ng < dist.get(ns, INF):
                dist[ns] = ng; prev[ns] = s; heapq.heappush(pq, (ng + h(ni, nj), ns))
    return None

def finish_astar(poly, c, w, net, L):
    poly = clean(poly)
    if len(poly) >= 2:
        # replace the last vertex (grid cell) by the exact goal through a dogleg
        head = poly[:-1]
        for tail in doglegs(head[-1], c):
            cand = clean(head + tail[1:])
            if all(is45(x, y) for x, y in zip(cand, cand[1:])) and score(cand, w, net, L) is not None:
                return cand
        if len(head) >= 2:
            head2 = head[:-1]
            for tail in doglegs(head2[-1], c):
                cand = clean(head2 + tail[1:])
                if all(is45(x, y) for x, y in zip(cand, cand[1:])) and score(cand, w, net, L) is not None:
                    return cand
    return None

KEEP = []
def preclean():
    tr = tracks()
    by = collections.defaultdict(list)
    for t in tr: by[(t.GetNetname(), t.GetLayer())].append(t)
    vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    nsnap = ndup = 0
    dele = []
    for (net, L), ts in by.items():
        anchors = [key(v.GetPosition()) for v in vias if v.GetNetname() == net and v.IsOnLayer(L)]
        anchors += [key(pad.GetPosition()) for Lp, g, nn, pad in B.pads if nn == net and Lp == L]
        reps = list(anchors)
        def rep(p):
            for r in reps:
                if r != p and abs(r[0] - p[0]) <= 5000 and abs(r[1] - p[1]) <= 5000 and math.hypot(r[0]-p[0], r[1]-p[1]) <= 5000:
                    return r
            reps.append(p); return p
        for t in ts:
            for get, setf in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
                p = key(get()); r = rep(p)
                if r != p: setf(pcbnew.VECTOR2I(*r)); nsnap += 1
        seen = {}
        for t in ts:
            s_, e_ = key(t.GetStart()), key(t.GetEnd())
            if s_ == e_: dele.append(t); ndup += 1; continue
            k = (min(s_, e_), max(s_, e_))
            if k in seen:
                o = seen[k]
                if o.GetWidth() >= t.GetWidth(): dele.append(t)
                else: dele.append(o); seen[k] = t
                ndup += 1
            else: seen[k] = t
    for t in dele: b.Remove(t)
    KEEP.extend(dele)
    return nsnap, ndup

# ---------------------------------------------------------------- main
only = None
if '--only' in sys.argv: only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
print('preclean snap/dup', preclean())
ns = split_T()
B.rebuild()
CH = chains()
print('split', ns, 'chains to fix', len(CH))
stats = collections.Counter(); fails = []
def endcount(p, net, L):
    n = 0
    for t in tracks():
        if t.GetNetname() == net and t.GetLayer() == L and (key(t.GetStart()) == p or key(t.GetEnd()) == p): n += 1
    return n

def flex_pad(p, net, L):
    """pad polygon if p is a free track end inside a pad (no via, one track), else None"""
    P = Point(p[0] / NM, p[1] / NM)
    for c, v in B.vias:
        if v.GetNetname() == net and v.IsOnLayer(L) and c.distance(P) < v.GetWidth() / NM / 2: return None
    if endcount(p, net, L) != 1: return None
    for Lp, g, n, pad in B.pads:
        if Lp == L and n == net and g.contains(P): return g
    return None

def variants(p, toward, g, w):
    """moved copies of end p (inside pad g) so that p -> toward is octilinear"""
    out = []
    dx, dy = toward[0] - p[0], toward[1] - p[1]
    cands = [(p[0], toward[1]), (toward[0], p[1]),
             (p[0], toward[1] - (1 if dy > 0 else -1) * abs(dx)), (toward[0] - (1 if dx > 0 else -1) * abs(dy), p[1])]
    inner = g.buffer(-0.01)
    for q in cands:
        q = (int(q[0]), int(q[1]))
        if q != p and inner.contains(Point(q[0] / NM, q[1] / NM)) and is45(q, toward):
            out.append(q)
    out.sort(key=lambda q: math.hypot(q[0] - p[0], q[1] - p[1]))
    return out[:2]

for net, L, w, seq, pts in CH:
    if only and net not in only: continue
    sol = None
    orig = B.slack(geom(pts, w), net, L)
    THR[0] = thr(orig)
    ga, gb = flex_pad(pts[0], net, L), flex_pad(pts[-1], net, L)
    # 0. single straight line by sliding a free end inside its pad
    if len(pts) >= 2:
        cl = []
        if ga is not None: cl += [[q] + pts[1:] for q in variants(pts[0], pts[1], ga, w)]
        if gb is not None: cl += [pts[:-1] + [q] for q in variants(pts[-1], pts[-2], gb, w)]
        cl = [c for c in cl if all(is45(x, y) for x, y in zip(c, c[1:]))]
        if cl:
            sol = best(cl, w, net, L)
            if sol: stats['slide'] += 1
    if sol is None and ga is not None and gb is None and len(pts) >= 2:
        for q in variants(pts[0], pts[-1], ga, w):
            sol = best([[q, pts[-1]]], w, net, L)
            if sol: stats['slide'] += 1; break
    if sol is None and gb is not None and len(pts) >= 2:
        for q in variants(pts[-1], pts[0], gb, w):
            sol = best([[pts[0], q]], w, net, L)
            if sol: stats['slide'] += 1; break
    if sol is None and len(pts) > 2:
        sol = best(doglegs(pts[0], pts[-1]), w, net, L)
        if sol: stats['chain'] += 1
    if sol is None:
        newpts = [pts[0]]; ok = True
        for a, c in zip(pts, pts[1:]):
            if is45(a, c): newpts.append(c); continue
            THR[0] = thr(B.slack(geom([a, c], w), net, L))
            part = best(doglegs(a, c), w, net, L)
            if part is None:
                for rr in (0.025, 0.0125):
                    p = astar(a, c, w, net, L, rr)
                    if p: part = finish_astar(p, c, w, net, L)
                    if part: stats['astar'] += 1; break
            if part is None:
                ok = False; fails.append((net, b.GetLayerName(L), a[0] / NM, a[1] / NM, c[0] / NM, c[1] / NM)); break
            newpts += part[1:]
            stats['seg'] += 1
        if not ok: continue
        sol = clean(newpts)
    for s_ in seq: b.Remove(s_); KEEP.append(s_)
    for a, c in zip(sol, sol[1:]): add_track(a, c, w, L, net)
    B.rebuild()
micro = sum(1 for t in tracks() if 0 < t.GetLength() < 0.02 * NM)
print('micro segments (< 20 um)', micro)
print(dict(stats), 'FAILED', len(fails))
for f in fails: print('  FAIL', f)
left = sum(1 for t in tracks() if t.GetLength() > 0 and not is45(key(t.GetStart()), key(t.GetEnd())))
print('non-45 segments left', left)
pcbnew.SaveBoard(path, b)
