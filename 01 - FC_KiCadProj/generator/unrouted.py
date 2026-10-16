import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 150, 100
b.BuildConnectivity()
c = b.GetConnectivity()
print('unconnected count', c.GetUnconnectedCount(True))
for name, ni in sorted(b.GetNetsByName().items(), key=lambda kv: str(kv[0])):
    code = ni.GetNetCode()
    if code <= 0: continue
    rn = c.GetRatsnestForNet(code)
    if rn is None: continue
    edges = [e for e in rn.GetEdges() if e.IsVisible()] if hasattr(rn, 'GetEdges') else []
    if edges:
        out = []
        for e in edges:
            s, t = e.GetSourcePos(), e.GetTargetPos()
            out.append('(%.1f,%.1f)-(%.1f,%.1f)' % (pcbnew.ToMM(s.x) - OX, OY - pcbnew.ToMM(s.y), pcbnew.ToMM(t.x) - OX, OY - pcbnew.ToMM(t.y)))
        print(str(name), len(edges), ' '.join(out))
