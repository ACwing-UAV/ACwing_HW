# Minimal KiCad 7 schematic writer (format 20230121) with embedded library symbols.
import copy, math, uuid
from sexp import parse, dump, find, find1, lib_symbol, Sym

NS = uuid.UUID('6f1c2d1e-3b7a-4c55-9a0e-1d2c3b4a5f60')
def uid(*k):
    return str(uuid.uuid5(NS, '/'.join(map(str, k))))

def S(x): return Sym(x)

def font(size=1.27):
    return [S('effects'), [S('font'), [S('size'), size, size]]]

def eff(hide=False, justify=None, size=1.27):
    e = [S('effects'), [S('font'), [S('size'), size, size]]]
    if justify: e.append([S('justify')] + [S(j) for j in justify.split()])
    if hide: e.append(S('hide'))
    return e

# ---------------------------------------------------------------- symbols
def rename_sym(node, old, new):
    node = copy.deepcopy(node)
    node[1] = new
    for sub in find(node, 'symbol'):
        if sub[1].startswith(old + '_'):
            sub[1] = new + sub[1][len(old):]
    return node

def flatten(lib, name):
    """Library symbol with 'extends' resolved, unit sub-symbols renamed to name."""
    s = lib_symbol(lib, name)
    ext = find1(s, 'extends')
    if not ext:
        return copy.deepcopy(s)
    parent = flatten(lib, ext[1])
    out = rename_sym(parent, parent[1], name)
    # replace properties with the child's
    out = [e for e in out if not (isinstance(e, list) and e and e[0] == 'property')]
    props = [copy.deepcopy(p) for p in find(s, 'property')]
    # insert props after the flags (before first sub-symbol)
    idx = next(i for i, e in enumerate(out) if isinstance(e, list) and e and e[0] == 'symbol')
    return out[:idx] + props + out[idx:]

def set_prop(sym, key, val):
    for p in find(sym, 'property'):
        if p[1] == key:
            p[2] = val
            return
    idx = next(i for i, e in enumerate(sym) if isinstance(e, list) and e and e[0] == 'symbol')
    sym.insert(idx, [S('property'), key, val, [S('at'), 0, 0, 0], eff(hide=True)])

def sym_pins(sym):
    """[(unit, pin dict)]"""
    out = []
    for sub in find(sym, 'symbol'):
        unit = int(sub[1].split('_')[-2])
        for e in sub:
            if isinstance(e, list) and e and e[0] == 'pin':
                at = find1(e, 'at')
                out.append(dict(unit=unit, type=str(e[1]), num=find1(e, 'number')[1],
                                name=find1(e, 'name')[1], x=float(at[1]), y=float(at[2]),
                                a=int(float(at[3])) if len(at) > 3 else 0,
                                hide=any(isinstance(z, Sym) and z == 'hide' for z in e)))
    return out

def is_power_sym(sym):
    return find1(sym, 'power') is not None

# ---------------------------------------------------------------- geometry
def xf(px, py, rot, mirror=False):
    """library point -> screen offset (schematic Y down), rotation CCW on screen."""
    sx, sy = (-px if mirror else px), -py
    r = math.radians(rot)
    c, s = round(math.cos(r)), round(math.sin(r))
    return (sx * c + sy * s, -sx * s + sy * c)

def vec(ang):
    a = math.radians(ang)
    return (round(math.cos(a)), -round(math.sin(a)))

def g(v):  # snap to 0.01 mm to kill float noise
    return round(v * 100) / 100.0

