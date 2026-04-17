#!/usr/bin/env python3
"""
LayIt Room Scan - Two-Photo Room Measurement
=============================================
Takes two photos shot from opposite ends of a room and combines them
to get accurate wall-to-wall measurements without needing to know
the camera's distance from the wall behind it.

Strategy:
  - Each photo pair (opposite directions) measures one dimension well:
    * Photos facing the LENGTH walls → accurate LENGTH (far wall clearly visible)
    * Photos facing the WIDTH walls → accurate WIDTH (both side walls visible)
  - Height is averaged across all photos where floor+ceiling are detected
  - Width uses the photo where BOTH side walls were found by RANSAC
  - Length uses the photo with the strongest far_wall plane detection

Usage:
    python stitch_room.py photo1.jpg photo2.jpg [photo3.jpg photo4.jpg]
    python stitch_room.py ./room_photos/

    Provide 2-4 photos:
      - 2 photos: opposite ends along one axis
      - 4 photos: opposite ends along both axes (best results)

    Optional flags:
      --actual-length FEET    Known room length for accuracy check
      --actual-width FEET     Known room width for accuracy check
      --actual-height FEET    Known room height for accuracy check
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

# Add depth pro to path
SCRIPT_DIR = Path(__file__).parent
DEPTH_PRO_DIR = SCRIPT_DIR / "ml-depth-pro"
sys.path.insert(0, str(DEPTH_PRO_DIR / "src"))

import depth_pro

# Import from run_depth.py
from run_depth import (
    load_model, estimate_depth, depth_to_3d_points,
    detect_planes_ransac, plane_distance, measure_out_of_square,
    save_depth_visualization, save_floorplan_visualization
)


def analyze_photo(depth_map, focallength_px, image_shape, subsample=4):
    """
    Analyze a single photo and return structured plane data.
    Does NOT try to interpret dimensions — just returns what it sees.
    """
    h, w = depth_map.shape
    X, Y, Z = depth_to_3d_points(depth_map, focallength_px)
    planes = detect_planes_ransac(X, Y, Z, subsample=subsample)

    # Organize by type
    by_type = {}
    for p in planes:
        t = p['type']
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(p)

    result = {
        'planes': planes,
        'by_type': by_type,
        'X': X, 'Y': Y, 'Z': Z,
        'shape': (h, w),
    }

    # --- What this photo can measure well ---

    # Far wall distance (camera to opposite wall)
    far_walls = by_type.get('far_wall', [])
    if far_walls:
        best_far = max(far_walls, key=lambda p: p['inlier_count'])
        result['far_wall_dist_m'] = abs(best_far['d'])
        result['far_wall_confidence'] = best_far['inlier_count']
    else:
        # Fallback
        center_depths = Z[h//4:3*h//4, w//4:3*w//4].flatten()
        result['far_wall_dist_m'] = float(np.percentile(center_depths, 85))
        result['far_wall_confidence'] = 0  # no confidence

    # Width (left wall to right wall)
    left_walls = by_type.get('left_wall', [])
    right_walls = by_type.get('right_wall', [])
    if left_walls and right_walls:
        left = max(left_walls, key=lambda p: p['inlier_count'])
        right = max(right_walls, key=lambda p: p['inlier_count'])
        result['width_m'] = plane_distance(left, right)
        result['width_confidence'] = min(left['inlier_count'], right['inlier_count'])

        # Out of square check
        sq_dists, sq_min, sq_max, sq_delta = measure_out_of_square(left, right)
        if sq_dists is not None:
            result['width_out_of_square'] = {
                'min_m': sq_min,
                'max_m': sq_max,
                'delta_m': sq_delta,
                'delta_inches': sq_delta * 39.3701,
                'measurements_m': sq_dists.tolist(),
            }
    else:
        result['width_m'] = None
        result['width_confidence'] = 0

    # Height (floor to ceiling)
    floors = by_type.get('floor', [])
    ceilings = by_type.get('ceiling', [])
    if floors and ceilings:
        floor = max(floors, key=lambda p: p['inlier_count'])
        ceiling = max(ceilings, key=lambda p: p['inlier_count'])
        result['height_m'] = plane_distance(floor, ceiling)
        result['height_confidence'] = min(floor['inlier_count'], ceiling['inlier_count'])
    else:
        # Fallback using Y extremes
        ceil_Y = Y[:int(h*0.15), w//4:3*w//4].flatten()
        floor_Y = Y[int(h*0.85):, w//4:3*w//4].flatten()
        if len(ceil_Y) > 0 and len(floor_Y) > 0:
            result['height_m'] = abs(np.median(floor_Y) - np.median(ceil_Y))
            result['height_confidence'] = 0
        else:
            result['height_m'] = None
            result['height_confidence'] = 0

    return result


def pick_best_measurement(analyses, key, conf_key):
    """
    From multiple photo analyses, pick the measurement with highest confidence.
    Returns (value_meters, confidence, photo_index).
    """
    best_val = None
    best_conf = -1
    best_idx = -1

    for i, a in enumerate(analyses):
        val = a.get(key)
        conf = a.get(conf_key, 0)
        if val is not None and conf > best_conf:
            best_val = val
            best_conf = conf
            best_idx = i

    return best_val, best_conf, best_idx


def m_to_ft(m):
    """Convert meters to feet."""
    return m * 3.28084


def ft_to_ft_in(ft):
    """Convert decimal feet to feet'inches\" string."""
    feet = int(ft)
    inches = (ft - feet) * 12
    return f"{feet}'{inches:.1f}\""


