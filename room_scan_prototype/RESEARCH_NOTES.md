# Room Scan Research Notes

Last updated: 2026-03-14

## Context

We're building a phone-camera-based room measurement system for tile layout projection.
The depth estimation backbone is Apple Depth Pro, which produces metric (absolute scale)
depth maps from a single photo in ~0.3 seconds. Our tests show raw depth values within
~1 inch of ground truth on direct measurements. The challenge is turning those depth maps
into accurate room dimensions.

---

## 1. Monocular Depth to Room Geometry

### Current approach (baseline)
- Back-project depth map to 3D point cloud via pinhole model
- Use percentile-based heuristics to find wall extents along X, Y, Z axes
- Problems: no plane awareness, sensitive to furniture/clutter, no out-of-square detection

### Better approach: RANSAC plane fitting

The standard pipeline for extracting room geometry from a point cloud is:

1. **Convert depth map to 3D point cloud** (pinhole back-projection -- we already do this)
2. **Fit planes using RANSAC** -- iteratively sample 3 points, fit a plane, count inliers
3. **Classify planes by normal direction:**
   - Normal ~= (0, 1, 0) or (0, -1, 0) -> floor or ceiling (horizontal)
   - Normal ~= (1, 0, 0) or (-1, 0, 0) -> left/right walls (vertical, perpendicular to X)
   - Normal ~= (0, 0, 1) or (0, 0, -1) -> front/back walls (vertical, perpendicular to Z)
4. **Extract room dimensions** from plane-to-plane distances

Key paper: "Floor Plan Reconstruction from Indoor 3D Point Clouds Using Iterative
RANSAC Line Segmentation" (2024) -- achieved 90%+ accuracy on line segment reconstruction
and 97% IoU on floor plan reconstruction, even for non-Manhattan (non-rectangular) rooms.

The MonoPlane paper (Nov 2024) introduced a proximity-guided RANSAC that incorporates
monocular depth and surface normal cues, significantly improving robustness on noisy inputs.

### Implementation plan (numpy-only RANSAC)
- Subsample point cloud (every Nth pixel) for speed
- RANSAC loop: sample 3 points, fit plane via cross product, count inliers within threshold
- After finding dominant plane, remove its inliers, repeat to find next plane
- Classify planes by normal vector direction
- Compute room dimensions from plane-to-plane distances

### Out-of-square wall detection
Once we have plane equations for opposite walls, we can:
- Measure the distance between wall planes at multiple Y-heights and X-positions
- If the distance varies by more than some threshold (e.g., 0.5 inch), the walls are not parallel
- Report the min/max/delta measurements so the tiler knows the room is out of square

---

## 2. The Camera Offset Problem

When you stand in a room and take a photo, the depth map measures from the camera to the
far wall. But the total room dimension also includes the space behind you (camera to the
wall behind you). Typical offset: ~12 inches (0.3m) when standing with back near a wall.

