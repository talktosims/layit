#!/usr/bin/env python3
"""
LayIt Room Scan — Fixed Feature Detection
==========================================
Detects niches, recesses, windows, and other fixed constraints from
depth maps. These features become "fixed constraints" in the tile
layout engine — the pattern must align to them, not the other way around.

A niche is a rectangular region where the depth is DEEPER than the
surrounding wall (it's recessed into the wall).
A protrusion (shelf, countertop edge) is where depth is SHALLOWER.
A window/door is where depth is MUCH deeper (looking through/outside).

Usage:
    python detect_features.py photo.jpg
    python detect_features.py photo.jpg --wall-tolerance 0.05 --min-feature-area 0.02

Output:
    - Feature map visualization (*_features.png)
    - JSON with detected features and their positions/dimensions
"""

import sys
import os
import json
import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SCRIPT_DIR = Path(__file__).parent
DEPTH_PRO_DIR = SCRIPT_DIR / "ml-depth-pro"
sys.path.insert(0, str(DEPTH_PRO_DIR / "src"))

from run_depth import load_model, estimate_depth, depth_to_3d_points


def find_dominant_wall_plane(depth_map, closeup_mode=False):
    """
    Find the dominant wall surface in the depth map.
    Returns the median depth and a mask of pixels belonging to the wall plane.

    For closeup_mode: when shooting a feature up close, the surrounding wall
    is at the EDGES of the image (closest to camera), not the center.
    The feature (niche) fills the center and is DEEPER.
    So we use the SHALLOWEST (closest) peak as the wall.
    """
    h, w = depth_map.shape

    if closeup_mode:
        # For closeups, the wall is at the edges of the frame
        edge_pixels = np.concatenate([
            depth_map[:int(h*0.15), :].flatten(),      # top strip
            depth_map[-int(h*0.15):, :].flatten(),      # bottom strip
            depth_map[:, :int(w*0.15)].flatten(),       # left strip
            depth_map[:, -int(w*0.15):].flatten(),      # right strip
        ])
        valid = edge_pixels[edge_pixels > 0.3]
        if len(valid) == 0:
            return None, None
        wall_depth = float(np.median(valid))
    else:
        # For full-wall shots, use the center region
        margin_y = int(h * 0.15)
        margin_x = int(w * 0.10)
        center = depth_map[margin_y:h - margin_y, margin_x:w - margin_x]

        valid = center[center > 0.3]
        if len(valid) == 0:
            return None, None

        # Compute histogram
        hist, bin_edges = np.histogram(valid, bins=100)
        peak_bin = np.argmax(hist)
        wall_depth = (bin_edges[peak_bin] + bin_edges[peak_bin + 1]) / 2

    # Wall plane mask: pixels within tolerance of the wall depth
    tolerance = 0.08  # 8cm tolerance for wall plane membership
    wall_mask = np.abs(depth_map - wall_depth) < tolerance

    return wall_depth, wall_mask


