#!/usr/bin/env python3
"""
Pro tile shape tracer — ALL the irons in the fire.

Pipeline:
  1. SAM 2.1 segments the tile from reference image
  2. Potrace converts the bitmap mask to smooth SVG bezier curves
  3. svgpathtools parses the SVG into exact control points
  4. Output: Canvas2D code ready to paste into LayIt

Usage:
  # Use StageIt's venv for SAM support:
  /Users/Sims/Desktop/stageit/.venv/bin/python3 trace-tile-pro.py <image> --click x,y --name leaf

  # Without SAM (OpenCV fallback):
  python3.12 trace-tile-pro.py <image> --click x,y --name leaf
"""

import sys
import os
import json
import subprocess
import tempfile
import numpy as np

def main():
    import cv2

    args = parse_args()
    img = cv2.imread(args.image)
    if img is None:
        print(f"Error: Could not load {args.image}")
        return

    h, w = img.shape[:2]
    click = args.click or (w // 2, h // 2)
    print(f"Image: {w}x{h}, click: {click}")

    # ── Step 1: Get tile mask (SAM or OpenCV fallback) ──
    print("\n═══ STEP 1: Segment tile ═══")
    mask = get_tile_mask(img, click)
    if mask is None:
        print("Failed to get tile mask")
        return

    # Save mask visualization
    viz = img.copy()
    viz[~mask] = (viz[~mask] * 0.3).astype(np.uint8)
    cv2.imwrite(f'/Users/Sims/Desktop/{args.name}_step1_mask.png', viz)

    # ── Step 2: Potrace → smooth SVG beziers ──
    print("\n═══ STEP 2: Potrace → SVG ═══")
    svg_path = potrace_mask_to_svg(mask, args.name)
    if svg_path is None:
        print("Potrace failed, falling back to contour approximation")
        result = fallback_contour(mask)
    else:
        result = parse_svg_curves(svg_path)

    if result is None:
        print("Failed to extract curves")
        return

    # ── Step 3: Normalize and generate Canvas2D ──
    print("\n═══ STEP 3: Generate Canvas2D ═══")
    canvas = generate_canvas2d(result, args.name)

    print(f"\n{'═'*60}")
    print(f"CANVAS2D CODE — paste into drawSubTilePath:")
    print(f"{'═'*60}")
    print(canvas)

    # Save everything
    output = {
        'name': args.name,
        'curves': result,
        'canvas_code': canvas,
    }
    json_path = f'/Users/Sims/Desktop/{args.name}_pro.json'
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to {json_path}")


def get_tile_mask(img, click):
    """Get tile mask via SAM 2.1 or OpenCV fallback."""
    import cv2

    try:
        import torch
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        print("Using SAM 2.1...")
        sam = build_sam2(
            'configs/sam2.1/sam2.1_hiera_t.yaml',
            '/Users/Sims/Desktop/stageit/sam2.1_hiera_tiny.pt',
            device='cpu'
        )
        predictor = SAM2ImagePredictor(sam)
        predictor.set_image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        masks, scores, _ = predictor.predict(
            point_coords=np.array([[click[0], click[1]]]),
            point_labels=np.array([1]),
            multimask_output=True
        )
        best = np.argmax(scores)
        print(f"SAM confidence: {scores[best]:.3f}")
        return masks[best].astype(bool)

    except ImportError:
        print("SAM not available, using OpenCV threshold...")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Adaptive threshold
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 21, 5)
        # Find connected component at click point
        h, w = binary.shape
        flood_mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(binary, flood_mask, click, 255, 10, 10)
        result = flood_mask[1:-1, 1:-1]

        kernel = np.ones((3, 3), np.uint8)
        result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel, iterations=2)
        return result > 0


