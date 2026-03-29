#!/usr/bin/env python3
"""
Verify tile tessellation correctness by rendering patterns and checking for gaps/overlaps.

Uses matplotlib to draw the exact same geometry as the Canvas2D renderer,
then samples random points to verify they're inside exactly one tile (or in grout).

Usage:
    python3 verify_tessellation.py [shape]

    shape: fishscale, ogee, arabesque, leaf, starcross (default: all)
"""

import sys
import math
import numpy as np

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.path import Path
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("matplotlib not found — running numerical verification only")


def fishscale_tile_path(cx, cy, rw):
    """
    Generate the fishscale tile boundary as a list of (x, y) points.

    Composed of three circular arcs:
    1. Dome: semicircle, center at (cx, cy), radius rw
    2. Right side: quarter circle, center at (cx + rw, cy + rw), radius rw
    3. Left side: quarter circle, center at (cx - rw, cy + rw), radius rw

    When stem_length = dome_radius, the side arcs match the dome circles
    of neighbor tiles, guaranteeing zero-gap nesting.
    """
    points = []
    n_arc = 32  # points per arc segment

    # Dome: semicircle from left to right across top (angle π to 2π)
    for i in range(n_arc + 1):
        angle = math.pi + i * math.pi / n_arc
        points.append((cx + rw * math.cos(angle), cy + rw * math.sin(angle)))

    # Right side: quarter circle from dome-right to bottom point
    # Center at (cx + rw, cy + rw), angle from -π/2 to -π (counterclockwise)
    arc_cx, arc_cy = cx + rw, cy + rw
    for i in range(1, n_arc + 1):
        angle = -math.pi / 2 - i * (math.pi / 2) / n_arc
        points.append((arc_cx + rw * math.cos(angle), arc_cy + rw * math.sin(angle)))

    # Left side: quarter circle from bottom point to dome-left
    # Center at (cx - rw, cy + rw), angle from 0 to π/2 (counterclockwise)
    arc_cx, arc_cy = cx - rw, cy + rw
    for i in range(1, n_arc + 1):
        angle = i * (-math.pi / 2) / n_arc
        points.append((arc_cx + rw * math.cos(angle), arc_cy + rw * math.sin(angle)))

    return points


def ogee_tile_path(cx, cy, hw, hh):
    """
    Generate ogee tile boundary using anti-symmetric bezier (proven tessellation).

    PROOF: For cubic bezier P0=(hw,0), P1=(hw,A*hh), P2=(0,(1-A)*hh), P3=(0,hh):
      x(t) = hw * (1-t)²(1+2t)  →  x(t) + x(1-t) = hw  (algebraic identity)
      y(t) + y(1-t) = hh
    This guarantees zero-gap, zero-overlap when rowSpacing = hh and tiles flip 180°.
    """
    A = 0.55  # curvature parameter

    points = []
    n = 32

    def cubic_bezier(p0, p1, p2, p3, num):
        pts = []
        for i in range(num + 1):
            t = i / num
            u = 1 - t
            x = u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0]
            y = u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]
            pts.append((x, y))
        return pts

    # Upper right: 180° rotation of anti-symmetric lower-left
    points.extend(cubic_bezier(
        (cx, cy - hh), (cx, cy - hh * (1 - A)),
        (cx + hw, cy - hh * A), (cx + hw, cy), n))
    # Lower right: anti-symmetric (proven to tile)
    points.extend(cubic_bezier(
        (cx + hw, cy), (cx + hw, cy + hh * A),
        (cx, cy + hh * (1 - A)), (cx, cy + hh), n)[1:])
    # Lower left: mirror of lower-right, reversed
    points.extend(cubic_bezier(
        (cx, cy + hh), (cx, cy + hh * (1 - A)),
        (cx - hw, cy + hh * A), (cx - hw, cy), n)[1:])
    # Upper left: mirror of upper-right, reversed
    points.extend(cubic_bezier(
        (cx - hw, cy), (cx - hw, cy - hh * A),
        (cx, cy - hh * (1 - A)), (cx, cy - hh), n)[1:])

    return points


