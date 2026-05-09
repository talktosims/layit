"""
Build a top-down assembly view of the LayIt Laser PCB.
Component positions estimated from the binder Section 3 ("R1/R2 near ESP32 footprint",
"U1/U2 between power input and ESP32", etc.). Coordinates in mm.

Run with:
    blender --background --python assemble.py -- <output.png>
"""
import bpy
import bmesh
import sys
import os
import math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--")+1:] if "--" in argv else []
png_path = argv[0] if argv else "/tmp/layit_assembly.png"
MODE = argv[1] if len(argv) > 1 else "full"  # full | wiring | exploded | phase1..7

# Phase number per binder Section 3
# 1=resistors, 2=ceramic caps, 3=DIP sockets, 4=semiconductors+power,
# 5=connectors+switches, 6=status LED, 7=ESP32, 8=ICs into sockets
PHASE_MAP = {
    # phase 1
    "R1": 1, "R2": 1, "R5": 1, "R6": 1, "R7": 1, "R8": 1, "R9": 1, "R10": 1,
    "R11": 1, "R12": 1, "R13": 1, "R14": 1, "R15": 1,
    # phase 2: ceramic + tantalum caps
    "C2": 2, "C3": 2, "C4": 2, "C5": 2, "C6": 2, "C7": 2, "C8": 2, "C9": 2,
    "C10": 2, "C11": 2, "C12": 2,
    # phase 4: semiconductors, regulators, electrolytic, schottky
    "C1": 4, "D1": 4, "U1 5V": 4, "U2 3V3": 4, "Q1": 4,
    # phase 5: connectors and switches
    "PD": 5, "J6 UART": 5, "SW1": 5, "SW2": 5, "J3 Laser": 5, "J4 Galvo": 5, "J5 FPC": 5,
    # phase 6: status LED
    "LED1": 6,
    # phase 7: ESP32 module
    "U3 ESP32": 7,
    # phase 8: ICs into sockets (using DIP-8 placeholder)
    "U4 DAC": 8, "U5 OpAmp": 8,
}
PHASE_NUM = None
if MODE.startswith("phase"):
    try:
        PHASE_NUM = int(MODE[5:])
    except ValueError:
        PHASE_NUM = None

MESHES = "/Users/Sims/Desktop/layit/models/meshes"

# (obj_filename, x_mm, y_mm, z_mm, rot_z_deg, label) — PCB plane is XY, Z up
COMPONENTS = [
    # Power input (LEFT edge)
    ("USB-C_GCT_USB4500-03-0-A.obj", -27,  0, 0,    90,  "PD"),
    ("Cap_470uF_electrolytic.obj",   -18,  4, 0,     0,  "C1"),
    ("SS34_SMA.obj",                  -16, -4, 0,     0,  "D1"),
    ("AMS1117_SOT-223.obj",          -11,  6, 0,    90,  "U1 5V"),
    ("AMS1117_SOT-223.obj",          -11, -6, 0,    90,  "U2 3V3"),
    ("Cap_ceramic_0805.obj",          -7,  6, 0,     0,  "C3"),
    ("Cap_ceramic_0805.obj",          -7, -6, 0,     0,  "C5"),

    # ESP32 (CENTER) — long axis along Y, antenna end at +Y edge
    ("ESP32-S3-WROOM-1.obj",           4,  0, 0,     0,  "U3 ESP32"),
    ("Tactile_6mm.obj",                4, -14, 0,    0,  "SW1"),
    ("Tactile_6mm.obj",               -2, -14, 0,    0,  "SW2"),
    ("Header_1x04.obj",                4, -19, 0,    0,  "J6 UART"),

    # ICs (TOP region)
    ("DIP-8_body.obj",                14,  8, 0,    90,  "U4 DAC"),
    ("DIP-8_body.obj",                14, -3, 0,    90,  "U5 OpAmp"),

    # Laser driver
    ("2N7000_TO-92.obj",              22,  4, 0,     0,  "Q1"),

    # Connectors at RIGHT edge
    ("JST_B3B-XH-A_3pin.obj",         28, -10, 0,    90, "J3 Laser"),
    ("JST_B6B-XH-A_6pin.obj",         28,   5, 0,    90, "J4 Galvo"),

    # FPC camera + status LED
    ("FPC_24pin.obj",                 14,  16, 0,    0,  "J5 FPC"),
    ("WS2812B.obj",                   -2,  -8, 0,    0,  "LED1"),
]