def potrace_mask_to_svg(mask, name):
    """Convert a binary mask to SVG using Potrace CLI."""
    import cv2

    # Save mask as PBM (Potrace's native format)
    mask_uint8 = (mask.astype(np.uint8)) * 255
    h, w = mask_uint8.shape

    pbm_path = f'/tmp/{name}_mask.pbm'
    svg_path = f'/Users/Sims/Desktop/{name}_potrace.svg'

    # Write PBM (P4 binary format)
    with open(pbm_path, 'wb') as f:
        f.write(f'P5\n{w} {h}\n255\n'.encode())
        f.write(mask_uint8.tobytes())

    # Invert: Potrace traces BLACK regions, so tile should be black on white
    mask_inverted = 255 - mask_uint8
    bmp_path = f'/tmp/{name}_mask.bmp'
    cv2.imwrite(bmp_path, mask_inverted)

    # Run Potrace: BMP → SVG with smooth bezier curves
    cmd = [
        'potrace', bmp_path,
        '-s',              # SVG output
        '-o', svg_path,
        '--turdsize', '5', # ignore small artifacts
        '--alphamax', '1.2',  # corner threshold (higher = smoother)
        '--opttolerance', '0.2',  # curve optimization tolerance
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"Potrace error: {result.stderr}")
            return None
        print(f"Potrace SVG: {svg_path}")
        return svg_path
    except Exception as e:
        print(f"Potrace failed: {e}")
        return None


def parse_svg_curves(svg_path):
    """Parse Potrace SVG output into normalized bezier curves."""
    try:
        from svgpathtools import svg2paths
    except ImportError:
        print("svgpathtools not available, parsing SVG manually")
        return parse_svg_manual(svg_path)

    paths, attributes = svg2paths(svg_path)

    if not paths:
        print("No paths found in SVG")
        return None

    # Pick the longest path (most likely the tile outline)
    longest = max(paths, key=lambda p: p.length())
    print(f"Path segments: {len(longest)}, length: {longest.length():.1f}")

    # Extract all curve segments
    curves = []
    for seg in longest:
        seg_type = type(seg).__name__
        if seg_type == 'CubicBezier':
            curves.append({
                'type': 'cubic',
                'p0': (seg.start.real, seg.start.imag),
                'cp1': (seg.control1.real, seg.control1.imag),
                'cp2': (seg.control2.real, seg.control2.imag),
                'p3': (seg.end.real, seg.end.imag),
            })
        elif seg_type == 'Line':
            curves.append({
                'type': 'line',
                'p0': (seg.start.real, seg.start.imag),
                'p3': (seg.end.real, seg.end.imag),
            })
        elif seg_type == 'QuadraticBezier':
            curves.append({
                'type': 'quadratic',
                'p0': (seg.start.real, seg.start.imag),
                'cp1': (seg.control.real, seg.control.imag),
                'p3': (seg.end.real, seg.end.imag),
            })

    print(f"Extracted {len(curves)} curve segments")

    # Normalize coordinates to centered -1..1
    all_points = []
    for c in curves:
        all_points.append(c['p0'])
        all_points.append(c['p3'])
        if 'cp1' in c:
            all_points.append(c['cp1'])
        if 'cp2' in c:
            all_points.append(c['cp2'])

    all_x = [p[0] for p in all_points]
    all_y = [p[1] for p in all_points]

    cx = (min(all_x) + max(all_x)) / 2
    cy = (min(all_y) + max(all_y)) / 2
    extent = max(max(all_x) - min(all_x), max(all_y) - min(all_y)) / 2

    bbox_w = (max(all_x) - min(all_x)) / extent
    bbox_h = (max(all_y) - min(all_y)) / extent

    print(f"Bbox: {bbox_w:.3f} x {bbox_h:.3f}, aspect 1:{bbox_h/bbox_w:.2f}")

    # Normalize
    for c in curves:
        c['p0'] = ((c['p0'][0] - cx) / extent, (c['p0'][1] - cy) / extent)
        c['p3'] = ((c['p3'][0] - cx) / extent, (c['p3'][1] - cy) / extent)
        if 'cp1' in c:
            c['cp1'] = ((c['cp1'][0] - cx) / extent, (c['cp1'][1] - cy) / extent)
        if 'cp2' in c:
            c['cp2'] = ((c['cp2'][0] - cx) / extent, (c['cp2'][1] - cy) / extent)

    return {
        'curves': curves,
        'bbox_w': bbox_w,
        'bbox_h': bbox_h,
        'num_segments': len(curves)
    }


