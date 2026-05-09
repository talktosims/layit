# LayIt Laser — Engineering Fixes v1
## Date: 2026-05-06
## Severity-ordered list of every issue and its fix

This document is the source of truth for every change between **Rev 1.0** (broken design) and **Rev 1.1** (fixed). All other docs (BOM v4, build addendum, firmware pin map, KiCad PCB) derive from this.

---

## 🔴 CRITICAL

### F-1 · Replace U1 (AMS1117-5.0) with MP1584EN buck converter
**Problem:** U1 dissipates ~5W (1A × 7V drop) when feeding cascaded 3.3V regulator. SOT-223 thermal limit is ~1W. U1 burns out.
**Fix:** Swap U1 for an MP1584EN buck-converter module (~$1, eBay/AliExpress, "MP1584EN mini DC-DC step down"). The module is a 4-pin breakout: VIN, GND, VOUT, EN. Set output to 5.0V via the onboard trim pot before wiring.
**BOM impact:** Drop AMS1117-5.0; add 1× MP1584EN module.
**Schematic impact:** Replace U1's SOT-223 pads with a 4-pin 0.1" header for the buck module. Output cap C3 (22µF) stays on output side.

### F-2 · Add R16 (10K) pull-up on Q1 gate
**Problem:** GPIO14 floats at boot until firmware runs `pinMode(OUTPUT)`. During that window, gate floats LOW → MOSFET OFF → R9 pulls TTL to 12V → laser fires.
**Fix:** Add R16 = 10K from Q1 gate (between R10 and gate, OR between gate and 3.3V) to +3.3V. With pull-up, gate is HIGH at boot → MOSFET ON → TTL LOW → laser OFF until firmware confirms.
**BOM impact:** +1× 10K 0805 (R16).

### F-3 · Re-pin camera D8/D9 off bootstrap pins
**Problem:** GPIO45 and GPIO46 are ESP32-S3 strapping pins. GPIO46 HIGH at boot triggers ROM bootloader. Camera asserting D9 at boot prevents firmware from running.
**Fix:** Move CAM_D8 from GPIO45 → **GPIO40**, and CAM_D9 from GPIO46 → **GPIO41**. Both are general-purpose, not strapped, exposed on WROOM-1 N16R8.
**Firmware impact:** `LayIt_Laser.ino` lines 66–67 — change `#define PIN_CAM_D8 45` → `40`, `#define PIN_CAM_D9 46` → `41`.
**Schematic impact:** Swap J5 traces from ESP32 GPIO45/46 → GPIO40/41.

### F-4 · SMD parts on fabricated PCB (not perfboard)
**Problem:** All your parts are SMD. Perfboard build is impossible.
**Fix:** Use the auto-generated `LayIt_Laser.kicad_pcb` (already has all 41 footprints placed correctly). Send Gerbers to JLCPCB/PCBWay. Optional: use JLCPCB's SMT Assembly service to have them populate SMD parts.

---

## 🟡 MAJOR

### F-5 · Op-amp simplified to unity-gain voltage follower
**Problem:** Original schematic's op-amp topology ambiguous; resistor values may not match galvo driver input range.
**Fix:** Reconfigure TL072 channels A and B as **voltage followers**. Connect each DAC output directly to the op-amp's (+) input. Connect the op-amp's output directly back to its own (-) input (no resistors). Output goes to galvo driver input.
**Result:** Galvo driver receives 0–4.096V single-ended directly buffered from DAC. No gain stage to mis-tune.
**BOM impact:** Drop R5, R6, R7, R8 (4 resistors removed).
**Caveat:** If your specific galvo driver expects ±5V differential, you'll need to add a charge pump (ICL7660) for -12V rail and a separate gain stage. Default assumption: galvo driver accepts 0–5V single-ended (most "20K PPS galvo scanner kit" drivers do).

### F-6 · Safety interlock wiring corrected
**Problem:** Binder Section 4 says wire COM+NC; logic requires COM+NO.
**Fix:** Wire SW3's **COM** terminal to one PCB pad and **NO** terminal to the other.
**Test:** With multimeter in continuity mode, lid CLOSED should beep, lid OPEN should not.

