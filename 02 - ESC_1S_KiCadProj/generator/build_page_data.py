# Packs the three board meshes (STEP -> npz) and the stack-check results into a JS data file for the viewer page.
import numpy as np, json, base64
MESH = {'ESC': '/tmp/claude-0/meshESCB.npz', 'FC': '/tmp/claude-0/meshH.npz', 'GPS': '/tmp/claude-0/meshGPSC.npz'}
out = {}
for k, f in MESH.items():
    d = np.load(f); T = d['T'].astype(np.float64).reshape(-1, 3).copy(); C = d['C']
    T[:, 0] -= 150.0; T[:, 1] += 100.0                       # STEP (x, y) -> board (u, v); z from the board bottom
    q = np.round(T * 500).astype(np.int16)                   # 2 um steps, +-65 mm
    col = np.clip(np.asarray(C, dtype=np.float64) * 255, 0, 255).astype(np.uint8)
    out[k] = dict(pos=base64.b64encode(q.tobytes()).decode(), col=base64.b64encode(col.tobytes()).decode(), n=int(len(T) // 3))
res = {s: json.load(open('/home/claude/stack/stack_check_s%d.json' % s)) for s in (6, 8)}
data = dict(mesh=out, checks=res)
open('/home/claude/stack/page/stack_data.js', 'w').write('window.STACK = ' + json.dumps(data, separators=(',', ':')) + ';\n')
print({k: v['n'] for k, v in out.items()}, 'bytes', len(open('/home/claude/stack/page/stack_data.js').read()))
