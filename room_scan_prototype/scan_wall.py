#!/usr/bin/env python3
"""
LayIt Single-Wall Scan → Tile Engine Bridge
=============================================
Takes a photo of a wall, runs depth estimation + feature detection,
and outputs JSON that the LayIt PWA tile engine can directly consume.

This is the bridge between:
  - Camera scan prototype (run_depth.py, detect_features.py)
  - LayIt PWA tile layout engine (index.html: C.wall, C.polygon, C.voids)

The output JSON maps directly to the LayIt app's internal data model:
  C.wall  = { tW, lH, rV, bV }       — wall dimensions in inches
  C.polygon = [{x, y}, ...]           — wall shape as polygon points (inches)
  C.voids = [{ l, x, y, w, h }, ...]  — cutouts/features (niches, windows, etc.)

Usage:
    python scan_wall.py photo.jpg
    python scan_wall.py photo.jpg --width 58 --height 70
    python scan_wall.py photo.jpg --width 58 --height 70 --confirm
    python scan_wall.py photo.jpg --output layout_data.json

Options:
    --width INCHES    Override AI-estimated wall width with manual measurement
    --height INCHES   Override AI-estimated wall height with manual measurement
    --confirm         Interactive mode: show AI estimates and ask for confirmation
    --output PATH     Output JSON file path (default: <image>_layout.json)
    --skip-features   Skip feature detection, just measure wall dimensions
"""

import sys
import os
import json
import argparse
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_depth import load_model, estimate_depth, depth_to_3d_points, fit_plane_ransac
from detect_features import (detect_features, auto_detect_closeup,
                              find_dominant_wall_plane)


# =============================================================================
# WALL DIMENSION EXTRACTION
# =============================================================================

def estimate_wall_dimensions(depth_map, focal_px):
    """
    Estimate wall width and height from a single photo's depth map.

    Uses the dominant wall plane depth + pinhole camera model to convert
    the visible wall extent from pixels to real-world inches.

    Returns: (width_inches, height_inches, wall_depth_m, confidence)
    """
    h, w = depth_map.shape
    cx, cy = w / 2.0, h / 2.0

    # Find the dominant wall plane
    closeup = auto_detect_closeup(depth_map)
    wall_depth, wall_mask = find_dominant_wall_plane(depth_map, closeup_mode=closeup)

    if wall_depth is None:
        return None, None, None, 'failed'

    # Find the extent of the wall in the image
    # Use the wall mask to find leftmost/rightmost and top/bottom wall pixels
    wall_rows, wall_cols = np.where(wall_mask)

    if len(wall_rows) == 0:
        return None, None, None, 'no_wall_pixels'

    # Use percentiles to avoid edge noise (5th and 95th percentile)
    left_px = np.percentile(wall_cols, 2)
    right_px = np.percentile(wall_cols, 98)
    top_px = np.percentile(wall_rows, 2)
    bottom_px = np.percentile(wall_rows, 98)

    # Convert pixel span to real-world dimensions using pinhole model
    # X = (u - cx) * Z / f
    Z = wall_depth

    x_left = (left_px - cx) * Z / focal_px
    x_right = (right_px - cx) * Z / focal_px
    width_m = abs(x_right - x_left)

    y_top = (top_px - cy) * Z / focal_px
    y_bottom = (bottom_px - cy) * Z / focal_px
    height_m = abs(y_bottom - y_top)

    width_inches = width_m * 39.3701
    height_inches = height_m * 39.3701

    # Confidence based on wall coverage
    wall_coverage = np.mean(wall_mask)
    if wall_coverage > 0.3:
        confidence = 'high'
    elif wall_coverage > 0.15:
        confidence = 'medium'
    else:
        confidence = 'low'

    return width_inches, height_inches, wall_depth, confidence


# =============================================================================
# FEATURE POSITION CONVERSION
# =============================================================================