def combine_measurements(analyses, image_names):
    """
    Combine measurements from multiple photos to get best room dimensions.

    Strategy:
      - WIDTH: Use the photo where both left+right walls were detected (highest confidence)
      - LENGTH: Use the photo with strongest far_wall detection
      - HEIGHT: Average across photos where floor+ceiling were found, weighted by confidence
    """
    print("\n" + "=" * 60)
    print("  COMBINED ROOM MEASUREMENT")
    print("=" * 60)

    results = {}

    # --- WIDTH ---
    width_m, width_conf, width_idx = pick_best_measurement(
        analyses, 'width_m', 'width_confidence'
    )
    if width_m is not None:
        width_ft = m_to_ft(width_m)
        results['width_m'] = round(width_m, 3)
        results['width_ft'] = round(width_ft, 2)
        results['width_source'] = image_names[width_idx]
        results['width_confidence'] = width_conf

        print(f"\n  WIDTH:  {width_ft:.2f} ft  ({ft_to_ft_in(width_ft)})")
        print(f"    Source: {image_names[width_idx]} (confidence: {width_conf})")

        # Out of square info
        sq = analyses[width_idx].get('width_out_of_square')
        if sq:
            if sq['delta_inches'] < 0.5:
                print(f"    Squareness: SQUARE (delta < 0.5\")")
            else:
                print(f"    Squareness: OUT OF SQUARE by {sq['delta_inches']:.1f}\"")
                print(f"      Min: {m_to_ft(sq['min_m']):.2f} ft  Max: {m_to_ft(sq['max_m']):.2f} ft")
                results['width_out_of_square_inches'] = round(sq['delta_inches'], 1)
    else:
        print("\n  WIDTH:  Could not determine (no photo captured both side walls)")
        print("    TIP: Take a photo facing a side wall so both left+right walls are visible")

    # --- LENGTH (far wall distance) ---
    # For length, we want the BEST far wall detection
    # If we have opposing photos, we could also average or cross-check
    length_m, length_conf, length_idx = pick_best_measurement(
        analyses, 'far_wall_dist_m', 'far_wall_confidence'
    )
    if length_m is not None:
        length_ft = m_to_ft(length_m)
        results['length_camera_to_wall_m'] = round(length_m, 3)
        results['length_camera_to_wall_ft'] = round(length_ft, 2)
        results['length_source'] = image_names[length_idx]
        results['length_confidence'] = length_conf

        print(f"\n  LENGTH: {length_ft:.2f} ft  ({ft_to_ft_in(length_ft)})  [camera → far wall]")
        print(f"    Source: {image_names[length_idx]} (confidence: {length_conf})")

        if length_conf == 0:
            print(f"    WARNING: No clear far wall plane detected, this is a fallback estimate")

        # Check if we have an opposing photo to cross-reference
        # If two photos face opposite walls, their far_wall distances should
        # both approximate the room length (each missing the camera offset)
        far_dists = []
        for i, a in enumerate(analyses):
            if a.get('far_wall_confidence', 0) > 0:
                far_dists.append((i, a['far_wall_dist_m']))

        if len(far_dists) >= 2:
            print(f"\n    Cross-reference from {len(far_dists)} photos with far wall detection:")
            for idx, dist in far_dists:
                print(f"      {image_names[idx]}: {m_to_ft(dist):.2f} ft")

            # The longest far_wall distance is likely the most accurate
            # (closer to true wall-to-wall since camera was further back)
            best_length = max(far_dists, key=lambda x: x[1])
            avg_length = np.mean([d for _, d in far_dists])

            results['length_best_ft'] = round(m_to_ft(best_length[1]), 2)
            results['length_avg_ft'] = round(m_to_ft(avg_length), 2)

            print(f"    Best (longest): {m_to_ft(best_length[1]):.2f} ft from {image_names[best_length[0]]}")
            print(f"    Average:        {m_to_ft(avg_length):.2f} ft")
            print(f"    NOTE: True wall-to-wall is LONGER than these (camera wasn't at the wall)")

    # --- HEIGHT ---
    heights = []
    for i, a in enumerate(analyses):
        h = a.get('height_m')
        conf = a.get('height_confidence', 0)
        if h is not None and h > 1.5 and h < 5.0:  # sanity check: 5-16 ft
            heights.append((i, h, conf))

    if heights:
        # Weight by confidence
        total_conf = sum(c for _, _, c in heights)
        if total_conf > 0:
            weighted_height = sum(h * c for _, h, c in heights) / total_conf
        else:
            weighted_height = np.mean([h for _, h, _ in heights])

        height_ft = m_to_ft(weighted_height)
        results['height_m'] = round(weighted_height, 3)
        results['height_ft'] = round(height_ft, 2)

        print(f"\n  HEIGHT: {height_ft:.2f} ft  ({ft_to_ft_in(height_ft)})")
        if len(heights) > 1:
            print(f"    Weighted average from {len(heights)} photos:")
            for idx, h, conf in heights:
                print(f"      {image_names[idx]}: {m_to_ft(h):.2f} ft (confidence: {conf})")
    else:
        print(f"\n  HEIGHT: Could not determine reliably")

    # --- FLOOR AREA ---
    if 'width_ft' in results:
        length_for_area = results.get('length_best_ft',
                          results.get('length_camera_to_wall_ft', 0))
        if length_for_area > 0:
            area = results['width_ft'] * length_for_area
            results['floor_area_sqft'] = round(area, 1)
            print(f"\n  FLOOR AREA: ~{area:.0f} sq ft (approximate — length is camera-to-wall)")

    print("\n" + "=" * 60)

    return results


