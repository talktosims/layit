# LayIt Laser — Bill of Materials v4
## Rev 1.1 (2026-05-06) — incorporates all fixes from FIXES_v1.md
## All parts SMD unless noted; intended for fabricated PCB

---

## ON-PCB COMPONENTS

### Active components (semiconductors, regulators, MCU)

| Ref | Part | Package / Spec | Qty | Notes |
|---|---|---|---|---|
| **U1** | **MP1584EN** buck converter module | 4-pin breakout | 1 | **Set to 5.0V output via trim pot before installing.** Replaces AMS1117-5.0 to fix overheating. |
| U2 | AMS1117-3.3 | SOT-223 | 1 | 3.3V LDO. Fed from U1's 5V output. |
| U3 | ESP32-S3-WROOM-1 N16R8 | Module | 1 | 16MB flash, 8MB Octal PSRAM. |
| U4 | MCP4822 | DIP-8 (or SOIC-8) | 1 | Dual 12-bit DAC, SPI. Use socket if DIP. |
| U5 | TL072 | DIP-8 (or SOIC-8) | 1 | Dual JFET op-amp. Use socket if DIP. |
| Q1 | 2N7000 | TO-92 (or SOT-23) | 1 | N-MOSFET, laser TTL inverter. |
| D1 | SS34 Schottky | SMA | 1 | Reverse polarity protection. |
| F1 | 3A PTC Fuse | 1206 | 1 | Resettable overcurrent. |
| LED1 | WS2812B | PLCC4 5×5mm | 1 | Status RGB LED. |
| **NEW** | **MPU6050 GY-521** module | breakout board | 1 | **Required by firmware for bump detection. Wired via I2C to GPIO1/2.** |

### Connectors and switches

| Ref | Part | Spec | Qty | Notes |
|---|---|---|---|---|
| J1 | (none) | - | 0 | USB-C PD trigger module is OFF-BOARD. Wires to PCB pads. |
| J2 | USB-C receptacle | GCT USB4500-03-0-A | 1 | Debug + firmware upload only. |
| J3 | JST-XH 3-pin vertical | B3B-XH-A | 1 | Laser module connector. |
| J4 | JST-XH 6-pin vertical | B6B-XH-A | 1 | Galvo driver connector. |
| J5 | FPC 24-pin | 0.5mm pitch | 1 | OV5640 camera ribbon. |
| J6 | 1×4 pin header 2.54mm | THT | 1 | UART programming (TX/RX/3V3/GND). |
| SW1 | Tactile button 6×6mm | THT | 1 | BOOT. |
| SW2 | Tactile button 6×6mm | THT | 1 | RESET. |
| SW3 | Microswitch | Omron D2F-01L | 1 | Lid interlock. **Wire COM + NO terminals (NOT NC).** Mounts on lid. |

### Passive components (resistors)

