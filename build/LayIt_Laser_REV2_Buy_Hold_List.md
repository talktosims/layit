# LayIt Laser Rev 2 - Buy / Hold List

Date: 2026-05-06

## Ownership Assumption

The user says he owns everything from the original Claude BOM/cart, plus the
China-sourced galvos and laser, plus the new ESP32-S3 DevKitC-1 and MP1584
order.

Under that assumption, the missing list is much smaller than the earlier
"buy if missing" list.

## Current Amazon Order

Do not cancel:

- ESP32-S3 DevKitC-1 N16R8 boards
- MP1584EN buck modules

Both are still useful for the corrected bench build.

The ESP32 dev board replaces the bare ESP32 module, USB-C debug connector,
BOOT/RESET switches, ESP32 regulator work, and a lot of risky SMD soldering.

The MP1584 buck makes the 5V rail for the ESP32 dev board and MCP4822 DAC.
Set it to 5.00V with a multimeter before connecting electronics.

## Photo Audit From 2026-05-06

The component photos change the galvo power-supply answer.

- `IMG_9448.HEIC` appears to show the galvo driver board.
- `IMG_9447.HEIC` shows a likely matching galvo split supply labeled
  `KPDS0-12A`, input `100-240V AC 1.0A 50/60Hz`, output `V1 +12V 4.0A` and
  `V2 -12V 1.0A`.
- `IMG_9451.JPG` through `IMG_9454.JPG` show white 3-pin output headers marked
  `+ G -`. Those are the likely low-voltage split outputs: +12V, ground, -12V.
- The green 3-screw terminal is on the AC mains input side near line-filter
  parts and safety-ground markings. Do not use that terminal as a low-voltage
  galvo output.
- `IMG_9445.HEIC` and `IMG_9446.HEIC` appear to show a controller/display
  board, not a part needed for the first ESP32-to-DAC bench path.

Do not buy a separate +/-15V galvo supply right now. Your kit appears to have a
split supply already, just at +/-12V instead of the +/-15V used by many generic
20K galvo specs.

The corrected TL072 analog stage can run from +/-12V and still generate the
roughly +/-4.9V command output needed for first galvo tests.

Safety note: the photographed galvo supply has 100-240V AC mains input. Do not
power it loose on the bench, do not touch it while powered, and do not wire it
until the terminal labels and driver connector labels are verified. It needs an
insulated enclosure, strain relief, and correct mains wiring before live tests.

## Actually Missing / Likely Worth Buying

### 1. Real 2.048V reference

Needed for the corrected analog command stage.

Recommended easy option:

- Adafruit Precision LM4040 Voltage Reference Breakout, product 2200
- Provides 2.048V and 4.096V references
- Source: https://www.adafruit.com/product/2200

Amazon search if you need Prime:

- https://www.amazon.com/s?k=LM4040+2.048V+voltage+reference+breakout

Do not buy random "voltage regulator" modules for this. It needs to be a
reference, not a power regulator.

### 2. Hard laser enable switch

Needed before the 200mW laser is powered.

Acceptable:

- Panel key switch or guarded toggle switch
- Rated for at least 12V DC and 2A
- Wired in series with the laser +12V enable path

Amazon search:

- https://www.amazon.com/s?k=12V+DC+panel+key+switch+2A
- https://www.amazon.com/s?k=12V+DC+guarded+toggle+switch

If you already have a rated switch, use it.

## Probably Already Owned From Original BOM

### OD4+ or better 520nm laser safety glasses

The original BOM/cart included OD4+ 520nm glasses. Do not buy another pair if
your glasses are physically marked for 520nm or 190-540nm and OD4+ or better.

Known suitable examples:

- Laserland T1 OD4+ 190-540nm glasses
  https://www.laserlands.net/protection/laser-glasses/t1.html
- Eagle Pair 190-540nm OD6 slip-over goggles
  https://www.survivallaserusa.com/Eagle_Pair__190-540nm_OD6_Slip_Over_Laser_Safety_Goggles/p1667092_7862524.aspx

Avoid generic "green laser glasses" without a wavelength range and OD marking.

### Resistors and capacitors

The original cart included resistor and capacitor assortments. Do not buy more
until we check the kit values.

For Rev 2, you need:

- 4x 10k 1 percent resistors for the analog stage
- 4x 24k 1 percent resistors for the analog stage
- 1x 10k resistor for R16, laser-off-at-boot gate pullup
- 100nF and 10uF decoupling caps for TL072 rails

The resistor/capacitor book likely covers all of this.

### Protoboard, jumpers, JST, standoffs, microswitch

The original cart included these categories. Do not buy more yet.

## Optional But Smart

Optional but strongly recommended.

Acceptable:

- 1mW to 5mW visible laser module
- Red or green is fine
- It is only for open-bench galvo shape testing

Amazon search:

- https://www.amazon.com/s?k=5mW+laser+module

Do not debug the galvo path for the first time using the 200mW laser.

If you do not want to buy this now, you can still validate early galvo motion
without a laser by watching mirror movement and measuring analog outputs. It is
not required for electrical bring-up.

## No Purchase Needed

### Beam stop

You do not necessarily need to buy a special beam stop for bench work. A matte,
non-reflective ceramic tile, dark brick, or blackened metal target can work for
brief tests. Do not use glossy tile, glass, polished metal, mirrors, or shiny
appliances.

## Hold Unless The Photo Audit Is Disproven

### Separate galvo split-rail power supply

Do not buy this now.

Your photos show what appears to be a matching split supply labeled +12V and
-12V. That is not the same as the old project 12V supply; it is a positive rail,
a ground reference, and a negative rail for the galvo electronics.

Only revisit buying a separate supply if one of these turns out to be true:

- The photographed supply did not come with the galvo kit.
- The galvo driver label/manual specifically requires +/-15V and forbids +/-12V.
- The supply fails no-load measurement or has damaged wiring/connectors.
- The driver power connector labels do not match the supply outputs.

If a separate supply is later proven necessary, prefer the power supply sold by
the galvo kit vendor or a laser-parts supplier for the exact galvo set. Amazon
search only after confirming it is needed:

- https://www.amazon.com/s?k=%2B15V+-15V+galvo+scanner+power+supply
- https://www.amazon.com/s?k=dual+rail+15V+power+supply+1A

Avoid exposed-mains open-frame supplies unless you are comfortable safely
wiring AC mains in an enclosure. For a bench build, a vendor-matched galvo
supply is preferable.

## Probably Already In Your Kits

Do not buy until checked:

- 4 extra 10k 1 percent resistors
- 4 extra 24k 1 percent resistors
- 100nF ceramic capacitors
- 10uF capacitors
- Hookup wire
- Solderable protoboard or breadboard
- Dupont jumpers

Your resistor/capacitor book probably covers most of this.

## Do Not Buy

- More ESP32 boards or ESP32 adapters
- More buck modules
- ICL7660 charge pump as a galvo fix
- Current KiCad PCB fabrication
- More FPC camera connectors
- More USB-C debug connectors
- Another AMS1117 regulator kit
- Another camera module until your current module pinout is known

## Sources

- Typical 20K galvo spec: +/-5V input and +15V/-15V power
  https://laser-parts.com/20kpps-galvanometer-set.html
- Adafruit LM4040 reference breakout
  https://www.adafruit.com/product/2200
- Laserland OD4+ 190-540nm safety glasses
  https://www.laserlands.net/protection/laser-glasses/t1.html
- Eagle Pair OD6 190-540nm goggles
  https://www.survivallaserusa.com/Eagle_Pair__190-540nm_OD6_Slip_Over_Laser_Safety_Goggles/p1667092_7862524.aspx
