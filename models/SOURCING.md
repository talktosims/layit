# LayIt Laser — 3D Model Sourcing Manifest

Cross-referenced against `LayIt_BOM_v3.md` and `Build Binder/LayIt_Build_Binder.pdf`.

**Power input:** USB-C PD only (BOM v3). The 12V barrel jack from binder Rev 1.1 is **dropped** — replaced by a USB-C PD trigger board negotiating 12V from a PD wall charger.

---

## TIER A — Auto-fetchable (direct curl, no login)

These pull straight from GitHub via `fetch_direct.sh`. All open-source CAD libraries.

| Part | Ref | Source | Format |
|---|---|---|---|
| ESP32-S3-WROOM-1 | U3 | [Espressif kicad-libraries](https://github.com/espressif/kicad-libraries) | STEP |
| AMS1117 (SOT-223 body) | U1, U2 | KiCad packages3D | STEP |
| 2N7000 (TO-92 body) | Q1 | KiCad packages3D | STEP |
| MCP4822 / TL072 (DIP-8 body) | U4, U5 | KiCad packages3D | STEP |
| SS34 Schottky (SMA package) | D1 | KiCad packages3D | STEP |
| WS2812B PLCC4 | LED1 | KiCad packages3D | STEP |
| Tactile push 6×6mm | SW1, SW2 | KiCad packages3D | STEP |
| 1x04 header 2.54mm | J6 | KiCad packages3D | STEP |
| FPC 24-pin 1.0mm (TE) | J5 | KiCad packages3D | STEP |
| Generic R, C 0805 + THT electrolytic | R*, C* | KiCad packages3D | STEP |

---

## TIER B — Manual download (login wall, opened in browser tabs)

Login required for SnapEDA / SnapMagic / UltraLibrarian (free accounts). `open_sources.sh` opens each page so you batch-click downloads. KiCad's free repo doesn't carry the JST XH series, so this is the cleanest path.

| Part | Ref | Best source | Notes |
|---|---|---|---|
| JST B3B-XH-A (3-pin vertical) | J3 | [SnapMagic](https://www.snapeda.com/parts/B3B-XH-A/JST/view-part/) | Laser power connector |
| JST B6B-XH-A (6-pin vertical) | J4 | [SnapMagic](https://www.snapeda.com/parts/B6B-XH-A/JST/view-part/) | Galvo driver connector |
| Hammond 1455 enclosure (~6×4×3) | — | [hammfg.com](https://www.hammfg.com/electronics/small-case/extruded/1455) | Pick exact PN from page; STEP is on each product subpage |
| 1/4-20 threaded insert | — | McMaster-Carr | Search "1/4-20 brass insert", click STEP |
| OV5640 module (if ArduCam variant) | — | ArduCam product page | Generic AliExpress version → photo-model instead |
| USB-C connector (GCT USB4135-GF-0170) | — | [SnapMagic](https://www.snapeda.com/parts/USB4135-GF-0170/GCT/view-part/) | Drops onto the PD trigger board outline |

---

## TIER C — Photo-modeling required (no published CAD)

For these, drop reference images into `reference_photos/<part_name>/` and model in Blender from photos + datasheet dim drawings. **Connector positions are what matter for wire routing** — measure those first.

| Part | Ref | What to capture | Wire-routing critical detail |
|---|---|---|---|
| USB-C PD trigger board (12V) | J1 (was barrel) | Photos top + edge of whichever board you sourced | USB-C connector position + 12V/GND output pad locations. The USB-C connector STEP itself comes from Tier B. |
| Laserland 4060-530D-200 (200mW 520nm) | LASER | Datasheet dim drawing + product photos | 3-wire pigtail exit point on cylindrical body (12V, TTL, GND) |
| 20K PPS galvo scanner set | GALVO | Photos from 3 sides + caliper | Mirror axes, motor shaft positions, mirror tilt |
| Galvo driver board (bundled) | — | Photos top + edge | Input header position (it IS a 6-pin XH — use J4 STEP) |
| OV5640 generic (AliExpress) | CAM | Photos + 24-pin FPC ribbon path | FPC connector position + ribbon entry orientation |
| 3S 11.1V LiPo pouch (Pro) | BAT | Photos + caliper | XT30 connector position |
| BMS 3S 12.6V 20A (Pro) | — | Photos top/bottom | Input + output pad locations |
| Buck/boost DC-DC (Pro) | — | Photos | Input/output terminal block positions |
| USB-C charging circuit (Pro) | — | Photos | USB-C connector + output wire pad |
| LED voltage display (Pro) | — | Photos | 2-wire input position |
| Battery sled / bay (Pro) | — | **Designed by you, not sourced** | Spring contact positions |

---

## Wire routing realism notes

For "see exactly which wire goes where" build instructions, three things matter most:

1. **Connector pin positions** must be accurate — that's where wire endpoints land. Tier A + B covers this.
2. **Wire colors** drive material assignments (Section 4 of binder, page 17): RED=12V, WHITE=5V, YELLOW=3.3V, BLACK=GND, BLUE=signals, GREEN=digital/safety.
3. **Bezier curves with sag** look more realistic than straight lines — use Blender's curve modifier with a slight gravity-droop in the Y axis.

Once parts are dropped in, the workflow per cable:
- Empty at connector A pin N → empty at connector B pin M
- Bezier connecting them, beveled with circular profile
- Material from color table
- Label geometry node (optional) for "RED 12V" floating text near each wire

---

## Status legend (filled in as you fetch)

- ⏳ pending
- ✅ downloaded
- 📷 photo-modeled in Blender
- ❌ blocked / needs alternate source
