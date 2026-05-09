# LayIt Physical Capture Checklist

Created: 2026-05-06

Use this checklist before replacing any ExpandIt placeholder with a
build-accurate model.

## Capture Setup

- Use calipers for dimensions. Photos alone are not dimensional truth.
- Put the part on graph paper or beside a metal ruler in the same plane.
- Shoot top and bottom straight down, not at an angle.
- Shoot all four sides for height, connector direction, and cable exits.
- Add close-ups of every label and connector.
- Record measurements in:
  - `/Users/Sims/Desktop/expandit/products/layit/component_measurements.csv`
  - `/Users/Sims/Desktop/layit/build/component_measurements_template.csv`

## First Priority Parts

### U3 ESP32-S3 Dev Board

Why first: it is central, large, and currently collides with several later
parts.

Measure:

- board length, width, thickness
- USB-C connector outer position and height
- two header row centerlines
- header pitch and row-to-row spacing
- pin 1 / 5V / GND / GPIO10 / GPIO11 / GPIO12 / GPIO13 / GPIO14 / GPIO47 /
  GPIO48 / GPIO40 / GPIO41 coordinates
- boot/reset button positions
- mounting holes, if present

Also confirm whether the board exactly matches Espressif ESP32-S3-DevKitC-1.
If it does, use the official Dimensions PDF/DXF as the source of truth.

### U1 MP1584 Buck Module

Why second: it establishes power wiring and has real pads that matter.

Measure:

- board length, width, thickness
- IN+ / IN- / OUT+ / OUT- pad centers
- pad dimensions
- inductor footprint and height
- trim pot footprint and screw position
- capacitor heights
- underside pads if present

### GALVO_PSU Split Supply

Why third: it is safety-critical and cannot be a vague block.

Measure:

- board outline
- mounting hole centers and diameters
- green AC terminal position and pin spacing
- white `+ G -` output header positions
- heatsink, transformer, capacitor heights
- clearance envelope for mains side

Never power this board loose for measurement.

### GALVO_DRV Board

Why fourth: galvo motion depends on exact connector labels.

Measure/photo:

- top and bottom straight-down photos
- all connector labels
- power connector pin labels
- signal connector pin labels
- board outline and mounting holes
- all connector center coordinates

Do not create solder guidance until these labels are entered.

### LASER Module

Why fifth: beam-axis position matters more than just body shape.

Measure:

- body diameter or rectangular body size
- body length
- driver board dimensions if separate
- wire exit location
- beam axis relative to body/mount
- mounting bracket dimensions

### KEY / Interlock Switches

Why sixth: panel/enclosure clearance depends on the real parts.

Measure:

- body size behind panel
- threaded barrel diameter/length
- nut/washer diameter
- terminal lug locations
- key orientation and front clearance

## Output Rule

For each part, the model is not accepted into solder-guidance mode until:

- `component_sources.json` has a source/evidence entry
- `component_measurements.csv` has real dimensions
- the GLB bounding box matches the measurements
- all connector/pin endpoints are real physical targets
- the geometry validator reports no impossible collisions

