"""v6: 8-pointed star + simple cross, correct proportions."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), 'output', 'shape_tests')
os.makedirs(OUT, exist_ok=True)

INNER_RATIO = np.sqrt(2 - np.sqrt(2))  # 0.7654

def fpoly(ax, pts, c, e='#8b7355', lw=0.8):
    from matplotlib.patches import Polygon
    ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=e, linewidth=lw))

def star8(cx, cy, R):
    ri = R * INNER_RATIO
    pts = []
    for i in range(16):
        a = i * np.pi/8 - np.pi/2
        r = R if i%2==0 else ri
        pts.append((cx + r*np.cos(a), cy + r*np.sin(a)))
    return pts

def plus_cross(cx, cy, arm_hw, arm_hl):
    """Simple + cross as 12-vertex polygon."""
    w, l = arm_hw, arm_hl
    return [
        (cx-w, cy-l), (cx+w, cy-l),  # top of N arm
        (cx+w, cy-w), (cx+l, cy-w),  # inner NE → E arm top
        (cx+l, cy+w), (cx+w, cy+w),  # E arm bottom → inner SE
        (cx+w, cy+l), (cx-w, cy+l),  # S arm bottom
        (cx-w, cy+w), (cx-l, cy+w),  # inner SW → W arm bottom
        (cx-l, cy-w), (cx-w, cy-w),  # W arm top → inner NW
    ]

def render(name, fn, fname):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal'); ax.set_facecolor('#e8e0d0')
    fn(ax)
    ax.set_title(name, fontsize=16, fontweight='bold')
    ax.autoscale()
    m=0.2; xl,xr=ax.get_xlim(); yl,yr=ax.get_ylim()
    ax.set_xlim(xl-m,xr+m); ax.set_ylim(yl-m,yr+m)
    ax.set_xticks([]); ax.set_yticks([])
    p = os.path.join(OUT, fname)
    fig.savefig(p, dpi=150, bbox_inches='tight', facecolor='#e8e0d0')
    plt.close(); print(f'  {fname}')

def draw(ax):
    R = 0.5
    g = 0.03
    pitch = 2*R + g

    # Cross arm proportions: derived from star geometry
    # arm_hw = R * sin(pi/8) = distance matching the star's inner notch
    arm_hw = R * np.sin(np.pi/8)  # ≈ 0.191*R... actually 0.383*R
    # Wait, sin(pi/8) = sin(22.5°) = 0.383
    arm_hw = R * 0.383
    arm_hl = R * 0.92

    sc = ['#d4c5a0','#c9b88a','#d0be92','#bfad7e']
    cc = ['#7a9b7a','#8aab8a','#98b898','#6b8b6b']

    for r in range(7):
        for c in range(7):
            x, y = c*pitch, r*pitch
            # Star
            fpoly(ax, star8(x, y, R-g/2), sc[(r*7+c)%4])
            # Cross at offset
            if c < 6 and r < 6:
                cx, cy = x+pitch/2, y+pitch/2
                fpoly(ax, plus_cross(cx, cy, arm_hw, arm_hl), cc[(r*7+c)%4])

if __name__ == '__main__':
    print('v6...')
    render('8-Point Star + Cross', draw, 'star8_plus_v6.png')
    print('Done')
