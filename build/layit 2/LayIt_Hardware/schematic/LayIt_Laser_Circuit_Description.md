# LayIt Laser — Circuit Description & Connection Reference
## Rev 1.0 | February 2026

This document accompanies the KiCad schematic file and provides a human-readable description of every circuit block, connection, and design decision.

---

## BLOCK DIAGRAM

```
                                    ┌─────────────────────────────────┐
                                    │         ESP32-S3-WROOM-1        │
                                    │           (N16R8)               │
                                    │                                 │
  ┌──────────┐   ┌──────────┐      │  SPI Bus    ┌─────────┐        │
  │ 12V DC   │──→│ Reverse  │──→12V│──(GPIO10-13)─│MCP4822  │        │
  │ Barrel   │   │ Polarity │  Rail│             │Dual DAC │        │
  │ Jack     │   │ + Fuse   │      │             └────┬────┘        │
  └──────────┘   └──────────┘      │                  │              │
        │                          │          ┌───────▼───────┐      │
        │         ┌────────┐       │          │   TL072       │      │
        ├────────→│AMS1117 │──→5V──┘          │  Dual Op-Amp  │      │
        │         │ -5.0   │                  │  (Buffer/Amp) │      │
        │         └────────┘                  └───┬───────┬───┘      │
        │                                         │       │          │
        │         ┌────────┐                ┌─────▼─┐ ┌───▼───┐     │
        ├────────→│AMS1117 │──→3.3V──→ESP32 │Galvo X│ │Galvo Y│     │
        │         │ -3.3   │                │Driver │ │Driver │     │
        │         └────────┘                └───────┘ └───────┘     │
        │                                                            │
        │    ┌────────────────┐    GPIO14    ┌──────────┐           │
        ├───→│ 520nm 200mW   │◄──(MOSFET)───│ Laser    │           │
        │    │ Laser Module   │    TTL       │ TTL Ctrl │           │
        │    └────────────────┘              └──────────┘           │
        │                                                            │
        │                          DVP Bus    ┌──────────┐           │
        │                      (GPIO4-9,     │ OV5640   │           │
        │                       15-18,45,46)─│ Camera   │           │
        │                      I2C(GPIO1,2)  │ 5MP 160° │           │
        │                                    └──────────┘           │
        │                                                            │
        │    ┌──────────┐      GPIO48        ┌──────────┐           │
        │    │ USB-C    │      (status)      │ WS2812B  │           │
        │    │ Debug    │──GPIO19,20         │ RGB LED  │           │
        │    └──────────┘                    └──────────┘           │
        │                                                            │
        │    ┌──────────┐      GPIO47        ┌──────────┐           │
        │    │ Safety   │──(interlock)       │ BOOT/RST │           │
        │    │ Switch   │                    │ Buttons  │           │
        │    └──────────┘                    └──────────┘           │
        │                                                            │
        └────────────────────────────────────────────────────────────┘
```

---

## 1. POWER INPUT & PROTECTION

### Components
| Ref | Part | Value | Purpose |
|-----|------|-------|---------|
| J1 | Barrel Jack | 5.5x2.1mm | 12V 3A DC input |
| D1 | SS34 Schottky | 3A 40V | Reverse polarity protection |
| F1 | PTC Fuse | 3A hold | Overcurrent protection (resettable) |
| C1 | Electrolytic | 470uF 25V | Bulk input filter |
| C2 | Ceramic | 100nF 25V | HF bypass |

### Circuit
```
J1 Pin1 (+) ──→ D1 Anode ──→ D1 Cathode ──→ F1 ──→ +12V RAIL
J1 Pin2 (-) ──→ GND RAIL
```

### Design Notes
- SS34 drops ~0.4V under load, so 12V input becomes ~11.6V at rail. Acceptable for all downstream components.
- PTC fuse protects against short circuits. Resets automatically after fault is cleared.
- 470uF bulk cap handles galvo motor current transients (galvos can draw brief spikes).

---

## 2. VOLTAGE REGULATION

### 5V Rail (U1 — AMS1117-5.0)
Powers: MCP4822 DAC (VDD), TL072 op-amp (V+)

