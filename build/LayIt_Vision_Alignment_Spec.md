# LayIt Laser — Vision Alignment System
## Technical Specification for Electrical Engineer
## Phase 2: Camera-Based Auto-Alignment

---

## OVERVIEW

The LayIt Laser projects tile layout patterns onto floors and walls using a galvanometer scanner. The user places real tiles on top of the projected lines. The Vision Alignment System uses the onboard OV5640 camera to maintain projection accuracy at all times — including after the unit is bumped, picked up and moved, or repositioned by the user.

**The core principle:** Every tile the user places becomes a permanent reference point. The camera reads the hard geometric edges of placed tiles, matches them to the known layout pattern in the app, and continuously corrects the projection. The system gets MORE accurate over time as more tiles are placed.

**No external markers, stickers, or setup required.** Point and play.

---

## HARDWARE (Already in BOM)

| Component | Role | Notes |
|-----------|------|-------|
| OV5640 Camera | 5MP, 160° FOV, DVP interface | Already on PCB (J5, 24-pin FPC) |
| ESP32-S3 N16R8 | 8MB PSRAM for frame buffering | 2 framebuffers in PSRAM |
| Existing DAC/Galvo chain | Projection output | No changes needed |

| MPU6050 IMU (accelerometer/gyro) | Instant bump detection, I2C | Already in BOM (#13), ~$2 |

The MPU6050 connects via I2C (shares bus with camera SCCB). Provides instant motion detection before the camera can even process a frame. Added to the Flagship BOM as component #13.

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     LAYIT APP (Phone)                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Layout Engine │  │ Tile Registry│  │ Alignment Status │  │
│  │ (tile coords) │  │ (placed tile │  │ (confidence      │  │
│  │               │  │  tracking)   │  │  indicator)      │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
└─────────┼─────────────────┼────────────────────┼────────────┘
          │ WebSocket       │ WebSocket          │ WebSocket
          ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   ESP32-S3 FIRMWARE                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Scan Loop    │  │ Vision Engine│  │ IMU Monitor      │  │
│  │ (galvo out)  │◄─┤ (OpenCV)    │  │ (bump detect)    │  │
│  │              │  │              │  │                   │  │
│  │ DAC → Galvo  │  │ Camera →    │  │ MPU6050 →        │  │
│  │ → Laser      │  │ Edge Detect→│  │ Motion Threshold→│  │
│  │              │  │ Homography → │  │ Trigger Relock   │  │
│  │              │  │ Correction   │  │                   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: COLD START (Before Any Tiles Are Placed)

This is the only moment where the camera has no tile edges to reference. The app's segment ordering system already handles this — it directs the user to start in a corner or against a wall.

### How It Works

**Step 1 — App determines starting segment:**

The existing serpentine path algorithm already starts from the top-left segment (row 0, col 0 in the segment grid). For floor mode, this means starting against the two walls that form a corner. For wall mode, this means starting from the bottom-left.

This is correct behavior — tile installers always start from a reference edge (wall, chalk line, or datum). The app should enforce this by:
- Locking all segments except the starting segment
- Displaying: "Position the LayIt Laser to project onto this corner"
- The starting segment is always adjacent to at least one wall edge

**Step 2 — User positions the unit:**

The user sets the LayIt Laser on a tripod (floor mode) or handheld/mounted (wall mode), aimed at the starting corner.

**Step 3 — Camera detects wall edges / room corner:**

The camera captures the work surface. The vision engine detects:
- **Straight edges** where the floor meets the wall (high contrast line)
- **Corner intersection** where two walls meet (two lines converging)
- **Surface plane** — the floor/wall surface the projection lands on

Algorithm:
1. Capture frame at VGA resolution (640×480)
2. Convert to grayscale
3. Apply Gaussian blur (reduce noise)
4. Canny edge detection (find edges)
5. Hough line transform (find straight lines — wall edges)
6. Identify the two dominant perpendicular lines (the corner)
7. Compute intersection point = room corner in camera coordinates

**Step 4 — User confirms origin:**

The app shows the camera feed with the detected corner highlighted:
- "I found the room corner. Is this your starting point?"
- User taps YES → projection begins from that corner
- User taps ADJUST → can manually nudge the origin point on screen

**Step 5 — Initial projection begins:**

The system now knows:
- Where the room corner is in camera space
- Where the room corner is in the layout pattern (0,0 origin)
- The projection distance (from existing manual calibration or auto-detected)

It projects the first segment's tile pattern aligned to the corner.

### Fallback: No Detectable Corner

If the camera can't find a clean corner (open room, curved wall, outdoor), the system falls back to:
1. Project a crosshair at center of projection
2. User physically aligns the crosshair to their chosen starting point
3. User confirms in app: "This is my origin"
4. System locks that camera-to-projection mapping as the baseline

This is the same as Phase 1 manual calibration but with a single tap instead of tape-measure verification.

---

## PHASE 2: LIVE TILE EDGE DETECTION (The Core System)

Once the first tile is placed, the vision system has its first permanent reference. Every subsequent tile strengthens the reference grid.

### Detection Pipeline

**Runs continuously — every 500ms (2 FPS vision loop):**

```
1. CAPTURE
   Camera grabs frame (VGA, 640×480)
   Store in PSRAM framebuffer

2. PREPROCESS
   Convert to grayscale
   Apply adaptive threshold (handles varying lighting)
   Morphological close (fill small gaps in grout lines)

3. EDGE DETECTION
   Canny edge detector
   → Finds tile edges (hard straight lines)
   → Grout lines appear as thin dark channels between tiles
   → Tile edges are high-contrast rectangles

4. CONTOUR EXTRACTION
   findContours() on thresholded image
   Filter: keep only quadrilateral contours (4-sided shapes)
   Filter: minimum area threshold (reject noise)
   Filter: aspect ratio check (reject non-tile shapes)
   → Each detected contour = one placed tile

5. CORNER REFINEMENT
   cornerSubPix() on each detected tile corner
   → Sub-pixel accuracy on corner positions
   → This is what gets you to <1mm precision

6. TILE MATCHING
   For each detected tile contour:
     - Compute center point and dimensions
     - Compare against the layout pattern's tile positions
     - Find the best match (nearest tile in the pattern that
       matches the detected size/orientation)
     - Record: camera_corner_points ↔ layout_corner_points

7. HOMOGRAPHY COMPUTATION
   Collect all matched tile corners:
     - Camera points: where the camera sees tile corners
     - Layout points: where those corners should be per the pattern

   findHomography(camera_points, layout_points)
   → Returns 3×3 transformation matrix
   → This matrix encodes the exact position, angle, and
      perspective of the projector relative to the work surface

   Minimum: 4 corner points (1 tile)
   Better: 16+ corner points (4+ tiles)
   More points = more robust = less sensitive to any single
   detection error

8. PROJECTION CORRECTION
   Apply homography to all unprojected tile positions
   → Transforms layout coordinates into corrected galvo coordinates
   → Accounts for: projector position, angle, tilt, distance,
      perspective distortion

   Update the galvo scan buffer with corrected coordinates
   Projection now aligns perfectly with placed tiles

9. CONFIDENCE SCORE
   Compute reprojection error:
     - For each matched tile corner, compute where the homography
       PREDICTS it should be vs. where the camera ACTUALLY sees it
     - Average error across all points = alignment confidence

   < 0.5mm average error → GREEN (locked, high confidence)
   0.5–2mm average error → YELLOW (usable, minor drift)
   > 2mm average error   → RED (unreliable, needs attention)
   No tiles detected     → RED (lost reference)
```

### Key Properties

**Absolute positioning:** Every correction cycle derives position from scratch using the placed tiles. It does NOT build on the previous correction. This means errors cannot accumulate. Frame N and frame N+1000 use the same math, with the same accuracy.

**Self-improving:** With 1 tile placed, the system has 4 reference corners. With 10 tiles placed, it has 40 reference corners. The homography computation with 40 points is dramatically more robust than with 4. Outlier detection (RANSAC) can reject any single bad detection without affecting the result.

**Lighting resilient:** Tile edges are physical depth changes (the grout channel is recessed). Even in low light, adaptive thresholding picks up the shadow/depth contrast. The laser itself also illuminates the work surface, helping the camera see edges.

---

## PHASE 3: BUMP RECOVERY

### Scenario: Unit Gets Bumped or Moved

**With IMU (recommended):**

1. MPU6050 detects acceleration spike above threshold (e.g., >0.5g)
2. Firmware immediately:
   - Flags `alignment_state = DISRUPTED`
   - Sends WebSocket: `{ "type": "alignment_warning", "reason": "motion_detected" }`
   - App displays: "Movement detected — verifying alignment..."
   - **Does NOT stop projecting yet** (bump might be minor)
3. Vision engine runs immediate re-alignment cycle (same pipeline as Phase 2)
4. If reprojection error < threshold:
   - Correction applied, projection updated
   - Flag: `alignment_state = LOCKED`
   - App displays: "Alignment verified" (green indicator)
   - Total recovery time: ~1 second
5. If reprojection error > threshold:
   - Projection pauses (laser blanked — galvos still running but laser off)
   - App displays: "Alignment lost — reposition unit to see placed tiles"
   - System waits for camera to detect tiles again
   - Once tiles detected and homography passes: auto-resumes

**Without IMU (camera-only):**

Same as above but detection relies on the continuous 500ms vision loop noticing that tile positions have shifted in the camera frame. Slightly slower response (~1-2 seconds) but still functional.

### Scenario: Unit Picked Up and Moved to New Position

1. Camera sees no tiles (pointed at ceiling during move, or new angle)
2. `alignment_state = LOST`
3. Projection pauses
4. User places unit in new position aimed at work surface
5. Camera detects placed tiles in view
6. Matches detected tiles to layout pattern
7. Computes new homography from new viewpoint
8. Projection resumes with correct alignment from new position
9. **The user does not need to do anything in the app.** The system finds its own way back.

This is the key feature: **pick up, move, set down, it just works.**

### Scenario: Unit Moved Mid-Tile (Worst Case)

The user is placing a tile when the unit gets bumped. The projection shifts. The tile they're placing is now potentially misaligned.

Safeguards:
1. IMU triggers instant warning: "Movement detected — hold tile placement"
2. Vision engine re-aligns within ~1 second
3. App shows: "Alignment restored — projection is accurate" or "Re-check last tile position"
4. If the tile was already set in thinset: camera can see it's placed, compares to pattern, and flags if it's off by more than the grout line width

---

## CONSTRAINT-AWARE AUTO-CORRECTION

### The Problem

When the first tile is placed slightly off from the planned position, the system auto-corrects the projected pattern to match the placed tile. This works well in open areas where wall cuts absorb the offset. However, if the room has **fixed features** — niches, drains, windows, thresholds — shifting the pattern can cause misalignment at those features. A niche opening is physically fixed in the wall; if the pattern shifts 3mm, the grout lines won't align with the niche edges.

### Constraint Hierarchy

The system distinguishes between two types of layout constraints:

**Fixed Constraints (never move — real physical features):**
- Niche/shelf openings (shower shelves, recessed soap dishes)
- Window frames and sills
- Floor drain positions
- Door thresholds and transition strips (tile-to-carpet, tile-to-wood)
- Countertop edges (backsplash top/bottom)
- Fixture mounting points (toilet flange, vanity)
- Any user-defined anchor point marked in the app

**Flexible Constraints (can absorb small offsets):**
- Wall edges (tiles are cut here anyway — a few mm offset just changes the cut width)
- Corner alignment
- The placed tile's actual position vs. planned position

### User Workflow: Marking Fixed Constraints

During layout planning (before projection begins), the user marks fixed constraints in the app:

1. **From camera scan:** The depth estimation system detects recesses (niches) and protrusions as planes at different depths. These are presented to the user for confirmation: "Is this a niche? Mark as fixed constraint?"

2. **Manual marking:** User taps the layout in the app to place constraint markers: "Niche here, 14" wide × 24" tall, bottom edge at 48" from floor." The layout engine ensures grout lines align with niche edges.

3. **Drain/fixture marking:** User taps approximate location, optionally takes a close-up photo for precise positioning via depth estimation.

The layout engine generates the pattern **anchored to the most critical fixed constraint first**, then works outward. Wall cuts absorb whatever offset remains.

### Auto-Correction with Constraint Checking

When the first tile (or any tile) is placed and detected by the camera:

1. Camera detects placed tile position via edge detection
2. System computes the offset vector: how far the tile is from the planned position (dx, dy in mm)
3. **Before applying the correction**, the system runs a constraint impact check:

   ```
   For each fixed_constraint in layout:
       projected_shift = apply_offset(constraint.grout_lines, dx, dy)
       misalignment = distance(projected_shift, constraint.physical_edge)
       if misalignment > grout_line_width / 2:
           flag constraint as IMPACTED
   ```

4. **Three outcomes:**

| Outcome | Condition | System Behavior |
|---------|-----------|-----------------|
| **SAFE** | No fixed constraints impacted | Auto-correct silently. Pattern shifts to match placed tile. Wall cuts absorb offset. |
| **WARNING** | Fixed constraint would be impacted | Alert user with specific info (see below). User chooses resolution. |
| **NO CONSTRAINTS** | No fixed constraints defined | Auto-correct freely. |

### Warning Dialog (Constraint Conflict)

When a placed tile's offset would impact a fixed constraint, the app displays:

```
⚠️ TILE OFFSET DETECTED

First tile is 3mm left of planned position.

Adjusting the pattern would misalign:
  • Shower niche (row 8) — grout line would be 3mm off niche edge

Options:
  [1] REPOSITION TILE (recommended)
      → Lift and re-place first tile 3mm to the right
      → Pattern stays anchored to niche

  [2] KEEP NICHE ALIGNMENT
      → Pattern stays anchored to niche
      → First tile cut at left wall will be 3mm narrower
      → This tile's position will not match projection

  [3] ADJUST TO TILE
      → Pattern shifts to match this tile
      → Niche grout lines will be 3mm off
      → NOT RECOMMENDED if niche alignment matters
```

For professional installers, option 1 or 2 is almost always the right call. The system defaults to recommending whichever preserves the fixed constraint.

### Tolerance Thresholds

Not every offset matters. The system uses configurable tolerances:

| Offset Amount | Grout Width | Result |
|---|---|---|
| < 1mm | Any | Auto-correct silently (imperceptible) |
| 1-2mm | 3mm+ grout | Auto-correct silently (absorbed by grout) |
| 1-2mm | 1mm grout (rectified tile) | Warn if fixed constraint exists |
| > 2mm | Any | Always warn if fixed constraint exists |
| > grout width | Any | Flag tile as misplaced regardless of constraints |

### Measurement Mismatch Detection

If the camera-based room measurement was used to generate the layout, and the first placed tiles reveal the measurement was off:

1. System continuously compares placed tile positions to the layout grid
2. If a systematic offset is detected across 3+ placed tiles (all shifted in the same direction by a similar amount), the system infers the room measurement was off
3. Alert: "Room measurement may be off by ~Xmm. The layout has been generated for a [wider/narrower] space than actual. Review cut tiles at [wall name] — they may be [larger/smaller] than shown."
4. User can choose to:
   - Continue (cuts will be slightly different than displayed)
   - Re-measure and regenerate layout (only practical before many tiles are set)
   - Manually adjust the room dimension in the app and regenerate remaining tiles

---

## CONFIDENCE INDICATOR (App UI)

The app displays an always-visible alignment status:

### States

| State | Color | Meaning | User Action |
|-------|-------|---------|-------------|
| INITIALIZING | Blue | Cold start, detecting room corner | Position unit, confirm origin |
| LOCKED | Green | Aligned, <0.5mm error | Work normally |
| CORRECTING | Yellow pulse | Minor drift detected, auto-correcting | Wait 1 second |
| DISRUPTED | Orange | Bump detected, verifying | Hold tile placement |
| LOST | Red | Cannot see reference tiles | Reposition unit |
| PAUSED | Red blink | Projection stopped, alignment unreliable | Reposition unit toward placed tiles |

### WebSocket Messages (New)

**Device → App:**
```json
{ "type": "alignment_update",
  "state": "locked",
  "confidence": 0.97,
  "error_mm": 0.3,
  "ref_tiles": 12,
  "homography": [3x3 matrix] }

{ "type": "alignment_warning",
  "reason": "motion_detected",
  "magnitude": 1.2 }

{ "type": "alignment_lost",
  "reason": "no_tiles_visible",
  "last_good_state": { ... } }

{ "type": "alignment_recovered",
  "error_mm": 0.4,
  "ref_tiles": 8 }
```

**App → Device:**
```json
{ "type": "confirm_origin",
  "corner": { "x": 0, "y": 0 },
  "wall_edges": true }

{ "type": "manual_adjust",
  "offset_x_mm": 2.5,
  "offset_y_mm": -1.0 }

{ "type": "tile_placed",
  "tile_id": 42,
  "segment": 0 }
```

---

## TILE REGISTRY (App-Side Tracking)

The app maintains a registry of which tiles have been placed. This helps the vision engine:

### Automatic Detection
When the camera detects a new tile edge that wasn't there in the previous frame, the app:
1. Matches it to the nearest expected tile in the layout
2. Marks that tile as "placed" in the registry
3. Updates the projection to dim/remove the outline for that tile (optional — user preference)
4. Adds this tile's corners to the reference point pool

### Manual Confirmation (Optional)
User can tap a tile in the app to confirm it's placed. This is not required but provides a backup if camera detection is uncertain (e.g., tile color matches substrate color closely).

### Registry Data Structure
```json
{
  "tiles": [
    {
      "id": 0,
      "layout_position": { "x": 0, "y": 0 },
      "layout_corners": [[0,0], [12,0], [12,12], [0,12]],
      "status": "placed",
      "detected_corners": [[px1,py1], [px2,py2], [px3,py3], [px4,py4]],
      "placement_error_mm": 0.3,
      "timestamp": 1708000000
    }
  ]
}
```

---

## INTEGRATION WITH EXISTING CODEBASE

### Firmware Changes (LayIt_Laser.ino)

**New modules to add:**
1. `vision_engine.cpp` — Camera capture, OpenCV processing, homography
2. `imu_monitor.cpp` — MPU6050 I2C polling, bump detection (if IMU added)
3. `alignment_manager.cpp` — State machine, confidence scoring, correction application

**Existing code that needs modification:**
- `buildScanBuffer()` — Apply homography correction to DAC coordinates before output
- `inchesToDAC()` — Add correction matrix multiplication step
- WebSocket handler — Add new message types (alignment_update, confirm_origin, etc.)
- Main loop — Add vision processing task on second core (ESP32-S3 is dual-core)

**Threading model:**
- **Core 0:** WiFi, WebSocket, vision processing (camera capture + OpenCV)
- **Core 1:** Scan loop (galvo output) — timing-critical, must not be interrupted

The ESP32-S3's dual-core architecture is well suited for this. The scan loop runs uninterrupted on Core 1 while vision processing happens on Core 0. The only shared data is the correction matrix, protected by a mutex.

### App Changes (index.html)

**New UI elements:**
- Alignment confidence indicator (always visible during projection)
- Camera preview during cold start (show detected corner)
- Origin confirmation dialog
- Tile registry overlay (show which tiles are detected as placed)

**New WebSocket handlers:**
- `alignment_update` → Update confidence indicator
- `alignment_warning` → Show bump notification
- `alignment_lost` → Show reposition prompt
- `alignment_recovered` → Clear warning, show green status

**Existing code that integrates:**
- `segmentState` — Starting segment selection already correct (corner-first)
- `generateSerpentinePathOrder()` — No changes needed (already starts from corner)
- Segment locking — Already prevents out-of-order work

---

## OPENCV ON ESP32-S3: FEASIBILITY

The ESP32-S3 with 8MB PSRAM can run lightweight OpenCV operations:

**What's feasible at VGA (640×480):**
- Grayscale conversion: <5ms
- Gaussian blur: ~10ms
- Canny edge detection: ~20ms
- Contour finding: ~15ms
- Homography computation: ~5ms
- **Total pipeline: ~50-80ms per frame (12-20 FPS potential)**

**Library:** Use `esp-who` (Espressif's official CV library) or compile OpenCV's core modules for ESP-IDF. Alternatively, implement Canny + contour detection manually (the algorithms are well-documented and the ESP32-S3 at 240MHz handles them).

**Memory budget:**
- 1 VGA frame (grayscale): 307KB
- 2 framebuffers: 614KB
- Edge map + contour storage: ~200KB
- Working memory: ~200KB
- **Total: ~1MB of 8MB PSRAM** — plenty of headroom

---

## ACCURACY EXPECTATIONS

| Tiles Placed | Reference Corners | Expected Accuracy | Notes |
|---|---|---|---|
| 0 (cold start) | Wall edges only | ±2-3mm | Depends on wall edge detection quality |
| 1 | 4 corners | ±1-2mm | Minimum viable reference |
| 4 | 16 corners | ±0.5-1mm | Good working accuracy |
| 10+ | 40+ corners | <0.5mm | Robust, outlier-resistant |
| 25+ | 100+ corners | <0.3mm | Highest accuracy tier |

For context: standard grout lines are 1.5mm (1/16") to 3mm (1/8"). Sub-0.5mm accuracy means the projection is well within the grout tolerance.

---

## EDGE CASES AND FAILURE MODES

| Scenario | System Response | User Experience |
|----------|----------------|-----------------|
| Unit bumped slightly | Auto-corrects in ~1 second | Brief yellow flash, then green |
| Unit picked up and moved | Pauses, re-detects tiles from new angle | Red → "Reposition toward tiles" → Green |
| All placed tiles blocked from view | Pauses projection | "Move unit to see placed tiles" |
| Very low light | Switches to longer exposure, uses laser reflection | May reduce to 1 FPS vision, still functional |
| Tile color matches substrate | Relies on grout channel shadow/depth | May need manual tile confirmation in app |
| Large format tiles (24"+) | Fewer corners per area | Still works — needs minimum 1 full tile visible |
| Herringbone/diagonal pattern | More edges per area, angled lines | Easier detection — more reference data |
| Wet thinset on surface | Reflective surface may cause glare | Camera auto-exposure compensates; worst case: use IMU for bump detection until tiles placed |
| Outdoor / bright sunlight | Camera exposure adjusts, edge contrast may reduce | Green laser (520nm) still visible in daylight; add ND filter to camera if needed |

---

## IMPLEMENTATION PRIORITY

**For the engineer — build in this order:**

1. **Camera initialization and frame capture** — Get the OV5640 streaming frames to PSRAM. Verify image quality. This validates the hardware.

2. **Edge detection on a test surface** — Lay a few tiles, run Canny + contour detection, verify tile edges are found reliably. This validates the algorithm.

3. **Homography computation** — With detected tile corners matched to known positions, compute the transformation. Project a test pattern and verify it aligns. This validates the math.

4. **Continuous correction loop** — Run the full pipeline at 2 FPS on Core 0 while the scan loop runs on Core 1. Bump the unit, verify it re-aligns. This validates real-time performance.

5. **Cold start / corner detection** — Implement wall edge detection for initial alignment. This is lower priority because it only runs once per job.

6. **IMU integration** (optional but recommended) — Add MPU6050, implement bump detection threshold, wire into alignment state machine.

7. **App integration** — Confidence indicator, camera preview, tile registry UI.

---

## SUMMARY

The Vision Alignment System turns the placed tiles into a self-reinforcing reference grid. No markers. No stickers. No extra setup. The user sets down the unit, confirms the starting corner, and starts tiling. The camera watches constantly, corrects silently, and alerts the user if anything needs attention.

The hardware is already in the BOM. The ESP32-S3 has the processing power. The algorithms are well-proven (OpenCV). The main engineering effort is firmware development — specifically the vision pipeline and the homography-to-galvo correction bridge.

This is the feature that makes LayIt Laser a professional tool rather than a novelty. It must work reliably. Build it incrementally, test it at every step, and do not ship until bump recovery is rock solid.
