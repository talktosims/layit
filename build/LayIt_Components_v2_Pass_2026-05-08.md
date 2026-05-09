# LayIt Components v2 Pass

Date: 2026-05-08
Author: Claude (Opus 4.7), complementary to Codex's REV2 work
Status: 7 components promoted to `datasheet_parametric` accuracy

## What changed

The ExpandIt LayIt manifest had every component at one of three low-trust
levels (`photo_only_placeholder`, `estimated_package_model`,
`logical_placeholder`). For seven of those parts there is publicly available
manufacturer mechanical CAD or a well-characterized standard package, so this
pass builds them parametrically from those drawings, exports realistic-shaded
GLBs, and promotes the manifest entries to `datasheet_parametric`.

Audit count change:

| Accuracy            | Before | After |
|---|---:|---:|
| datasheet_parametric | 0  | 7  |
| estimated_package_model | 8  | 4  |
| photo_only_placeholder | 10 | 8  |
| logical_placeholder | 3  | 2  |

No footprint overlaps. No missing connection endpoints. Validator
(`validate_layit_geometry.mjs`) is clean.

## Components promoted

| Ref | Part | GLB | Source |
|---|---|---|---|
| U3 | ESP32-S3-DevKitC-1 N16R8 | `models/ESP32-S3-DevKitC-1.glb` | Espressif DevKitC-1 v1.1 user guide + Dimensions PDF/DXF |
| U4 | Microchip MCP4822 PDIP-8 | `models/MCP4822_PDIP8.glb` | Microchip DS22249 §5.6 (C04-018) |
| U5 | TI TL072CP PDIP-8 | `models/TL072CP_PDIP8.glb` | TI TL072 datasheet, P0008 |
| C10 | 0805 ceramic MLCC | `models/Cap_0805_ceramic_v2.glb` | IPC SMD-A 0805 std dims |
| Q1 | Onsemi 2N7000 TO-92 | `models/2N7000_TO92_v2.glb` | Onsemi 2N7000 datasheet, TO-226-3 |
| VREF | Adafruit LM4040 2.048V breakout (PRD 2200) | `models/LM4040_Adafruit2200.glb` | Adafruit PRD 2200 EagleCAD mechanicals |
| IMU | MPU6050 GY-521 module | `models/MPU6050_GY521.glb` | InvenSense MPU-6050 datasheet + GY-521 module reference |

Each GLB carries embedded Principled BSDF materials (black epoxy + tin leads
on ICs, blue PCB + gold pads on GY-521, classic Adafruit black + gold pads on
the LM4040 breakout, RF shield + USB-C + RGB LED + tactile buttons on the
ESP32 dev board).

Preview renders in `/Users/Sims/Desktop/layit/models/renders/components_v2/`.

## What's still low-trust (intentional — these need physical measurement)

These remain at `photo_only_placeholder` or `estimated_package_model` because
they are kit/no-name boards with no manufacturer CAD, or logical groupings
that should be split into individual parts in a later layout pass:

| Ref | Why it stays low-trust | Resolution path |
|---|---|---|
| U1 | MP1584 module — Amazon kit-PCB, no datasheet for the module | Caliper measurement when the 5-pack arrives Friday |
| GALVO_PSU | KPDS0-12A AC-input split supply, no manufacturer mechanicals | Photo capture protocol from Dimensional Modeling Plan + caliper |
| GALVO_DRV | Kit galvo driver board, vendor-unknown | Same |
| GALVOS | Generic 20K galvo set | Same — body + mounting flange + mirror dims |
| LASER | 200mW 520nm laser module | Caliper when it arrives, plus mounting/heatsink dims |
| CAM | OV5640 module — depends on user's specific listing | Photo + caliper of actual module; FPC pinout |
| SW3 | Lid interlock microswitch | Once the panel-mount switch is chosen |
| KEY | Hard laser enable / key switch | Once the key switch is chosen |
| 12V_IN | Logical placeholder for the 12V source | Decide PD trigger vs barrel-jack supply |
| BEAM_STOP | Logical placeholder | Decide ceramic tile vs commercial beam stop |
| R_XY, C_ANALOG | Logical groups of 4x 0805 each | Split into individual placed parts in a layout pass |
| R9/R10/R16 | Logical group of 3x 0805 | Split into individual placed parts |

Note: a `Resistor_0805_v2.glb` was also built and is available; the
group-resistor entries (`R_XY`, `R9/R10/R16`) still reference primitive blocks
because splitting them into individual placed parts is a layout change that
needs deliberate position assignment, not just a model swap.

## Provenance / scripts

- Build: `/Users/Sims/Desktop/layit/models/scripts/build_real_components.py`
- Render: `/Users/Sims/Desktop/layit/models/scripts/render_components.py`
- Manifest promotion: `/Users/Sims/Desktop/layit/models/scripts/promote_components.py`
- Manifest backup: `/Users/Sims/Desktop/expandit/products/layit/manifest.pre-realmodels-2026-05-08.json`

Re-run any of these with Blender 5.1 (`/Applications/Blender.app/Contents/MacOS/Blender`)
or python3.

## Honest accuracy disclaimer

`datasheet_parametric` means the geometry was built from the manufacturer's
mechanical drawing without independent physical verification of the specific
part purchased. For the standard JEDEC packages (DIP-8, TO-92, 0805) this is
indistinguishable from `vendor_step_verified` for fit-checking purposes,
because the physical part has no degrees of freedom outside the JEDEC tolerance.

For the **ESP32-S3-DevKitC-1** entry specifically: it is built to Espressif's
reference design. The user has ordered a Hosyond clone — Hosyond clones
typically follow DevKitC-1 outlines but vary in:
- Header row count (2x18 vs 2x19 vs 2x21)
- USB-C connector variant (overhang amount, dimensions)
- LED placement
- Sometimes silkscreen/labeling

Physical clone-confirmation is a 30-second job with calipers when the boards
arrive Friday and is a precondition before claiming solder-by-eye accuracy.
Until then, treat U3 as `datasheet_parametric` for layout planning but not
for solder targets.

For the **Adafruit LM4040 breakout** entry: the part is Adafruit PRD 2200,
which Adafruit publishes EagleCAD for. If the user buys a different LM4040
breakout (e.g. Sparkfun, generic eBay), this model will be wrong.

For the **GY-521 MPU6050 module**: the GY-521 is a clone-class module, not a
single manufacturer part. There are slight variations across listings (some
have 20.6 x 15.8 vs 21.2 x 15.8, some have header-up vs header-down). The
manifest uses the most common dimensions; verify with calipers when the user
gets to that subsystem.

## Why these specific seven and not the others

The split is empirical: parts whose envelope is fully constrained by JEDEC or
a published manufacturer drawing get parametric models; parts whose envelope
is set by a kit vendor's PCB layout decisions don't, because there's no
authoritative source to model from.

The user can resolve the remaining 8 photo-only items by following the
photo capture protocol in `LayIt_Dimensional_Modeling_Plan.md` and filling
out `component_measurements.csv` — Codex's existing infrastructure handles
the rest.
