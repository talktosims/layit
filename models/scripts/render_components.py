"""
Render PNG preview of every freshly-built component GLB.

Run:
    blender --background --python render_components.py -- <models_dir> <out_dir>
"""
import bpy
import os
import sys
import math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
MODELS_DIR = argv[0] if argv else "/Users/Sims/Desktop/expandit/products/layit/models"
OUT_DIR = argv[1] if len(argv) > 1 else "/Users/Sims/Desktop/layit/models/renders/components_v2"
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    "MCP4822_PDIP8.glb",
    "TL072CP_PDIP8.glb",
    "2N7000_TO92_v2.glb",
    "Resistor_0805_v2.glb",
    "Cap_0805_ceramic_v2.glb",
    "LM4040_Adafruit2200.glb",
    "MPU6050_GY521.glb",
    "ESP32-S3-DevKitC-1.glb",
]


def reset_scene():
    for o in list(bpy.context.scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def setup_render(width=1024, height=768):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.samples = 128
    s.cycles.use_denoising = True
    try:
        s.cycles.device = 'GPU'
    except Exception:
        pass
    s.render.resolution_x = width
    s.render.resolution_y = height
    s.render.image_settings.file_format = 'PNG'
    s.render.film_transparent = False
    s.view_settings.exposure = 0.0
    s.view_settings.gamma = 1.0
    # Use AgX (Blender's modern filmic tone-map) so highlights compress and
    # mid-tones stay where the materials say they are.
    try:
        s.view_settings.view_transform = 'AgX'
    except Exception:
        try:
            s.view_settings.view_transform = 'Filmic'
        except Exception:
            pass
    # Solid pale-blue world. No HDR — just a soft floor of indirect light.
    w = bpy.data.worlds['World']
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.78, 0.82, 0.86, 1.0)
        bg.inputs[1].default_value = 0.35


def add_studio_lights(scale_factor):
    """Photographer-style three-point setup. Energy scales with area² so the
    apparent illumination per square meter stays roughly constant from a 2mm
    resistor to a 60mm dev board. Tuned so a base_color=0.05 surface lands
    around 5% gray, not 100% white."""
    d = max(scale_factor, 0.005)
    # Inverse-square law: to keep apparent illumination constant, energy must
    # scale with distance². Base 25 W at 1 m gives a sensible level after AgX.
    e_base = 25.0 * (d * 4.0) ** 2  # area-light distance ~4d
    # Key light (warmer, brighter, front-right)
    bpy.ops.object.light_add(type='AREA', location=(d * 2.5, -d * 3.5, d * 3.0))
    key = bpy.context.active_object
    key.data.size = d * 2.5
    key.data.energy = e_base * 1.0
    key.data.color = (1.0, 0.96, 0.92)
    direction = -Vector(key.location)
    key.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    # Fill (cooler, softer, front-left)
    bpy.ops.object.light_add(type='AREA', location=(-d * 3.0, -d * 2.5, d * 2.0))
    fill = bpy.context.active_object
    fill.data.size = d * 3.0
    fill.data.energy = e_base * 0.4
    fill.data.color = (0.95, 0.97, 1.0)
    direction = -Vector(fill.location)
    fill.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    # Rim (back, slightly cooler)
    bpy.ops.object.light_add(type='AREA', location=(0, d * 3.5, d * 2.8))
    rim = bpy.context.active_object
    rim.data.size = d * 2.0
    rim.data.energy = e_base * 0.7
    rim.data.color = (0.92, 0.95, 1.0)
    direction = -Vector(rim.location)
    rim.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def add_shadow_catcher(scale_factor):
    """Invisible plane that just catches shadows for grounding without taking
    over the frame."""
    size = max(scale_factor * 8.0, 0.05)
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, -0.0001))
    p = bpy.context.active_object
    p.name = "shadow_catcher"
    p.is_shadow_catcher = True


def frame_camera_to_objects(objs):
    bb = []
    for o in objs:
        if o.type == 'MESH':
            for c in o.bound_box:
                bb.append(o.matrix_world @ Vector(c))
    if not bb:
        return None
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    center = (mn + mx) / 2
    size = mx - mn
    # Use the larger of horizontal extent or 1.8x vertical extent so tall
    # narrow parts (TO-92) and flat wide parts (PCBs) both fit.
    horizontal = max(size.x, size.y)
    radius = max(horizontal, size.z * 0.7) * 0.5
    fov_h = math.radians(30)  # we want the part to fill ~75% of frame
    cam_dist = radius / math.tan(fov_h / 2) * 1.15
    elev = math.radians(33)
    azim = math.radians(-32)
    cam_loc = center + Vector((
        cam_dist * math.cos(elev) * math.sin(azim),
        -cam_dist * math.cos(elev) * math.cos(azim),
        cam_dist * math.sin(elev),
    ))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.active_object
    direction = center - cam_loc
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 50
    cam.data.sensor_width = 36
    cam.data.clip_start = 0.0001  # default 0.1m clips small parts entirely
    cam.data.clip_end = 1000.0
    bpy.context.scene.camera = cam
    return cam


def render_one(glb_path, out_path):
    reset_scene()
    setup_render()
    bpy.ops.import_scene.gltf(filepath=glb_path)
    imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not imported:
        print(f"  !! no mesh imported: {glb_path}", file=sys.stderr)
        return
    # Compute world-space bounding box (glTF importer converts Y-up to Z-up
    # by default, so the part now has its vertical along Z).
    bb = []
    for o in imported:
        for c in o.bound_box:
            bb.append(o.matrix_world @ Vector(c))
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    # Drop to sit on Z=0
    for o in imported:
        o.location.z -= mn.z
    # Recompute after drop
    bb = []
    for o in imported:
        for c in o.bound_box:
            bb.append(o.matrix_world @ Vector(c))
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    size = mx - mn
    diag = math.sqrt(size.x ** 2 + size.y ** 2 + size.z ** 2)
    add_shadow_catcher(diag)
    add_studio_lights(diag)
    frame_camera_to_objects(imported)
    bpy.context.scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"  rendered -> {out_path}  (diag={diag*1000:.1f}mm)")


def main():
    print(f"Rendering from {MODELS_DIR} to {OUT_DIR}")
    for fname in TARGETS:
        glb = os.path.join(MODELS_DIR, fname)
        if not os.path.exists(glb):
            print(f"  MISSING: {glb}")
            continue
        out = os.path.join(OUT_DIR, fname.replace(".glb", ".png"))
        try:
            render_one(glb, out)
        except Exception as e:
            print(f"  !! render failed for {fname}: {e}", file=sys.stderr)
            import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
