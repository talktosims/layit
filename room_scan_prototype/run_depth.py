#!/usr/bin/env python3
"""
LayIt Room Scan Prototype
=========================
Takes phone photos of a room, runs Apple Depth Pro to get metric depth maps,
then extracts wall positions and room dimensions using RANSAC plane fitting.

Usage:
    python run_depth.py <image_path_or_folder> [options]
    python run_depth.py photo1.jpg
    python run_depth.py photo1.jpg --camera-offset 0.3
    python run_depth.py ./my_room_photos/

Options:
    --camera-offset METERS   Distance from camera to wall behind user (default: 0.0)
                             Set to ~0.3 (12") when standing with back near a wall.
    --no-ransac              Disable RANSAC plane fitting, use legacy percentile method
    --subsample N            Point cloud subsample factor (default: 4, higher = faster)

Output:
    - Depth map visualization (saved as *_depth.png next to each input)
    - Top-down floor plan view (saved as *_floorplan.png)
    - Console output with estimated room dimensions (raw + offset-corrected)
    - JSON file with structured measurements
"""

import sys
import os
import json
import glob
import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# Add depth pro to path
SCRIPT_DIR = Path(__file__).parent
DEPTH_PRO_DIR = SCRIPT_DIR / "ml-depth-pro"
sys.path.insert(0, str(DEPTH_PRO_DIR / "src"))

import depth_pro


# =============================================================================
# Model loading
# =============================================================================

