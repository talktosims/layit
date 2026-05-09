# LayIt Laser Rev 2 Build Binder

Date: 2026-05-06
Audience: careful solo builder with basic soldering tools
Scope: bench prototype first, not a production PCB

## 0. Hard Stop Rules

1. Do not use the old build binder as an assembly guide.
2. Do not send the generated KiCad PCB to fabrication.
3. Do not connect a galvo driver to the project 12V rail. Use the matched
   split supply for that driver unless its own label/manual says otherwise.
4. Do not open-bench test the 200mW laser as the first optical test.
5. Do not trust wire colors on off-brand modules. Verify labels and pinouts.
6. Do not continue if any supply rail is not correct with no load attached.

## 1. Corrected System Architecture

Bench build signal flow:

```text
Phone / LayIt app
  -> WiFi/WebSocket
ESP32-S3 DevKitC-1
  -> SPI: CS, MOSI, SCK, LDAC
MCP4822 dual DAC, 0V to 4.096V per axis
  -> corrected analog command stage
TL072 difference amplifiers, powered from verified split rails
  -> about -4.9V to +4.9V per axis
20K galvo driver, powered from its matched split supply
  -> galvo mirrors
Laser TTL blanking, tested low power first
  -> 200mW 520nm module only after safety tests pass
```

Power flow:

```text
12V DC supply or USB-C PD trigger
  -> laser module 12V input, through hard enable/interlock path
  -> MP1584 buck adjusted to 5.00V
       -> ESP32 DevKitC-1 5V pin
       -> MCP4822 VDD

Galvo split supply
  -> galvo driver +V / GND / -V
  -> TL072 op-amp +V / GND / -V

All grounds join at one system ground point:
  ESP32 GND, MCP4822 GND, analog stage GND, galvo signal GND, laser GND
```

Photo audit, 2026-05-06:

- IMG_9447 shows a supply label: KPDS0-12A, input 100-240V AC 1.0A
  50/60Hz, output V1 +12V 4.0A and V2 -12V 1.0A.
- That means your kit appears to include a split galvo supply already, but it
  is +/-12V, not +/-15V.
- IMG_9451 through IMG_9454 show white 3-pin output headers marked `+ G -`.
  Treat those as the likely low-voltage split outputs: +12V, ground, -12V.
- The green 3-screw terminal is on the AC mains input side near line-filter
  parts and safety-ground markings. Do not use it for the galvo driver output.
- Do not buy another galvo supply yet. Use this supply only after the terminal
  labels and driver power connector are verified.
- The corrected TL072 stage can run from +/-12V and still generate the needed
  roughly +/-4.9V command range.
- Do not power this board loose or while handheld. It needs an insulated
  enclosure, strain relief, and correct mains wiring before live testing.

## 2. What The Dev Board Replaces

Use the ESP32-S3 DevKitC-1 N16R8 for the bench prototype.

Do not install these old PCB items for the bench build:

- Bare ESP32-S3-WROOM-1 module
- On-board USB-C receptacle J2
- USB-C CC resistors R3/R4
- BOOT switch SW1
- RESET switch SW2
- EN pullup R1 and GPIO0 pullup R2, unless you later design a custom PCB
- AMS1117 3.3V regulator for the ESP32
- FPC camera connector J5, until the actual camera module pinout is confirmed

The dev board already gives you USB programming, reset/boot, 3.3V regulation,
and header pins.

## 3. ESP32 Pin Map For Bench Prototype

Keep these firmware pins for now:

| Function | ESP32-S3 GPIO | Notes |
|---|---:|---|
| MCP4822 CS | GPIO10 | SPI chip select |
| MCP4822 MOSI | GPIO11 | Data to DAC |
| MCP4822 SCK | GPIO12 | Clock to DAC |
| MCP4822 LDAC | GPIO13 | Simultaneous DAC update |
| Laser blanking control | GPIO14 | Inverted MOSFET logic, HIGH = laser off |
| Safety interlock input | GPIO47 | LOW = allowed, HIGH = unsafe |
| Status LED | GPIO48 | DevKit may already have RGB LED on this pin |
| Camera D8 later | GPIO40 | Corrected away from strapping pin |
| Camera D9 later | GPIO41 | Corrected away from strapping pin |

