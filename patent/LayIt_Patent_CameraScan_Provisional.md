# UNITED STATES PROVISIONAL PATENT APPLICATION

---

## PROVISIONAL PATENT APPLICATION

> **Filing Notes:**
> - This provisional application establishes a priority date for the camera-based room measurement and automatic tile layout generation system.
> - This is intended to be combined with the existing LayIt provisional patent (laser projection system) into a single utility patent application.
> - Filing fee: $180 (micro-entity) or $320 (small entity) as of 2026.
> - **Strongly recommended**: Have a registered patent attorney or agent review this document before filing with the USPTO.
> - This provisional must be converted to a utility application within 12 months of filing.

---

## 1. TITLE OF THE INVENTION

Method and System for Automatic Room Geometry Extraction from Monocular Camera Images for Generation of Tile Installation Layouts

---

## 2. INVENTOR

Sole Inventor: [INVENTOR FULL LEGAL NAME]

---

## 3. CROSS-REFERENCE TO RELATED APPLICATIONS

This application is related to U.S. Provisional Application No. [PRIOR APP NUMBER], filed [DATE], entitled "System and Method for Real-Time Laser Projection of Tile Installation Patterns with Vision-Based Self-Correcting Alignment," the entirety of which is incorporated herein by reference. The present invention describes additional methods and systems for automatically determining room geometry from camera images, which geometry data is used to generate tile installation layouts for projection by the laser system described in the related application, or for independent use in tile layout planning software.

---

## 4. FIELD OF THE INVENTION

The present invention relates generally to computer vision-based measurement systems for construction applications, and more particularly to a method and system for extracting accurate metric room dimensions from one or more photographs captured by a standard mobile phone camera, using monocular depth estimation neural networks and geometric plane fitting algorithms, to automatically generate tile installation layout patterns without requiring manual measurement, LiDAR sensors, time-of-flight cameras, or specialized measurement hardware.

---

## 5. BACKGROUND OF THE INVENTION

### 5.1 The Room Measurement Problem in Tile Installation

Before any tile installation can begin, the installer must obtain accurate measurements of the work surface. For floor installations, this means measuring room length, width, and the positions of obstacles, alcoves, and transitions to other flooring materials. For wall installations (backsplashes, shower surrounds, accent walls), this means measuring the wall height, width, and positions of fixtures, outlets, windows, and other features.

These measurements must be highly accurate. In tile work, a dimensional error as small as one centimeter can compound across a floor or wall, resulting in misaligned grout joints, improper tile cuts at boundaries, and visible pattern discontinuities. Professional installers typically spend 15-45 minutes per surface on measurement and layout planning before any tile is set.

### 5.2 Existing Measurement Methods and Their Limitations

**Manual Tape Measurement.** The standard method requires physically stretching a tape measure or deploying a laser distance meter (such as a Bosch GLM device) between reference points. While highly accurate when performed correctly, manual measurement is time-consuming, requires physical access to both endpoints, is difficult in cluttered or furnished rooms, and is subject to human error in recording and transcribing measurements.

**LiDAR-Based Scanning.** Recent mobile devices (notably Apple iPhone 12 Pro and later models equipped with LiDAR sensors) can perform room scanning using time-of-flight depth sensing. Applications such as Apple's Measure app and third-party room scanning tools generate 3D room models exported as USDZ or other 3D formats. However, LiDAR-based room scanning has significant practical limitations for tile installation purposes:

(a) LiDAR sensors are available only on premium-tier mobile devices, excluding the majority of smartphones in active use;

(b) LiDAR room scans produce noisy point clouds that require significant post-processing to extract usable room dimensions;

(c) In testing by the present inventor, LiDAR-based room scans from consumer mobile devices consistently produced dimensional errors of 2-6 inches (5-15 cm) on room-scale measurements, which is unacceptable for tile layout purposes;

(d) LiDAR performance degrades significantly on reflective surfaces (glazed tile, mirrors, glass shower doors) and transparent surfaces (windows), which are commonly present in rooms where tile is installed;

(e) The scanning process requires the user to slowly walk around the room while holding the device steady, which is awkward and time-consuming.

**Photogrammetry.** Traditional multi-view photogrammetry requires capturing dozens of overlapping photographs from calibrated positions, processing them through computationally intensive structure-from-motion algorithms, and extracting measurements from the resulting point cloud. This process requires significant expertise, computational resources, and time (often hours of processing), making it impractical for job-site use.

### 5.3 Recent Advances in Monocular Depth Estimation

Recent advances in deep learning have produced neural network models capable of estimating metric (absolute-scale) depth from a single RGB photograph. Models such as Apple Depth Pro (2024), Depth Anything v3 (ByteDance, 2025), and DepthFM (2025) can produce dense depth maps with metric accuracy from a single image captured by a standard phone camera, without requiring LiDAR, stereo cameras, or known camera calibration parameters.

