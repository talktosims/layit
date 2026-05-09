# LayIt Web Spec Source Pass

Created: 2026-05-06

## Purpose

This pass answers a specific question: which LayIt parts can be dimensioned
from web/manufacturer data, and which parts still need real-part confirmation?

The answer is not "measure everything." A lot can be solved from datasheets,
CAD, DXF, and known package standards. The only parts that need the user's help
are clone modules, kit boards, or safety fixtures where web data is not enough.

## Status Categories

- `web_solvable_package`: manufacturer/package sources should be enough.
- `web_solvable_if_exact_part`: web data works if the exact purchased part
  number is confirmed.
- `web_assisted_module_confirm_needed`: web data gives a candidate outline, but
  clone/module variations must be checked.
- `real_part_required`: the actual kit/module/fixture must be photographed or
  measured.
- `layout_not_final`: the electrical part must be split/placed before geometry
  matters.
- `part_not_selected`: choose the part first.

## Component Source Map

| Ref | Current Status | Web/Spec Result | What I Still Need From You |
|---|---|---|---|
| U3 | `web_assisted_clone_confirm_needed` | Espressif's official ESP32-S3-DevKitC-1 docs provide schematic, PCB layout, dimensions PDF/DXF, and header tables. | Confirm the ordered Hosyond board matches the official DevKitC outline, or send a straight top photo once it arrives. |
| U4 | `web_solvable_package` | MCP4822-E/P can be modeled from Microchip product data/CAD/datasheet. | Only confirm the chip is DIP-8 MCP4822-E/P, not SOIC or a different DAC. |
| U5 | `web_solvable_package` | TL072CP can be modeled from TI product/package drawings. | Only confirm the chip is TL072CP DIP-8. |
| C10 / C_ANALOG | `web_solvable_if_exact_package` | 0805 package can be modeled from standard dimensions. | Confirm whether you are actually using SMD 0805 caps on the bench or through-hole parts on perfboard. |
| Q1 | `web_solvable_if_exact_package` | 2N7000 TO-92 can be modeled from package drawings. | Confirm TO-92 vs SOT-23 and visible lead order/flat face. |
| SW3 | `web_solvable_if_exact_part` | Omron D2F-01L is source-modelable if that exact switch was bought. | Confirm it is really D2F-01L, not a generic lever microswitch. |
| U1 | `web_assisted_module_confirm_needed` | MPS has official MP1584 IC CAD/data, but the Amazon buck module is a full clone board. | Need exact listing or clear top/bottom photos with any ruler/known object for board/pad layout. |
| LASER | `web_assisted_dimension_confirm_needed` | Laserland page confirms 4060-530D-200 electrical/optical identity. Mechanical drawing is still needed for beam-axis precision. | Send product page/order confirmation or a straight side/top photo when ready. |
| IMU | `web_assisted_module_confirm_needed` | MPU6050 GY-521 module family is common, but clone board layouts vary. | Exact listing or straight photo if the IMU is used in this prototype. |
| CAM | `web_assisted_module_confirm_needed` | OV5640 24-pin DVP modules vary in board size/lens/FPC orientation. | Exact module listing before any camera pin or fit model is trusted. |
| GALVO_PSU | `real_part_required` | Existing photos identify likely +12/G/-12 outputs, but web data for this kit supply is weak. | We already have useful photos; a straight top/bottom shot with scale would make it modelable. |
| GALVO_DRV | `real_part_required` | Generic 20K galvo listings are not enough for exact connector labels or board layout. | Straight top/bottom photos and connector label closeups. |
| GALVOS | `real_part_required` | Scanner block/mirror/cable geometry is kit-specific. | Exact listing or clear photos of scanner block and cable exit. |
| KEY | `real_part_required` | Key switches vary too much by listing. | Exact part/listing or photo once selected. |
| TEST_LASER | `part_not_selected` | Cannot model until selected. | None now; we can choose later if needed. |
| VREF | `part_not_selected` | Cannot model until the 2.048 V reference approach is chosen. | None now; we can choose a specific reference module/IC first. |
| R_XY / R9/R10/R16 | `layout_not_final` | Need to split logical resistor blocks into individual physical resistors. | No measuring yet; first lock the real bench layout/package style. |
| BEAM_STOP | `real_part_required` | Safety fixture is custom/bench-specific. | Decide actual material/size before modeling. |
| 12V_IN | `real_part_or_offboard_decision_needed` | If off-board, don't model it as a mounted block. If a PD trigger board is mounted, use that exact board. | Decide whether the 12V source/PD trigger lives inside the build or outside as a cable input. |

## Web Sources Already Seeded

- Espressif ESP32-S3-DevKitC-1 official hardware docs:
  https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html
- Microchip MCP4822 official product page:
  https://www.microchip.com/en-us/product/mcp4822
- DigiKey MCP4822-E/P authorized listing:
  https://www.digikey.com/en/products/detail/microchip-technology/MCP4822-E-P/951465
- Texas Instruments TL072 official product page:
  https://www.ti.com/product/TL072
- DigiKey TL072CP authorized listing:
  https://www.digikey.com/en/products/detail/texas-instruments/TL072CP/277421
- MPS MP1584 official IC page:
  https://www.monolithicpower.com/en/mp1584.html
- Laserland 4060-530D-200 product page:
  https://www.laserlands.net/diode-laser-module/500nm-green-laser-module/520nm-laser-module/4060-530d-200-12v-ttl.html

## Practical Takeaway

I can progress without asking for calipers right now.

The next web-first modeling pass should build/verify:

1. DIP-8 package geometry for MCP4822 and TL072.
2. 0805, TO-92, and other standard packages.
3. ESP32-S3 DevKitC candidate outline from official Espressif docs.
4. A source-marked "clone check required" overlay for U1, U3, GALVO_PSU,
   GALVO_DRV, GALVOS, LASER, CAM, and IMU.

Only after that should we ask for real-part photos/measurements, and only for
the parts the web cannot pin down.

