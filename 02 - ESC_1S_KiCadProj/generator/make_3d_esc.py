# DimaQuadESC rev A / FC rev F: STEP models missing from the KiCad 7 library (frame convention of genD/make_3d.py).
import sys
sys.argv = sys.argv[:2]
exec(open('/home/claude/genD/make_3d.py').read().split('# ---- PowerPAK')[0])

# ---- JST SH SM08B-SRSS-TB side entry: body 10.0 x 4.25 x 2.9, mouth at footprint +Y (model -Y),
#      signal pins at footprint Y -2.0 (x -3.5..3.5), fixing tabs at (+-4.8, 1.875)
body = box(10.0, 4.25, 2.9, 0, -0.4, 0).cut(box(8.6, 3.2, 1.6, 0, -1.1, 0.6))
parts = [(body, C(.95, .95, .92), 'body')]
for k in range(8):
    parts.append((box(0.3, 1.3, 0.12, -3.5 + k, 2.0, 0), TINW, 'pin%d' % k))
for x in (-4.8, 4.8):
    parts.append((box(1.0, 1.6, 0.15, x, -1.875, 0), TINW, 'tab%g' % x))
save('JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal', parts)