These models represent a fundamental shift: accurate 3D geometry can now be extracted from ordinary photographs taken with any smartphone camera. However, no existing system applies monocular depth estimation specifically to the problem of room measurement for tile installation layout generation, with the specific accuracy requirements, surface-specific workflow, and integration with projection-based installation guidance that tile work demands.

### 5.4 Unmet Need

There exists a need for a system that can:

(a) Accept one or more standard photographs of a room or work surface captured by any smartphone camera (not limited to devices with LiDAR or other depth sensors);

(b) Automatically extract accurate metric dimensions of the room or work surface, including length, width, ceiling height, and detection of non-square (out-of-parallel) wall conditions;

(c) Achieve dimensional accuracy sufficient for tile installation purposes (ideally within 1 inch / 2.5 cm on room-scale measurements);

(d) Detect and measure irregular room features including alcoves, shower enclosures, kitchen islands, and non-rectangular floor plans;

(e) Allow the user to specify the intended tiling boundary when the tiling surface does not extend to all visible room boundaries (e.g., tile-to-carpet transitions in open floor plans);

(f) Automatically generate a tile installation layout within the measured boundaries; and

(g) Optionally transmit the generated layout to a laser projection system for real-time on-surface guidance.

### 5.5 Distinction from Prior Art

Several existing patents and commercial systems address aspects of indoor spatial measurement or tile visualization, but none anticipate or render obvious the present invention's combination of monocular depth estimation, tile-specific layout computation, architectural constraint detection, and laser projection integration.

**US Patent 10,026,218 — Indoor Scene Modeling Using Vanishing-Point Geometry.** This patent describes a method for modeling indoor scenes by detecting vanishing points from visible lines (wall-ceiling edges, wall-floor edges, and wall-wall intersections) in photographs and using the vanishing-point geometry to infer room structure. This approach fundamentally requires that room corners, ceiling lines, and floor lines be visible and unoccluded in the image. The present invention differs in that it uses monocular depth estimation neural networks that produce per-pixel metric depth values directly from the RGB image, without requiring detection of vanishing points, visible room corners, or geometric line intersections. This enables the present invention to operate from photographs taken at arbitrary angles, in rooms where corners are occluded by furniture or fixtures, and on surfaces (such as shower surrounds) where vanishing-point geometry is geometrically degenerate or undefined. Furthermore, US 10,026,218 produces a structural model of the room but does not address tile-specific layout generation, grout line computation, fixed constraint detection, or integration with physical installation guidance systems.

**US Patent Application US20170052026A1 — Laser and Phone Projection System.** This published application describes a system combining a laser projector with a mobile phone for general-purpose image projection. The system projects arbitrary images or patterns onto surfaces using the phone as a control interface. The present invention differs fundamentally in that it includes tile-specific layout computation comprising grout line spacing, pattern type selection (brick-bond, herringbone, chevron, etc.), cut tile optimization at boundaries, and non-square room compensation — none of which are addressed in US20170052026A1. More critically, the present invention includes constraint-aware auto-correction that checks whether tile pattern adjustments would break grout alignment at fixed architectural features (niches, windows, shelves), a capability entirely absent from general-purpose projection systems.

**Houzz-Type Augmented Reality Tile Visualization Systems.** Commercial systems such as those described in patents assigned to Houzz, Inc. and similar companies provide augmented reality overlays that allow users to visualize how different tile styles would appear on surfaces by superimposing virtual tile images onto a live camera feed. These systems are designed for aesthetic visualization and product selection, not for physical installation. They do not extract metric room dimensions from the camera image, do not generate physical installation layouts with computed tile cuts and grout line positions, do not detect or measure architectural features as fixed constraints, and do not interface with laser projection hardware for on-surface installation guidance. The present invention addresses the entirely distinct problem of producing an accurate, physically installable tile layout from camera-based room measurement.

---

## 6. SUMMARY OF THE INVENTION

The present invention provides a method and system for automatically extracting room geometry from one or more photographs captured by a standard mobile phone camera and generating a tile installation layout from the extracted geometry.

In a preferred embodiment, the method comprises the following steps:

**Step 1: Image Capture.** A user captures one or more photographs of the work surface or room using a standard smartphone camera. For a single-surface measurement (e.g., a wall, backsplash, or shower surround), a single photograph taken approximately perpendicular to the surface is sufficient. For a full-room measurement (e.g., a floor installation), the user captures two to four photographs from different positions within the room, preferably from opposite corners or walls.

