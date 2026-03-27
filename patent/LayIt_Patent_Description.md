# UNITED STATES PATENT APPLICATION

---

## PROVISIONAL / UTILITY PATENT APPLICATION

> **Filing Notes:**
> - Sections 1-6 and 8 (Title, Field, Background, Summary, Drawings Description, Detailed Description, Abstract) are **required for provisional filing**.
> - Section 7 (Claims) is **optional for provisional** but strongly recommended. Claims are **required for utility filing**.
> - Drawings are **optional for provisional** but strongly recommended. They are **required for utility filing**. This document includes textual descriptions of recommended figures; formal patent drawings should be prepared by a patent illustrator.
> - **Strongly recommended**: Have a registered patent attorney or agent review this document before filing with the USPTO.

---

## 1. TITLE OF THE INVENTION

System and Method for Real-Time Laser Projection of Tile Installation Patterns with Vision-Based Self-Correcting Alignment

---

## 2. INVENTOR

Sole Inventor: [INVENTOR FULL LEGAL NAME]

---

## 3. FIELD OF THE INVENTION

The present invention relates generally to construction guidance tools, and more particularly to a system and method for projecting tile installation patterns onto work surfaces using galvanometer-steered laser projection, combined with a vision-based automatic alignment system that uses placed tile edges as self-reinforcing reference points for continuous real-time projection correction.

---

## 4. BACKGROUND OF THE INVENTION

### 4.1 Current State of the Art

Tile installation is one of the most labor-intensive and precision-demanding tasks in residential and commercial construction. Professional tile installers and do-it-yourself homeowners must accurately lay hundreds or thousands of individual tiles in precise geometric patterns on floors, walls, backsplashes, and shower enclosures. The quality of the finished installation depends critically on maintaining consistent spacing, alignment, and pattern continuity across the entire work surface.

### 4.2 Existing Methods and Their Limitations

**Manual Layout Methods.** The traditional approach to tile installation involves manual measurement and marking of reference lines using chalk lines, straightedges, tape measures, and pencils. The installer measures the work surface, calculates tile positions, snaps chalk lines to establish a grid, and lays tiles along these static reference marks. This process is time-consuming (often requiring 30-60 minutes of layout per surface), error-prone (cumulative measurement errors compound across the work area), and inflexible (any change to the pattern requires erasing and re-marking the entire layout).

**Laser Level Tools.** Existing laser tools for construction, such as cross-line laser levels and rotary laser levels, project one or two straight reference lines onto a surface. While useful for establishing level and plumb references, these tools cannot project complex tile patterns (such as herringbone, hexagonal, or brick-bond layouts), cannot account for wall irregularities (non-square corners, varying wall heights), and cannot dynamically update their projection based on actual tile placement. They require manual repositioning to cover different areas of a large surface.

**Computer-Aided Design Software.** Various software applications exist for designing tile layouts on a computer or tablet. However, these tools produce only a digital representation that must be manually transferred to the physical work surface through measurement and marking. The translation from digital design to physical layout introduces errors and requires significant time and skill.

**Industrial Laser Projection Systems.** Large-scale industrial laser projection systems (used in aerospace manufacturing, composite layup, and similar applications) exist but are prohibitively expensive (typically $20,000-$100,000+), require specialized training, are not designed for tile installation patterns, and lack the portability and ease of use required for construction job sites.

**Emerging Construction Laser Projection.** Recently, several companies have introduced laser projection systems targeted at construction applications (e.g., Mechasys XR Projector, LightYX BeamerOne). These systems project pre-loaded templates or CAD drawings onto surfaces for general construction marking — framing layouts, plumbing rough-in positions, HVAC duct locations, and similar tasks. However, these systems are designed for generic template projection and lack tile-specific capabilities: they do not compute tile patterns from user-specified tile dimensions and grout spacing, do not generate cut tile dimensions at boundaries, do not support tile-specific pattern types (herringbone, hexagonal, brick-bond), and critically, do not include vision-based self-correcting alignment that uses the edges of physically placed tiles as reference points. Their alignment methods rely on pre-placed fiducial markers, QR codes, or manual calibration rather than leveraging the installed work product itself as a continuously improving reference grid.

### 4.3 Unmet Needs

There exists a need for a compact, affordable, and easy-to-use system that can:

(a) Allow a user to digitally design a tile layout pattern on a smartphone or tablet, including support for multiple tile shapes, sizes, and pattern types;

(b) Wirelessly transmit the designed pattern to a portable hardware device;

(c) Project the full tile pattern as visible laser lines onto the actual work surface at 1:1 scale in real-time;

(d) Automatically detect and correct for projection errors caused by device positioning, surface angle, and distance variations;

(e) Use already-placed tiles as reference points for self-correcting alignment that improves in accuracy as the installation progresses;

(f) Automatically recover from accidental device displacement (bumps or repositioning) without requiring manual recalibration;

(g) Support large work areas by segmenting the projection into manageable zones with guided sequencing; and

(h) Track installation progress including cut tile management and measurement display.

### 4.4 Distinction from Prior Art

The present invention is distinguished from existing and emerging laser projection systems in several fundamental respects:

(a) **Tile-specific pattern computation.** Unlike generic laser template projectors that display pre-loaded CAD files or DXF templates, the present system computes tile layouts in real-time from user-specified parameters (tile dimensions, grout width, pattern type, brick-bond offset). The system generates all tile vertex coordinates, computes cut tile dimensions at boundaries and around obstacles, and optimizes pattern placement to minimize waste — functionality that has no equivalent in generic projection systems.

(b) **Self-reinforcing vision alignment from placed tiles.** Existing construction laser projectors maintain alignment through pre-placed fiducial markers, QR code targets, or periodic manual recalibration. The present invention uniquely uses the edges of tiles already placed by the installer as reference points for continuous alignment correction. Because each placed tile adds four new high-precision reference corners, the system's accuracy improves monotonically as the installation progresses — a property absent from all known prior systems.

(c) **Grout line projection.** The present system projects individual grout lines as part of the tile pattern, showing the installer exactly where each grout joint falls. Generic construction projectors project outlines of templates or room features but do not compute or display grout line positions, which are critical for tile alignment.

(d) **Cut tile management.** The companion application automatically identifies tiles that intersect work surface boundaries or void regions, computes precise cut dimensions from the intersection geometry, and provides a tracking system for marking tiles through pending, selected, and completed states. This tile-installation-specific workflow management has no equivalent in generic projection tools.

(e) **Integration with camera-based room measurement.** In a complete system embodiment described in the related application, the present system receives tile layouts generated from automatic camera-based room geometry extraction, creating an end-to-end workflow from room photograph to projected tile pattern with no manual measurement required.

---

## 5. SUMMARY OF THE INVENTION

The present invention provides a tile installation guidance system comprising three integrated components: (1) a companion software application executing on a mobile computing device, (2) a portable laser projection hardware device, and (3) an optional cloud synchronization service for multi-device collaboration.

The companion application allows a user to define a work surface geometry (including irregular wall shapes, non-square corners, and void regions such as windows and outlets), select a tile type and pattern (including hexagonal, herringbone, square, and rectangular configurations with adjustable grout spacing and brick-bond offsets), and generate a complete tile layout with automatically computed cut dimensions for partial tiles at boundaries and around obstacles.

The laser projection device receives the tile layout data wirelessly from the companion application via a WiFi connection and WebSocket protocol. A dual-core microcontroller processes the tile vertex coordinates and drives a dual-axis galvanometer mirror system through a digital-to-analog converter and analog signal conditioning circuit. A visible laser beam (preferably 520nm green, 200mW) is steered by the galvanometer mirrors to trace the tile outlines onto the work surface at 1:1 scale. The laser is modulated via TTL blanking to draw only the tile edges, with the beam blanked (turned off) during repositioning movements between disconnected line segments.

A key innovation of the present invention is the vision-based self-correcting alignment system. An onboard wide-angle camera captures images of the work surface during projection. Rather than requiring external fiducial markers, calibration targets, or manual alignment procedures, the system detects the edges of tiles that have already been physically placed by the installer. Using computer vision techniques including edge detection, contour extraction, sub-pixel corner refinement, and homography computation with RANSAC outlier rejection, the system continuously computes a perspective transformation matrix that maps the camera's view of placed tiles to the known tile layout coordinates. This transformation is applied in real-time to correct the projected pattern for the device's actual position, angle, and distance relative to the work surface.

Critically, this approach creates a self-reinforcing reference grid: each tile placed by the installer adds four new high-precision reference corners to the alignment computation. The system's accuracy therefore improves monotonically as the installation progresses, from approximately plus or minus 2-3 millimeters at cold start (using wall edge detection only) to less than 0.3 millimeters after 25 or more tiles have been placed. Because the alignment is recomputed from scratch on every camera frame using all currently visible placed tiles, errors do not accumulate over time; this provides absolute positioning rather than relative positioning.

