# LayIt Exploded-View App Rev 2 Notes

Date: 2026-05-06

## Current App Status

The ExpandIt runtime is at:

```text
/Users/Sims/Desktop/expandit/runtime/index.html
```

The current LayIt product manifest is at:

```text
/Users/Sims/Desktop/expandit/products/layit/manifest.json
```

The app has been upgraded from a simple exploded-view phase viewer into a
builder-grade Rev 2 scaffold.

It now supports:

- Phase-by-phase 3D assembly
- Simple procedural component placeholders when no GLB exists yet
- Named component pins and connector anchors
- Guided wire paths between named pins
- Per-phase build checks
- Required verification gates before advancing
- Accuracy notes on parts that are still placeholders

The current LayIt manifest contains:

- 7 phases
- 21 components
- 86 named pins
- 44 guided connections
- 24 required or explicit build checks

## Important Accuracy Boundary

The manifest is logic-accurate and safety-gated, but not yet a fully measured
digital twin.

Known real-photo details already captured:

- Galvo PSU label: KPDS0-12A
- Input: 100-240V AC 1.0A 50/60Hz
- Output: V1 +12V 4.0A and V2 -12V 1.0A
- White galvo PSU output headers marked `+ G -`
- Green 3-screw terminal belongs to the AC input side, not the low-voltage
  galvo output side

Known placeholder geometry:

- ESP32-S3 DevKitC-style board outline
- MP1584 buck module outline
- Galvo PSU board outline
- Galvo driver board outline and connector positions
- Laser module body
- Key switch / hard enable
- 2.048V reference module
- Camera and IMU

Do not treat placeholder part shapes as exact fit or final enclosure geometry.

## Rev 2 Builder Strategy

The app should be the build authority only when each step includes both:

- A named physical target, such as `GALVO_PSU.OUT_PLUS`
- A verification gate, such as `+ to G = +12V`

That is now the structure of the LayIt manifest.

The next accuracy pass should add caliper measurements for the real parts:

1. Overall board width/depth/thickness
2. Connector center locations from a fixed corner
3. Mounting-hole locations and diameters
4. Header pitch and pin order
5. Component height where enclosure clearance matters
6. Cable exit directions and strain-relief needs

Recommended minimum measurement accuracy:

- Connector centers: +/-0.5mm
- Mounting holes: +/-0.25mm
- Board outlines: +/-0.5mm
- Enclosure clearances: add at least 1.0mm margin after measurement

## Current Runtime Schema Additions

The runtime now reads these Rev 2 fields:

```json
{
  "checks": [
    {
      "id": "galvo_plus",
      "label": "Galvo PSU + to G measurement",
      "method": "White + G - header, + probe on + and black probe on G",
      "expected": "+11.5V to +12.5V",
      "required": true
    }
  ],
  "connections": [
    {
      "from": "GALVO_PSU.OUT_PLUS",
      "to": "GALVO_DRV.PWR_PLUS",
      "net": "+12V_GALVO",
      "color": "#ff4d4d",
      "instruction": "Driver positive split rail."
    }
  ],
  "components": [
    {
      "ref": "GALVO_PSU",
      "pins": [
        {
          "id": "OUT_PLUS",
          "label": "+",
          "offset_mm": [21, -5, 14],
          "net": "+12V_GALVO"
        }
      ],
      "accuracy": "Pin labels verified from photos; outline still placeholder."
    }
  ]
}
```

Checks are stored in browser `localStorage` per manifest id. Required checks
must be ticked before the app allows the next phase.

## Asset Work Still Needed

Existing useful GLBs:

- Resistor_0805.glb
- Cap_ceramic_0805.glb
- DIP-8_body.glb
- 2N7000_TO-92.glb
- Header_1x04.glb
- JST models
- Microswitch model

Assets still worth building from measurements/photos:

- ESP32-S3 DevKitC-1 full dev board
- MP1584 buck module
- Galvo PSU board with `+ G -` headers and AC terminal distinction
- Galvo driver board with actual connector labels
- Galvo mirror block
- Laserland 520nm module
- 2.048V reference breakout
- Key switch / hard enable
- Beam stop and test target

## Safety Policy For The App

The app must keep these gates:

- Galvo PSU cannot advance until +12V, -12V, and 24V span are measured
- TL072 stage cannot advance until the 2.048V reference and analog outputs are
  measured
- Galvo driver cannot advance until the 200mW laser is physically disconnected
- 200mW laser cannot advance until eyewear, beam stop, hard enable, TTL boot-off,
  and interlock checks are confirmed
- Camera work remains blocked until projection works and the real camera pinout
  is known

This is what keeps ExpandIt from becoming a pretty but unsafe build guide.
