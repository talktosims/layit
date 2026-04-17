# LayIt Laser — Bill of Materials v3.2
## Flagship ($499) & Pro ($649) Models
## Both models now ship with 200mW laser

---

## FLAGSHIP MODEL — LayIt Laser ($499)
### USB-C PD Powered, 200mW Laser

| # | Component | Specification | Est. Cost | Source |
|---|-----------|--------------|-----------|--------|
| 1 | Laser Module | 520nm Green, **200mW**, 12V, TTL 15kHz, direct diode, DOT | $35-45 | Laserland 4060-530D-200: laserlands.net (~$38) |
| 2 | Galvanometer Set | 20K PPS, dual-axis, with mirrors | $45-65 | AliExpress: search "20K galvo scanner set" / eBay |
| 3 | Galvo Driver Board | ±5V analog input (ILDA-standard), bundled with galvo set | $0 (bundled) | Included with galvo scanner set |
| 4 | ESP32-S3-WROOM-1 | N16R8 (16MB flash, 8MB PSRAM) | $8-12 | Amazon: "ESP32-S3-WROOM-1 N16R8" |
| 5 | Camera Module | OV5640, 5MP, 160° wide-angle, DVP | $30-45 | AliExpress / Amazon: "OV5640 wide angle DVP" |
| 6 | DAC (Dual Channel) | MCP4822 or MCP4922, SPI, DIP/SOIC | $3-5 | DigiKey / Mouser / Amazon: "MCP4822" |
| 7 | Op-Amp Buffer | TL072 dual op-amp | $1-2 | Amazon: "TL072 DIP" |
| 8 | USB-C PD Trigger Board | 12V output, PD3.0 negotiation | $5-8 | Amazon/AliExpress: "USB-C PD trigger board 12V" |
| 9 | USB-C PD Cable | 100W PD capable, 6ft, braided | $5-8 | Amazon: "USB-C PD 100W cable 6ft" |
| 10 | Voltage Regulators | AMS1117-5.0 + AMS1117-3.3 | $2-3 | Amazon: "AMS1117 5V 3.3V regulator kit" |
| 11 | Enclosure | Aluminum, 6"×4"×3", vented, tripod mount | $25-35 | Amazon: "aluminum project enclosure" / Hammond Mfg |
| 12 | Tripod Mount | 1/4"-20 threaded insert | $1-2 | Amazon: "1/4-20 threaded insert for tripod" |
| 13 | Misc | PCB prototype board, JST connectors, wires, headers, screws, standoffs, laser safety lens | $15-25 | Amazon: "PCB prototype board kit" + "JST connector assortment" |
| 14 | IMU / Accelerometer | MPU6050 6-axis, I2C, bump detection for vision alignment | $2-3 | Amazon: "MPU6050 GY-521 module" / DigiKey |

| | **FLAGSHIP TOTAL BOM** | | **$239-314** | |

**Retail Price: $499**
**Gross Margin:** ~$188-263 (38-53%)

---

## PRO MODEL — LayIt Laser Pro ($649)
### USB-C PD Powered + Rechargeable Swappable Battery
### Same 200mW Laser as Flagship

The Pro model is identical to Flagship PLUS battery system for cordless operation.
**The only difference is the battery system — both models have the same 200mW laser.**

Pro power modes:
- **Battery mode:** Swappable 3S LiPo packs for cordless operation
- **USB-C plugged in:** System runs on USB-C power AND charges battery simultaneously
- **Switchover:** Automatic via priority diode circuit (~$2-3 component)

Everything in Flagship PLUS:

| # | Component | Specification | Est. Cost | Notes |
|---|-----------|--------------|-----------|-------|
| 15 | Battery Pack | 3S 11.1V 3000mAh LiPo, XT30 connector | $15-25 | NEW |
| 16 | Battery BMS Board | 3S 12.6V, 20A, with balance charging | $5-8 | NEW |
| 17 | Battery Sled/Bay | Removable housing with spring contacts, tool-free | $8-12 | NEW |
| 18 | USB-C Charging Circuit | 12.6V 3S Li-ion charger, CC/CV, 2A charge rate | $5-8 | NEW |
| 19 | Battery Level Indicator | 3S LED voltage display, panel mount | $2-3 | NEW |
| 20 | DC-DC Buck/Boost | 12V stable output from 9-12.6V battery range | $3-5 | NEW |
| 21 | Power Priority Diode | Schottky diode + relay for auto-switchover | $2-3 | NEW |
| 22 | Second Battery Pack | Spare swappable 3S 3000mAh (included in box) | $15-25 | NEW |

| | **PRO-ONLY ADDITIONS** | | **$55-89** | |
| | **PRO TOTAL BOM** | | **$294-403** | |

**Retail Price: $649**
**Gross Margin:** ~$249-358 (38-55%)

---

## PRO MODEL POWER DESIGN

### How It Works:
```
                    ┌─────────────────────┐
  USB-C PD (12V) ──→│ Priority Diode      │
                    │ (Schottky + Relay)  │──→ 12V Power Rail ──→ System
  Battery Pack ────→│ Auto-switchover     │
                    └─────────────────────┘
                              │
                    USB-C PD ─┘ (charges battery when plugged in)
```

### Power Priority Logic:
1. **USB-C plugged in** → System runs on USB-C power, battery charges via BMS
2. **USB-C unplugged** → Automatic switchover to battery (no interruption)
3. **Battery removed** → Must use USB-C power (unit still fully functional)
4. **Both disconnected** → Unit off

