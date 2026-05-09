#!/usr/bin/env freecadcmd
"""
Convert a STEP file to OBJ, preserving sub-solid groupings as separate
material groups (usemtl). Connectors typically split into housing + pins +
contacts; ICs split into body + leads; etc. This lets Blender color them.

Usage:
    freecadcmd step_to_obj.py -- <input.step> <output.obj>

The output OBJ has one 'usemtl' per sub-solid named "Solid_<index>".
A companion .mtl file is also written so Blender's importer creates
distinct material slots automatically.
"""
import sys
import os
import Part
import MeshPart

args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
if len(args) < 2:
    print("usage: step_to_obj.py <input.step> <output.obj>", file=sys.stderr)
    sys.exit(2)

step_in, obj_out = args[0], args[1]
mtl_out = os.path.splitext(obj_out)[0] + ".mtl"
mtl_basename = os.path.basename(mtl_out)

shape = Part.Shape()
shape.read(step_in)

# Solids = independent volumetric pieces. Connector housings, pins, etc.
solids = shape.Solids if shape.Solids else [shape]

# Tessellate each solid -> mesh -> collect verts and faces with offsets
all_verts = []
all_faces_per_solid = []  # list of [(v1,v2,v3), ...] per solid

for solid in solids:
    try:
        m = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.1, AngularDeflection=0.5)
    except Exception as e:
        print(f"  skip solid (mesh fail): {e}", file=sys.stderr)
        continue

    # Pull topology
    base = len(all_verts)
    pts = m.Topology[0]
    facets = m.Topology[1]
    for p in pts:
        all_verts.append((p.x, p.y, p.z))
    faces = []
    for f in facets:
        # OBJ indices are 1-based
        faces.append((f[0]+1+base, f[1]+1+base, f[2]+1+base))
    all_faces_per_solid.append(faces)

# Write OBJ
with open(obj_out, "w") as f:
    f.write(f"# Generated from {os.path.basename(step_in)}\n")
    f.write(f"mtllib {mtl_basename}\n")
    for v in all_verts:
        f.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
    for i, faces in enumerate(all_faces_per_solid):
        f.write(f"\ng Solid_{i}\n")
        f.write(f"usemtl Solid_{i}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")

# Write minimal MTL stub — colors get overridden in Blender per heuristic
with open(mtl_out, "w") as f:
    for i in range(len(all_faces_per_solid)):
        f.write(f"newmtl Solid_{i}\nKd 0.6 0.6 0.6\nKa 0.0 0.0 0.0\nKs 0.1 0.1 0.1\nNs 50\n\n")

n_facets = sum(len(faces) for faces in all_faces_per_solid)
size_kb = os.path.getsize(obj_out) // 1024
print(f"  -> {obj_out} ({size_kb} KB, {len(solids)} solids, {n_facets} facets)")