### Approaches:
1. **Fixed offset** -- Add a configurable constant (default 0.3m / 12") to the length
   measurement. Simple, works well when the user stands with back against the wall.
2. **Two-photo method** -- Take one photo facing each direction. Sum the two depth
   measurements. The overlap region (where both photos see the same area) can be used
   to detect and correct any double-counting.
3. **Corner-to-corner** -- Stand in a corner and photograph diagonally. The room
   diagonal gives both dimensions via geometry, but requires knowing the corner angle.
4. **Calibration-based** -- Use known room measurements to learn a per-setup correction
   factor that accounts for typical standing distance.

**Recommendation:** Start with approach #1 (fixed offset flag) and approach #4 (calibration).
The two-photo method is the most accurate but requires multi-view alignment (see below).

---

## 3. Multi-View Room Reconstruction

### Why multi-view?
A single photo cannot see the entire room. Combining multiple photos gives:
- Complete coverage of all walls
- Redundant measurements for higher accuracy
- Out-of-square detection (measure same wall from different angles)

### State of the art: DUSt3R / MASt3R / MUSt3R (NAVER Labs, 2024-2025)

These are transformer-based 3D foundation models that reconstruct 3D scenes from
unconstrained image collections WITHOUT requiring known camera poses or intrinsics.

- **DUSt3R**: Predicts "pointmaps" from image pairs, regressing 3D structure directly.
  Works with as few as 2 images. No camera calibration needed.
  GitHub: https://github.com/naver/dust3r

- **MASt3R**: Extension of DUSt3R that adds metric pointmaps and a matching head.
  Outputs are in metric scale, making it suitable for measurement.
  GitHub: https://github.com/naver/mast3r

- **MV-DUSt3R+**: Multi-view extension that reconstructs single rooms in ~0.9 seconds
  from 12 views. Handles large multi-room scenes in ~1.5 seconds.

### Simpler approaches for our "2 straight-on shots" use case:

Since our use case is measuring a rectangular-ish room, we can use a simpler strategy:

1. **Photo 1**: Face the far wall. Get depth to far wall = D1 (room length contribution)
2. **Photo 2**: Turn 180 degrees, face the opposite wall. Get depth = D2
3. **Room length** = D1 + D2 - overlap (person's body width, ~0.5m)

For this to work without full 3D alignment:
- Each photo independently measures camera-to-wall distance
- Total room length = D1 + D2 (if we assume no overlap / the user sidesteps)
- Width comes from the wider of the two photos' X-extent measurements
- Height should be consistent across both photos

### ICP-based alignment (classical approach):
If we want to properly merge two point clouds:
1. Find corresponding 3D points (feature matching between the two images)
2. Estimate rigid transform (rotation + translation) using RANSAC or ICP
3. Transform second point cloud into first point cloud's coordinate frame
4. Merge and extract unified room geometry

This is more complex but handles arbitrary camera positions.

---

## 4. Practical Recommendations (ranked by impact vs complexity)

### Tier 1: High impact, low complexity (do now)
1. **RANSAC plane fitting** -- Replace percentile heuristics with proper plane detection.
   Pure numpy implementation, no new deps. Will dramatically improve wall detection accuracy.
2. **Camera offset flag** -- Simple --camera-offset argument. Immediate accuracy improvement
   for the primary use case (standing near wall, photographing opposite wall).
3. **Calibration script** -- Accumulate known-measurement vs estimated-measurement pairs.
   Compute correction factors. Essential for validating and improving the pipeline.

### Tier 2: Medium impact, medium complexity (next sprint)
4. **Out-of-square detection** -- Once we have plane equations, measure wall distances at
   multiple points. Critical for tiling (out-of-square rooms need adjusted layouts).
5. **Top-down floor plan visualization** -- Project detected wall planes onto XZ plane,
   draw as lines. Gives the user immediate visual feedback on room shape.
6. **Two-photo simple merge** -- Sum measurements from two opposite-facing photos.
   No alignment needed, just arithmetic. Big accuracy improvement.

### Tier 3: High impact, high complexity (future)
7. **DUSt3R/MASt3R integration** -- Full pose-free multi-view reconstruction. Would give
   complete room model from arbitrary photos. Requires GPU, additional model download (~2GB).
8. **Surface normal estimation** -- Use Depth Pro's depth map to compute surface normals,
   then use normals to improve plane fitting (MonoPlane approach).
9. **Trained correction model** -- After accumulating enough calibration data, train a
   small model that predicts correction factors based on image features (room size, FOV, etc).

---

## 5. Open Source Tools We Can Leverage

| Tool | What it does | License | Notes |
|------|-------------|---------|-------|
| [Apple Depth Pro](https://github.com/apple/ml-depth-pro) | Metric monocular depth | Apple | Already using |
| [DUSt3R](https://github.com/naver/dust3r) | Pose-free 3D reconstruction | CC BY-NC-SA 4.0 | Best for multi-view, non-commercial |
| [MASt3R](https://github.com/naver/mast3r) | Metric matching + reconstruction | CC BY-NC-SA 4.0 | DUSt3R + metric + matching |
| [pyRANSAC-3D](https://github.com/leomariga/pyRANSAC-3D) | RANSAC primitive fitting | MIT | Could use, but numpy-only is fine |
| [MonoPlane](https://arxiv.org/html/2411.01226v1) | Monocular plane reconstruction | Research | Proximity-guided RANSAC approach |

---

## 6. Key Insights from Testing

- Depth Pro's metric depth is remarkably accurate on direct measurements (~1 inch error)
- The main source of error is NOT the depth values themselves, but how we extract geometry
- Percentile-based wall finding breaks down with furniture, open doorways, and alcoves
- RANSAC plane fitting should be much more robust to these real-world complications
- The camera offset is a systematic bias that can be corrected with a simple constant
- For tiling, we care most about floor dimensions and wall straightness, not full 3D

---

## 7. References

- Floor plan from point clouds via iterative RANSAC: https://www.sciencedirect.com/science/article/abs/pii/S2352710224008064
- MonoPlane (monocular plane reconstruction): https://arxiv.org/html/2411.01226v1
- DUSt3R (pose-free 3D): https://github.com/naver/dust3r
- MASt3R (metric matching): https://github.com/naver/mast3r
- MV-DUSt3R+ (multi-view): https://mv-dust3rp.github.io/
- Apple Depth Pro paper: https://machinelearning.apple.com/research/depth-pro
- pyRANSAC-3D: https://github.com/leomariga/pyRANSAC-3D
- Plane detection and ranking: https://arxiv.org/html/2508.09625v1
