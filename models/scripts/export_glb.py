"""
Convert each component OBJ to a self-contained .glb (glTF binary).
Materials from render_one.py's heuristic are baked in so the .glb
displays correctly in any glTF runtime.

Usage:
    blender --background --python export_glb.py -- <input.obj> <output.glb>
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
    print("usage: blender -b -P export_glb.py -- <input.obj> <output.glb>", file=sys.stderr)
    sys.exit(2)

obj_path, glb_path = argv[0], argv[1]
part_name = os.path.splitext(os.path.basename(obj_path))[0]
name_lc = part_name.lower()

# wipe scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for item in list(block):
        block.remove(item)

# import OBJ keeping group splits
bpy.ops.wm.obj_import(filepath=obj_path, use_split_groups=True)
imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not imported:
    print(f"!! No mesh in {obj_path}", file=sys.stderr); sys.exit(3)


def mesh_volume(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    v = abs(bm.calc_volume(signed=True)) if len(bm.faces) > 0 else 0
    bm.free()
    return v


sub = sorted([(o, mesh_volume(o)) for o in imported], key=lambda x: x[1], reverse=True)
biggest = sub[0][1] if sub[0][1] > 0 else 1.0


def body_palette():
    if any(k in name_lc for k in ("esp32", "wroom")):
        return (0.78, 0.79, 0.81), 0.32, 0.92
    if any(k in name_lc for k in ("dip-8", "tl072", "mcp")):
        return (0.04, 0.04, 0.05), 0.55, 0.0
    if "to-92" in name_lc or "2n7000" in name_lc:
        return (0.05, 0.05, 0.06), 0.55, 0.0
    if any(k in name_lc for k in ("ams1117", "sot-223")):
        return (0.06, 0.06, 0.07), 0.5, 0.0
    if "ss34" in name_lc or "_sma" in name_lc:
        return (0.05, 0.05, 0.06), 0.5, 0.05
    if "ws2812" in name_lc:
        return (0.95, 0.95, 0.96), 0.35, 0.0
    if "jst" in name_lc:
        return (0.92, 0.88, 0.74), 0.55, 0.0
    if "fpc" in name_lc:
        return (0.10, 0.10, 0.12), 0.55, 0.0
    if "header" in name_lc:
        return (0.06, 0.06, 0.07), 0.5, 0.0
    if "usb" in name_lc:
        return (0.78, 0.79, 0.82), 0.30, 0.85
    if "microswitch" in name_lc or "d2f" in name_lc:
        return (0.05, 0.05, 0.06), 0.5, 0.0
    if "tactile" in name_lc:
        return (0.04, 0.04, 0.05), 0.55, 0.05
    if "470uf" in name_lc or "electrolytic" in name_lc:
        return (0.04, 0.04, 0.06), 0.45, 0.6
    if "ceramic" in name_lc and "cap" in name_lc:
        return (0.78, 0.62, 0.30), 0.55, 0.0
    if "resistor" in name_lc:
        return (0.18, 0.16, 0.22), 0.5, 0.05
    if "ov5640" in name_lc:
        return (0.08, 0.32, 0.10), 0.5, 0.0
    return (0.45, 0.48, 0.52), 0.45, 0.3


def metal_palette():
    if any(k in name_lc for k in ("jst", "header", "usb", "fpc")):
        return (0.85, 0.65, 0.20), 0.30, 1.0
    return (0.85, 0.86, 0.88), 0.25, 1.0


def make_mat(name, color, rough, metallic):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*color, 1.0)
        b.inputs["Roughness"].default_value = rough
        if "Metallic" in b.inputs:
            b.inputs["Metallic"].default_value = metallic
    return m


body_mat = make_mat(f"{part_name}_body", *body_palette())
metal_mat = make_mat(f"{part_name}_metal", *metal_palette())

many_solids = len(sub) > 20
for o, vol in sub:
    if many_solids:
        chosen = body_mat
    else:
        is_metal = (vol < biggest * 0.05) and biggest > 0
        chosen = metal_mat if is_metal else body_mat
    o.data.materials.clear()
    o.data.materials.append(chosen)

# Lay flat (smallest dim → Z) and bake transform
bpy.ops.object.select_all(action='DESELECT')
for o in imported: o.select_set(True)
bpy.context.view_layer.objects.active = imported[0]
if len(imported) > 1:
    bpy.ops.object.join()
part = bpy.context.view_layer.objects.active
part.location = (0, 0, 0)
part.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

bb = [Vector(c) for c in part.bound_box]
mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
size = mx - mn
dims = [size.x, size.y, size.z]
smallest = dims.index(min(dims))
if smallest == 0:
    part.rotation_euler = (0, math.pi/2, 0)
elif smallest == 1:
    part.rotation_euler = (math.pi/2, 0, 0)
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(rotation=True)

# Recenter to origin
bb = [part.matrix_world @ Vector(c) for c in part.bound_box]
mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
center = (mn + mx) / 2
part.location -= center
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True)

# Scale: KiCad/STEP files are typically in mm. glTF is unitless but conventionally meters.
# Components in mm-as-meter scale would be huge (a 25mm chip would render as 25m). Scale to meters.
# Multiply by 0.001 to convert mm→m.
part.scale = (0.001, 0.001, 0.001)
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(scale=True)

# Export GLB (binary glTF). Self-contained — materials baked in.
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_image_format='AUTO',
)
size_kb = os.path.getsize(glb_path) // 1024
print(f"  -> {glb_path} ({size_kb} KB)")