# Decorative resistor tags (we have one R STEP, just multi-place it)
RESISTORS = [
    (  3,  -5, "R1"),  (  6, -5, "R2"),     # near ESP32
    ( 14,  16, "R13"), ( 17, 16, "R14"),    # near camera FPC
    (-15, -10, "R15"),                      # near safety switch wire pads
    ( 11,   3, "R5"),  ( 11,  -1, "R6"),
    ( 17,   3, "R7"),  ( 17,  -1, "R8"),
    ( 22,   8, "R9"),  ( 19,   8, "R10"),
    ( 11,  16, "R11"), ( 17,  19, "R12"),
]

CAPS = [
    (  4,   2, "C2"),  ( 14,   3, "C4"),  ( 14,  -8, "C6"),
    (  4,  -2, "C7"),  (-12,   8, "C8"),  (-12,  -8, "C9"),
    ( 22,   1, "C10"), ( 14,  20, "C11"), (-15,  -1, "C12"),
]


# ─── scene wipe ───
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for item in list(block):
        block.remove(item)


# ─── per-part color heuristic (same as render_one.py body_palette) ───
def palette_for(name_lc):
    if any(k in name_lc for k in ("esp32", "wroom")):
        return (0.78, 0.79, 0.81), 0.32, 0.92
    if any(k in name_lc for k in ("dip-8", "tl072", "mcp")):
        return (0.04, 0.04, 0.05), 0.55, 0.0
    if "to-92" in name_lc or "2n7000" in name_lc:
        return (0.05, 0.05, 0.06), 0.55, 0.0
    if any(k in name_lc for k in ("ams1117", "sot-223")):
        return (0.06, 0.06, 0.07), 0.5, 0.0
    if "ss34" in name_lc or "_sma" in name_lc or "d1" == name_lc:
        return (0.05, 0.05, 0.06), 0.5, 0.05
    if "ws2812" in name_lc or name_lc == "led1":
        return (0.95, 0.95, 0.96), 0.35, 0.0
    if "jst" in name_lc:
        return (0.92, 0.88, 0.74), 0.55, 0.0
    if "fpc" in name_lc:
        return (0.10, 0.10, 0.12), 0.55, 0.0
    if "header" in name_lc or "j6" in name_lc:
        return (0.06, 0.06, 0.07), 0.5, 0.0
    if "usb" in name_lc or "pd" == name_lc:
        return (0.78, 0.79, 0.82), 0.30, 0.85
    if "microswitch" in name_lc or "d2f" in name_lc:
        return (0.05, 0.05, 0.06), 0.5, 0.0
    if "tactile" in name_lc:
        return (0.04, 0.04, 0.05), 0.55, 0.05
    if "470uf" in name_lc or "electrolytic" in name_lc or "c1" == name_lc:
        return (0.04, 0.04, 0.06), 0.45, 0.6
    if "ceramic" in name_lc and "cap" in name_lc:
        return (0.78, 0.62, 0.30), 0.55, 0.0
    if "resistor" in name_lc:
        return (0.18, 0.16, 0.22), 0.5, 0.05
    return (0.45, 0.48, 0.52), 0.45, 0.3


