"""
Render a single OBJ file as a clean preview PNG.
The OBJ is split into 'g' groups per sub-solid (housing, pins, contacts, etc.).
Materials are assigned per-group using part-type + relative-size heuristics:
the largest group gets the part's "body" color; small groups get metal.

Run via:
    blender --background --python render_one.py -- <input.obj> <output.png>
"""
import bpy
import bmesh
import sys
import os
import math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--")+1:] if "--" in argv else []
if len(argv) < 2:
    print("usage: blender -b -P render_one.py -- <input.obj> <output.png>", file=sys.stderr)
    sys.exit(2)

obj_path, png_path = argv[0], argv[1]
part_name = os.path.splitext(os.path.basename(obj_path))[0]
name_lc = part_name.lower()

# Wipe scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for item in list(block):
        block.remove(item)

# Import OBJ — split by group so each Solid_N becomes its own object
bpy.ops.wm.obj_import(filepath=obj_path, use_split_groups=True)
imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not imported:
    print(f"!! No mesh imported from {obj_path}", file=sys.stderr)
    sys.exit(3)

# Compute volume per sub-mesh, sort largest first
def mesh_volume(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vol = abs(bm.calc_volume(signed=True)) if len(bm.faces) > 0 else 0
    bm.free()
    return vol

sub = [(o, mesh_volume(o)) for o in imported]
sub.sort(key=lambda x: x[1], reverse=True)
biggest_vol = sub[0][1] if sub[0][1] > 0 else 1.0


# Color palettes per part type — (base_color_RGB, roughness, metallic)
def body_palette():
    if any(k in name_lc for k in ("esp32", "wroom")):
        return (0.78, 0.79, 0.81), 0.32, 0.92  # tin shield
    if any(k in name_lc for k in ("dip-8", "tl072", "mcp")):
        return (0.04, 0.04, 0.05), 0.55, 0.0    # IC matte black
    if "to-92" in name_lc or "2n7000" in name_lc:
        return (0.05, 0.05, 0.06), 0.55, 0.0
    if any(k in name_lc for k in ("ams1117", "sot-223")):
        return (0.06, 0.06, 0.07), 0.5, 0.0
    if "ss34" in name_lc or "_sma" in name_lc:
        return (0.05, 0.05, 0.06), 0.5, 0.05
    if "ws2812" in name_lc or name_lc.endswith("led") or "_led" in name_lc:
        return (0.95, 0.95, 0.96), 0.35, 0.0    # white LED package
    if "jst" in name_lc:
        return (0.92, 0.88, 0.74), 0.55, 0.0    # JST cream-yellow
    if "fpc" in name_lc:
        return (0.10, 0.10, 0.12), 0.55, 0.0    # FPC connector black
    if "header" in name_lc:
        return (0.06, 0.06, 0.07), 0.5, 0.0     # pin header black
    if "usb" in name_lc:
        return (0.78, 0.79, 0.82), 0.30, 0.85   # USB-C steel shell
    if "microswitch" in name_lc or "d2f" in name_lc:
        return (0.05, 0.05, 0.06), 0.5, 0.0
    if "tactile" in name_lc:
        return (0.04, 0.04, 0.05), 0.55, 0.05
    if "470uf" in name_lc or "electrolytic" in name_lc:
        return (0.04, 0.04, 0.06), 0.45, 0.6    # aluminum can blackish blue
    if "ceramic" in name_lc and "cap" in name_lc:
        return (0.78, 0.62, 0.30), 0.55, 0.0    # tan ceramic
    if "resistor" in name_lc:
        return (0.18, 0.16, 0.22), 0.5, 0.05    # dark blue-grey
    if "ov5640" in name_lc:
        return (0.08, 0.32, 0.10), 0.5, 0.0     # PCB green
    return (0.45, 0.48, 0.52), 0.45, 0.3


def metal_palette():
    # Pins/contacts — gold for connectors, silver-tin for everything else
    if any(k in name_lc for k in ("jst", "header", "usb", "fpc")):
        return (0.85, 0.65, 0.20), 0.30, 1.0    # gold-plated
    return (0.85, 0.86, 0.88), 0.25, 1.0        # nickel-tin


body_color, body_rough, body_metal = body_palette()
metal_color, metal_rough, metal_metal = metal_palette()


def make_mat(name, color, rough, metallic):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


body_mat = make_mat(f"{part_name}_body", body_color, body_rough, body_metal)
metal_mat = make_mat(f"{part_name}_metal", metal_color, metal_rough, metal_metal)

# Apply: largest sub-mesh = body, small (< 5% of largest volume) = metal
# But: if STEP has many sub-solids (>20), it's an internal-detail model
# (ESP32, populated PCBs, etc.) — use single body color uniformly
many_solids = len(sub) > 20
for obj, vol in sub:
    if many_solids:
        chosen = body_mat
    else:
        is_metal = (vol < biggest_vol * 0.05) and biggest_vol > 0
        chosen = metal_mat if is_metal else body_mat
    obj.data.materials.clear()
    obj.data.materials.append(chosen)

# Combine all into one for camera framing convenience
bpy.ops.object.select_all(action='DESELECT')
for o in imported: o.select_set(True)
bpy.context.view_layer.objects.active = imported[0]
if len(imported) > 1:
    bpy.ops.object.join()
part = bpy.context.view_layer.objects.active
part.name = part_name

# Bounds
bb = [part.matrix_world @ Vector(c) for c in part.bound_box]
min_v = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
max_v = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
size = max_v - min_v
center = (min_v + max_v) / 2
part.location -= center

# Rotate so smallest dim becomes Z (lay flat)
dims = [size.x, size.y, size.z]
smallest = dims.index(min(dims))
if smallest == 0:
    part.rotation_euler = (0, math.pi/2, 0)
elif smallest == 1:
    part.rotation_euler = (math.pi/2, 0, 0)
bpy.context.view_layer.update()

bb = [part.matrix_world @ Vector(c) for c in part.bound_box]
min_v = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
max_v = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
size = max_v - min_v
center = (min_v + max_v) / 2
part.location -= center
bpy.context.view_layer.update()
bb = [part.matrix_world @ Vector(c) for c in part.bound_box]
min_v = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
diag = size.length

# Camera — 3/4 hero shot
cam_data = bpy.data.cameras.new("RenderCam")
cam_data.lens = 50
cam = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam)
d = max(diag * 1.5, 0.05)
cam.location = (d * 0.9, -d * 1.1, d * 0.55)
direction = -cam.location
direction.normalize()
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Lighting
def add_area(name, loc, energy, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy
    ld.size = max(diag * 2, 0.05)
    ld.color = color
    obj = bpy.data.objects.new(name, ld)
    obj.location = loc
    bpy.context.collection.objects.link(obj)

add_area("Key",  ( diag*2, -diag*2, diag*2.5), 25)
add_area("Fill", (-diag*2, -diag,   diag*1.5), 10, (0.9, 0.95, 1.0))
add_area("Back", ( 0,       diag*2, diag*2),   15)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.5
sun_data.angle = math.radians(8)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(35), math.radians(15), math.radians(40))
bpy.context.collection.objects.link(sun)

# World
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.78, 0.79, 0.81, 1)
    bg.inputs[1].default_value = 0.6

# Floor
floor_mesh = bpy.data.meshes.new("Floor")
floor_obj = bpy.data.objects.new("Floor", floor_mesh)
bpy.context.collection.objects.link(floor_obj)
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=diag * 4)
bm.to_mesh(floor_mesh)
bm.free()
floor_obj.location.z = min_v.z - 0.0001
floor_mat = bpy.data.materials.new("FloorMat")
floor_mat.use_nodes = True
fbsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
if fbsdf:
    fbsdf.inputs["Base Color"].default_value = (0.88, 0.88, 0.90, 1)
    fbsdf.inputs["Roughness"].default_value = 0.85
floor_obj.data.materials.append(floor_mat)

# Render — EEVEE for speed
scene = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = png_path

bpy.ops.render.render(write_still=True)
print(f"  -> {png_path}")
