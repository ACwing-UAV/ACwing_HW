# ACwing logo geometry: the vector path supplied by Andrea Cirillo (1254 x 1254 px canvas, even-odd fill), as shapely
# polygons. MARK = drone + "AC" monogram, WORD = "ACwing" wordmark.
import re, os
from shapely.geometry import Polygon
from shapely.ops import unary_union
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ACwing_reference_vector.svg')
d = re.search(r' d="([^"]+)"', open(SRC).read()).group(1)
rings = []
for sub in d.split('Z'):
    pts = [tuple(map(float, m)) for m in re.findall(r'[ML]\s*([-\d.]+)\s+([-\d.]+)', sub)]
    if len(pts) >= 3:
        rings.append(Polygon(pts).buffer(0))
shape = None
for r in rings:                                   # even-odd = XOR of all rings
    shape = r if shape is None else shape.symmetric_difference(r)
parts = list(shape.geoms) if shape.geom_type == 'MultiPolygon' else [shape]
MARK = unary_union([p for p in parts if p.centroid.y < 800])
WORD = unary_union([p for p in parts if p.centroid.y >= 800])
FULL = unary_union([MARK, WORD])
