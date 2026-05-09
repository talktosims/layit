# LayIt Model Preview Log

Created: 2026-05-06

## Preview Pass 1

The ExpandIt runtime now supports richer parametric preview models for the
first high-impact placeholder parts.

Updated runtime:

- `/Users/Sims/Desktop/expandit/runtime/index.html`

Updated manifest:

- `/Users/Sims/Desktop/expandit/products/layit/manifest.json`

## New Runtime Primitive Types

### `esp32_devkit`

Used by:

- `U3`

Adds:

- PCB body
- ESP32-S3 module can
- antenna/label area
- USB-C connector body
- two button bodies
- dual header strips
- individual gold header pins

Trust status:

- Preview only.
- Based on a DevKitC-style outline.
- The ordered Hosyond board still needs clone confirmation before solder
  guidance.

### `mp1584_module`

Used by:

- `U1`

Adds:

- PCB body
- inductor block
- MP1584 IC body
- trimpot
- electrolytic/ceramic capacitor cylinders
- four visible solder pads

Trust status:

- Preview only.
- Uses common MP1584 module proportions.
- Exact purchased module listing/photo still needed before pad coordinates are
  trusted.

### `galvo_psu_board`

Used by:

- `GALVO_PSU`

Adds:

- PCB body
- transformer block
- heatsink/regulator block
- large capacitors
- green AC terminal block
- white `+ G -` output header

Trust status:

- Photo-informed visual preview only.
- Existing photos verify the general +/G/- output label relationship, but not
  exact board dimensions or connector center coordinates.

## Important Result

The improved models make the current layout conflicts more obvious. This is
good: better geometry should expose collisions rather than hide them.

The preview is not yet a build-accurate solder layout. It is a staged upgrade
from anonymous blocks toward measured geometry.

## Next Modeling Targets

1. Verify/source DIP-8 geometry for MCP4822 and TL072.
2. Split logical resistor groups into individual physical parts.
3. Add exact source/package status for TO-92 2N7000 and 0805 passives.
4. Add a layout-cleanup pass after the first three larger modules are better
   represented.

## Preview Pass 2

Updated runtime:

- `/Users/Sims/Desktop/expandit/runtime/index.html`

Updated manifest:

- `/Users/Sims/Desktop/expandit/products/layit/manifest.json`

New runtime primitive types:

- `dip8_ic`
- `smd_0805`
- `smd_array`
- `to92_package`

Upgraded component previews:

- `U4` MCP4822 now uses a parametric DIP-8 candidate package.
- `U5` TL072 now uses a parametric DIP-8 candidate package.
- `C10` now uses a parametric 0805 capacitor body.
- `C_ANALOG` now uses a grouped 0805 capacitor preview.
- `R_XY` now uses a grouped 0805 resistor preview.
- `Q1` 2N7000 now uses a parametric TO-92 candidate package.
- `R9/R10/R16` now uses a grouped 0805 resistor preview.

Layout update:

- Component positions are now spaced as an exploded bench map so visible parts
  no longer intersect in the preview.
- This is not a final PCB layout or a solder-by-eye wiring authority.
- The validator reports zero footprint overlaps and zero missing connection
  endpoints after this pass.

Runtime behavior update:

- Reset view and Escape now frame the actual visible build bounds instead of
  aiming only at the origin.

Trust status:

- DIP-8, 0805, and TO-92 bodies are package-candidate previews.
- They still need exact purchased-part confirmation before the app can claim
  build-accurate placement or lead order.
- Logical grouped resistors/capacitors still need to become individual placed
  parts in the final solder guide.