Avoid GPIO45 and GPIO46 for camera data. They are strapping pins.
Avoid GPIO33 through GPIO37 on N16R8/octal PSRAM variants.

## 4. MCP4822 DAC Wiring

MCP4822 DIP-8 pins:

| MCP4822 pin | Name | Connect to |
|---:|---|---|
| 1 | VDD | 5V from MP1584 |
| 2 | CS | ESP32 GPIO10 |
| 3 | SCK | ESP32 GPIO12 |
| 4 | SDI | ESP32 GPIO11 |
| 5 | LDAC | ESP32 GPIO13 |
| 6 | VOUTA | X analog command stage input |
| 7 | VOUTB | Y analog command stage input |
| 8 | VSS | GND |

Add a 100nF ceramic capacitor directly across VDD and VSS.

Firmware already configures MCP4822 for 2x gain, giving 0V to 4.096V.
The firmware center value is 2048, which becomes about 2.048V at the DAC.

## 5. Corrected Galvo Command Stage

Goal:

```text
DAC 0.000V -> about -4.9V galvo command
DAC 2.048V -> about 0.0V galvo command
DAC 4.096V -> about +4.9V galvo command
```

Use the TL072 only with split rails. Power it from the galvo analog supply. In
your photographed kit this appears to be +/-12V. Many galvo kits use +/-15V.
Use the rails printed on the actual supply and driver labels.

| TL072 pin | Connect to |
|---:|---|
| 8 | positive split rail, +12V or +15V |
| 4 | negative split rail, -12V or -15V |
| GND reference | system ground, not an op-amp power pin |

Add decoupling close to TL072:

- 100nF from positive split rail to GND
- 10uF from positive split rail to GND
- 100nF from negative split rail to GND
- 10uF from negative split rail to GND

### X Axis Difference Amplifier

Use TL072 channel A.

```text
MCP4822 VOUTA -> 10k -> TL072 pin 3 (+ input)
TL072 pin 3 (+ input) -> 24k -> GND

2.048V reference -> 10k -> TL072 pin 2 (- input)
TL072 pin 1 output -> 24k feedback -> TL072 pin 2 (- input)

TL072 pin 1 output -> Galvo X IN+
Galvo X IN- -> GND for first single-ended test
Galvo X signal GND -> system GND
```

### Y Axis Difference Amplifier

Use TL072 channel B.

```text
MCP4822 VOUTB -> 10k -> TL072 pin 5 (+ input)
TL072 pin 5 (+ input) -> 24k -> GND

2.048V reference -> 10k -> TL072 pin 6 (- input)
TL072 pin 7 output -> 24k feedback -> TL072 pin 6 (- input)

TL072 pin 7 output -> Galvo Y IN+
Galvo Y IN- -> GND for first single-ended test
Galvo Y signal GND -> system GND
```

With 24k / 10k, the gain is 2.4. That gives about +/-4.9V from the MCP4822.
This is close enough for first galvo tests and can be calibrated in firmware.

For a final product, replace this with a properly reviewed analog front end,
possibly with true differential outputs. For the bench build, this is a sane
way to test the concept using parts you mostly already own.

### 2.048V Reference Options

Best:

- Use a real 2.048V reference IC.

Acceptable for first bench tests:

- Use a trimpot or resistor divider from 5V adjusted/measured to 2.048V.
- Add 100nF from the reference node to GND.
- Expect to recalibrate center if this reference drifts.

Do not use "whatever midpoint" without measuring it.

## 6. Galvo Driver Wiring

