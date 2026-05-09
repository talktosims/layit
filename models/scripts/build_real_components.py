"""
Build dimensional GLBs for LayIt Laser bench-build components from
manufacturer mechanical drawings (datasheet_parametric accuracy).

Run:
    blender --background --python build_real_components.py -- [out_dir]

Each function builds one component centered at world origin, axis-aligned,
in millimeters; the export step rescales mm->m for glTF and exports a
single .glb per component.

Source citations live next to each function.
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
OUT_DIR = argv[0] if argv else "/Users/Sims/Desktop/expandit/products/layit/models"
os.makedirs(OUT_DIR, exist_ok=True)


# -----------------------------------------------------------------------------
# Scene / material helpers
# -----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                  bpy.data.lights, bpy.data.objects):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_mat(name, base_color, roughness=0.5, metallic=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission is not None and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 1.0
    return m


# Material palette ------------------------------------------------------------
def palette():
    return {
        # IC packages
        "ic_epoxy":        make_mat("IC_Epoxy_Black",       (0.025, 0.025, 0.030), roughness=0.55, metallic=0.0),
        "ic_silkscreen":   make_mat("IC_Silkscreen_White",  (0.85, 0.85, 0.86),    roughness=0.7,  metallic=0.0),
        "lead_tin":        make_mat("Lead_Tin",             (0.78, 0.79, 0.82),    roughness=0.30, metallic=1.0),
        # Discrete packages
        "to92_epoxy":      make_mat("TO92_Epoxy_Black",     (0.030, 0.030, 0.035), roughness=0.62, metallic=0.0),
        # SMD passives
        "resistor_body":   make_mat("Resistor_0805_Body",   (0.035, 0.035, 0.045), roughness=0.55, metallic=0.0),
        "resistor_top":    make_mat("Resistor_0805_Top",    (0.040, 0.045, 0.060), roughness=0.50, metallic=0.0),
        "resistor_term":   make_mat("Resistor_0805_Term",   (0.85, 0.86, 0.88),    roughness=0.30, metallic=1.0),
        "cap_mlcc":        make_mat("Cap_0805_MLCC_Tan",    (0.78, 0.62, 0.30),    roughness=0.45, metallic=0.0),
        # PCBs
        "pcb_adafruit":    make_mat("PCB_Adafruit_Black",   (0.04, 0.04, 0.05),    roughness=0.45, metallic=0.0),
        "pcb_gy521":       make_mat("PCB_GY521_Blue",       (0.04, 0.18, 0.40),    roughness=0.45, metallic=0.0),
        "pcb_espressif":   make_mat("PCB_Espressif_Black",  (0.05, 0.05, 0.06),    roughness=0.5,  metallic=0.0),
        "silkscreen_white": make_mat("Silkscreen_White",    (0.88, 0.88, 0.89),    roughness=0.7),
        "pcb_pad_gold":    make_mat("PCB_Pad_Gold",         (0.95, 0.78, 0.36),    roughness=0.30, metallic=1.0),
        # Header pins / pin rows
        "header_plastic":  make_mat("Header_Plastic_Black", (0.025, 0.025, 0.030), roughness=0.7,  metallic=0.0),
        "header_pin":      make_mat("Header_Pin_Gold",      (0.95, 0.78, 0.36),    roughness=0.20, metallic=1.0),
        # ESP32 specifics
        "rf_shield":       make_mat("RF_Shield_Tin",        (0.78, 0.79, 0.82),    roughness=0.32, metallic=1.0),
        "antenna_trace":   make_mat("Antenna_Trace_Gold",   (0.92, 0.78, 0.42),    roughness=0.25, metallic=1.0),
        "usbc_metal":      make_mat("USBC_Shell",           (0.80, 0.80, 0.83),    roughness=0.30, metallic=1.0),
        "usbc_insert":     make_mat("USBC_Insert_White",    (0.88, 0.88, 0.89),    roughness=0.70, metallic=0.0),
        "tactile_button":  make_mat("Tactile_Button_Black", (0.04, 0.04, 0.05),    roughness=0.45, metallic=0.0),
        "led_red":         make_mat("LED_Red",              (0.85, 0.10, 0.05),    roughness=0.20, metallic=0.0, emission=(0.6, 0.05, 0.02)),
        # MPU6050 module
        "qfn_chip":        make_mat("QFN_Chip_Black",       (0.030, 0.030, 0.035), roughness=0.55, metallic=0.0),
    }


# -----------------------------------------------------------------------------
# Geometry primitives
# -----------------------------------------------------------------------------
def add_box(name, sx, sy, sz, loc=(0, 0, 0), bevel=0.0, mat=None):
    """Add a box centered at loc with full size sx,sy,sz (mm)."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    if bevel > 0:
        m = o.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        bpy.ops.object.modifier_apply(modifier=m.name)
    if mat:
        o.data.materials.append(mat)
    return o