**Step 2: Monocular Depth Estimation.** Each captured photograph is processed by a monocular depth estimation neural network that produces a dense metric depth map. The depth map assigns a distance value in meters to each pixel of the photograph, representing the distance from the camera to the physical surface visible at that pixel. The depth estimation model operates on standard RGB images and does not require LiDAR data, stereo image pairs, or known camera intrinsic parameters. In a preferred embodiment, the depth estimation model is a vision transformer-based architecture (such as Apple Depth Pro or equivalent) that produces metric (absolute-scale) depth without requiring scene-specific calibration.

**Step 3: 3D Point Cloud Generation.** The metric depth map is converted to a three-dimensional point cloud using the pinhole camera model. Each pixel (u, v) with estimated depth Z is projected to a 3D point (X, Y, Z) using the equations:

    X = (u - cx) * Z / f
    Y = (v - cy) * Z / f
    Z = Z

where (cx, cy) is the image center and f is the focal length in pixels, either extracted from the image EXIF metadata or estimated by the depth model.

**Step 4: Plane Detection via RANSAC.** The 3D point cloud is processed using an iterative Random Sample Consensus (RANSAC) algorithm to detect planar surfaces. The algorithm:

(a) Randomly samples three points from the point cloud;
(b) Computes the plane equation (normal vector and offset) defined by the three sample points;
(c) Counts the number of inlier points within a distance threshold (preferably 2-3 cm) of the candidate plane;
(d) Repeats steps (a)-(c) for a predetermined number of iterations (preferably 500-1000);
(e) Selects the plane with the highest inlier count;
(f) Removes the inlier points from the point cloud; and
(g) Repeats steps (a)-(f) to detect additional planes (up to a maximum of 6-8 planes for a typical room).

Each detected plane is classified by its normal vector direction as a floor (upward normal), ceiling (downward normal), left wall, right wall, far wall, or near wall.

**Step 5: Room Dimension Extraction.** Room dimensions are computed from the detected planes:

(a) **Width** is computed as the distance between opposing wall planes (e.g., left wall to right wall), measured as the difference in median position of inlier points along the dominant axis of the plane normals;

(b) **Length** is computed as the distance from the camera to the far wall plane. When two photographs taken from opposite ends of the room are available, the system uses the photograph with the highest-confidence far wall detection (determined by inlier count);

(c) **Ceiling height** is computed as the distance between the floor plane and ceiling plane;

(d) **Out-of-square detection** is performed by measuring the wall-to-wall distance at multiple sample points along the room length. If the measured distances vary by more than a threshold (preferably 0.5 inches / 1.3 cm), the system reports the walls as non-parallel and provides the minimum, maximum, and delta measurements. This information is critical for tile layout planning, as non-square rooms require tapered cuts along one or more walls.

**Step 6: Multi-Photo Fusion (Optional).** When multiple photographs are provided, the system selects the best measurement for each dimension based on detection confidence:

(a) Width is taken from the photograph in which both opposing side walls were detected with the highest combined inlier count;

(b) Length is taken from the photograph with the strongest far-wall plane detection;

(c) Height is computed as a confidence-weighted average across all photographs in which both floor and ceiling planes were detected;

(d) Out-of-square measurements from multiple photographs are cross-referenced for consistency.

**Step 7: User Boundary Specification (Optional).** For installations where the tiling surface does not extend to all room boundaries (e.g., a kitchen floor where tile transitions to carpet in an adjacent living room), the system presents the measured room polygon to the user in the companion application interface, and the user adjusts the boundary by dragging edges or vertices to define the intended tiling area. The system may also allow the user to place boundary markers in photographs before capture, which are detected and used to automatically define the tiling boundary.

**Step 8: Tile Layout Generation.** The measured room polygon (or user-adjusted boundary) is passed to a tile layout engine that:

(a) Accepts user-specified tile dimensions, pattern type (grid, brick-bond, herringbone, hexagonal, chevron, etc.), and grout spacing;

(b) Computes the optimal tile placement to minimize waste cuts, optionally centering the pattern on a focal point or balancing cut sizes at opposing walls;

(c) Generates a complete vertex list of all tile outlines, including computed dimensions for cut tiles at boundaries and around obstacles;

(d) Accounts for non-square wall conditions by computing tapered cuts where walls are not parallel.

**Step 9: Layout Transmission (Optional).** The generated tile layout is transmitted via wireless communication (preferably WiFi/WebSocket) to the laser projection hardware device described in the related application, which projects the tile pattern onto the physical work surface at 1:1 scale for installation guidance.

### Key Advantages Over Prior Art

The present invention provides several advantages over existing room measurement methods for tile installation:

1. **No specialized hardware required.** Any smartphone with a standard RGB camera can be used. No LiDAR sensor, depth camera, stereo camera rig, or external measurement device is needed.

2. **Speed.** A single-surface measurement can be completed in under 5 seconds (photograph capture plus processing). A full-room measurement from 2-4 photographs can be completed in under 30 seconds, compared to 15-45 minutes for manual measurement.