def load_model():
    """Load Depth Pro model with Apple Silicon (MPS) acceleration."""
    print("Loading Depth Pro model...")

    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("  Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("  Using NVIDIA GPU (CUDA)")
    else:
        device = torch.device("cpu")
        print("  Using CPU (will be slower)")

    checkpoint_path = str(DEPTH_PRO_DIR / "checkpoints" / "depth_pro.pt")
    config = depth_pro.depth_pro.DEFAULT_MONODEPTH_CONFIG_DICT
    config.checkpoint_uri = checkpoint_path

    model, transform = depth_pro.create_model_and_transforms(
        config=config,
        device=device,
        precision=torch.float32,
    )
    model.eval()

    return model, transform, device


def estimate_depth(model, transform, device, image_path):
    """Run depth estimation on a single image. Returns metric depth in meters."""
    print(f"\nProcessing: {image_path}")

    image, _, f_px = depth_pro.load_rgb(str(image_path))
    image_tensor = transform(image)

    with torch.no_grad():
        prediction = model.infer(image_tensor, f_px=f_px)

    depth_raw = prediction["depth"]
    depth_map = depth_raw.cpu().numpy() if hasattr(depth_raw, 'cpu') else np.array(depth_raw)
    fl_raw = prediction["focallength_px"]
    focallength_px = fl_raw.cpu().item() if hasattr(fl_raw, 'cpu') else float(fl_raw)

    print(f"  Image size: {image.shape[1]}x{image.shape[0]}")
    print(f"  Focal length: {focallength_px:.1f} px")
    print(f"  Depth range: {depth_map.min():.2f}m - {depth_map.max():.2f}m")

    return depth_map, focallength_px, image


# =============================================================================
# 3D point cloud
# =============================================================================

def depth_to_3d_points(depth_map, focallength_px):
    """
    Convert a depth map to a 3D point cloud using the pinhole camera model.

    Each pixel (u, v) with depth Z maps to:
        X = (u - cx) * Z / f
        Y = (v - cy) * Z / f
        Z = Z

    Where X = horizontal, Y = vertical (down), Z = forward/depth.
    """
    h, w = depth_map.shape
    cx, cy = w / 2.0, h / 2.0

    u = np.arange(w)[np.newaxis, :]
    v = np.arange(h)[:, np.newaxis]

    X = (u - cx) * depth_map / focallength_px
    Y = (v - cy) * depth_map / focallength_px
    Z = depth_map

    return X, Y, Z


# =============================================================================
# RANSAC plane fitting
# =============================================================================

def fit_plane_ransac(points, n_iterations=1000, distance_threshold=0.02):
    """
    Fit a plane to a 3D point cloud using RANSAC.

    Args:
        points: (N, 3) array of 3D points
        n_iterations: number of RANSAC iterations
        distance_threshold: max distance (meters) for a point to be an inlier

    Returns:
        best_normal: (3,) unit normal vector of the best plane
        best_d: scalar d in the plane equation ax + by + cz + d = 0
        best_inlier_mask: (N,) boolean mask of inlier points
    """
    N = len(points)
    if N < 3:
        return None, None, None

    # Seed RNG for reproducible plane detection across runs
    rng = np.random.RandomState(42)

    best_inlier_count = 0
    best_normal = None
    best_d = None
    best_inlier_mask = None

    for _ in range(n_iterations):
        # Sample 3 random points
        idx = rng.choice(N, 3, replace=False)
        p1, p2, p3 = points[idx[0]], points[idx[1]], points[idx[2]]

        # Compute plane normal via cross product
        v1 = p2 - p1
        v2 = p3 - p1
        normal = np.cross(v1, v2)
        norm_len = np.linalg.norm(normal)
        if norm_len < 1e-10:
            continue
        normal = normal / norm_len

        # Plane equation: normal . (x - p1) = 0  =>  normal . x + d = 0
        d = -np.dot(normal, p1)

        # Compute distances from all points to this plane
        distances = np.abs(points @ normal + d)

        # Count inliers
        inlier_mask = distances < distance_threshold
        inlier_count = np.sum(inlier_mask)

        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_normal = normal
            best_d = d
            best_inlier_mask = inlier_mask

    return best_normal, best_d, best_inlier_mask


def classify_plane(normal):
    """
    Classify a plane by its normal direction.

    Returns one of: 'floor', 'ceiling', 'left_wall', 'right_wall',
                    'far_wall', 'near_wall', 'angled_ceiling', 'angled_floor', 'unknown'

    Distinguishes between true horizontal surfaces (normal nearly vertical)
    and angled surfaces (like vaulted/cathedral ceilings or ramps).
    A true floor/ceiling has its Y component > 0.85 (within ~30° of vertical).
    An angled surface has Y between 0.5 and 0.85.
    """
    abs_normal = np.abs(normal)
    dominant_axis = np.argmax(abs_normal)

    # Thresholds
    horizontal_threshold = 0.85   # True floor/ceiling (nearly horizontal surface)
    angled_threshold = 0.5        # Angled ceiling/floor (sloped surface)
    wall_threshold = 0.6          # Walls

    # Y-axis dominant (vertical normal) = floor or ceiling
    if dominant_axis == 1 and abs_normal[1] > horizontal_threshold:
        return 'floor' if normal[1] > 0 else 'ceiling'

    # Angled ceiling/floor: Y is dominant but not strongly vertical
    if dominant_axis == 1 and abs_normal[1] > angled_threshold:
        return 'angled_floor' if normal[1] > 0 else 'angled_ceiling'

    # Also catch angled surfaces where Y isn't dominant but is significant
    if abs_normal[1] > angled_threshold and abs_normal[1] > 0.4:
        if dominant_axis == 0 or dominant_axis == 2:
            # The surface is tilted — more like a slope than a wall
            return 'angled_floor' if normal[1] > 0 else 'angled_ceiling'

    # X-axis dominant = left or right wall
    if dominant_axis == 0 and abs_normal[0] > wall_threshold:
        return 'right_wall' if normal[0] > 0 else 'left_wall'

    # Z-axis dominant = far or near wall
    if dominant_axis == 2 and abs_normal[2] > wall_threshold:
        return 'far_wall' if normal[2] > 0 else 'near_wall'

    return 'unknown'


def detect_planes_ransac(X, Y, Z, subsample=4, max_planes=6,
                         n_iterations=500, distance_threshold=0.03):
    """
    Detect multiple planes in the point cloud using iterative RANSAC.

    Args:
        X, Y, Z: 2D arrays from depth_to_3d_points
        subsample: take every Nth pixel for speed
        max_planes: maximum number of planes to detect
        n_iterations: RANSAC iterations per plane
        distance_threshold: inlier threshold in meters

    Returns:
        planes: list of dicts with 'normal', 'd', 'type', 'inlier_points', 'inlier_count'
    """
    # Subsample and flatten to Nx3
    X_sub = X[::subsample, ::subsample].flatten()
    Y_sub = Y[::subsample, ::subsample].flatten()
    Z_sub = Z[::subsample, ::subsample].flatten()

    # Filter out very close or very far points (likely noise)
    valid = (Z_sub > 0.3) & (Z_sub < 15.0)
    points = np.stack([X_sub[valid], Y_sub[valid], Z_sub[valid]], axis=1)

    planes = []
    remaining_points = points.copy()

    for i in range(max_planes):
        if len(remaining_points) < 100:
            break

        normal, d, inlier_mask = fit_plane_ransac(
            remaining_points, n_iterations=n_iterations,
            distance_threshold=distance_threshold
        )

        if normal is None:
            break

        inlier_count = np.sum(inlier_mask)
        # Stop if plane is too small (less than 5% of remaining points)
        if inlier_count < max(100, 0.05 * len(remaining_points)):
            break

        plane_type = classify_plane(normal)
        inlier_points = remaining_points[inlier_mask]

        planes.append({
            'normal': normal,
            'd': d,
            'type': plane_type,
            'inlier_points': inlier_points,
            'inlier_count': inlier_count,
        })

        # Remove inliers for next iteration
        remaining_points = remaining_points[~inlier_mask]

        print(f"  Plane {i+1}: {plane_type} (normal=[{normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f}], "
              f"{inlier_count} inliers)")

    return planes


# =============================================================================
# Room measurement extraction
# =============================================================================

def plane_distance(plane1, plane2):
    """
    Compute the distance between two planes using their inlier points.
    Uses the median position along the dominant normal axis for robustness.
    """
    pts1 = plane1['inlier_points']
    pts2 = plane2['inlier_points']

    # Use the average normal to determine which axis to measure along
    avg_normal = (plane1['normal'] - plane2['normal'])  # opposite-facing normals subtract
    abs_avg = np.abs(plane1['normal'])
    dominant = np.argmax(abs_avg)

    # Measure distance along the dominant axis using median of each point set
    pos1 = np.median(pts1[:, dominant])
    pos2 = np.median(pts2[:, dominant])
    return abs(pos2 - pos1)


def measure_out_of_square(plane1, plane2, n_samples=10):
    """
    Measure the distance between two wall planes at multiple points to detect
    out-of-square conditions.

    Returns:
        distances: array of distances measured at different positions
        min_dist, max_dist, delta: summary statistics
    """
    pts1 = plane1['inlier_points']
    pts2 = plane2['inlier_points']
    n1 = plane1['normal']

    # Determine the axis along which to sample
    # For walls with X-dominant normals, sample along Z
    # For walls with Z-dominant normals, sample along X
    abs_n = np.abs(n1)
    if abs_n[0] > abs_n[2]:
        # X-normal walls (left/right), sample along Z
        sample_axis = 2
        measure_axis = 0
    else:
        # Z-normal walls (front/back), sample along X
        sample_axis = 0
        measure_axis = 2

    # Get the range along the sample axis
    all_pts = np.vstack([pts1, pts2])
    sample_min = np.percentile(all_pts[:, sample_axis], 5)
    sample_max = np.percentile(all_pts[:, sample_axis], 95)
    sample_positions = np.linspace(sample_min, sample_max, n_samples)

    distances = []
    bin_width = (sample_max - sample_min) / n_samples * 1.5

    for pos in sample_positions:
        # Find points near this sample position on each plane
        mask1 = np.abs(pts1[:, sample_axis] - pos) < bin_width
        mask2 = np.abs(pts2[:, sample_axis] - pos) < bin_width

        if np.sum(mask1) < 5 or np.sum(mask2) < 5:
            continue

        # Measure distance along the measurement axis
        val1 = np.median(pts1[mask1, measure_axis])
        val2 = np.median(pts2[mask2, measure_axis])
        distances.append(abs(val2 - val1))

    if len(distances) < 2:
        return None, None, None, None

    distances = np.array(distances)
    return distances, float(np.min(distances)), float(np.max(distances)), float(np.max(distances) - np.min(distances))


def analyze_room_ransac(depth_map, focallength_px, image_shape, camera_offset=0.0, subsample=4):
    """
    Extract room dimensions using RANSAC plane fitting.
    """
    h, w = depth_map.shape
    results = {}

    print("\n  --- RANSAC Plane Detection ---")
    X, Y, Z = depth_to_3d_points(depth_map, focallength_px)

    planes = detect_planes_ransac(X, Y, Z, subsample=subsample)

    # Organize planes by type
    planes_by_type = {}
    for p in planes:
        ptype = p['type']
        if ptype not in planes_by_type:
            planes_by_type[ptype] = []
        planes_by_type[ptype].append(p)

    results['detected_planes'] = [
        {'type': p['type'],
         'normal': [round(float(n), 3) for n in p['normal']],
         'inlier_count': int(p['inlier_count'])}
        for p in planes
    ]

    # --- ROOM LENGTH (Z-axis: camera to far wall) ---
    far_walls = planes_by_type.get('far_wall', [])
    if far_walls:
        # Use the far wall plane with the most inliers
        far_wall = max(far_walls, key=lambda p: p['inlier_count'])
        # Distance from origin (camera) to the far wall plane
        room_length_raw_m = abs(far_wall['d'])
    else:
        # Fallback: use the 85th percentile of center depths
        center_depths = Z[h//4:3*h//4, w//4:3*w//4].flatten()
        room_length_raw_m = float(np.percentile(center_depths, 85))
        print("  WARNING: No far wall plane detected, using depth percentile fallback")

    room_length_corrected_m = room_length_raw_m + camera_offset

    results["room_length_raw_m"] = round(float(room_length_raw_m), 3)
    results["room_length_raw_ft"] = round(float(room_length_raw_m * 3.28084), 2)
    results["room_length_corrected_m"] = round(float(room_length_corrected_m), 3)
    results["room_length_corrected_ft"] = round(float(room_length_corrected_m * 3.28084), 2)
    results["camera_offset_m"] = round(float(camera_offset), 3)

    # --- ROOM WIDTH (X-axis: left wall to right wall) ---
    left_walls = planes_by_type.get('left_wall', [])
    right_walls = planes_by_type.get('right_wall', [])

    if left_walls and right_walls:
        left_wall = max(left_walls, key=lambda p: p['inlier_count'])
        right_wall = max(right_walls, key=lambda p: p['inlier_count'])
        room_width_m = plane_distance(left_wall, right_wall)

        # Out-of-square check
        sq_dists, sq_min, sq_max, sq_delta = measure_out_of_square(left_wall, right_wall)
        if sq_dists is not None:
            results['width_out_of_square'] = {
                'min_ft': round(float(sq_min * 3.28084), 2),
                'max_ft': round(float(sq_max * 3.28084), 2),
                'delta_inches': round(float(sq_delta * 39.3701), 1),
                'is_square': sq_delta < 0.013,  # < 0.5 inch
            }
            if sq_delta >= 0.013:
                print(f"  WARNING: Walls out of square! Width varies by {sq_delta*39.3701:.1f} inches")
    else:
        # Fallback: use median X at image edges
        mid_h = slice(h//3, 2*h//3)
        left_X = X[mid_h, :int(w*0.15)].flatten()
        right_X = X[mid_h, int(w*0.85):].flatten()
        room_width_m = abs(np.median(right_X) - np.median(left_X))
        print("  WARNING: Could not find both side walls, using edge fallback")

    results["room_width_m"] = round(float(room_width_m), 3)
    results["room_width_ft"] = round(float(room_width_m * 3.28084), 2)

    # --- CEILING HEIGHT (Y-axis: floor to ceiling) ---
    floors = planes_by_type.get('floor', [])
    ceilings = planes_by_type.get('ceiling', [])
    angled_ceilings = planes_by_type.get('angled_ceiling', [])
    angled_floors = planes_by_type.get('angled_floor', [])

    # Angled surfaces are tricky — an "angled_floor" might actually be an angled
    # ceiling seen from below (positive Y normal because camera looks up at it).
    # Use the median Y position to disambiguate: if the surface is in the upper
    # half of the scene (negative Y in camera coords), it's a ceiling.
    for af in angled_floors[:]:
        median_y = np.median(af['inlier_points'][:, 1])
        if median_y < 0:
            # This surface is above the camera center — it's an angled ceiling, not floor
            af['type'] = 'angled_ceiling'
            angled_ceilings.append(af)
            angled_floors.remove(af)
            print(f"  NOTE: Reclassified angled_floor as angled_ceiling (median Y={median_y:.2f}, above camera)")

    # Find the best floor plane
    floor_plane = None
    if floors:
        floor_plane = max(floors, key=lambda p: p['inlier_count'])
    elif angled_floors:
        # An angled_floor might actually be the floor if no true floor was detected
        # Only use it if its Y component is reasonably strong (> 0.7)
        best_af = max(angled_floors, key=lambda p: p['inlier_count'])
        if abs(best_af['normal'][1]) > 0.7:
            floor_plane = best_af
            print("  NOTE: Using angled surface as floor plane")

    room_height_m = None
    height_method = None

    if floor_plane and ceilings:
        # Best case: true floor + true ceiling
        ceiling_plane = max(ceilings, key=lambda p: p['inlier_count'])
        room_height_m = plane_distance(floor_plane, ceiling_plane)
        height_method = 'floor_ceiling_planes'

    elif floor_plane and angled_ceilings:
        # Angled ceiling detected — compute height at the highest visible point
        # and also try to find where the flat part starts
        angled_ceil = max(angled_ceilings, key=lambda p: p['inlier_count'])

        # The height varies along the angled ceiling.
        # Use the Y extent of the room: max floor Y to min ceiling Y
        floor_y_median = np.median(floor_plane['inlier_points'][:, 1])
        ceil_y_values = angled_ceil['inlier_points'][:, 1]

        # The minimum Y on the angled ceiling = the highest point of the ceiling
        # (Y points downward in camera coords, so min Y = highest)
        ceil_y_min = np.percentile(ceil_y_values, 5)  # Use 5th percentile for robustness
        ceil_y_max = np.percentile(ceil_y_values, 95)

        # Height at highest point of angled ceiling
        max_height_m = abs(floor_y_median - ceil_y_min)
        # Height at lowest point of angled ceiling (where it meets the wall/knee wall)
        min_height_m = abs(floor_y_median - ceil_y_max)

        # Use the max height as the room height (flat ceiling height)
        room_height_m = max_height_m
        height_method = 'angled_ceiling'

        results['angled_ceiling'] = {
            'max_height_ft': round(float(max_height_m * 3.28084), 2),
            'min_height_ft': round(float(min_height_m * 3.28084), 2),
            'ceiling_slope_deg': round(float(np.degrees(np.arccos(abs(angled_ceil['normal'][1])))), 1),
        }
        print(f"  Angled ceiling detected:")
        print(f"    Max height: {max_height_m * 3.28084:.1f} ft")
        print(f"    Min height (at knee wall): {min_height_m * 3.28084:.1f} ft")
        print(f"    Ceiling slope: {np.degrees(np.arccos(abs(angled_ceil['normal'][1]))):.0f}°")

    elif not floor_plane and (ceilings or angled_ceilings):
        # No floor plane detected — try multiple strategies to estimate floor Y

        # Strategy A: Use wall plane extents (most reliable when walls are detected)
        # Wall inlier points span from floor to ceiling, so max Y = floor level
        wall_types_for_height = ['left_wall', 'right_wall', 'far_wall', 'near_wall']
        wall_planes_all = []
        for wt in wall_types_for_height:
            wall_planes_all.extend(planes_by_type.get(wt, []))

        floor_y_est = None
        floor_est_method = None

        if wall_planes_all:
            # Collect Y values from all wall inlier points
            all_wall_y = np.concatenate([p['inlier_points'][:, 1] for p in wall_planes_all])
            # The 95th percentile Y of wall points ≈ floor level
            # (Y points down in camera coords, so high Y = low in room = floor)
            wall_floor_y = np.percentile(all_wall_y, 95)
            floor_y_est = wall_floor_y
            floor_est_method = 'wall_extent'
            print(f"  Floor estimated from wall extents (Y={floor_y_est:.3f}m)")

        # Strategy B: Depth-aware bottom-of-image fallback
        # Only use points near the back wall depth, not close-up furniture
        if floor_y_est is None:
            back_wall_depth = room_length_raw_m
            floor_region_Y = Y[int(h*0.7):, :].flatten()
            floor_region_Z = Z[int(h*0.7):, :].flatten()

            # Filter for points at reasonable depth (within 50% of back wall depth)
            # This excludes close furniture (vanity, toilet) that skew the estimate
            depth_mask = (floor_region_Z > back_wall_depth * 0.4) & \
                         (floor_region_Z < back_wall_depth * 1.5)

            if np.sum(depth_mask) > 50:
                floor_y_est = np.percentile(floor_region_Y[depth_mask], 90)
                floor_est_method = 'depth_filtered_edge'
                print(f"  Floor estimated from depth-filtered edge (Y={floor_y_est:.3f}m)")
            else:
                # Final fallback: use all bottom-of-image points
                floor_Y_edge = Y[int(h*0.85):, w//4:3*w//4].flatten()
                floor_y_est = np.median(floor_Y_edge)
                floor_est_method = 'raw_edge'
                print(f"  Floor estimated from raw image edge (Y={floor_y_est:.3f}m)")

        if ceilings:
            ceiling_plane = max(ceilings, key=lambda p: p['inlier_count'])
            ceil_y_est = np.median(ceiling_plane['inlier_points'][:, 1])
            room_height_m = abs(floor_y_est - ceil_y_est)
            height_method = f'ceiling_plane_floor_{floor_est_method}'
        elif angled_ceilings:
            # Use the highest point of the angled ceiling
            angled_ceil = max(angled_ceilings, key=lambda p: p['inlier_count'])
            ceil_y_min = np.percentile(angled_ceil['inlier_points'][:, 1], 5)
            ceil_y_max = np.percentile(angled_ceil['inlier_points'][:, 1], 95)
            room_height_m = abs(floor_y_est - ceil_y_min)
            height_method = f'angled_ceiling_floor_{floor_est_method}'

            results['angled_ceiling'] = {
                'max_height_ft': round(float(abs(floor_y_est - ceil_y_min) * 3.28084), 2),
                'min_height_ft': round(float(abs(floor_y_est - ceil_y_max) * 3.28084), 2),
                'ceiling_slope_deg': round(float(np.degrees(np.arccos(abs(angled_ceil['normal'][1])))), 1),
            }
            print(f"  Angled ceiling detected (no floor plane):")
            print(f"    Max height: {abs(floor_y_est - ceil_y_min) * 3.28084:.1f} ft")
            print(f"    Min height: {abs(floor_y_est - ceil_y_max) * 3.28084:.1f} ft")

        print(f"  WARNING: No floor plane detected, used {floor_est_method} fallback for floor")

    if room_height_m is None:
        # Full fallback: try wall extents first, then image edges
        wall_types_for_height = ['left_wall', 'right_wall', 'far_wall', 'near_wall']
        wall_planes_all = []
        for wt in wall_types_for_height:
            wall_planes_all.extend(planes_by_type.get(wt, []))

        if wall_planes_all:
            all_wall_y = np.concatenate([p['inlier_points'][:, 1] for p in wall_planes_all])
            floor_y_est = np.percentile(all_wall_y, 95)
            ceil_y_est = np.percentile(all_wall_y, 5)
            room_height_m = abs(floor_y_est - ceil_y_est)
            height_method = 'wall_extent_fallback'
            print(f"  WARNING: No floor/ceiling planes, using wall extent fallback")
        else:
            ceil_Y = Y[:int(h*0.15), w//4:3*w//4].flatten()
            floor_Y = Y[int(h*0.85):, w//4:3*w//4].flatten()
            room_height_m = abs(np.median(floor_Y) - np.median(ceil_Y))
            height_method = 'edge_fallback'
            print("  WARNING: Could not find any planes, using edge fallback")

    results["room_height_m"] = round(float(room_height_m), 3)
    results["room_height_ft"] = round(float(room_height_m * 3.28084), 2)
    results["height_method"] = height_method

    # --- Diagnostic info ---
    results["depth_range_m"] = f"{depth_map.min():.2f} - {depth_map.max():.2f}"
    results["floor_area_sqft"] = round(
        results["room_length_corrected_ft"] * results["room_width_ft"], 1
    )

    # Store plane data for floor plan visualization
    results['_planes'] = planes
    results['_X'] = X
    results['_Z'] = Z

    return results


def analyze_room_legacy(depth_map, focallength_px, image_shape, camera_offset=0.0):
    """
    Legacy room analysis using percentile-based heuristics (no RANSAC).
    Kept for comparison/fallback.
    """
    h, w = depth_map.shape
    results = {}

    X, Y, Z = depth_to_3d_points(depth_map, focallength_px)

    # Room length (Z-axis)
    center_depths = Z[h//4:3*h//4, w//4:3*w//4].flatten()
    far_wall_z = np.percentile(center_depths, 85)
    room_length_raw_m = far_wall_z

    results["room_length_raw_m"] = round(float(room_length_raw_m), 3)
    results["room_length_raw_ft"] = round(float(room_length_raw_m * 3.28084), 2)
    results["room_length_corrected_m"] = round(float(room_length_raw_m + camera_offset), 3)
    results["room_length_corrected_ft"] = round(float((room_length_raw_m + camera_offset) * 3.28084), 2)
    results["camera_offset_m"] = round(float(camera_offset), 3)

    # Room width (X-axis)
    mid_h = slice(h//3, 2*h//3)
    left_X = X[mid_h, :int(w*0.15)].flatten()
    right_X = X[mid_h, int(w*0.85):].flatten()
    room_width_m = abs(np.median(right_X) - np.median(left_X))

    results["room_width_m"] = round(float(room_width_m), 3)
    results["room_width_ft"] = round(float(room_width_m * 3.28084), 2)

    # Room height (Y-axis)
    ceil_Y = Y[:int(h*0.15), w//4:3*w//4].flatten()
    floor_Y = Y[int(h*0.85):, w//4:3*w//4].flatten()
    room_height_m = abs(np.median(floor_Y) - np.median(ceil_Y))

    results["room_height_m"] = round(float(room_height_m), 3)
    results["room_height_ft"] = round(float(room_height_m * 3.28084), 2)

    results["depth_range_m"] = f"{depth_map.min():.2f} - {depth_map.max():.2f}"
    results["floor_area_sqft"] = round(
        results["room_length_corrected_ft"] * results["room_width_ft"], 1
    )

    return results


# =============================================================================
# Visualization
# =============================================================================

def save_depth_visualization(depth_map, image, output_path):
    """Save a side-by-side visualization of the original image and depth map."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    axes[0].imshow(image)
    axes[0].set_title("Original Photo")
    axes[0].axis("off")

    im = axes[1].imshow(depth_map, cmap="turbo")
    axes[1].set_title("Metric Depth (meters)")
    axes[1].axis("off")
    plt.colorbar(im, ax=axes[1], label="Distance (m)", shrink=0.8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved depth visualization: {output_path}")


def save_floorplan_visualization(measurements, output_path):
    """
    Save a top-down floor plan view showing detected walls as lines.
    Projects wall plane inlier points onto the XZ (horizontal) plane.
    """
    planes = measurements.get('_planes', [])
    if not planes:
        return

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Color map for plane types
    colors = {
        'floor': '#888888',
        'ceiling': '#AAAAAA',
        'left_wall': '#E74C3C',   # red
        'right_wall': '#3498DB',   # blue
        'far_wall': '#2ECC71',     # green
        'near_wall': '#F39C12',    # orange
        'unknown': '#95A5A6',      # gray
    }

    wall_types = {'left_wall', 'right_wall', 'far_wall', 'near_wall'}

    for plane in planes:
        pts = plane['inlier_points']
        ptype = plane['type']
        color = colors.get(ptype, '#95A5A6')

        if ptype in wall_types:
            # Project wall points onto XZ plane (top-down view)
            # X = horizontal, Z = depth (forward)
            ax.scatter(pts[:, 0], pts[:, 2], c=color, s=1, alpha=0.3, label=ptype)

            # Fit a line to the projected wall points for cleaner visualization
            if len(pts) > 10:
                abs_n = np.abs(plane['normal'])
                if abs_n[0] > abs_n[2]:
                    # X-normal wall: appears as vertical line in top-down view
                    x_pos = np.median(pts[:, 0])
                    z_range = [np.percentile(pts[:, 2], 5), np.percentile(pts[:, 2], 95)]
                    ax.plot([x_pos, x_pos], z_range, color=color, linewidth=3, alpha=0.8)
                else:
                    # Z-normal wall: appears as horizontal line in top-down view
                    z_pos = np.median(pts[:, 2])
                    x_range = [np.percentile(pts[:, 0], 5), np.percentile(pts[:, 0], 95)]
                    ax.plot(x_range, [z_pos, z_pos], color=color, linewidth=3, alpha=0.8)

    # Mark camera position
    ax.plot(0, 0, 'k^', markersize=15, label='Camera', zorder=5)
    ax.annotate('Camera', (0, 0), textcoords="offset points",
                xytext=(10, -15), fontsize=10, fontweight='bold')

    # Add dimension annotations
    length_ft = measurements.get('room_length_corrected_ft',
                                 measurements.get('room_length_raw_ft', 0))
    width_ft = measurements.get('room_width_ft', 0)

    ax.set_xlabel('X (meters) - Left/Right', fontsize=12)
    ax.set_ylabel('Z (meters) - Depth/Forward', fontsize=12)
    ax.set_title(f'Top-Down Floor Plan\n'
                 f'Length: {length_ft:.1f} ft  |  Width: {width_ft:.1f} ft',
                 fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # Add legend (deduplicate)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved floor plan: {output_path}")


# =============================================================================
# Main processing
# =============================================================================

def process_images(image_paths, camera_offset=0.0, use_ransac=True, subsample=4):
    """Process a list of images and return combined room measurements."""
    model, transform, device = load_model()

    all_results = []

    for img_path in image_paths:
        img_path = Path(img_path)

        # Run depth estimation
        depth_map, focal_px, image = estimate_depth(model, transform, device, img_path)

        # Analyze room geometry
        if use_ransac:
            measurements = analyze_room_ransac(
                depth_map, focal_px, image.shape,
                camera_offset=camera_offset, subsample=subsample
            )
        else:
            measurements = analyze_room_legacy(
                depth_map, focal_px, image.shape,
                camera_offset=camera_offset
            )

        measurements["image"] = str(img_path.name)
        measurements["method"] = "ransac" if use_ransac else "legacy"

        # Save visualizations
        depth_out = img_path.parent / f"{img_path.stem}_depth.png"
        save_depth_visualization(depth_map, image, depth_out)

        if use_ransac:
            floor_out = img_path.parent / f"{img_path.stem}_floorplan.png"
            save_floorplan_visualization(measurements, floor_out)

        # Print results
        print(f"\n  === Room Dimensions from {img_path.name} ===")
        if camera_offset > 0:
            print(f"  Length (raw):       {measurements['room_length_raw_ft']:.1f} ft ({measurements['room_length_raw_m']:.3f} m)")
            print(f"  Length (corrected): {measurements['room_length_corrected_ft']:.1f} ft ({measurements['room_length_corrected_m']:.3f} m)")
            print(f"    (camera offset:  +{camera_offset:.2f} m / +{camera_offset*39.3701:.0f} inches)")
        else:
            print(f"  Length:        {measurements['room_length_raw_ft']:.1f} ft ({measurements['room_length_raw_m']:.3f} m)")
        print(f"  Width:         {measurements['room_width_ft']:.1f} ft ({measurements['room_width_m']:.3f} m)")
        print(f"  Height:        {measurements['room_height_ft']:.1f} ft ({measurements['room_height_m']:.3f} m)")
        print(f"  Floor area:    {measurements['floor_area_sqft']:.0f} sq ft")

        if 'width_out_of_square' in measurements:
            sq = measurements['width_out_of_square']
            if sq['is_square']:
                print(f"  Squareness:    SQUARE (delta < 0.5\")")
            else:
                print(f"  Squareness:    OUT OF SQUARE by {sq['delta_inches']:.1f}\" "
                      f"(min {sq['min_ft']:.2f} ft, max {sq['max_ft']:.2f} ft)")

        # Clean up internal data before storing
        clean = {k: v for k, v in measurements.items() if not k.startswith('_')}
        all_results.append(clean)

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="LayIt Room Scan - Measure rooms from photos using Apple Depth Pro"
    )
    parser.add_argument("target", help="Image file or folder of images")
    parser.add_argument("--camera-offset", type=float, default=0.0,
                        help="Distance from camera to wall behind user, in meters (default: 0.0). "
                             "Use ~0.3 for 12 inches.")
    parser.add_argument("--no-ransac", action="store_true",
                        help="Disable RANSAC plane fitting, use legacy percentile method")
    parser.add_argument("--subsample", type=int, default=4,
                        help="Point cloud subsample factor (default: 4, higher = faster)")

    args = parser.parse_args()
    target = args.target

    # Collect image paths
    image_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp'}

    if os.path.isdir(target):
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(target, f"*{ext}")))
            image_paths.extend(glob.glob(os.path.join(target, f"*{ext.upper()}")))
        image_paths = sorted(set(image_paths))
        print(f"Found {len(image_paths)} images in {target}")
    elif os.path.isfile(target):
        image_paths = [target]
    else:
        print(f"Error: '{target}' is not a valid file or directory.")
        sys.exit(1)

    if not image_paths:
        print("No images found!")
        sys.exit(1)

    # Process all images
    results = process_images(
        image_paths,
        camera_offset=args.camera_offset,
        use_ransac=not args.no_ransac,
        subsample=args.subsample,
    )

    # If multiple images, compute averages
    if len(results) > 1:
        print("\n" + "=" * 50)
        print("COMBINED ESTIMATE (averaged across all photos)")
        print("=" * 50)

        key = "room_length_corrected_ft" if args.camera_offset > 0 else "room_length_raw_ft"
        avg_length = np.mean([r[key] for r in results])
        avg_width = np.mean([r["room_width_ft"] for r in results])
        avg_height = np.mean([r["room_height_ft"] for r in results])

        print(f"  Length:        ~{avg_length:.1f} ft")
        print(f"  Width:         ~{avg_width:.1f} ft")
        print(f"  Height:        ~{avg_height:.1f} ft")
        print(f"  Floor area:    ~{avg_length * avg_width:.0f} sq ft")

    # Save JSON results
    output_json = Path(image_paths[0]).parent / "room_measurements.json"
    with open(output_json, "w") as f:
        json.dump({
            "images": results,
            "model": "Apple Depth Pro v1",
            "method": "ransac" if not args.no_ransac else "legacy",
            "camera_offset_m": args.camera_offset,
            "note": "Measurements are estimates. 'raw' = direct depth measurement, "
                    "'corrected' = raw + camera offset."
        }, f, indent=2)
    print(f"\nSaved measurements to: {output_json}")

    if args.camera_offset == 0:
        print("\n--- TIP ---")
        print("If you were standing near a wall, try adding --camera-offset 0.3")
        print("to account for the ~12\" between you and the wall behind you.")


if __name__ == "__main__":
    main()
