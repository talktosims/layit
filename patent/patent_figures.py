#!/usr/bin/env python3
"""
Generate patent figures for LayIt Camera Scan Provisional Patent.
Produces clean black-and-white diagrams suitable for USPTO filing.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def fig1_system_architecture():
    """FIG. 1 - System Architecture Block Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(11, 8.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    ax.set_aspect('equal')

    # Title
    ax.text(5.5, 8.1, 'FIG. 1 — System Architecture', fontsize=14,
            ha='center', fontweight='bold', family='serif')

    # --- Mobile Device (left) ---
    mobile = FancyBboxPatch((0.5, 1.5), 3.5, 5.5, boxstyle="round,pad=0.15",
                             facecolor='white', edgecolor='black', linewidth=2)
    ax.add_patch(mobile)
    ax.text(2.25, 6.6, 'MOBILE DEVICE', fontsize=10, ha='center',
            fontweight='bold', family='serif')
    ax.text(2.25, 6.3, '(Smartphone/Tablet)', fontsize=8, ha='center',
            style='italic', family='serif')

    # Sub-blocks inside mobile
    blocks_mobile = [
        (0.8, 5.3, 2.9, 0.7, 'RGB Camera'),
        (0.8, 4.3, 2.9, 0.7, 'Depth Estimation\nNeural Network'),
        (0.8, 3.3, 2.9, 0.7, 'Geometric Processing\n(RANSAC Plane Fitting)'),
        (0.8, 2.3, 2.9, 0.7, 'Feature Detection\n(Niches, Windows)'),
        (0.8, 1.3, 2.9, 0.7, 'Tile Layout Engine'),
    ]
    # Adjust y positions to fit inside the box
    blocks_mobile = [
        (0.8, 5.5, 2.9, 0.6, 'RGB Camera'),
        (0.8, 4.6, 2.9, 0.6, 'Depth Estimation\nNeural Network'),
        (0.8, 3.7, 2.9, 0.6, 'Geometric Processing\n(RANSAC Plane Fitting)'),
        (0.8, 2.8, 2.9, 0.6, 'Feature Detection\n(Niches, Windows)'),
        (0.8, 1.9, 2.9, 0.6, 'Tile Layout Engine'),
    ]

    for x, y, w, h, label in blocks_mobile:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                              facecolor='#f0f0f0', edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, fontsize=7.5, ha='center', va='center',
                family='serif')

    # Arrows between mobile blocks
    for i in range(len(blocks_mobile) - 1):
        x1 = blocks_mobile[i][0] + blocks_mobile[i][2] / 2
        y1 = blocks_mobile[i][1]
        y2 = blocks_mobile[i+1][1] + blocks_mobile[i+1][3]
        ax.annotate('', xy=(x1, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # --- Laser Projection Device (right) ---
    laser = FancyBboxPatch((7, 3), 3.5, 4, boxstyle="round,pad=0.15",
                            facecolor='white', edgecolor='black', linewidth=2)
    ax.add_patch(laser)
    ax.text(8.75, 6.6, 'LASER PROJECTION', fontsize=10, ha='center',
            fontweight='bold', family='serif')
    ax.text(8.75, 6.3, 'DEVICE', fontsize=10, ha='center',
            fontweight='bold', family='serif')

    blocks_laser = [
        (7.3, 5.5, 2.9, 0.5, 'WiFi/WebSocket\nReceiver'),
        (7.3, 4.7, 2.9, 0.5, 'Microcontroller\n+ DAC'),
        (7.3, 3.9, 2.9, 0.5, 'Galvanometer\nMirror System'),
        (7.3, 3.2, 2.9, 0.5, 'Vision-Based\nAlignment Camera'),
    ]

    for x, y, w, h, label in blocks_laser:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                              facecolor='#f0f0f0', edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, fontsize=7.5, ha='center', va='center',
                family='serif')

    # --- Cloud Service (top right) ---
    cloud = FancyBboxPatch((7, 0.5), 3.5, 2, boxstyle="round,pad=0.15",
                            facecolor='white', edgecolor='black', linewidth=2)
    ax.add_patch(cloud)
    ax.text(8.75, 2.1, 'CLOUD SERVICE', fontsize=10, ha='center',
            fontweight='bold', family='serif')
    ax.text(8.75, 1.5, 'Calibration Data\nAggregation', fontsize=8,
            ha='center', family='serif')
    ax.text(8.75, 0.9, 'Camera-Model-Specific\nCorrection Factors', fontsize=7,
            ha='center', style='italic', family='serif')

    # --- Connection Arrows ---
    # Mobile to Laser (WiFi)
    ax.annotate('', xy=(7, 5.2), xytext=(4, 2.2),
                arrowprops=dict(arrowstyle='->', lw=2, color='black',
                                connectionstyle='arc3,rad=-0.2'))
    ax.text(5.5, 4.2, 'WiFi\n(Layout Data)', fontsize=8, ha='center',
            family='serif', style='italic')

    # Mobile to Cloud
    ax.annotate('', xy=(7, 1.5), xytext=(4, 2.0),
                arrowprops=dict(arrowstyle='<->', lw=2, color='black',
                                connectionstyle='arc3,rad=0.2'))
    ax.text(5.5, 1.2, 'Calibration\nSync', fontsize=8, ha='center',
            family='serif', style='italic')

    # Work surface
    ax.add_patch(FancyBboxPatch((4.5, 0.3), 2, 1, boxstyle="round,pad=0.08",
                                 facecolor='#e8e8e8', edgecolor='black', linewidth=1.5,
                                 linestyle='--'))
    ax.text(5.5, 0.8, 'WORK SURFACE', fontsize=9, ha='center',
            fontweight='bold', family='serif')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'patent_fig1_architecture.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def fig2_pipeline_flowchart():
    """FIG. 2 - Camera Scan Pipeline Flowchart"""
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 11)
    ax.axis('off')
    ax.set_aspect('equal')

    ax.text(4.25, 10.7, 'FIG. 2 — Camera Scan Processing Pipeline', fontsize=13,
            ha='center', fontweight='bold', family='serif')

    # Flow steps
    steps = [
        ('User captures\nwall photograph(s)', '#e8e8e8', 'rounded'),
        ('Monocular Depth\nEstimation (Neural Network)', '#f0f0f0', 'process'),
        ('Metric Depth Map\n(distance per pixel)', '#ffffff', 'data'),
        ('3D Point Cloud via\nPinhole Camera Model', '#f0f0f0', 'process'),
        ('RANSAC Plane Detection\n(walls, floor, ceiling)', '#f0f0f0', 'process'),
        ('Dimension Extraction\n(width, height, out-of-square)', '#f0f0f0', 'process'),
        ('Feature Detection\n(niches, windows, shelves)', '#f0f0f0', 'process'),
        ('Tile Layout Generation\nwith Fixed Constraints', '#f0f0f0', 'process'),
        ('Output: Layout JSON\n+ Laser Projection Data', '#e8e8e8', 'rounded'),
    ]

    y_start = 10.0
    y_spacing = 1.05
    box_w = 4.5
    box_h = 0.7
    center_x = 4.25

    for i, (label, color, style) in enumerate(steps):
        y = y_start - i * y_spacing
        x = center_x - box_w / 2

        if style == 'rounded':
            box = FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.12",
                                  facecolor=color, edgecolor='black', linewidth=1.5)
        elif style == 'data':
            # Parallelogram-ish — use skewed rect
            box = FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.05",
                                  facecolor=color, edgecolor='black', linewidth=1.5,
                                  linestyle='--')
        else:
            box = FancyBboxPatch((x, y), box_w, box_h, boxstyle="square,pad=0.05",
                                  facecolor=color, edgecolor='black', linewidth=1.5)

        ax.add_patch(box)
        ax.text(center_x, y + box_h / 2, label, fontsize=9, ha='center', va='center',
                family='serif')

        # Arrow to next step
        if i < len(steps) - 1:
            ax.annotate('', xy=(center_x, y), xytext=(center_x, y + 0.0),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
            # Position arrow between boxes
            arrow_y_start = y
            arrow_y_end = y_start - (i + 1) * y_spacing + box_h
            ax.annotate('', xy=(center_x, arrow_y_end),
                        xytext=(center_x, arrow_y_start),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # Side annotation: Multi-photo fusion
    ax.annotate('Multi-Photo\nFusion\n(confidence-\nweighted)', xy=(center_x + box_w/2, y_start - 4*y_spacing + box_h/2),
                xytext=(center_x + box_w/2 + 1.3, y_start - 4*y_spacing + box_h/2),
                fontsize=7.5, ha='left', va='center', family='serif', style='italic',
                arrowprops=dict(arrowstyle='->', lw=1, color='gray'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray'))

    # Side annotation: Closeup mode
    ax.annotate('Closeup Mode\nAuto-Detection', xy=(center_x - box_w/2, y_start - 6*y_spacing + box_h/2),
                xytext=(center_x - box_w/2 - 1.8, y_start - 6*y_spacing + box_h/2),
                fontsize=7.5, ha='right', va='center', family='serif', style='italic',
                arrowprops=dict(arrowstyle='->', lw=1, color='gray'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray'))

    # Side annotation: Calibration
    ax.annotate('Calibration\nCorrection\nFactors', xy=(center_x + box_w/2, y_start - 5*y_spacing + box_h/2),
                xytext=(center_x + box_w/2 + 1.3, y_start - 5.5*y_spacing + box_h/2),
                fontsize=7.5, ha='left', va='center', family='serif', style='italic',
                arrowprops=dict(arrowstyle='->', lw=1, color='gray'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray'))

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'patent_fig2_pipeline.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def fig3_feature_detection():
    """FIG. 3 - Feature Detection Concept Diagram"""
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))

    for ax in axes:
        ax.set_aspect('equal')

    # Panel A: Wall with niche (cross-section view)
    ax = axes[0]
    ax.set_xlim(-1, 7)
    ax.set_ylim(-0.5, 6)
    ax.set_title('(a) Wall Cross-Section\n(Top-Down View)', fontsize=9, family='serif')

    # Wall surface
    ax.plot([0, 6], [3, 3], 'k-', linewidth=3)
    ax.text(3, 3.3, 'Wall Surface (Dominant Plane)', fontsize=7, ha='center', family='serif')

    # Niche (recessed)
    ax.plot([2, 2], [3, 4.5], 'k-', linewidth=2)
    ax.plot([2, 4], [4.5, 4.5], 'k-', linewidth=2)
    ax.plot([4, 4], [4.5, 3], 'k-', linewidth=2)
    ax.fill([2, 2, 4, 4], [3, 4.5, 4.5, 3], color='#d0d0d0', alpha=0.5)
    ax.text(3, 3.9, 'Niche\n(Recessed)', fontsize=7, ha='center', family='serif')

    # Camera
    ax.annotate('', xy=(3, 3), xytext=(3, 0.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', linestyle='--'))
    ax.text(3, 0.2, 'Camera', fontsize=8, ha='center', family='serif', fontweight='bold')

    # Depth labels
    ax.annotate('', xy=(5.5, 3), xytext=(5.5, 0.5),
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(6.2, 1.75, 'Wall\nDepth', fontsize=7, ha='center', family='serif')

    ax.annotate('', xy=(1.3, 4.5), xytext=(1.3, 0.5),
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(0.3, 2.5, 'Niche\nDepth', fontsize=7, ha='center', family='serif')

    ax.axis('off')

    # Panel B: Depth map representation
    ax = axes[1]
    # Create synthetic depth map
    depth = np.ones((100, 100)) * 0.6
    depth[25:55, 35:65] = 0.8  # niche (deeper = higher value)
    # Simple blur without scipy
    kernel_size = 7
    kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
    from numpy.lib.stride_tricks import as_strided
    padded = np.pad(depth, kernel_size//2, mode='edge')
    # Manual convolution
    blurred = np.zeros_like(depth)
    for i in range(depth.shape[0]):
        for j in range(depth.shape[1]):
            blurred[i, j] = np.mean(padded[i:i+kernel_size, j:j+kernel_size])
    depth = blurred

    ax.imshow(depth, cmap='turbo', aspect='equal')
    ax.set_title('(b) Depth Map\n(warmer = deeper)', fontsize=9, family='serif')

    # Niche bounding box
    rect = plt.Rectangle((33, 23), 34, 34, linewidth=2, edgecolor='red',
                           facecolor='none', linestyle='--')
    ax.add_patch(rect)
    ax.text(50, 18, 'Detected Feature', fontsize=7, ha='center', color='red',
            family='serif', fontweight='bold')
    ax.axis('off')

    # Panel C: Output to tile engine
    ax = axes[2]
    ax.set_xlim(0, 58)
    ax.set_ylim(0, 70)
    ax.set_title('(c) Layout Output\n(wall + void)', fontsize=9, family='serif')

    # Wall outline
    wall = plt.Rectangle((0, 0), 58, 70, linewidth=2, edgecolor='black',
                           facecolor='#f8f8f8')
    ax.add_patch(wall)

    # Niche void
    niche = plt.Rectangle((22, 30), 14, 12, linewidth=2, edgecolor='red',
                            facecolor='#ffcccc', linestyle='-')
    ax.add_patch(niche)
    ax.text(29, 36, 'Niche\n(Void)', fontsize=7, ha='center', family='serif',
            color='red', fontweight='bold')

    # Dimension labels
    ax.annotate('', xy=(0, -3), xytext=(58, -3),
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(29, -6, '58"', fontsize=8, ha='center', family='serif')

    ax.annotate('', xy=(-3, 0), xytext=(-3, 70),
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(-7, 35, '70"', fontsize=8, ha='center', family='serif', rotation=90)

    # Niche position labels
    ax.annotate('', xy=(22, 27), xytext=(0, 27),
                arrowprops=dict(arrowstyle='<->', lw=0.8, color='gray'))
    ax.text(11, 25, 'x: 22"', fontsize=6, ha='center', family='serif', color='gray')

    ax.set_xlim(-10, 62)
    ax.set_ylim(-10, 75)
    ax.axis('off')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'patent_fig3_features.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def fig4_constraint_autocorrect():
    """FIG. 4 - Constraint-Aware Auto-Correction Flowchart"""
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 7))
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_aspect('equal')

    ax.text(4.25, 6.7, 'FIG. 4 — Constraint-Aware Auto-Correction', fontsize=13,
            ha='center', fontweight='bold', family='serif')

    cx = 4.25
    bw, bh = 3.5, 0.55

    # Step 1: Tile placed
    y = 6.0
    box = FancyBboxPatch((cx - bw/2, y), bw, bh, boxstyle="round,pad=0.1",
                          facecolor='#e8e8e8', edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(cx, y + bh/2, 'Tile placed — offset detected', fontsize=9,
            ha='center', va='center', family='serif')

    # Arrow
    y_next = 5.1
    ax.annotate('', xy=(cx, y_next + bh), xytext=(cx, y),
                arrowprops=dict(arrowstyle='->', lw=1.5))

    # Step 2: Compute shift
    y = y_next
    box = FancyBboxPatch((cx - bw/2, y), bw, bh, boxstyle="square,pad=0.05",
                          facecolor='#f0f0f0', edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(cx, y + bh/2, 'Compute proposed pattern shift', fontsize=9,
            ha='center', va='center', family='serif')

    # Arrow
    y_next = 4.1
    ax.annotate('', xy=(cx, y_next + bh), xytext=(cx, y),
                arrowprops=dict(arrowstyle='->', lw=1.5))

    # Step 3: Diamond - fixed constraints?
    y = y_next
    diamond_size = 0.6
    diamond = plt.Polygon([
        (cx, y + bh + 0.1),
        (cx + 1.5, y + bh/2),
        (cx, y - 0.1),
        (cx - 1.5, y + bh/2)
    ], facecolor='#ffffff', edgecolor='black', linewidth=1.5)
    ax.add_patch(diamond)
    ax.text(cx, y + bh/2, 'Fixed constraints\naffected?', fontsize=8,
            ha='center', va='center', family='serif')

    # NO branch (left) → Auto-correct
    y_left = 2.8
    ax.annotate('', xy=(1.5, y_left + bh), xytext=(cx - 1.5, y + bh/2),
                arrowprops=dict(arrowstyle='->', lw=1.5))
    ax.text(cx - 2.2, y + 0.1, 'NO', fontsize=8, fontweight='bold', family='serif')

    box = FancyBboxPatch((0.2, y_left), 2.6, bh, boxstyle="round,pad=0.1",
                          facecolor='#d4edda', edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(1.5, y_left + bh/2, 'SAFE\nAuto-correct pattern', fontsize=8,
            ha='center', va='center', family='serif')

    # YES branch (right) → Warning
    y_right = 2.8
    ax.annotate('', xy=(7, y_right + bh), xytext=(cx + 1.5, y + bh/2),
                arrowprops=dict(arrowstyle='->', lw=1.5))
    ax.text(cx + 1.8, y + 0.1, 'YES', fontsize=8, fontweight='bold', family='serif')

    box = FancyBboxPatch((5.7, y_right), 2.6, bh, boxstyle="round,pad=0.1",
                          facecolor='#fff3cd', edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(7, y_right + bh/2, 'WARNING\nAlert user', fontsize=8,
            ha='center', va='center', family='serif')

    # Three options from WARNING
    options_y = 1.6
    opts = [
        (5.0, 'Reposition\ntile'),
        (7.0, 'Keep tile,\naccept offset'),
        (8.8, 'Adjust\nmeasurement'),
    ]

    for ox, label in opts:
        ax.annotate('', xy=(ox, options_y + 0.4), xytext=(7, y_right),
                    arrowprops=dict(arrowstyle='->', lw=1, color='gray'))
        box = FancyBboxPatch((ox - 0.8, options_y - 0.1), 1.6, 0.5,
                              boxstyle="round,pad=0.08",
                              facecolor='#f0f0f0', edgecolor='gray', linewidth=1)
        ax.add_patch(box)
        ax.text(ox, options_y + 0.15, label, fontsize=7, ha='center', va='center',
                family='serif')

    # No constraints branch (center)
    y_center = 2.8
    ax.annotate('', xy=(cx, y_center + bh), xytext=(cx, y + bh/2 - 0.35),
                arrowprops=dict(arrowstyle='->', lw=1.5))
    ax.text(cx + 0.1, y - 0.25, 'NONE', fontsize=8, fontweight='bold',
            family='serif', ha='center')

    box = FancyBboxPatch((cx - 1.3, y_center), 2.6, bh, boxstyle="round,pad=0.1",
                          facecolor='#d4edda', edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(cx, y_center + bh/2, 'NO CONSTRAINTS\nFreely auto-correct', fontsize=8,
            ha='center', va='center', family='serif')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'patent_fig4_autocorrect.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


if __name__ == "__main__":
    print("Generating patent figures...")
    fig1_system_architecture()
    fig2_pipeline_flowchart()
    fig3_feature_detection()
    fig4_constraint_autocorrect()
    print("\nDone! All figures saved.")