3. **Accuracy.** In testing by the present inventor, the system achieved dimensional accuracy within 0.5 inches (1.3 cm) on direct wall-to-wall measurements where both walls were visible in the photograph, which approaches the accuracy of manual tape measurement.

4. **Out-of-square detection.** The system automatically detects and quantifies non-parallel wall conditions, which is information that many installers fail to check manually and which causes significant problems during installation.

5. **Integrated workflow.** The measurement flows directly into tile layout generation and optionally into laser-projected installation guidance, eliminating the manual transcription of measurements that is a common source of error in traditional workflows.

6. **Improving accuracy over time.** The system includes a calibration mechanism wherein users provide known manual measurements alongside photographs, allowing the system to compute correction factors that improve accuracy over time and across different camera models and room types.

7. **Depth anomaly-based architectural feature detection.** Unlike systems that require manual marking or LiDAR scanning to detect niches, windows, and other surface features, the present invention automatically detects these features from depth map deviations relative to the dominant wall plane, enabling fully automatic constraint detection from a single photograph.

8. **Constraint-aware auto-correction.** No known prior system checks whether a tile pattern shift would break grout alignment at fixed architectural features before applying the correction. The present invention's three-outcome decision logic (SAFE/WARNING/NO CONSTRAINTS) prevents the most costly installation errors — misaligned tiles around shower niches, windows, and other visible focal points.

---

## 7. DETAILED DESCRIPTION OF PREFERRED EMBODIMENTS

### 7.1 System Architecture

The camera-based room measurement system comprises:

(a) A mobile computing device (smartphone or tablet) with a standard RGB camera and sufficient processing capability to execute a neural network inference (or with network connectivity to offload inference to a cloud server);

(b) A monocular depth estimation neural network model, either executing locally on the mobile device or on a cloud server accessible via network;

(c) A geometric processing module that converts depth maps to 3D point clouds, performs RANSAC-based plane detection, and extracts room dimensions;

(d) A tile layout generation engine that produces tile placement patterns from room geometry;

(e) Optionally, a wireless communication interface for transmitting generated layouts to a laser projection device.

### 7.2 Single-Surface Measurement Mode

For measuring a single tiling surface (wall, backsplash, shower surround, or similar), the preferred procedure is:

(a) The user positions themselves facing the surface and captures a single photograph that includes the full extent of the surface (all four edges visible);

(b) The system processes the photograph through the depth estimation model and RANSAC plane detection;

(c) The dominant plane in the depth map (the tiling surface itself) is identified;

(d) The extent of the surface is determined by detecting the bounding edges of the dominant plane — the points where the plane terminates (at adjacent walls, floor, ceiling, countertop, or other boundary surfaces);

(e) Surface width is computed from the horizontal extent of the plane, and surface height from the vertical extent;

(f) If the surface is not perfectly rectangular (e.g., a shower wall with a bench or niche), the system detects multiple planes and constructs a composite polygon representing the tiling area.

This mode is expected to provide the highest accuracy because: the camera is aimed directly at a single plane (minimizing oblique angle distortion), the surface boundaries are clearly defined by adjacent perpendicular surfaces, and the measurement is inherently wall-to-wall (no camera offset ambiguity since the camera is facing the surface, not standing against one end of it).

### 7.3 Full-Room Measurement Mode

For measuring a full room (floor installation or multi-wall installation), the preferred procedure is:

(a) The user captures 2-4 photographs from different positions within the room. The recommended protocol is:
   - Two photographs from opposite ends of the room, each facing the opposite wall (provides length measurements);
   - Two photographs from opposite sides of the room, each facing the opposite wall (provides width measurements);

(b) Each photograph is independently processed through depth estimation and plane detection;

(c) Measurements are combined using the confidence-weighted fusion method described in Section 6, Step 6;

(d) The system constructs a room polygon by combining the wall positions detected across all photographs.

### 7.4 Camera Offset Compensation

When a photograph is taken with the user's back near a wall, the camera measures the distance from the camera lens to the far wall, not the wall-to-wall distance. The present invention addresses this in several ways:

(a) **Perpendicular measurement preference.** For width measurements, the system uses photographs where the camera faces a side wall, allowing both opposing walls to be detected and measured. This provides a true wall-to-wall measurement regardless of camera position.

(b) **Floor-based triangulation.** The camera can observe the floor surface directly below and in front of the user. The closest floor point in the depth map establishes the camera's height above the floor, and the angle from the camera to the floor-wall junction behind the user can be used to estimate the camera's distance from the rear wall.

(c) **Known-object reference scaling.** If a tile of known dimensions is visible in the photograph (common during installation when sample tiles are present), the ratio of the known tile size to its apparent size in the depth map provides an absolute scale reference that can correct systematic depth bias.

