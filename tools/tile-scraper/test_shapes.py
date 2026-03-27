"""
Render all LayIt tile shapes to PNG for visual verification against real tile photos.
Each shape is rendered at the exact same scale and math as the app's Canvas2D code.
v2: Fixed spacing (use full tile height, not half), fixed star k-value, fixed arabesque shape.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), 'output', 'shape_tests')
os.makedirs(OUT_DIR, exist_ok=True)

def quad_bezier(p0, p1, p2, n=30):
    t = np.linspace(0, 1, n)
    x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0]
    y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1]
    return list(zip(x, y))

def cubic_bezier(p0, p1, p2, p3, n=30):
    t = np.linspace(0, 1, n)
    x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
    y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
    return list(zip(x, y))

def arc_points(cx, cy, r, start_angle, end_angle, n=30):
    angles = np.linspace(start_angle, end_angle, n)
    return [(cx + r*np.cos(a), cy + r*np.sin(a)) for a in angles]

def fill_polygon(ax, pts, color='#d4c5a9', edge='#8b7355', lw=0.8):
    from matplotlib.patches import Polygon
    poly = Polygon(pts, closed=True, facecolor=color, edgecolor=edge, linewidth=lw)
    ax.add_patch(poly)

def render_shape(name, draw_func, filename, **kwargs):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_aspect('equal')
    ax.set_facecolor('#e8e0d0')
    draw_func(ax, **kwargs)
    ax.set_title(f'{name}', fontsize=16, fontweight='bold')
    ax.autoscale()
    m = 0.2
    xl, xr = ax.get_xlim(); yl, yr = ax.get_ylim()
    ax.set_xlim(xl-m, xr+m); ax.set_ylim(yl-m, yr+m)
    ax.set_xticks([]); ax.set_yticks([])
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#e8e0d0')
    plt.close(fig)
    print(f'  {filename}')
    return path


# ═══════════════════════════════════════════
# STAR & CROSS — k=0.42 (gentle concavity, cross has visible arms)
# ═══════════════════════════════════════════

def star_pts(cx, cy, hw, hh, k):
    pts = []
    pts += quad_bezier((cx, cy-hh), (cx+hw*k, cy-hh*k), (cx+hw, cy))
    pts += quad_bezier((cx+hw, cy), (cx+hw*k, cy+hh*k), (cx, cy+hh))
    pts += quad_bezier((cx, cy+hh), (cx-hw*k, cy+hh*k), (cx-hw, cy))
    pts += quad_bezier((cx-hw, cy), (cx-hw*k, cy-hh*k), (cx, cy-hh))
    return pts

def cross_pts(cx, cy, hw, hh, k):
    pts = []
    pts += quad_bezier((cx, cy-hh), (cx+hw*(1-k), cy+hh*(k-1)), (cx+hw, cy))
    pts += quad_bezier((cx+hw, cy), (cx+hw*(1-k), cy+hh*(1-k)), (cx, cy+hh))
    pts += quad_bezier((cx, cy+hh), (cx+hw*(k-1), cy+hh*(1-k)), (cx-hw, cy))
    pts += quad_bezier((cx-hw, cy), (cx+hw*(k-1), cy+hh*(k-1)), (cx, cy-hh))
    return pts

def draw_starcross(ax, grid=5, grout=0.04):
    k = 0.42
    hw = hh = 0.5
    pitch = 2*hw + grout
    star_c = ['#c9b88a', '#d4c5a0', '#bfad7e', '#c2b590']
    cross_c = ['#8aab8a', '#9ab89a', '#7a9b7a', '#88aa88']
    for r in range(grid):
        for c in range(grid):
            cx, cy = c*pitch, r*pitch
            fill_polygon(ax, star_pts(cx, cy, hw, hh, k), star_c[(r*grid+c)%4])
            if c < grid-1 and r < grid-1:
                fill_polygon(ax, cross_pts(cx+pitch/2, cy+pitch/2, hw, hh, k), cross_c[(r*grid+c)%4])


# ═══════════════════════════════════════════
# ARABESQUE — true lantern: wide shoulders, very narrow waist
# Real arabesque: shoulders ~90% of hw, waist ~35% of hw
# ═══════════════════════════════════════════

def arabesque_pts(cx, cy, hw, hh):
    """Lantern shape: pointed ends, convex shoulders, concave waist."""
    pts = []
    # Top → right shoulder (convex outward) → right waist (concave inward)
    pts += cubic_bezier((cx, cy-hh),
                        (cx+hw*0.55, cy-hh*0.88),
                        (cx+hw*1.08, cy-hh*0.45),
                        (cx+hw*0.88, cy-hh*0.12))
    # Right waist → right hip → bottom
    pts += cubic_bezier((cx+hw*0.88, cy-hh*0.12),
                        (cx+hw*0.35, cy+hh*0.05),
                        (cx+hw*0.35, cy+hh*0.05),
                        (cx+hw*0.35, cy+hh*0.12))
    pts += cubic_bezier((cx+hw*0.35, cy+hh*0.12),
                        (cx+hw*1.08, cy+hh*0.45),
                        (cx+hw*0.55, cy+hh*0.88),
                        (cx, cy+hh))
    # Bottom → left hip → left waist → left shoulder → top
    pts += cubic_bezier((cx, cy+hh),
                        (cx-hw*0.55, cy+hh*0.88),
                        (cx-hw*1.08, cy+hh*0.45),
                        (cx-hw*0.35, cy+hh*0.12))
    pts += cubic_bezier((cx-hw*0.35, cy+hh*0.12),
                        (cx-hw*0.35, cy+hh*0.05),
                        (cx-hw*0.35, cy+hh*0.05),
                        (cx-hw*0.88, cy-hh*0.12))
    pts += cubic_bezier((cx-hw*0.88, cy-hh*0.12),
                        (cx-hw*1.08, cy-hh*0.45),
                        (cx-hw*0.55, cy-hh*0.88),
                        (cx, cy-hh))
    return pts

def draw_arabesque(ax, grid=5, grout=0.04):
    hw, hh = 0.5, 0.65
    # Full tile height = 2*hh. Row spacing = full_height * 0.75
    col_sp = 2*hw + grout
    row_sp = 2*hh * 0.75 + grout  # FIXED: was hh*0.75, should be 2*hh*0.75
    colors = ['#7bafd4', '#8bbfe0', '#6b9fc4', '#9bcbe8']
    for r in range(-1, grid+2):
        for c in range(-1, grid+1):
            cx = c * col_sp
            cy = r * row_sp
            if r % 2 == 1:
                cx += col_sp / 2
            fill_polygon(ax, arabesque_pts(cx, cy, hw, hh),
                         colors[(r*grid+c)%4], '#4a7a9a')


# ═══════════════════════════════════════════
# OGEE — gothic arch: WIDE convex top, narrow concave bottom taper
# NOT vertically symmetric — top is wider than bottom
# ═══════════════════════════════════════════

def ogee_pts(cx, cy, hw, hh):
    pts = []
    # Top point
    # Right upper: convex arch bowing far outward
    pts += cubic_bezier((cx, cy-hh),
                        (cx+hw*0.75, cy-hh*0.9),
                        (cx+hw, cy-hh*0.45),
                        (cx+hw, cy-hh*0.05))
    # Right lower: concave taper to pointed bottom
    pts += cubic_bezier((cx+hw, cy-hh*0.05),
                        (cx+hw, cy+hh*0.3),
                        (cx+hw*0.35, cy+hh*0.75),
                        (cx, cy+hh))
    # Left lower: mirror
    pts += cubic_bezier((cx, cy+hh),
                        (cx-hw*0.35, cy+hh*0.75),
                        (cx-hw, cy+hh*0.3),
                        (cx-hw, cy-hh*0.05))
    # Left upper: mirror
    pts += cubic_bezier((cx-hw, cy-hh*0.05),
                        (cx-hw, cy-hh*0.45),
                        (cx-hw*0.75, cy-hh*0.9),
                        (cx, cy-hh))
    return pts

def draw_ogee(ax, grid=5, grout=0.04):
    hw, hh = 0.45, 0.8
    col_sp = 2*hw + grout
    row_sp = 2*hh * 0.5 + grout  # FIXED: was hh*0.5
    colors = ['#e8d5b5', '#f0ddc0', '#dcc8a5', '#e5d2b0']
    for r in range(-1, grid+2):
        for c in range(-1, grid+1):
            cx = c * col_sp
            cy = r * row_sp
            if r % 2 == 1:
                cx += col_sp / 2
            fill_polygon(ax, ogee_pts(cx, cy, hw, hh), colors[(r*grid+c)%4], '#a08060')


# ═══════════════════════════════════════════
# LEAF — narrow, elongated, sharp tips
# ═══════════════════════════════════════════

def leaf_pts(cx, cy, hw, hh):
    leafW = min(hw, hh * 0.465)
    pts = []
    pts += cubic_bezier((cx, cy-hh),
                        (cx+leafW*0.55, cy-hh*0.85),
                        (cx+leafW*0.95, cy-hh*0.35),
                        (cx+leafW, cy))
    pts += cubic_bezier((cx+leafW, cy),
                        (cx+leafW*0.95, cy+hh*0.35),
                        (cx+leafW*0.55, cy+hh*0.85),
                        (cx, cy+hh))
    pts += cubic_bezier((cx, cy+hh),
                        (cx-leafW*0.55, cy+hh*0.85),
                        (cx-leafW*0.95, cy+hh*0.35),
                        (cx-leafW, cy))
    pts += cubic_bezier((cx-leafW, cy),
                        (cx-leafW*0.95, cy-hh*0.35),
                        (cx-leafW*0.55, cy-hh*0.85),
                        (cx, cy-hh))
    return pts

def draw_leaf(ax, grid=5, grout=0.04):
    hw, hh = 0.35, 0.75
    col_sp = 2*hw + grout
    row_sp = 2*hh * 0.5 + grout  # FIXED
    colors = ['#c8c8c8', '#d8d8d8', '#b8b8b8', '#e0e0e0']
    for r in range(-1, grid+2):
        for c in range(-1, grid+1):
            cx = c * col_sp
            cy = r * row_sp
            if r % 2 == 1:
                cx += col_sp / 2
            fill_polygon(ax, leaf_pts(cx, cy, hw, hh), colors[(r*grid+c)%4], '#909090')


# ═══════════════════════════════════════════
# FISHSCALE
# ═══════════════════════════════════════════

def fishscale_pts(cx, cy, rw):
    stem_len = rw * 0.5
    total_h = rw + stem_len
    flat_y = cy - total_h/2 + rw
    stem_y = cy + total_h/2
    pts = arc_points(cx, flat_y, rw, np.pi, 2*np.pi, n=30)
    pts += quad_bezier((cx+rw, flat_y), (cx+rw*0.15, flat_y+(stem_y-flat_y)*0.45), (cx, stem_y), n=15)
    pts += quad_bezier((cx, stem_y), (cx-rw*0.15, flat_y+(stem_y-flat_y)*0.45), (cx-rw, flat_y), n=15)
    return pts

def draw_fishscale(ax, grid=6, grout=0.03):
    rw = 0.4
    subW = 2*rw
    col_sp = subW + grout
    stem_len = rw * 0.5
    row_sp = stem_len + grout  # This one is correct — row spacing is just stem length
    colors = ['#7ec8c8', '#8ed8d8', '#6eb8b8', '#9edede']
    for r in range(-2, grid+2):
        for c in range(-1, grid+1):
            cx = c * col_sp
            cy = r * row_sp
            if r % 2 == 1:
                cx += col_sp / 2
            fill_polygon(ax, fishscale_pts(cx, cy, rw), colors[(r*grid+c)%4], '#4a8a8a')


# ═══════════════════════════════════════════
# CHEVRON — tight V-pattern, no row gaps
# ═══════════════════════════════════════════

def chevron_pts(cx, cy, hw, hh, col):
    skew = min(hw, hh) * 0.45
    sk = skew if col % 2 == 0 else -skew
    return [
        (cx - hw + sk, cy - hh),
        (cx + hw + sk, cy - hh),
        (cx + hw - sk, cy + hh),
        (cx - hw - sk, cy + hh),
    ]

def draw_chevron(ax, grid=5, grout=0.03):
    hw, hh = 0.3, 0.9
    skew = min(hw, hh) * 0.45
    col_sp = 2*hw + skew + grout  # account for parallelogram lean
    row_sp = 2*hh + grout
    colors = ['#d4a574', '#c49564', '#e4b584', '#b48554']
    for r in range(-1, grid+1):
        for c in range(-1, grid+2):
            cx = c * col_sp
            cy = r * row_sp
            fill_polygon(ax, chevron_pts(cx, cy, hw, hh, c), colors[(r*grid+c)%4], '#8a6a4a')


# ═══════════════════════════════════════════

if __name__ == '__main__':
    print('Rendering v2...')
    render_shape('Star & Cross (k=0.42)', draw_starcross, 'starcross_v2.png')
    render_shape('Arabesque / Lantern v2', draw_arabesque, 'arabesque_v2.png')
    render_shape('Ogee / Provençal v2', draw_ogee, 'ogee_v2.png')
    render_shape('Leaf / Teardrop v2', draw_leaf, 'leaf_v2.png')
    render_shape('Fish Scale v2', draw_fishscale, 'fishscale_v2.png')
    render_shape('Chevron v2', draw_chevron, 'chevron_v2.png')
    print(f'Done → {OUT_DIR}/')