| Ref | Value | Package | Qty | Purpose |
|---|---|---|---|---|
| R1, R2 | 10K | 0805 | 2 | EN + GPIO0 pull-ups (ESP32 boot). |
| **R3, R4** | **5.1K** | **0805** | **2** | **USB-C CC1/CC2 pull-downs. (CRITICAL — without these the USB-C port doesn't work.)** |
| R9 | 4.7K | 0805 | 1 | Laser TTL drain pull-up. |
| R10 | 100Ω | 0805 | 1 | Q1 gate series resistor (current limit). |
| R11, R12 | 4.7K | 0805 | 2 | Camera I2C SDA/SCL pull-ups. |
| R13 | 10K | 0805 | 1 | Camera RESET pull-up. |
| R14 | 10K | 0805 | 1 | Camera PWDN pull-down. |
| R15 | 10K | 0805 | 1 | Safety interlock pull-up. |
| **R16** | **10K** | **0805** | **1** | **NEW — Q1 gate pull-up to 3.3V. Keeps laser OFF at boot.** |
| **R17** | **470Ω** | **0805** | **1** | **NEW — WS2812B data line series resistor.** |

### Removed from previous BOM

| Ref | Was | Removed Because |
|---|---|---|
| ~~R5, R7~~ | ~~10K op-amp input~~ | Op-amp simplified to unity-gain follower — no series resistor needed. |
| ~~R6, R8~~ | ~~24K op-amp feedback~~ | Op-amp simplified to unity-gain follower — no feedback divider needed. |

### Passive components (capacitors)

| Ref | Value | Package | Qty | Purpose |
|---|---|---|---|---|
| C1 | 470µF 25V | THT radial, 10mm | 1 | Bulk input filter. |
| C2 | 100nF | 0805 | 1 | 12V rail bypass. |
| C3 | 22µF 10V | 1206 ceramic or tantalum | 1 | 5V output bulk cap (after MP1584). |
| C4 | 100nF | 0805 | 1 | 5V rail bypass. |
| C5 | 22µF 10V | 1206 ceramic or tantalum | 1 | 3.3V output bulk cap (after AMS1117-3.3). |
| C6 | 100nF | 0805 | 1 | 3.3V rail bypass. |
| C7 | 10µF | 0805 ceramic | 1 | ESP32 power filter. |
| C8, C9 | 100nF | 0805 | 2 | ESP32 power decoupling. |
| C10 | 100nF | 0805 | 1 | MCP4822 VDD bypass. |
| C11 | 100nF | 0805 | 1 | TL072 VDD bypass. |
| C12 | 100nF | 0805 | 1 | Camera 3.3V bypass. |

### ESD protection (NEW, all SMD)

| Ref | Part | Package | Qty | Purpose |
|---|---|---|---|---|
| TVS1 | USBLC6-2P6 | SOT-23-6 | 1 | USB-C D+/D- ESD protection. |
| TVS2 | PESD5V0S1UB | SOD-323 | 1 | Laser TTL ESD. |
| TVS3-6 | PESD5V0S1UB | SOD-323 | 4 | Galvo signal pins ESD. |

---

## OFF-BOARD COMPONENTS

| Part | Spec | Qty | Source |
|---|---|---|---|
| USB-C PD trigger board | 12V output, ZY12PDN or similar | 1 | Amazon/AliExpress (~$5). Provides 12V from any USB-C PD wall charger. |
| Laser module | Laserland 4060-530D-200, 200mW 520nm green, 12V TTL | 1 | laserlands.net (~$38). |
| Galvo scanner set + driver | 20K PPS dual-axis with mirrors | 1 | AliExpress (~$70-120). **Verify input voltage range (0-5V single-ended preferred) before fab.** |
| OV5640 camera module | 5MP, 24-pin DVP, 160° wide-angle lens, FPC ribbon | 1 | AliExpress / Amazon (~$15-30). |
| USB-C PD wall charger | 20W or higher, PD3.0 | 1 | Any modern PD charger. |
| USB-C cable | 100W rated, ~6 ft | 1 | Generic. |
| Aluminum enclosure | ~6"×4"×3" vented, with tripod mount | 1 | Hammond 1455 series or generic. |
| 1/4-20 brass threaded insert | Standard tripod mount | 1 | McMaster-Carr or Amazon. |
| Laser safety glasses | OD4+ at 520nm | 1 | Amazon (~$15). **Mandatory.** |
| Hookup wire | 24 AWG, 6 colors (red/black/white/yellow/blue/green) | 1 kit | Amazon (~$10). |
| JST-XH connector kit | 3-pin and 6-pin housings + crimped wires | 1 kit | Amazon (~$8). |
| FPC 24-pin ribbon cable | 0.5mm pitch, ~10cm | 1 | AliExpress. |

---

## TOTAL ESTIMATED BOM COST (qty 1 prototype)

| Category | Cost |
|---|---|
| PCB fabrication (5 boards, JLCPCB) | $5–10 |
| PCB SMT assembly service (optional) | $15–25 |
| All on-PCB SMD parts (resistors, caps, ICs, TVS) | ~$15 |
| MP1584EN buck module | $1 |
| MPU6050 GY-521 module | $3 |
| Off-PCB hardware (laser, galvos, camera, enclosure, etc.) | ~$200 |
| **Total per prototype** | **~$240–270** |

(Per FIXES_v1.md, fixes add ~$3-5 to BOM cost. Substantially cheaper than the wrong path of ordering parts that won't work.)

---

## Sourcing notes

- **DigiKey or Mouser** for U1, U2, U3, U4, U5, ICs, TVS diodes, and any specific-part-number components. Authentic parts.
- **AliExpress** for galvos, laser, camera, MP1584 module — known-good cheap sources for these specific commodities.
- **Amazon** for fast shipping of resistor/capacitor kits and connectors.
- **JLCPCB** for fab + SMT assembly; their parts library covers ~80% of typical BOMs at low cost.

---

## Pin assignment summary (firmware reference)

| ESP32-S3 GPIO | Function | Notes |
|---|---|---|
| EN | Reset | R1 pull-up + SW2 button |
| GPIO0 | Boot | R2 pull-up + SW1 button |
| GPIO1, 2 | I2C SDA, SCL | Camera + IMU shared bus |
| GPIO4–9 | Camera DVP (VSYNC, HREF, PCLK, XCLK, D6, D7) | Standard Espressif camera pinout |
| GPIO10–13 | SPI to MCP4822 (CS, MOSI, CLK, LDAC) | |
| GPIO14 | Laser TTL via Q1 | **Pull-up R16 added; HIGH at boot keeps laser OFF.** |
| GPIO15–18 | Camera D2–D5 | |
| GPIO19, 20 | Native USB D-, D+ | |
| **GPIO40, 41** | **Camera D8, D9 (NEW — moved off bootstrap pins 45/46)** | |
| GPIO47 | Safety interlock | R15 pull-up; SW3 to GND |
| GPIO48 | Status LED | R17 series + LED1 DIN |

GPIO45, 46 = unused / leave floating. They are bootstrap pins and the camera should not be wired to them.