(d) **Calibration-based correction.** Over time, as the user provides manual reference measurements alongside photographs, the system computes systematic correction factors for each measurement direction.

### 7.5 Out-of-Square Wall Detection and Handling

A significant practical advantage of the present system is automatic detection of non-square room geometry. Many residential rooms, particularly in older construction, have walls that are not perfectly parallel or perpendicular. The system detects this condition as follows:

(a) After detecting opposing wall planes via RANSAC, the system measures the distance between the planes at N sample points distributed along the room length (preferably N >= 10);

(b) At each sample point, the system selects inlier points from each plane within a spatial bin centered on the sample position and computes the median position along the measurement axis;

(c) If the standard deviation of the N distance measurements exceeds a threshold (preferably 0.5 inches / 1.3 cm), the system reports the walls as non-parallel;

(d) The minimum, maximum, and delta measurements are reported to the user;

(e) The tile layout engine uses the actual wall positions (not an assumed rectangular room) to compute tile cuts that account for the taper, ensuring proper fit along non-parallel walls.

### 7.6 Handling Obstructions and Complex Room Geometry

For rooms with obstructions (kitchen islands, columns) or complex geometry (L-shaped rooms, alcoves, shower enclosures with benches):

(a) The system detects multiple planes at different depths and orientations, constructing a more complex room polygon;

(b) For kitchen islands and similar obstructions, photographs from multiple angles allow the system to identify surfaces at intermediate depths that do not span the full room width, classifying them as obstructions rather than walls;

(c) The user may be prompted to capture additional photographs from specific angles if the system detects ambiguous geometry;

(d) For features that cannot be reliably detected from photographs (small outlets, drain positions, exact shower valve locations), the system allows the user to manually mark these features on the generated room plan in the companion application.

### 7.7 Tiling Boundary Specification for Open Floor Plans

In open-concept floor plans where tile does not extend to all visible room boundaries:

(a) After room geometry extraction, the system presents the detected floor polygon to the user in the companion application;

(b) The user defines the tiling boundary by adjusting edges of the polygon, drawing a custom boundary line, or specifying a transition type (straight line, diagonal, curved);

(c) The tile layout engine generates the tile pattern within the user-defined boundary, computing appropriate cut tiles along the custom boundary edge;

