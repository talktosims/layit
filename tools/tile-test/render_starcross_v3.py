#!/usr/bin/env python3
"""
Star & Cross v3 — Cross edges are the EXACT complement of star curves.
The cross boundary IS the star boundary, translated from adjacent stars.
"""
import math, os
from PIL import Image, ImageDraw

def quad_bezier(p0, p1, p2, n=16):
    """Sample quadratic bezier. Returns n+1 points."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0]
        y = u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]
        pts.append((x, y))
    return pts

def star_edge_cp(R, ck):
    """
    Control point for one star edge (from top tip to right tip), in star-centered coords.
    Star has tips at (0,-R), (R,0), (0,R), (-R,0).
    Edge from top (0,-R) to right (R,0):
      Midpoint = (R/2, -R/2)
      Direction to center = (-1/√2, 1/√2)
      CP = midpoint + dir * dist * (1-ck)
    """
    # Midpoint of top→right edge
    mx, my = R/2, -R/2
    # Distance from midpoint to center = R/√2
    d = R / math.sqrt(2)
    # Direction from midpoint to center (normalized)
    dx, dy = -mx/d, -my/d  # = (-1/√2, 1/√2)
    # Control point
    cp_x = mx + dx * d * (1 - ck)
    cp_y = my + dy * d * (1 - ck)
    return (cp_x, cp_y)

def star_curved_verts(cx, cy, R, ck, n=16):
    """4-pointed star with concave bezier edges."""
    tips = [(cx, cy - R), (cx + R, cy), (cx, cy + R), (cx - R, cy)]

    # Base control point for top→right edge
    base_cp = star_edge_cp(R, ck)

    verts = []
    for i in range(4):
        p0 = tips[i]
        p2 = tips[(i + 1) % 4]
        # Rotate base_cp by i*90°
        angle = i * math.pi / 2
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        cp_x = base_cp[0] * cos_a - base_cp[1] * sin_a
        cp_y = base_cp[0] * sin_a + base_cp[1] * cos_a
        p1 = (cx + cp_x, cy + cp_y)

        pts = quad_bezier(p0, p1, p2, n)
        verts.extend(pts[:-1])
    return verts

def cross_curved_verts(cx, cy, S, R, ck, g, n=16):
    """
    Cross as exact complement of surrounding stars.
    The cross has 4 curved edges (from 4 stars) + 4 straight arm tips.
    """
    b = S/2 - R + g/2       # arm tip half-width (with grout)
    arm = S/2 - g/2          # arm length from center (with grout)

    # Star edge control points for each adjacent star, in cross coords.
    # Star NE at (S/2, -S/2): contributes curve from its left tip to its bottom tip
    # = in star coords: from (-R, 0) to (0, R)
    # This is the REVERSE of the top→right edge. For top→right: P0=(0,-R), P2=(R,0), CP=base_cp
    # For left→bottom (rotated 180°): P0=(-R,0), P2=(0,R), CP = rotated 180° = (-base_cp[0], -base_cp[1])
    # But reversed bezier has same CP: from bottom→left is P0=(0,R), P2=(-R,0), CP=(-base_cp[0], -base_cp[1])
    # We want left→bottom: P0=(-R,0), P2=(0,R)

    # Actually, let me just directly compute each star's relevant edge.

    # For star NE at (S/2, -S/2), the edge that borders the cross is:
    # bottom_tip → left_tip in star coords = (0, R) → (-R, 0)
    # This is the edge from bottom to left, which is the reverse of top→right rotated by 180°

    # Edge from bottom (0,R) to left (-R,0): rotate top→right by 180°
    # top→right CP: base_cp = (cp_x, cp_y)
    # Rotated 180°: (-cp_x, -cp_y)

    base_cp = star_edge_cp(R, ck)

    # But we traverse bottom→left, which in terms of the rotated edge is P0=(0,R)→P2=(-R,0)
    # The CP for this edge (rotating top→right by 180°):
    # top→right: (0,-R) → CP → (R,0)
    # bottom→left: (0,R) → (-CP_x, -CP_y) → (-R,0)

    # In star coords, edge bottom→left:
    # P0=(0, R), P1=(-base_cp[0], -base_cp[1]), P2=(-R, 0)

    # Translated to cross coords (star NE at S/2, -S/2):
    # P0 = (S/2 + 0, -S/2 + R) = (S/2, R - S/2)
    # P1 = (S/2 - base_cp[0], -S/2 - base_cp[1])
    # P2 = (S/2 - R, -S/2)

    # For the cross, we want this curve but REVERSED (from P2 to P0):
    # from (S/2-R, -S/2) to (S/2, R-S/2), same CP
    # With grout adjustment, approximately:
    # from (b, -arm) to (arm, -b)

    # Let me compute all 4 star curves in cross coords:

    curves = []  # Each: (start, control, end) in cross coords

    # Stars at 4 diagonal positions relative to cross center
    star_positions = [
        (S/2, -S/2),   # NE — contributes curve between N arm and E arm
        (S/2, S/2),    # SE — between E arm and S arm
        (-S/2, S/2),   # SW — between S arm and W arm
        (-S/2, -S/2),  # NW — between W arm and N arm
    ]

    for si, (sx, sy) in enumerate(star_positions):
        # Each star contributes one curved edge.
        # Star NE: curve from its left tip to its bottom tip (traversed in cross-clockwise order)
        # = bottom→left in star coords, reversed for cross traversal

        # The relevant edge of each star (going clockwise around cross):
        # NE star: from left_tip (-R,0) to bottom_tip (0,R) in star coords
        # = traversed as: left→bottom
        # SE star: from top_tip (0,-R) to left_tip (-R,0) in star coords
        # = top→left
        # SW star: from right_tip (R,0) to top_tip (0,-R) in star coords
        # = right→top
        # NW star: from bottom_tip (0,R) to right_tip (R,0) in star coords
        # = bottom→right

        # These are all the same edge shape, just rotated.
        # NE: edge from left(-R,0) to bottom(0,R) = rotate base edge by 180° then reverse
        #     = edge from bottom(0,R) to left(-R,0) reversed = left(-R,0) to bottom(0,R)

        # OK let me just use rotation directly.
        # The base edge is top→right: (0,-R) → CP → (R,0)
        # For star NE, the relevant edge in star coords is:
        #   Going clockwise around cross, after the N arm tip we need to reach E arm tip.
        #   The curve goes from near (b, -arm) to (arm, -b) in cross coords.
        #   In star NE coords: from (b-S/2, -arm+S/2) to (arm-S/2, -b+S/2)
        #     = (S/2-R - S/2, -S/2 - (-S/2)) wait this is getting confused.

        # Let me use a different approach. I'll compute the star's 4 edges, find the one
        # that faces the cross, and translate it.

        # Star edge i goes from tip[i] to tip[i+1] in star coords
        # Base edge (i=0): top(0,-R) → right(R,0), CP = base_cp
        # Edge i=1: right(R,0) → bottom(0,R), CP = rotate base_cp by 90°
        # Edge i=2: bottom(0,R) → left(-R,0), CP = rotate base_cp by 180°
        # Edge i=3: left(-R,0) → top(0,-R), CP = rotate base_cp by 270°

        # For NE star: the edge facing the cross center is the one going from
        # bottom-ish to left-ish in star coords. That's edge i=2: bottom→left
        # The cross traverses this edge in REVERSE: left→bottom

        # But which edge faces the cross depends on the star position.
        # NE star faces cross with its bottom-left region → edge i=2 (bottom→left)
        #   Traversed from star's left tip to bottom tip for clockwise cross
        # SE star faces cross with its top-left region → edge i=3 (left→top)
        # SW star faces cross with its top-right region → edge i=0 (top→right)
        # NW star faces cross with its bottom-right region → edge i=1 (right→bottom)

        edge_indices = [2, 3, 0, 1]  # which star edge faces the cross, per star position
        ei = edge_indices[si]

        # Rotate base_cp by ei * 90°
        angle = ei * math.pi / 2
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        cp_rot = (base_cp[0]*cos_a - base_cp[1]*sin_a,
                  base_cp[0]*sin_a + base_cp[1]*cos_a)

        # Edge endpoints in star coords (tip[ei] → tip[ei+1])
        tips_local = [(0, -R), (R, 0), (0, R), (-R, 0)]
        p0_local = tips_local[ei]
        p2_local = tips_local[(ei + 1) % 4]

        # Translate to cross coords
        p0 = (sx + p0_local[0], sy + p0_local[1])
        p2 = (sx + p2_local[0], sy + p2_local[1])
        cp = (sx + cp_rot[0], sy + cp_rot[1])

        # For the cross, traverse this edge in REVERSE (p2 → p0)
        # Reversed bezier has same control point
        curves.append((p2, cp, p0))

    # Now build the cross outline: alternate straight arm tips and star curves
    # Going clockwise from N arm tip left:

    verts = []

    # Arm tips in cross coords (clockwise)
    arm_tips = [
        ((-b, -arm), (b, -arm)),    # N arm tip: left to right
        ((arm, -b), (arm, b)),       # E arm tip: top to bottom
        ((b, arm), (-b, arm)),       # S arm tip: right to left
        ((-arm, b), (-arm, -b)),     # W arm tip: bottom to top
    ]

    for i in range(4):
        # Arm tip (straight)
        ts, te = arm_tips[i]
        verts.append((cx + ts[0], cy + ts[1]))
        verts.append((cx + te[0], cy + te[1]))

        # Star curve to next arm
        p0, p1, p2 = curves[i]
        # Apply grout offset: shrink curve toward cross center
        # Simple approach: just use the curve as-is (grout is in b and arm)
        curve_pts = quad_bezier(p0, p1, p2, n)
        # Skip first and last (they overlap with arm tip endpoints)
        # Actually the curve endpoints should match the arm tip endpoints
        # Let me just add the sampled curve points
        verts.extend(curve_pts[1:-1])

    return verts

def polygon_area(verts):
    n = len(verts)
    a = 0
    for i in range(n):
        j = (i + 1) % n
        a += verts[i][0] * verts[j][1] - verts[j][0] * verts[i][1]
    return abs(a) / 2

def render(star_ratio=0.94, curve_k=0.35, cell=250, grout=5,
           filename='starcross_v3.png', grid_size=4):

    R = cell * star_ratio / 2
    S = cell
    g = grout

    w = cell * (grid_size + 1)
    h = cell * (grid_size + 1)

    star_color = '#3d7a6a'
    cross_color = '#f0e8d4'
    grout_color = '#c0b8a0'

    img = Image.new('RGB', (w, h), grout_color)
    draw = ImageDraw.Draw(img)

    ox = cell // 2
    oy = cell // 2

    for row in range(-1, grid_size + 1):
        for col in range(-1, grid_size + 1):
            sx = ox + col * cell
            sy = oy + row * cell

            # Star (slightly reduced for grout)
            sv = star_curved_verts(sx, sy, R - g/2, curve_k)
            if len(sv) >= 3:
                draw.polygon(sv, fill=star_color)

            # Cross (using exact star curve complement)
            cv = cross_curved_verts(sx + cell/2, sy + cell/2, cell, R, curve_k, g)
            if len(cv) >= 3:
                draw.polygon(cv, fill=cross_color)

    # Metrics
    star_v = star_curved_verts(0, 0, R - g/2, curve_k)
    cross_v = cross_curved_verts(0, 0, cell, R, curve_k, g)
    sa = polygon_area(star_v)
    ca = polygon_area(cross_v)
    cell_a = cell * cell

    print(f'\n{"═"*50}')
    print(f'V3: Star ratio={star_ratio}, curve_k={curve_k}')
    print(f'Star: {sa:,.0f}px² ({sa/cell_a*100:.1f}%) | Cross: {ca:,.0f}px² ({ca/cell_a*100:.1f}%)')
    print(f'Star/Cross ratio: {sa/ca:.2f}x | Coverage: {(sa+ca)/cell_a*100:.1f}%')
    print(f'{"═"*50}')

    outpath = os.path.join(os.path.dirname(__file__) or '.', filename)
    img.save(outpath)
    print(f'Saved: {outpath}')

def render_comparison():
    configs = [
        (0.94, 0.25, 'v3_ck25.png'),
        (0.94, 0.35, 'v3_ck35.png'),
        (0.94, 0.45, 'v3_ck45.png'),
        (0.94, 0.55, 'v3_ck55.png'),
        (0.94, 0.65, 'v3_ck65.png'),
    ]
    for sr, ck, fn in configs:
        render(star_ratio=sr, curve_k=ck, cell=200, grout=4, filename=fn, grid_size=3)

if __name__ == '__main__':
    render_comparison()
