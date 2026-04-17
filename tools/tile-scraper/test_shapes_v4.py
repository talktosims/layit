"""v4: 8-pointed star (real cement tile geometry), improved arabesque."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), 'output', 'shape_tests')
os.makedirs(OUT, exist_ok=True)

def cbez(p0,p1,p2,p3,n=30):
    t=np.linspace(0,1,n)
    x=(1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t**2*p2[0]+t**3*p3[0]
    y=(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t**2*p2[1]+t**3*p3[1]
    return list(zip(x,y))

def fpoly(ax,pts,c='#d4c5a9',e='#8b7355',lw=0.8):
    from matplotlib.patches import Polygon
    ax.add_patch(Polygon(pts,closed=True,facecolor=c,edgecolor=e,linewidth=lw))

def render(name,fn,fname):
    fig,ax=plt.subplots(figsize=(10,10)); ax.set_aspect('equal'); ax.set_facecolor('#e8e0d0')
    fn(ax); ax.set_title(name,fontsize=16,fontweight='bold'); ax.autoscale()
    m=0.3; xl,xr=ax.get_xlim(); yl,yr=ax.get_ylim()
    ax.set_xlim(xl-m,xr+m); ax.set_ylim(yl-m,yr+m)
    ax.set_xticks([]); ax.set_yticks([])
    p=os.path.join(OUT,fname)
    fig.savefig(p,dpi=150,bbox_inches='tight',facecolor='#e8e0d0'); plt.close(); print(f'  {fname}')


# ═══════════════════════════════════════════
# 8-POINTED STAR & CROSS — proper cement tile geometry
# Star: 16-vertex polygon, alternating outer radius R and inner radius ri
# Cross: fills gap between 4 stars
# ═══════════════════════════════════════════

def star8_pts(cx, cy, R, ri):
    """8-pointed star as 16-vertex polygon."""
    pts = []
    for i in range(16):
        angle = i * np.pi / 8 - np.pi / 2  # start from top
        r = R if i % 2 == 0 else ri
        pts.append((cx + r * np.cos(angle), cy + r * np.sin(angle)))
    return pts

def cross_pts(cx, cy, R, ri):
    """Cross/filler shape — complement of star, fills the gap between 4 stars.
    Constructed as a rotated star with swapped radii: tips where star has notches."""
    pts = []
    for i in range(16):
        # Offset by 22.5° (one half-step) so cross tips point between star tips
        angle = i * np.pi / 8 - np.pi / 2 + np.pi / 16
        # Cross is the "inverse" — wide where star is narrow
        r = R * 0.92 if i % 2 == 0 else ri * 0.85
        pts.append((cx + r * np.cos(angle), cy + r * np.sin(angle)))
    return pts

def draw_starcross_8pt(ax):
    R = 0.5  # outer tip radius
    ri = R * 0.62  # inner notch radius (waist ~62% of tip)
    grout = 0.04
    pitch = 2 * R + grout

    star_c = ['#c9b88a', '#d4c5a0', '#bfad7e', '#c2b590']
    cross_c = ['#8aab8a', '#9ab89a', '#7a9b7a', '#88aa88']

    for r in range(6):
        for c in range(6):
            x, y = c * pitch, r * pitch
            fpoly(ax, star8_pts(x, y, R, ri), star_c[(r*6+c) % 4])
            # Cross at half-pitch offset
            if c < 5 and r < 5:
                fpoly(ax, cross_pts(x + pitch/2, y + pitch/2, R, ri),
                      cross_c[(r*6+c) % 4])


# Try different inner radius values
def draw_starcross_ri55(ax):
    R = 0.5; ri = R * 0.55; grout = 0.04; pitch = 2*R + grout
    sc = ['#c9b88a','#d4c5a0','#bfad7e','#c2b590']
    cc = ['#8aab8a','#9ab89a','#7a9b7a','#88aa88']
    for r in range(6):
        for c in range(6):
            fpoly(ax, star8_pts(c*pitch, r*pitch, R, ri), sc[(r*6+c)%4])
            if c<5 and r<5:
                fpoly(ax, cross_pts(c*pitch+pitch/2, r*pitch+pitch/2, R, ri), cc[(r*6+c)%4])

def draw_starcross_ri45(ax):
    R = 0.5; ri = R * 0.45; grout = 0.04; pitch = 2*R + grout
    sc = ['#c9b88a','#d4c5a0','#bfad7e','#c2b590']
    cc = ['#8aab8a','#9ab89a','#7a9b7a','#88aa88']
    for r in range(6):
        for c in range(6):
            fpoly(ax, star8_pts(c*pitch, r*pitch, R, ri), sc[(r*6+c)%4])
            if c<5 and r<5:
                fpoly(ax, cross_pts(c*pitch+pitch/2, r*pitch+pitch/2, R, ri), cc[(r*6+c)%4])


# ═══════════════════════════════════════════
# ARABESQUE — 8-curve lantern (same as v3)
# ═══════════════════════════════════════════

def arab_pts(cx, cy, hw, hh):
    pts = []
    pts += cbez((cx,cy-hh),(cx+hw*0.4,cy-hh*0.95),(cx+hw*0.85,cy-hh*0.7),(cx+hw,cy-hh*0.25))
    pts += cbez((cx+hw,cy-hh*0.25),(cx+hw*1.02,cy+hh*0.05),(cx+hw*0.52,cy-hh*0.02),(cx+hw*0.38,cy))
    pts += cbez((cx+hw*0.38,cy),(cx+hw*0.52,cy+hh*0.02),(cx+hw*1.02,cy-hh*0.05),(cx+hw,cy+hh*0.25))
    pts += cbez((cx+hw,cy+hh*0.25),(cx+hw*0.85,cy+hh*0.7),(cx+hw*0.4,cy+hh*0.95),(cx,cy+hh))
    pts += cbez((cx,cy+hh),(cx-hw*0.4,cy+hh*0.95),(cx-hw*0.85,cy+hh*0.7),(cx-hw,cy+hh*0.25))
    pts += cbez((cx-hw,cy+hh*0.25),(cx-hw*1.02,cy-hh*0.05),(cx-hw*0.52,cy+hh*0.02),(cx-hw*0.38,cy))
    pts += cbez((cx-hw*0.38,cy),(cx-hw*0.52,cy-hh*0.02),(cx-hw*1.02,cy+hh*0.05),(cx-hw,cy-hh*0.25))
    pts += cbez((cx-hw,cy-hh*0.25),(cx-hw*0.85,cy-hh*0.7),(cx-hw*0.4,cy-hh*0.95),(cx,cy-hh))
    return pts

def draw_arab(ax):
    hw, hh = 0.5, 0.65
    col_sp = 2*hw + 0.04
    row_sp = 2*hh * 0.75 + 0.04
    cs = ['#7bafd4','#8bbfe0','#6b9fc4','#9bcbe8']
    for r in range(-1, 7):
        for c in range(-1, 6):
            cx = c * col_sp; cy = r * row_sp
            if r % 2 == 1: cx += col_sp / 2
            fpoly(ax, arab_pts(cx, cy, hw, hh), cs[(r*6+c)%4], '#4a7a9a')


if __name__ == '__main__':
    print('v4...')
    render('8-Point Star & Cross (ri=0.62)', draw_starcross_8pt, 'star8_ri62.png')
    render('8-Point Star & Cross (ri=0.55)', draw_starcross_ri55, 'star8_ri55.png')
    render('8-Point Star & Cross (ri=0.45)', draw_starcross_ri45, 'star8_ri45.png')
    render('Arabesque Lantern', draw_arab, 'arabesque_v4.png')
    print('Done')