Before wiring, photograph the galvo driver labels and write down every connector.
Common labels:

Power connector:

```text
+V, often +12V or +15V
GND
-V, often -12V or -15V
```

Signal connector per axis:

```text
IN+
GND
IN-
```

First test wiring:

```text
Analog X output -> X IN+
GND -> X GND
GND -> X IN-

Analog Y output -> Y IN+
GND -> Y GND
GND -> Y IN-

Galvo PSU +V -> driver +V
Galvo PSU GND -> driver GND
Galvo PSU -V -> driver -V
```

For your photographed supply, the likely DC output headers are CN6/CN7 marked
`+ G -`. Verify with a meter before connecting the driver:

```text
 to G should measure about +12V
- to G should measure about -12V
+ to - should measure about 24V
```

Do not attach the galvo driver to the green screw terminal. That terminal is
on the AC input side.

If your driver manual explicitly demands a different connector pinout, follow
the manual. The labels on the real board beat every generated binder.

## 7. Laser Blanking And Safety

Original blanking idea:

```text
ESP32 GPIO14 -> 100 ohm -> 2N7000 gate
2N7000 source -> GND
2N7000 drain -> laser TTL input
4.7k pullup from laser TTL input to +12V
10k pullup from 2N7000 gate to +3.3V
```

Logic:

```text
GPIO14 HIGH -> MOSFET on -> TTL pulled low -> laser off
GPIO14 LOW  -> MOSFET off -> TTL pulled high -> laser on
```

Important placement:

- Put the 10k gate pullup on the MOSFET gate side of the 100 ohm resistor.
- This holds the actual gate high during ESP32 boot.

Bench-safety correction:

Do not make this the only safety mechanism for the 200mW laser. Add a hard
power enable path for the laser 12V line:

```text
12V source -> key switch or hard enable -> lid interlock -> laser +12V
```

During early tests, leave the 200mW laser disconnected and use one of:

- a 1mW to 5mW visible test laser
- a reflected phone flashlight / LED alignment target for mirror movement
- a multimeter/LED on the TTL output

## 8. Stage-by-Stage Build

### Stage A - Power Rails Only

1. Set MP1584 output to 5.00V before connecting ESP32 or DAC.
2. Verify 12V input polarity.
3. Verify 5V rail with no load.
4. Verify galvo PSU outputs match its own label before connecting galvos.
   Your photographed supply appears to be +12V, GND, and -12V.
5. Join grounds only after verifying each supply is sane.

Pass criteria:

- 5V rail: 4.85V to 5.15V
- Positive galvo rail: close to the printed positive output value
- Negative galvo rail: close to the printed negative output value
- No heat, smell, or supply shutdown

### Stage B - ESP32 And DAC

1. Power ESP32 DevKit from USB first.
2. Wire MCP4822 to ESP32 SPI pins.
3. Power MCP4822 from 5V and GND.
4. Upload a tiny test sketch or use the LayIt firmware's DAC startup center.
5. Measure DAC outputs.

Pass criteria:

- DAC A and B center near 2.048V when commanded to 2048
- DAC low near 0V
- DAC high near 4.096V

### Stage C - Analog Command Stage

1. Build the TL072 difference amplifier circuit.
2. Power TL072 from the verified galvo split rails.
3. Measure the 2.048V reference.
4. Feed DAC A/B into the stage.
5. Measure analog outputs before connecting galvos.

Pass criteria:

- DAC center -> analog output near 0V
- DAC low -> analog output around -4.9V
- DAC high -> analog output around +4.9V
- No output stuck at a rail

### Stage D - Galvo Motion Without 200mW Laser

1. Connect analog X/Y to the galvo driver.
2. Keep the laser disconnected.
3. Power galvo driver from the verified matching split supply.
4. Run a slow circle or square command.
5. Watch mirror motion.

Pass criteria:

- Mirrors move smoothly and return to center
- No buzzing, violent slamming, or overheating
- X and Y respond independently

If mirrors slam to one side, power down immediately and check analog polarity,
offset, and scale.

### Stage E - Low-Power Optical Test

1. Use a low-power visible laser if available.
2. Project a slow circle/square onto a beam stop or matte wall target.
3. Confirm blanking works.
4. Confirm galvo shape is recognizable.

Pass criteria:

- Laser off during blanking moves
- Shape closes on itself
- No obvious axis inversion that cannot be fixed in firmware

### Stage F - 200mW Laser Test

Only after Stage E passes.

1. Wear OD4+ 520nm glasses.
2. Keep beam path below eye level if possible.
3. Use a non-reflective beam stop.
4. Use hard laser enable switch and interlock.
5. Start with laser power disabled and TTL verified.
6. Enable laser briefly.

Pass criteria:

- Laser never emits during boot
- Laser turns off when GPIO14 is HIGH
- Laser turns off when interlock opens
- Laser turns off when hard enable switch opens

## 9. Camera And IMU

Do not make the camera part of the first working build.

The OV5640 DVP pinout is module-specific. A 24-pin FPC connector in a generic
document does not prove your real camera ribbon pinout. Use the camera only
after the galvo/laser path works.

When camera work resumes:

- Keep D8 on GPIO40
- Keep D9 on GPIO41
- Do not use GPIO45 or GPIO46 for camera data
- Verify the exact FPC pinout from the module seller or by continuity
- Expect the firmware camera pipeline to need real hardware debugging

The MPU6050 is optional for first projection. It can share I2C with the camera
later because MPU6050 is normally at 0x68 and OV5640 SCCB is normally 0x3C
when represented as a 7-bit I2C address.

## 10. Old Binder Corrections Summary

Old claim: Galvo driver powered from 12V.
Correction: galvo driver needs its matched split supply, not the project 12V
rail. Your photos show a likely kit supply labeled +12V and -12V; many generic
20K galvo specs use +/-15V. The real labels/manual win.

Old claim: TL072 can buffer 0V to 4.096V on single supply.
Correction: TL072 cannot properly handle signals near ground on single supply.
Use split rails and a level-shifting difference amplifier.

Old claim: R5/R6/R7/R8 gain stage is enough.
Correction: old topology was ambiguous. Corrected bench stage needs eight
matched resistors and a 2.048V reference.

Old claim: perfboard full build is beginner friendly.
Correction: use modular bench boards first. SMD-on-perfboard is not the right
first path for this laser/galvo project.

Old claim: generated KiCad PCB is corrected.
Correction: it has placed footprints but no real netlist/routing and still
contains stale design assumptions. Do not fab.

Old claim: build camera/FPC into first assembly.
Correction: camera waits until projection works.

## 11. Rev 2 Actual BOM Delta

Already useful from your orders:

- ESP32-S3 DevKitC-1 N16R8
- MP1584EN buck module

Not currently required from the photo audit:

- Separate galvo split-rail supply. Your kit appears to include one labeled
  +12V 4.0A and -12V 1.0A. Verify wiring labels before powering.

Likely required for corrected analog stage unless already in your kits:

- 2.048V reference IC or adjustable trimpot/divider parts
- Extra 10k and 24k resistors for two difference amplifiers
- Extra 100nF and 10uF decoupling capacitors
- Small protoboard or breadboard space

Required before 200mW laser testing:

- OD4+ safety glasses rated for 520nm
- Beam stop
- Hard laser enable switch or key switch
- Lid interlock or equivalent hard power interrupt

Optional but wise:

- Low-power visible test laser
- Cheap logic analyzer
- Oscilloscope

Do not buy:

- PCB fab for current KiCad files
- More camera FPC connectors
- More USB-C debug connectors
- More ESP32 module adapters
- ICL7660 as a galvo fix
- A new regulator just to replace the MP1584
