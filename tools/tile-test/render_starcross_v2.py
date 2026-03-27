#!/usr/bin/env python3
"""
Star & Cross v2 — curved edges for proper visual concavity + correct area ratio.
The star edges are quadratic bezier curves that bow inward, creating visible
concavity while retaining more area than straight-line notches.
"""
import math
import os

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Need Pillow: pip install Pillow")
    exit(1)

# ═══════════════════════════════════════════
# Bezier Sampling
# ═══════════════════════════════════════════

def quad_bezier(p0, p1, p2, n=12):
    """Sample a quadratic bezier curve. Returns n+1 points."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0]
        y = u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]
        pts.append((x, y))
    return pts

# ═══════════════════════════════════════════
# Star with Curved Edges
# ═══════════════════════════════════════════

def star_curved(cx, cy, R, curve_k, samples=12):
    """
    4-pointed star with concave curved edges.
    curve_k: 0.0 = extreme concavity (curve through center)
             0.707 = straight line (no concavity)
             <0.707 = concave (inward bow)
    Good range for real tiles: 0.25-0.45
    """
    # 4 tip points
    tips = [
        (cx, cy - R),   # top
        (cx + R, cy),    # right
        (cx, cy + R),    # bottom
        (cx - R, cy),    # left
    ]

    # For each pair of adjacent tips, draw a concave curve
    # Control point is on the diagonal, pulled toward center
    verts = []
    for i in range(4):
        p0 = tips[i]
        p2 = tips[(i + 1) % 4]
        # Midpoint of straight line
        mx = (p0[0] + p2[0]) / 2
        my = (p0[1] + p2[1]) / 2
        # Direction from midpoint toward center
        dx = cx - mx
        dy = cy - my
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        # Control point: midpoint moved toward center by (1-curve_k) * dist_to_center
        # curve_k=1 → control at midpoint (straight line)
        # curve_k=0 → control at center (extreme concavity)
        cp_x = mx + dx * dist * (1 - curve_k)
        cp_y = my + dy * dist * (1 - curve_k)

        # Sample the bezier (skip first point to avoid duplicates)
        pts = quad_bezier(p0, (cp_x, cp_y), p2, samples)
        verts.extend(pts[:-1])  # skip last point (it's the next tip)

    return verts

def cross_curved(cx, cy, S, R, curve_k, g, samples=12):
    """
    Cross shape that complements the curved star.
    The cross edges match the star's curves (convex where star is concave).
    """
    # The cross has 4 arms. Each arm is bounded by curves from adjacent stars.
    # For simplicity, define the cross as a 12-vertex polygon with curved notch indentations.

    # Cross arm geometry (same as before for the straight-edge version):
    # We need to compute where the star curves intersect at the cross boundary.
    # The cross notch point is where two star curves from adjacent stars meet.

    # For a curved star, the effective "inner vertex" position is determined by
    # where the curve reaches the diagonal. At t=0.5 on the bezier from top to right:
    # The curve's closest approach to center determines the notch depth.

    # Approximate with straight-edge cross using the curve's midpoint distance as effective inR
    # Midpoint of curve from (0,-R) to (R,0) with control at (cp_x, cp_y):
    # At t=0.5: B = 0.25*P0 + 0.5*P1 + 0.25*P2

    # For the tip at (0,-R) and next tip at (R,0):
    mx = R / 2  # midpoint x of straight line
    my = -R / 2  # midpoint y
    # Direction to center from midpoint
    dist_to_center = math.sqrt(mx*mx + my*my)  # = R/sqrt(2)
    dx = -mx / dist_to_center
    dy = -my / dist_to_center

    cp_x = mx + dx * dist_to_center * (1 - curve_k)
    cp_y = my + dy * dist_to_center * (1 - curve_k)

    # Curve midpoint (t=0.5):
    mid_x = 0.25 * 0 + 0.5 * cp_x + 0.25 * R
    mid_y = 0.25 * (-R) + 0.5 * cp_y + 0.25 * 0

    # Effective inner radius (distance from center to curve midpoint on diagonal)
    eff_inR = math.sqrt(mid_x*mid_x + mid_y*mid_y)

    # Now build tapered cross using effective inR
    a = S/2 - eff_inR - g/2    # arm half-width at base
    b = max(S/2 - R + g/2, 1)  # arm half-width at tip
    arm = S/2 - g/2            # arm length

    # Build cross with curved notch indentations
    verts = []

    # For each of the 4 arm-notch-arm segments:
    # N arm tip: (-b, -arm) → (b, -arm) [straight]
    # NE notch: curved indentation from (a, -a) inward
    # E arm tip: (arm, -b) → (arm, b) [straight]
    # etc.

    # For simplicity, use straight cross edges with curved concave notches
    # The notch between N and E arms curves inward toward the cross center

    notch_pts_per_corner = max(samples // 2, 4)

    arms = [
        # (tip_start, tip_end, notch_far)
        ((-b, -arm), (b, -arm), (a, -a)),      # N arm → NE notch
        ((arm, -b), (arm, b), (a, a)),           # E arm → SE notch
        ((b, arm), (-b, arm), (-a, a)),          # S arm → SW notch
        ((-arm, b), (-arm, -b), (-a, -a)),       # W arm → NW notch
    ]

    for i, (ts, te, notch) in enumerate(arms):
        # Arm tip (straight line from ts to te)
        verts.append((cx + ts[0], cy + ts[1]))
        verts.append((cx + te[0], cy + te[1]))

        # Notch: curve from arm end to next arm start
        # End of this arm tip = te
        # Start of next arm tip = next arms[i+1][0] (ts of next)
        next_ts = arms[(i + 1) % 4][0]

        # Control point for notch curve: pull toward cross center
        notch_mx = (te[0] + next_ts[0]) / 2
        notch_my = (te[1] + next_ts[1]) / 2
        notch_dist = math.sqrt(notch_mx*notch_mx + notch_my*notch_my)

        if notch_dist > 0:
            # Pull control point toward center for concave notch
            pull = 0.3  # how much to curve the notch (0=straight, 1=to center)
            ncp_x = notch_mx * (1 - pull)
            ncp_y = notch_my * (1 - pull)
        else:
            ncp_x, ncp_y = 0, 0

        p0 = (cx + te[0], cy + te[1])
        p1 = (cx + ncp_x, cy + ncp_y)
        p2 = (cx + next_ts[0], cy + next_ts[1])

        # Sample notch curve (skip endpoints to avoid duplicates)
        notch_curve = quad_bezier(p0, p1, p2, notch_pts_per_corner)
        verts.extend(notch_curve[1:-1])

    return verts

# ═══════════════════════════════════════════
# Rendering
# ═══════════════════════════════════════════

def render(star_ratio=0.94, curve_k=0.35, cell=200, grout=4,
           filename='starcross_v2.png', star_color='#3d7a6a', cross_color='#f0e8d4',
           grout_color='#c0b8a0', grid_size=4):
    """Render star & cross with curved edges."""

    R = cell * star_ratio / 2
    g = grout

    w = cell * (grid_size + 1)
    h = cell * (grid_size + 1)

    img = Image.new('RGB', (w, h), grout_color)
    draw = ImageDraw.Draw(img)

    ox = cell // 2
    oy = cell // 2

    for row in range(-1, grid_size + 1):
        for col in range(-1, grid_size + 1):
            sx = ox + col * cell
            sy = oy + row * cell

            # Star
            sv = star_curved(sx, sy, R - g/2, curve_k)
            if len(sv) >= 3:
                draw.polygon(sv, fill=star_color)

            # Cross
            cv = cross_curved(sx + cell/2, sy + cell/2, cell, R, curve_k, g)
            if len(cv) >= 3:
                draw.polygon(cv, fill=cross_color)

    # Compute star area using sampled polygon
    star_v = star_curved(0, 0, R, curve_k)
    star_area = polygon_area(star_v)
    cross_v = cross_curved(0, 0, cell, R, curve_k, g)
    cross_area = polygon_area(cross_v)
    cell_area = cell * cell

    print(f'\n{"═"*50}')
    print(f'Star & Cross V2 (Curved Edges)')
    print(f'{"═"*50}')
    print(f'Cell: {cell}px | Star ratio: {star_ratio} | Curve k: {curve_k}')
    print(f'Star tip-to-tip: {2*R:.0f}px | Grout: {g}px')
    print(f'{"─"*50}')
    print(f'Star area:  {star_area:,.0f}px² ({star_area/cell_area*100:.1f}%)')
    print(f'Cross area: {cross_area:,.0f}px² ({cross_area/cell_area*100:.1f}%)')
    print(f'Coverage:   {(star_area+cross_area)/cell_area*100:.1f}%')
    print(f'Star/Cross: {star_area/cross_area:.2f}x')
    print(f'{"═"*50}')

    outpath = os.path.join(os.path.dirname(__file__) or '.', filename)
    img.save(outpath)
    print(f'Saved: {outpath}')
    return outpath

def polygon_area(verts):
    n = len(verts)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += verts[i][0] * verts[j][1]
        area -= verts[j][0] * verts[i][1]
    return abs(area) / 2

def render_comparison():
    """Side-by-side comparison of curve_k values."""
    configs = [
        {'label': 'A: ck=0.25', 'curve_k': 0.25},
        {'label': 'B: ck=0.35', 'curve_k': 0.35},
        {'label': 'C: ck=0.45', 'curve_k': 0.45},
        {'label': 'D: ck=0.55', 'curve_k': 0.55},
    ]

    cell = 150
    g = 3
    star_ratio = 0.94
    R = cell * star_ratio / 2
    tile_count = 3
    tile_size = cell * tile_count
    margin = 20
    label_h = 25

    total_w = len(configs) * (tile_size + margin) + margin
    total_h = tile_size + margin * 2 + label_h

    img = Image.new('RGB', (total_w, total_h), '#222222')
    draw = ImageDraw.Draw(img)

    for ci, cfg in enumerate(configs):
        ox_base = margin + ci * (tile_size + margin)
        oy_base = margin + label_h

        for row in range(-1, tile_count + 1):
            for col in range(-1, tile_count + 1):
                sx = ox_base + cell // 2 + col * cell
                sy = oy_base + cell // 2 + row * cell

                sv = star_curved(sx, sy, R - g/2, cfg['curve_k'])
                if len(sv) >= 3:
                    draw.polygon(sv, fill='#3d7a6a')

                cv = cross_curved(sx + cell/2, sy + cell/2, cell, R, cfg['curve_k'], g)
                if len(cv) >= 3:
                    draw.polygon(cv, fill='#f0e8d4')

        draw.rectangle([ox_base, oy_base, ox_base + tile_size, oy_base + tile_size],
                       outline='#555', width=2)
        draw.text((ox_base + 5, margin + 2), cfg['label'], fill='#ffffff')

    outpath = os.path.join(os.path.dirname(__file__) or '.', 'starcross_v2_comparison.png')
    img.save(outpath)
    print(f'\nSaved comparison: {outpath}')

if __name__ == '__main__':
    print('Star & Cross V2 — Curved Edges\n')

    # Best candidate
    render(star_ratio=0.94, curve_k=0.35, cell=250, grout=5, filename='starcross_v2_best.png')

    # Comparison
    render_comparison()