| Ref | Part | Value | Purpose |
|-----|------|-------|---------|
| U1 | AMS1117-5.0 | SOT-223 | 12V→5V LDO, 1A max |
| C3 | Tantalum/Ceramic | 22uF 10V | Output stability |
| C4 | Ceramic | 100nF | HF decoupling |

### 3.3V Rail (U2 — AMS1117-3.3)
Powers: ESP32-S3, Camera module, I2C pull-ups, status LED, safety interlock

| Ref | Part | Value | Purpose |
|-----|------|-------|---------|
| U2 | AMS1117-3.3 | SOT-223 | 5V→3.3V LDO, 1A max |
| C5 | Tantalum/Ceramic | 22uF 10V | Output stability |
| C6 | Ceramic | 100nF | HF decoupling |

### Power Budget
| Consumer | Voltage | Max Current | Notes |
|----------|---------|-------------|-------|
| ESP32-S3 | 3.3V | 500mA (WiFi TX) | Peaks during WiFi transmission |
| OV5640 Camera | 3.3V | 140mA | During capture |
| MCP4822 DAC | 5V | 5mA | Negligible |
| TL072 Op-Amp | 12V | 10mA | Negligible |
| Laser Module | 12V | 1200mA | Direct from 12V rail |
| Galvo Driver | 12V | 500mA | From 12V rail, motor current |
| WS2812B LED | 3.3V | 60mA | Full white |
| **Total 12V** | | **~1.7A** | Well within 3A supply |
| **Total 5V** | | **~15mA** | Minimal load on U1 |
| **Total 3.3V** | | **~700mA** | Within U2 1A rating |

### ENGINEER NOTE — 5V→3.3V Cascade
U2 is fed from U1's 5V output (not directly from 12V). This reduces heat dissipation in U2. If U2 were fed from 12V directly: P = (12-3.3) * 0.7 = 6W (too hot for SOT-223). With 5V input: P = (5-3.3) * 0.7 = 1.2W (acceptable with thermal pad).

---

## 3. ESP32-S3 MICROCONTROLLER

### Pin Assignment Table

| GPIO | Function | Direction | Connected To | Notes |
|------|----------|-----------|--------------|-------|
| 3V3 | Power | IN | +3.3V rail | Via C7 (10uF) + C8 (100nF) bypass |
| GND | Ground | — | GND rail | Multiple ground pins, all connected |
| EN | Enable/Reset | IN | R1 (10K pull-up), C9 (100nF), SW2 | Active HIGH. Low resets chip. |
| GPIO0 | Boot Select | IN | R2 (10K pull-up), SW1 | Hold LOW during reset for download mode |
| GPIO1 | I2C SDA | I/O | Camera J5.SDA, R11 (4.7K pull-up) | SCCB protocol (I2C compatible) |
| GPIO2 | I2C SCL | OUT | Camera J5.SCL, R12 (4.7K pull-up) | 100kHz or 400kHz |
| GPIO4 | CAM VSYNC | IN | Camera J5.VSYNC | Frame sync |
| GPIO5 | CAM HREF | IN | Camera J5.HREF | Line valid |
| GPIO6 | CAM PCLK | IN | Camera J5.PCLK | Pixel clock |
| GPIO7 | CAM XCLK | OUT | Camera J5.XCLK | 20MHz reference clock to camera |
| GPIO8 | CAM D6 | IN | Camera J5.D6 | 8-bit parallel data |
| GPIO9 | CAM D7 | IN | Camera J5.D7 | 8-bit parallel data |
| GPIO10 | SPI CS | OUT | MCP4822 /CS (pin 2) | Active LOW chip select |
| GPIO11 | SPI MOSI | OUT | MCP4822 SDI (pin 4) | Serial data to DAC |
| GPIO12 | SPI CLK | OUT | MCP4822 SCK (pin 3) | SPI clock, up to 20MHz |
| GPIO13 | DAC LDAC | OUT | MCP4822 /LDAC (pin 5) | Pulse LOW to latch both channels simultaneously |
| GPIO14 | LASER TTL | OUT | R10 (100R) → Q1 Gate | HIGH = laser ON, LOW = laser OFF |
| GPIO15 | CAM D2 | IN | Camera J5.D2 | 8-bit parallel data |
| GPIO16 | CAM D3 | IN | Camera J5.D3 | 8-bit parallel data |
| GPIO17 | CAM D4 | IN | Camera J5.D4 | 8-bit parallel data |
| GPIO18 | CAM D5 | IN | Camera J5.D5 | 8-bit parallel data |
| GPIO19 | USB D- | I/O | J2 USB-C D- | Native USB (CDC/JTAG) |
| GPIO20 | USB D+ | I/O | J2 USB-C D+ | Native USB (CDC/JTAG) |
| GPIO45 | CAM D8 | IN | Camera J5.D8 | 8-bit parallel data |
| GPIO46 | CAM D9 | IN | Camera J5.D9 | 8-bit parallel data |
| GPIO47 | SAFETY | IN | SW3 + R15 (10K pull-up) | LOW = safe (lid closed), HIGH = kill laser |
| GPIO48 | STATUS LED | OUT | LED1 WS2812B DIN | Addressable RGB status indicator |

