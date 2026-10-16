# STEP models (with colours) for the parts whose 3D model is missing from the KiCad 7 library or that
# use project footprints. Model frame = KiCad convention: origin at the footprint origin on the board
# top surface, X as in the footprint, Y = -Y(footprint), Z up, mm.
import sys, os
import cadquery as cq

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
C = lambda r, g, b: cq.Color(r, g, b)
BLACK, DGREY, LGREY, METAL, GOLD, WHITE = C(.08, .08, .08), C(.22, .22, .24), C(.55, .55, .58), C(.78, .78, .80), C(.85, .68, .25), C(.92, .92, .9)
ORANGE, STEEL, TINW = C(.95, .45, .1), C(.6, .62, .66), C(.82, .82, .84)

from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TCollection import TCollection_ExtendedString
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TDataStd import TDataStd_Name
from OCP.Interface import Interface_Static

def save(name, parts):
    """one free shape per part, colour on the shape and on every face (what KiCad's STEP reader uses)"""
    doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    # like the official KiCad models: ONE shape (compound of all parts), colours on its faces
    shapes, colors = [], []
    for i, (shape, color, nm) in enumerate(parts):
        for v in (shape.vals() if hasattr(shape, 'vals') else [shape]):
            shapes.append(v); colors.append(color)
    comp = cq.Compound.makeCompound(shapes)
    lbl = st.AddShape(comp.wrapped, False)
    TDataStd_Name.Set_s(lbl, TCollection_ExtendedString(name))
    for v, color in zip(shapes, colors):
        r, g, b_ = color.toTuple()[:3]
        qc = Quantity_Color(r, g, b_, Quantity_TOC_RGB)
        ex = TopExp_Explorer(v.wrapped, TopAbs_FACE)
        while ex.More():
            sub = st.AddSubShape(lbl, ex.Current())
            if not sub.IsNull():
                ct.SetColor(sub, qc, XCAFDoc_ColorType.XCAFDoc_ColorSurf)
            ex.Next()
    w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True)
    Interface_Static.SetCVal_s('write.step.schema', 'AP214')
    w.Transfer(doc, STEPControl_AsIs)
    w.Write(os.path.join(OUT, name + '.step'))
    print('written', name)

def box(x, y, z, cx=0, cy=0, z0=0):
    return cq.Workplane('XY').box(x, y, z, centered=(True, True, False)).translate((cx, cy, z0))

# ---- PowerPAK 1212-8 single (Vishay outline, fits AON7524 DFN3x3A as approximated by the footprint)
body = box(3.3, 3.3, 0.97, 0, 0, 0.05).edges('|Z').fillet(0.15)
leads = cq.Workplane('XY')
parts = [(body, BLACK, 'body')]
for y in (-0.99, -0.33, 0.33, 0.99):                     # S S S G on -X
    parts.append((box(0.45, 0.33, 0.25, -1.55, -y, 0.0), TINW, 'lead%g' % y))
parts.append((box(1.75, 2.3, 0.2, 0.62, 0, 0.0), TINW, 'drain'))   # exposed drain pad
parts.append((cq.Workplane('XY').circle(0.18).extrude(0.02).translate((-1.0, 1.0, 1.02)), WHITE, 'pin1'))
save('PowerPAK_1212-8_Single', parts)

# ---- DFN-6 1.3 x 1.2 mm, 0.38 mm (LD39130S)
body = box(1.3, 1.2, 0.36, 0, -0.025, 0.02)
parts = [(body, DGREY, 'body')]
for x in (-0.5, 0.5):
    for y in (-0.4, 0.0, 0.4):
        parts.append((box(0.3, 0.18, 0.02, x, -y, 0.0), TINW, 'p%g%g' % (x, y)))
parts.append((cq.Workplane('XY').circle(0.08).extrude(0.01).translate((-0.4, 0.38, 0.38)), WHITE, 'pin1'))
save('DFN-6_1.3x1.2mm_P0.4mm', parts)

# ---- ST HLGA-10 2 x 2 x 0.73 (LPS22DF), with the pressure vent
body = box(2.0, 2.0, 0.71, 0, 0, 0.02).cut(cq.Workplane('XY').circle(0.2).extrude(0.3).translate((0.45, 0.45, 0.5)))
parts = [(body, DGREY, 'body')]
parts.append((cq.Workplane('XY').circle(0.07).extrude(0.01).translate((-0.7, 0.7, 0.73)), WHITE, 'pin1'))
save('ST_HLGA-10_2x2mm', parts)