def convert_features_to_voids(constraints, wall_width_in, wall_height_in):
    """
    Convert detect_features.py constraint output (center-relative positions)
    to LayIt PWA void format (from-left, from-bottom positions).

    detect_features.py outputs:
        position_x_from_center_inches  (negative = left of center)
        position_y_from_center_inches  (negative = above center in image coords)

    LayIt PWA expects:
        x = distance from left edge of wall (inches)
        y = distance from bottom edge of wall (inches)
        w = feature width (inches)
        h = feature height (inches)
        l = label string
    """
    voids = []

    for c in constraints:
        # Convert from center-relative to absolute position
        # Center of wall = (wall_width/2, wall_height/2)
        center_x = c['position_x_from_center_inches']
        center_y = c['position_y_from_center_inches']

        # Feature center in absolute wall coordinates
        # X: center_x is positive to the right, wall origin is left edge
        abs_center_x = (wall_width_in / 2.0) + center_x

        # Y: In image coords, positive Y = downward = lower on wall
        # In LayIt coords, Y is from bottom, so we flip:
        # Image center Y maps to wall_height/2 from bottom
        # Positive center_y (downward in image) = lower on wall = smaller Y from bottom
        abs_center_y = (wall_height_in / 2.0) - center_y

        feat_w = c['width_inches']
        feat_h = c['height_inches']

        # Convert from center position to corner position (from left, from bottom)
        void_x = abs_center_x - (feat_w / 2.0)
        void_y = abs_center_y - (feat_h / 2.0)

        # Clamp to wall bounds
        void_x = max(0, min(void_x, wall_width_in - feat_w))
        void_y = max(0, min(void_y, wall_height_in - feat_h))

        # Generate label from classification
        classification = c.get('feature', 'feature')
        label_map = {
            'shower_niche': 'Niche',
            'alcove_or_recess': 'Alcove',
            'small_recess': 'Recess',
            'shelf_or_ledge': 'Shelf',
            'countertop_or_cabinet': 'Cabinet',
            'door_or_window': 'Door/Window',
            'window': 'Window',
            'opening': 'Opening',
            'protrusion': 'Protrusion',
        }
        label = label_map.get(classification, classification.replace('_', ' ').title())

        voids.append({
            'l': label,
            'x': round(void_x, 2),
            'y': round(void_y, 2),
            'w': round(feat_w, 2),
            'h': round(feat_h, 2),
            # Extra metadata (not consumed by PWA but useful for debugging)
            '_confidence': c.get('confidence', 'unknown'),
            '_requires_grout_alignment': c.get('requires_grout_alignment', False),
            '_recess_depth_inches': c.get('recess_depth_inches', 0),
            '_auto_detected': True,
        })

    return voids


# =============================================================================
# POLYGON GENERATION
# =============================================================================