### Boot Mode
| EN | GPIO0 | Mode |
|----|-------|------|
| LOW | X | Reset (chip held in reset) |
| HIGH | HIGH | Normal boot (run firmware) |
| HIGH | LOW | Download mode (firmware upload via USB) |

---

## 4. DAC — MCP4822 (SPI, Dual 12-bit)

### Purpose
Converts digital galvo coordinates from ESP32 into analog voltage for the galvo amplifier.

### Pinout
| Pin | Name | Connection |
|-----|------|------------|
| 1 | VDD | +5V rail + C10 (100nF bypass) |
| 2 | /CS | ESP32 GPIO10 |
| 3 | SCK | ESP32 GPIO12 |
| 4 | SDI | ESP32 GPIO11 |
| 5 | /LDAC | ESP32 GPIO13 |
| 6 | VOUTA | R5 (10K) → TL072 Ch A input (Galvo X) |
| 7 | VOUTB | R7 (10K) → TL072 Ch B input (Galvo Y) |
| 8 | VSS | GND |

### SPI Protocol
- Mode 0,0 (CPOL=0, CPHA=0)
- 16-bit write: `[A/B][BUF][GA][SHDN][D11:D0]`
  - Bit 15: Channel select (0=A, 1=B)
  - Bit 14: Buffered (1=buffered Vref)
  - Bit 13: Gain (0=2x, 1=1x). Use 0 for 2x gain → 0-4.096V output
  - Bit 12: Shutdown (1=active, 0=shutdown)
  - Bits 11-0: 12-bit data value (0-4095)

### Output Range
- With 2x gain and internal 2.048V Vref: **0 to 4.096V**
- Resolution: 4.096V / 4096 = **1mV per step**
- Update rate: Limited by SPI speed. At 10MHz SPI clock, each 16-bit write takes 1.6μs. Writing both channels + LDAC pulse ≈ 4μs per point → **250,000 points/sec theoretical max** (well above 20K PPS galvo limit)

---

## 5. OP-AMP BUFFER/AMPLIFIER — TL072

### Purpose
Scales MCP4822 output (0-4.096V) to the voltage range required by the galvo driver board.

### Configuration: Non-Inverting Amplifier (Voltage Follower with Gain)

```
              R6 (24K)
         ┌────/\/\/────┐
         │             │
DAC_A ──R5(10K)──┤(+)     │
                 │  TL072  ├──→ Galvo X+ (J4 Pin 1)
            ┌───┤(-)     │
            │   │        │
            └───┴────────┘
```

### Gain Calculation
- Gain = 1 + (R6/R5) = 1 + (24K/10K) = **3.4x** (for voltage follower)
- OR if configured as inverting: Gain = R6/R5 = 24K/10K = **2.4x**

### ENGINEER NOTE — Galvo Input Requirements
Most hobby/consumer galvo driver boards accept **±5V analog input** (differential or single-ended). The exact voltage range depends on the specific galvo driver purchased. The engineer should:

