"""
Phase renderer driven by the ExpandIt manifest. Loads perfboard.glb +
components.glb at their manifest-specified positions, highlights pins
for the current phase, draws polarity arrows.

Usage:
    blender --background --python render_phase_v2.py -- <manifest.json> <phase_id> <out.png>

phase_id options: "0" (bare board), "1"..."8" (cumulative through phase N), "all" (full assembly)
"""
import bpy
import bmesh
import json
import sys
import os
import math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--")+1:] if "--" in argv else []
if len(argv) < 3:
    print("usage: render_phase_v2.py <manifest> <phase_id> <out.png>", file=sys.stderr); sys.exit(2)

manifest_path, phase_target, png_path = argv[0], argv[1], argv[2]
manifest_dir = os.path.dirname(manifest_path)

with open(manifest_path) as f:
    M = json.load(f)

# Wipe scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.armatures, bpy.data.curves):
    for item in list(block):
        block.remove(item)


def import_glb(path, scale_mm=True):
    """Import a .glb. Returns the imported object(s) joined into one."""
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new_objs = [o for o in bpy.context.scene.objects if o not in before and o.type == 'MESH']
    if not new_objs:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in new_objs: o.select_set(True)
    bpy.context.view_layer.objects.active = new_objs[0]
    if len(new_objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    if scale_mm:
        # glb is in meters; scale up to mm-as-units
        obj.scale = (1000.0, 1000.0, 1000.0)
        bpy.ops.object.transform_apply(scale=True)
    return obj


# ─── Load perfboard ───
pb_path = os.path.join(manifest_dir, M["base"]["model"])
pb = import_glb(pb_path)
pb.name = "Perfboard"
pb_w, pb_h, pb_t = M["base"]["size_mm"]

# ─── Decide which phases to render ───
if phase_target == "0":
    target_id = 0
elif phase_target == "all":
    target_id = 99
else:
    target_id = int(phase_target)


# ─── Load components for phases ≤ target_id ───
placed_components = []
for phase in M["phases"]:
    if phase["id"] > target_id:
        continue
    is_current_phase = (phase["id"] == target_id)
    for c in phase["components"]:
        glb = os.path.join(manifest_dir, c["model"])
        if not os.path.exists(glb):
            print(f"  miss: {glb}", file=sys.stderr); continue
        obj = import_glb(glb)
        if obj is None: continue
        obj.name = f"{c['ref']}"
        x, y, z = c["position_mm"]
        # Component's GLB is centered at origin with smallest dim → Z, in mm.
        # bbox to lift bottom to z=board_top
        bb = [obj.matrix_world @ Vector(b) for b in obj.bound_box]
        mn_z = min(v.z for v in bb)
        obj.location = (x, y, z - mn_z + pb_t)
        obj.rotation_euler = (0, 0, math.radians(c["rotation_deg"]))
        bpy.context.view_layer.update()
        placed_components.append((c, obj, is_current_phase))


# ─── Highlight pin holes for current-phase components ───
def add_pin_highlight(x, y, z_top):
    """Yellow ring around a pin position to show 'put pin here'."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=20, radius1=1.4, radius2=1.4, depth=0.1, cap_ends=False)
    m = bpy.data.meshes.new("hl")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("hl", m)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, z_top + 0.5)

    mat = bpy.data.materials.new("hl_mat")
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (1.0, 0.85, 0.1, 1)
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (1.0, 0.85, 0.1, 1)
        b.inputs["Emission Strength"].default_value = 4.0
    obj.data.materials.append(mat)


# Highlight pins of components in the CURRENT phase only (so user sees what's new this step)
for c, obj, is_current in placed_components:
    if not is_current:
        continue
    for p in c.get("pins", []):
        add_pin_highlight(p["x_mm"], p["y_mm"], pb_t / 2)


# ─── Polarity callouts ───
def add_text_label(text, x, y, z, size=2.0, color=(1.0, 0.9, 0.1)):
    bpy.ops.object.text_add(location=(x, y, z))
    txt = bpy.context.object
    txt.data.body = text
    txt.data.size = size
    txt.data.align_x = 'CENTER'
    txt.data.align_y = 'CENTER'
    txt.data.extrude = 0.05
    mat = bpy.data.materials.new("LblMat")
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = 2.0
    txt.data.materials.append(mat)


def add_arrow(start, end, color=(1.0, 0.2, 0.2)):
    """Small 3D arrow for orientation/polarity callout."""
    bm = bmesh.new()
    s = Vector(start); e = Vector(end)
    direction = (e - s)
    length = direction.length
    if length < 0.01: return
    direction.normalize()
    # build a small cylinder with cone head
    bmesh.ops.create_cone(bm, segments=12, radius1=0.25, radius2=0.25, depth=length * 0.7, cap_ends=True)
    # offset cylinder along its Z to start at origin
    for v in bm.verts: v.co.z += length * 0.35
    # cone head at end
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, segments=12, radius1=0.6, radius2=0.0, depth=length * 0.3, cap_ends=True)
    for v in tmp.verts: v.co.z += length * 0.85
    for f in tmp.faces:
        verts = [bm.verts.new(v.co) for v in f.verts]
        bm.faces.new(verts)
    tmp.free()
    m = bpy.data.meshes.new("arrow"); bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("arrow", m)
    bpy.context.collection.objects.link(obj)
    obj.location = s
    # rotate the +Z-aligned arrow to point in direction
    up = Vector((0, 0, 1))
    if direction != up:
        axis = up.cross(direction)
        angle = math.acos(max(-1, min(1, up.dot(direction))))
        if axis.length > 0.01:
            obj.rotation_mode = 'AXIS_ANGLE'
            obj.rotation_axis_angle = (angle, *axis.normalized())
    mat = bpy.data.materials.new("arr_mat")
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = 1.0
    obj.data.materials.append(mat)


for c, obj, is_current in placed_components:
    if not is_current: continue
    polarity = c.get("polarity")
    if not polarity: continue
    x, y, _ = c["position_mm"]
    # Arrow markers per polarity type
    z_arrow_base = pb_t + 6
    z_arrow_top = pb_t + 1
    if polarity == "diode_stripe":
        # stripe-side cathode pin
        add_text_label("← stripe (K)", x - 5, y + 3, z_arrow_base, size=1.4, color=(1.0, 0.3, 0.3))
    elif polarity == "electrolytic_plus":
        add_text_label("+ leg (long)", x, y + 6, z_arrow_base, size=1.6, color=(1.0, 0.85, 0.2))
        add_text_label("− leg (stripe)", x, y - 6, z_arrow_base, size=1.6, color=(0.5, 0.7, 1.0))
    elif polarity == "tantalum_stripe":
        add_text_label("+ stripe", x, y + 3, z_arrow_base, size=1.2, color=(1.0, 0.85, 0.2))
    elif polarity == "ic_pin1_notch":
        add_text_label("◄ pin 1 notch", x - 4, y + 4, z_arrow_base, size=1.2, color=(0.4, 1.0, 0.4))
    elif polarity == "led_notch":
        add_text_label("◄ notched corner = pin 1", x - 3, y + 3, z_arrow_base, size=1.0)
    elif polarity == "transistor_flat":
        add_text_label("flat side ↑", x, y + 3, z_arrow_base, size=1.2, color=(1.0, 0.6, 0.2))
    elif polarity == "regulator_tab":
        add_text_label("tab ↑", x, y + 3, z_arrow_base, size=1.2, color=(0.4, 1.0, 0.4))


# ─── Reference designator labels (small white text near each placed part) ───
for c, obj, is_current in placed_components:
    x, y, _ = c["position_mm"]
    add_text_label(c["ref"], x, y, pb_t + 3.5, size=1.3, color=(1.0, 1.0, 0.15) if is_current else (0.6, 0.6, 0.6))


# ─── Camera + lights ───
diag = math.sqrt(pb_w**2 + pb_h**2)

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = pb_w * 1.3
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0, -10, 100)
target = Vector((0, 0, 0))
direction = target - cam.location
direction.normalize()
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam


def add_area(name, loc, energy, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, type='AREA')
    ld.energy = energy
    ld.size = diag * 1.5
    ld.color = color
    obj = bpy.data.objects.new(name, ld)
    obj.location = loc
    bpy.context.collection.objects.link(obj)


add_area("Key",  ( diag,    -diag,    diag*1.5), 8000)
add_area("Fill", (-diag*0.7, -diag*0.4, diag*0.8), 3000, (0.9, 0.95, 1.0))
add_area("Back", (  0,       diag*1.2, diag),    4000)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(45))
bpy.context.collection.objects.link(sun)

world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.85, 0.85, 0.87, 1)
    bg.inputs[1].default_value = 0.6


scene = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
scene.render.resolution_x = 2400
scene.render.resolution_y = 1800
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = png_path

bpy.ops.render.render(write_still=True)
print(f"  -> {png_path} (phase {phase_target}, {len(placed_components)} components)")