def check_accuracy(results, actual_length=None, actual_width=None, actual_height=None):
    """Compare estimates to known measurements and print accuracy report."""
    print("\n  ACCURACY CHECK vs Tape Measurements")
    print("  " + "-" * 40)

    checks = []

    if actual_width and 'width_ft' in results:
        est = results['width_ft']
        err_ft = abs(est - actual_width)
        err_in = err_ft * 12
        err_pct = (err_ft / actual_width) * 100
        status = "✅" if err_in <= 1.0 else "⚠️" if err_in <= 3.0 else "❌"
        print(f"  {status} Width:  {est:.2f} ft est vs {actual_width:.2f} ft actual "
              f"(off by {err_in:.1f}\" / {err_pct:.1f}%)")
        checks.append(('width', err_in))

    if actual_length:
        # Check against best available length
        length_est = results.get('length_best_ft',
                     results.get('length_camera_to_wall_ft'))
        if length_est:
            err_ft = abs(length_est - actual_length)
            err_in = err_ft * 12
            err_pct = (err_ft / actual_length) * 100
            status = "✅" if err_in <= 1.0 else "⚠️" if err_in <= 3.0 else "❌"
            print(f"  {status} Length: {length_est:.2f} ft est vs {actual_length:.2f} ft actual "
                  f"(off by {err_in:.1f}\" / {err_pct:.1f}%)")
            print(f"       (Note: estimate is camera→wall, true wall-to-wall is longer)")
            checks.append(('length', err_in))

    if actual_height and 'height_ft' in results:
        est = results['height_ft']
        err_ft = abs(est - actual_height)
        err_in = err_ft * 12
        err_pct = (err_ft / actual_height) * 100
        status = "✅" if err_in <= 1.0 else "⚠️" if err_in <= 3.0 else "❌"
        print(f"  {status} Height: {est:.2f} ft est vs {actual_height:.2f} ft actual "
              f"(off by {err_in:.1f}\" / {err_pct:.1f}%)")
        checks.append(('height', err_in))

    if checks:
        avg_err = np.mean([e for _, e in checks])
        print(f"\n  Average error: {avg_err:.1f} inches across {len(checks)} dimensions")
        if avg_err <= 1.0:
            print(f"  VERDICT: Tape-measure accurate!")
        elif avg_err <= 3.0:
            print(f"  VERDICT: Close but needs calibration refinement")
        else:
            print(f"  VERDICT: Needs improvement — check photo angles and room obstructions")


