#!/usr/bin/env python3
"""
Star & Cross tile pattern renderer.
Renders the pattern with configurable parameters and outputs PNG for visual comparison.
"""
import math
import os

# Try to use matplotlib, fall back to pure PIL/Pillow
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ═══════════════════════════════════════════
# Pattern Parameters
# ═══════════════════════════════════════════

# Unit cell size in pixels
CELL = 200

# Star tip-to-tip as fraction of cell
STAR_RATIO = 0.94

# Concavity: inner vertex distance / tip radius
# Lower = more concave (deeper notches, wider cross arms)
# Higher = less concave (shallow notches, narrower cross arms)
CONCAVITY_K = 0.48

# Grout width in pixels
GROUT = 4

# Colors
STAR_COLOR = '#3d7a6a'
CROSS_COLOR = '#f0e8d4'
GROUT_COLOR = '#c0b8a0'

# Canvas
COLS = 5
ROWS = 5
WIDTH = CELL * COLS + CELL
HEIGHT = CELL * ROWS + CELL

# ═══════════════════════════════════════════
# Geometry Functions
# ═══════════════════════════════════════════

def star_vertices(cx, cy, R, inR):
    """8-vertex 4-pointed star with straight concave sides."""
    return [
        (cx, cy - R),           # top tip
        (cx + inR, cy - inR),   # inner upper-right
        (cx + R, cy),           # right tip
        (cx + inR, cy + inR),   # inner lower-right
        (cx, cy + R),           # bottom tip
        (cx - inR, cy + inR),   # inner lower-left
        (cx - R, cy),           # left tip
        (cx - inR, cy - inR),   # inner upper-left
    ]

def cross_vertices(cx, cy, S, R, inR, g):
    """12-vertex tapered plus sign (complement of star)."""
    a = S/2 - inR - g/2    # arm half-width at base (notch)
    b = max(S/2 - R + g/2, 1)  # arm half-width at tip
    arm = S/2 - g/2             # arm length from center

    return [
        # N arm (clockwise)
        (cx - a, cy - a),       # NW notch
        (cx - b, cy - arm),     # N tip left
        (cx + b, cy - arm),     # N tip right
        (cx + a, cy - a),       # NE notch
        # E arm
        (cx + arm, cy - b),     # E tip top
        (cx + arm, cy + b),     # E tip bottom
        (cx + a, cy + a),       # SE notch
        # S arm
        (cx + b, cy + arm),     # S tip right
        (cx - b, cy + arm),     # S tip left
        (cx - a, cy + a),       # SW notch
        # W arm
        (cx - arm, cy + b),     # W tip bottom
        (cx - arm, cy - b),     # W tip top
    ]

def polygon_area(verts):
    """Shoelace formula for polygon area."""
    n = len(verts)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += verts[i][0] * verts[j][1]
        area -= verts[j][0] * verts[i][1]
    return abs(area) / 2

# ═══════════════════════════════════════════
# Parameter Sweep
# ═══════════════════════════════════════════

def sweep_parameters():
    """Render a grid of patterns with different star_ratio and concavity_k values."""
    ratios = [0.90, 0.92, 0.94, 0.96, 0.98]
    ks = [0.40, 0.45, 0.50, 0.55, 0.60]

    cell = 120
    g = 3
    margin = 40

    cols = len(ratios)
    rows = len(ks)

    tile_w = cell * 3
    tile_h = cell * 3

    total_w = cols * (tile_w + margin) + margin
    total_h = rows * (tile_h + margin) + margin + 30  # extra for labels

    if not HAS_PIL:
        print("PIL/Pillow not available for sweep rendering")
        return

    img = Image.new('RGB', (total_w, total_h), GROUT_COLOR)
    draw = ImageDraw.Draw(img)

    for ri, ratio in enumerate(ratios):
        for ki, k in enumerate(ks):
            ox = margin + ri * (tile_w + margin)
            oy = margin + 30 + ki * (tile_h + margin)

            R = cell * ratio / 2
            inR = R * k

            # Draw 3x3 grid of pattern
            for row in range(-1, 3):
                for col in range(-1, 3):
                    sx = ox + cell * 1.5 + col * cell
                    sy = oy + cell * 1.5 + row * cell

                    # Star
                    sv = star_vertices(sx, sy, R - g/2, inR - g/2*k)
                    draw.polygon(sv, fill=STAR_COLOR)

                    # Cross
                    cv = cross_vertices(sx + cell/2, sy + cell/2, cell, R, inR, g)
                    draw.polygon(cv, fill=CROSS_COLOR)

            # Clip to tile area
            # Draw border
            draw.rectangle([ox, oy, ox + tile_w, oy + tile_h], outline='#333', width=2)

            # Label
            label = f'r={ratio:.2f} k={k:.2f}'
            draw.text((ox + 5, oy + 5), label, fill='#000')

    # Column headers
    for ri, ratio in enumerate(ratios):
        x = margin + ri * (tile_w + margin) + tile_w // 2
        draw.text((x - 30, 5), f'ratio={ratio}', fill='#333')

    # Row headers
    for ki, k in enumerate(ks):
        y = margin + 30 + ki * (tile_h + margin) + tile_h // 2
        draw.text((5, y - 8), f'k={k}', fill='#333')

    outpath = os.path.join(os.path.dirname(__file__), 'starcross_sweep.png')
    img.save(outpath)
    print(f'Saved parameter sweep: {outpath}')
    return outpath