def generate_wall_polygon(wall_width_in, wall_height_in, right_variance=0, bottom_variance=0):
    """
    Generate the C.polygon array for the LayIt tile engine.

    For a simple rectangle:
        [{x:0, y:0}, {x:W, y:0}, {x:W, y:H}, {x:0, y:H}]

    For out-of-square walls, the right edge and/or bottom edge can be offset:
        right_variance: how much the right edge deviates (positive = wider at top)
        bottom_variance: how much the bottom deviates (positive = taller on left)
    """
    polygon = [
        {'x': 0, 'y': 0},
        {'x': round(wall_width_in, 2), 'y': round(bottom_variance, 2)},
        {'x': round(wall_width_in + right_variance, 2), 'y': round(wall_height_in, 2)},
        {'x': 0, 'y': round(wall_height_in, 2)},
    ]

    # If it's a perfect rectangle, simplify
    if abs(right_variance) < 0.01 and abs(bottom_variance) < 0.01:
        polygon = [
            {'x': 0, 'y': 0},
            {'x': round(wall_width_in, 2), 'y': 0},
            {'x': round(wall_width_in, 2), 'y': round(wall_height_in, 2)},
            {'x': 0, 'y': round(wall_height_in, 2)},
        ]

    return polygon


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def scan_wall(image_path, manual_width=None, manual_height=None,
              skip_features=False, interactive=False):
    """
    Full single-wall scan pipeline.

    1. Load image → run depth estimation
    2. Estimate wall dimensions (or use manual overrides)
    3. Detect features (niches, windows, etc.)
    4. Convert everything to LayIt PWA format
    5. Return the layout data dict
    """
    image_path = Path(image_path)
    print(f"\n{'='*60}")
    print(f"  LayIt Single-Wall Scan")
    print(f"  Photo: {image_path.name}")
    print(f"{'='*60}")

    # Step 1: Load model and get depth map
    print("\n📷 Step 1: Running depth estimation...")
    model, transform, device = load_model()
    depth_map, focal_px, image = estimate_depth(model, transform, device, image_path)
    img_h, img_w = image.shape[:2] if hasattr(image, 'shape') else (image.size[1], image.size[0])
    print(f"  Image size: {img_w}x{img_h}")
    print(f"  Focal length: {focal_px:.1f} px")

    # Step 2: Estimate wall dimensions
    print("\n📏 Step 2: Measuring wall dimensions...")
    ai_width, ai_height, wall_depth, confidence = estimate_wall_dimensions(depth_map, focal_px)

    if ai_width is None:
        print("  ❌ Could not detect wall plane. Try a more head-on photo.")
        return None

    print(f"  AI estimate: {ai_width:.1f}\" wide × {ai_height:.1f}\" tall")
    print(f"  ({ai_width/12:.1f} ft × {ai_height/12:.1f} ft)")
    print(f"  Wall depth: {wall_depth:.2f}m, Confidence: {confidence}")

    # Apply manual overrides
    final_width = manual_width if manual_width is not None else ai_width
    final_height = manual_height if manual_height is not None else ai_height

    if manual_width is not None or manual_height is not None:
        print(f"\n  📐 Using manual measurements:")
        if manual_width is not None:
            print(f"    Width: {manual_width}\" (manual) vs {ai_width:.1f}\" (AI)")
        if manual_height is not None:
            print(f"    Height: {manual_height}\" (manual) vs {ai_height:.1f}\" (AI)")

    if interactive:
        print(f"\n  Current dimensions: {final_width:.1f}\" × {final_height:.1f}\"")
        resp = input("  Accept? [Y/n/edit]: ").strip().lower()
        if resp == 'edit' or resp == 'e':
            w_input = input(f"  Width ({final_width:.1f}\"): ").strip()
            if w_input:
                final_width = float(w_input)
            h_input = input(f"  Height ({final_height:.1f}\"): ").strip()
            if h_input:
                final_height = float(h_input)
        elif resp == 'n':
            print("  Cancelled.")
            return None

    # Step 3: Detect features
    constraints = []
    voids = []

    if not skip_features:
        print("\n🔍 Step 3: Detecting wall features (niches, windows, etc.)...")
        # Pass precomputed depth data to avoid loading model twice
        precomputed = {
            'depth_map': depth_map,
            'focal_px': focal_px,
            'image': image,
        }
        result = detect_features(str(image_path), precomputed=precomputed)

        if result is not None:
            features_by_type, constraints = result
            voids = convert_features_to_voids(constraints, final_width, final_height)

            if voids:
                print(f"\n  Found {len(voids)} feature(s) to include as voids:")
                for v in voids:
                    print(f"    {v['l']}: {v['w']}\" × {v['h']}\" at ({v['x']}\", {v['y']}\" from left/bottom)")
                    if v.get('_requires_grout_alignment'):
                        print(f"      ⚠️  Requires grout alignment (fixed constraint)")
            else:
                print("  No features detected — wall appears flat.")
    else:
        print("\n⏭️  Step 3: Skipping feature detection")

    # Step 4: Build LayIt PWA compatible output
    print(f"\n📦 Step 4: Building layout data for LayIt PWA...")

    polygon = generate_wall_polygon(final_width, final_height)

    # Strip metadata prefixed with _ from voids for the PWA-compatible version
    pwa_voids = []
    for v in voids:
        pwa_voids.append({k: v[k] for k in ['l', 'x', 'y', 'w', 'h']})

    layout_data = {
        'wall': {
            'tW': round(final_width, 2),
            'lH': round(final_height, 2),
            'rV': 0,
            'bV': 0,
        },
        'polygon': polygon,
        'voids': pwa_voids,
    }

    # Also include the full metadata version for debugging/calibration
    full_output = {
        'layit_layout': layout_data,
        'scan_metadata': {
            'image': image_path.name,
            'ai_width_inches': round(ai_width, 1),
            'ai_height_inches': round(ai_height, 1),
            'final_width_inches': round(final_width, 2),
            'final_height_inches': round(final_height, 2),
            'width_source': 'manual' if manual_width is not None else 'ai',
            'height_source': 'manual' if manual_height is not None else 'ai',
            'wall_depth_m': round(float(wall_depth), 3),
            'dimension_confidence': confidence,
        },
        'detected_features': voids,
        'constraints': constraints,
        'instructions': {
            'how_to_use': (
                'Copy the "layit_layout" object into the LayIt PWA. '
                'Set C.wall = layit_layout.wall, '
                'C.polygon = layit_layout.polygon, '
                'C.voids = layit_layout.voids, '
                'then call calculateSegments() and draw().'
            ),
            'manual_override': (
                'If any measurements are off, edit wall.tW (width) and wall.lH (height) '
                'in inches. For voids, adjust x (from left) and y (from bottom) positions.'
            ),
        },
    }

    return full_output


