# ACwing Flow rev A: silkscreen extras (back side), project footprint library (ACwing_Flow.pretty) with project 3D models.
#   python3 gps_finish.py <out dir>
import sys, os, re, json, shutil
import pcbnew

OUT = sys.argv[1]
PROJECT = 'ACwing_Flow_A'
BOARD = os.path.join(OUT, PROJECT + '.kicad_pcb')
SCH = os.path.join(OUT, PROJECT + '.kicad_sch')
OX, OY = 150.0, 100.0
LIB = 'ACwing_Flow'
LIB3D = '/usr/share/kicad/3dmodels'
D3 = os.path.join(OUT, '3d')
MODEL_FOR = {}
NEW_MODEL = {'PixArt_PMW3901MB_COB-28_6x6mm', 'ST_UFQFPN-20_3x3mm_P0.5mm', 'JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal'}   # made by genE/make_3d_e.py
def P(u, v): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + u), pcbnew.FromMM(OY - v))

b = pcbnew.LoadBoard(BOARD)
# ---------------------------------------------------------------- 1. silkscreen: board name on the back (no parts there)
for d in list(b.GetDrawings()):
    if d.GetLayer() == pcbnew.B_SilkS and d.GetClass() == 'PCB_TEXT' and d.GetText().startswith(('ACwing_Flow', 'Qwiic')):
        b.Delete(d)
def text(s, u, v, size=0.8):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(pcbnew.B_SilkS); t.SetPosition(P(u, v)); t.SetMirrored(True)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size))); t.SetTextThickness(pcbnew.FromMM(0.15))
    b.Add(t)
text('ACwing Flow rev A', 0, -9.5, 1.0)
text('ACwing Flow rev A', 0, -11.0, 0.8)
text('Qwiic J1 / J2', 0, 9.6, 0.8)
pcbnew.SaveBoard(BOARD, b)

# ---------------------------------------------------------------- 2. project library + 3D models
os.makedirs(os.path.join(OUT, LIB + '.pretty'), exist_ok=True)
os.makedirs(D3, exist_ok=True)
b = pcbnew.LoadBoard(BOARD)
names = {}
for f in b.GetFootprints():
    fpid = f.GetFPID()
    lib, name = str(fpid.GetLibNickname()), str(fpid.GetLibItemName())
    names[name] = lib if lib != LIB else names.get(name, lib)
for name, lib in names.items():
    if lib == LIB:
        continue
    src = pcbnew.FootprintLoad('/usr/share/kicad/footprints/%s.pretty' % lib, name)
    pcbnew.FootprintSave(os.path.join(OUT, LIB + '.pretty'), src)
for f in b.GetFootprints():
    f.SetFPID(pcbnew.LIB_ID(LIB, str(f.GetFPID().GetLibItemName())))
pcbnew.SaveBoard(BOARD, b)

def fix_models(text_):
    def sub(m):
        base = m.group(2)
        dst = MODEL_FOR.get(base, base)
        if not os.path.exists(os.path.join(D3, dst + '.step')):
            src = os.path.join(LIB3D, m.group(1) + '.3dshapes', base + '.step')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(D3, dst + '.step'))
            else:
                print('NO MODEL', base)
        return '(model "${KIPRJMOD}/3d/%s.step"' % dst
    return re.subn(r'\(model "?\$\{KICAD\d_3DMODEL_DIR\}/([^/"]+)\.3dshapes/([^/" ]+)\.(?:wrl|step)"?', sub, text_)
b = pcbnew.LoadBoard(BOARD)
for f in b.GetFootprints():
    nm = str(f.GetFPID().GetLibItemName())
    if nm in NEW_MODEL:
        f.Models().clear()
        m = pcbnew.FP_3DMODEL(); m.m_Filename = '${KIPRJMOD}/3d/%s.step' % nm
        m.m_Scale = pcbnew.VECTOR3D(1, 1, 1); m.m_Offset = pcbnew.VECTOR3D(0, 0, 0); m.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
        f.Add3DModel(m); shutil.copy('/home/claude/models_e/%s.step' % nm, os.path.join(D3, nm + '.step'))
        lf = pcbnew.FootprintLoad(os.path.join(OUT, LIB + '.pretty'), nm)
        lf.Models().clear()
        m2 = pcbnew.FP_3DMODEL(); m2.m_Filename = m.m_Filename
        m2.m_Scale = pcbnew.VECTOR3D(1, 1, 1); m2.m_Offset = pcbnew.VECTOR3D(0, 0, 0); m2.m_Rotation = pcbnew.VECTOR3D(0, 0, 0)
        lf.Add3DModel(m2); pcbnew.FootprintSave(os.path.join(OUT, LIB + '.pretty'), lf)
pcbnew.SaveBoard(BOARD, b)
s, n = fix_models(open(BOARD).read()); open(BOARD, 'w').write(s)
nl = 0
for fn in os.listdir(os.path.join(OUT, LIB + '.pretty')):
    p = os.path.join(OUT, LIB + '.pretty', fn)
    t, k = fix_models(open(p).read()); open(p, 'w').write(t); nl += k
print('model paths: board %d, library %d; models in 3d/: %s' % (n, nl, ' '.join(sorted(os.listdir(D3)))))

# schematic + parts.json links
s = open(SCH).read()
s2, k = re.subn(r'\(property "Footprint" "(?!%s:)[^":]+:([^"]+)"' % LIB, r'(property "Footprint" "%s:\1"' % LIB, s)
open(SCH, 'w').write(s2)
pj = SCH + '.parts.json'
pp = json.load(open(pj))
for v in pp.values():
    if v.get('fp') and ':' in v['fp']:
        v['fp'] = LIB + ':' + v['fp'].split(':', 1)[1]
json.dump(pp, open(pj, 'w'), indent=0)
open(os.path.join(OUT, 'fp-lib-table'), 'w').write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.pretty")(options "")'
    '(descr "ACwing Flow project footprints (3D models in ${KIPRJMOD}/3d)"))\n)\n' % (LIB, LIB))
if os.path.exists(os.path.join(OUT, 'sym-lib-table')):
    os.remove(os.path.join(OUT, 'sym-lib-table'))
print('library', LIB, 'footprints', len(os.listdir(os.path.join(OUT, LIB + '.pretty'))), '| schematic links', k)