def add_cyl(name, r, h, loc=(0, 0, 0), axis='Z', mat=None, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    if axis == 'X':
        o.rotation_euler = (0, math.pi / 2, 0)
        bpy.ops.object.transform_apply(rotation=True)
    elif axis == 'Y':
        o.rotation_euler = (math.pi / 2, 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
    if mat:
        o.data.materials.append(mat)
    return o


def add_lead(name, length, width=0.4, thickness=0.25, bend_at=None, loc=(0, 0, 0), mat=None):
    """Through-hole lead, oriented along -Z (lead points downward by default).
    bend_at: if provided, lead is straight for `bend_at` mm then bends 90deg
             to extend horizontally. We approximate as L-shape.
    """
    if bend_at is None:
        b = add_box(name, width, thickness, length, loc=loc, mat=mat)
        return b
    # L-shape: vertical segment + horizontal segment (joined)
    vert = add_box(f"{name}_v", width, thickness, bend_at,
                   loc=(loc[0], loc[1], loc[2] - bend_at / 2), mat=mat)
    horiz_len = max(length - bend_at, 1.0)
    horiz = add_box(f"{name}_h", width, thickness, thickness,
                    loc=(loc[0], loc[1], loc[2] - bend_at - thickness / 2), mat=mat)
    horiz.scale = (1, 1, 1)
    horiz.dimensions = (horiz_len, thickness, thickness)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.select_all(action='DESELECT')
    vert.select_set(True)
    horiz.select_set(True)
    bpy.context.view_layer.objects.active = vert
    bpy.ops.object.join()
    vert.name = name
    return vert


# -----------------------------------------------------------------------------
# Components
# -----------------------------------------------------------------------------
def build_dip8(label_text, var_name):
    """
    PDIP-8 body and leads, JEDEC MS-001 / Microchip / TI dimensions.
    Body (excluding leads): 9.27 x 6.35 x 3.30 mm
    Lead pitch: 2.54 mm, row spacing (eB): 7.62 mm
    Lead L: 3.30 mm (below body), insertion: ~3.30 mm
    Pin 1: notch + dot on top
    Sources:
      - Microchip MCP4822 DS22249, 8-Lead PDIP package drawing C04-018
      - TI TL072 (TL072CP) PDIP-8 package P0008
    """
    pal = palette()
    objs = []

    body_w, body_d, body_h = 9.27, 6.35, 3.30
    # Body (epoxy block) — slight bevel
    body = add_box(f"{var_name}_body", body_w, body_d, body_h,
                   loc=(0, 0, body_h / 2), bevel=0.18, mat=pal["ic_epoxy"])
    objs.append(body)

    # Pin-1 dimple (small inset cylinder near corner, top face)
    dimple = add_cyl(f"{var_name}_pin1_dimple", r=0.5, h=0.35,
                     loc=(-body_w / 2 + 1.4, -body_d / 2 + 1.4, body_h - 0.05),
                     mat=pal["ic_epoxy"])
    objs.append(dimple)

    # Pin-1 notch (half-cylinder cut at edge — model as small box, additive look)
    notch = add_cyl(f"{var_name}_notch", r=0.85, h=0.40,
                    loc=(-body_w / 2 + 0.85, 0, body_h - 0.05),
                    mat=pal["ic_epoxy"], verts=24)
    objs.append(notch)

    # Silkscreen label rectangle on top (slightly raised)
    label_thickness = 0.02
    label = add_box(f"{var_name}_label", body_w * 0.55, body_d * 0.45, label_thickness,
                    loc=(0.4, 0.2, body_h + label_thickness / 2),
                    mat=pal["ic_silkscreen"])
    objs.append(label)

    # Leads — 4 per side, pitch 2.54, row spacing 7.62
    pitch = 2.54
    row = 7.62
    lead_w, lead_t, lead_h = 0.45, 0.25, 3.10
    pin_below = lead_h
    for side in (-1, 1):
        x = side * row / 2
        for i in range(4):
            y = (i - 1.5) * pitch
            # Shoulder where lead exits body
            shoulder = add_box(f"{var_name}_shoulder_{side}_{i}",
                               (row - body_w) / 2 + 0.2, lead_w, lead_t,
                               loc=(side * (body_w / 2 + ((row - body_w) / 4)),
                                    y, body_h * 0.25),
                               mat=pal["lead_tin"])
            objs.append(shoulder)
            # Vertical pin going down through-hole style
            pin = add_box(f"{var_name}_lead_{side}_{i}", lead_w, lead_t, pin_below + 0.5,
                          loc=(x, y, -pin_below / 2 + 0.25),
                          mat=pal["lead_tin"])
            objs.append(pin)

    return objs


def build_2n7000_to92():
    """
    2N7000 TO-92 (TO-226-3 case).
    Body cross-section: 4.50 mm flat side x 3.80 mm depth; height 5.20 mm.
    Leads: 14.50 mm long, 1.27 mm pitch (0.05"), 0.45 x 0.45 mm cross-section.
    Pin order (flat facing you, leads down, left-to-right): D, G, S (2N7000).
    Source: Onsemi 2N7000 datasheet / TO-226-3 mech drawing.
    """
    pal = palette()
    objs = []

    body_w = 4.50
    body_d_flat = 3.80   # depth on the rounded side
    body_h = 5.20

    # Build the rounded D shape: a cylinder sliced flat.
    # Approx: a half-cylinder (radius = body_w/2) + a flat slab at the front.
    # Implement as cylinder with a box subtracting half — simpler: use a cylinder
    # of radius body_w/2 (which gives a 4.5-diam body) and a box that flattens it.
    # Easier still: a cylinder half + a thin slab to face flat on one side.
    radius = body_w / 2
    rear = add_cyl("Q1_body_rear", r=radius, h=body_h,
                   loc=(0, 0, body_h / 2), mat=pal["to92_epoxy"], verts=32)
    objs.append(rear)
    # Small flat front face by adding a box on the flat side (the JEDEC TO-92 flat).
    flat_thickness = body_d_flat - radius
    if flat_thickness > 0:
        front_flat = add_box("Q1_body_flat", body_w, flat_thickness, body_h,
                             loc=(0, -radius - flat_thickness / 2 + 0.001, body_h / 2),
                             mat=pal["to92_epoxy"])
        objs.append(front_flat)

    # Leads: 3 leads, pitch 1.27 mm centered on x, exiting bottom of body.
    pitch = 1.27
    lead_w = 0.45
    lead_d = 0.45
    lead_len = 14.50
    for i, name in enumerate(("D", "G", "S")):
        x = (i - 1) * pitch
        lead = add_box(f"Q1_lead_{name}", lead_w, lead_d, lead_len,
                       loc=(x, 0, -lead_len / 2),
                       mat=pal["lead_tin"])
        objs.append(lead)
    return objs


def build_resistor_0805(label="R"):
    """
    0805 chip resistor, IPC SMD-A footprint dims.
    Body: 2.00 x 1.25 x 0.55 mm (0.5-0.6 typical).
    Terminations: 0.40 mm wide on each end, full body height.
    Top: thin layer with white text (we model the top as a separate
    shell with the silkscreen color baked into a small inset).
    """
    pal = palette()
    objs = []
    body_l, body_w, body_h = 2.00, 1.25, 0.55
    term_w = 0.40

    # Black ceramic body
    body = add_box("R_body", body_l, body_w, body_h,
                   loc=(0, 0, body_h / 2), bevel=0.04, mat=pal["resistor_body"])
    objs.append(body)
    # Top inset — slightly raised plate for the resistor value silkscreen
    top = add_box("R_top", body_l - 0.20, body_w - 0.10, 0.04,
                  loc=(0, 0, body_h + 0.02), mat=pal["resistor_top"])
    objs.append(top)
    # Terminations (silver tin) on both ends
    for side in (-1, 1):
        tx = side * (body_l / 2 - term_w / 2)
        term = add_box(f"R_term_{'L' if side<0 else 'R'}",
                       term_w, body_w + 0.04, body_h + 0.04,
                       loc=(tx, 0, body_h / 2), bevel=0.02,
                       mat=pal["resistor_term"])
        objs.append(term)
    return objs


def build_cap_0805():
    """0805 ceramic MLCC. Body 2.0 x 1.25 x 0.50 mm typical X7R. Tan body."""
    pal = palette()
    objs = []
    body_l, body_w, body_h = 2.00, 1.25, 0.50
    term_w = 0.40

    body = add_box("C_body", body_l, body_w, body_h,
                   loc=(0, 0, body_h / 2), bevel=0.04, mat=pal["cap_mlcc"])
    objs.append(body)
    for side in (-1, 1):
        tx = side * (body_l / 2 - term_w / 2)
        term = add_box(f"C_term_{'L' if side<0 else 'R'}",
                       term_w, body_w + 0.04, body_h + 0.04,
                       loc=(tx, 0, body_h / 2), bevel=0.02,
                       mat=pal["resistor_term"])
        objs.append(term)
    return objs


def build_lm4040_adafruit2200():
    """
    Adafruit LM4040 Voltage Reference Breakout (PRD 2200).
    PCB: 16.51 x 10.16 x 1.6 mm (0.65" x 0.4"), classic Adafruit black.
    Header pin row: 5 pins on the long edge, 2.54 mm pitch, 0.64 mm sq pin.
    Onboard parts: 1x SOT-23-3 LM4040 IC, 1-2x 0805 decoupling caps.
    Source: Adafruit PRD 2200 product page mechanical (EagleCAD).
    """
    pal = palette()
    objs = []
    pcb_l, pcb_w, pcb_t = 16.51, 10.16, 1.60

    pcb = add_box("LM4040_PCB", pcb_l, pcb_w, pcb_t,
                  loc=(0, 0, pcb_t / 2), bevel=0.10, mat=pal["pcb_adafruit"])
    objs.append(pcb)
    # 4 mounting-hole annular rings (just gold dots)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ring = add_cyl(f"LM4040_pad_{sx}_{sy}", r=1.0, h=0.05,
                           loc=(sx * (pcb_l / 2 - 1.6), sy * (pcb_w / 2 - 1.6),
                                pcb_t + 0.01),
                           mat=pal["pcb_pad_gold"])
            objs.append(ring)
    # Header pin row, 5 pins on long edge
    pin_pitch = 2.54
    pin_count = 5
    pin_w = 0.64
    pin_total_h = 11.5  # pin sticks down 8mm + plastic 2.5mm + above-plastic stub
    plastic_h = 2.50
    # Header plastic strip
    strip = add_box("LM4040_header_plastic",
                    pin_pitch * pin_count, 2.54, plastic_h,
                    loc=(0, -pcb_w / 2 + 1.27, pcb_t + plastic_h / 2),
                    mat=pal["header_plastic"])
    objs.append(strip)
    for i in range(pin_count):
        x = (i - (pin_count - 1) / 2) * pin_pitch
        # Pin above plastic
        above = add_box(f"LM4040_pin_above_{i}", pin_w, pin_w, 6.0,
                        loc=(x, -pcb_w / 2 + 1.27, pcb_t + plastic_h + 3.0),
                        mat=pal["header_pin"])
        objs.append(above)
        # Pin below PCB
        below = add_box(f"LM4040_pin_below_{i}", pin_w, pin_w, 3.0,
                        loc=(x, -pcb_w / 2 + 1.27, -1.5),
                        mat=pal["header_pin"])
        objs.append(below)
    # SOT-23-3 IC (LM4040)
    ic = add_box("LM4040_IC_SOT23", 2.90, 1.30, 1.10,
                 loc=(2.0, 1.2, pcb_t + 0.55), bevel=0.05, mat=pal["ic_epoxy"])
    objs.append(ic)
    # 2x 0805 decoupling caps on top
    for i, x in enumerate((-3.5, -1.5)):
        cap = add_box(f"LM4040_C{i}", 2.0, 1.25, 0.50,
                      loc=(x, 1.5, pcb_t + 0.25), mat=pal["cap_mlcc"])
        objs.append(cap)
    # Silkscreen ID block (small white rectangle near header)
    silk = add_box("LM4040_silk", 6.0, 1.2, 0.02,
                   loc=(-3.0, -2.5, pcb_t + 0.011),
                   mat=pal["silkscreen_white"])
    objs.append(silk)
    return objs


def build_mpu6050_gy521():
    """
    MPU6050 GY-521 module (very common clone).
    PCB: 21.2 x 15.8 x 1.6 mm, blue.
    Header: 8-pin 0.1" single row, soldered on long edge.
    Center IC: MPU-6050 in QFN-24 (4.0 x 4.0 x 0.9 mm).
    Source: GY-521 module reference (multiple identical clone listings).
    """
    pal = palette()
    objs = []
    pcb_l, pcb_w, pcb_t = 21.2, 15.8, 1.6

    pcb = add_box("MPU_PCB", pcb_l, pcb_w, pcb_t,
                  loc=(0, 0, pcb_t / 2), bevel=0.10, mat=pal["pcb_gy521"])
    objs.append(pcb)
    # Mounting holes (just gold rings; 4 corners)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ring = add_cyl(f"MPU_pad_{sx}_{sy}", r=1.4, h=0.05,
                           loc=(sx * (pcb_l / 2 - 2.5), sy * (pcb_w / 2 - 2.5),
                                pcb_t + 0.01),
                           mat=pal["pcb_pad_gold"])
            objs.append(ring)
    # Center MPU-6050 QFN
    qfn = add_box("MPU_chip", 4.0, 4.0, 0.95,
                  loc=(0, 0, pcb_t + 0.475), bevel=0.05, mat=pal["qfn_chip"])
    objs.append(qfn)
    # White dot on chip pin-1 corner
    dot = add_cyl("MPU_chip_dot", r=0.18, h=0.02,
                  loc=(-1.6, -1.6, pcb_t + 0.96),
                  mat=pal["silkscreen_white"])
    objs.append(dot)
    # Voltage reg + a couple of caps near edge
    reg = add_box("MPU_reg", 2.9, 1.6, 1.10,
                  loc=(-7.0, -3.2, pcb_t + 0.55), bevel=0.05, mat=pal["ic_epoxy"])
    objs.append(reg)
    for i, x in enumerate((-5.5, -3.5, 5.0, 6.5)):
        cap = add_box(f"MPU_C{i}", 2.0, 1.25, 0.5,
                      loc=(x, -3.5, pcb_t + 0.25), mat=pal["cap_mlcc"])
        objs.append(cap)
    # Header (8-pin) along one long edge
    pin_pitch = 2.54
    pin_count = 8
    pin_w = 0.64
    plastic_h = 2.50
    strip = add_box("MPU_header_plastic",
                    pin_pitch * pin_count, 2.54, plastic_h,
                    loc=(0, -pcb_w / 2 + 1.27, pcb_t + plastic_h / 2),
                    mat=pal["header_plastic"])
    objs.append(strip)
    for i in range(pin_count):
        x = (i - (pin_count - 1) / 2) * pin_pitch
        above = add_box(f"MPU_pin_above_{i}", pin_w, pin_w, 6.0,
                        loc=(x, -pcb_w / 2 + 1.27, pcb_t + plastic_h + 3.0),
                        mat=pal["header_pin"])
        objs.append(above)
        below = add_box(f"MPU_pin_below_{i}", pin_w, pin_w, 3.0,
                        loc=(x, -pcb_w / 2 + 1.27, -1.5),
                        mat=pal["header_pin"])
        objs.append(below)
    # Silkscreen rectangle for "GY-521" text block
    silk = add_box("MPU_silk", 8.0, 1.2, 0.02,
                   loc=(0, 4.0, pcb_t + 0.011),
                   mat=pal["silkscreen_white"])
    objs.append(silk)
    # Power LED
    led = add_box("MPU_LED", 1.6, 0.8, 0.6,
                  loc=(8.5, 4.0, pcb_t + 0.30),
                  mat=pal["led_red"])
    objs.append(led)
    return objs