def main():
    parser = argparse.ArgumentParser(
        description="LayIt Single-Wall Scan — Photo to Tile Layout Bridge"
    )
    parser.add_argument("image", help="Path to wall photo")
    parser.add_argument("--width", type=float, default=None,
                        help="Manual wall width in inches (overrides AI estimate)")
    parser.add_argument("--height", type=float, default=None,
                        help="Manual wall height in inches (overrides AI estimate)")
    parser.add_argument("--confirm", action="store_true",
                        help="Interactive mode — confirm/edit dimensions before output")
    parser.add_argument("--skip-features", action="store_true",
                        help="Skip feature detection, just measure wall dimensions")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file path (default: <image>_layout.json)")

    args = parser.parse_args()

    result = scan_wall(
        args.image,
        manual_width=args.width,
        manual_height=args.height,
        skip_features=args.skip_features,
        interactive=args.confirm,
    )

    if result is None:
        print("\n❌ Scan failed. Try a different photo or provide manual measurements.")
        sys.exit(1)

    # Save output
    output_path = args.output
    if output_path is None:
        output_path = str(Path(args.image).parent / f"{Path(args.image).stem}_layout.json")

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Layout data saved: {output_path}")

    # Print the PWA-ready snippet
    layout = result['layit_layout']
    print(f"\n{'='*60}")
    print(f"  LAYIT PWA IMPORT DATA")
    print(f"{'='*60}")
    print(f"\n  Wall: {layout['wall']['tW']}\" × {layout['wall']['lH']}\"")
    print(f"        ({layout['wall']['tW']/12:.1f} ft × {layout['wall']['lH']/12:.1f} ft)")

    if layout['voids']:
        print(f"\n  Voids ({len(layout['voids'])}):")
        for v in layout['voids']:
            print(f"    {v['l']}: {v['w']}\" × {v['h']}\" @ ({v['x']}\", {v['y']}\" from left/bottom)")

    print(f"\n  Polygon: {len(layout['polygon'])} points")
    for i, p in enumerate(layout['polygon']):
        print(f"    P{i}: ({p['x']}, {p['y']})")

    print(f"\n  To use in LayIt PWA:")
    print(f"    C.wall = {json.dumps(layout['wall'])}")
    print(f"    C.polygon = {json.dumps(layout['polygon'])}")
    print(f"    C.voids = {json.dumps(layout['voids'])}")
    print()


if __name__ == "__main__":
    main()
