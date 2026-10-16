import sys, numpy as np, cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.Quantity import Quantity_Color
from OCP.TopLoc import TopLoc_Location
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.BRep import BRep_Tool
from OCP.TopoDS import TopoDS
path, out = sys.argv[1], sys.argv[2]
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True)
r.ReadFile(path); r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
tris, cols = [], []
def color_of(lbl, shape):
    c = Quantity_Color()
    for t in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        if ct.GetColor_s(lbl, t, c) or ct.GetColor(shape, t, c):
            return (c.Red(), c.Green(), c.Blue())
    return None
def walk(lbl, loc, inherited):
    shape = st.GetShape_s(lbl)
    col = color_of(lbl, shape) or inherited
    if st.IsAssembly_s(lbl) or st.IsReference_s(lbl):
        if st.IsReference_s(lbl):
            ref = TDF_Label(); st.GetReferredShape_s(lbl, ref)
            walk(ref, loc.Multiplied(st.GetLocation_s(lbl)), col); return
        seq = TDF_LabelSequence(); st.GetComponents_s(lbl, seq)
        for i in range(1, seq.Length() + 1):
            walk(seq.Value(i), loc, col)
        return
    s = shape.Moved(loc)
    BRepMesh_IncrementalMesh(s, 0.08, False, 0.5, True)
    ex = TopExp_Explorer(s, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current()); l = TopLoc_Location()
        fc = Quantity_Color(); fcol = col
        f0 = TopoDS.Face_s(ex.Current())
        if ct.GetColor(f0.Moved(loc.Inverted()), XCAFDoc_ColorType.XCAFDoc_ColorSurf, fc) or ct.GetColor(f0, XCAFDoc_ColorType.XCAFDoc_ColorSurf, fc):
            fcol = (fc.Red(), fc.Green(), fc.Blue())
        tri = BRep_Tool.Triangulation_s(f, l)
        if tri is not None:
            tr = l.Transformation()
            pts = [tri.Node(i).Transformed(tr) for i in range(1, tri.NbNodes() + 1)]
            P = np.array([[p.X(), p.Y(), p.Z()] for p in pts])
            for i in range(1, tri.NbTriangles() + 1):
                a, b_, c = tri.Triangle(i).Get()
                tris.append(P[[a - 1, b_ - 1, c - 1]]); cols.append(fcol or (0.2, 0.5, 0.2))
        ex.Next()
roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1, roots.Length() + 1):
    walk(roots.Value(i), TopLoc_Location(), None)
T = np.array(tris); C = np.array(cols)
np.savez_compressed(out, T=T, C=C)
print(T.shape)
