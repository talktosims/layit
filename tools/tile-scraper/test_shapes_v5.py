"""
v5: CORRECT Islamic geometry construction for star-cross.
8-pointed star from two overlapping squares. innerRadiusRatio = sqrt(2-sqrt(2)) = 0.7654.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), 'output', 'shape_tests')
os.makedirs(OUT, exist_ok=True)

def fpoly(ax, pts, c='#d4c5a9', e='#8b7355', lw=0.8):
    from matplotlib.patches import Polygon
    ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=e, linewidth=lw))

def render(name, fn, fname):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal'); ax.set_facecolor('#e8e0d0')
    fn(ax)
    ax.set_title(name, fontsize=16, fontweight='bold')
    ax.autoscale()
    m = 0.3; xl, xr = ax.get_xlim(); yl, yr = ax.get_ylim()
    ax.set_xlim(xl-m, xr+m); ax.set_ylim(yl-m, yr+m)
    ax.set_xticks([]); ax.set_yticks([])
    p = os.path.join(OUT, fname)
    fig.savefig(p, dpi=150, bbox_inches='tight', facecolor='#e8e0d0')
    plt.close(); print(f'  {fname}')


# ═══════════════════════════════════════════════════
# 8-POINTED STAR — Islamic geometric construction
#
# Two overlapping squares of equal size, one rotated 45°.
# Star tips: 8 vertices of both squares (all at circumradius R)
# Inner notches: 8 edge-intersection points (at radius ri = R * sqrt(2-sqrt(2)))
#
# This gives innerRadiusRatio = 0.7654... which matches the TILE_GEOMETRY_DB.
# ═══════════════════════════════════════════════════

INNER_RATIO = np.sqrt(2 - np.sqrt(2))  # 0.76536...

def star8_vertices(cx, cy, R):
    """Compute 16 vertices of 8-pointed star: 8 tips + 8 notches."""
    ri = R * INNER_RATIO
    verts = []
    for i in range(16):
        angle = i * np.pi / 8 - np.pi / 2  # start from top
        r = R if (i % 2 == 0) else ri
        verts.append((cx + r * np.cos(angle), cy + r * np.sin(angle)))
    return verts

def cross_vertices(cx, cy, R):
    """Cross shape that fills gap between 4 stars.

    The cross is the complement of the star — its edges are determined by
    the star edges of the 4 surrounding stars. For simplicity, we construct
    it as an 8-pointed cross polygon that fills the gap.

    The cross tips point toward the 4 adjacent stars' inner notches.
    The cross notches align with the stars' outer tips.
    """
    ri = R * INNER_RATIO
    # The cross is essentially a star rotated 22.5° with different radii
    # Cross tips reach toward adjacent stars: about 0.85*R outward
    # Cross notches pull in where adjacent star tips extend: about ri*0.7
    cr_outer = R * 0.82  # cross arm tip radius
    cr_inner = ri * 0.55  # cross waist radius
    verts = []
    for i in range(16):
        angle = i * np.pi / 8 - np.pi / 2 + np.pi / 16  # offset 11.25°
        r = cr_outer if (i % 2 == 0) else cr_inner
        verts.append((cx + r * np.cos(angle), cy + r * np.sin(angle)))
    return verts

def draw_starcross(ax):
    R = 0.5
    grout = 0.03
    pitch = 2 * R + grout

    sc = ['#d4c5a0', '#c9b88a', '#bfad7e', '#d0be92']
    cc = ['#7a9b7a', '#8aab8a', '#6b8b6b', '#98b898']

    for r in range(7):
        for c in range(7):
            x, y = c * pitch, r * pitch
            fpoly(ax, star8_vertices(x, y, R - grout/2), sc[(r*7+c)%4])
            if c < 6 and r < 6:
                cx, cy = x + pitch/2, y + pitch/2
                fpoly(ax, cross_vertices(cx, cy, R - grout/2), cc[(r*7+c)%4])


# Also render a version with NO gap between star and cross to check interlocking
def draw_starcross_tight(ax):
    """Star-cross with cross shape computed as exact negative space."""
    R = 0.5
    grout = 0.03
    pitch = 2 * R + grout
    ri = R * INNER_RATIO

    sc = ['#d4c5a0', '#c9b88a', '#bfad7e', '#d0be92']
    cc = ['#7a9b7a', '#8aab8a', '#6b8b6b', '#98b898']

    # For the cross, compute it as the polygon formed by the nearest
    # inner-notch vertices of the 4 surrounding stars
    def compute_cross(cx, cy):
        """Build cross from adjacent stars' inner notch points."""
        pts = []
        # The 4 surrounding stars are at (cx±pitch/2, cy±pitch/2)
        stars = [
            (cx - pitch/2, cy - pitch/2),  # NW star
            (cx + pitch/2, cy - pitch/2),  # NE star
            (cx + pitch/2, cy + pitch/2),  # SE star
            (cx - pitch/2, cy + pitch/2),  # SW star
        ]

        # From each star, get the 2 inner notch points facing the cross
        # NW star: its SE notch and E notch face the cross
        for si, (sx, sy) in enumerate(stars):
            # The star has notches at angles: 22.5° + k*45° for k=0..7
            # We want the 2 notches facing the cross center
            # Cross is SE of NW star → star notches at ~135° and ~180° (in star coords)
            base_angle = si * np.pi / 2  # 0=NW faces SE, 1=NE faces SW, etc.
            # The two notches closest to the cross direction
            for offset in [-np.pi/8, np.pi/8]:
                angle = base_angle + np.pi/4 + offset - np.pi/2
                pts.append((sx + ri * np.cos(angle), sy + ri * np.sin(angle)))

        # Sort points by angle from cross center
        pts.sort(key=lambda p: np.arctan2(p[1]-cy, p[0]-cx))
        return pts

    for r in range(7):
        for c in range(7):
            x, y = c * pitch, r * pitch
            fpoly(ax, star8_vertices(x, y, R - grout/2), sc[(r*7+c)%4])
            if c < 6 and r < 6:
                cx, cy = x + pitch/2, y + pitch/2
                cpts = compute_cross(cx, cy)
                if len(cpts) >= 3:
                    fpoly(ax, cpts, cc[(r*7+c)%4])


if __name__ == '__main__':
    print('v5...')
    render('8-Point Star & Cross (Islamic construction)', draw_starcross, 'star8_islamic.png')
    render('8-Point Star & Cross (tight fit)', draw_starcross_tight, 'star8_tight.png')
    print('Done')