def parse_svg_manual(svg_path):
    """Fallback: parse SVG path d attribute manually."""
    import re

    with open(svg_path) as f:
        svg = f.read()

    # Find path d attribute
    match = re.search(r'd="([^"]+)"', svg)
    if not match:
        print("No path found in SVG")
        return None

    d = match.group(1)
    print(f"SVG path: {d[:100]}...")

    # Parse SVG path commands
    # Potrace outputs: M (moveto), C (cubic bezier), z (close)
    commands = re.findall(r'([MCLZz])\s*([-\d.,\s]*)', d)

    curves = []
    current = (0, 0)

    for cmd, params in commands:
        nums = [float(x) for x in re.findall(r'-?[\d.]+', params)]

        if cmd == 'M' and len(nums) >= 2:
            current = (nums[0], nums[1])
        elif cmd == 'C':
            # Cubic bezier: cp1x,cp1y cp2x,cp2y endx,endy (can be chained)
            i = 0
            while i + 5 < len(nums):
                curves.append({
                    'type': 'cubic',
                    'p0': current,
                    'cp1': (nums[i], nums[i+1]),
                    'cp2': (nums[i+2], nums[i+3]),
                    'p3': (nums[i+4], nums[i+5]),
                })
                current = (nums[i+4], nums[i+5])
                i += 6
        elif cmd == 'L':
            i = 0
            while i + 1 < len(nums):
                curves.append({
                    'type': 'line',
                    'p0': current,
                    'p3': (nums[i], nums[i+1]),
                })
                current = (nums[i], nums[i+1])
                i += 2

    if not curves:
        print("No curves parsed from SVG")
        return None

    print(f"Parsed {len(curves)} segments from SVG")

    # Normalize
    all_points = []
    for c in curves:
        all_points.extend([c['p0'], c['p3']])
        if 'cp1' in c: all_points.append(c['cp1'])
        if 'cp2' in c: all_points.append(c['cp2'])

    all_x = [p[0] for p in all_points]
    all_y = [p[1] for p in all_points]
    cx = (min(all_x) + max(all_x)) / 2
    cy = (min(all_y) + max(all_y)) / 2
    extent = max(max(all_x) - min(all_x), max(all_y) - min(all_y)) / 2

    bbox_w = (max(all_x) - min(all_x)) / extent
    bbox_h = (max(all_y) - min(all_y)) / extent

    for c in curves:
        c['p0'] = (round((c['p0'][0] - cx) / extent, 4), round((c['p0'][1] - cy) / extent, 4))
        c['p3'] = (round((c['p3'][0] - cx) / extent, 4), round((c['p3'][1] - cy) / extent, 4))
        if 'cp1' in c:
            c['cp1'] = (round((c['cp1'][0] - cx) / extent, 4), round((c['cp1'][1] - cy) / extent, 4))
        if 'cp2' in c:
            c['cp2'] = (round((c['cp2'][0] - cx) / extent, 4), round((c['cp2'][1] - cy) / extent, 4))

    return {
        'curves': curves,
        'bbox_w': round(bbox_w, 4),
        'bbox_h': round(bbox_h, 4),
        'num_segments': len(curves)
    }