(d) Alternatively, the user may place a physical marker (such as painter's tape) along the intended boundary before capturing photographs. The system detects the marker in the image and automatically uses it as the tiling boundary.

### 7.8 Calibration and Accuracy Improvement System

The system includes a calibration mechanism for improving accuracy over time:

(a) The user may optionally provide known manual measurements (from a tape measure or laser distance meter) alongside photographs of the same room;

(b) The system computes the ratio of estimated-to-actual measurement for each dimension;

(c) Calibration data is stored in a persistent database on the device, accumulating across measurement sessions;

(d) After a sufficient number of calibration data points (preferably 10 or more rooms), the system computes optimal per-dimension correction factors using the median ratio across all calibration sessions;

(e) Subsequent measurements are automatically corrected using these factors;

(f) In a networked embodiment, calibration data from multiple users with the same camera model is aggregated on a cloud server, allowing the system to provide camera-model-specific correction factors that benefit from the collective measurement experience of all users of that camera model;

(g) This collective calibration mechanism creates a network effect: the more users employ the system, the more accurate it becomes for all users, particularly those with the same device model.

### 7.9 Automatic Detection of Fixed Constraints (Niches, Windows, and Other Features)

A critical innovation of the present system is the automatic detection and measurement of fixed surface features — such as shower niches, window openings, alcoves, shelves, and other recesses or protrusions — from the same photograph used for wall measurement. These features become "fixed constraints" in the tile layout engine, meaning the tile pattern must align to them rather than the other way around.

The feature detection method comprises:

(a) **Dominant wall plane identification.** After depth estimation, the system identifies the dominant flat surface (the wall to be tiled) by finding the depth value that represents the largest contiguous region of approximately constant depth. This is the "wall plane depth."

(b) **Depth anomaly detection.** The system identifies regions of the depth map that deviate significantly (preferably by more than 3 cm) from the wall plane depth. Regions deeper than the wall plane are classified as recesses (niches, alcoves). Regions shallower than the wall plane are classified as protrusions (shelves, countertop edges, cabinet fronts). Regions significantly deeper (more than 0.5 m beyond the wall plane) are classified as openings (windows, doors).

(c) **Rectangular region extraction.** Anomalous depth regions are segmented into connected components using flood-fill or equivalent algorithms. Each connected component is bounded by a rectangle, and the rectangle dimensions are refined using depth gradient analysis at the component boundaries to achieve sub-pixel edge localization.

(d) **Real-world dimension computation.** The pixel-space bounding rectangles are converted to real-world dimensions (in inches or centimeters) using the pinhole camera model at the wall plane depth. The position of each feature is computed relative to the wall edges (distance from left edge, distance from bottom edge).

(e) **Feature classification.** Detected features are classified by dimension and depth characteristics. For example: a recess 8-36 inches wide, 8-48 inches tall, and 1-8 inches deep is classified as a "shower niche." A recess larger than 24 inches in both dimensions and deeper than 12 inches is classified as an "alcove." A shallow protrusion wider than 24 inches and less than 6 inches tall is classified as a "shelf or ledge."

(f) **Closeup mode auto-detection.** When the user photographs a feature at close range (e.g., a niche that fills most of the frame), the system automatically detects this condition by comparing the center depth to the edge depths. In closeup mode, the surrounding wall is identified from the image edges rather than the center, and the feature is permitted to occupy up to 60% of the image area (compared to 25% in normal mode). This allows accurate measurement of individual features from dedicated closeup photographs.

(g) **Constraint output.** Each detected feature is output as a "fixed constraint" data structure containing: feature type, width, height, recess depth, position relative to wall edges, confidence level, and a flag indicating whether the feature requires grout line alignment (true for niches, false for windows).

### 7.10 Constraint-Aware Tile Layout Auto-Correction

When a tile installer begins placing tiles, small deviations between planned and actual tile positions are inevitable. The system includes a constraint-aware auto-correction mechanism that accounts for fixed features when adjusting the tile layout.

The auto-correction method comprises:

(a) **Constraint hierarchy.** The system distinguishes between fixed constraints (niches, drains, shower valves, window openings, thresholds) that cannot be moved and whose tile alignment is critical, and flexible constraints (wall edges, first tile position) that can accommodate small adjustments.

(b) **Offset detection.** When the system detects that a placed tile deviates from its planned position (either through the vision-based alignment system of the laser projector, or through user input), it calculates the offset vector.

(c) **Constraint checking.** Before applying any auto-correction (shifting the entire tile pattern to match the placed tile's actual position), the system checks whether the proposed shift would cause any fixed constraint to lose grout line alignment. For each fixed constraint, the system computes whether the feature's edges would still coincide with grout lines after the shift, using a tolerance threshold based on grout width (preferably 50% of the grout line width).

(d) **Three-outcome decision logic:**
   - **SAFE:** No fixed constraints are affected by the proposed shift. The system automatically adjusts the pattern.
   - **WARNING:** One or more fixed constraints would be affected. The system alerts the user and presents options: (i) reposition the tile to match the planned layout, (ii) keep the current tile position and accept the constraint misalignment, or (iii) adjust the constraint measurement.
   - **NO CONSTRAINTS:** No fixed constraints exist on the surface. The system freely auto-corrects to the first placed tile's position.

(e) **Measurement mismatch detection.** After 3 or more tiles have been placed, the system compares the cumulative actual tile width (plus grout) against the planned dimension. If the measurements diverge beyond a threshold, the system alerts the user to a possible measurement discrepancy before the error compounds further.

### 7.11 Integration with Laser Projection System

In the complete system embodiment, the camera-based measurement system operates in conjunction with the laser projection hardware described in the related provisional application:

(a) The user captures photographs of the work surface using the companion application;

(b) The system extracts room geometry and generates a tile layout as described herein;

(c) The tile layout vertex data is transmitted wirelessly to the laser projection device;

(d) The laser device projects the tile pattern onto the physical work surface at 1:1 scale;

(e) As the user installs tiles, the vision-based alignment system of the laser device (described in the related application) uses placed tile edges to continuously refine the projection accuracy;

(f) This creates a complete workflow from photograph to installed tile with no manual measurement or layout marking required.

---

## 8. CLAIMS

**Claim 1.** A method for determining the dimensions of a physical space for tile installation layout generation, the method comprising:
(a) receiving one or more digital photographs of the physical space captured by a standard RGB camera of a mobile computing device;
(b) processing each photograph through a monocular depth estimation neural network to generate a metric depth map assigning a distance value in meters to each pixel, the neural network producing per-pixel metric depth values without requiring detection of vanishing points, visible room corners, or geometric line intersections in the image;
(c) converting the metric depth map to a three-dimensional point cloud using a pinhole camera model;
(d) detecting one or more planar surfaces in the three-dimensional point cloud using an iterative random sample consensus (RANSAC) algorithm;
(e) classifying each detected planar surface by its normal vector direction as a floor, ceiling, or wall surface;
(f) computing room dimensions from the spatial relationships between detected planar surfaces; and
(g) generating a tile installation layout pattern within the computed room dimensions.

**Claim 2.** The method of claim 1, wherein computing room dimensions comprises measuring the distance between opposing detected wall planes to determine room width, and wherein the measurement is performed at multiple sample points along the room length to detect non-parallel wall conditions.

**Claim 3.** The method of claim 2, further comprising reporting non-parallel wall conditions to a user when the measured wall-to-wall distance varies by more than a predetermined threshold across the multiple sample points, and generating a tile layout with tapered tile cuts that account for the non-parallel condition.

**Claim 4.** The method of claim 1, wherein the one or more digital photographs comprise at least two photographs taken from substantially opposite positions within the physical space, and wherein the method further comprises selecting measurements for each dimension from the photograph with the highest detection confidence for that dimension.

**Claim 5.** The method of claim 1, further comprising transmitting the generated tile installation layout pattern wirelessly to a laser projection device that projects the tile pattern onto the physical surface at 1:1 scale.

**Claim 6.** The method of claim 1, wherein the monocular depth estimation neural network produces metric depth values with absolute scale without requiring LiDAR data, stereo image pairs, or manual camera calibration.

**Claim 7.** The method of claim 1, further comprising:
(a) receiving a known manual measurement of at least one dimension of the physical space;
(b) computing a correction factor as the ratio of the known measurement to the estimated measurement;
(c) storing the correction factor in a persistent calibration database; and
(d) applying accumulated correction factors to subsequent measurements to improve accuracy over time.

**Claim 8.** The method of claim 7, further comprising aggregating calibration data from multiple users on a networked server to compute camera-model-specific correction factors.

**Claim 9.** The method of claim 1, wherein the physical space is a single tiling surface, and wherein the method further comprises:
(a) identifying a dominant plane in the three-dimensional point cloud corresponding to the tiling surface;
(b) detecting boundary edges of the dominant plane where it terminates at adjacent perpendicular surfaces; and
(c) computing the surface width and height from the extent of the dominant plane within its boundary edges.

**Claim 10.** A method for determining the dimensions of a physical space for tile installation layout generation, the method comprising:
(a) presenting a measured room polygon to a user in a software application;
(b) receiving user input adjusting the boundary of the measured room polygon to define a tiling area that is a subset of the total room area; and
(c) generating a tile installation layout pattern within the user-defined tiling area.

**Claim 11.** The method of claim 10, wherein the user input defines a transition boundary where tile terminates and a different flooring material begins.

**Claim 12.** A system for automatic room measurement and tile installation layout generation, the system comprising:
(a) a mobile computing device with an RGB camera;
(b) a monocular depth estimation neural network model configured to process photographs from the RGB camera and produce metric depth maps;
(c) a geometric processing module configured to convert depth maps to three-dimensional point clouds, detect planar surfaces using RANSAC, classify surfaces as floor, ceiling, or wall, and compute room dimensions from detected surface positions;
(d) a tile layout generation engine configured to generate tile installation patterns from the computed room dimensions; and
(e) a wireless communication interface for transmitting generated tile layouts to a laser projection device.

**Claim 13.** The system of claim 12, wherein the geometric processing module is further configured to measure the distance between opposing wall planes at multiple sample points to detect and quantify non-parallel wall conditions.

**Claim 14.** The system of claim 12, further comprising a calibration module that stores ratios of known manual measurements to estimated measurements and applies accumulated correction factors to subsequent measurements.

**Claim 15.** The system of claim 14, wherein the calibration module aggregates calibration data from a plurality of users via a networked server to compute correction factors specific to a camera model of the mobile computing device.

**Claim 16.** The method of claim 1, further comprising:
(a) identifying a dominant wall plane in the metric depth map as the depth value representing the largest contiguous region of approximately constant depth;
(b) detecting depth anomaly regions where the depth deviates from the dominant wall plane depth by more than a predetermined threshold, wherein the depth anomaly detection operates on continuous depth values rather than edge-based or feature-point detection, enabling detection of features that lack sharp visual edges in the RGB image;
(c) classifying anomaly regions as recesses, protrusions, or openings based on depth relative to the wall plane;
(d) extracting bounding rectangles for each anomaly region and converting pixel coordinates to real-world dimensions using the pinhole camera model;
(e) generating fixed constraint data structures for each detected feature, including position relative to wall edges, feature dimensions, and a grout alignment requirement flag; and
(f) incorporating the fixed constraints into the tile layout generation such that the tile pattern aligns grout lines to the edges of features flagged as requiring grout alignment.

**Claim 17.** The method of claim 16, further comprising automatically detecting a closeup photography mode when the center depth of the image exceeds the edge depth by more than a predetermined threshold and the total depth range of the image is less than a predetermined value, and in closeup mode, identifying the wall plane from edge pixels of the image rather than center pixels, and permitting detected features to occupy a larger fraction of the image area.

**Claim 18.** The method of claim 16, further comprising refining the bounding rectangle of each detected feature using depth gradient analysis at the feature boundaries, wherein the gradient magnitude along rows and columns of the depth map is computed within a search region surrounding the initial bounding rectangle, and the boundary is adjusted to the pixel location of maximum depth gradient.

**Claim 19.** A method for constraint-aware auto-correction of a tile installation layout, the method comprising:
(a) maintaining a set of fixed constraints representing physical features of the tiling surface whose positions are predetermined and whose tile alignment is critical;
(b) detecting a deviation between a planned tile position and an actual placed tile position;
(c) computing a proposed pattern shift to align the tile layout with the actual placed tile position;
(d) for each fixed constraint, determining whether the proposed pattern shift would cause the feature's edges to lose alignment with grout lines of the tile pattern, using a tolerance threshold based on grout width, wherein the constraint checking operates in real-time during tile placement and accounts for both translational and rotational pattern adjustments; and
(e) selectively applying the pattern shift only when no fixed constraints lose grout alignment, or alerting the user and presenting correction options when one or more fixed constraints would be affected.

**Claim 20.** The method of claim 19, further comprising detecting measurement mismatch after a plurality of tiles have been placed by comparing the cumulative actual tile dimension including grout spacing against the planned dimension, and alerting the user when the cumulative deviation exceeds a predetermined threshold.

**Claim 21.** The method of claim 1, wherein the monocular depth estimation neural network is a vision transformer-based architecture that produces metric depth with absolute scale from a single RGB image without requiring LiDAR data, stereo image pairs, known camera intrinsic parameters, or detection of vanishing points or geometric line features in the image, thereby enabling room measurement from photographs taken at arbitrary angles and in rooms where corners, ceiling, or floor are partially or fully occluded by furniture or fixtures.

**Claim 22.** The method of claim 16, wherein the fixed constraint data structures are transmitted with the tile layout to a laser projection device, and the laser projection device visually distinguishes projected grout lines adjacent to fixed constraints from other grout lines using a different laser modulation pattern, alerting the installer to alignment-critical areas during physical tile placement.

---

## 9. ABSTRACT

A method and system for automatically extracting room dimensions and detecting fixed surface features from one or more standard photographs captured by a mobile phone camera, for the purpose of generating tile installation layouts. The system processes each photograph through a monocular depth estimation neural network to produce a metric depth map, converts the depth map to a three-dimensional point cloud, detects planar surfaces (walls, floor, ceiling) using iterative RANSAC plane fitting, and computes room dimensions from the spatial relationships between detected planes. The system further detects fixed surface features (niches, windows, alcoves, shelves) by identifying depth anomalies relative to the dominant wall plane, classifying features by type and dimension, and computing their positions relative to wall edges. The system detects non-parallel (out-of-square) wall conditions by measuring wall-to-wall distances at multiple points. Multiple photographs from different positions are combined using confidence-weighted fusion for improved accuracy. Detected fixed features become constraints in the tile layout engine, with a constraint-aware auto-correction system that prevents tile pattern adjustments from breaking grout alignment at critical features such as shower niches. The measured room geometry and detected features are used to automatically generate a tile installation layout, which may be transmitted wirelessly to a laser projection device for real-time on-surface installation guidance. A calibration system allows accuracy to improve over time through user-provided reference measurements, with optional network aggregation of calibration data across users and camera models.

---

## FILING CHECKLIST

### Before Filing (Claude handles these)
- [x] Draft specification with all technical details
- [x] Draft 22 claims covering full pipeline, feature detection, constraint-aware auto-correction, and prior art distinctions
- [x] Update with latest prototype results (single-wall scan bridge, closeup mode, feature detection)
- [ ] Convert this markdown to PDF for upload
- [ ] Generate system architecture diagram (Figure 1)
- [ ] Generate pipeline flowchart (Figure 2)
- [ ] Generate depth map + feature detection visualization example (Figure 3)
- [ ] Generate constraint-aware auto-correction flowchart (Figure 4)

### Filing Day (Robbie handles these)
- [ ] Create USPTO account at https://patentcenter.uspto.gov/ (requires identity verification)
- [ ] Insert inventor full legal name in Section 2
- [ ] Insert related application number and date in Section 3 (if laser patent already filed; otherwise mark as "to be filed concurrently")
- [ ] Log into Patent Center → New Submission → Provisional Application
- [ ] Upload specification PDF
- [ ] Upload figures PDF
- [ ] Select micro-entity status ($180 fee)
- [ ] Pay $180 via credit/debit card
- [ ] Click Submit
- [ ] Record the application number and filing date
- [ ] Calendar the 12-month deadline for utility conversion (March 2027 if filed March 2026)

### After Filing
- [ ] File the laser projection provisional separately ($180) if not already filed
- [ ] Begin building/testing toward utility patent conversion
- [ ] At month 10: use PowerPatent (~$199) to convert provisional → utility draft
- [ ] At month 11: file utility + Track One ($933 + ~$430 micro entity fees)