def save_combined_visualization(analyses, image_names, results, output_path):
    """Create a combined floor plan from all photo analyses."""
    fig, axes = plt.subplots(1, len(analyses) + 1, figsize=(6 * (len(analyses) + 1), 6))

    if len(analyses) == 1:
        axes = [axes, plt.subplot(1, 2, 2)]

    colors_by_type = {
        'floor': '#888888', 'ceiling': '#AAAAAA',
        'left_wall': '#E74C3C', 'right_wall': '#3498DB',
        'far_wall': '#2ECC71', 'near_wall': '#F39C12',
        'unknown': '#95A5A6',
    }
    wall_types = {'left_wall', 'right_wall', 'far_wall', 'near_wall'}

    # Individual floor plans
    for i, (analysis, name) in enumerate(zip(analyses, image_names)):
        ax = axes[i]
        for plane in analysis['planes']:
            pts = plane['inlier_points']
            ptype = plane['type']
            if ptype in wall_types:
                color = colors_by_type.get(ptype, '#95A5A6')
                ax.scatter(pts[:, 0], pts[:, 2], c=color, s=1, alpha=0.3, label=ptype)

        ax.plot(0, 0, 'k^', markersize=12, zorder=5)
        ax.set_title(name, fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Z (m)')

    # Summary panel
    ax_summary = axes[-1]
    ax_summary.axis('off')

    summary_text = "COMBINED MEASUREMENTS\n" + "=" * 30 + "\n\n"
    if 'width_ft' in results:
        summary_text += f"Width:  {results['width_ft']:.2f} ft ({ft_to_ft_in(results['width_ft'])})\n"
    length_ft = results.get('length_best_ft', results.get('length_camera_to_wall_ft'))
    if length_ft:
        summary_text += f"Length: {length_ft:.2f} ft ({ft_to_ft_in(length_ft)})\n"
        summary_text += f"  (camera to wall)\n"
    if 'height_ft' in results:
        summary_text += f"Height: {results['height_ft']:.2f} ft ({ft_to_ft_in(results['height_ft'])})\n"
    if 'floor_area_sqft' in results:
        summary_text += f"\nFloor: ~{results['floor_area_sqft']:.0f} sq ft\n"
    if 'width_out_of_square_inches' in results:
        summary_text += f"\nOut of square: {results['width_out_of_square_inches']:.1f}\"\n"

    ax_summary.text(0.1, 0.9, summary_text, transform=ax_summary.transAxes,
                    fontsize=12, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved combined visualization: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="LayIt Room Scan - Combine multiple photos for accurate room measurement"
    )
    parser.add_argument("targets", nargs='+', help="Image files or folder of images")
    parser.add_argument("--actual-length", type=float, default=None,
                        help="Known room length in feet (for accuracy check)")
    parser.add_argument("--actual-width", type=float, default=None,
                        help="Known room width in feet (for accuracy check)")
    parser.add_argument("--actual-height", type=float, default=None,
                        help="Known room height in feet (for accuracy check)")
    parser.add_argument("--subsample", type=int, default=4,
                        help="Point cloud subsample factor (default: 4)")

    args = parser.parse_args()

    # Collect image paths
    image_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp'}
    image_paths = []

    for target in args.targets:
        if os.path.isdir(target):
            import glob as globmod
            for ext in image_extensions:
                image_paths.extend(globmod.glob(os.path.join(target, f"*{ext}")))
                image_paths.extend(globmod.glob(os.path.join(target, f"*{ext.upper()}")))
        elif os.path.isfile(target):
            image_paths.append(target)

    image_paths = sorted(set(image_paths))

    if not image_paths:
        print("No images found!")
        sys.exit(1)

    print(f"Processing {len(image_paths)} photos...")
    print(f"Photos: {[Path(p).name for p in image_paths]}")

    # Load model once
    model, transform, device = load_model()

    # Analyze each photo
    analyses = []
    image_names = []

    for img_path in image_paths:
        img_path = Path(img_path)
        image_names.append(img_path.name)

        # Run depth estimation
        depth_map, focal_px, image = estimate_depth(model, transform, device, img_path)

        # Save depth visualization
        depth_out = img_path.parent / f"{img_path.stem}_depth.png"
        save_depth_visualization(depth_map, image, depth_out)

        # Analyze planes
        analysis = analyze_photo(depth_map, focal_px, image.shape, subsample=args.subsample)
        analyses.append(analysis)

        # Print per-photo summary
        print(f"\n  {img_path.name} summary:")
        print(f"    Far wall:  {m_to_ft(analysis['far_wall_dist_m']):.2f} ft "
              f"(conf: {analysis['far_wall_confidence']})")
        if analysis['width_m']:
            print(f"    Width:     {m_to_ft(analysis['width_m']):.2f} ft "
                  f"(conf: {analysis['width_confidence']})")
        else:
            print(f"    Width:     N/A (couldn't see both side walls)")
        if analysis['height_m']:
            print(f"    Height:    {m_to_ft(analysis['height_m']):.2f} ft "
                  f"(conf: {analysis['height_confidence']})")

    # Combine measurements
    results = combine_measurements(analyses, image_names)

    # Accuracy check if actuals provided
    if any([args.actual_length, args.actual_width, args.actual_height]):
        check_accuracy(results, args.actual_length, args.actual_width, args.actual_height)

    # Save combined visualization
    output_dir = Path(image_paths[0]).parent
    save_combined_visualization(
        analyses, image_names, results,
        output_dir / "room_combined.png"
    )

    # Save JSON
    output_json = output_dir / "room_combined.json"
    clean_results = {k: v for k, v in results.items() if not k.startswith('_')}
    # Convert numpy types to native Python for JSON serialization
    def make_serializable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        return obj

    with open(output_json, 'w') as f:
        json.dump(make_serializable({
            'measurements': clean_results,
            'photos': image_names,
            'model': 'Apple Depth Pro v1',
            'method': 'multi-photo RANSAC',
        }), f, indent=2)
    print(f"Saved measurements to: {output_json}")


if __name__ == "__main__":
    main()