def auto_detect_closeup(depth_map):
    """
    Detect if this is a closeup shot of a feature.
    Heuristic: if the center of the image is significantly DEEPER than the edges,
    we're probably looking at a niche/recess from up close.
    """
    h, w = depth_map.shape

    center_depth = np.median(depth_map[h//3:2*h//3, w//3:2*w//3])
    edge_depth = np.median(np.concatenate([
        depth_map[:int(h*0.12), :].flatten(),
        depth_map[-int(h*0.12):, :].flatten(),
        depth_map[:, :int(w*0.12)].flatten(),
        depth_map[:, -int(w*0.12):].flatten(),
    ]))

    depth_diff = center_depth - edge_depth

    # If center is >5cm deeper than edges and total depth range is small (<1m),
    # this is likely a closeup of a recessed feature
    total_range = depth_map.max() - depth_map.min()
    is_closeup = depth_diff > 0.05 and total_range < 1.0

    if is_closeup:
        print(f"  Auto-detected CLOSEUP mode (center {depth_diff*39.37:.1f}\" deeper than edges)")

    return is_closeup


def detect_depth_anomalies(depth_map, wall_depth, wall_mask, min_depth_diff=0.03):
    """
    Find regions where depth deviates significantly from the wall plane.

    Returns:
        niches: regions DEEPER than wall (recessed into wall)
        protrusions: regions SHALLOWER than wall (sticking out)
        openings: regions MUCH deeper (doors, windows looking outside)
    """
    h, w = depth_map.shape

    # Ignore edges (floor, ceiling, side walls)
    margin_y = int(h * 0.10)
    margin_x = int(w * 0.08)
    roi_mask = np.zeros_like(depth_map, dtype=bool)
    roi_mask[margin_y:h - margin_y, margin_x:w - margin_x] = True

    # Depth differences from wall plane
    depth_diff = depth_map - wall_depth

    # Niches: deeper than wall by at least min_depth_diff (3cm default)
    # but not absurdly deep (that's a doorway/window to outside)
    niche_mask = (depth_diff > min_depth_diff) & (depth_diff < 0.5) & roi_mask & ~wall_mask

    # Protrusions: shallower than wall
    protrusion_mask = (depth_diff < -min_depth_diff) & (depth_diff > -0.5) & roi_mask & ~wall_mask

    # Openings: much deeper (windows, doorways)
    opening_mask = (depth_diff > 0.5) & roi_mask & ~wall_mask

    return niche_mask, protrusion_mask, opening_mask


def refine_niche_bounds_via_gradient(depth_map, y_min, y_max, x_min, x_max, wall_depth, expand=30):
    """
    Refine bounding box of a niche using depth gradients.
    Looks for sharp depth transitions (wall→niche edges) to find precise bounds.

    The key insight: a niche edge is where depth changes sharply from wall_depth
    to niche_depth. We scan inward from each side of the bounding box looking
    for the steepest gradient — that's the real edge.
    """
    h, w = depth_map.shape

    # Expand the search area slightly beyond the initial bounding box
    search_y_min = max(0, y_min - expand)
    search_y_max = min(h, y_max + expand)
    search_x_min = max(0, x_min - expand)
    search_x_max = min(w, x_max + expand)

    region = depth_map[search_y_min:search_y_max, search_x_min:search_x_max]

    # Compute depth gradients
    grad_y = np.gradient(region, axis=0)  # vertical gradient
    grad_x = np.gradient(region, axis=1)  # horizontal gradient

    # --- Refine LEFT edge ---
    # Scan columns from left: find where horizontal gradient is strongest (wall→niche transition)
    mid_y = region.shape[0] // 2
    y_band = slice(max(0, mid_y - region.shape[0]//4), min(region.shape[0], mid_y + region.shape[0]//4))
    col_gradients = np.abs(grad_x[y_band, :]).mean(axis=0)

    # Find the strongest gradient in the left half
    left_half = col_gradients[:region.shape[1]//2]
    if len(left_half) > 0 and np.max(left_half) > 0.001:
        refined_x_min = search_x_min + int(np.argmax(left_half))
    else:
        refined_x_min = x_min

    # --- Refine RIGHT edge ---
    right_half = col_gradients[region.shape[1]//2:]
    if len(right_half) > 0 and np.max(right_half) > 0.001:
        refined_x_max = search_x_min + region.shape[1]//2 + int(np.argmax(right_half))
    else:
        refined_x_max = x_max

    # --- Refine TOP edge ---
    mid_x = region.shape[1] // 2
    x_band = slice(max(0, mid_x - region.shape[1]//4), min(region.shape[1], mid_x + region.shape[1]//4))
    row_gradients = np.abs(grad_y[:, x_band]).mean(axis=1)

    top_half = row_gradients[:region.shape[0]//2]
    if len(top_half) > 0 and np.max(top_half) > 0.001:
        refined_y_min = search_y_min + int(np.argmax(top_half))
    else:
        refined_y_min = y_min

    # --- Refine BOTTOM edge ---
    bottom_half = row_gradients[region.shape[0]//2:]
    if len(bottom_half) > 0 and np.max(bottom_half) > 0.001:
        refined_y_max = search_y_min + region.shape[0]//2 + int(np.argmax(bottom_half))
    else:
        refined_y_max = y_max

    # Sanity check: refined box should be smaller than or similar to original
    # If refinement made it bigger, something went wrong — fall back
    orig_w = x_max - x_min
    orig_h = y_max - y_min
    ref_w = refined_x_max - refined_x_min
    ref_h = refined_y_max - refined_y_min

    if ref_w > orig_w * 1.5 or ref_w < orig_w * 0.3:
        refined_x_min, refined_x_max = x_min, x_max
    if ref_h > orig_h * 1.5 or ref_h < orig_h * 0.3:
        refined_y_min, refined_y_max = y_min, y_max

    return refined_y_min, refined_y_max, refined_x_min, refined_x_max


def find_rectangular_regions(binary_mask, min_area_fraction=0.005, max_area_fraction=0.25,
                             depth_map=None, wall_depth=None):
    """
    Find rectangular bounding regions in a binary mask.
    Uses connected component analysis + gradient-based edge refinement.

    Returns list of dicts with bounding box info.
    """
    if not np.any(binary_mask):
        return []

    h, w = binary_mask.shape
    total_pixels = h * w
    min_pixels = int(total_pixels * min_area_fraction)
    max_pixels = int(total_pixels * max_area_fraction)

    # Downsample the mask for faster processing
    scale = 4
    small_h, small_w = h // scale, w // scale
    small_mask = np.zeros((small_h, small_w), dtype=bool)

    for sy in range(small_h):
        for sx in range(small_w):
            block = binary_mask[sy*scale:(sy+1)*scale, sx*scale:(sx+1)*scale]
            small_mask[sy, sx] = np.mean(block) > 0.3

    # Find connected components via iterative labeling
    labels = np.zeros_like(small_mask, dtype=int)
    current_label = 0

    for y in range(small_h):
        for x in range(small_w):
            if small_mask[y, x] and labels[y, x] == 0:
                current_label += 1
                queue = [(y, x)]
                labels[y, x] = current_label
                while queue:
                    cy, cx = queue.pop(0)
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < small_h and 0 <= nx < small_w:
                            if small_mask[ny, nx] and labels[ny, nx] == 0:
                                labels[ny, nx] = current_label
                                queue.append((ny, nx))

    # Extract bounding boxes for each component
    regions = []
    for label_id in range(1, current_label + 1):
        component = labels == label_id
        pixel_count = np.sum(component) * (scale * scale)

        if pixel_count < min_pixels or pixel_count > max_pixels:
            continue

        ys, xs = np.where(component)
        if len(ys) == 0:
            continue

        # Initial bounding box in original image coordinates
        y_min = int(ys.min()) * scale
        y_max = int(ys.max() + 1) * scale
        x_min = int(xs.min()) * scale
        x_max = int(xs.max() + 1) * scale

        # Refine bounds using depth gradients if depth map available
        if depth_map is not None and wall_depth is not None:
            y_min, y_max, x_min, x_max = refine_niche_bounds_via_gradient(
                depth_map, y_min, y_max, x_min, x_max, wall_depth
            )
            # Recount pixels in refined region
            pixel_count = int(np.sum(binary_mask[y_min:y_max, x_min:x_max]))

        bbox_area = (y_max - y_min) * (x_max - x_min)
        fill_ratio = pixel_count / max(bbox_area, 1)

        region_depths = binary_mask[y_min:y_max, x_min:x_max]
        actual_fill = np.mean(region_depths)

        regions.append({
            'y_min': y_min, 'y_max': y_max,
            'x_min': x_min, 'x_max': x_max,
            'pixel_count': int(pixel_count),
            'fill_ratio': float(actual_fill),
            'bbox_area': int(bbox_area),
        })

    return regions


def compute_feature_dimensions(regions, depth_map, focallength_px, wall_depth):
    """
    Convert pixel bounding boxes to real-world dimensions in inches.
    Uses the depth at the feature location for accurate sizing.
    """
    h, w = depth_map.shape
    cx, cy = w / 2.0, h / 2.0

    features = []
    for region in regions:
        # Use the wall depth for projecting the feature dimensions
        # (the feature is ON the wall, even if it's recessed)
        Z = wall_depth

        # Convert pixel coordinates to real-world dimensions
        # Width: difference in X at the feature's depth
        x_left = (region['x_min'] - cx) * Z / focallength_px
        x_right = (region['x_max'] - cx) * Z / focallength_px
        feature_width_m = abs(x_right - x_left)

        # Height: difference in Y at the feature's depth
        y_top = (region['y_min'] - cy) * Z / focallength_px
        y_bottom = (region['y_max'] - cy) * Z / focallength_px
        feature_height_m = abs(y_bottom - y_top)

        # Position: center of feature relative to image center, in real units
        center_x_px = (region['x_min'] + region['x_max']) / 2
        center_y_px = (region['y_min'] + region['y_max']) / 2
        pos_x_m = (center_x_px - cx) * Z / focallength_px
        pos_y_m = (center_y_px - cy) * Z / focallength_px

        # Depth of the feature itself (how deep is the niche?)
        feature_region = depth_map[region['y_min']:region['y_max'],
                                   region['x_min']:region['x_max']]
        feature_depth = float(np.median(feature_region[feature_region > 0.3]))
        recess_depth_m = feature_depth - wall_depth  # positive = recessed, negative = protruding

        # Convert to inches
        feature_width_in = feature_width_m * 39.3701
        feature_height_in = feature_height_m * 39.3701
        recess_depth_in = recess_depth_m * 39.3701
        pos_x_in = pos_x_m * 39.3701
        pos_y_in = pos_y_m * 39.3701

        # Position from left edge and bottom of wall (approximate)
        # We estimate left edge as the leftmost wall extent
        # and bottom as the lowest wall extent

        features.append({
            'width_inches': round(feature_width_in, 1),
            'height_inches': round(feature_height_in, 1),
            'recess_depth_inches': round(recess_depth_in, 1),
            'center_x_inches_from_center': round(pos_x_in, 1),
            'center_y_inches_from_center': round(pos_y_in, 1),
            'width_m': round(feature_width_m, 3),
            'height_m': round(feature_height_m, 3),
            'recess_depth_m': round(recess_depth_m, 3),
            'fill_ratio': round(region['fill_ratio'], 2),
            'pixel_bounds': {
                'x_min': region['x_min'], 'x_max': region['x_max'],
                'y_min': region['y_min'], 'y_max': region['y_max'],
            }
        })

    return features


def classify_feature(feature, feature_type_hint):
    """
    Classify a detected feature based on its dimensions and type.
    """
    w = feature['width_inches']
    h = feature['height_inches']
    d = feature['recess_depth_inches']

    if feature_type_hint == 'niche':
        # Common shower niche: 12-16" wide, 12-28" tall, 3-4" deep
        if 8 <= w <= 36 and 8 <= h <= 48 and 1 <= d <= 8:
            feature['classification'] = 'shower_niche'
            feature['confidence'] = 'high'
        elif w > 36 or h > 48:
            feature['classification'] = 'alcove_or_recess'
            feature['confidence'] = 'medium'
        else:
            feature['classification'] = 'small_recess'
            feature['confidence'] = 'low'

    elif feature_type_hint == 'protrusion':
        if w > 24 and h < 6:
            feature['classification'] = 'shelf_or_ledge'
            feature['confidence'] = 'medium'
        elif w > 12 and h > 12:
            feature['classification'] = 'countertop_or_cabinet'
            feature['confidence'] = 'medium'
        else:
            feature['classification'] = 'protrusion'
            feature['confidence'] = 'low'

    elif feature_type_hint == 'opening':
        if w > 24 and h > 48:
            feature['classification'] = 'door_or_window'
            feature['confidence'] = 'high'
        elif w > 18 and h > 18:
            feature['classification'] = 'window'
            feature['confidence'] = 'medium'
        else:
            feature['classification'] = 'opening'
            feature['confidence'] = 'low'

    return feature


def save_feature_visualization(image, depth_map, wall_mask, features_by_type, output_path):
    """Save visualization showing detected features on the original image."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    # Original image with feature boxes
    axes[0].imshow(image)
    axes[0].set_title("Detected Features", fontsize=14, fontweight='bold')

    colors = {'niche': '#FF4444', 'protrusion': '#44FF44', 'opening': '#4444FF'}
    labels_shown = set()

    for ftype, features in features_by_type.items():
        color = colors.get(ftype, '#FFFFFF')
        for f in features:
            pb = f['pixel_bounds']
            rect = Rectangle(
                (pb['x_min'], pb['y_min']),
                pb['x_max'] - pb['x_min'],
                pb['y_max'] - pb['y_min'],
                linewidth=3, edgecolor=color, facecolor='none',
                linestyle='--' if f.get('confidence') == 'low' else '-'
            )
            axes[0].add_patch(rect)

            label = f.get('classification', ftype)
            dims = f"{f['width_inches']:.0f}\" x {f['height_inches']:.0f}\""
            axes[0].text(
                pb['x_min'], pb['y_min'] - 10,
                f"{label}\n{dims}",
                color=color, fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7)
            )

            if ftype not in labels_shown:
                # Add to legend
                labels_shown.add(ftype)

    axes[0].axis('off')

    # Depth map
    im = axes[1].imshow(depth_map, cmap='turbo')
    axes[1].set_title("Depth Map", fontsize=14)
    axes[1].axis('off')
    plt.colorbar(im, ax=axes[1], shrink=0.8, label='Depth (m)')

    # Wall mask + anomaly overlay
    overlay = np.zeros((*depth_map.shape, 3))
    overlay[wall_mask] = [0.3, 0.3, 0.3]  # wall = gray

    for ftype, features in features_by_type.items():
        c = {'niche': [1, 0.2, 0.2], 'protrusion': [0.2, 1, 0.2], 'opening': [0.2, 0.2, 1]}
        color_rgb = c.get(ftype, [1, 1, 1])
        for f in features:
            pb = f['pixel_bounds']
            overlay[pb['y_min']:pb['y_max'], pb['x_min']:pb['x_max']] = color_rgb

    axes[2].imshow(overlay)
    axes[2].set_title("Wall Plane (gray) + Features", fontsize=14)
    axes[2].axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved feature visualization: {output_path}")


def detect_features(image_path, min_depth_diff=0.03, min_area=0.005,
                     precomputed=None):
    """
    Main feature detection pipeline.
    Returns detected features organized by type.

    Args:
        precomputed: Optional dict with 'depth_map', 'focal_px', 'image' to skip
                     re-running the depth model (saves ~10s on repeated calls).
    """
    image_path = Path(image_path)

    if precomputed is not None:
        depth_map = precomputed['depth_map']
        focal_px = precomputed['focal_px']
        image = precomputed['image']
    else:
        # Load model and estimate depth
        model, transform, device = load_model()
        depth_map, focal_px, image = estimate_depth(model, transform, device, image_path)

    # Find the dominant wall plane
    print("\n  Finding dominant wall plane...")
    closeup = auto_detect_closeup(depth_map)
    wall_depth, wall_mask = find_dominant_wall_plane(depth_map, closeup_mode=closeup)

    if wall_depth is None:
        print("  ERROR: Could not find a dominant wall plane.")
        return None

    print(f"  Wall depth: {wall_depth:.3f}m ({wall_depth * 3.28084:.2f} ft)")
    print(f"  Wall coverage: {np.mean(wall_mask) * 100:.1f}% of image")

    # Detect anomalies
    print("  Detecting depth anomalies...")
    niche_mask, protrusion_mask, opening_mask = detect_depth_anomalies(
        depth_map, wall_depth, wall_mask, min_depth_diff=min_depth_diff
    )

    print(f"  Niche pixels: {np.sum(niche_mask)} ({np.mean(niche_mask) * 100:.1f}%)")
    print(f"  Protrusion pixels: {np.sum(protrusion_mask)} ({np.mean(protrusion_mask) * 100:.1f}%)")
    print(f"  Opening pixels: {np.sum(opening_mask)} ({np.mean(opening_mask) * 100:.1f}%)")

    # Find rectangular regions
    # In closeup mode, the feature can fill most of the frame (up to 60%)
    max_area = 0.60 if closeup else 0.25
    features_by_type = {}

    for ftype, mask in [('niche', niche_mask), ('protrusion', protrusion_mask), ('opening', opening_mask)]:
        regions = find_rectangular_regions(mask, min_area_fraction=min_area,
                                                  max_area_fraction=max_area,
                                                  depth_map=depth_map, wall_depth=wall_depth)
        if regions:
            features = compute_feature_dimensions(regions, depth_map, focal_px, wall_depth)
            features = [classify_feature(f, ftype) for f in features]
            features_by_type[ftype] = features
            print(f"\n  Found {len(features)} {ftype}(s):")
            for f in features:
                cls = f.get('classification', ftype)
                print(f"    {cls}: {f['width_inches']:.1f}\" x {f['height_inches']:.1f}\" "
                      f"(recess: {f['recess_depth_inches']:.1f}\") "
                      f"[{f.get('confidence', '?')} confidence]")

    if not features_by_type:
        print("\n  No significant features detected — wall appears flat/uniform.")

    # Save visualization
    output_path = image_path.parent / f"{image_path.stem}_features.png"
    save_feature_visualization(image, depth_map, wall_mask, features_by_type, output_path)

    # Save JSON
    json_path = image_path.parent / f"{image_path.stem}_features.json"

    # Build constraint list for the layout engine
    constraints = []
    for ftype, features in features_by_type.items():
        for f in features:
            constraint = {
                'type': 'fixed',
                'feature': f.get('classification', ftype),
                'width_inches': f['width_inches'],
                'height_inches': f['height_inches'],
                'recess_depth_inches': f['recess_depth_inches'],
                'position_x_from_center_inches': f['center_x_inches_from_center'],
                'position_y_from_center_inches': f['center_y_inches_from_center'],
                'confidence': f.get('confidence', 'unknown'),
                'requires_grout_alignment': ftype == 'niche',  # niches need grout lines to align
                'auto_detected': True,
            }
            constraints.append(constraint)

    with open(json_path, 'w') as out:
        json.dump({
            'wall_depth_m': round(float(wall_depth), 3),
            'features': {k: v for k, v in features_by_type.items()},
            'constraints': constraints,
            'note': 'Constraints with requires_grout_alignment=true are fixed constraints '
                    'that the tile layout must align to. Auto-correction will check these '
                    'before shifting the pattern.',
        }, out, indent=2)
    print(f"\n  Saved feature data: {json_path}")

    return features_by_type, constraints


def main():
    parser = argparse.ArgumentParser(
        description="LayIt Feature Detection — Find niches, windows, and fixed constraints"
    )
    parser.add_argument("image", help="Path to photo of wall/surface")
    parser.add_argument("--min-depth-diff", type=float, default=0.03,
                        help="Minimum depth difference (meters) to flag as feature (default: 0.03 = 3cm)")
    parser.add_argument("--min-area", type=float, default=0.005,
                        help="Minimum feature area as fraction of image (default: 0.005 = 0.5%%)")

    args = parser.parse_args()
    detect_features(args.image, args.min_depth_diff, args.min_area)


if __name__ == "__main__":
    main()