### F-7 · Add R3, R4 USB-C CC pull-down resistors to BOM and binder
**Problem:** R3 and R4 (5.1K each, USB-C CC1/CC2 → GND) are in the schematic but missing from the binder parts checklist. Without them, USB-C debug port doesn't enumerate; firmware uploads fail.
**Fix:** Add to BOM and binder.
**BOM impact:** +2× 5.1K 0805.

### F-8 · Add MPU6050 IMU to binder
**Problem:** BOM v3 includes MPU6050 GY-521 module ($2-3). Firmware actively uses it for bump detection and tilt compensation. Binder Section 2 doesn't include it.
**Fix:** Add MPU6050 GY-521 breakout to binder parts list. Wire VCC → 3.3V, GND → GND, SDA → ESP32 GPIO1 (shared with camera I2C), SCL → ESP32 GPIO2.

---

## 🟠 MODERATE

### F-9 · Add ESD/TVS protection on external connectors
**Problem:** USB-C, JST, FPC, microswitch wires are user-touchable. Static discharge can kill ESP32 or camera.
**Fix:** Add TVS diodes (PESD5V0S1UB or USBLC6-2P6 for USB-C) across:
- USB-C D+/D- (1× USBLC6-2P6 or 2× PESD3V3S1UB)
- J3 laser TTL pin to GND (1× PESD5V0S1UB)
- J4 galvo signal pins (4× PESD5V0S1UB)
- J5 FPC critical pins (optional)
**BOM impact:** +6× TVS diodes (~$0.10 each).

### F-10 · Schottky drop noted in spec
**Problem:** SS34 drops ~0.4V → "12V" rail is actually ~11.6V at full load.
**Fix:** Document in spec. If laser/galvo brownout under load, swap SS34 for a P-MOSFET ideal-diode (SiR642DP, ~$1) which drops <0.1V.

### F-11 · Status LED series resistor
**Problem:** No resistor on WS2812B DIN line.
**Fix:** Add R17 = 470Ω in series between GPIO48 and LED1 DIN. Cheap insurance for signal integrity and ESD.
**BOM impact:** +1× 470Ω 0805.

---

## 🟢 RESIDUAL CAVEATS (need physical-world data — flag for EE review)

- **Galvo driver input range** — assumed 0-5V single-ended. **Verify with your specific 20K PPS galvo driver before fab.** If it's ±5V differential, add charge pump + redesign op-amp stage.
- **MP1584 module mounting** — buck modules are 17×11mm boards with 4-pin headers. The PCB needs space for them. The current KiCad layout uses the original SOT-223 footprint; manual rework needed.
- **Antenna keepout** — verify no copper or components within 10mm of ESP32 antenna in final PCB.
- **Class 3B laser regulatory** — FDA/CDRH compliance (21 CFR 1040.10) is required before any sale. Hire a regulatory consultant before commercial release.

---

## Summary of BOM additions / removals

| Action | Part | Qty | Ref |
|---|---|---|---|
| ADD | MP1584EN buck module | 1 | replaces U1 |
| ADD | 10K 0805 resistor | 1 | R16 (Q1 gate pullup) |
| ADD | 5.1K 0805 resistor | 2 | R3, R4 (USB-C CC) |
| ADD | 470Ω 0805 resistor | 1 | R17 (LED data) |
| ADD | MPU6050 GY-521 module | 1 | IMU |
| ADD | PESD5V0S1UB TVS diode | 5 | external connector ESD |
| ADD | USBLC6-2P6 TVS array | 1 | USB-C D+/D- ESD |
| REMOVE | AMS1117-5.0 | 1 | superseded by MP1584 |
| REMOVE | 10K 0805 (R5, R7) | 2 | unity-gain follower |
| REMOVE | 24K 0805 (R6, R8) | 2 | unity-gain follower |

**Net change:** +5 unique part numbers added, −2 removed.