# ---------------------------------------------------------------- schematic
class Schematic:
    def __init__(self, project, paper='A3', title=None):
        self.project = project
        self.paper = paper
        self.root = uid(project, 'root')
        self.libs = {}       # lib_id -> symbol node (named lib_id)
        self.items = []
        self.parts = {}      # ref -> dict
        self.title = title or {}
        self.pwr_n = 0
        self.flg_n = 0
        self.expected = {}   # (ref, pin) -> net (for checks)
        self.nc = set()
        self.wires = []
        self.points = set()

    def add_lib(self, lib_id, node):
        if lib_id not in self.libs:
            n = copy.deepcopy(node)
            n[1] = lib_id
            self.libs[lib_id] = n
        return self.libs[lib_id]

    def lib(self, lib_id):
        if lib_id not in self.libs:
            lib, name = lib_id.split(':')
            self.add_lib(lib_id, flatten(lib, name))
        return self.libs[lib_id]

    # -- primitive items
    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            a, b = (g(a[0]), g(a[1])), (g(b[0]), g(b[1]))
            if a != b:
                self.wires.append((a, b))

    def _emit_wires(self):
        # KiCad only connects at segment ends: split every segment at junctions,
        # other segments' ends, labels, power pins and pin ends lying on it.
        pts = set(self.points)
        for a, b in self.wires:
            pts.add(a); pts.add(b)
        out = []
        for a, b in self.wires:
            cut = [a, b]
            for p in pts:
                if p in (a, b):
                    continue
                if a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1]):
                    cut.append(p)
                elif a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0]):
                    cut.append(p)
            cut.sort(key=lambda q: (q[0] - a[0]) ** 2 + (q[1] - a[1]) ** 2)
            out += list(zip(cut, cut[1:]))
        for a, b in out:
            self.items.append([S('wire'), [S('pts'), [S('xy'), a[0], a[1]], [S('xy'), b[0], b[1]]],
                               [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
                               [S('uuid'), uid('w', a, b)]])

    def junction(self, p):
        self.points.add((g(p[0]), g(p[1])))
        self.items.append([S('junction'), [S('at'), g(p[0]), g(p[1])], [S('diameter'), 0],
                           [S('color'), 0, 0, 0, 0], [S('uuid'), uid('j', p)]])

    def label(self, net, p, ang):
        self.points.add((g(p[0]), g(p[1])))
        just = 'left bottom' if ang in (0, 90) else 'right bottom'
        self.items.append([S('label'), net, [S('at'), g(p[0]), g(p[1]), ang], [S('fields_autoplaced')],
                           eff(justify=just), [S('uuid'), uid('l', net, p)]])

    def noconn(self, p):
        self.items.append([S('no_connect'), [S('at'), g(p[0]), g(p[1])], [S('uuid'), uid('nc', p)]])

    def text(self, s, p, size=1.27, bold=False):
        e = [S('effects'), [S('font'), [S('size'), size, size]] + ([S('bold')] if bold else []),
             [S('justify'), S('left'), S('top')]]
        self.items.append([S('text'), s, [S('at'), g(p[0]), g(p[1]), 0], e, [S('uuid'), uid('t', s[:40], p)]])

    def rect(self, a, b):
        self.items.append([S('rectangle'), [S('start'), g(a[0]), g(a[1])], [S('end'), g(b[0]), g(b[1])],
                           [S('stroke'), [S('width'), 0], [S('type'), S('dash')]], [S('fill'), [S('type'), S('none')]],
                           [S('uuid'), uid('r', a, b)]])

    # -- symbol instances
    def _instance(self, lib_id, ref, value, x, y, rot, unit=1, fp='', fields=None, dnp=False,
                  in_bom=True, on_board=True, field_pos=None, mirror=False):
        sym = self.lib(lib_id)
        key = (ref, unit)
        node = [S('symbol'), [S('lib_id'), lib_id], [S('at'), g(x), g(y), rot]]
        if mirror:
            node.append([S('mirror'), S('y')])
        node += [[S('unit'), unit],
                [S('in_bom'), S('yes' if in_bom else 'no')], [S('on_board'), S('yes' if on_board else 'no')],
                [S('dnp'), S('yes' if dnp else 'no')], [S('uuid'), uid('sym', ref, unit)]]
        lp = {p[1]: p for p in find(sym, 'property')}
        def prop(k, v, pos=None, hide=False, just=None):
            if pos is None:
                if k in lp:
                    at = lp[k][3]
                    ox, oy = xf(float(at[1]), float(at[2]), rot, mirror)
                    pos = (x + ox, y + oy)
                else:
                    pos = (x, y)
            fa = 90 if rot in (90, 270) else 0
            node.append([S('property'), k, v, [S('at'), g(pos[0]), g(pos[1]), fa], eff(hide=hide, justify=just)])
        power = is_power_sym(sym)
        fpos = dict(field_pos or {})
        if rot == 90 and fpos.get('just') in ('left', 'right'):   # KiCad mirrors justification here
            fpos['just'] = 'right' if fpos['just'] == 'left' else 'left'
        prop('Reference', ref, fpos.get('Reference'), hide=power or ref.startswith('#'), just=fpos.get('just'))
        prop('Value', value, fpos.get('Value'), just=fpos.get('just'))
        if not fp and 'Footprint' in lp:
            fp = lp['Footprint'][2]
        prop('Footprint', fp, hide=True)
        prop('Datasheet', (lp['Datasheet'][2] if 'Datasheet' in lp else '~') or '~', hide=True)
        for k, v in (fields or {}).items():
            prop(k, v, hide=True)
        pins = [p for p in sym_pins(sym) if p['unit'] in (0, unit)]
        for p in pins:
            node.append([S('pin'), p['num'], [S('uuid'), uid('pin', ref, unit, p['num'])]])
        node.append([S('instances'), [S('project'), self.project,
                                      [S('path'), '/' + self.root, [S('reference'), ref], [S('unit'), unit]]]])
        self.items.append(node)
        return sym, pins

    def pin_end(self, ref, num, unit=None):
        part = self.parts[ref]
        for (u, p) in part['pins']:
            if p['num'] == num and (unit is None or u == unit):
                mir = part.get('mirror', False)
                ox, oy = xf(p['x'], p['y'], part['rot'][u], mir)
                X, Y = part['pos'][u]
                a = (180 - p['a']) % 360 if mir else p['a']
                out = (a + 180 + part['rot'][u]) % 360
                return (g(X + ox), g(Y + oy)), out, p
        raise KeyError((ref, num))

    def power(self, net, p, outward, flag=False):
        """Place power symbol for net at point p with its body pointing 'outward'."""
        lib_id = POWER_LIB[net]
        down = net == 'GND'
        rot = (outward + 90) % 360 if down else (outward - 90) % 360
        self.pwr_n += 1
        self.points.add((g(p[0]), g(p[1])))
        fpos = None
        if rot in (90, 270) and not down:      # sideways rail: horizontal text beside the arrow
            left = rot == 90
            fpos = {'Value': (p[0] - 3.3 if left else p[0] + 3.3, p[1]), 'just': 'right' if left else 'left'}
        elif down and rot in (90, 270):
            left = rot == 270
            fpos = {'Value': (p[0] - 3.6 if left else p[0] + 3.6, p[1]), 'just': 'right' if left else 'left'}
        self._instance(lib_id, '#PWR%03d' % self.pwr_n, net, p[0], p[1], rot, field_pos=fpos)

    def tie(self, ref, nums, net, offset=2.54, unit=None, sym_at=None):
        """Join several pins (assigned ('W', net)) with a bar and a single power symbol."""
        ends = [self.pin_end(ref, n, unit) for n in nums]
        out = ends[0][1]
        d = vec(out)
        qs = []
        for (p, o, _) in ends:
            q = (g(p[0] + d[0] * offset), g(p[1] + d[1] * offset))
            self.wire(p, q)
            qs.append(q)
        qs.sort()
        self.wire(qs[0], qs[-1])
        for q in qs[1:-1]:
            self.junction(q)
        m = qs[len(qs) // 2] if sym_at is None else qs[sym_at]
        if net in POWER_LIB:
            self.power(net, m, out)
        else:
            self.label(net, m, out)

    def pwr_flag(self, net, p):
        self.flg_n += 1
        rot = 0 if net == 'GND' else 180
        self._instance('power:PWR_FLAG', '#FLG%02d' % self.flg_n, 'PWR_FLAG', p[0], p[1], rot)
        self.power(net, p, 270 if net == 'GND' else 90)

    def part(self, ref, lib_id, value, x, y, rot=0, conns=None, fp='', fields=None, dnp=False,
             unit=1, stub=2.54, field_pos=None, in_bom=True, on_board=True, mirror=False):
        if not fp:
            fp = next((p[2] for p in find(self.lib(lib_id), 'property') if p[1] == 'Footprint'), '')
        sym, pins = self._instance(lib_id, ref, value, x, y, rot, unit, fp, fields, dnp,
                                   in_bom=in_bom, on_board=on_board, field_pos=field_pos, mirror=mirror)
        P = self.parts.setdefault(ref, dict(lib_id=lib_id, value=value, fp=fp, pins=[], pos={}, rot={},
                                            fields=fields or {}, dnp=dnp, mirror=mirror))
        P['pos'][unit] = (x, y)
        P['rot'][unit] = rot
        P['pins'] += [(unit, p) for p in pins]
        conns = conns or {}
        seen_pos = {}
        for p in pins:
            num = p['num']
            (pt, out, _) = self.pin_end(ref, num, unit)
            self.points.add(pt)
            if num in conns:
                net = conns[num]
                if net is None:
                    self.noconn(pt)
                    self.nc.add((ref, num))
                    continue
                wired = False
                if isinstance(net, tuple):      # ('W', net): connected by explicit wires
                    wired, net = True, net[1]
                self.expected[(ref, num)] = net
                seen_pos[pt] = net
                if wired:
                    continue
                if net in POWER_LIB:
                    self.power(net, pt, out)
                else:
                    d = vec(out)
                    q = (pt[0] + d[0] * stub, pt[1] + d[1] * stub)
                    self.wire(pt, q)
                    self.label(net, q, out if out in (0, 180) else 0)
            else:
                if p['type'] == 'no_connect':
                    continue
                if pt in seen_pos:              # stacked pin at the same spot
                    self.expected[(ref, num)] = seen_pos[pt]
                    continue
                if p['hide']:
                    # hidden pin stacked on a visible one: resolved after all pins
                    P.setdefault('stacked', []).append((num, pt))
                    continue
                raise ValueError('%s pin %s (%s) not assigned' % (ref, num, p['name']))
        for num, pt in P.pop('stacked', []):
            if pt in seen_pos:
                self.expected[(ref, num)] = seen_pos[pt]
            else:
                raise ValueError('%s hidden pin %s floating' % (ref, num))
        return P

    def write(self, path):
        tb = [S('title_block')]
        for k in ('title', 'date', 'rev', 'company'):
            if k in self.title:
                tb.append([S(k), self.title[k]])
        for i, c in enumerate(self.title.get('comments', []), 1):
            tb.append([S('comment'), i, c])
        doc = [S('kicad_sch'), [S('version'), 20230121], [S('generator'), S('eeschema')],
               [S('uuid'), self.root], [S('paper'), self.paper], tb,
               [S('lib_symbols')] + list(self.libs.values())]
        self._emit_wires()
        doc += self.items
        doc.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
        with open(path, 'w') as f:
            f.write(dump(doc) + '\n')

POWER_LIB = {}