_mat_cache = {}
def get_mat(filename):
    base = os.path.basename(filename).lower()
    if base in _mat_cache:
        return _mat_cache[base]
    color, rough, metal = palette_for(base)
    mat = bpy.data.materials.new(name=f"M_{base}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metal
    _mat_cache[base] = mat
    return mat


_label_records = []   # (label_text, world_xy_target_above_part)


def add_label(text, x, y, z_top):
    """Flat 2D-style text above the part, readable top-down."""
    # short labels (1-3 char like R1, C5) get smaller text than long ones (U3 ESP32)
    sz = 1.4 if len(text) <= 3 else 2.0
    # Lift higher above the tallest component (ESP32 is ~3mm) so text stays above all parts
    bpy.ops.object.text_add(location=(x, y, z_top + 1.5))
    txt = bpy.context.object
    txt.data.body = text
    txt.data.size = sz
    txt.data.align_x = 'CENTER'
    txt.data.align_y = 'CENTER'
    txt.data.extrude = 0.05
    txt.rotation_euler = (0, 0, 0)   # flat = readable from top-down ortho

    # White text with bright outline-like emission for legibility on green PCB
    mat = bpy.data.materials.new(name=f"Lbl_{text}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.95, 0.20, 1)  # yellow
        bsdf.inputs["Roughness"].default_value = 0.5
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.95, 0.20, 1)
            bsdf.inputs["Emission Strength"].default_value = 1.5
    txt.data.materials.append(mat)
    _label_records.append((text, (x, y, z_top + 1.5)))


# ─── PCB footprint helpers (holes + SMD pads + silkscreen) ───
_hole_mat = None
_pad_mat = None
_silk_mat = None


def _hole_material():
    global _hole_mat
    if _hole_mat is None:
        _hole_mat = bpy.data.materials.new("M_hole")
        _hole_mat.use_nodes = True
        b = _hole_mat.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (0.015, 0.015, 0.015, 1)
        b.inputs["Roughness"].default_value = 0.7
    return _hole_mat


def _pad_material():
    global _pad_mat
    if _pad_mat is None:
        _pad_mat = bpy.data.materials.new("M_pad")
        _pad_mat.use_nodes = True
        b = _pad_mat.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (0.85, 0.78, 0.45, 1)  # ENIG gold-ish
        b.inputs["Roughness"].default_value = 0.25
        if "Metallic" in b.inputs:
            b.inputs["Metallic"].default_value = 1.0
    return _pad_mat


def _silk_material():
    global _silk_mat
    if _silk_mat is None:
        _silk_mat = bpy.data.materials.new("M_silk")
        _silk_mat.use_nodes = True
        b = _silk_mat.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (0.96, 0.96, 0.94, 1)
        b.inputs["Roughness"].default_value = 0.7
    return _silk_mat


PCB_TOP_Z = 0.0  # board sits with top at z=0


def add_hole(x, y, radius=0.55):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=16, radius1=radius, radius2=radius, depth=0.4, cap_ends=True)
    m = bpy.data.meshes.new("hole")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("hole", m)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, PCB_TOP_Z - 0.1)
    obj.data.materials.append(_hole_material())


def add_pad(x, y, w, l, rotation_z_deg=0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co.x *= w / 2
        v.co.y *= l / 2
        v.co.z *= 0.05
    m = bpy.data.meshes.new("pad")
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new("pad", m)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, PCB_TOP_Z + 0.05)
    obj.rotation_euler = (0, 0, math.radians(rotation_z_deg))
    obj.data.materials.append(_pad_material())


def add_silkscreen_outline(x, y, w, l, rotation_z_deg=0):
    """Thin white rectangle outline showing component footprint area."""
    # Create as 4 thin strips around the perimeter
    thick = 0.25
    bm = bmesh.new()
    # outer rectangle
    outer = bmesh.ops.create_cube(bm, size=1)["verts"]
    for v in outer:
        v.co.x *= (w + thick) / 2
        v.co.y *= (l + thick) / 2
        v.co.z *= 0.04
    # cut hole in middle by making it a rectangle ring — easier: just make 4 strips
    bm.free()
    # Use 4 rectangles along the edges instead
    for dx, dy, dw, dl in [(0, l/2, w + thick, thick),
                           (0, -l/2, w + thick, thick),
                           (w/2, 0, thick, l - thick),
                           (-w/2, 0, thick, l - thick)]:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1)
        for v in bm.verts:
            v.co.x *= dw / 2
            v.co.y *= dl / 2
            v.co.z *= 0.04
        cosr = math.cos(math.radians(rotation_z_deg))
        sinr = math.sin(math.radians(rotation_z_deg))
        wx = dx * cosr - dy * sinr
        wy = dx * sinr + dy * cosr
        m = bpy.data.meshes.new("silk")
        bm.to_mesh(m); bm.free()
        obj = bpy.data.objects.new("silk", m)
        bpy.context.collection.objects.link(obj)
        obj.location = (x + wx, y + wy, PCB_TOP_Z + 0.04)
        obj.rotation_euler = (0, 0, math.radians(rotation_z_deg))
        obj.data.materials.append(_silk_material())


