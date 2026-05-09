# LayIt Laser Rev 2 - Read First

Date: 2026-05-06
Status: source-of-truth replacement for the Claude Rev 1 / Rev 1.1 binder

This file supersedes the old build binder, BOM v3, BOM v4, generated KiCad PCB,
and the current ExpandIt manifest for anything involving physical assembly.
Keep the old files only as historical notes and asset references.

## Current Verdict

Do not build or fab the old design.

The old binder and Claude's Rev 1.1 fixes identified some real issues, but the
result is still not a reliable build package. The biggest problem is the galvo
chain. Typical 20K galvo scanner sets are not 12V, 0-5V input devices. The
reference specs found in this project and current galvo vendor pages describe:

- Galvo driver power: +15V and -15V rails
- Command input: +/-5V analog, high impedance, usually differential
- Input connector: IN+, signal ground, IN- per axis, or equivalent

That means the old "12V rail to J4" plan and the single-supply TL072 follower
plan are not appropriate.

## What To Build First

Build a bench prototype in stages:

1. ESP32-S3 DevKitC-1 -> MCP4822 DAC
2. MCP4822 -> corrected +/-5V analog command stage
3. Analog command stage -> galvo driver powered by its proper +/-15V supply
4. Use a low-power test laser or non-laser optical target first
5. Add the 200mW green laser only after blanking and interlock tests pass
6. Add camera, IMU, enclosure, and polished wiring after the galvo path works

Do not start with the old perfboard all-in-one layout. It tries to solve too
many unvalidated things at once.

## Parts You Already Ordered That Are Still Useful

The screenshot and handoff confirm these new orders:

- ESP32-S3 DevKitC-1 N16R8 boards: useful. Use one as the main controller for
  the bench build. This replaces the bare WROOM module, USB-C connector, BOOT
  button, RESET button, EN pullup, GPIO0 pullup, and the risky SMD module work.
- MP1584EN buck modules: useful. Use one to make a 5V rail from the 12V input
  for the ESP32 5V pin and MCP4822 DAC. Set it to 5.00V with a multimeter before
  connecting anything else.

## Things Not To Buy Yet

Do not buy more PCB parts, camera connectors, alternate ESP32 modules, USB-C
debug connectors, PCB fab, or enclosure machining until the galvo bench test
works.

Do not buy an ICL7660 charge pump as "the galvo fix." It is not a galvo power
supply. It can make a tiny negative rail for light analog loads, but it cannot
power galvo drivers.

Do not buy a new buck converter just because MP1584 switching noise was
mentioned. For the corrected bench architecture, the MP1584 only makes the 5V
digital/DAC rail. The galvo command op-amp runs from the galvo analog rails.

## Things You May Actually Need

Buy only after checking whether you already have them.

1. Proper galvo power supply

If your galvo kit includes a supply marked +15V / GND / -15V, use that.
If it does not, you need a galvo-appropriate dual-rail supply:

- Output: +15V and -15V
- Current: at least +15V at 1A and -15V at 0.6A
- Prefer: a supply sold with/for the exact galvo driver

Do not power the galvo driver from the 12V DC supply.

2. Corrected analog command-stage parts

You can reuse the MCP4822 and TL072 if you have the DIP versions. Add:

- 1x 2.048V reference, preferred for stable centering
- OR, for first bench testing only, a divider/trimpot adjusted to 2.048V
- 4x 10k resistors, 1 percent or better
- 4x 24k resistors, 1 percent or better
- 2x 100nF ceramic caps for TL072 rail decoupling
- 2x 10uF caps for TL072 rail decoupling
- Small breadboard or solderable proto board for this analog stage

If your resistor book already has extra 10k and 24k values, do not buy more.
The old BOM's R5/R6/R7/R8 are not enough by themselves for the corrected stage;
the corrected difference-amp stage needs eight resistors total.

3. Safe optical test parts

Strongly recommended before using the 200mW laser:

- 1x low-power visible laser module, ideally 1mW to 5mW, for open-bench tests
- OD4+ safety glasses rated for 520nm before the 200mW laser is ever powered
- A beam stop: matte black metal, ceramic tile, or other non-reflective target
- Key switch or master enable switch for the laser power path
- Emergency stop or accessible hard power switch

The low-power test laser is not part of the final product, but it is cheap
insurance against a dangerous bench mistake.

4. Test tools

Minimum:

- Multimeter
- Breadboard or solderable protoboard
- Dupont jumpers or hookup wire
- Small screw terminals or JST pigtails for galvo/laser connections

Very helpful but not mandatory for the first pass:

- Cheap USB logic analyzer for SPI checks
- Oscilloscope for DAC and galvo command waveform checks

## Sources Checked

- Espressif ESP32-S3 GPIO docs: GPIO45 and GPIO46 are strapping pins; GPIO40
  and GPIO41 are ordinary GPIOs. GPIO33-37 are restricted on octal memory
  variants. https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html
- Espressif ESP32-S3-DevKitC-1 docs: GPIO40 and GPIO41 are exposed on J3.
  https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html
- Typical 20K galvo scanner spec: +/-5V input, 200k differential input, +15V
  and -15V power. https://laser-parts.com/20kpps-galvanometer-set.html
- Microchip MCP4822: dual 12-bit DAC with internal 2.048V reference and SPI.
  https://www.microchip.com/en-us/product/MCP4822
- TI TL072: input/output do not go to the negative rail on single supply; it is
  suitable only when powered with enough headroom, such as split rails.
  https://www.ti.com/product/TL072
- Laserland 4060/520nm class module family: 12VDC, <1.2A, 520nm, 200mW option,
  TTL 15kHz. https://www.laserlands.net/diode-laser-module/510nm-530nm-green-laser-module/520nm-laser-dot/4060-530d-200-12v-ttl.html
- US laser product rule reference for Class IIIb safety expectations:
  https://www.law.cornell.edu/cfr/text/21/1040.10