1. Check the galvo driver board's input specification
2. Adjust R5/R6 values to match the required output swing
3. Consider whether a **virtual ground** (at Vdd/2) is needed for bipolar output
4. If galvos need true ±5V, add a charge pump IC (ICL7660 or MAX1044) to generate -12V rail for TL072 V-

### Current Design (Single Supply)
- TL072 V+ = +12V, V- = GND
- Output range: ~0V to ~10V (limited by rail saturation)
- Firmware maps galvo coordinates to this 0-10V range
- If galvo driver expects ±5V: subtract 5V offset at driver input, or redesign with split supply

---

## 6. LASER MODULE DRIVER

### Circuit
```
ESP32 GPIO14 ──R10(100Ω)──→ Q1 Gate
                              │
                     Q1 (2N7000 N-MOSFET)
                              │
                   +12V ──R9(4.7K)──┤ Drain ──→ J3 Pin 2 (Laser TTL)
                                    │
                              Source → GND
```

### Operation
- **GPIO14 HIGH** → Q1 turns ON → Drain pulled to GND → Laser TTL goes LOW
- **GPIO14 LOW** → Q1 turns OFF → R9 pulls TTL to +12V → Laser TTL goes HIGH

### IMPORTANT: Active Level
The Laserland 4060-530D-200 laser module is **TTL active HIGH** (12V = laser ON).
- So: ESP32 LOW → MOSFET OFF → TTL HIGH → **Laser ON**
- And: ESP32 HIGH → MOSFET ON → TTL LOW → **Laser OFF**
- **Firmware must invert the logic**: `digitalWrite(LASER_PIN, !laserState)`

### Switching Speed
- 2N7000 turn-on: ~10ns, turn-off: ~10ns
- R10 (100Ω) limits gate ringing
- Laser TTL rated for 15kHz → 66μs period. MOSFET is ~1000x faster than needed. No issues.

---

## 7. CAMERA — OV5640 (DVP Interface)

### Purpose
Auto-calibration: camera captures reference markers on the wall to calculate projection geometry and correct for distance/angle.

### Interface: 8-bit DVP (Digital Video Port)
- 8 data lines (D2-D9) → parallel pixel data
- VSYNC, HREF, PCLK → synchronization
- XCLK ← 20MHz reference clock from ESP32
- SCCB (I2C) ← configuration registers

### Pull-up/Pull-down Resistors
| Ref | Pin | Value | To | Purpose |
|-----|-----|-------|----|---------|
| R11 | SDA | 4.7K | 3.3V | I2C pull-up |
| R12 | SCL | 4.7K | 3.3V | I2C pull-up |
| R13 | RESET | 10K | 3.3V | Keep camera out of reset |
| R14 | PWDN | 10K | GND | Keep camera powered on |

### Camera Module Power
The OV5640 module board has its own 1.8V and 2.8V regulators. It only needs 3.3V input from our board.

---

## 8. SAFETY INTERLOCK

### Circuit
```
3.3V ──R15(10K)──┬──→ ESP32 GPIO47
                  │
             SW3 (microswitch, normally closed when lid is shut)
                  │
                 GND
```

### Operation
- **Lid closed**: SW3 closed → GPIO47 pulled LOW → **Safe, laser can operate**
- **Lid opened**: SW3 opens → R15 pulls GPIO47 HIGH → **UNSAFE, firmware kills laser immediately**

### Firmware Behavior
- GPIO47 is checked in the main projection loop (every cycle)
- Also configured as an interrupt for instant response
- Laser cannot be re-enabled until GPIO47 reads LOW again

---

## 9. STATUS LED — WS2812B

### Color Codes (defined in firmware)
| Color | Meaning |
|-------|---------|
| Solid Green | Ready, waiting for connection |
| Pulsing Blue | Connected to app, idle |
| Solid Blue | Projecting pattern |
| Pulsing Amber | Calibrating |
| Solid Red | Error (safety interlock, overtemp, etc.) |
| Rainbow Cycle | Firmware update in progress |

---

## 10. USB-C (Debug/Firmware Updates)

