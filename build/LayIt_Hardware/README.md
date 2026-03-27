# LayIt Laser — Hardware Engineering Package
## Version 1.0 | February 2026

---

## What Is This?

This package contains the starting engineering deliverables for the **LayIt Laser** — a compact laser projection system that projects tile installation patterns onto walls and floors. It receives pattern data from the LayIt smartphone app (PWA) via WiFi and drives a galvanometer-based laser scanner to draw tile outlines in real-time.

**This is a DRAFT engineering package.** It provides a complete starting point for an electrical engineer to review, refine, and bring to a physical prototype.

---

## Package Contents

```
LayIt_Hardware/
├── README.md                           ← You are here
├── schematic/
│   ├── LayIt_Laser.kicad_sch           ← KiCad 7+ schematic file
│   └── LayIt_Laser_Circuit_Description.md  ← Human-readable circuit docs
├── firmware/
│   ├── LayIt_Laser.ino                 ← ESP32-S3 Arduino firmware (complete)
│   ├── README_firmware.md              ← Build instructions & protocol docs
│   └── lib/                            ← (empty — libraries installed via Arduino IDE)
├── bom/
│   └── LayIt_Laser_BOM.csv             ← Engineer-ready BOM with part numbers
└── docs/                               ← (reserved for future docs)
```

---

## System Overview

### What It Does
1. User designs a tile layout in the LayIt app (free PWA)
2. App sends tile coordinates to the LayIt hardware via WiFi/WebSocket
3. ESP32-S3 converts tile vertex data into galvo scan paths
4. MCP4822 dual DAC outputs analog XY signals via TL072 op-amp buffer
5. Galvanometer mirrors steer a 520nm green laser to draw tile outlines
6. User lays tiles directly on the projected laser lines

### Core Signal Path
```
LayIt App (phone)
    │ WiFi / WebSocket (JSON)
    ▼
ESP32-S3-WROOM-1 (N16R8)
    │ SPI @ 10MHz
    ▼
MCP4822 Dual 12-bit DAC
    │ 0-4.096V analog
    ▼
TL072 Dual Op-Amp (buffer/scale)
    │ Scaled analog for galvo input
    ▼
Galvo Driver Board (20K PPS)
    │ Motor drive signals
    ▼
Dual-Axis Galvanometer Mirrors
    │ Steered laser beam
    ▼
520nm 200mW Green Laser (TTL blanked)
    │
    ▼
Wall / Floor (projected tile pattern)
```

---

## What the Engineer Needs to Do

### Phase 0: Breadboard Proof of Concept (DO THIS FIRST)

Before touching KiCad or ordering PCBs, validate the core signal path on a breadboard. This proves the system works end-to-end with zero risk and minimal cost.

**Step 1 — Galvos steering a dot**
- [ ] Wire ESP32-S3 dev board → MCP4822 DAC via SPI (MOSI, SCK, CS, LDAC)
- [ ] Wire MCP4822 outputs → TL072 op-amp buffer → galvo driver board inputs
- [ ] Power galvo driver board from 12V USB-C PD trigger board
- [ ] Power ESP32-S3 from 5V regulator off 12V rail
- [ ] Upload basic test firmware: output a slow sine wave on both DAC channels
- [ ] Verify galvo mirrors move in a controlled pattern (should trace a circle/figure-8)
- [ ] No laser yet — use a flashlight or phone light to see mirror movement

**Step 2 — Laser fires through TTL**
- [ ] Wire 2N7000 MOSFET: ESP32 GPIO → gate, 12V pull-up → drain, laser TTL → drain
- [ ] Connect laser module to 12V rail + TTL from MOSFET drain
- [ ] **PUT ON SAFETY GLASSES (OD4+ at 520nm) — mandatory from this point forward**
- [ ] Upload firmware that toggles laser TTL on/off at 1Hz (blink test)
- [ ] Verify laser blinks on command
- [ ] Combine: galvo steering + laser on = dot should trace a visible pattern on wall/floor

**Step 3 — App connection via WiFi**
- [ ] Upload full LayIt firmware (WiFi AP + WebSocket server)
- [ ] Connect phone to "LayIt-Laser" WiFi network
- [ ] Open LayIt app, go to Projection tab
- [ ] Send a simple rectangle or single tile outline
- [ ] Verify laser draws the shape on the wall/floor
- [ ] **Milestone: first projected tile line from the app. Film this.**

**Step 4 — Camera (optional at this stage)**
- [ ] Wire OV5640 camera module to ESP32-S3 DVP pins
- [ ] Verify camera captures a frame and streams to serial/WiFi
- [ ] Camera calibration and vision alignment can wait until PCB phase

Once Steps 1-3 work on the breadboard, you have a functioning proof-of-concept. Everything after this is refinement — PCB layout, enclosure, polish.

---

### Phase 1: Review & Refine Schematic
- [ ] Open `schematic/LayIt_Laser.kicad_sch` in KiCad 7+
- [ ] Draw wires according to the connection list in the `.kicad_sch` comments and `Circuit_Description.md`
- [ ] Verify galvo driver board input requirements (voltage range, single-ended vs. differential)
- [ ] Decide on TL072 supply: single-supply (current design) vs. split supply (if galvos need true ±5V)
- [ ] Verify OV5640 camera module FPC pinout matches J5 assignment
- [ ] Run ERC (Electrical Rules Check) and resolve any issues
- [ ] Add any missing protection (TVS diodes, EMI filtering, etc.)

