"""
Generate the perf-board base as a .glb file:
  - Tan FR4 substrate
  - 28 × 20 grid of through-holes at 2.54mm (0.1") pitch
  - Copper annular rings around each hole

Output: /Users/Sims/Desktop/expandit/products/layit/models/perfboard.glb

Run: blender --background --python make_perfboard.py
"""
import bpy
import bmesh
import math
from mathutils import Matrix

W, H, T = 70.0, 50.0, 1.6   # mm
PITCH = 2.54
COLS = int(W / PITCH)         # 27
ROWS = int(H / PITCH)         # 19
HOLE_R = 0.5
PAD_R_OUTER = 0.95
PAD_THICK = 0.05

OUT = "/Users/Sims/Desktop/expandit/products/layit/models/perfboard.glb"

# Wipe scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for item in list(block):
        block.remove(item)


def make_substrate():
    """FR4 substrate with grid of through-holes."""
    bm = bmesh.new()
    # outer rectangle
    cube = bmesh.ops.create_cube(bm, size=1)   # unit cube: verts at ±0.5
    for v in cube["verts"]:
        v.co.x *= W   # 0.5 * W = W/2 → bbox spans -W/2 to +W/2
        v.co.y *= H
        v.co.z *= T
    # cut a hole at each grid position (use bmesh subtract isn't available; use boolean modifier later)
    m = bpy.data.meshes.new("Substrate")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("Substrate", m)
    bpy.context.collection.objects.link(obj)
    return obj


def make_pad_grid():
    """All copper annular rings as a single mesh (one big bmesh build)."""
    bm = bmesh.new()
    for r in range(ROWS):
        for c in range(COLS):
            x = (c - (COLS - 1) / 2) * PITCH
            y = (r - (ROWS - 1) / 2) * PITCH
            ring = bmesh.ops.create_circle(bm, cap_ends=False, segments=16, radius=PAD_R_OUTER)
            for v in ring["verts"]:
                v.co.x += x
                v.co.y += y
                v.co.z = T / 2 + PAD_THICK / 2
    m = bpy.data.meshes.new("PadGrid")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("PadGrid", m)
    bpy.context.collection.objects.link(obj)
    return obj


def make_pad_grid_solid():
    """Solid rings (annular discs) using small cylinders, joined into one mesh."""
    bm = bmesh.new()
    for r in range(ROWS):
        for c in range(COLS):
            x = (c - (COLS - 1) / 2) * PITCH
            y = (r - (ROWS - 1) / 2) * PITCH
            # outer disc: solid cap
            tmp = bmesh.new()
            bmesh.ops.create_cone(tmp, segments=16, radius1=PAD_R_OUTER, radius2=PAD_R_OUTER,
                                  depth=PAD_THICK, cap_ends=True)
            for v in tmp.verts:
                v.co.x += x
                v.co.y += y
                v.co.z += T / 2 + PAD_THICK / 2
            # merge into bm
            for f in tmp.faces:
                verts = [bm.verts.new(v.co) for v in f.verts]
                bm.faces.new(verts)
            tmp.free()
    bm.normal_update()
    m = bpy.data.meshes.new("PadGrid")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("PadGrid", m)
    bpy.context.collection.objects.link(obj)
    return obj


def make_hole_grid():
    """Dark dots (the actual through-hole) overlaid on top of the pads."""
    bm = bmesh.new()
    for r in range(ROWS):
        for c in range(COLS):
            x = (c - (COLS - 1) / 2) * PITCH
            y = (r - (ROWS - 1) / 2) * PITCH
            tmp = bmesh.new()
            bmesh.ops.create_cone(tmp, segments=12, radius1=HOLE_R, radius2=HOLE_R,
                                  depth=PAD_THICK + 0.02, cap_ends=True)
            for v in tmp.verts:
                v.co.x += x
                v.co.y += y
                v.co.z += T / 2 + PAD_THICK / 2 + 0.01
            for f in tmp.faces:
                verts = [bm.verts.new(v.co) for v in f.verts]
                bm.faces.new(verts)
            tmp.free()
    bm.normal_update()
    m = bpy.data.meshes.new("HoleGrid")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("HoleGrid", m)
    bpy.context.collection.objects.link(obj)
    return obj


def material(name, color, rough, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    if "Metallic" in b.inputs:
        b.inputs["Metallic"].default_value = metallic
    return m


# Build pieces
substrate = make_substrate()
pads = make_pad_grid_solid()
holes = make_hole_grid()

# Materials
fr4 = material("FR4", (0.06, 0.32, 0.14), 0.45, 0.0)        # green soldermask
copper = material("Copper", (0.85, 0.65, 0.18), 0.25, 1.0)  # ENIG gold pad
hole_dark = material("HoleDark", (0.02, 0.02, 0.02), 0.8, 0.0)

substrate.data.materials.append(fr4)
pads.data.materials.append(copper)
holes.data.materials.append(hole_dark)

# Join into a single object for clean export
bpy.ops.object.select_all(action='DESELECT')
substrate.select_set(True)
pads.select_set(True)
holes.select_set(True)
bpy.context.view_layer.objects.active = substrate
bpy.ops.object.join()
joined = bpy.context.view_layer.objects.active
joined.name = "Perfboard"

# Scale to meters (mm × 0.001) for glTF
joined.scale = (0.001, 0.001, 0.001)
bpy.ops.object.transform_apply(scale=True)

# Export
bpy.ops.object.select_all(action='DESELECT')
joined.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
)

import os
size_kb = os.path.getsize(OUT) // 1024
print(f"  -> {OUT} ({size_kb} KB, {ROWS*COLS} holes)")
