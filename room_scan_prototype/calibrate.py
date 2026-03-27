#!/usr/bin/env python3
"""
LayIt Calibration Script
========================
Takes a photo + known measurements, runs depth estimation, and computes
error metrics. Saves calibration data to a JSON file that accumulates
over time. After multiple runs, computes optimal correction factors.

Usage:
    python calibrate.py photo.jpg --length 14.25 --width 9 --height 8.25
    python calibrate.py photo.jpg --length 14.25 --width 9 --height 8.25 --camera-offset 0.3
    python calibrate.py --report    # Show calibration summary from accumulated data

All dimensions are in feet.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np

# Add this script's directory to path so we can import run_depth
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_depth import (
    load_model, estimate_depth, depth_to_3d_points,
    analyze_room_ransac, analyze_room_legacy
)

CALIBRATION_FILE = SCRIPT_DIR / "calibration_data.json"


def load_calibration_data():
    """Load existing calibration data or return empty structure."""
    if CALIBRATION_FILE.exists():
        with open(CALIBRATION_FILE) as f:
            return json.load(f)
    return {"runs": [], "correction_factors": None}


def save_calibration_data(data):
    """Save calibration data to JSON file."""
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved calibration data to: {CALIBRATION_FILE}")


def compute_error(estimated, actual):
    """Compute absolute and percentage error."""
    abs_error = estimated - actual
    pct_error = (abs_error / actual) * 100 if actual != 0 else 0
    abs_error_inches = abs_error * 12  # convert feet to inches
    return {
        "estimated_ft": round(estimated, 2),
        "actual_ft": round(actual, 2),
        "abs_error_ft": round(abs_error, 3),
        "abs_error_inches": round(abs_error_inches, 1),
        "pct_error": round(pct_error, 1),
    }


def compute_correction_factors(runs):
    """
    Compute optimal correction factors from accumulated calibration runs.

    Returns multiplicative correction factors: estimated * factor = actual
    """
    if len(runs) < 1:
        return None

    factors = {"length": [], "width": [], "height": []}

    for run in runs:
        for dim in ["length", "width", "height"]:
            if dim in run["errors"]:
                est = run["errors"][dim]["estimated_ft"]
                act = run["errors"][dim]["actual_ft"]
                if est > 0:
                    factors[dim].append(act / est)

    result = {}
    for dim in ["length", "width", "height"]:
        if factors[dim]:
            vals = np.array(factors[dim])

            # Reject outliers: exclude values where the correction ratio is
            # more than 1.4x or less than 0.7x (i.e., > 40% error).
            # These are usually caused by misdetection (e.g., seeing through
            # doorways, mirror reflections, angled ceilings as floor, etc.)
            # A 40% threshold keeps legitimate systematic bias while rejecting
            # clearly broken plane detections.
            reasonable = vals[(vals > 0.7) & (vals < 1.4)]

            if len(reasonable) > 0:
                use_vals = reasonable
                n_rejected = len(vals) - len(reasonable)
                if n_rejected > 0:
                    print(f"  Note: {dim} — rejected {n_rejected} extreme outlier(s)")
            else:
                use_vals = vals  # Keep all if everything is an "outlier"

            result[dim] = {
                "factor": round(float(np.median(use_vals)), 4),
                "mean": round(float(np.mean(use_vals)), 4),
                "std": round(float(np.std(use_vals)), 4),
                "n_samples": len(use_vals),
                "n_rejected": int(len(vals) - len(use_vals)),
            }

    return result


def print_report(data):
    """Print a summary report of all calibration runs."""
    runs = data["runs"]
    if not runs:
        print("No calibration data yet. Run some calibrations first!")
        return

    print("\n" + "=" * 70)
    print("CALIBRATION REPORT")
    print(f"Total runs: {len(runs)}")
    print("=" * 70)

    for i, run in enumerate(runs):
        print(f"\n--- Run {i+1}: {run['image']} ({run['timestamp']}) ---")
        print(f"  Camera offset: {run.get('camera_offset_m', 0):.2f} m")
        print(f"  Method: {run.get('method', 'unknown')}")
        for dim in ["length", "width", "height"]:
            if dim in run["errors"]:
                e = run["errors"][dim]
                direction = "over" if e["abs_error_ft"] > 0 else "under"
                print(f"  {dim.capitalize():8s}: estimated {e['estimated_ft']:.2f} ft, "
                      f"actual {e['actual_ft']:.2f} ft, "
                      f"error {abs(e['abs_error_inches']):.1f}\" {direction} "
                      f"({e['pct_error']:+.1f}%)")

    # Compute and display correction factors
    factors = compute_correction_factors(runs)
    if factors:
        print("\n" + "=" * 70)
        print("CORRECTION FACTORS (multiply estimate by factor to get actual)")
        print("=" * 70)
        for dim in ["length", "width", "height"]:
            if dim in factors:
                f = factors[dim]
                print(f"  {dim.capitalize():8s}: {f['factor']:.4f} "
                      f"(mean={f['mean']:.4f}, std={f['std']:.4f}, n={f['n_samples']})")

        # Compute residual errors after correction
        print("\n  --- Expected accuracy after correction ---")
        for dim in ["length", "width", "height"]:
            if dim in factors and factors[dim]['n_samples'] >= 2:
                f = factors[dim]
                # Residual error ~= std * typical_measurement
                typical_ft = np.mean([
                    run["errors"][dim]["actual_ft"]
                    for run in runs if dim in run["errors"]
                ])
                residual_inches = f['std'] * typical_ft * 12
                print(f"  {dim.capitalize():8s}: ~{residual_inches:.1f}\" residual error "
                      f"(based on {f['n_samples']} samples)")

        data["correction_factors"] = factors
        save_calibration_data(data)


def run_calibration(image_path, actual_length=None, actual_width=None,
                    actual_height=None, camera_offset=0.0, use_ransac=True,
                    subsample=4):
    """
    Run depth estimation on image and compare against known measurements.
    """
    model, transform, device = load_model()

    depth_map, focal_px, image = estimate_depth(model, transform, device, image_path)

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

    # Compute errors
    errors = {}
    length_key = "room_length_corrected_ft" if camera_offset > 0 else "room_length_raw_ft"

    if actual_length is not None:
        errors["length"] = compute_error(measurements[length_key], actual_length)
    if actual_width is not None:
        errors["width"] = compute_error(measurements["room_width_ft"], actual_width)
    if actual_height is not None:
        errors["height"] = compute_error(measurements["room_height_ft"], actual_height)

    # Print results
    print("\n" + "=" * 60)
    print("CALIBRATION RESULTS")
    print("=" * 60)

    for dim_name, dim_key in [("Length", "length"), ("Width", "width"), ("Height", "height")]:
        if dim_key in errors:
            e = errors[dim_key]
            direction = "over" if e["abs_error_ft"] > 0 else "under"
            print(f"  {dim_name}:")
            print(f"    Estimated:  {e['estimated_ft']:.2f} ft")
            print(f"    Actual:     {e['actual_ft']:.2f} ft")
            print(f"    Error:      {abs(e['abs_error_inches']):.1f} inches {direction} "
                  f"({e['pct_error']:+.1f}%)")

    # Save to calibration file
    cal_data = load_calibration_data()

    run_entry = {
        "image": str(Path(image_path).name),
        "timestamp": datetime.now().isoformat(),
        "camera_offset_m": camera_offset,
        "method": "ransac" if use_ransac else "legacy",
        "errors": errors,
        "raw_measurements": {
            k: v for k, v in measurements.items()
            if not k.startswith('_') and k != 'detected_planes'
        },
    }

    cal_data["runs"].append(run_entry)

    # Recompute correction factors
    cal_data["correction_factors"] = compute_correction_factors(cal_data["runs"])

    save_calibration_data(cal_data)

    # If we have enough data, show correction factors
    if len(cal_data["runs"]) >= 2 and cal_data["correction_factors"]:
        print("\n  --- Updated Correction Factors ---")
        for dim in ["length", "width", "height"]:
            if dim in cal_data["correction_factors"]:
                f = cal_data["correction_factors"][dim]
                print(f"  {dim.capitalize():8s}: multiply by {f['factor']:.4f} "
                      f"(based on {f['n_samples']} samples)")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="LayIt Calibration - Compare depth estimates against known measurements"
    )
    parser.add_argument("image", nargs="?", help="Image file to calibrate against")
    parser.add_argument("--length", type=float, help="Actual room length in feet")
    parser.add_argument("--width", type=float, help="Actual room width in feet")
    parser.add_argument("--height", type=float, help="Actual room height in feet")
    parser.add_argument("--camera-offset", type=float, default=0.0,
                        help="Distance from camera to wall behind user, in meters (default: 0.0)")
    parser.add_argument("--no-ransac", action="store_true",
                        help="Disable RANSAC, use legacy method")
    parser.add_argument("--subsample", type=int, default=4,
                        help="Point cloud subsample factor (default: 4)")
    parser.add_argument("--report", action="store_true",
                        help="Show calibration report from accumulated data")
    parser.add_argument("--reset", action="store_true",
                        help="Reset calibration data")

    args = parser.parse_args()

    if args.reset:
        if CALIBRATION_FILE.exists():
            os.remove(CALIBRATION_FILE)
            print("Calibration data reset.")
        else:
            print("No calibration data to reset.")
        return

    if args.report:
        data = load_calibration_data()
        print_report(data)
        return

    if not args.image:
        parser.print_help()
        print("\nError: Please provide an image path, or use --report to see calibration data.")
        sys.exit(1)

    if not os.path.isfile(args.image):
        print(f"Error: '{args.image}' is not a valid file.")
        sys.exit(1)

    if args.length is None and args.width is None and args.height is None:
        print("Error: Please provide at least one actual measurement (--length, --width, or --height)")
        sys.exit(1)

    run_calibration(
        args.image,
        actual_length=args.length,
        actual_width=args.width,
        actual_height=args.height,
        camera_offset=args.camera_offset,
        use_ransac=not args.no_ransac,
        subsample=args.subsample,
    )


if __name__ == "__main__":
    main()