# ---- STM32WB5MMG SiP-LGA-86 11 x 7.3 x 1.38: shielded part + unshielded antenna end (footprint -Y)
H = 1.382
shield = box(7.3, 11.0 - 3.2, H - 0.02, 0, -1.6, 0.02).edges('|Z').fillet(0.2)
antenna = box(7.3, 3.2, H - 0.02, 0, 5.5 - 1.6, 0.02)
mark = (cq.Workplane('XY').text('STM32WB5MMG', 0.7, 0.01).translate((0, -1.6, H)))
parts = [(shield, DGREY, 'shield'), (antenna, BLACK, 'antenna_mold'),
         (cq.Workplane('XY').circle(0.25).extrude(0.01).translate((-2.9, 1.6, H)), WHITE, 'pin1')]
try:
    parts.append((mark, WHITE, 'marking'))
except Exception:
    pass
save('ST-SiP-LGA-86-11x7.3mm', parts)

# ---- USB-C receptacle HRO TYPE-C-31-M-12 (top mount): 8.94 x 7.3 x 3.16, mouth toward footprint +Y
W_, D_, H_ = 8.94, 7.3, 3.16
shell = (cq.Workplane('XZ').center(0, H_ / 2).rect(W_, H_).extrude(D_ / 2, both=True)
         .edges('|Y').fillet(1.2))
cav = (cq.Workplane('XZ').center(0, H_ / 2).rect(W_ - 0.5, H_ - 0.5).extrude(D_ / 2 - 0.4, both=True)
       .edges('|Y').fillet(1.0).translate((0, -0.45, 0)))
shell = shell.cut(cav)
tongue = box(6.7, 4.2, 0.7, 0, -1.4, H_ / 2 - 0.35)
parts = [(shell, METAL, 'shell'), (tongue, BLACK, 'tongue')]
for (x, y) in ((4.32, -1.05), (-4.32, -1.05), (4.32, 3.0), (-4.32, 3.0)):     # shell legs through the PCB
    parts.append((box(0.6, 1.0, 2.4, x, y, -2.0), METAL, 'leg%g%g' % (x, y)))
for i, x in enumerate([-3.25, -2.45, -1.75, -1.25, -0.75, -0.25, 0.25, 0.75, 1.25, 1.75, 2.45, 3.25]):
    parts.append((box(0.3 if abs(x) < 2 else 0.5, 1.2, 0.1, x, 4.0, 0.0), GOLD, 'pin%d' % i))
save('USB_C_Receptacle_HRO_TYPE-C-31-M-12', parts)

# ---- SMAflat DO-221AC (STPS3L45AF): body 4.3 x 2.6 x 1.0, flat leads, cathode band at pad 1 (-X)
body = box(4.2, 2.6, 0.95, 0, 0, 0.05).edges('|Z').fillet(0.1)
parts = [(body, BLACK, 'body')]
for s in (-1, 1):
    parts.append((box(1.1, 1.5, 0.2, s * 2.1, 0, 0.0), TINW, 'lead%d' % s))
parts.append((box(0.45, 2.6, 0.01, -1.45, 0, 1.0), LGREY, 'band'))
save('D_SMAflat', parts)

# ---- coreless 8520 motor + TPU sleeve, centred on the motor axis (offset applied in the footprint)
# board top = z 0; flange on top (FL_T 1.2), motor top 2.0 above the flange, 20 mm long (macro v9)
top = 1.2 + 2.0
motor = cq.Workplane('XY').circle(4.25).extrude(20.0).translate((0, 0, top - 20.0))
cap = cq.Workplane('XY').circle(2.6).extrude(0.6).translate((0, 0, top))
shaft = cq.Workplane('XY').circle(0.5).extrude(4.0).translate((0, 0, top + 0.6))
sleeve = (cq.Workplane('XY').circle(5.45).circle(4.15).extrude(8.0).translate((0, 0, 1.2 - 8.0))
          .union(cq.Workplane('XY').circle(7.5).circle(4.15).extrude(1.2)))
tabs = cq.Workplane('XY').box(1.2, 0.8, 0.3).translate((0, -2.5, top - 20.0 - 0.15))
save('Motor_Coreless_8520', [(motor, METAL, 'can'), (cap, LGREY, 'cap'), (shaft, STEEL, 'shaft'),
                             (sleeve, ORANGE, 'sleeve_TPU'), (tabs, GOLD, 'terminals')])
