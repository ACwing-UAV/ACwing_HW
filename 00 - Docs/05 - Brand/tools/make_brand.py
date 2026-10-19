# Brand files for the ACwing repository and the KiCad logo footprints.
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_geom import MARK, WORD, FULL
from shapely.geometry import Polygon, LineString, MultiPolygon, box
from shapely.ops import split, unary_union
from shapely import affinity
import cairosvg
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

def svg_path(geom):
    gs = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    d = []
    for g in gs:
        for ring in [g.exterior] + list(g.interiors):
            c = list(ring.coords)[:-1]
            d.append('M ' + ' L '.join('%.1f %.1f' % p for p in c) + ' Z')
    return ' '.join(d)
def write_svg(name, geom, fg, bg=None, margin=40, title='ACwing logo'):
    x0, y0, x1, y1 = geom.bounds
    x0 -= margin; y0 -= margin; x1 += margin; y1 += margin
    w, h = x1 - x0, y1 - y0
    if bg:                                           # square canvas for the filled variant
        s = max(w, h); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0, y0, w, h = cx - s / 2, cy - s / 2, s, s
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" width="%d" height="%d">\n'
           '<title>%s</title>\n<desc>ACwing - Andrea Cirillo. Vector logo.</desc>\n' % (x0, y0, w, h, round(w), round(h), title))
    if bg:
        svg += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>\n' % (x0, y0, w, h, bg)
    svg += '<path d="%s" fill="%s" fill-rule="evenodd"/>\n</svg>\n' % (svg_path(geom), fg)
    p = os.path.join(OUT, name + '.svg'); open(p, 'w').write(svg)
    cairosvg.svg2png(url=p, write_to=os.path.join(OUT, name + '.png'), output_width=1024 if w >= h else None,
                     output_height=None if w >= h else 1024)
write_svg('ACwing_logo_white', FULL, '#ffffff', title='ACwing logo, white (for dark backgrounds)')
write_svg('ACwing_logo_black', FULL, '#111111', title='ACwing logo, black (for light backgrounds)')
write_svg('ACwing_logo_on_black', FULL, '#ffffff', bg='#000000', margin=120, title='ACwing logo on black')
write_svg('ACwing_mark_white', MARK, '#ffffff', title='ACwing mark, white')
write_svg('ACwing_mark_black', MARK, '#111111', title='ACwing mark, black')
print('brand files written')

# ---------------------------------------------------------------- KiCad silkscreen footprints
def no_holes(geom):
    """KiCad 7 fp_poly has no holes: split every polygon with holes by vertical cuts through its holes."""
    todo = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    done = []
    while todo:
        g = todo.pop()
        if g.is_empty or g.area < 1e-6:
            continue
        if not g.interiors:
            done.append(g); continue
        hx = g.interiors[0].centroid.x
        y0, y1 = g.bounds[1] - 1, g.bounds[3] + 1
        pieces = split(g, LineString([(hx, y0), (hx, y1)]))
        for pc in pieces.geoms:
            todo.append(pc)
    return done
def footprint(name, geom, height_mm, layer='F.SilkS', descr=''):
    x0, y0, x1, y1 = geom.bounds
    s = height_mm / (y1 - y0)
    g = affinity.translate(geom, -(x0 + x1) / 2, -(y0 + y1) / 2)
    g = affinity.scale(g, s, s, origin=(0, 0))                 # SVG y down = KiCad y down
    g = g.simplify(0.01)
    polys = no_holes(g)
    w = (x1 - x0) * s
    lines = ['(footprint "%s" (version 20221018) (generator pcbnew)' % name, '  (layer "F.Cu")',
             '  (descr "%s")' % descr, '  (tags "logo ACwing")', '  (attr board_only exclude_from_pos_files exclude_from_bom)',
             '  (fp_text reference "REF**" (at 0 %.2f) (layer "F.Fab") hide (effects (font (size 0.8 0.8) (thickness 0.12))))' % (height_mm / 2 + 1),
             '  (fp_text value "%s" (at 0 %.2f) (layer "F.Fab") hide (effects (font (size 0.8 0.8) (thickness 0.12))))' % (name, height_mm / 2 + 2)]
    for p in polys:
        pts = ' '.join('(xy %.4f %.4f)' % c for c in list(p.exterior.coords)[:-1])
        lines.append('  (fp_poly (pts %s) (stroke (width 0) (type solid)) (fill solid) (layer "%s"))' % (pts, layer))
    lines.append(')')
    return '\n'.join(lines) + '\n', w, len(polys)
LIBDIR = os.path.join(OUT, 'ACwing_Logo.pretty'); os.makedirs(LIBDIR, exist_ok=True)
for kind, geom in (('Full', FULL), ('Mark', MARK)):
    for h in (4, 5, 6, 7, 8, 9, 10, 12):
        txt, w, n = footprint('ACwing_Logo_%s_%gmm' % (kind, h), geom, h,
                              descr='ACwing %s logo on the silkscreen, %g mm high' % ('full' if kind == 'Full' else 'mark-only', h))
        open(os.path.join(LIBDIR, 'ACwing_Logo_%s_%gmm.kicad_mod' % (kind, h)), 'w').write(txt)
print('footprints written; full logo aspect w/h = %.3f, mark aspect = %.3f' % ((FULL.bounds[2] - FULL.bounds[0]) / (FULL.bounds[3] - FULL.bounds[1]), (MARK.bounds[2] - MARK.bounds[0]) / (MARK.bounds[3] - MARK.bounds[1])))
# minimum stroke width at a given height: thinnest feature ~ largest erosion that keeps every part
for kind, geom in (('Full', FULL), ('Mark', MARK)):
    h_px = geom.bounds[3] - geom.bounds[1]
    for r in range(2, 40):
        er = geom.buffer(-r)
        parts = len(er.geoms) if er.geom_type == 'MultiPolygon' else (0 if er.is_empty else 1)
        if parts < (len(geom.geoms) if geom.geom_type == 'MultiPolygon' else 1):
            print('%s: thinnest stroke ~ %d px = %.4f x height' % (kind, 2 * r, 2 * r / h_px)); break
