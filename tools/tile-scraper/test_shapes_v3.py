"""v3: Matches index.html exactly — star k=0.42, arabesque 8-curve lantern."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), 'output', 'shape_tests')
os.makedirs(OUT, exist_ok=True)

def qbez(p0,p1,p2,n=30):
    t=np.linspace(0,1,n); x=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t**2*p2[0]; y=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t**2*p2[1]; return list(zip(x,y))
def cbez(p0,p1,p2,p3,n=30):
    t=np.linspace(0,1,n); x=(1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t**2*p2[0]+t**3*p3[0]; y=(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t**2*p2[1]+t**3*p3[1]; return list(zip(x,y))
def arc_pts(cx,cy,r,a0,a1,n=30): a=np.linspace(a0,a1,n); return [(cx+r*np.cos(t),cy+r*np.sin(t)) for t in a]

def fpoly(ax,pts,c='#d4c5a9',e='#8b7355',lw=0.8):
    from matplotlib.patches import Polygon; ax.add_patch(Polygon(pts,closed=True,facecolor=c,edgecolor=e,linewidth=lw))

def render(name,fn,fname):
    fig,ax=plt.subplots(figsize=(10,10)); ax.set_aspect('equal'); ax.set_facecolor('#e8e0d0')
    fn(ax); ax.set_title(name,fontsize=16,fontweight='bold'); ax.autoscale()
    m=0.2; xl,xr=ax.get_xlim(); yl,yr=ax.get_ylim(); ax.set_xlim(xl-m,xr+m); ax.set_ylim(yl-m,yr+m)
    ax.set_xticks([]); ax.set_yticks([]); p=os.path.join(OUT,fname)
    fig.savefig(p,dpi=150,bbox_inches='tight',facecolor='#e8e0d0'); plt.close(); print(f'  {fname}')

# ── STAR & CROSS k=0.42 ──
def star(cx,cy,hw,hh,k):
    return qbez((cx,cy-hh),(cx+hw*k,cy-hh*k),(cx+hw,cy))+qbez((cx+hw,cy),(cx+hw*k,cy+hh*k),(cx,cy+hh))+qbez((cx,cy+hh),(cx-hw*k,cy+hh*k),(cx-hw,cy))+qbez((cx-hw,cy),(cx-hw*k,cy-hh*k),(cx,cy-hh))
def cross(cx,cy,hw,hh,k):
    return qbez((cx,cy-hh),(cx+hw*(1-k),cy+hh*(k-1)),(cx+hw,cy))+qbez((cx+hw,cy),(cx+hw*(1-k),cy+hh*(1-k)),(cx,cy+hh))+qbez((cx,cy+hh),(cx+hw*(k-1),cy+hh*(1-k)),(cx-hw,cy))+qbez((cx-hw,cy),(cx+hw*(k-1),cy+hh*(k-1)),(cx,cy-hh))

def draw_sc(ax):
    k=0.42; hw=hh=0.5; p=2*hw+0.04; sc=['#c9b88a','#d4c5a0','#bfad7e','#c2b590']; cc=['#8aab8a','#9ab89a','#7a9b7a','#88aa88']
    for r in range(5):
        for c in range(5):
            fpoly(ax,star(c*p,r*p,hw,hh,k),sc[(r*5+c)%4])
            if c<4 and r<4: fpoly(ax,cross(c*p+p/2,r*p+p/2,hw,hh,k),cc[(r*5+c)%4])

# ── ARABESQUE 8-curve lantern ──
def arab(cx,cy,hw,hh):
    pts=[]
    pts+=cbez((cx,cy-hh),(cx+hw*0.4,cy-hh*0.95),(cx+hw*0.85,cy-hh*0.7),(cx+hw,cy-hh*0.25))
    pts+=cbez((cx+hw,cy-hh*0.25),(cx+hw*1.02,cy+hh*0.05),(cx+hw*0.52,cy-hh*0.02),(cx+hw*0.38,cy))
    pts+=cbez((cx+hw*0.38,cy),(cx+hw*0.52,cy+hh*0.02),(cx+hw*1.02,cy-hh*0.05),(cx+hw,cy+hh*0.25))
    pts+=cbez((cx+hw,cy+hh*0.25),(cx+hw*0.85,cy+hh*0.7),(cx+hw*0.4,cy+hh*0.95),(cx,cy+hh))
    pts+=cbez((cx,cy+hh),(cx-hw*0.4,cy+hh*0.95),(cx-hw*0.85,cy+hh*0.7),(cx-hw,cy+hh*0.25))
    pts+=cbez((cx-hw,cy+hh*0.25),(cx-hw*1.02,cy-hh*0.05),(cx-hw*0.52,cy+hh*0.02),(cx-hw*0.38,cy))
    pts+=cbez((cx-hw*0.38,cy),(cx-hw*0.52,cy-hh*0.02),(cx-hw*1.02,cy+hh*0.05),(cx-hw,cy-hh*0.25))
    pts+=cbez((cx-hw,cy-hh*0.25),(cx-hw*0.85,cy-hh*0.7),(cx-hw*0.4,cy-hh*0.95),(cx,cy-hh))
    return pts

def draw_arab(ax):
    hw,hh=0.5,0.65; col_sp=2*hw+0.04; row_sp=2*hh*0.75+0.04
    cs=['#7bafd4','#8bbfe0','#6b9fc4','#9bcbe8']
    for r in range(-1,7):
        for c in range(-1,6):
            cx=c*col_sp; cy=r*row_sp
            if r%2==1: cx+=col_sp/2
            fpoly(ax,arab(cx,cy,hw,hh),cs[(r*6+c)%4],'#4a7a9a')

if __name__=='__main__':
    print('v3...')
    render('Star & Cross (k=0.42)',draw_sc,'starcross_v3.png')
    render('Arabesque 8-curve Lantern',draw_arab,'arabesque_v3.png')
    print('Done')
