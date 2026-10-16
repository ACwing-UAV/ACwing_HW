# removes the track stubs / vias that KiCad's own DRC reports as dangling, plus duplicated vias; refills zones
import sys, re, pcbnew
B = sys.argv[1]
for rnd in range(4):
    b = pcbnew.LoadBoard(B)
    pcbnew.WriteDRCReport(b, '/tmp/claude-0/cl.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True)
    t = open('/tmp/claude-0/cl.rpt').read()
    targets = []
    for bl in re.split(r'\n(?=\[)', t):
        if bl.startswith(('[track_dangling]', '[via_dangling]')):
            m = re.search(r'@\(([-\d.]+) mm, ([-\d.]+) mm\): (Track|Via) \[([^\]]*)\][^\n]*?(?:length ([\d.]+) mm)?\s*$', next((l for l in bl.splitlines() if '@(' in l), ''))
            if m:
                targets.append((float(m.group(1)), float(m.group(2)), m.group(3), m.group(4), float(m.group(5)) if m.group(5) else None))
    if not targets:
        break
    n = 0
    for (x, y, kind, net, ln) in targets:
        p = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
        for tr in [tr for tr in b.GetTracks()]:
            if tr.GetNetname() != net:
                continue
            if kind == 'Via' and tr.GetClass() == 'PCB_VIA' and (tr.GetPosition() - p).EuclideanNorm() < 2000:
                b.Delete(tr); n += 1; break
            # the marker sits on one end of the stub, possibly a junction shared with good tracks:
            # match the reported length too
            if kind == 'Track' and tr.GetClass() == 'PCB_TRACK' and \
                    min((tr.GetStart() - p).EuclideanNorm(), (tr.GetEnd() - p).EuclideanNorm()) < 2000 and \
                    (ln is None or abs(pcbnew.ToMM(tr.GetLength()) - ln) < 0.002):
                b.Delete(tr); n += 1; break
    seen = set()
    for tr in [tr for tr in b.GetTracks()]:
        if tr.GetClass() == 'PCB_VIA':
            k = (tr.GetPosition().x // 2000, tr.GetPosition().y // 2000, tr.GetNetname())
            if k in seen:
                b.Delete(tr); n += 1
            seen.add(k)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(B, b)
    print('round', rnd, 'removed', n)
