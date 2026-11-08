# Geometry model of a KiCad 7 board (converted from KiCad 10) for 45-degree re-routing and clearance checks.
import json, fnmatch, math, os, re
import pcbnew
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

NM = 1e6
def mm(v): return v / NM
def xy(p): return (p.x / NM, p.y / NM)

def poly_from_set(s):
    out = []
    for i in range(s.OutlineCount()):
        o = s.Outline(i)
        ext = [xy(o.CPoint(j)) for j in range(o.PointCount())]
        holes = []
        for k in range(s.HoleCount(i)):
            h = s.Hole(i, k); holes.append([xy(h.CPoint(j)) for j in range(h.PointCount())])
        if len(ext) >= 3: out.append(Polygon(ext, holes).buffer(0))
    return unary_union(out) if out else Polygon()

class Rules:
    def __init__(self, pro):
        d = json.load(open(pro))
        ns = d['net_settings']
        self.cls = {c['name']: c for c in ns['classes']}
        self.pat = [(p['pattern'], p['netclass']) for p in ns.get('netclass_patterns', [])]
        r = d['board']['design_settings']['rules']
        self.edge = r.get('min_copper_edge_clearance', 0.3)
        self.hole = r.get('min_hole_clearance', 0.25)
        self.minclr = r.get('min_clearance', 0.1)
        self.cache = {}
    def netclass(self, net):
        if net not in self.cache:
            c = 'Default'
            for p, nc in self.pat:
                if fnmatch.fnmatchcase(net, p): c = nc; break
            self.cache[net] = c
        return self.cache[net]
    def clr(self, a, b):
        return max(self.cls[self.netclass(a)]['clearance'] or 0, self.cls[self.netclass(b)]['clearance'] or 0, self.minclr)

class Board:
    def __init__(self, path, pro, margin=0.012):
        self.path = path
        self.b = pcbnew.LoadBoard(path)
        self.R = Rules(pro)
        self.margin = margin
        b = self.b
        self.cu = [l for l in range(pcbnew.PCB_LAYER_ID_COUNT) if pcbnew.IsCopperLayer(l) and b.IsLayerEnabled(l)]
        ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
        self.outline = poly_from_set(ps)
        self.edge_ring = self.outline.boundary
        # static items: pads, holes, rule areas, zone fills
        self.pads = []      # (layer, geom, net, pad)
        self.holes = []     # (geom, net)
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) and p.GetDrillSize().x > 0:
                    ds = p.GetDrillSize(); c = xy(p.GetPosition())
                    self.holes.append((Point(c).buffer(min(ds.x, ds.y) / NM / 2), p.GetNetname()))
                for L in self.cu:
                    if p.IsOnLayer(L) and p.FlashLayer(L):
                        s = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s, L, 0, pcbnew.FromMM(0.002))
                        self.pads.append((L, poly_from_set(s), p.GetNetname(), p))
        self.keep = {L: [] for L in self.cu}   # track keep-outs
        self.vkeep = []
        self.zfill = {L: [] for L in self.cu}  # (geom, net, name)
        for z in b.Zones():
            if z.GetIsRuleArea():
                g = poly_from_set(z.Outline())
                for L in self.cu:
                    if z.IsOnLayer(L) and z.GetDoNotAllowTracks(): self.keep[L].append(g)
                if z.GetDoNotAllowVias(): self.vkeep.append((g, [L for L in self.cu if z.IsOnLayer(L)]))
            else:
                for L in self.cu:
                    if z.IsOnLayer(L):
                        self.zfill[L].append((poly_from_set(z.GetFilledPolysList(L)), z.GetNetname(), z.GetZoneName()))
        self.rebuild()

    def rebuild(self):
        """dynamic copper (tracks, vias) + pads per layer, in an STRtree"""
        self.items = {L: [] for L in self.cu}   # (geom, net, kind, obj)
        for L, g, n, p in self.pads: self.items[L].append((g, n, 'pad', p))
        self.vias = []
        for t in self.b.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                c = Point(xy(t.GetPosition())); g = c.buffer(t.GetWidth() / NM / 2)
                self.vias.append((c, t))
                for L in self.cu:
                    if t.IsOnLayer(L): self.items[L].append((g, t.GetNetname(), 'via', t))
            else:
                g = LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(t.GetWidth() / NM / 2) if t.GetLength() > 0 else Point(xy(t.GetStart())).buffer(t.GetWidth() / NM / 2)
                self.items[t.GetLayer()].append((g, t.GetNetname(), 'trk', t))
        self.tree = {L: STRtree([i[0] for i in self.items[L]]) for L in self.cu}
        self.vholes = [(c.buffer(t.GetDrillValue() / NM / 2), t.GetNetname()) for c, t in self.vias]
        self.htree = STRtree([h[0] for h in self.holes + self.vholes]) if (self.holes or self.vholes) else None
        self.hlist = self.holes + self.vholes

    def violations(self, geom, net, L, ignore=()):
        """geom = copper shape of a new track (already buffered by w/2). returns list of reasons"""
        bad = []
        mg = self.margin
        if not self.outline.buffer(-(self.R.edge + mg)).contains(geom):
            bad.append('edge')
        for k in self.keep[L]:
            if k.intersects(geom): bad.append('keepout')
        cand = self.tree[L].query(geom.buffer(0.5))
        for i in cand:
            g, n, kind, obj = self.items[L][i]
            if n == net and n != '': continue
            if obj in ignore: continue
            c = self.R.clr(net, n)
            if g.distance(geom) < c + mg: bad.append((kind, n))
        if self.htree is not None:
            for i in self.htree.query(geom.buffer(0.6)):
                h, n = self.hlist[i]
                if n == net and n: continue
                if h.distance(geom) < self.R.hole + mg: bad.append(('hole', n))
        return bad

    def slack(self, geom, net, L):
        """min (distance - required clearance) against everything of other nets; -1 for a keep-out hit"""
        sl = self.outline.exterior.distance(geom) - self.R.edge if self.outline.contains(geom) else -1.0
        for h in self.outline.interiors:
            sl = min(sl, h.distance(geom) - self.R.edge)
        for k in self.keep[L]:
            if k.intersects(geom): return -1.0
        for i in self.tree[L].query(geom.buffer(0.6)):
            g, n, kind, obj = self.items[L][i]
            if n == net and n != '': continue
            sl = min(sl, g.distance(geom) - self.R.clr(net, n))
        if self.htree is not None:
            for i in self.htree.query(geom.buffer(0.6)):
                h, n = self.hlist[i]
                if n == net and n: continue
                sl = min(sl, h.distance(geom) - self.R.hole)
        return sl

    def pour_cost(self, geom, net, L):
        """length-ish measure of how much a track cuts into other-net zone fills"""
        c = 0.0
        for g, n, name in self.zfill[L]:
            if n != net and not g.is_empty:
                c += g.intersection(geom).area
        return c

def ang_ok(dx, dy, tol=1e-6):
    if abs(dx) < tol or abs(dy) < tol: return True
    return abs(abs(dx) - abs(dy)) < tol
