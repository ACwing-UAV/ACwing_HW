# Removes footprint silkscreen lines that KiCad's DRC reports as clipped by a solder mask opening of another part
# (J2 body outline next to the USB-C shell leg on the bottom). Cosmetic only.
import sys, re, pcbnew
B = sys.argv[1]
b = pcbnew.LoadBoard(B)
pcbnew.WriteDRCReport(b, '/tmp/claude-0/sf.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True)
pts = [(float(m.group(1)), float(m.group(2))) for m in re.finditer(r'\[silk_over_copper\][^\n]*\n[^\n]*\n\s*@\(([-\d.]+) mm, ([-\d.]+) mm\): Line', open('/tmp/claude-0/sf.rpt').read())]
n = 0
for (x, y) in pts:
    P = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
    for f in b.GetFootprints():
        for g in list(f.GraphicalItems()):
            if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g.GetClass() != 'PCB_TEXT' and g.HitTest(P, pcbnew.FromMM(0.02)):
                f.Remove(g); n += 1
# reference labels still overlapping another part's silkscreen: keep them on the Fab layer only
m = 0
for ref in re.findall(r"\[silk_overlap\][^\n]*\n[^\n]*\n(?:[^\n]*\n)?\s*@\([^)]*\): Reference '([^']+)'", open('/tmp/claude-0/sf.rpt').read()):
    f = b.FindFootprintByReference(ref)
    if f is not None and f.Reference().IsVisible():
        f.Reference().SetVisible(False); m += 1
pcbnew.SaveBoard(B, b)
print('silk lines removed:', n, '| references moved to Fab only:', m)
