#!/usr/bin/env python3
"""
Trace a tile shape from a reference image using computer vision.
Extracts the outline contour and converts to Canvas2D bezier curves.

Usage: python3 trace-tile.py <image_path> [--threshold 127] [--simplify 0.02]
"""

import cv2
import numpy as np
import sys
import json

def trace_tile(image_path, threshold=127, simplify_epsilon=0.015):
    """Extract the outline of a single tile from a reference image."""

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return None

    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection (Canny)
    edges = cv2.Canny(blurred, 50, 150)

    # Also try threshold-based approach for cleaner tiles
    _, binary = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY_INV)

    # Morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours from both methods
    contours_edge, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_thresh, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Pick the best contour (largest area, most likely the tile)
    all_contours = list(contours_edge) + list(contours_thresh)
    if not all_contours:
        print("No contours found!")
        return None

    # Sort by area, pick largest
    all_contours.sort(key=cv2.contourArea, reverse=True)

    # Find a contour that's a reasonable tile size (10-80% of image area)
    img_area = w * h
    best_contour = None
    for c in all_contours:
        area = cv2.contourArea(c)
        ratio = area / img_area
        if 0.05 < ratio < 0.85:
            best_contour = c
            print(f"Selected contour: area={area:.0f} ({ratio*100:.1f}% of image)")
            break

    if best_contour is None:
        # Fall back to largest
        best_contour = all_contours[0]
        area = cv2.contourArea(best_contour)
        print(f"Fallback to largest contour: area={area:.0f}")

    # Simplify the contour (reduce points while preserving shape)
    perimeter = cv2.arcLength(best_contour, True)
    epsilon = simplify_epsilon * perimeter
    simplified = cv2.approxPolyDP(best_contour, epsilon, True)

    print(f"Contour points: {len(best_contour)} → simplified to {len(simplified)}")

    # Normalize coordinates to -1..1 range (centered)
    points = simplified.reshape(-1, 2).astype(float)

    # Center the contour
    cx = (points[:, 0].min() + points[:, 0].max()) / 2
    cy = (points[:, 1].min() + points[:, 1].max()) / 2
    points[:, 0] -= cx
    points[:, 1] -= cy

    # Scale to -1..1 based on the larger dimension
    max_extent = max(points[:, 0].max() - points[:, 0].min(),
                     points[:, 1].max() - points[:, 1].min()) / 2
    points /= max_extent

    # Get bounding box in normalized coords
    bbox_w = (points[:, 0].max() - points[:, 0].min())
    bbox_h = (points[:, 1].max() - points[:, 1].min())
    print(f"Normalized bbox: {bbox_w:.3f} x {bbox_h:.3f}")
    print(f"Aspect ratio: 1:{bbox_h/bbox_w:.2f}")

    # Output as normalized vertices
    vertices = []
    for pt in points:
        vertices.append({
            'x': round(float(pt[0]), 4),
            'y': round(float(pt[1]), 4)
        })

    # Also fit bezier curves
    beziers = fit_bezier_to_contour(points)

    # Generate Canvas2D code
    canvas_code = generate_canvas_code(vertices, beziers, bbox_w, bbox_h)

    return {
        'vertices': vertices,
        'beziers': beziers,
        'canvas_code': canvas_code,
        'bbox_w': bbox_w,
        'bbox_h': bbox_h,
        'num_points': len(vertices)
    }


def fit_bezier_to_contour(points):
    """Fit cubic bezier curves to the contour segments."""
    n = len(points)
    beziers = []

    for i in range(n):
        p0 = points[i]
        p3 = points[(i + 1) % n]

        # Simple cubic bezier: control points at 1/3 and 2/3 along the segment
        # with slight offset toward the contour's curvature
        p1 = p0 + (p3 - p0) * 0.33
        p2 = p0 + (p3 - p0) * 0.67

        beziers.append({
            'p0': {'x': round(float(p0[0]), 4), 'y': round(float(p0[1]), 4)},
            'cp1': {'x': round(float(p1[0]), 4), 'y': round(float(p1[1]), 4)},
            'cp2': {'x': round(float(p2[0]), 4), 'y': round(float(p2[1]), 4)},
            'p3': {'x': round(float(p3[0]), 4), 'y': round(float(p3[1]), 4)},
        })

    return beziers


def generate_canvas_code(vertices, beziers, bbox_w, bbox_h):
    """Generate Canvas2D JavaScript code for rendering the shape."""
    lines = []
    lines.append(f"// Traced from reference image — {len(vertices)} vertices")
    lines.append(f"// Aspect ratio: {bbox_w:.3f} x {bbox_h:.3f}")
    lines.append(f"var hw = (stWpx - stGrPx) / 2;")
    lines.append(f"var hh = (stHpx - stGrPx) / 2;")

    # Scale factors (vertices are normalized to -1..1 on the larger axis)
    if bbox_h >= bbox_w:
        lines.append(f"var sx = hw * {bbox_w/bbox_h:.4f};  // scale x for aspect ratio")
        lines.append(f"var sy = hh;")
    else:
        lines.append(f"var sx = hw;")
        lines.append(f"var sy = hh * {bbox_h/bbox_w:.4f};  // scale y for aspect ratio")

    # MoveTo first point
    v0 = vertices[0]
    lines.append(f"cx.moveTo(px + sx * {v0['x']}, py + sy * {v0['y']});")

    # LineTo remaining points
    for v in vertices[1:]:
        lines.append(f"cx.lineTo(px + sx * {v['x']}, py + sy * {v['y']});")

    lines.append("cx.closePath();")

    return '\n'.join(lines)


def visualize_contour(image_path, contour, output_path):
    """Save a visualization of the detected contour."""
    img = cv2.imread(image_path)
    cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)
    cv2.imwrite(output_path, img)
    print(f"Visualization saved to {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 trace-tile.py <image_path> [--threshold 127] [--simplify 0.02]")
        sys.exit(1)

    image_path = sys.argv[1]
    threshold = 127
    simplify = 0.015

    for i, arg in enumerate(sys.argv):
        if arg == '--threshold' and i + 1 < len(sys.argv):
            threshold = int(sys.argv[i + 1])
        if arg == '--simplify' and i + 1 < len(sys.argv):
            simplify = float(sys.argv[i + 1])

    result = trace_tile(image_path, threshold, simplify)

    if result:
        print(f"\n{'='*60}")
        print(f"TRACED SHAPE: {result['num_points']} vertices")
        print(f"{'='*60}")
        print(f"\nVertices (normalized -1..1):")
        for i, v in enumerate(result['vertices']):
            print(f"  [{i}] ({v['x']:7.4f}, {v['y']:7.4f})")

        print(f"\n{'='*60}")
        print(f"CANVAS2D CODE:")
        print(f"{'='*60}")
        print(result['canvas_code'])

        # Save JSON
        json_path = image_path.rsplit('.', 1)[0] + '_traced.json'
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull data saved to {json_path}")
