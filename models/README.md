# LayIt Laser — Blender 3D Build Reconstruction

Goal: a complete, dimensionally-faithful 3D model of the LayIt Laser so you can produce illustrated build instructions where every wire path is visible in 3D space.

## Folder layout

```
models/
├── auto/              ← STEP files fetched by fetch_direct.sh
│   ├── pcb_ics/
│   ├── pcb_passives/
│   ├── connectors/
│   └── switches/
├── manual/            ← STEP files you download from login-walled sources
│   ├── connectors/    (JST XH, USB-C)
│   ├── enclosure/     (Hammond)
│   └── hardware/      (McMaster fasteners, tripod insert)
├── photo_model/       ← Parts modeled from photos (laser, galvos, camera, batteries)
├── reference_photos/  ← Drop reference imagery here, organized by part
└── blender/           ← The .blend assembly file lives here
```

## Workflow

### 1. Auto-fetch the open-source STEPs (~13 parts)
```bash
chmod +x fetch_direct.sh open_sources.sh
./fetch_direct.sh
```
This pulls Espressif's official ESP32-S3-WROOM-1 STEP plus generic packages (DIP-8, SOT-223, TO-92, SMA, FPC, headers, barrel jack, tactile switches, electrolytic cap, R/C 0805) from open-source CAD libraries. Failures are reported with HTTP codes so we can fix URL drift.

### 2. Batch-open login-walled sources
```bash
./open_sources.sh
```
This opens each Tier-B source in your browser. Sign in once to SnapMagic (free) and McMaster, then click download on each. Drop files into `models/manual/<subfolder>/`.

### 3. Photo-model the rest
The laser, galvos, OV5640, and Pro battery system don't have published CAD. For each:
- Take photos from 3 angles + close-ups of every connector
- Note dimensions with calipers (the dim drawing in the binder is a starting point)
- Drop photos in `reference_photos/<part_name>/`
- Model in Blender from photos — connector positions are the priority

### 4. Assembly in Blender
Import all STEPs via File → Import → STEP (requires the [STEPper](https://github.com/ambient-design/blender-stepper) addon, or convert to OBJ first). Build the assembly bottom-up:
1. PCB outline
2. Drop ICs at silkscreen positions (MCP4822 at U4, etc. — refer to binder Section 3 phase-by-phase)
3. Drop connectors (J1-J6, SW1-SW3) at their footprints
4. Mount external components (laser, galvo, camera) inside enclosure
5. Run wires as Bezier curves between connector pins, materials assigned by color (RED/WHITE/YELLOW/BLACK/BLUE/GREEN per binder Section 4)

### 5. Render build steps
Each phase from the binder becomes a render:
- Resistors only
- Resistors + caps
- … through ESP32 module mount → connectors → external wiring

## Accuracy expectations

| Tier | Source | Accuracy |
|---|---|---|
| A: Auto-fetched | Manufacturer-published STEP | Dimensionally exact |
| B: Manual download | Manufacturer/SnapEDA STEP | Dimensionally exact |
| C: Photo-modeled | Reference photos + calipers | Visually faithful, ±1mm typical |

For wire-routing instructions, Tier A and B accuracy is more than sufficient — connector pin positions are exact. Tier C parts (laser, galvos, camera) have the connector positions as the only critical detail; the rest of the body shape just needs to look right.

## See also

- `SOURCING.md` — full manifest, per-part status tracking
- `../LayIt_BOM_v3.md` — canonical BOM (USB-C PD design)
- `../Build Binder/LayIt_Build_Binder.pdf` — assembly steps + wiring (Rev 1.1, barrel-jack era)