An inertial measurement unit (IMU) provides supplementary bump detection. If the device is accidentally displaced during use, the IMU detects the motion event within milliseconds and triggers an immediate re-alignment cycle using the camera-based system, allowing seamless recovery without any user intervention or manual recalibration.

For large work surfaces that exceed the projection coverage of the galvanometer system, the system automatically segments the work area into a grid of projection zones and guides the installer through a sequential path (serpentine for floor installations, bottom-up for wall installations) to ensure complete coverage.

The system further includes multiple safety features: a hardware interlock switch on the enclosure lid that disables the laser via hardware interrupt when the enclosure is opened, firmware-enforced safety checks at multiple levels (interrupt service routine, main loop, and scan loop), and automatic laser timeout after a configurable period of communication inactivity.

In a preferred embodiment designated the "Pro" model, the system further comprises a dual-power architecture with automatic switchover between a corded 12V DC power supply and a swappable rechargeable lithium polymer battery pack, enabling both corded and cordless operation.

---

## 6. BRIEF DESCRIPTION OF THE DRAWINGS

The following drawings are recommended for inclusion with this application. Formal patent drawings should be prepared by a qualified patent illustrator.

**FIG. 1** is a system architecture block diagram showing the three major components of the tile installation guidance system: the companion application on a mobile device, the laser projection hardware device, and the cloud synchronization service, with wireless communication paths indicated between them.

**FIG. 2** is a hardware signal path diagram showing the complete electronic signal chain from the microcontroller through the digital-to-analog converter, operational amplifier buffer, galvanometer driver, galvanometer mirrors, and laser module, including the TTL blanking control path through the MOSFET switch.

**FIG. 3** is a block diagram of the ESP32-S3 microcontroller pin assignments showing all GPIO connections to peripheral components including the DAC, camera, IMU, laser driver, safety interlock, status LED, and USB interface.

**FIG. 4** is a power distribution schematic showing the 12V input, reverse polarity protection, overcurrent protection, and cascaded voltage regulation to the 5V and 3.3V rails, with all powered components indicated on their respective rails.

**FIG. 5** is a flowchart of the galvo scanning algorithm showing the coordinate transformation pipeline from tile vertex coordinates (in inches) through segment-relative translation, DAC scaling, center offset, and clamping to produce 12-bit galvanometer drive values.

**FIG. 6** is a diagram of the scan buffer construction process showing how tile vertex coordinates are converted to a sequential list of scan points with laser-on and laser-off (blanking) states, including corner dwell points and line interpolation points.

**FIG. 7** is a flowchart of the vision-based alignment pipeline showing the nine-stage process: image capture, preprocessing, Canny edge detection, contour extraction, corner refinement, tile matching, homography computation, projection correction, and confidence scoring.

**FIG. 8** is a diagram illustrating the self-reinforcing reference grid concept, showing progressive improvement in alignment accuracy as tiles are placed: from cold start with wall edge detection (2-3mm accuracy), through single-tile reference (1-2mm), through multi-tile reference (less than 0.5mm), to full grid reference (less than 0.3mm).

**FIG. 9** is a state diagram of the alignment confidence system showing transitions between INITIALIZING, LOCKED (green), CORRECTING (yellow), DISRUPTED (orange), LOST (red), and PAUSED states, with trigger conditions for each transition.

**FIG. 10** is a flowchart of the bump recovery process showing the IMU-triggered detection, camera re-alignment, and automatic recovery sequence for minor bumps, full device repositioning, and mid-placement displacement events.

**FIG. 11** is a diagram of the segment grid system showing how a large work surface is divided into projection zones, with serpentine path ordering for floor mode and bottom-up ordering for wall mode.

**FIG. 12** is a screen capture or mockup of the companion application user interface showing the tile pattern design view with wall dimensions, tile configuration, void regions, and cut tile detail views.

**FIG. 13** is a diagram of the WebSocket communication protocol showing the message types exchanged between the companion application and the projection device, including pattern loading, segment selection, projection control, alignment status updates, and safety notifications.

**FIG. 14** is a circuit diagram of the laser TTL blanking driver showing the MOSFET switching circuit with level translation from 3.3V GPIO to 12V TTL output.

**FIG. 15** is a schematic of the safety interlock system showing the microswitch, pull-up resistor, GPIO connection, and interrupt-driven emergency stop path.

**FIG. 16** is a block diagram of the Pro model dual-power system showing the automatic switchover between corded DC power and battery power, including the battery management system, charging circuit, and priority diode circuit.

**FIG. 17** is a diagram of the four supported tile pattern types: hexagonal (pointy-top and flat-top orientations), herringbone (45-degree alternating rotation), and rectangular with brick-bond offset variations (0%, 33%, 50%, 67%).

**FIG. 18** is a diagram illustrating the cut tile detection and dimension calculation process, showing wall boundary intersection, void notch detection, and the resulting cut dimensions displayed to the user.

---

## 7. DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENT

The following description sets forth the preferred embodiment of the present invention with sufficient detail to enable a person having ordinary skill in the art to make and use the invention. It is understood that various modifications and adaptations will be apparent to those skilled in the art without departing from the spirit and scope of the invention as defined by the appended claims.

### 7.1 SYSTEM ARCHITECTURE OVERVIEW

Referring to FIG. 1, the tile installation guidance system of the present invention comprises three integrated components that work together to guide a user through a complete tile installation:

**(a) Companion Application (Software Component).** A Progressive Web Application (PWA) executing on a user's smartphone, tablet, or computer. The application provides a graphical interface for designing tile layouts, configuring projection parameters, controlling the hardware device, and tracking installation progress. The application communicates with the hardware device via WiFi and with the cloud service via the internet.

**(b) Laser Projection Device (Hardware Component).** A portable electro-optical device comprising a microcontroller, digital-to-analog converter, operational amplifier, dual-axis galvanometer mirror assembly, visible laser source, camera, inertial measurement unit, safety systems, and power management circuitry. The device receives tile layout data from the companion application and projects visible laser outlines of tile positions onto the work surface at 1:1 scale.

**(c) Cloud Synchronization Service (Network Component).** An optional cloud-based database service that enables multiple devices to share project data using a passphrase-based pairing mechanism. This allows, for example, a user to design a tile layout on a tablet at a desk and then access the same project on a phone at the job site.

#### 7.1.1 End-to-End Workflow

The system is used in the following general workflow:

**Step 1 — Surface Measurement.** The user measures the work surface (wall or floor) and enters dimensions into the companion application, including overall width and height, any irregularities (non-square corners, varying heights), and the locations and sizes of void regions (windows, electrical outlets, shower niches, cabinets, or other obstacles).

**Step 2 — Pattern Design.** The user selects a tile shape (hexagonal, herringbone, square, or rectangular), enters tile dimensions and grout spacing, chooses a pattern orientation and brick-bond offset, and optionally runs an automatic optimization algorithm that adjusts the pattern position to minimize the number of cut tiles or avoid small slivers.

**Step 3 — Device Positioning.** The user places the projection device on a tripod or flat surface aimed at the work area. The device creates a WiFi access point, and the user connects the companion application to the device wirelessly.

**Step 4 — Calibration.** The device projects a calibration square of known size (default 12 inches). The user verifies the projected size with a tape measure and adjusts the projection distance parameter if necessary.

**Step 5 — Projection.** The user selects a segment (projection zone) in the companion application and initiates projection. The device projects the tile outlines for that segment onto the work surface as visible laser lines.

**Step 6 — Installation with Live Alignment.** As the user places tiles along the projected laser lines, the device's camera detects the placed tile edges and continuously refines the projection alignment. The companion application displays an alignment confidence indicator. The user proceeds through segments in the guided sequence until the entire surface is covered.

**Step 7 — Cut Management.** For tiles at boundaries and around voids, the companion application displays precise cut dimensions (in inches and fractions) and tracks which tiles have been cut and placed.

### 7.2 TILE PATTERN GENERATION AND COORDINATE SYSTEM

The companion application implements a tile pattern generation engine that computes the vertex coordinates of every tile in the layout based on user-specified parameters. All coordinates are computed in inches with the origin at the bottom-left corner of the work surface.

#### 7.2.1 Supported Tile Patterns

Referring to FIG. 17, the system supports four distinct tile pattern types, each with its own geometry and spacing algorithm:

**Hexagonal Tiles — Pointy-Top Orientation.** Each tile is a regular hexagon with vertices at the top and bottom (pointy-top configuration). For a hexagonal tile of width `tw` (measured flat-to-flat) and height `th` (measured point-to-point), the six vertices of a tile centered at position (cx, cy) are computed as:

    Vertex 0: (cx, cy - th/2)           [top point]
    Vertex 1: (cx + tw/2, cy - th/4)    [upper right]
    Vertex 2: (cx + tw/2, cy + th/4)    [lower right]
    Vertex 3: (cx, cy + th/2)           [bottom point]
    Vertex 4: (cx - tw/2, cy + th/4)    [lower left]
    Vertex 5: (cx - tw/2, cy - th/4)    [upper left]

Column spacing is computed as `colSp = tw + grout` and row spacing as `rowSp = th * 0.75 + grout`. Even-numbered rows receive a horizontal offset of `colSp / 2` to produce the characteristic honeycomb stagger.

**Hexagonal Tiles — Flat-Top Orientation.** Each tile is a regular hexagon with flat edges at the top and bottom. For a tile of width `w` and height `h`, the six vertices centered at (cx, cy) are:

    Vertex 0: (cx - w/4, cy - h/2)      [upper left]
    Vertex 1: (cx + w/4, cy - h/2)      [upper right]
    Vertex 2: (cx + w/2, cy)            [right point]
    Vertex 3: (cx + w/4, cy + h/2)      [lower right]
    Vertex 4: (cx - w/4, cy + h/2)      [lower left]
    Vertex 5: (cx - w/2, cy)            [left point]

Column spacing is `colSp = th * 0.75 + grout` and row spacing is `rowSp = tw + grout`. Even-numbered columns receive a vertical offset of `rowSp / 2`.

**Herringbone Pattern.** Rectangular tiles are placed at alternating 45-degree and negative-45-degree rotations to form a zigzag pattern. For a tile of long dimension `lg` and short dimension `sm`, the column spacing is `colSp = lg * 0.5 * sqrt(2)` and the row spacing is `rowSp = sm * sqrt(2)`. Odd-numbered columns receive a vertical offset of `rowSp / 2`.

Each tile's rectangular vertices are first computed at the origin and then rotated by the appropriate angle using the standard rotation transformation:

    x' = x * cos(theta) - y * sin(theta)
    y' = x * sin(theta) + y * cos(theta)