def fallback_contour(mask):
    """Fallback when Potrace isn't available — scipy spline fitting."""
    import cv2
    try:
        from scipy.interpolate import splprep, splev
    except ImportError:
        print("scipy not available for spline fitting")
        return None

    mask_uint8 = (mask.astype(np.uint8)) * 255
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    points = contour.reshape(-1, 2).astype(float)

    # Fit B-spline through all contour points
    # Subsample for performance (every 3rd point)
    step = max(1, len(points) // 100)
    pts = points[::step]

    tck, u = splprep([pts[:, 0], pts[:, 1]], s=len(pts) * 0.5, per=True)

    # Evaluate at evenly spaced points
    u_new = np.linspace(0, 1, 200)
    x_new, y_new = splev(u_new, tck)

    # Convert to cubic bezier segments (approximate: use every 4th point as control)
    curves = []
    step = 8  # points per bezier segment
    for i in range(0, len(x_new) - step, step):
        curves.append({
            'type': 'cubic',
            'p0': (x_new[i], y_new[i]),
            'cp1': (x_new[i + step//3], y_new[i + step//3]),
            'cp2': (x_new[i + 2*step//3], y_new[i + 2*step//3]),
            'p3': (x_new[i + step], y_new[i + step]),
        })

    # Normalize
    all_x = x_new
    all_y = y_new
    cx = (all_x.min() + all_x.max()) / 2
    cy = (all_y.min() + all_y.max()) / 2
    extent = max(all_x.max() - all_x.min(), all_y.max() - all_y.min()) / 2

    for c in curves:
        c['p0'] = (round((c['p0'][0] - cx) / extent, 4), round((c['p0'][1] - cy) / extent, 4))
        c['cp1'] = (round((c['cp1'][0] - cx) / extent, 4), round((c['cp1'][1] - cy) / extent, 4))
        c['cp2'] = (round((c['cp2'][0] - cx) / extent, 4), round((c['cp2'][1] - cy) / extent, 4))
        c['p3'] = (round((c['p3'][0] - cx) / extent, 4), round((c['p3'][1] - cy) / extent, 4))

    bbox_w = round((all_x.max() - all_x.min()) / extent, 4)
    bbox_h = round((all_y.max() - all_y.min()) / extent, 4)

    return {
        'curves': curves,
        'bbox_w': bbox_w,
        'bbox_h': bbox_h,
        'num_segments': len(curves)
    }


def generate_canvas2d(result, name):
    """Generate Canvas2D JavaScript from parsed curves."""
    curves = result['curves']
    bbox_w = result['bbox_w']
    bbox_h = result['bbox_h']

    lines = []
    lines.append(f"// {name} — traced via SAM + Potrace ({len(curves)} segments)")
    lines.append(f"// Aspect ratio: {bbox_w:.3f} x {bbox_h:.3f} (1:{bbox_h/bbox_w:.2f})")
    lines.append(f"var hw = (stWpx - stGrPx) / 2;")
    lines.append(f"var hh = (stHpx - stGrPx) / 2;")

    if not curves:
        lines.append("// ERROR: No curves extracted")
        return '\n'.join(lines)

    # First point: moveTo
    p0 = curves[0]['p0']
    lines.append(f"cx.moveTo(px + hw * {p0[0]:.4f}, py + hh * {p0[1]:.4f});")

    for c in curves:
        if c['type'] == 'cubic':
            lines.append(
                f"cx.bezierCurveTo("
                f"px + hw * {c['cp1'][0]:.4f}, py + hh * {c['cp1'][1]:.4f}, "
                f"px + hw * {c['cp2'][0]:.4f}, py + hh * {c['cp2'][1]:.4f}, "
                f"px + hw * {c['p3'][0]:.4f}, py + hh * {c['p3'][1]:.4f});"
            )
        elif c['type'] == 'quadratic':
            lines.append(
                f"cx.quadraticCurveTo("
                f"px + hw * {c['cp1'][0]:.4f}, py + hh * {c['cp1'][1]:.4f}, "
                f"px + hw * {c['p3'][0]:.4f}, py + hh * {c['p3'][1]:.4f});"
            )
        elif c['type'] == 'line':
            lines.append(
                f"cx.lineTo(px + hw * {c['p3'][0]:.4f}, py + hh * {c['p3'][1]:.4f});"
            )

    lines.append("cx.closePath();")
    return '\n'.join(lines)


def parse_args():
    class Args:
        image = sys.argv[1] if len(sys.argv) > 1 else None
        click = None
        name = 'tile'

    args = Args()
    if not args.image:
        print("Usage: python3 trace-tile-pro.py <image> --click x,y --name tile_name")
        sys.exit(1)

    for i, a in enumerate(sys.argv):
        if a == '--click' and i + 1 < len(sys.argv):
            parts = sys.argv[i+1].split(',')
            args.click = (int(parts[0]), int(parts[1]))
        if a == '--name' and i + 1 < len(sys.argv):
            args.name = sys.argv[i+1]

    return args


if __name__ == '__main__':
    main()