def draw_footprint(obj_file, x, y, rotation_z_deg):
    """Place through-holes / SMD pads / silkscreen for a component package."""
    name_lc = obj_file.lower()
    cosr = math.cos(math.radians(rotation_z_deg))
    sinr = math.sin(math.radians(rotation_z_deg))
    def at(dx, dy):
        return (x + dx * cosr - dy * sinr, y + dx * sinr + dy * cosr)

    if "dip-8" in name_lc:
        for side in (-1, 1):
            for i in range(4):
                add_hole(*at(side * 3.81, (i - 1.5) * 2.54))
        add_silkscreen_outline(x, y, 6.4, 9.4, rotation_z_deg)
    elif "jst_b3b" in name_lc:
        for i in range(3):
            add_hole(*at((i - 1) * 2.5, 0))
        add_silkscreen_outline(x, y, 8, 6, rotation_z_deg)
    elif "jst_b6b" in name_lc:
        for i in range(6):
            add_hole(*at((i - 2.5) * 2.5, 0))
        add_silkscreen_outline(x, y, 16, 6, rotation_z_deg)
    elif "header_1x04" in name_lc:
        for i in range(4):
            add_hole(*at((i - 1.5) * 2.54, 0))
    elif "tactile" in name_lc:
        for sx in (-1, 1):
            for sy in (-1, 1):
                add_hole(*at(sx * 3.25, sy * 2.25), radius=0.45)
        add_silkscreen_outline(x, y, 6.0, 6.0, rotation_z_deg)
    elif "to-92" in name_lc or "2n7000" in name_lc:
        for i in range(3):
            add_hole(*at((i - 1) * 1.27, 0))
    elif "470uf" in name_lc or "electrolytic" in name_lc:
        for i in range(2):
            add_hole(*at((i - 0.5) * 5, 0), radius=0.8)
    elif "ws2812" in name_lc:
        for sx, sy in [(-1.6, -0.8), (1.6, -0.8), (1.6, 0.8), (-1.6, 0.8)]:
            add_pad(*at(sx, sy), 0.8, 0.8, rotation_z_deg)
        add_silkscreen_outline(x, y, 5.4, 5.4, rotation_z_deg)
    elif "ams1117" in name_lc or "sot-223" in name_lc:
        for i in range(3):
            add_pad(*at((i - 1) * 2.3, -1.6), 1.0, 1.5, rotation_z_deg)
        add_pad(*at(0, 1.6), 3.5, 1.7, rotation_z_deg)
    elif "ss34" in name_lc or "_sma" in name_lc:
        for i in (-1, 1):
            add_pad(*at(i * 2.4, 0), 1.6, 1.7, rotation_z_deg)
    elif "resistor_0805" in name_lc or "cap_ceramic_0805" in name_lc:
        for i in (-1, 1):
            add_pad(*at(i * 1.0, 0), 1.0, 1.4, rotation_z_deg)
    elif "fpc" in name_lc:
        for i in range(24):
            add_pad(*at((i - 11.5) * 0.5, 0), 0.3, 1.2, rotation_z_deg)
        add_silkscreen_outline(x, y, 14, 7, rotation_z_deg)
    elif "esp32" in name_lc:
        for side in (-1, 1):
            for i in range(16):
                add_pad(*at(side * 9, (i - 7.5) * 1.27), 0.9, 0.65, rotation_z_deg)
        for i in range(8):
            add_pad(*at((i - 3.5) * 1.27, -12.75), 0.65, 0.9, rotation_z_deg)
        add_silkscreen_outline(x, y, 18.5, 26.0, rotation_z_deg)
    elif "usb" in name_lc:
        for sx, sy in [(-4.5, -3.5), (4.5, -3.5), (-4.5, 3.5), (4.5, 3.5)]:
            add_hole(*at(sx, sy), radius=0.7)
        for i in range(16):
            add_pad(*at(0, (i - 7.5) * 0.5), 0.3, 1.0, rotation_z_deg)
        add_silkscreen_outline(x, y, 9, 8, rotation_z_deg)