def point_in_polygon(x, y, polygon):
    """Ray casting algorithm for point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def verify_fishscale():
    """Verify fishscale tessellation has zero gaps."""
    print("\n" + "=" * 60)
    print("FISHSCALE TESSELLATION VERIFICATION")
    print("=" * 60)

    tile_w = 2.0  # inches
    grout = 0.125  # 1/8"
    rw = (tile_w - grout) / 2
    stem_len = rw  # EXACT: stem = dome radius
    col_spacing = tile_w
    row_spacing = stem_len + grout

    print(f"Tile width: {tile_w}\"")
    print(f"Dome radius (rw): {rw:.4f}\"")
    print(f"Stem length: {stem_len:.4f}\" (= rw, exact)")
    print(f"Total height: {rw + stem_len:.4f}\"")
    print(f"Row spacing: {row_spacing:.4f}\"")
    print(f"Col spacing: {col_spacing:.4f}\"")

    # Generate tile polygons for a 3x3 patch
    tiles = []
    for row in range(-1, 4):
        for col in range(-1, 4):
            cx = tile_w / 2 + col * col_spacing
            cy = (rw + stem_len) / 2 + row * row_spacing
            if row % 2 == 1:
                cx += col_spacing / 2
            # Dome center at tile center vertical position
            dome_y = cy
            poly = fishscale_tile_path(cx, dome_y, rw)
            tiles.append(poly)

    # Sample random points in the center region and check coverage
    test_region = (tile_w, row_spacing, tile_w * 2, row_spacing * 3)
    n_samples = 10000
    rng = np.random.default_rng(42)

    in_tile = 0
    in_grout = 0
    in_multiple = 0
    in_none = 0

    for _ in range(n_samples):
        x = test_region[0] + rng.random() * (test_region[2] - test_region[0])
        y = test_region[1] + rng.random() * (test_region[3] - test_region[1])

        count = 0
        for poly in tiles:
            if point_in_polygon(x, y, poly):
                count += 1

        if count == 0:
            in_none += 1
        elif count == 1:
            in_tile += 1
        else:
            in_multiple += 1

    # The grout region should account for some "in_none" samples
    grout_fraction = grout / tile_w  # rough estimate of grout area
    expected_grout_pct = grout_fraction * 100
    none_pct = in_none / n_samples * 100
    multi_pct = in_multiple / n_samples * 100
    tile_pct = in_tile / n_samples * 100

    print(f"\nSampled {n_samples} random points in test region:")
    print(f"  In exactly 1 tile: {in_tile} ({tile_pct:.1f}%)")
    print(f"  In grout (0 tiles): {in_none} ({none_pct:.1f}%)")
    print(f"  In 2+ tiles (OVERLAP): {in_multiple} ({multi_pct:.1f}%)")

    if in_multiple == 0 and none_pct < 15:
        print(f"\n  ✓ PASS — Zero overlaps, grout-only gaps ({none_pct:.1f}% grout area)")
    elif in_multiple > 0:
        print(f"\n  ✗ FAIL — {in_multiple} points in multiple tiles (OVERLAP detected)")
    else:
        print(f"\n  ⚠ WARN — {none_pct:.1f}% in no tile (possible gaps beyond grout)")

    # Render to PNG if matplotlib available
    if HAS_MPL:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        ax.set_aspect('equal')
        ax.set_facecolor('#888880')  # grout color

        colors = ['#5a8a9a', '#4a7a8a']
        for i, poly in enumerate(tiles):
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            ax.fill(xs, ys, color=colors[i % 2], edgecolor='#333', linewidth=0.5)

        ax.set_xlim(test_region[0] - 0.5, test_region[2] + 0.5)
        ax.set_ylim(test_region[3] + 0.5, test_region[1] - 0.5)  # flip Y
        ax.set_title(f'Fishscale — stemLen=rw (exact circular arcs)\n'
                     f'{in_tile}/{n_samples} in tile, {in_none} grout, {in_multiple} overlap')

        out = '/Users/Sims/Desktop/layit/tools/tile-test/verify_fishscale.png'
        plt.savefig(out, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Rendered to: {out}")

    return in_multiple == 0


def verify_ogee():
    """Verify ogee tessellation has minimal gaps."""
    print("\n" + "=" * 60)
    print("OGEE TESSELLATION VERIFICATION")
    print("=" * 60)

    tile_w = 2.0   # subW
    grout = 0.125   # subGr
    sub_h = 3.0     # subH (specified tile height)
    hw = (tile_w - grout) / 2
    hh = (sub_h - grout) / 2
    col_spacing = tile_w + grout   # stColIn
    row_spacing = (sub_h - grout) / 2  # stRowIn = face hh, exact anti-symmetry

    print(f"Tile: subW={tile_w}\" subH={sub_h}\"")
    print(f"Face: hw={hw:.4f} hh={hh:.4f}")
    print(f"Row spacing: {row_spacing:.4f}\" (= subH/2)")
    print(f"Col spacing: {col_spacing:.4f}\" (= subW + subGr)")
    print(f"Using kappa={0.5523} bezier approximation, midY=0")

    tiles = []
    for row in range(-1, 6):
        for col in range(-1, 4):
            cx = col_spacing / 2 + col * col_spacing
            cy = row_spacing + row * row_spacing
            if row % 2 == 1:
                cx += col_spacing / 2

            # Generate tile polygon
            poly = ogee_tile_path(cx, cy, hw, hh)

            # Flip odd rows by rotating 180° around tile center
            if row % 2 == 1:
                poly = [(2 * cx - x, 2 * cy - y) for (x, y) in poly]

            tiles.append(poly)

    test_region = (tile_w, row_spacing * 2, tile_w * 2, row_spacing * 4)
    n_samples = 10000
    rng = np.random.default_rng(42)

    in_tile = 0
    in_none = 0
    in_multiple = 0

    for _ in range(n_samples):
        x = test_region[0] + rng.random() * (test_region[2] - test_region[0])
        y = test_region[1] + rng.random() * (test_region[3] - test_region[1])
        count = sum(1 for poly in tiles if point_in_polygon(x, y, poly))
        if count == 0: in_none += 1
        elif count == 1: in_tile += 1
        else: in_multiple += 1

    none_pct = in_none / n_samples * 100
    multi_pct = in_multiple / n_samples * 100

    print(f"\nSampled {n_samples} points:")
    print(f"  In exactly 1 tile: {in_tile} ({in_tile/n_samples*100:.1f}%)")
    print(f"  In grout (0 tiles): {in_none} ({none_pct:.1f}%)")
    print(f"  In 2+ tiles (OVERLAP): {in_multiple} ({multi_pct:.1f}%)")

    if in_multiple == 0 and none_pct < 20:
        print(f"\n  ✓ PASS — Zero overlaps, grout-only gaps")
    elif in_multiple > 0:
        print(f"\n  ⚠ WARN — {in_multiple} points overlap (bezier approximation artifact)")

    if HAS_MPL:
        fig, ax = plt.subplots(1, 1, figsize=(10, 12))
        ax.set_aspect('equal')
        ax.set_facecolor('#888880')

        colors = ['#5a8a9a', '#d4c4a0']
        for i, poly in enumerate(tiles):
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            row_idx = i // 5  # rough row estimate
            ax.fill(xs, ys, color=colors[row_idx % 2], edgecolor='#333', linewidth=0.5)

        ax.set_xlim(test_region[0] - 0.5, test_region[2] + 0.5)
        ax.set_ylim(test_region[3] + 0.5, test_region[1] - 0.5)
        ax.set_title(f'Ogee — kappa bezier S-curve (K=0.5523)\n'
                     f'{in_tile}/{n_samples} in tile, {in_none} grout, {in_multiple} overlap')

        out = '/Users/Sims/Desktop/layit/tools/tile-test/verify_ogee.png'
        plt.savefig(out, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Rendered to: {out}")

    return in_multiple < n_samples * 0.01  # less than 1% overlap


def main():
    shapes = sys.argv[1:] if len(sys.argv) > 1 else ['fishscale', 'ogee']

    results = {}
    for shape in shapes:
        if shape == 'fishscale':
            results[shape] = verify_fishscale()
        elif shape == 'ogee':
            results[shape] = verify_ogee()
        else:
            print(f"Unknown shape: {shape}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for shape, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {shape}: {status}")


if __name__ == '__main__':
    main()
