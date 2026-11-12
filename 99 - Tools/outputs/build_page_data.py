# Packs the three board meshes (STEP -> npz, step_mesh.py) and the stack-check result into the JS data file of the viewer page.
import numpy as np, json, base64, sys
out = {}
for k in ('ESC', 'FC', 'GPSD'):
    d = np.load('mesh_%s.npz' % k); T = d['T'].astype(np.float64).reshape(-1, 3).copy(); C = d['C']
    T[:, 0] -= 150.0; T[:, 1] += 100.0                       # STEP (x, y) -> board (u, v); z from the board bottom
    q = np.round(T * 500).astype(np.int16)                   # 2 um steps, +-65 mm
    col = np.clip(np.asarray(C, dtype=np.float64) * 255, 0, 255).astype(np.uint8)
    out[k] = dict(pos=base64.b64encode(q.tobytes()).decode(), col=base64.b64encode(col.tobytes()).decode(), n=int(len(T) // 3))
data = dict(mesh=out, checks={'D6': json.load(open('stack_check_d6.json'))})
open(sys.argv[1], 'w').write('window.STACK = ' + json.dumps(data, separators=(',', ':')) + ';\n')
print({k: v['n'] for k, v in out.items()})