def import_obj_at(obj_file, x, y, z, rot_z_deg, label):
    """Import OBJ, place at (x,y,z) mm with Z rotation, name it, return the joined object."""
    path = os.path.join(MESHES, obj_file)
    if not os.path.exists(path):
        print(f"  !! missing: {path}", file=sys.stderr)
        return None
    bpy.ops.wm.obj_import(filepath=path, use_split_groups=True)
    new_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.name.startswith(("PCB", "Floor"))]
    new_objs = [o for o in new_objs if not o.get("placed")]
    if not new_objs:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    for o in new_objs: o.select_set(True)
    bpy.context.view_layer.objects.active = new_objs[0]
    if len(new_objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = f"{label}_{obj.name}"
    obj["placed"] = True

    # Apply uniform per-part body material (overrides default mtl gray)
    mat = get_mat(obj_file)
    obj.data.materials.clear()
    obj.data.materials.append(mat)

    # Step 1: lay flat (smallest dim → Z), bake into mesh
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    bb = [Vector(c) for c in obj.bound_box]   # local coords, identity matrix
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    size = mx - mn
    dims = [size.x, size.y, size.z]
    smallest = dims.index(min(dims))
    if smallest == 0:
        obj.rotation_euler = (0, math.pi/2, 0)
    elif smallest == 1:
        obj.rotation_euler = (math.pi/2, 0, 0)
    bpy.context.view_layer.update()
    # bake the flattening rotation into the mesh data so bound_box reflects it
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(rotation=True, scale=False, location=False)
    # now apply only the Z spin, leave on rotation_euler (cheap, won't affect bbox much)
    obj.rotation_euler = (0, 0, math.radians(rot_z_deg))
    bpy.context.view_layer.update()

    # Step 2: get post-rotation world bbox, then translate so bbox center → target
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    cx = (mn.x + mx.x) / 2
    cy = (mn.y + mx.y) / 2
    bottom_z_offset = mn.z
    obj.location = Vector((x - cx, y - cy, z - bottom_z_offset))
    bpy.context.view_layer.update()
    bb2 = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mx_z = max(v.z for v in bb2)
    add_label(label, x, y, mx_z)
    return obj


# ─── PCB plane ───
pcb_w, pcb_h, pcb_t = 70, 50, 1.6  # mm
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co.x *= pcb_w / 2
    v.co.y *= pcb_h / 2
    v.co.z *= pcb_t / 2
pcb_mesh = bpy.data.meshes.new("PCB")
bm.to_mesh(pcb_mesh); bm.free()
pcb = bpy.data.objects.new("PCB", pcb_mesh)
bpy.context.collection.objects.link(pcb)
pcb.location = (4, 0, -pcb_t / 2)  # board centered roughly under ESP32

pcb_mat = bpy.data.materials.new("PCB_Green")
pcb_mat.use_nodes = True
b = pcb_mat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.05, 0.30, 0.10, 1)
b.inputs["Roughness"].default_value = 0.55
pcb.data.materials.append(pcb_mat)

def in_phase(label):
    if PHASE_NUM is None:
        return True
    return PHASE_MAP.get(label, 99) <= PHASE_NUM


def explode_z_offset(label):
    """For exploded view: Z offset based on assembly phase — later phase = higher in stack."""
    if MODE != "exploded":
        return 0
    phase = PHASE_MAP.get(label, 4)
    # Phase 1 = lowest, phase 7/8 = highest
    return phase * 8.0


