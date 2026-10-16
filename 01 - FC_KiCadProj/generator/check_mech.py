# Mechanical checks of the frame-C handoff on the board: grommet component keep-outs, antenna keep-out,
# courtyard inside the outline (0.25), pogo-pad surroundings, bottom height (from the CSV max heights).
import sys, csv, pcbnew
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
BOARD, CSVF = sys.argv[1], sys.argv[2]
OX, OY = 150.0, 100.0
b = pcbnew.LoadBoard(BOARD)
def B(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def poly(ps):
    return unary_union([Polygon([B(ps.Outline(i).CPoint(j)) for j in range(ps.Outline(i).PointCount())]) for i in range(ps.OutlineCount())])
ps = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps); BOARD_POLY = poly(ps)
H = {r['Ref']: float(r['Max_height_mm']) for r in csv.DictReader(open(CSVF))}
HOLES = [(8, 8), (-8, 8), (-8, -8), (8, -8)]
ANT = box(-20.5, 9.0, -17.5, 20.5)     # rev C2 chip-antenna keep-out
TP = box(-3.81 - 0.5, -14.27 - 0.5, 3.81 + 0.5, -11.73 + 0.5)      # pogo pads (u, v), pad r 0.5
err = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    fp.BuildCourtyardCaches()
    bot = fp.IsFlipped()
    c = fp.GetCourtyard(pcbnew.B_CrtYd if bot else pcbnew.F_CrtYd)
    if not c.OutlineCount():
        continue
    cy = poly(c)
    if ref.startswith('H'):
        continue
    if not BOARD_POLY.buffer(-0.25).contains(cy) and ref not in ('J1', 'U2'):
        err.append('%s courtyard closer than 0.25 mm to the outline' % ref)
    for (x, y) in HOLES:
        r = 3.6 if bot else 3.0
        if cy.intersects(Point(x, y).buffer(r)):
            err.append('%s (%s) inside the grommet keep-out r %.1f at (%g, %g)' % (ref, 'bottom' if bot else 'top', r, x, y))
    if ref not in ('AE1', 'R34') and cy.intersects(ANT):
        err.append('%s inside the antenna keep-out' % ref)
    if bot and H.get(ref, 0) > 1.2:
        err.append('%s on the bottom is %.2f mm tall (max 1.2)' % (ref, H[ref]))
    if bot and not ref.startswith('TP') and H.get(ref, 0) > 0.3 and cy.distance(TP) < 1.5:
        err.append('%s (%.2f mm) within 1.5 mm of the pogo pads' % (ref, H.get(ref, 0)))
print('\n'.join(err) if err else 'mechanical checks OK')