def build_esp32_s3_devkitc():
    """
    Espressif ESP32-S3-DevKitC-1 v1.1 (N16R8 variant for our build).
    Board PCB: 56.0 x 25.4 x 1.6 mm.
    Module ESP32-S3-WROOM-1: 18.0 x 25.5 x 3.1 mm with RF shield, mounted at
      one short end with module width overhanging the board to expose the
      antenna PCB trace at the very end.
    USB-C connector at opposite end (~7.5 mm wide x 9 mm deep, ~3.2 mm above
      board top surface).
    Two tactile buttons (BOOT, RESET) near USB-C side, ~6 mm square, ~3.4 mm tall.
    Two 1x18 (or 1x19 depending on variant) header rows on long edges, pitch 2.54
      mm. We model 1x18 to be conservative for typical N16R8.
    Source: Espressif ESP32-S3-DevKitC-1 v1.1 user guide and dimensions PDF.
    Note: this is the Espressif reference; the user's Hosyond clone needs
    physical clone-confirmation before solder-by-eye trust.
    """
    pal = palette()
    objs = []
    pcb_l, pcb_w, pcb_t = 56.0, 25.4, 1.6

    pcb = add_box("ESP32_PCB", pcb_l, pcb_w, pcb_t,
                  loc=(0, 0, pcb_t / 2), bevel=0.15, mat=pal["pcb_espressif"])
    objs.append(pcb)

    # Mounting holes (corner gold pads)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ring = add_cyl(f"ESP32_mh_{sx}_{sy}", r=1.5, h=0.05,
                           loc=(sx * (pcb_l / 2 - 2.5), sy * (pcb_w / 2 - 2.5),
                                pcb_t + 0.01),
                           mat=pal["pcb_pad_gold"])
            objs.append(ring)

    # Module: WROOM-1 (18 x 25.5 mm), centered widthwise, at -X end of board
    mod_l, mod_w, mod_h = 18.0, 25.5, 3.10
    # The module is positioned so its PCB end overhangs the dev-board PCB end
    # to expose the antenna at the extreme -X.
    mod_x = -pcb_l / 2 + mod_l / 2 + 1.5
    mod_pcb = add_box("ESP32_module_pcb", mod_l, mod_w, 0.8,
                      loc=(mod_x, 0, pcb_t + 0.4),
                      mat=pal["pcb_espressif"])
    objs.append(mod_pcb)
    # RF shield (covers most of the module except the antenna end)
    shield_l = mod_l - 5.0
    shield = add_box("ESP32_RF_shield", shield_l, mod_w - 1.6, 2.0,
                     loc=(mod_x + 2.5, 0, pcb_t + 0.8 + 1.0),
                     bevel=0.10, mat=pal["rf_shield"])
    objs.append(shield)
    # Antenna trace area (gold-ish meander rectangle)
    ant_w = 4.0
    ant = add_box("ESP32_antenna", ant_w, mod_w - 6.0, 0.04,
                  loc=(mod_x - mod_l / 2 + ant_w / 2 + 0.5, 0,
                       pcb_t + 0.8 + 0.02),
                  mat=pal["antenna_trace"])
    objs.append(ant)

    # USB-C connector at opposite (+X) end
    usb_w, usb_d, usb_h = 8.94, 7.35, 3.26  # GCT USB4500 typical
    usb_x = pcb_l / 2 - usb_d / 2 + 1.0  # overhang the board edge slightly
    usb = add_box("ESP32_USBC_shell", usb_d, usb_w, usb_h,
                  loc=(usb_x, 0, pcb_t + usb_h / 2),
                  bevel=0.20, mat=pal["usbc_metal"])
    objs.append(usb)
    # USB-C tongue insert (white plastic visible inside the shell)
    insert = add_box("ESP32_USBC_insert",
                     usb_d - 1.5, usb_w - 3.5, usb_h - 1.6,
                     loc=(usb_x + 0.4, 0, pcb_t + usb_h / 2),
                     mat=pal["usbc_insert"])
    objs.append(insert)

    # BOOT and RESET tactile buttons (6 x 6 x 3.4 mm), near USB-C end
    btn_size = 6.0
    btn_h = 3.4
    btn_y_offset = 8.0
    for name, dy in (("BOOT", -btn_y_offset), ("RESET", btn_y_offset)):
        b = add_box(f"ESP32_btn_{name}", btn_size, btn_size, btn_h,
                    loc=(pcb_l / 2 - 12.0, dy, pcb_t + btn_h / 2),
                    bevel=0.30, mat=pal["tactile_button"])
        objs.append(b)
        # Button cap (slightly smaller, slightly raised)
        cap = add_box(f"ESP32_btn_{name}_cap", btn_size - 1.0, btn_size - 1.0, 0.6,
                      loc=(pcb_l / 2 - 12.0, dy, pcb_t + btn_h + 0.30),
                      bevel=0.10, mat=pal["tactile_button"])
        objs.append(cap)

    # Power/RGB indicator LED (5050 RGB on GPIO48 in many variants)
    led = add_box("ESP32_LED_RGB", 5.0, 5.0, 1.6,
                  loc=(pcb_l / 2 - 22.0, pcb_w / 2 - 4.5, pcb_t + 0.8),
                  bevel=0.05, mat=pal["led_red"])
    objs.append(led)

    # Header rows: dual 1x18 0.1" pitch on long edges
    # Real DevKitC has 2x21 typical; many N16R8 clones are 2x19 or 2x18 — choose 2x19.
    pin_pitch = 2.54
    pin_count = 19
    pin_w = 0.64
    plastic_h = 2.50
    plastic_w = 2.54

    for sy in (-1, 1):
        y = sy * (pcb_w / 2 - plastic_w / 2 - 0.5)
        # Header plastic strip
        strip = add_box(f"ESP32_header_strip_{'A' if sy<0 else 'B'}",
                        pin_pitch * pin_count, plastic_w, plastic_h,
                        loc=(2.0, y, pcb_t + plastic_h / 2),
                        mat=pal["header_plastic"])
        objs.append(strip)
        for i in range(pin_count):
            x = 2.0 + (i - (pin_count - 1) / 2) * pin_pitch
            above = add_box(f"ESP32_pin_{sy}_above_{i}", pin_w, pin_w, 6.0,
                            loc=(x, y, pcb_t + plastic_h + 3.0),
                            mat=pal["header_pin"])
            objs.append(above)
            below = add_box(f"ESP32_pin_{sy}_below_{i}", pin_w, pin_w, 3.2,
                            loc=(x, y, -1.6),
                            mat=pal["header_pin"])
            objs.append(below)
    return objs


