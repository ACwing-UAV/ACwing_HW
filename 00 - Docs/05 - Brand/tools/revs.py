# Rewrites revision references in the docs: released boards -> rev A, older pre-release iterations -> draft X.
import re, sys, os, glob
CUR = {'FC': 'H', 'ESC': 'B', 'GPS': 'D', 'FLOW': 'A'}
KEYS = [(r'(?i)flight controller|\bFC\b', 'FC'), (r'(?i)ESC ?1S|power board|motor board|\bESC rev', 'ESC'), (r'\bGPS\b', 'GPS'), (r'(?i)\bflow\b', 'FLOW')]
DEF = {'00 - FC_Docs': 'FC', '01 - ESC_1S_Docs': 'ESC', '02 - GPS_Docs': 'GPS', '03 - FLOW_Docs': 'FLOW',
       '01 - FC_KiCadProj': 'FC', '02 - ESC_1S_KiCadProj': 'ESC', '03 - GPS_KiCadProj': 'GPS', '04 - FLOW_KiCadProj': 'FLOW'}
PAT = re.compile(r'\b([Rr]ev)(s?) ?((?:[A-H]2?)(?:/[A-H]2?)*)\b')
def board_for(line, pos, default):
    look = line[max(0, pos - 45):pos]
    best = None
    for k, b in KEYS:
        for m in re.finditer(k, look):
            if best is None or m.start() > best[0]: best = (m.start(), b)
    return best[1] if best else default
def conv(m, b):
    R, s, letters = m.group(1), m.group(2), m.group(3).split('/')
    if b is None: return None
    cur = [l == CUR[b] for l in letters]
    if all(cur): return R + ' A'
    if not any(cur):
        word = ('Draft' if R == 'Rev' else 'draft') + ('s' if len(letters) > 1 else '')
        return word + ' ' + '/'.join(letters)
    return None
def run(f, apply):
    parts = f.split(os.sep); default = next((DEF[p] for p in parts if p in DEF), 'FC')
    out = []; todo = []
    for i, line in enumerate(open(f).read().split('\n')):
        def rep(m):
            if m.group(3) == 'A' and re.search(r'ACwing (FC|ESC 1S|GPS|Flow) $', line[:m.start()]): return m.group(0)
            b = board_for(line, m.start(), default); r = conv(m, b)
            if r is None: todo.append((i + 1, m.group(0), line.strip()[:150])); return m.group(0)
            if r != m.group(0): print('  %s:%d  %-10s -> %-12s [%s] %s' % (os.path.basename(f), i + 1, m.group(0), r, b, line.strip()[:110]) if not apply else '', end='\n' if not apply else '')
            return r
        out.append(PAT.sub(rep, line))
    for t in todo: print('  TODO %s:%d %s | %s' % (os.path.basename(f), *t))
    if apply: open(f, 'w').write('\n'.join(out))
if __name__ == '__main__':
    apply = sys.argv[1] == 'apply'
    for f in sys.argv[2:]: run(f, apply)