### Phase 2: PCB Layout
- [ ] Create PCB from verified schematic
- [ ] ESP32-S3 antenna keepout zone (no copper within 10mm of antenna edge)
- [ ] Place DAC + op-amp close together to minimize analog noise
- [ ] Solid ground plane under analog section
- [ ] Keep 12V power traces wide (1A+ for laser)
- [ ] Add test points: +12V, +5V, +3.3V, GND, DAC_A, DAC_B, LASER_TTL
- [ ] Add mounting holes matching chosen enclosure
- [ ] Consider 2-layer vs. 4-layer (4-layer preferred for better ground plane)
- [ ] Board dimensions to fit Hammond 1455N1601BK enclosure (~6"x4")

### Phase 3: Prototype Assembly & Test
- [ ] Order PCB from JLCPCB/PCBWay/OSHPark
- [ ] Assemble and power up (check voltage rails first, no modules connected)
- [ ] Verify: +12V rail, +5V rail, +3.3V rail within spec
- [ ] Connect ESP32-S3, verify USB serial output
- [ ] Upload firmware via Arduino IDE
- [ ] Connect to "LayIt-Laser" WiFi, verify WebSocket communication
- [ ] Connect DAC, verify SPI waveforms with oscilloscope
- [ ] Connect galvo driver, verify mirror movement
- [ ] Connect laser (with safety glasses!), verify TTL blanking
- [ ] Full integration test with LayIt app

### Phase 4: Enclosure
- [ ] Drill/mill enclosure for: USB-C PD port, laser aperture, camera lens, status LED
- [ ] Install 1/4-20 tripod mount on bottom
- [ ] Install safety interlock microswitch on lid
- [ ] Route and dress internal wiring
- [ ] Verify safety interlock kills laser when lid is removed

---

## Key Design Decisions (For Engineer's Context)

### Why ESP32-S3 (not regular ESP32)?
- Native USB support (no external FTDI/CP2102 needed)
- Camera DVP interface (8-bit parallel, needed for OV5640)
- 8MB PSRAM for large pattern data buffering
- Faster CPU (240MHz dual-core) for scan loop timing

### Why MCP4822 (not ESP32 internal DAC)?
- 12-bit resolution (ESP32 DAC is only 8-bit)
- Dual channel with simultaneous latch (/LDAC) — critical for X/Y sync
- Internal voltage reference (stable, temperature-compensated)
- SPI interface — fast, simple, reliable

### Why TL072 Op-Amp Buffer?
- JFET input: high impedance, won't load the DAC
- Low noise: important for clean galvo signals (jitter = line wobble)
- Widely available, cheap, well-documented
- DIP-8 package for easy prototyping

### Why 200mW Laser (not 50mW)?
- Only ~$1 more expensive than 50mW
- 4x brighter lines visible in daylight/lit rooms
- Same footprint and pinout
- Both models ship with 200mW (per product spec)

### Why 2N7000 MOSFET (not direct GPIO)?
- Laser TTL needs 12V logic level; ESP32 GPIO is 3.3V
- 2N7000 is a logic-level MOSFET (turns on fully at 3.3V gate)
- Open-drain with pull-up gives clean 12V TTL signal
- Handles 15kHz TTL switching easily (nanosecond response)

---

## Companion Documents (On Desktop)

These existing documents provide additional product context:

| File | Location | Contents |
|------|----------|----------|
| LayIt_BOM_v3.md | Desktop | Detailed BOM with sourcing notes for both Flagship & Pro models |
| LayIt_BOM_Sourcing.html | Desktop | Interactive sourcing guide with supplier links |
| LayIt_Component_Shopping_List.html | Desktop | Shopping list with direct purchase URLs |
| LayIt_Laser_Product_Spec_v2.docx | Desktop | Full product specification document |
| LayIt_Laser_Build_Guide_v2.docx | Desktop | Assembly/build instructions |
| LayIt_Laser_Product_Spec.md | Downloads/Projects/LayIt/ | Comprehensive spec (markdown format) |

---

## Software / App Integration

The LayIt app is a PWA (Progressive Web App) hosted at:
**https://talktosims.github.io/layit/**

Source code: `/Users/Sims/Desktop/layit/index.html` (single-file app)

### Data Format
The app exports tile patterns in `.layit` format (JSON):
- All coordinates in **inches**
- Origin (0,0) at wall bottom-left
- Tile vertices are pre-clipped to wall boundaries
- Voids (windows, outlets) are defined as rectangles

### Communication Protocol
- WiFi connection to device AP ("LayIt-Laser")
- WebSocket on port 81
- JSON messages for all commands (see `firmware/README_firmware.md`)

---

## Safety Requirements

### Laser Safety (Class 3B — 200mW)
- **Safety labeling required** on enclosure (Class 3B warning label)
- **Safety interlock** on enclosure lid (microswitch, firmware-enforced)
- **Laser safety glasses** (OD4+ at 520nm) included in box
- **Auto-timeout**: laser disables after 5 minutes of no communication
- **Regulatory**: FDA/CDRH compliance required before sale (21 CFR 1040.10)

### Electrical Safety
- Reverse polarity protection (Schottky diode D1)
- Overcurrent protection (resettable PTC fuse F1)
- Low-voltage DC only (12V, no mains voltage)

---

## Budget Estimate (Prototype)

| Category | Cost |
|----------|------|
| PCB fabrication (5 boards) | $25-50 |
| PCB components (BOM above) | ~$15 per board |
| Laser module | $38 |
| Galvo scanner set | $70-120 |
| Camera module | $15-30 |
| Power adapter | $8-12 |
| Enclosure + hardware | $30-40 |
| **Total per prototype** | **~$200-280** |

---

*Generated February 2026 — LayIt*
