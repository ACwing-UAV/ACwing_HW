# remove dangling track stubs reported by the DRC, as long as the board stays fully connected
import sys, re, subprocess, shutil
path = sys.argv[1]
def drc():
    subprocess.run(['python3.12', '-c', f"""
import pcbnew
b=pcbnew.LoadBoard('{path}'); pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.WriteDRCReport(b,'/tmp/pc.rpt',pcbnew.EDA_UNITS_MILLIMETRES,True)"""], capture_output=True)
    t = open('/tmp/pc.rpt').read()
    unc = int(re.search(r'Found (\d+) unconnected', t).group(1))
    d = re.findall(r'\[track_dangling\].*?\n.*?\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): Track \[([^\]]*)\] on (\S+), length ([\d.]+) mm', t)
    return unc, d
for it in range(40):
    unc, d = drc()
    print('iter', it, 'unconnected', unc, 'dangling', len(d))
    if not d or unc: break
    shutil.copy(path, path + '.bak')
    r = subprocess.run(['python3.12', '-c', f"""
import pcbnew
b=pcbnew.LoadBoard('{path}')
D={sorted(set((float(x), float(y), n, l, float(ln)) for x, y, n, l, ln in d))!r}
trs=[t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK']
dele=[]
for x,y,net,lay,ln in D:
    for tr in trs:
        if tr in dele or tr.GetNetname()!=net or tr.GetLayerName()!=lay: continue
        if abs(tr.GetLength()/1e6-ln)>0.0006: continue
        s,e=tr.GetStart(),tr.GetEnd()
        if min(abs(s.x/1e6-x)+abs(s.y/1e6-y),abs(e.x/1e6-x)+abs(e.y/1e6-y))<0.0006:
            dele.append(tr); break
for tr in dele: b.Remove(tr)
pcbnew.SaveBoard('{path}',b)
print('removed',len(dele))"""], capture_output=True, text=True)
    print(' ', r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])
    if drc()[0] > 0:
        shutil.copy(path + '.bak', path); print('removal disconnected something: reverted'); break
