#!/usr/bin/env python3
"""
SAM-based tile shape tracer.
Uses SAM 2.1 to segment a single tile from a reference image,
then extracts the contour and converts to Canvas2D bezier curves.

Usage:
  python3 sam-trace-tile.py <image_path> [--click x,y] [--output tile_name]

If --click is not provided, uses center of image as the prompt point.
"""

import sys
import os
import json
import numpy as np

# Add StageIt's path for SAM
sys.path.insert(0, '/Users/Sims/Desktop/stageit')

def trace_with_sam(image_path, click_point=None, output_name='tile'):
    """Use SAM to segment one tile, then extract its contour."""

    import cv2

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return None

    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    # Default click point: center of image
    if click_point is None:
        click_point = (w // 2, h // 2)

    print(f"Click point: {click_point}")

    try:
        import torch
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        sam_checkpoint = '/Users/Sims/Desktop/stageit/sam2.1_hiera_tiny.pt'
        sam_config = 'configs/sam2.1/sam2.1_hiera_t.yaml'

        print("Loading SAM 2.1...")
        device = 'cpu'
        sam = build_sam2(sam_config, sam_checkpoint, device=device)
        predictor = SAM2ImagePredictor(sam)

        # Convert BGR to RGB for SAM
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        predictor.set_image(img_rgb)

        # Predict mask at click point
        input_point = np.array([[click_point[0], click_point[1]]])
        input_label = np.array([1])  # foreground

        masks, scores, logits = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True
        )

        # Pick the best mask
        best_idx = np.argmax(scores)
        mask = masks[best_idx]
        print(f"Best mask score: {scores[best_idx]:.3f}")
        print(f"Mask shape: {mask.shape}, coverage: {mask.sum()/(h*w)*100:.1f}%")

    except ImportError as e:
        print(f"SAM not available ({e}), falling back to OpenCV threshold")
        mask = fallback_threshold(img, click_point)

    if mask is None:
        return None

    # Extract contour from mask
    mask_uint8 = (mask * 255).astype(np.uint8)
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("No contours found in mask!")
        return None

    # Pick largest contour
    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)
    print(f"Contour area: {area:.0f} px²")

    # Simplify contour
    perimeter = cv2.arcLength(contour, True)
    epsilon = 0.008 * perimeter  # tight simplification to preserve curves
    simplified = cv2.approxPolyDP(contour, epsilon, True)
    print(f"Contour points: {len(contour)} → simplified to {len(simplified)}")

    # Normalize to -1..1
    points = simplified.reshape(-1, 2).astype(float)
    cx = (points[:, 0].min() + points[:, 0].max()) / 2
    cy = (points[:, 1].min() + points[:, 1].max()) / 2
    points[:, 0] -= cx
    points[:, 1] -= cy

    extent_x = (points[:, 0].max() - points[:, 0].min()) / 2
    extent_y = (points[:, 1].max() - points[:, 1].min()) / 2

    # Normalize so max dimension = 1
    max_extent = max(extent_x, extent_y)
    points /= max_extent

    bbox_w = points[:, 0].max() - points[:, 0].min()
    bbox_h = points[:, 1].max() - points[:, 1].min()
    print(f"Normalized bbox: {bbox_w:.3f} x {bbox_h:.3f}")

    # Fit smooth bezier curves through the points
    canvas_code = generate_smooth_canvas(points, bbox_w, bbox_h)

    # Save visualization
    viz = img.copy()
    cv2.drawContours(viz, [simplified], -1, (0, 255, 0), 2)
    cv2.circle(viz, click_point, 5, (0, 0, 255), -1)
    viz_path = f'/Users/Sims/Desktop/{output_name}_traced.png'
    cv2.imwrite(viz_path, viz)
    print(f"Visualization: {viz_path}")

    # Save mask
    mask_bool = mask.astype(bool)
    mask_viz = np.zeros_like(img)
    mask_viz[mask_bool] = img[mask_bool]
    mask_path = f'/Users/Sims/Desktop/{output_name}_mask.png'
    cv2.imwrite(mask_path, mask_viz)
    print(f"Mask: {mask_path}")

    return {
        'vertices': [{'x': round(float(p[0]), 4), 'y': round(float(p[1]), 4)} for p in points],
        'bbox_w': round(bbox_w, 4),
        'bbox_h': round(bbox_h, 4),
        'canvas_code': canvas_code,
        'num_points': len(points)
    }


def fallback_threshold(img, click_point):
    """OpenCV-based fallback when SAM isn't available."""
    import cv2

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Adaptive threshold
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 21, 5)

    # Flood fill from click point to find the tile
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(binary, mask, click_point, 255, 10, 10)

    # Extract the flood-filled region
    result = mask[1:-1, 1:-1]

    # Morphological cleanup
    kernel = np.ones((3, 3), np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel, iterations=2)

    return result > 0


def generate_smooth_canvas(points, bbox_w, bbox_h):
    """Generate Canvas2D code with smooth bezier curves through the traced points."""
    n = len(points)
    lines = []
    lines.append(f"// SAM-traced tile — {n} control points")
    lines.append(f"// Bbox: {bbox_w:.3f} x {bbox_h:.3f}, aspect 1:{bbox_h/bbox_w:.2f}")
    lines.append(f"var hw = (stWpx - stGrPx) / 2;")
    lines.append(f"var hh = (stHpx - stGrPx) / 2;")

    # For the smooth curve, use quadratic bezier segments through the vertices
    # Each segment uses the vertex as a control point, with the midpoint between
    # consecutive vertices as the on-curve point

    # First point: move to midpoint between first and last vertex
    mid_x = (points[0][0] + points[-1][0]) / 2
    mid_y = (points[0][1] + points[-1][1]) / 2
    lines.append(f"cx.moveTo(px + hw * {mid_x:.4f}, py + hh * {mid_y:.4f});")

    # Quadratic bezier through each vertex
    for i in range(n):
        cp = points[i]
        next_pt = points[(i + 1) % n]
        mid_x = (cp[0] + next_pt[0]) / 2
        mid_y = (cp[1] + next_pt[1]) / 2
        lines.append(f"cx.quadraticCurveTo(px + hw * {cp[0]:.4f}, py + hh * {cp[1]:.4f}, px + hw * {mid_x:.4f}, py + hh * {mid_y:.4f});")

    lines.append("cx.closePath();")
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 sam-trace-tile.py <image_path> [--click x,y] [--output name]")
        print("  --click x,y  : pixel coordinates to click on a tile (default: center)")
        print("  --output name : output file prefix (default: 'tile')")
        sys.exit(1)

    image_path = sys.argv[1]
    click = None
    output = 'tile'

    for i, arg in enumerate(sys.argv):
        if arg == '--click' and i + 1 < len(sys.argv):
            parts = sys.argv[i + 1].split(',')
            click = (int(parts[0]), int(parts[1]))
        if arg == '--output' and i + 1 < len(sys.argv):
            output = sys.argv[i + 1]

    result = trace_with_sam(image_path, click, output)

    if result:
        print(f"\n{'='*60}")
        print(f"CANVAS2D CODE (paste into drawSubTilePath):")
        print(f"{'='*60}")
        print(result['canvas_code'])

        # Save JSON
        json_path = f'/Users/Sims/Desktop/{output}_geometry.json'
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull geometry saved to {json_path}")
