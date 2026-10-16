# Rev C2: STEP models for the new parts whose 3D model is not in the KiCad 7 library.
# Same frame convention as make_3d.py (origin = footprint origin on the board top, Y = -Y(footprint), Z up, mm).
import sys
sys.argv = sys.argv[:2]
exec(open(__file__.replace('make_3d_c2.py', 'make_3d.py')).read().split('# ---- PowerPAK')[0])

# ---- ST MLPF-WB55-01E3 bumpless CSP 1.0 x 1.6 x ~0.4 mm, A1 (OUT) at footprint (-0.25, -0.587)
die = box(1.0, 1.6, 0.36, 0, 0, 0.04)
parts = [(die, DGREY, 'die')]
for x in (-0.25, 0.25):
    for y in (-0.587, 0.0, 0.587):
        parts.append((cq.Workplane('XY').circle(0.1).extrude(0.04).translate((x, -y, 0)), TINW, 'b%g%g' % (x, y)))
parts.append((cq.Workplane('XY').circle(0.07).extrude(0.01).translate((-0.3, 0.6, 0.40)), WHITE, 'A1'))
save('ST_MLPF-WB55-01E3', parts)

# ---- 32 MHz crystal SMD 2016, 4 pads: ceramic base + metal lid, h 0.45
base = box(2.0, 1.6, 0.25, 0, 0, 0.02)
lid = box(1.8, 1.4, 0.18, 0, 0, 0.27).edges('|Z').fillet(0.1)
parts = [(base, C(.85, .8, .7), 'base'), (lid, METAL, 'lid')]
for x in (-0.7, 0.7):
    for y in (-0.55, 0.55):
        parts.append((box(0.6, 0.45, 0.02, x, y, 0), GOLD, 'p%g%g' % (x, y)))
save('Crystal_SMD_2016-4Pin_2.0x1.6mm', parts)