# ═══════════════════════════════════════════
# Single Pattern Render
# ═══════════════════════════════════════════

def render_pattern(star_ratio=STAR_RATIO, concavity_k=CONCAVITY_K, cell=CELL,
                   grout=GROUT, filename='starcross_pattern.png'):
    """Render a single star & cross pattern."""

    R = cell * star_ratio / 2
    inR = R * concavity_k
    g = grout

    cols, rows = 4, 4
    w = cell * (cols + 1)
    h = cell * (rows + 1)

    if not HAS_PIL:
        print("PIL/Pillow not available")
        return

    img = Image.new('RGB', (w, h), GROUT_COLOR)
    draw = ImageDraw.Draw(img)

    ox = cell // 2
    oy = cell // 2

    for row in range(-1, rows + 1):
        for col in range(-1, cols + 1):
            sx = ox + col * cell
            sy = oy + row * cell

            # Star (shrink by grout for visual gap)
            sv = star_vertices(sx, sy, R - g/2, (R - g/2) * concavity_k)
            draw.polygon(sv, fill=STAR_COLOR)

            # Cross
            cv = cross_vertices(sx + cell/2, sy + cell/2, cell, R, inR, g)
            draw.polygon(cv, fill=CROSS_COLOR)

    # Print metrics
    star_area = polygon_area(star_vertices(0, 0, R, inR))
    cross_area = polygon_area(cross_vertices(0, 0, cell, R, inR, g))
    cell_area = cell * cell
    coverage = (star_area + cross_area) / cell_area * 100
    tip_gap = cell - 2 * R
    arm_base = cell - 2 * inR - g
    arm_tip = cell - 2 * R + g

    print(f'\n{"═"*50}')
    print(f'Star & Cross Pattern Parameters')
    print(f'{"═"*50}')
    print(f'Cell size:       {cell}px')
    print(f'Star ratio:      {star_ratio} (tip-to-tip = {2*R:.1f}px)')
    print(f'Concavity k:     {concavity_k} (inner vertex = {inR:.1f}px from center)')
    print(f'Grout:           {g}px')
    print(f'{"─"*50}')
    print(f'Star area:       {star_area:.0f}px²')
    print(f'Cross area:      {cross_area:.0f}px²')
    print(f'Cell area:       {cell_area:.0f}px²')
    print(f'Tile coverage:   {coverage:.1f}%')
    print(f'Tip gap:         {tip_gap:.1f}px (target: ~{g}px)')
    print(f'Cross arm base:  {arm_base:.1f}px')
    print(f'Cross arm tip:   {arm_tip:.1f}px')
    print(f'{"═"*50}\n')

    outpath = os.path.join(os.path.dirname(__file__), filename)
    img.save(outpath)
    print(f'Saved: {outpath}')
    return outpath

# ═══════════════════════════════════════════
# Comparison render: multiple ratios side by side
# ═══════════════════════════════════════════

def render_comparison():
    """Render 3 versions side by side for comparison."""
    configs = [
        {'label': 'A: r=0.92 k=0.45', 'star_ratio': 0.92, 'k': 0.45},
        {'label': 'B: r=0.94 k=0.48', 'star_ratio': 0.94, 'k': 0.48},
        {'label': 'C: r=0.94 k=0.52', 'star_ratio': 0.94, 'k': 0.52},
        {'label': 'D: r=0.96 k=0.50', 'star_ratio': 0.96, 'k': 0.50},
    ]

    cell = 150
    g = 3
    tile_count = 3
    tile_size = cell * tile_count
    margin = 20
    label_h = 25

    total_w = len(configs) * (tile_size + margin) + margin
    total_h = tile_size + margin * 2 + label_h

    if not HAS_PIL:
        print("PIL/Pillow not available")
        return

    img = Image.new('RGB', (total_w, total_h), '#222222')
    draw = ImageDraw.Draw(img)

    for ci, cfg in enumerate(configs):
        ox_base = margin + ci * (tile_size + margin)
        oy_base = margin + label_h

        R = cell * cfg['star_ratio'] / 2
        inR = R * cfg['k']

        for row in range(-1, tile_count + 1):
            for col in range(-1, tile_count + 1):
                sx = ox_base + cell // 2 + col * cell
                sy = oy_base + cell // 2 + row * cell

                sv = star_vertices(sx, sy, R - g/2, (R - g/2) * cfg['k'])
                draw.polygon(sv, fill=STAR_COLOR)

                cv = cross_vertices(sx + cell/2, sy + cell/2, cell, R, inR, g)
                draw.polygon(cv, fill=CROSS_COLOR)

        # Border
        draw.rectangle([ox_base, oy_base, ox_base + tile_size, oy_base + tile_size],
                       outline='#555', width=2)

        # Label
        draw.text((ox_base + 5, margin + 2), cfg['label'], fill='#ffffff')

    outpath = os.path.join(os.path.dirname(__file__), 'starcross_comparison.png')
    img.save(outpath)
    print(f'Saved comparison: {outpath}')
    return outpath

# ═══════════════════════════════════════════
# Main
# ═══════════════════════════════════════════

if __name__ == '__main__':
    print('Rendering star & cross patterns...\n')

    # Single pattern with current params
    render_pattern()

    # Comparison of different parameter combos
    render_comparison()

    # Full parameter sweep
    sweep_parameters()

    print('\nDone! Open the PNG files to compare with reference images.')