### Battery Specs:
- **Chemistry:** 3S Lithium Polymer (11.1V nominal, 12.6V full)
- **Capacity:** 3000mAh (~33Wh)
- **Runtime:** ~1.5-2 hours continuous projection
- **Charge Time:** ~1.5 hours via USB-C PD (2A)
- **Swappable:** Slide-out battery bay, tool-free
- **Spare Included:** Pro ships with 2 battery packs for continuous use
- **On-unit indicator:** LED battery level display visible without removing pack

---

## LASER MODULE — BOTH MODELS

### The Module:
- **Laserland 4060-530D-200** — 520nm 200mW Direct Diode, 12V, TTL 15kHz
- **Price:** ~$38
- **Buy from:** https://www.laserlands.net/4060-530d-200-12v-ttl.html
- Also available via Laserland's AliExpress store

### Why 200mW for both:
- 200mW module costs ~$38 vs ~$37 for 50mW — negligible difference
- 4× brighter lines visible in well-lit kitchens and bathrooms
- Better experience out of the box for ALL users
- No reason to ship an inferior laser when the cost is identical

### Specs:
- Wavelength: 520nm (direct diode, NOT 532nm DPSS)
- Power: 200mW
- Voltage: 12V DC
- Current: <1.2A
- TTL: 15kHz (sufficient for static tile pattern projection)
- Operating temp: -15°C to 45°C
- Beam diameter: 12-15mm
- Pattern: DOT output (galvos steer to draw lines)

### What to AVOID when shopping:
- ❌ 532nm DPSS modules (slow TTL response, temperature sensitive)
- ❌ "Line" or "cross" pattern modules (you need DOT — galvos steer the dot)
- ❌ 3V or 5V modules (wrong voltage rail)
- ❌ No-name modules without TTL driver (need TTL for blanking between segments)

---

## MODEL COMPARISON

| Feature | Flagship ($499) | Pro ($649) |
|---------|----------------|------------|
| Laser | 200mW 520nm | 200mW 520nm (same) |
| Auto-calibration camera | ✅ | ✅ |
| USB-C PD power | ✅ | ✅ |
| Swappable battery | ❌ | ✅ (2 included) |
| Cordless operation | ❌ | ✅ (~1.5-2hr per battery) |
| Auto cord/battery switchover | N/A | ✅ |
| Battery level indicator | N/A | ✅ |
| Tripod mount | ✅ | ✅ |
| WiFi + BLE | ✅ | ✅ |
| LayIt App (free) | ✅ | ✅ |

**The $150 premium is purely for the battery packs and cordless operation. Both models use the same USB-C port — Flagship for power only, Pro for power + charging.**

---

## SOURCING PRIORITY

### Best for Prototyping (fast shipping, USA):
1. **Amazon** — ESP32-S3, power supplies, enclosures, misc electronics
2. **Adafruit / SparkFun** — ESP32-S3 dev boards, breakout boards
3. **DigiKey / Mouser** — DAC, op-amps, voltage regulators (exact parts, datasheets)

### Best for Cost (2-4 week shipping):
1. **AliExpress / Laserland** — Laser modules, galvo sets, camera modules
2. **eBay** — Galvo scanner sets, laser modules

### Recommended Order of Purchase:
1. **Order first (longest lead time):** Galvo set + driver from AliExpress (2-4 weeks)
2. **Order second:** Laser module from Laserland, OV5640 camera from AliExpress (2-3 weeks)
3. **Order last (fast shipping):** ESP32-S3, DAC, op-amp, USB-C PD trigger board, enclosure from Amazon/DigiKey

---

## WHAT SHIPS IN THE BOX

### Flagship ($499):
- LayIt Laser unit (200mW)
- USB-C PD cable (6ft, 100W — main power source)
- Tripod mount (1/4"-20)
- Quick start guide
- Laser safety glasses (OD4+ at 520nm)

### Pro ($649):
- LayIt Laser Pro unit (200mW)
- **USB-C PD cable (6ft, 100W — power + charging)**
- **2× swappable battery packs**
- Tripod mount (1/4"-20)
- Quick start guide
- Laser safety glasses (OD4+ at 520nm)

---

## NOTES
- Both models use the same LayIt app (free)
- Both include auto-calibration camera
- Both ship with identical 200mW laser
- Both use USB-C PD as the sole power input — no barrel jack
- Pro enclosure is slightly larger to accommodate battery bay
- Flagship could be field-upgraded with battery kit (future accessory: "LayIt Battery Upgrade Kit" ~$99?)
- All prices estimated for single-unit prototype quantities; bulk pricing would reduce 20-40%
- Laser safety: 200mW = Class 3B — safety labeling required for BOTH models
- Laser safety glasses MUST be included in box for both models

---

## COMPONENT CHANGES — USB-C Migration

### Components to RETURN (when they arrive):
- 12V 3A DC adapter (5.5x2.1mm barrel jack)
- Barrel jack connectors (panel mount)

### Components to ORDER:
- USB-C PD Trigger Board (12V output, PD3.0 negotiation) — needed for Flagship; Pro already had one in BOM
- USB-C PD Cable (100W, 6ft) — needed for Flagship; Pro already had one in BOM
- (Check if Pro USB-C PD trigger board and cable were already ordered — if so, order one more set for Flagship)

### Components UNCHANGED:
- Laser module (Laserland 4060-530D-200)
- Galvanometer set + driver board
- ESP32-S3-WROOM-1 (N16R8)
- Camera module (OV5640)
- DAC (MCP4822/MCP4922)
- Op-Amp (TL072)
- Voltage regulators (AMS1117)
- Enclosure + tripod mount
- IMU (MPU6050)
- All Pro battery components (battery packs, BMS, sled, charging circuit, indicator, buck/boost, priority diode)
- Misc (PCB, connectors, wires, headers, screws, standoffs, laser safety lens)