def add_drop_line(label, x, y, z_top):
    """In exploded mode, draw a thin dashed-look line from PCB up to the lifted component."""
    if MODE != "exploded":
        return
    cd = bpy.data.curves.new(f"drop_{label}", type='CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = 0.15
    cd.bevel_resolution = 2
    sp = cd.splines.new('POLY')
    sp.points.add(1)
    sp.points[0].co = (x, y, 0, 1)
    sp.points[1].co = (x, y, z_top - 1, 1)
    obj = bpy.data.objects.new(f"drop_{label}", cd)
    bpy.context.collection.objects.link(obj)
    mat = bpy.data.materials.new(f"M_drop_{label}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.20, 1)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.85, 0.85, 0.20, 1)
            bsdf.inputs["Emission Strength"].default_value = 1.0
    obj.data.materials.append(mat)

# Always draw ALL footprints first — they're the "permanent" PCB markings,
# they don't depend on which components are installed yet.
for entry in COMPONENTS:
    ofile, x, y, z, rotz, label = entry
    draw_footprint(ofile, x, y, rotz)
for x, y, label in RESISTORS:
    draw_footprint("Resistor_0805.obj", x, y, 0)
for x, y, label in CAPS:
    draw_footprint("Cap_ceramic_0805.obj", x, y, 0)

# Then place only the components that fall within the current phase
placed_count = 0
for entry in COMPONENTS:
    ofile, x, y, z, rotz, label = entry
    if in_phase(label):
        z_off = explode_z_offset(label)
        obj = import_obj_at(ofile, x, y, z + z_off, rotz, label)
        if obj is not None and MODE == "exploded":
            add_drop_line(label, x, y, z + z_off)
        placed_count += 1

for x, y, label in RESISTORS:
    if in_phase(label):
        z_off = explode_z_offset(label)
        obj = import_obj_at("Resistor_0805.obj", x, y, z_off, 0, label)
        if obj is not None and MODE == "exploded":
            add_drop_line(label, x, y, z_off)
        placed_count += 1

for x, y, label in CAPS:
    if in_phase(label):
        z_off = explode_z_offset(label)
        obj = import_obj_at("Cap_ceramic_0805.obj", x, y, z_off, 0, label)
        if obj is not None and MODE == "exploded":
            add_drop_line(label, x, y, z_off)
        placed_count += 1

print(f"Placed {placed_count} components (mode={MODE})", file=sys.stderr)


# ─── wire colors per binder Section 4 ───
WIRE_COLORS = {
    "RED":    (0.92, 0.10, 0.06),
    "BLACK":  (0.05, 0.05, 0.06),
    "GREEN":  (0.10, 0.78, 0.18),
    "BLUE":   (0.10, 0.30, 0.92),
    "WHITE":  (0.92, 0.92, 0.92),
    "YELLOW": (0.95, 0.85, 0.10),
}


def wire_material(color_name):
    cache_key = f"wire_{color_name}"
    if cache_key in bpy.data.materials:
        return bpy.data.materials[cache_key]
    rgb = WIRE_COLORS[color_name]
    mat = bpy.data.materials.new(cache_key)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1)
        bsdf.inputs["Roughness"].default_value = 0.5
    return mat


def add_wire(start, end, color_name, sag=8.0, name="wire"):
    """Draw a curved wire from start to end with realistic sag in -Z."""
    cd = bpy.data.curves.new(name, type='CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = 0.55
    cd.bevel_resolution = 6
    cd.use_fill_caps = True
    sp = cd.splines.new('BEZIER')
    sp.bezier_points.add(2)  # 3 control points: start, mid, end
    s, e = Vector(start), Vector(end)
    mid = (s + e) / 2
    mid.z -= sag
    sp.bezier_points[0].co = s
    sp.bezier_points[0].handle_left_type = 'AUTO'
    sp.bezier_points[0].handle_right_type = 'AUTO'
    sp.bezier_points[1].co = mid
    sp.bezier_points[1].handle_left_type = 'AUTO'
    sp.bezier_points[1].handle_right_type = 'AUTO'
    sp.bezier_points[2].co = e
    sp.bezier_points[2].handle_left_type = 'AUTO'
    sp.bezier_points[2].handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, cd)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(wire_material(color_name))
    return obj


def add_box(name, size, location, color, rotation_z_deg=0, roughness=0.55, metallic=0.0):
    """Quick rectangular placeholder for photo-modeled parts."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    sx, sy, sz = size
    for v in bm.verts:
        v.co.x *= sx / 2
        v.co.y *= sy / 2
        v.co.z *= sz / 2
    m = bpy.data.meshes.new(name)
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new(name, m)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (0, 0, math.radians(rotation_z_deg))
    mat = bpy.data.materials.new(f"M_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    obj.data.materials.append(mat)
    return obj


def add_cylinder(name, radius, length, location, axis='X', color=(0.45, 0.45, 0.5)):
    from mathutils import Matrix
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=32, radius1=radius, radius2=radius, depth=length, cap_ends=True)
    if axis == 'X':
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.pi/2, 3, 'Y'))
    elif axis == 'Y':
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.pi/2, 3, 'X'))
    m = bpy.data.meshes.new(name)
    bm.to_mesh(m); bm.free()
    obj = bpy.data.objects.new(name, m)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    mat = bpy.data.materials.new(f"M_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = 0.4
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.7
    obj.data.materials.append(mat)
    return obj


# ─── external components + wiring (only shown in wiring mode) ───
if MODE == "wiring":
    # Laser module: cylindrical body offset to right of board
    laser_pos = (75, -25, 8)
    add_cylinder("Laser_4060-530D-200", radius=8, length=50, location=laser_pos, axis='X',
                 color=(0.20, 0.21, 0.25))
    add_label("Laser Module", laser_pos[0], laser_pos[1], laser_pos[2] + 12)

    # Galvo set: driver board + 2 galvo motors
    drv_pos = (75, 20, 14)
    add_box("Galvo_Driver", (50, 80, 28), drv_pos, color=(0.12, 0.45, 0.18), roughness=0.5)
    add_label("Galvo Driver", drv_pos[0], drv_pos[1], drv_pos[2] + 18)
    # Two galvo motor cans on top of the driver
    add_cylinder("Galvo_X", radius=10, length=30, location=(60, 5, 38), axis='X',
                 color=(0.30, 0.30, 0.32))
    add_cylinder("Galvo_Y", radius=10, length=30, location=(60, 35, 38), axis='Y',
                 color=(0.30, 0.30, 0.32))

    # OV5640 camera: long thin PCB above the board (connected via FPC ribbon)
    cam_pos = (14, 60, 8)
    add_box("OV5640_Camera", (14, 70, 1.6), cam_pos, color=(0.08, 0.32, 0.10))
    add_box("OV5640_Lens", (12, 12, 12), (14, 60, 16), color=(0.05, 0.05, 0.05))
    add_label("Camera (OV5640)", cam_pos[0], cam_pos[1] + 10, cam_pos[2] + 14)

    # Microswitch (lid interlock) — using a simple box; the real STEP is in models/manual/switches/
    sw_pos = (-25, 30, 4)
    add_box("Microswitch_SW3", (12, 6, 6), sw_pos, color=(0.08, 0.08, 0.10))
    add_label("SW3 Lid Switch", sw_pos[0], sw_pos[1], sw_pos[2] + 8)

    # USB-C PD trigger board (replaces former barrel jack J1)
    pd_pos = (-50, 0, 2)
    add_box("PD_Trigger", (15, 31, 4), pd_pos, color=(0.10, 0.45, 0.18))
    add_label("USB-C PD Trigger", pd_pos[0], pd_pos[1], pd_pos[2] + 6)

    # ─── wires ───
    # Helpful short aliases for connector pin coords on the PCB:
    # J3 (3-pin laser) at world (28, -10, 0) — pins along Y, top of connector at z≈8
    j3 = lambda i: (28 + (i - 1) * 2.5 - 2.5, -10, 6)   # pins spread in X
    # J4 (6-pin galvo) at (28, 5, 0)
    j4 = lambda i: (28 + (i - 1) * 2.5 - 6, 5, 6)
    # J5 FPC at (14, 16, 0) — ribbon exits in +Y direction
    j5_exit = (14, 18, 5)
    # SW3 pads (placed at left side of PCB near R15 area)
    sw3_pad_a = (-15, -10, 1)
    sw3_pad_b = (-15, -12, 1)
    # PD output to power input (the ex-barrel-jack location)
    pd_out_12v = (-22, -2, 1)
    pd_out_gnd = (-22,  2, 1)

    # Laser wires (J3): RED (+12V) → laser+, GREEN (TTL) → laser TTL, BLACK (GND) → laser-
    laser_in = (60, -25, 6)   # back end of laser cylinder
    add_wire(j3(1), (laser_in[0], laser_in[1] - 2, laser_in[2]), "RED",   sag=2, name="W_J3_RED")
    add_wire(j3(2), (laser_in[0], laser_in[1],     laser_in[2]), "GREEN", sag=2, name="W_J3_GREEN")
    add_wire(j3(3), (laser_in[0], laser_in[1] + 2, laser_in[2]), "BLACK", sag=2, name="W_J3_BLACK")

    # Galvo driver wires (J4): pins 1-4 BLUE, pin 5 RED, pin 6 BLACK
    drv_in = (50, 20, 14)
    for i in range(1, 5):
        add_wire(j4(i), (drv_in[0], drv_in[1] + (i - 2.5) * 3, drv_in[2]),
                 "BLUE", sag=2, name=f"W_J4_BLUE{i}")
    add_wire(j4(5), (drv_in[0], drv_in[1] + 8, drv_in[2]), "RED",   sag=2, name="W_J4_RED")
    add_wire(j4(6), (drv_in[0], drv_in[1] - 8, drv_in[2]), "BLACK", sag=2, name="W_J4_BLACK")

    # FPC ribbon to camera — flat tan ribbon, modeled as thicker stiffer "wire"
    add_wire(j5_exit, (cam_pos[0], cam_pos[1] - 35, cam_pos[2]), "YELLOW",
             sag=1, name="W_J5_FPC")

    # Microswitch wires: GREEN (digital safety signal) + BLACK (GND)
    add_wire(sw3_pad_a, (sw_pos[0] + 3, sw_pos[1], sw_pos[2]), "GREEN", sag=4, name="W_SW3_GREEN")
    add_wire(sw3_pad_b, (sw_pos[0] + 3, sw_pos[1] - 2, sw_pos[2]), "BLACK", sag=4, name="W_SW3_BLACK")

    # PD trigger output wires to PCB power input (RED 12V + BLACK GND)
    add_wire((pd_pos[0] + 8, pd_pos[1], pd_pos[2] + 2), pd_out_12v, "RED",   sag=2, name="W_PD_RED")
    add_wire((pd_pos[0] + 8, pd_pos[1] + 2, pd_pos[2] + 2), pd_out_gnd, "BLACK", sag=2, name="W_PD_BLACK")


# ─── camera + lights for assembly hero shot ───
diag = math.sqrt(pcb_w**2 + pcb_h**2)

cam_data = bpy.data.cameras.new("Cam")
if MODE == "exploded":
    # Perspective at 3/4 angle so we can see the layered stack
    cam_data.type = 'PERSP'
    cam_data.lens = 55
    cam_loc = (60, -90, 75)
    cam_target = Vector((4, 0, 30))
elif MODE == "wiring":
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 200
    cam_loc = (10, 0, 200)
    cam_target = Vector((10, 10, 0))
else:
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 90
    cam_loc = (4, -25, 80)
    cam_target = Vector((4, 0, 0))
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = cam_loc
direction = cam_target - cam.location
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
add_area("Back", (  4,       diag*1.2, diag),    4000)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.angle = math.radians(8)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(40), math.radians(20), math.radians(45))
bpy.context.collection.objects.link(sun)

# World
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.82, 0.83, 0.85, 1)
    bg.inputs[1].default_value = 0.6

# Floor
floor_m = bpy.data.meshes.new("FloorM")
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=diag * 3)
bm.to_mesh(floor_m); bm.free()
floor = bpy.data.objects.new("Floor", floor_m)
bpy.context.collection.objects.link(floor)
floor.location.z = -pcb_t - 0.5
fmat = bpy.data.materials.new("FMat")
fmat.use_nodes = True
fb = fmat.node_tree.nodes.get("Principled BSDF")
fb.inputs["Base Color"].default_value = (0.92, 0.92, 0.93, 1)
fb.inputs["Roughness"].default_value = 0.85
floor.data.materials.append(fmat)

# Render
scene = bpy.context.scene
engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
scene.render.resolution_x = 2400
scene.render.resolution_y = 1800
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = png_path

bpy.ops.render.render(write_still=True)
print(f"  -> {png_path}", file=sys.stderr)