# -----------------------------------------------------------------------------
# Export driver
# -----------------------------------------------------------------------------
def export_glb(out_path):
    """Join all selected objects, scale mm->m, export."""
    # Select all visible meshes
    bpy.ops.object.select_all(action='DESELECT')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        print(f"  !! no meshes for {out_path}", file=sys.stderr)
        return False
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    # Don't join — preserve materials per primitive

    # Apply mm->m scale to each object via parent empty
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    parent = bpy.context.active_object
    parent.name = "ROOT"
    for m in meshes:
        m.parent = parent
    parent.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Export
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_image_format='AUTO',
    )
    sz_kb = os.path.getsize(out_path) // 1024
    print(f"  -> {out_path} ({sz_kb} KB)")
    return True


def build_and_export(name, builder_fn, *args, **kwargs):
    print(f"== Building {name} ==")
    reset_scene()
    builder_fn(*args, **kwargs)
    out_path = os.path.join(OUT_DIR, f"{name}.glb")
    export_glb(out_path)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    print(f"Output dir: {OUT_DIR}")
    targets = [
        ("MCP4822_PDIP8",        lambda: build_dip8("MCP4822", "U4")),
        ("TL072CP_PDIP8",        lambda: build_dip8("TL072CP", "U5")),
        ("2N7000_TO92_v2",       build_2n7000_to92),
        ("Resistor_0805_v2",     build_resistor_0805),
        ("Cap_0805_ceramic_v2",  build_cap_0805),
        ("LM4040_Adafruit2200",  build_lm4040_adafruit2200),
        ("MPU6050_GY521",        build_mpu6050_gy521),
        ("ESP32-S3-DevKitC-1",   build_esp32_s3_devkitc),
    ]
    for name, fn in targets:
        try:
            build_and_export(name, fn)
        except Exception as e:
            print(f"  !! FAILED {name}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
