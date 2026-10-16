# Points every footprint at a STEP model inside the project (${KIPRJMOD}/3d), copying the official KiCad
# models there, so the 3D view / STEP export is complete in KiCad 7, 8 and 9 alike.
import sys, os, re, shutil, math
import pcbnew
OUT = sys.argv[1]
BOARD = os.path.join(OUT, 'DimaQuadFC_C2.kicad_pcb')
LIB3D = '/usr/share/kicad/3dmodels'
D3 = os.path.join(OUT, '3d')
RENAME = {'Vishay_PowerPAK_1212-8_Single': 'PowerPAK_1212-8_Single',
          'ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y': 'ST_HLGA-10_2x2mm'}
CUSTOM = {'D_SMAflat': ('D_SMAflat', (0, 0, 0))}
# QFN-48 EP5.6: the library has no model; 3d/ holds a copy of the EP5.15 one (same 7 x 7 body)
# rev C: the motors sit in the frame ducts, not on the board -> MotorPads without a 3D body
b = pcbnew.LoadBoard(BOARD)
report = {}
for fp in b.GetFootprints():
    name = fp.GetFPID().GetLibItemName().wx_str() if hasattr(fp.GetFPID().GetLibItemName(), 'wx_str') else str(fp.GetFPID().GetLibItemName())
    models = list(fp.Models())
    if name == 'MotorPads_1x02_SMD':
        fp.Models().clear(); report[name] = '(no model: the motor sits in the frame)'; continue
    if name in CUSTOM:
        fp.Models().clear()
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = '${KIPRJMOD}/3d/%s.step' % CUSTOM[name][0]
        m.m_Offset = pcbnew.VECTOR3D(*CUSTOM[name][1]); m.m_Scale = pcbnew.VECTOR3D(1, 1, 1); m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
        fp.Add3DModel(m)
        report[name] = m.m_Filename
        continue
    for m in models:
        f = m.m_Filename
        base = os.path.splitext(os.path.basename(f))[0]
        dst_base = RENAME.get(base, base)
        dst = os.path.join(D3, dst_base + '.step')
        if not os.path.exists(dst):
            src = re.sub(r'\$\{KICAD\d_3DMODEL_DIR\}', LIB3D, f)
            src = os.path.splitext(src)[0] + '.step'
            if os.path.exists(src):
                shutil.copy(src, dst)
            else:
                print('NO MODEL for', name, base); continue
        m.m_Filename = '${KIPRJMOD}/3d/%s.step' % dst_base
        report[name] = m.m_Filename
pcbnew.SaveBoard(BOARD, b)
for k, v in sorted(report.items()):
    print('%-48s %s' % (k, v))
no = sorted({str(f.GetFPID().GetLibItemName()) for f in b.GetFootprints() if not len(list(f.Models()))})
print('no model (no physical body):', no)

# project footprint library: same models
for fn, (mod, off) in [('D_SMAflat', CUSTOM['D_SMAflat'])]:
    p = os.path.join(OUT, 'DimaQuad.pretty', fn + '.kicad_mod')
    s = open(p).read()
    while '(model ' in s:                         # strip existing model blocks (balanced parentheses)
        i = s.index('(model '); d = 0
        for j in range(i, len(s)):
            d += {'(': 1, ')': -1}.get(s[j], 0)
            if d == 0:
                break
        s = s[:i].rstrip(' ') + s[j + 1:].lstrip('\n')
    blk = ('  (model "${KIPRJMOD}/3d/%s.step"\n    (offset (xyz %g %g %g))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n' % ((mod,) + off))
    s = s.rstrip().rstrip(')') + blk + ')\n'
    open(p, 'w').write(s)

# pcbnew returns copies of the model list: rewrite the library model paths directly in the board file
s = open(BOARD).read()
def sub(m):
    base = RENAME.get(m.group(2), m.group(2))
    return '(model "${KIPRJMOD}/3d/%s.step"' % base
s2, n = re.subn(r'\(model "?\$\{KICAD\d_3DMODEL_DIR\}/([^/"]+)\.3dshapes/([^/" ]+)\.(?:wrl|step)"?', sub, s)
open(BOARD, 'w').write(s2)
print('model paths rewritten in board file:', n)
