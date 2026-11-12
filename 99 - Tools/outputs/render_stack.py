# ACwing stack render: ESC 1S + FC (M2 grommets, 5 mm gap) + GPS (6 mm standoffs), KiCad 10 GLB exports, Blender Cycles.
import bpy, math, mathutils, sys
OUT = sys.argv[-1] if sys.argv[-1].endswith('/') else '/home/claude/stack/'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
Z = {'ESC': 0.0, 'FC': 6.0, 'GPS': 13.0}
for k, z in Z.items():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f'/home/claude/stack/{k}.glb')
    new = set(bpy.data.objects) - before
    root = bpy.data.objects.new(k, None); sc.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    root.scale = (1000, 1000, 1000); root.location = (-150, 100, z)
def mat(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']; bsdf.inputs['Base Color'].default_value = (*rgb, 1)
    bsdf.inputs['Roughness'].default_value = rough; bsdf.inputs['Metallic'].default_value = metal
    return m
BLACK, GREY, NYLON, SIL = mat('wire', (0.02, 0.02, 0.02), 0.4), mat('plug', (0.82, 0.82, 0.80), 0.6), mat('nylon', (0.85, 0.82, 0.72), 0.5), mat('grommet', (0.12, 0.12, 0.13), 0.8)
def cyl(x, y, z0, z1, r, m, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), vertices=verts)
    o = bpy.context.object; o.data.materials.append(m); return o
def boxo(x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object; o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2); o.data.materials.append(m); return o
for x in (-10, 10):
    for y in (-10, 10):
        cyl(x, y, 1.0, 6.0, 2.5, SIL); cyl(x, y, 7.0, 8.0, 2.5, SIL)       # grommet body and top flange
        cyl(x, y, 8.0, 13.0, 2.0, NYLON, 6)                                 # nylon standoff (hex)
def wire(pts, r=0.28):
    cu = bpy.data.curves.new('w', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('wire', cu); o.data.materials.append(BLACK); sc.collection.objects.link(o)
# cable A: ESC J1 -> FC J2, 1:1 U-loop in front of the front edge (pins u -7 ... -14)
boxo(-15.4, -5.6, 19.4, 22.2, 1.15, 4.1, GREY); boxo(-15.4, -5.6, 19.4, 22.2, 7.15, 10.1, GREY)
for i in range(8):
    u = -7.0 - i
    wire([(u, 22.0, 2.6), (u, 24.6, 3.4), (u, 25.6, 5.6), (u, 24.6, 7.9), (u, 22.0, 8.6)], 0.22)
# Qwiic: FC J3 (right edge) -> GPS J1 (right edge), pins v 2.1 ... 5.1
boxo(19.4, 22.2, 0.2, 7.0, 7.15, 10.1, GREY); boxo(14.5, 17.3, 0.45, 7.25, 14.15, 17.1, GREY)
for i in range(4):
    v1, v2 = 2.1 + i, 2.35 + i
    wire([(22.0, v1, 8.6), (24.5, v1, 9.6), (25.2, (v1 + v2) / 2, 12.6), (23.0, v2, 16.4), (17.1, v2, 15.6)], 0.22)
# floor, light, world
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -2.6)); fl = bpy.context.object; fl.is_shadow_catcher = True
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
bpy.ops.object.light_add(type='SUN', location=(30, 40, 80)); s = bpy.context.object; s.data.energy = 3.0; s.data.angle = math.radians(12)
s.rotation_euler = (math.radians(30), math.radians(15), math.radians(35))
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(sys.argv[-2]) if sys.argv[-2].isdigit() else 64; sc.cycles.device = 'CPU'
sc.render.film_transparent = True; sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 1100, 800
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
def shot(loc, target, lens, name, ortho=None):
    co.location = loc; d = mathutils.Vector(target) - mathutils.Vector(loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if ortho: cam.type = 'ORTHO'; cam.ortho_scale = ortho
    else: cam.type = 'PERSP'; cam.lens = lens
    sc.render.filepath = OUT + name; bpy.ops.render.render(write_still=True)
shot((95, 120, 75), (0, 2, 6), 85, 'stack_frontright.png')
shot((0, 160, 9), (0, 0, 7), 85, 'stack_front.png', ortho=58)
