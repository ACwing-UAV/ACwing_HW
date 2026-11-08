# Write the tracks / vias / zone fills of a modified KiCad 7 board back into the original KiCad 10 file (text level).
# usage: k10write.py orig_k10.kicad_pcb mod_k7.kicad_pcb out.kicad_pcb [--rmfp J7,J8] [--rmtext "-BAT+"] [--movefp J1] [--movetext "TO FC"]
import sys, re, uuid, pcbnew
src, k7, out = sys.argv[1:4]
opt = {}
a = sys.argv[4:]
for i in range(0, len(a), 2): opt[a[i]] = a[i + 1].split(',')
txt = open(src).read()
lines = txt.split('\n')
# top-level blocks
blocks = []   # (kind, text)
i = 0
head = []
assert lines[0] == '(kicad_pcb'
i = 1
while i < len(lines):
    l = lines[i]
    if l.startswith('\t(') :
        j = i
        if l.endswith(')') and l.count('(') == l.count(')'):
            blocks.append([l[2:].split()[0].rstrip(')'), l]); i += 1; continue
        while lines[j] != '\t)': j += 1
        blocks.append([l[2:].split()[0], '\n'.join(lines[i:j + 1])]); i = j + 1
    elif l == ')':
        break
    else:
        blocks.append(['raw', l]); i += 1
b = pcbnew.LoadBoard(k7)
f = lambda v: ('%.6f' % (v / 1e6)).rstrip('0').rstrip('.')
def uid(o): return o.m_Uuid.AsString()
tr = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
vias = {uid(t): t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA'}
def seg_text(t):
    s, e = t.GetStart(), t.GetEnd()
    lk = '\t\t(locked yes)\n' if t.IsLocked() else ''
    return (f'\t(segment\n\t\t(start {f(s.x)} {f(s.y)})\n\t\t(end {f(e.x)} {f(e.y)})\n\t\t(width {f(t.GetWidth())})\n'
            f'{lk}\t\t(layer "{t.GetLayerName()}")\n\t\t(net "{t.GetNetname()}")\n\t\t(uuid "{uid(t)}")\n\t)')
# zones fills from k7
zfill = {}
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    parts = []
    for L in z.GetLayerSet().Seq():
        ps = z.GetFilledPolysList(L)
        for k in range(ps.OutlineCount()):
            o = ps.Outline(k)
            pts = [f'(xy {f(o.CPoint(j).x)} {f(o.CPoint(j).y)})' for j in range(o.PointCount())]
            rows = ['\t\t\t\t' + ' '.join(pts[n:n + 4]) for n in range(0, len(pts), 4)]
            parts.append(f'\t\t(filled_polygon\n\t\t\t(layer "{b.GetLayerName(L)}")\n\t\t\t(pts\n' + '\n'.join(rows) + '\n\t\t\t)\n\t\t)')
            # holes are fractured by kicad into the outline (fill mode), nothing else to write
    zfill[uid(z)] = parts
outb = []
seg_done = False
stat = dict(seg_old=0, seg_new=len(tr), via_kept=0, via_moved=0, via_del=0, fp_del=0, fp_moved=0, txt=0, zones=0)
for kind, t in blocks:
    m = re.search(r'\n\t\t\(uuid "([^"]+)"\)', t)
    u = m.group(1) if m else None
    if kind == 'segment':
        stat['seg_old'] += 1
        if not seg_done:
            outb.append('\n'.join(seg_text(x) for x in tr)); seg_done = True
        continue
    if kind == 'via':
        v = vias.pop(u, None)
        if v is None: stat['via_del'] += 1; continue
        p = v.GetPosition()
        t2 = re.sub(r'\n\t\t\(at [-\d.]+ [-\d.]+\)', f'\n\t\t(at {f(p.x)} {f(p.y)})', t, count=1)
        stat['via_moved' if t2 != t else 'via_kept'] += 1
        outb.append(t2); continue
    if kind == 'footprint':
        r = re.search(r'\(property "Reference" "([^"]+)"', t).group(1)
        if r in opt.get('--rmfp', []): stat['fp_del'] += 1; continue
        if r in opt.get('--movefp', []):
            fp = b.FindFootprintByReference(r); p = fp.GetPosition()
            t = re.sub(r'\n\t\t\(at [-\d.]+ [-\d.]+( [-\d.]+)?\)', lambda mm: f'\n\t\t(at {f(p.x)} {f(p.y)}{mm.group(1) or ""})', t, count=1)
            stat['fp_moved'] += 1
        outb.append(t); continue
    if kind == 'gr_text':
        s = re.match(r'\t\(gr_text "((?:[^"\\]|\\.)*)"', t).group(1)
        if s in opt.get('--rmtext', []): stat['txt'] += 1; continue
        if s in opt.get('--movetext', []):
            d = [x for x in b.GetDrawings() if x.GetClass() == 'PCB_TEXT' and x.GetText() == s][0]; p = d.GetPosition()
            t = re.sub(r'\n\t\t\(at [-\d.]+ [-\d.]+', f'\n\t\t(at {f(p.x)} {f(p.y)}', t, count=1); stat['txt'] += 1
        outb.append(t); continue
    if kind == 'zone' and u in zfill:
        t = re.sub(r'\n\t\t\(filled_polygon\n.*?\n\t\t\)', '', t, flags=re.S)
        assert t.endswith('\n\t)')
        if zfill[u]: t = t[:-3] + '\n' + '\n'.join(zfill[u]) + '\n\t)'
        stat['zones'] += 1
        outb.append(t); continue
    outb.append(t)
assert not vias, 'new vias not handled: %d' % len(vias)
open(out, 'w').write('(kicad_pcb\n' + '\n'.join(outb) + '\n)\n')
print(stat)
