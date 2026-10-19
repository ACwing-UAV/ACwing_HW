# Mechanical handoff DXF for the ACwing Flow rev A board. Board frame, mm, origin at the board centre,
# u right / v up, viewed from the SENSOR side (the side that faces the ground once mounted).
import ezdxf, math
HX, HY, R = 10.5, 12.5, 1.5
doc = ezdxf.new('R2010', setup=True); doc.units = ezdxf.units.MM
msp = doc.modelspace()
def layer(n, c): doc.layers.add(n, color=c)
for n, c in (('OUTLINE', 7), ('HOLES_M2', 1), ('HOLE_KEEPOUT_R2.4', 6), ('PMW3901_LENS_6x6', 3), ('PMW3901_OPTICAL_AXIS', 3),
             ('VL53L1X_PACKAGE', 4), ('VL53L1X_AXIS', 4), ('QWIIC_PLUG_ZONE', 5), ('SENSOR_SIDE_PARTS_MAX_3.0MM', 8), ('NOTES', 7)):
    layer(n, c)
# outline: rounded rectangle
k = R
pts = []
for cx, cy, a0 in ((HX - k, HY - k, 0), (-HX + k, HY - k, 90), (-HX + k, -HY + k, 180), (HX - k, -HY + k, 270)):
    for i in range(0, 91, 10):
        a = math.radians(a0 + i); pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'OUTLINE'})
for u in (-8.0, 8.0):
    msp.add_circle((u, 0.4), 1.1, dxfattribs={'layer': 'HOLES_M2'})
    msp.add_circle((u, 0.4), 2.4, dxfattribs={'layer': 'HOLE_KEEPOUT_R2.4'})
def rect(cx, cy, w, h, lay):
    msp.add_lwpolyline([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], close=True, dxfattribs={'layer': lay})
def cross(cx, cy, lay, s=1.0):
    msp.add_line((cx - s, cy), (cx + s, cy), dxfattribs={'layer': lay}); msp.add_line((cx, cy - s), (cx, cy + s), dxfattribs={'layer': lay})
rect(0.0, -6.2, 6.0, 6.0, 'PMW3901_LENS_6x6'); cross(0.0, -6.2, 'PMW3901_OPTICAL_AXIS')
rect(0.0, 0.8, 4.9, 2.5, 'VL53L1X_PACKAGE'); cross(0.0, 0.8, 'VL53L1X_AXIS')
# Qwiic plug zones: plug body + wire bend outside the left / right edge, at v = 7.0
for s in (-1, 1):
    x0 = s * HX
    msp.add_lwpolyline([(x0, 3.5), (x0 + s * 10.0, 3.5), (x0 + s * 10.0, 10.5), (x0, 10.5)], close=False, dxfattribs={'layer': 'QWIIC_PLUG_ZONE'})
msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'SENSOR_SIDE_PARTS_MAX_3.0MM'})
for txt, (x, y) in (('SENSOR SIDE VIEW (faces the ground)', (-10.5, 14.5)), ('PMW3901 lens 6x6x2.28, FOV 42 deg', (-10.5, -16.0)),
                    ('VL53L1X 4.9x2.5x1.56, FOV 27 deg', (-10.5, -17.5)), ('J1', (-12.0, 7.0)), ('J2', (11.0, 7.0))):
    msp.add_text(txt, height=0.8, dxfattribs={'layer': 'NOTES'}).set_placement((x, y))
doc.saveas('/home/claude/outFlow/handoff/ACwing_Flow_A_mech_outline.dxf')
print('ok')
