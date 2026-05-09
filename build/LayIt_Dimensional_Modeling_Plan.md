# LayIt Laser Dimensional Modeling Plan

Created: 2026-05-06

## Why this exists

The current ExpandIt LayIt manifest is useful as a safety-gated wiring concept
viewer, but it is not a dimensionally reliable assembly model yet.

Current manifest audit:

- 21 rendered components
- 12 procedural placeholder blocks
- 9 GLB models, many of them generic package models
- Multiple footprint collisions in the current layout
- Several connection endpoints are logical pins, not measured solder targets

Do not use the current 3D layout as a solder-by-eye authority until every
component has measured geometry, real pin coordinates, and collision checks.

## Accuracy target

Minimum useful accuracy for builder guidance:

- Standard IC packages/connectors: use manufacturer package drawings or vendor
  STEP models, then verify exported GLB bounding box within +/-0.2 mm.
- Generic modules and boards: measure with calipers and orthographic photos;
  target +/-0.5 mm for body/board dimensions and +/-0.3 mm for connector/pin
  locations.
- Wire/solder endpoints: must land on real pads, header pins, or through-hole
  leads, not approximate labels floating above the part.

## Evidence levels

Every component model should carry one of these evidence levels in the manifest:

1. `vendor_step_verified`
   - Source is a manufacturer STEP/3D model or mechanical CAD file.
   - Bounding box and pin origin have been checked after GLB export.
2. `datasheet_parametric`
   - Built in Blender/FreeCAD from manufacturer mechanical drawings.
   - Dimensions, pitch, pin count, lead shape, and pin 1 are recorded.
3. `measured_parametric`
   - Built from caliper measurements and perpendicular reference photos.
   - Used for no-name Amazon/eBay/kit boards where datasheets are weak.
4. `photo_only_placeholder`
   - Visual reference only. Not approved for physical fit or solder guidance.

The runtime should visibly warn when any visible part is below
`measured_parametric`.

## Source strategy by part type

### ESP32-S3 dev board

Use Espressif official mechanical sources first. Their ESP32-S3-DevKitC-1 docs
link the board schematic, PCB layout PDF, Dimensions PDF, and Dimensions DXF.
The docs also list the J1/J3 header tables, which should become actual pin
coordinates. Confirm whether the ordered Hosyond board exactly matches the
Espressif DevKitC outline before trusting those files.

Needed:

- exact board variant/version
- board outline
- header pitch and row spacing
- USB connector position and height
- boot/reset button locations
- pin 1 orientation and all GPIO header coordinates

### MCP4822 and TL072

Use package-level mechanical drawings or manufacturer CAD. These are normal
DIP-8 parts, so one verified DIP-8 model can serve both, but only if the pin
numbering, notch, body height, pin pitch, and lead row spacing are correct.

Needed:

- package variant actually purchased: PDIP, SOIC, etc.
- body dimensions
- 2.54 mm pin pitch
- row spacing
- pin 1 notch/dot
- lead diameter/width and insertion depth

### MP1584 buck module

Do not model only the MP1584 IC. The Amazon module is a whole PCB assembly with
terminal pads, inductor, trim pot, capacitors, and module-specific pin pads.
Manufacturer IC CAD is useful only for the chip on the board.

Needed from the real module:

- board length/width/thickness
- corner radius or chamfer if present
- pad locations and labels: IN+, IN-, OUT+, OUT-
- inductor size and height
- trim pot position
- tallest component height
- underside pad/copper positions if soldered flat to perfboard

### Galvo PSU and galvo driver boards

These are the highest-risk modeling items because the photos show kit boards,
not a known manufacturer CAD package. They must be measured from the exact
parts in hand.

Needed:

- board outline length/width/thickness
- mounting hole diameter and center coordinates
- heatsink/transformer/capacitor maximum heights
- all connector footprints and labels
- white `+ G -` output header pin centers
- AC input terminal location, orientation, and keepout/enclosure note
- galvo-driver signal/power connector pin labels from photos

### Connectors, switches, laser module, camera, IMU

Use vendor STEP/datasheet where exact part numbers exist. For generic modules,
measure the real part and create a parametric model.

Needed:

- exact part number when available
- body dimensions
- pin pitch and pin count
- mounting holes
- mating direction / cable exit direction
- usable clearance volume for plugs and wires

## Photo capture protocol

For each physical module/board:

1. Put the part on a flat surface with graph paper or a ruler in the same plane.
2. Take top and bottom photos straight down, not angled.
3. Take front, back, left, and right side photos for connector heights.
4. Add one close-up of each connector label.
5. Record caliper measurements in the template CSV.
6. Do not rely on perspective photos for final dimensions; use photos for
   orientation, labels, and visual texture.

## Blender / CAD workflow

Recommended path:

1. Collect source data into `component_measurements.csv`.
2. Create or import a source model:
   - vendor STEP/DXF when available
   - FreeCAD/Blender parametric mesh from measured dimensions otherwise
3. Set model units to millimeters.
4. Put the component origin at the manifest mounting origin.
5. Add named empty objects or metadata for real pin/solder endpoints.
6. Export GLB.
7. Run a bounding-box validator against the manifest dimensions.
8. Run collision and clearance checks against the full assembly.
9. Only then replace the manifest placeholder.

## Manifest changes needed

Add these fields to every component:

```json
{
  "model_accuracy": "measured_parametric",
  "source_refs": ["photo:IMG_9451", "measurement:component_measurements.csv"],
  "measured_size_mm": [42.0, 28.0, 12.0],
  "origin_definition": "board_center_top_surface",
  "clearance_mm": 1.0,
  "pins": [
    {
      "id": "OUT_PLUS",
      "label": "+",
      "position_mm": [46.2, -18.0, 14.0],
      "target_type": "connector_pin"
    }
  ]
}
```

For solder guidance, prefer absolute `position_mm` for pins after the layout is
measured. Local `offset_mm` is okay during early modeling, but it hides mistakes
when components rotate or move.

## Validation gates

Before the viewer claims a component is build-accurate:

- GLB bounding box matches measured/source dimensions.
- Pin coordinates match real pads or leads.
- Component footprint does not collide with any earlier/later installed part.
- Through-hole pins land on perfboard holes or the model declares that the part
  is off-board/panel-mounted.
- Wire endpoints attach to real solder/terminal targets.
- Hazardous modules include keepout/enclosure notes.

## Immediate next steps

1. Freeze the current app as `concept_viewer`.
2. Create a measured part library starting with:
   - ESP32-S3 dev board
   - MP1584 buck module
   - galvo PSU
   - galvo driver
   - laser module
   - actual interlock/key switch
3. Replace current placeholder blocks one at a time.
4. Add a runtime accuracy filter so parts can be shown as:
   - verified
   - measured
   - estimated
   - placeholder
5. Refuse “solder guidance” mode until all visible endpoints are verified.

## Useful official source starting points

- Espressif ESP32-S3-DevKitC-1 hardware docs: schematic, PCB layout, dimensions
  PDF, and dimensions DXF are linked from the official user guide.
- Microchip MCP4822 product page: datasheet and CAD models are linked from the
  official product page.
- MPS MP1584 product page: official symbols, footprints, and 3D models exist
  for the IC, but the purchased buck module still needs caliper modeling.