where theta is +45 degrees for even columns and -45 degrees for odd columns (or the inverse, depending on the user's selected orientation). A 2:1 aspect ratio is recommended for herringbone patterns (e.g., 2 inches by 4 inches, 3 inches by 12 inches).

**Square and Rectangular Tiles with Brick-Bond Offset.** Standard rectangular tiles are arranged in a grid with configurable offset (stagger) of alternating rows. The system supports four offset levels:

    0%  — Stack bond (no offset, tiles aligned in a grid)
    33% — One-third offset
    50% — Running bond (half offset, standard brick pattern)
    67% — Two-thirds offset

For odd-numbered rows, the horizontal position is shifted by `colSpacing * offsetFraction`. Both portrait (tall) and landscape (wide) orientations are supported.

#### 7.2.2 Grout Spacing

Grout spacing is configurable in the companion application and is factored into all spacing calculations. Common grout widths include 1/16 inch (0.0625), 1/8 inch (0.125), and 1/4 inch (0.25). The grout width is added to the tile dimension when computing the center-to-center spacing between adjacent tiles:

    columnSpacing = tileWidth + groutWidth
    rowSpacing = tileHeight + groutWidth

(Modified for hexagonal and herringbone patterns as described above.)

#### 7.2.3 Stable Tile Identification

Each tile in the layout is assigned a persistent identification key based on its computed position in inches, rounded to three decimal places:

    tileKey = round(tileXInches * 1000) + "," + round(tileYInches * 1000)

This key remains stable across zoom, pan, and pattern repositioning operations and is used to persist tile cut states (pending, selected, completed) across user sessions.

#### 7.2.4 Wall Boundary Intersection

The work surface is defined as a polygon (quadrilateral for standard rectangular surfaces, or an arbitrary polygon for irregular surfaces drawn by the user). Tile visibility relative to the wall boundary is determined using a ray-casting point-in-polygon test:

For each tile, the system evaluates whether each vertex lies inside the wall polygon. A tile is classified as:
- **Full tile**: All vertices inside the wall polygon
- **Cut tile**: Some vertices inside and some outside (tile crosses the wall boundary)
- **Outside tile**: No vertices inside the wall polygon (not rendered)

For cut tiles, the system computes the intersection points between each tile edge and each wall edge using parametric line-line intersection:

Given line segment P1-P2 and line segment P3-P4, the intersection parameter t is:

    t = ((P1.x - P3.x)(P3.y - P4.y) - (P1.y - P3.y)(P3.x - P4.x)) /
        ((P1.x - P2.x)(P3.y - P4.y) - (P1.y - P2.y)(P3.x - P4.x))

An intersection exists if both t and the corresponding parameter u are in the range [0, 1]. The resulting intersection points, combined with tile vertices that lie inside the wall, define the cut tile shape. These points are ordered by angle from their centroid to form a proper convex polygon.

#### 7.2.5 Void Region Handling

Void regions (windows, electrical outlets, shower niches, cabinets, or other obstacles) are defined as rectangular regions within the wall polygon. Each void is specified by its position (x, y) and dimensions (width, height) in inches.

A tile is classified as touching a void if any tile vertex lies inside the void polygon, or if any void corner lies inside the tile polygon. A tile is fully inside a void (and therefore not rendered) if all tile vertices lie inside a single void polygon.

For tiles that partially overlap a void, the system computes notch dimensions: the width and height of the rectangular region that must be removed from the tile, along with the corner designation (top-left, top-right, bottom-left, or bottom-right) indicating the location of the notch.

#### 7.2.6 Pattern Optimization

The companion application includes an automatic optimization algorithm that adjusts the horizontal and vertical offset of the entire tile grid to achieve the best placement. The algorithm evaluates candidate offsets from 0 to the tile width (and height) in steps of one-eighth tile width, scoring each position according to one of three selectable criteria:

- **Maximize Full Tiles**: Score = (full tile count * 100) - (cut tile count * 10)
- **Avoid Small Slivers**: Score = -(small cut count * 100) + (full tile count * 10)
- **Balanced**: Score = (full tile count * 50) - (cut tile count * 5) - (small cut count * 100)

The position with the highest score is recommended to the user.

### 7.3 HARDWARE SIGNAL PATH

Referring to FIG. 2, the laser projection device implements the following signal chain to convert digital tile coordinates into physical laser beam positions on the work surface:

#### 7.3.1 Microcontroller

The preferred embodiment uses an ESP32-S3-WROOM-1 (N16R8) system-on-module, which provides a dual-core Xtensa LX7 processor running at 240 MHz, 16 MB of flash memory, 8 MB of quad-SPI PSRAM, integrated WiFi (802.11 b/g/n) and Bluetooth Low Energy, native USB support (CDC and JTAG), a camera DVP (Digital Video Port) interface for 8-bit parallel camera data, SPI peripherals, I2C bus, and sufficient GPIO pins for all peripheral connections.

Referring to FIG. 3, the microcontroller GPIO assignments in the preferred embodiment are as follows:

    GPIO1:  I2C SDA (camera SCCB + IMU)
    GPIO2:  I2C SCL (camera SCCB + IMU)
    GPIO4:  Camera VSYNC (frame sync)
    GPIO5:  Camera HREF (line valid)
    GPIO6:  Camera PCLK (pixel clock)
    GPIO7:  Camera XCLK (20 MHz reference clock output)
    GPIO8:  Camera D6
    GPIO9:  Camera D7
    GPIO10: SPI chip select (DAC, active low)
    GPIO11: SPI MOSI (DAC serial data)
    GPIO12: SPI clock (DAC)
    GPIO13: DAC LDAC (simultaneous latch, active low)
    GPIO14: Laser TTL control (via MOSFET)
    GPIO15: Camera D2
    GPIO16: Camera D3
    GPIO17: Camera D4
    GPIO18: Camera D5
    GPIO19: USB D- (native USB)
    GPIO20: USB D+ (native USB)
    GPIO45: Camera D8
    GPIO46: Camera D9
    GPIO47: Safety interlock input
    GPIO48: Status LED data (WS2812B)

The dual-core architecture is utilized to separate time-critical projection scanning from network and vision processing:

- **Core 0** handles WiFi communication, WebSocket message processing, HTTP server, vision system image processing, and non-time-critical housekeeping tasks.
- **Core 1** is dedicated to the real-time galvanometer scan loop, which must maintain consistent point-to-point timing to avoid visible flicker or distortion in the projected pattern.

A mutex-protected shared data structure allows Core 0 to update the scan buffer and homography correction matrix while Core 1 continuously reads and projects the current buffer.

#### 7.3.2 Digital-to-Analog Converter

The preferred embodiment uses a Microchip MCP4822 dual-channel 12-bit digital-to-analog converter (DAC). The MCP4822 provides two independent analog output channels (Channel A for galvo X-axis, Channel B for galvo Y-axis) with an internal 2.048V voltage reference and selectable 1x or 2x gain.

Communication with the microcontroller uses the SPI (Serial Peripheral Interface) protocol at 10 MHz clock speed. The SPI configuration is Mode 0,0 (CPOL=0, CPHA=0).

Each DAC channel is written with a 16-bit command word:

    Bit 15:     Channel select (0 = Channel A / X-axis, 1 = Channel B / Y-axis)
    Bit 14:     Buffered reference (1 = use internal buffered reference)
    Bit 13:     Gain select (0 = 2x gain for 0-4.096V output, 1 = 1x for 0-2.048V)
    Bit 12:     Shutdown control (1 = channel active, 0 = channel shutdown)
    Bits 11-0:  12-bit data value (0-4095)

With 2x gain and the internal 2.048V reference, each channel produces an output voltage range of 0 to 4.096V with a resolution of 1 millivolt per step (4.096V / 4096 steps).

A critical feature of the MCP4822 is the LDAC (Latch DAC) pin, which allows both channels to be written sequentially and then latched simultaneously. This ensures that the X and Y galvanometer positions are updated at the exact same instant, preventing any axis skew or diagonal artifacts during coordinate transitions. The latching sequence is:

    1. Hold LDAC high (prevent latching)
    2. Write Channel A (X-axis) via SPI (1.6 microseconds at 10 MHz)
    3. Write Channel B (Y-axis) via SPI (1.6 microseconds)
    4. Pulse LDAC low for at least 100 nanoseconds
    5. Return LDAC high

Total time per coordinate update: approximately 4 microseconds, yielding a theoretical maximum of 250,000 points per second (far exceeding the 20,000 points per second galvanometer specification).

#### 7.3.3 Operational Amplifier Buffer and Scaling

The DAC output (0-4.096V) is conditioned by a TL072 dual operational amplifier configured as a non-inverting amplifier. The TL072 is a JFET-input dual op-amp chosen for its high input impedance (which avoids loading the DAC), low noise (important for clean galvo signals where electrical noise translates to visible line wobble), wide availability, and low cost.

In the preferred embodiment, the op-amp is configured with:

    Input resistor R5 (R7 for channel B): 10K ohms
    Feedback resistor R6 (R8 for channel B): 24K ohms
    Gain = 1 + (R_feedback / R_input) = 1 + (24K / 10K) = 3.4x

This scales the 0-4.096V DAC output to approximately 0-13.9V, though in practice the output is limited to approximately 0-10V by the 12V supply rail saturation. The op-amp is powered from the +12V rail (V+) and ground (V-) in a single-supply configuration.

It is noted that the specific gain and supply configuration may be adjusted based on the input requirements of the particular galvanometer driver board used. Some galvanometer drivers accept 0-5V single-ended input, while others require plus or minus 5V differential input. The engineer may substitute a split-supply configuration (using a charge pump IC to generate a negative voltage rail) if the galvanometer driver requires bipolar input signals.

#### 7.3.4 Galvanometer Mirror Assembly

The projection device uses a dual-axis galvanometer scanner set rated at 20,000 points per second (20K PPS). Each galvanometer consists of a small mirror mounted on a limited-rotation motor shaft. The X-axis galvanometer steers the laser beam horizontally, and the Y-axis galvanometer steers the beam vertically.

The galvanometer driver board accepts analog voltage input from the operational amplifier and drives the galvanometer motors with closed-loop position control. The scan angle range is approximately plus or minus 20 degrees from center, corresponding to a projection coverage of:

    coverage_inches = distance_feet * 12 * 2 * tan(20 degrees)
    coverage_inches = distance_feet * 12 * 0.728

At a typical working distance of 6 feet, the projection coverage is approximately 54.2 inches (approximately 4.5 feet) in both the horizontal and vertical directions.

#### 7.3.5 Laser Module

The preferred embodiment uses a 520nm (green) direct-diode laser module with 200 milliwatt output power, 12V DC operating voltage, and TTL (Transistor-Transistor Logic) modulation capability at 15 kHz. The 520nm green wavelength is chosen for high visibility in typical indoor lighting conditions.

The laser is a direct-diode type (not a 532nm DPSS/frequency-doubled type), which provides faster TTL response, better temperature stability, and the ability to operate at low temperatures. The dot-pattern output (not line or cross) is essential because the galvanometer mirrors steer a single point of light to trace the tile outlines.

The 200mW power level provides visible lines in well-lit rooms at distances up to 8-10 feet. This power level places the laser in the Class 3B category per FDA/CDRH regulations (21 CFR 1040.10), requiring appropriate safety measures as described in Section 7.9.

#### 7.3.6 Laser TTL Blanking Circuit

Referring to FIG. 14, the laser is turned on and off (blanked) during scanning to draw only the desired tile outlines and suppress the beam during repositioning movements between disconnected line segments. The blanking circuit uses a 2N7000 N-channel MOSFET in the following configuration:

    ESP32 GPIO14 --[100 ohm resistor R10]--> 2N7000 Gate
    2N7000 Drain --[4.7K ohm pull-up resistor R9 to +12V]--> Laser TTL input
    2N7000 Source --> Ground

The logic is inverted:
- When GPIO14 is LOW, the MOSFET is OFF, the pull-up resistor holds the laser TTL input at +12V (HIGH), and the laser is ON.
- When GPIO14 is HIGH, the MOSFET is ON, it sinks the laser TTL input to ground (LOW), and the laser is OFF.

The firmware accounts for this inversion. The 2N7000 provides level translation from 3.3V GPIO to 12V TTL, with switching times on the order of 10 nanoseconds (approximately 1000 times faster than the 15 kHz TTL modulation rate of the laser).

The 100-ohm gate resistor limits ringing, and the 4.7K pull-up resistor provides a clean 12V high state when the MOSFET is off.

### 7.4 GALVANOMETER SCANNING ALGORITHM

Referring to FIGS. 5 and 6, the galvanometer scanning algorithm converts tile vertex coordinates (expressed in inches) into a sequential buffer of scan points that drive the galvanometer mirrors and laser blanking in real-time.

#### 7.4.1 Coordinate Transformation

The coordinate transformation from tile layout coordinates to DAC output values proceeds as follows:

**Projection Mapping.** Given the projection distance in feet (default 6.0 feet, configurable by the user), the system computes the projection coverage in inches:

    coverageInches = distance_feet * 12 * 0.728

And the conversion factor from inches to DAC units:

    inchesToDac = DAC_RESOLUTION / coverageInches

where DAC_RESOLUTION is 4096 (12-bit range). At 6 feet distance, this yields approximately 75.5 DAC units per inch.

**Segment-Relative Translation.** The current segment's origin coordinates (segmentX, segmentY) and any calibration offsets (originX, originY) are subtracted from the tile coordinate to obtain the position relative to the current projection viewport:

    relX = tileXInches - segmentX - originX
    relY = tileYInches - segmentY - originY

**DAC Scaling and Centering.** The relative position is scaled to DAC units and centered at the midpoint of the DAC range (2048 for 12-bit):

    dacX = DAC_CENTER + (relX * inchesToDac)
    dacY = DAC_CENTER + (relY * inchesToDac)

where DAC_CENTER = 2048.

**Range Clamping.** Any resulting DAC value outside the valid range of 0-4095 indicates that the point is outside the current projection area, and the point is excluded from the scan buffer.

#### 7.4.2 Scan Buffer Construction

The scan buffer is a sequential array of scan points, each comprising an X DAC value (16-bit unsigned), a Y DAC value (16-bit unsigned), and a laser-on boolean flag. The maximum buffer size in the preferred embodiment is 20,000 points.

For each tile that overlaps the current projection segment (determined by a bounding-box check with a 1-inch margin), the system adds scan points as follows:

**Move to First Vertex (Blanked).** Two blanked points (laser off) are output at the first vertex position to allow the galvanometer mirrors settling time before the laser turns on.

**Draw Outline.** For each successive vertex of the tile:
- **Corner Dwell Points.** Three repeated points at the exact corner position with the laser on. This creates a brighter corner, compensating for the fact that the galvanometer decelerates and reverses direction at corners, which would otherwise produce dimmer corners than straight segments.
- **Interpolated Line Points.** Between each pair of consecutive vertices, intermediate points are generated at regular spacing to ensure smooth galvanometer motion. The number of interpolation steps is calculated as:

        steps = euclideanDistance(vertex1, vertex2) / 50.0

    where the distance is in DAC units and 50 DAC units corresponds to approximately 1 degree of galvanometer angle. Each interpolated point is computed by linear interpolation:

        ix = x1 + (stepIndex / (steps + 1)) * (x2 - x1)
        iy = y1 + (stepIndex / (steps + 1)) * (y2 - y1)

**Close Shape.** The outline returns to the first vertex with corner dwell points and a final blanked point.

#### 7.4.3 Scan Loop Timing

The scan loop runs at the galvanometer's rated speed of 20,000 points per second. Two different timing delays are used:

- **Laser ON points** (visible drawing): 50 microseconds per point
- **Laser OFF points** (blanking/repositioning): 100 microseconds per point

The longer blanking delay allows the galvanometer mirrors additional settling time during repositioning movements, preventing visible artifacts at the start of each new line segment.

For a typical tile pattern containing 8,000-15,000 scan points, the complete scan buffer is traversed in approximately 0.5-1.5 seconds, yielding a refresh rate of approximately 0.67-2 Hz. While this is below the human flicker fusion frequency, the projected pattern appears as continuous static lines because the tile outlines do not change position.

### 7.5 VISION-BASED ALIGNMENT SYSTEM

Referring to FIGS. 7, 8, and 9, the vision-based alignment system is a key innovation of the present invention. It provides automatic, continuous correction of the projected pattern's position and orientation without requiring external calibration targets, fiducial markers, or manual alignment procedures.

#### 7.5.1 Camera Hardware

The preferred embodiment uses an OV5640 5-megapixel CMOS camera module with a 160-degree wide-angle lens. The camera connects to the microcontroller via an 8-bit DVP (Digital Video Port) parallel interface with the following signal lines:

- 8 data lines (D2-D9) for parallel pixel data
- VSYNC for frame synchronization
- HREF for line validity
- PCLK for pixel clock
- XCLK receiving a 20 MHz reference clock from the microcontroller
- I2C (SCCB protocol) for camera configuration register access

The camera operates at VGA resolution (640 by 480 pixels) for the vision pipeline, with dual framebuffers stored in the microcontroller's 8 MB PSRAM (approximately 614 KB total for two VGA grayscale frames). The wide-angle lens provides a large field of view to capture the maximum number of placed tiles for alignment reference.

#### 7.5.2 Processing Architecture

The vision pipeline runs on Core 0 of the dual-core microcontroller at a rate of 2 frames per second (one processing cycle every 500 milliseconds). This rate is deliberately chosen to balance processing load against alignment responsiveness. The total processing time per frame is approximately 50-80 milliseconds, consuming only about 16% of the available time budget per cycle.

The galvanometer scan loop continues to run uninterrupted on Core 1 throughout all vision processing. The homography correction matrix computed by the vision system is shared between cores via a mutex-protected data structure.

#### 7.5.3 Cold Start Procedure

When the projection device is first powered on and aimed at a bare work surface with no tiles placed, the system performs a cold start calibration:

**Primary Method — Wall/Corner Edge Detection.** The camera captures the work surface, and the system applies the following computer vision pipeline:

1. Convert image to grayscale
2. Apply Gaussian blur to reduce noise
3. Apply Canny edge detection to find high-contrast boundaries (the floor-to-wall interface, wall-to-ceiling interface, or wall corners)
4. Apply Hough line transform to identify straight lines in the edge map representing wall edges
5. Compute the intersection of perpendicular detected lines to locate the room corner

The detected corner position is presented to the user in the companion application for confirmation. The user may accept the detected corner as the projection origin or manually adjust it using on-screen controls.

**Fallback Method — Manual Crosshair Alignment.** If the system cannot reliably detect wall edges (e.g., due to poor lighting or lack of contrast), it projects a crosshair pattern at the center of the projection area. The user physically aligns the crosshair to a chosen starting point and confirms in the companion application. The system then locks the camera-to-projection mapping as the baseline.

Cold start accuracy is approximately plus or minus 2-3 millimeters, depending on wall edge quality and lighting conditions.

#### 7.5.4 Live Tile Edge Detection Pipeline

Once tile installation begins, the vision system transitions to its primary operating mode: live tile edge detection. This nine-stage pipeline runs continuously at 2 FPS:

**Stage 1 — Image Capture.** The OV5640 camera acquires a single VGA (640x480) frame. The frame is stored in a PSRAM framebuffer using dual-buffering (one buffer for the current capture, one for the previous frame being processed), ensuring that capture and processing can overlap.

**Stage 2 — Preprocessing.** The captured frame is converted to grayscale. An adaptive threshold is applied to compensate for varying lighting conditions across the work surface. A morphological closing operation fills small gaps in grout lines caused by recessed grout channels. The result is a binary image where tile edges appear as white lines against a black background.

**Stage 3 — Canny Edge Detection.** The Canny edge detection algorithm is applied with a 3x3 kernel, low threshold of approximately 50, and high threshold of approximately 150. This detects high-contrast transitions in the image, producing thin, continuous edge lines at tile boundaries. The system is resilient to low lighting because grout channels create depth and shadow contrast between adjacent tiles, and the laser reflection on the tile surface aids visibility.

**Stage 4 — Contour Extraction.** The `findContours()` operation extracts closed contours from the edge map. Contours are filtered to retain only quadrilateral shapes (4-sided polygons), with minimum area thresholds to reject noise particles and aspect ratio checks to reject elongated artifacts. The expected number of contours per frame is 1-25 tiles, depending on camera angle and the number of tiles visible in the field of view.

**Stage 5 — Sub-Pixel Corner Refinement.** For each detected tile contour, the four corner positions are refined to sub-pixel accuracy using the `cornerSubPix()` algorithm. This achieves positional accuracy of approximately 0.1-0.2 pixels. At a typical working distance of 6 feet with the 160-degree field of view, each pixel corresponds to approximately 0.3-0.4 millimeters; sub-pixel refinement therefore achieves less than 0.1 millimeter positional error per corner.

**Stage 6 — Tile Matching.** Each detected tile contour is matched to a tile in the known layout pattern. The matching algorithm computes the centroid (center point), width, height, and aspect ratio of each detected contour and compares these to the expected tile positions. A nearest-neighbor search with a distance threshold (rejecting outliers at greater than 2x the expected tile size) identifies the corresponding layout tile. Multi-tile context (considering adjacent detected tiles) is used for disambiguation when multiple possible matches exist.

The result of this stage is a set of matched pairs: (detected camera corner coordinates) mapped to (known layout corner coordinates).

**Stage 7 — Homography Computation.** From the matched corner pairs, the system computes a 3x3 homography matrix H using the `findHomography()` function with RANSAC (Random Sample Consensus) outlier rejection.

The homography matrix encodes the complete perspective transformation between the camera's view of the work surface and the known tile layout coordinate system. It implicitly captures:
- The device's position (X, Y, Z) relative to the work surface
- The device's orientation (rotation angles)
- Perspective distortion due to non-perpendicular mounting angle
- Horizontal and vertical scaling differences

The RANSAC implementation iteratively selects random 4-point subsets, fits a homography to each subset, counts inliers (points within a reprojection error threshold), and returns the model with the most inliers. This makes the computation robust to individual mis-detected tile corners.

Minimum input requirements:
- 4 corner points (1 detected tile) — functional but minimal
- 16 corner points (4 detected tiles) — good, outlier detection begins to operate
- 40+ corner points (10+ detected tiles) — excellent, RANSAC highly robust

**Stage 8 — Projection Correction.** The computed homography matrix is applied to all unprojected (not yet placed) tile vertex coordinates to correct their projected positions:

    corrected_galvo_point = H * layout_point

This transforms all tile vertices from the ideal layout coordinate space into the corrected coordinate space that accounts for the device's actual position and orientation. The corrected coordinates are used to rebuild the galvanometer scan buffer, and the projection updates in real-time without interruption.

**Stage 9 — Confidence Scoring.** The system computes a confidence score based on the reprojection error:

    For each matched corner:
        predicted_position = H * detected_camera_position
        actual_position = known_layout_position
        error = ||predicted - actual||

    average_error = mean(all errors)

The confidence score maps to a visual indicator displayed in the companion application:

    Average error < 0.5mm:   GREEN (LOCKED) — high confidence, accurate alignment
    Average error 0.5-2mm:   YELLOW (CORRECTING) — minor drift, auto-correcting
    Average error > 2mm:     RED (DISRUPTED) — unreliable, requires attention
    No tiles detected:       RED (LOST) — cannot compute homography

#### 7.5.5 Self-Reinforcing Reference Grid

A critical property of the present invention is that the alignment reference grid is self-reinforcing: it improves in both accuracy and robustness as the installation progresses. This is because each tile placed by the installer adds four new high-precision reference corners to the alignment computation.

The progressive accuracy improvement is as follows:

    0 tiles placed (cold start):    ~2 reference points (wall edges)     +-2-3mm accuracy
    1 tile placed:                  4 reference corners                   +-1-2mm accuracy
    4 tiles placed:                 16 reference corners                  +-0.5-1mm accuracy
    10 tiles placed:                40+ reference corners                 <0.5mm accuracy
    25+ tiles placed:               100+ reference corners                <0.3mm accuracy

For context, standard grout lines are 1.5-3 millimeters wide. Achieving less than 0.5 millimeter accuracy is therefore well within the acceptable tolerance for professional tile installation.

#### 7.5.6 Absolute Positioning

Unlike systems that accumulate corrections incrementally (where small errors in each correction step compound over time), the present invention recomputes the device-to-surface transformation from scratch on every camera frame using all currently visible placed tiles.

Frame N and Frame N+1000 use the identical algorithm with identical accuracy expectations. The system does not carry forward any state from previous alignment cycles except the set of tiles known to have been placed. This provides absolute positioning: the alignment accuracy at any point in time depends only on the number of visible reference tiles, not on the duration of operation or the number of previous corrections.

### 7.6 BUMP RECOVERY SYSTEM

Referring to FIG. 10, the bump recovery system provides seamless automatic recovery from accidental displacement of the projection device during use.

#### 7.6.1 Inertial Measurement Unit

The preferred embodiment includes a 6-axis IMU (MPU6050) connected to the microcontroller via I2C, sharing the bus with the camera's SCCB interface. The accelerometer is configured to detect acceleration spikes exceeding a threshold of 0.5g, indicating that the device has been physically moved.

#### 7.6.2 Recovery Scenarios

The system handles three displacement scenarios:

**Minor Bump (device shifts slightly but remains aimed at work surface).** The IMU detects an acceleration spike and immediately sets the alignment state to DISRUPTED. The companion application displays a warning ("Movement detected — verifying alignment"). Projection continues without interruption (the bump may have been minor enough that the pattern is still usable). The vision system runs an immediate re-alignment cycle. If the reprojection error is below the threshold, the corrected alignment is applied silently and the state returns to LOCKED. Total recovery time is approximately 1 second.

**Device Repositioned (picked up and moved to a new location).** The camera loses visibility of previously detected tiles (the device is pointed at a blank surface or ceiling during transit). The alignment state is set to LOST and projection pauses. When the user positions the device at the new location aimed at the work surface, the camera detects previously placed tiles from the new viewpoint. The system matches the detected tiles to the layout pattern, computes a new homography from the new perspective, and resumes projection with correct alignment. No user action in the companion application is required — recovery is fully automatic.

**Displacement During Tile Placement (worst case).** The IMU triggers an immediate warning ("Movement detected — hold tile placement"). The vision system re-aligns within approximately 1 second. The camera can detect whether a tile currently being placed is offset from its intended position. If the offset exceeds the grout line width, the companion application flags the tile for the user's review.

#### 7.6.3 Key Property

The user never needs to perform manual recalibration after a bump or device move. The already-placed tiles serve as permanent, immutable reference points that allow the system to re-establish accurate alignment from any viewpoint.

### 7.7 SEGMENTED LARGE-AREA PROJECTION

Referring to FIG. 11, for work surfaces larger than the projection coverage of the galvanometer system, the system automatically divides the work area into a grid of projection segments and guides the installer through a sequential path.

#### 7.7.1 Segment Grid Generation

The segment grid is computed by dividing the wall dimensions by the usable projection coverage (90% of the theoretical coverage, providing a safety buffer):

    usableCoverage = coverage * 0.9
    columns = ceil(wallWidth / usableCoverage)
    rows = ceil(wallHeight / usableCoverage)

Each segment is assigned a position (row, column), pixel bounds (x, y, width, height), a status (locked, ready, current, complete), and adjacency information (references to neighboring segments).

#### 7.7.2 Path Ordering

**Floor Mode — Serpentine Path.** Starting from the bottom-left corner (row 0, column 0), the path proceeds across the first row left-to-right, then reverses direction for the second row (right-to-left), and continues alternating. This serpentine pattern minimizes the distance the user must move the projection device between segments and ensures that the vision system always has previously placed tiles visible at the boundary between segments.

**Wall Mode — Bottom-Up Path.** For wall installations, the path proceeds from the bottom row upward, left-to-right within each row. This follows the natural tile installation order for walls (starting from the bottom and working up).

#### 7.7.3 Segment Navigation

The companion application provides a fullscreen projection view showing the current segment with navigation controls: previous segment, next segment, mark complete, and exit. A cut count badge indicates the number of tiles requiring cutting within the current segment.

The status progression for each segment is: locked (cannot be selected until previous segment is complete or adjacent) to ready (available for selection) to current (actively being projected) to complete (all tiles placed and cuts made).

### 7.8 WEBSOCKET COMMUNICATION PROTOCOL

Referring to FIG. 13, the projection device communicates with the companion application via a WebSocket connection over WiFi.

#### 7.8.1 Network Configuration

The projection device operates as a WiFi access point with a configurable SSID (default: "LayIt-Laser") and password. The companion application connects to this access point. The device runs two servers:

- An HTTP server on port 80 providing a status page and JSON status endpoint
- A WebSocket server on port 81 for real-time bidirectional communication

All messages are formatted as JSON text frames.

#### 7.8.2 Application-to-Device Messages

**load_pattern:** Transmits the complete tile layout including wall dimensions, tile parameters, void regions, and the vertex coordinates of all tiles. The device parses the JSON, stores the pattern data, computes the projection mapping, and builds the scan buffer. The device responds with a confirmation including the tile count and scan point count.

**set_segment:** Specifies the current projection segment by position (x, y) and dimensions (width, height) in inches. The device rebuilds the scan buffer to include only tiles within the specified segment.

**set_distance:** Updates the projection distance in feet. The device recalculates the inches-to-DAC conversion factor and rebuilds the scan buffer with the new scaling.

**start:** Initiates projection. The device enables the galvanometer scan loop and laser output, subject to safety interlock verification.

**stop:** Halts projection. The laser is disabled, and the galvanometer mirrors return to the center position.

**calibrate:** Commands the device to project a calibration square of specified size (default 12 inches) with a crosshair at the center, used for verifying projection distance and alignment.

**ping:** Keep-alive heartbeat. The device responds with a pong message.

#### 7.8.3 Device-to-Application Messages

The device sends status updates including: device identification and version information, pattern loading confirmation, projection state changes, alignment status updates (confidence level, error magnitude, reference tile count, homography matrix), safety stop notifications (interlock opened), and error messages.

#### 7.8.4 Communication Safety

The device tracks the timestamp of the most recent received message. If no message is received for 5 minutes (configurable), the device automatically disables the laser and halts projection, preventing unattended laser operation in the event of WiFi disconnection or companion application crash.

### 7.9 SAFETY SYSTEMS

Referring to FIG. 15, the projection device implements multiple layers of safety protection appropriate for a Class 3B laser device.

#### 7.9.1 Hardware Interlock

A normally-closed microswitch (SW3) is mounted on the enclosure lid. When the lid is closed, the switch connects GPIO47 to ground through a 10K pull-up resistor circuit. When the lid is opened, the switch opens, and the pull-up resistor pulls GPIO47 to the 3.3V logic level.

The microcontroller monitors GPIO47 via a hardware interrupt (ISR) configured for edge detection. When the lid is opened:

1. The interrupt service routine executes within microseconds
2. The ISR directly sets the laser TTL pin to the OFF state (GPIO14 HIGH)
3. The ISR sets the `laserEnabled` flag to false
4. The ISR sets the `safetyOK` flag to false

The ISR runs in IRAM (Instruction RAM) for the fastest possible execution time.

#### 7.9.2 Firmware Safety Checks

In addition to the hardware interrupt, the firmware implements redundant safety checks at three levels:

- **Interrupt Level:** ISR disables laser within microseconds of lid opening
- **Main Loop Level:** Every iteration of the main loop reads GPIO47 and verifies `safetyOK`
- **Scan Loop Level:** Every cycle of the scan loop checks `safetyOK` and `projecting` before outputting any laser-on scan point

This triple redundancy ensures that a single software fault cannot result in unintended laser operation.

#### 7.9.3 Emergency Stop

When a safety event occurs, the device executes an emergency stop sequence:

1. Laser turned off immediately
2. Projection halted
3. Laser enable flag cleared
4. Galvanometer mirrors returned to center position
5. Status LED set to red (error indication)
6. Safety stop notification sent to companion application via WebSocket

The laser cannot be re-enabled until the safety interlock reads the safe state (lid closed) and the user explicitly restarts projection from the companion application.

#### 7.9.4 Auto-Timeout

The device automatically disables the laser after a configurable period (default 5 minutes) of no communication from the companion application. This prevents unattended laser operation.

#### 7.9.5 Status LED

A WS2812B addressable RGB LED provides visual status indication:

    Slow green pulse:     Device ready, waiting for companion application connection
    Slow blue pulse:      Connected to companion application, idle
    Solid bright blue:    Actively projecting pattern
    Solid amber:          Calibrating
    Fast red blink:       Error or safety interlock open

### 7.10 POWER ARCHITECTURE

Referring to FIG. 4 and FIG. 16, the system supports two power configurations.

#### 7.10.1 Flagship Model — Corded Power

The Flagship model is powered by an external 12V 3A DC adapter through a 5.5mm x 2.1mm barrel jack connector. The power input is protected by:

- A Schottky diode (SS34, 3A 40V) for reverse polarity protection, dropping approximately 0.4V under load
- A resettable PTC fuse (3A hold current) for overcurrent protection
- A 470 microfarad 25V electrolytic capacitor for bulk input filtering, sized to handle galvanometer motor current transients

Voltage regulation is cascaded to minimize heat dissipation:

- First stage: AMS1117-5.0 LDO regulator converts 12V to 5V (powers DAC and op-amp)
- Second stage: AMS1117-3.3 LDO regulator converts 5V to 3.3V (powers microcontroller, camera, LED, I2C bus)

The 3.3V regulator is fed from the 5V rail rather than directly from 12V. This reduces heat dissipation in the 3.3V regulator from 6 watts (which would exceed the SOT-223 package thermal rating) to 1.2 watts (acceptable with a thermal pad).

#### 7.10.2 Pro Model — Dual Power

The Pro model adds a dual-power system comprising:

- A removable lithium polymer battery pack (3S configuration, 11.1V nominal, 12.6V fully charged, 3000mAh capacity)
- A battery management system (BMS) board for balance charging and protection
- A USB-C Power Delivery charging circuit for battery charging
- A DC-DC buck/boost converter for stable 12V output from the variable battery voltage (9.0V-12.6V)
- A priority diode circuit with automatic switchover between corded and battery power

The dual-power logic operates as follows:
- When the DC adapter is plugged in, the system runs on wall power and the battery charges
- When the DC adapter is removed, the system automatically switches to battery power with no interruption to projection
- When the battery is removed, the system operates on DC adapter power only
- A panel-mounted LED battery level indicator displays remaining charge

The battery provides approximately 1.5-2 hours of continuous projection per charge. The Pro model ships with two swappable battery packs for extended operation.

### 7.11 CLOUD SYNCHRONIZATION

The system includes an optional cloud synchronization service that allows project data to be shared between multiple devices.

#### 7.11.1 Architecture

The cloud service uses a Firebase Realtime Database with anonymous authentication. No user account creation is required.

#### 7.11.2 Passphrase-Based Pairing

Devices are paired using a user-entered passphrase. The passphrase is hashed using an FNV (Fowler-Noll-Vo) hash function to produce a deterministic path key. The FNV hash was chosen specifically because it is implementable in pure JavaScript without cryptographic APIs, which is necessary because the standard Web Crypto API (`crypto.subtle`) is unavailable on mobile devices accessing the application over non-HTTPS local network connections.

The hash function:

    function hashPassphrase(passphrase):
        hash = 2166136261  (FNV offset basis)
        for each character in passphrase:
            hash = hash XOR character_code
            hash = hash * 16777619  (FNV prime)
            hash = hash >>> 0  (force unsigned 32-bit)
        return hash as hexadecimal string

Project data is stored at the database path: `sync/{hashed_passphrase}/layit` as a JSON string.

#### 7.11.3 Conflict Resolution

When a device first connects to the cloud and finds existing data that differs from local data, the user is prompted to choose between keeping local data (overwriting the cloud) or using cloud data (replacing local data). This prevents silent data loss.

#### 7.11.4 Synchronization Timing

Edits are pushed to the cloud with a 3-second debounce delay. This batches rapid sequential edits (such as adjusting tile dimensions) into a single push, reducing network traffic and database write operations.

### 7.12 CUT VISUALIZATION AND TRACKING

The companion application provides comprehensive cut tile management including dimension display, progress tracking, and detail views.

#### 7.12.1 Cut Tile State Machine

Each tile requiring cutting is tracked through a three-state progression:

    State 0 (Pending):    Tile requires cutting, displayed in orange
    State 1 (Selected):   Tile selected for detail view, displayed in yellow
    State 2 (Complete):   Tile has been cut and placed, displayed in red

Tapping a tile advances it to the next state. The user may reset a completed tile to pending state after confirmation.

#### 7.12.2 Cut Dimension Calculation

For each cut tile, the system computes and displays:

**Wall Boundary Cuts.** The system finds the intersection points of tile edges with wall edges, calculates the distance from each tile corner to the nearest wall intersection, and determines which portions of the tile extend beyond the wall boundary. The resulting cut dimensions (the remaining piece that fits within the wall) are displayed in inches and fractions.

**Void Notch Cuts.** When a tile partially overlaps a void region, the system computes the notch dimensions (width and height of the rectangular region to be removed) and identifies the corner of the tile where the notch is located (top-left, top-right, bottom-left, or bottom-right).

**Dimension Display.** All dimensions are converted from decimal inches to fractional notation (nearest 1/16 inch) for display:

    sixteenths = round(remainder * 16)
    Simplify: 8/16 → 1/2, 4/16 → 1/4, 2/16 → 1/8, etc.
    Format: "whole-numerator/denominator" (e.g., "2-3/8 inches")

#### 7.12.3 Detail View

Tapping a cut tile opens a detail view showing the tile at enlarged scale with:
- The cut shape (the portion of the tile that remains after cutting)
- Cut lines displayed as dashed lines
- Dimension labels positioned along each cut edge
- Pinch-to-zoom and pan navigation for close inspection

---

## 8. CLAIMS

### Independent Claims

**Claim 1.** A tile installation guidance system comprising:

(a) a companion application configured to execute on a mobile computing device, the companion application providing a user interface for defining a work surface geometry and generating a tile layout pattern comprising a plurality of tiles with computed vertex coordinates, including computation of grout line positions from user-specified grout spacing, identification of cut tiles at work surface boundaries and around void regions, and computation of cut tile dimensions from tile-boundary intersection geometry;

(b) a portable laser projection device communicating wirelessly with the companion application, the projection device comprising:
- a microcontroller;
- a digital-to-analog converter connected to the microcontroller via a serial interface;
- a dual-axis galvanometer mirror assembly driven by analog signals from the digital-to-analog converter;
- a laser source modulated by the microcontroller via a blanking circuit;
- a camera connected to the microcontroller; and
- an inertial measurement unit connected to the microcontroller;

wherein the microcontroller receives tile layout data from the companion application, converts tile vertex coordinates to galvanometer drive signals, and drives the galvanometer mirror assembly to steer the laser source to project tile outlines onto a work surface at actual scale; and

(c) a vision-based alignment subsystem executing on the microcontroller, the alignment subsystem configured to:
- capture images of the work surface using the camera;
- detect edges of tiles that have been physically placed on the work surface using computer vision processing;
- match detected tile edges to corresponding tiles in the tile layout pattern;
- compute a perspective transformation matrix from the matched tile positions using homography computation with outlier rejection; and
- apply the perspective transformation to correct the projected positions of unplaced tiles in real-time;

whereby each tile placed by the user adds reference points to the alignment computation, creating a self-reinforcing reference grid that improves in accuracy as the installation progresses.

**Claim 2.** A method for projecting tile installation patterns with self-correcting alignment, comprising the steps of:

(a) receiving, at a portable projection device, tile layout data comprising vertex coordinates for a plurality of tiles from a wirelessly connected companion application;

(b) converting the tile vertex coordinates to galvanometer drive signals through a digital-to-analog converter;

(c) driving a dual-axis galvanometer mirror assembly to steer a modulated laser beam to project tile outlines onto a work surface;

(d) capturing images of the work surface with an onboard camera during projection;

(e) detecting edges of physically placed tiles in the captured images using edge detection and contour extraction, wherein the detected tile edges are edges of tiles that have been physically installed on the work surface by the user during the current installation session, as distinguished from pre-placed fiducial markers, QR codes, or calibration targets;

(f) refining detected tile corner positions to sub-pixel accuracy;

(g) matching detected tile corners to corresponding positions in the known tile layout;

(h) computing a homography matrix from the matched corner positions using random sample consensus (RANSAC) for outlier rejection;

(i) applying the homography matrix to transform the projected positions of all unplaced tiles; and

(j) repeating steps (d) through (i) continuously during projection, whereby alignment accuracy improves as additional tiles are placed and detected.

**Claim 3.** A portable laser projection device for tile installation guidance, comprising:

(a) a dual-core microcontroller, wherein a first core is dedicated to a real-time galvanometer scan loop and a second core handles wireless communication and vision processing;

(b) a dual-channel digital-to-analog converter with simultaneous latch capability, connected to the microcontroller via SPI, providing synchronized X-axis and Y-axis analog output;

(c) a dual-axis galvanometer mirror assembly driven by the analog output of the digital-to-analog converter through an operational amplifier buffer;

(d) a visible laser source with TTL modulation, controlled by the microcontroller through a MOSFET switching circuit for blanking during repositioning movements;

(e) a wide-angle camera connected to the microcontroller for capturing images of the work surface;

(f) an inertial measurement unit for detecting physical displacement of the device; and

(g) a safety interlock switch connected to the microcontroller via a hardware interrupt, configured to disable the laser within microseconds when the device enclosure is opened.

### Dependent Claims

**Claim 4.** The system of claim 1, wherein the vision-based alignment subsystem performs a cold start calibration procedure comprising detecting wall or corner edges in camera images using Canny edge detection and Hough line transform, and computing the room corner position from the intersection of detected perpendicular lines to establish an initial projection origin.

**Claim 5.** The system of claim 1, wherein the inertial measurement unit is configured to detect acceleration spikes exceeding a predetermined threshold, and upon detection, triggering an immediate re-alignment cycle using the vision-based alignment subsystem to provide automatic bump recovery without user intervention.

**Claim 6.** The system of claim 1, wherein the vision-based alignment subsystem computes a confidence score based on the average reprojection error of matched tile corners, and communicates the confidence score to the companion application for display as a visual indicator having a plurality of states corresponding to alignment quality levels.

**Claim 7.** The system of claim 1, wherein the alignment computation is performed independently on each camera frame using all currently visible placed tiles, such that alignment errors do not accumulate over time, providing absolute positioning.

**Claim 8.** The system of claim 1, wherein the companion application is further configured to automatically segment a work surface larger than the projection coverage into a grid of projection zones and guide the user through the zones in a sequential path, the path being serpentine for floor installations and bottom-up for wall installations.

**Claim 9.** The system of claim 1, wherein the companion application supports a plurality of tile pattern types including hexagonal tiles in pointy-top and flat-top orientations with computed honeycomb stagger offsets, herringbone patterns with alternating 45-degree tile rotations and computed zigzag vertex coordinates, and rectangular tiles with configurable brick-bond offset percentages, and wherein for each pattern type the companion application computes all tile vertex coordinates, grout line positions, and cut tile dimensions specific to that pattern geometry.

**Claim 10.** The system of claim 1, further comprising a cloud synchronization service configured to synchronize project data between multiple instances of the companion application using a passphrase-based pairing mechanism, wherein the passphrase is hashed using a non-cryptographic hash function to produce a database path key.

**Claim 11.** The method of claim 2, wherein step (e) comprises applying an adaptive threshold to the captured image to compensate for varying lighting conditions, applying a morphological closing operation to fill gaps in grout lines, applying Canny edge detection, and extracting quadrilateral contours from the edge map.

**Claim 12.** The method of claim 2, further comprising the step of computing corner dwell points at each tile vertex in the scan buffer, wherein multiple identical scan points are output at each vertex with the laser on, to compensate for reduced dwell time at corners caused by galvanometer deceleration and direction reversal.

**Claim 13.** The method of claim 2, further comprising the step of interpolating intermediate scan points between consecutive tile vertices at a spacing corresponding to approximately one degree of galvanometer angle, to ensure smooth mirror motion and uniform line brightness.

**Claim 14.** The method of claim 2, wherein the laser is blanked during repositioning movements between disconnected tile line segments, and the blanking delay is longer than the drawing delay to allow galvanometer mirror settling before the next line segment begins.

**Claim 15.** The device of claim 3, wherein the safety interlock switch is connected to the microcontroller via a hardware interrupt, and an interrupt service routine executing in instruction RAM disables the laser directly at the hardware level within microseconds of enclosure opening, independently of the main firmware execution.

**Claim 16.** The device of claim 3, further comprising an automatic timeout mechanism that disables the laser after a configurable period of no communication from the companion application.

**Claim 17.** The device of claim 3, further comprising a dual-power system with automatic switchover between a corded DC power supply and a removable rechargeable battery pack, wherein a priority circuit selects the corded power supply when available and switches to battery power without interruption when the corded supply is disconnected.

**Claim 18.** The device of claim 3, wherein the dual-channel digital-to-analog converter uses a simultaneous latch pin to update both X-axis and Y-axis outputs at the same instant, preventing axis skew during coordinate transitions.

**Claim 19.** The system of claim 1, wherein the companion application further provides cut tile management comprising: identification of tiles intersecting work surface boundaries or void regions, computation of cut dimensions from tile-boundary intersection geometry, display of cut dimensions in fractional inch notation, and a state tracking system for marking tiles through pending, selected, and completed states.

**Claim 20.** The system of claim 1, wherein the companion application includes a pattern optimization algorithm that evaluates a plurality of pattern offset positions and selects the position that maximizes a score based on one of: total full tile count, minimization of small cut pieces, or a weighted combination thereof.

**Claim 21.** The method of claim 2, wherein the tile matching in step (g) uses a nearest-neighbor search based on centroid distance and size comparison, with a distance threshold for outlier rejection, and multi-tile context for disambiguation of ambiguous matches.

**Claim 22.** The system of claim 1, wherein the companion application defines work surface void regions as rectangular areas within the wall polygon, and the tile layout engine classifies each tile as: fully inside a void (not rendered), partially overlapping a void (rendered with notch cut dimensions), or not touching any void (rendered as full tile).

**Claim 23.** The device of claim 3, wherein the microcontroller includes a power management architecture with cascaded voltage regulation, wherein a first regulator converts input voltage to a first intermediate voltage and a second regulator converts the first intermediate voltage to a second lower voltage, the cascaded configuration reducing thermal dissipation compared to direct conversion from input voltage.

**Claim 24.** The system of claim 1, wherein the companion application assigns each tile a persistent identification key derived from the tile's computed position in inches rounded to a fixed precision, the key remaining stable across zoom, pan, and pattern repositioning operations.

**Claim 25.** The method of claim 2, wherein the homography matrix computed in step (h) encodes the complete perspective transformation including the device position, orientation, and perspective distortion relative to the work surface, and is recomputed from scratch on each camera frame without reference to previously computed matrices.

**Claim 26.** The system of claim 1, wherein the vision-based alignment subsystem is distinguished from fiducial-marker-based alignment systems in that the reference points used for alignment computation are the physical edges of tiles installed by the user during the current installation, which edges are detected in camera images without requiring any pre-placed markers, targets, or machine-readable codes on the work surface, and wherein the number of available reference points increases monotonically as the installation progresses.

**Claim 27.** The system of claim 1, wherein the companion application further comprises a constraint-aware layout adjustment system that, upon receiving fixed constraint data representing physical features of the work surface from a camera-based room measurement system, checks whether any proposed tile pattern adjustment would cause grout lines to lose alignment with the edges of the fixed constraints, and selectively permits or warns against the adjustment based on the constraint check result.

---

## 9. ABSTRACT

A tile installation guidance system comprising a companion software application, a portable laser projection device, and an optional cloud synchronization service. The companion application allows a user to design tile layouts for multiple pattern types including hexagonal, herringbone, and rectangular with configurable grout spacing and brick-bond offsets. The projection device receives tile layout data wirelessly and drives a dual-axis galvanometer mirror assembly to project tile outlines as visible laser lines onto a work surface at actual scale. A vision-based alignment subsystem uses an onboard camera to detect the edges of tiles already placed by the installer and computes a homography transformation to continuously correct the projected pattern in real-time. Each placed tile adds reference points to the alignment computation, creating a self-reinforcing reference grid that improves in accuracy as installation progresses. An inertial measurement unit provides bump detection for automatic recovery from device displacement without manual recalibration. Safety systems include a hardware interlock, firmware-enforced safety checks, and automatic laser timeout.

---

> **PROVISIONAL FILING NOTE:** For a provisional patent application filing, Sections 1-7 (Title through Detailed Description) and Section 9 (Abstract) establish the priority date. Section 8 (Claims) is optional for the provisional but is included here for completeness and is recommended for inclusion. Formal drawings (referenced in Section 6) are optional for the provisional but should be prepared for the subsequent utility application filing within the 12-month provisional period.

> **ATTORNEY REVIEW RECOMMENDED:** This document is a technical disclosure prepared by the inventor. It is strongly recommended that a registered patent attorney or patent agent review and refine this document before filing, particularly the claims section, to ensure maximum protection and compliance with USPTO formal requirements.