### Connections
| USB-C Pin | Connection |
|-----------|------------|
| D- | ESP32 GPIO19 |
| D+ | ESP32 GPIO20 |
| GND | GND rail |
| VBUS | Not connected to power rail (power from barrel jack only) |
| CC1 | R3 (5.1K) to GND |
| CC2 | R4 (5.1K) to GND |

### Notes
- CC resistors configure USB-C as a device/sink (not a host)
- ESP32-S3 has native USB support — no external USB-UART bridge needed
- Used for: firmware uploads, serial debug output, future OTA trigger
- VBUS is not used for powering the board (12V barrel jack is the sole power source)

---

## COMPLETE BILL OF MATERIALS SUMMARY

| Ref | Qty | Part | Value/Package | Purpose |
|-----|-----|------|---------------|---------|
| J1 | 1 | Barrel Jack | 5.5x2.1mm | Power input |
| J2 | 1 | USB-C Receptacle | USB 2.0 | Debug/FW |
| J3 | 1 | JST-XH 3-pin | 2.5mm pitch | Laser module |
| J4 | 1 | JST-XH 6-pin | 2.5mm pitch | Galvo driver |
| J5 | 1 | FPC 24-pin | 0.5mm pitch | Camera |
| U1 | 1 | AMS1117-5.0 | SOT-223 | 5V regulator |
| U2 | 1 | AMS1117-3.3 | SOT-223 | 3.3V regulator |
| U3 | 1 | ESP32-S3-WROOM-1 | N16R8 | MCU |
| U4 | 1 | MCP4822 | DIP-8 | Dual DAC |
| U5 | 1 | TL072 | DIP-8 | Dual op-amp |
| Q1 | 1 | 2N7000 | TO-92 | Laser MOSFET |
| D1 | 1 | SS34 | SMA | Polarity protection |
| F1 | 1 | PTC Fuse | 1206 | 3A overcurrent |
| LED1 | 1 | WS2812B | PLCC4 5x5mm | Status LED |
| SW1 | 1 | Tactile Switch | 6x6mm | BOOT |
| SW2 | 1 | Tactile Switch | 6x6mm | RESET |
| SW3 | 1 | Microswitch | Panel mount | Safety interlock |
| R1,R2,R13,R14,R15 | 5 | Resistor | 10K 0805 | Pull-up/down |
| R3,R4 | 2 | Resistor | 5.1K 0805 | USB CC |
| R5,R7 | 2 | Resistor | 10K 0805 | Op-amp input |
| R6,R8 | 2 | Resistor | 24K 0805 | Op-amp feedback |
| R9 | 1 | Resistor | 4.7K 0805 | Laser TTL pull-up |
| R10 | 1 | Resistor | 100R 0805 | Gate series |
| R11,R12 | 2 | Resistor | 4.7K 0805 | I2C pull-up |
| C1 | 1 | Electrolytic | 470uF 25V | Bulk filter |
| C3,C5 | 2 | Tantalum/Ceramic | 22uF 10V | Regulator output |
| C2,C4,C6,C8,C9,C10,C11,C12 | 8 | Ceramic | 100nF 0805 | Bypass |
| C7 | 1 | Ceramic | 10uF 0805 | ESP32 bypass |

**Total unique parts: ~30**
**Total component count: ~45**

---

## DESIGN REVIEW CHECKLIST FOR ENGINEER

- [ ] Verify galvo driver board input voltage range and adjust R5-R8 accordingly
- [ ] Decide on single-supply vs. split-supply for TL072 (affects output swing)
- [ ] Confirm OV5640 module pinout matches FPC connector assignment
- [ ] Verify laser module TTL polarity (active HIGH assumed — confirm with datasheet)
- [ ] Add thermal relief pads for U1, U2 on PCB
- [ ] Consider adding TVS diodes on 12V input for ESD protection
- [ ] Review ESP32-S3 antenna keepout zone (no copper/components within 10mm of antenna)
- [ ] Add test points for: +12V, +5V, +3.3V, GND, DAC_A, DAC_B, LASER_TTL
- [ ] Consider adding a power switch between J1 and D1
- [ ] Review ground plane continuity (single ground plane recommended)
