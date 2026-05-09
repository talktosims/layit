"""
Generate ExpandIt manifest.json for LayIt Laser from binder data.
Output: /Users/Sims/Desktop/expandit/products/layit/manifest.json
"""
import json
import os

OUT = "/Users/Sims/Desktop/expandit/products/layit/manifest.json"

# Each tuple: (ref, model_glb, x_mm, y_mm, rotation_deg, value, polarity, pins_local,
#              instruction, warning, phase)
# pins_local are (id, dx_mm, dy_mm) offsets from component center, before rotation.

PINS_RES_0805 = [("1", -1.0, 0), ("2", 1.0, 0)]
PINS_CAP_0805 = [("1", -1.0, 0), ("2", 1.0, 0)]
PINS_SOT223  = [("1", -2.3, -1.5), ("2", 0, -1.5), ("3", 2.3, -1.5), ("TAB", 0, 1.6)]
PINS_DIP8    = [(str(i+1), x, y) for i, (x, y) in enumerate([
    (-3.81, -3.81), (-3.81, -1.27), (-3.81, 1.27), (-3.81, 3.81),
    ( 3.81,  3.81), ( 3.81, 1.27), ( 3.81, -1.27), ( 3.81, -3.81),
])]
PINS_TO92    = [("S", -1.27, 0), ("G", 0, 0), ("D", 1.27, 0)]   # 2N7000: source/gate/drain
PINS_TACTILE = [("A1", -3.25, -2.25), ("A2", 3.25, -2.25), ("B1", -3.25, 2.25), ("B2", 3.25, 2.25)]
PINS_HEADER4 = [(str(i+1), (i - 1.5) * 2.54, 0) for i in range(4)]
PINS_JST3    = [("1", -2.5, 0), ("2", 0, 0), ("3", 2.5, 0)]
PINS_JST6    = [(str(i+1), (i - 2.5) * 2.5, 0) for i in range(6)]
PINS_FPC24   = [(str(i+1), (i - 11.5) * 0.5, 0) for i in range(24)]
PINS_USB_C   = [(f"M{i+1}", x, y) for i, (x, y) in enumerate([
    (-4.5, -3.5), (4.5, -3.5), (-4.5, 3.5), (4.5, 3.5)
])]
PINS_RADIAL  = [("+", -2.5, 0), ("-", 2.5, 0)]
PINS_SMA     = [("A", -2.4, 0), ("K", 2.4, 0)]   # K = cathode (silver-stripe side)
PINS_WS2812  = [("VDD", -1.6, -0.8), ("DOUT", 1.6, -0.8), ("DIN", 1.6, 0.8), ("GND", -1.6, 0.8)]
PINS_ESP32_LONG = [(str(i+1), -9, (i - 7.5) * 1.27) for i in range(16)] + \
                  [(str(17+i), 9, (i - 7.5) * 1.27) for i in range(16)] + \
                  [(str(33+i), (i - 3.5) * 1.27, -12.75) for i in range(8)]


def rotate_pins(pins, deg):
    import math
    c = math.cos(math.radians(deg))
    s = math.sin(math.radians(deg))
    return [{"id": pid, "x_mm": dx*c - dy*s, "y_mm": dx*s + dy*c, "z_mm": 0}
            for (pid, dx, dy) in pins]


def comp(ref, model, x, y, rot, value, polarity, pins_local, instruction, warning=None, phase=1, animation_entry="from_above"):
    return {
        "ref": ref,
        "model": f"models/{model}",
        "model_scale": 1.0,
        "position_mm": [x, y, 0],
        "rotation_deg": rot,
        "pins": [
            {"id": p["id"], "x_mm": x + p["x_mm"], "y_mm": y + p["y_mm"], "z_mm": 0}
            for p in rotate_pins(pins_local, rot)
        ],
        "polarity": polarity,
        "instruction": instruction,
        "warning": warning,
        "value": value,
        "spec": "",
        "animation": {"entry": animation_entry, "duration_s": 1.2},
    }


# Phase 1 — resistors (all 0805 SMD, no polarity)
PHASE1 = [
    comp(f"R{i}", "Resistor_0805.glb", x, y, 0, val, None, PINS_RES_0805,
         f"{val} resistor. No polarity — either direction works. Solder 2 joints.",
         phase=1)
    for (i, x, y, val) in [
        (1, 3, -5, "10KΩ"), (2, 6, -5, "10KΩ"), (5, 11, 3, "10KΩ"),
        (6, 11, -1, "24KΩ"), (7, 17, 3, "10KΩ"), (8, 17, -1, "24KΩ"),
        (9, 22, 8, "4.7KΩ"), (10, 19, 8, "100Ω"), (11, 11, 16, "4.7KΩ"),
        (12, 17, 19, "4.7KΩ"), (13, 14, 16, "10KΩ"), (14, 17, 16, "10KΩ"),
        (15, -15, -10, "10KΩ"),
    ]
]

# Phase 2 — ceramic + tantalum caps
PHASE2 = [
    comp("C2",  "Cap_ceramic_0805.glb",  4,  2, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass cap. No polarity. Goes near the IC it serves.", phase=2),
    comp("C4",  "Cap_ceramic_0805.glb", 14,  3, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass cap. No polarity.", phase=2),
    comp("C6",  "Cap_ceramic_0805.glb", 14, -8, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass cap. No polarity.", phase=2),
    comp("C7",  "Cap_ceramic_0805.glb",  4, -2, 0, "10µF",  None, PINS_CAP_0805,
         "10µF ceramic cap near ESP32. No polarity.", phase=2),
    comp("C8",  "Cap_ceramic_0805.glb", -12,  8, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass.", phase=2),
    comp("C9",  "Cap_ceramic_0805.glb", -12, -8, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass.", phase=2),
    comp("C10", "Cap_ceramic_0805.glb", 22,  1, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass.", phase=2),
    comp("C11", "Cap_ceramic_0805.glb", 14, 20, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass.", phase=2),
    comp("C12", "Cap_ceramic_0805.glb",-15, -1, 0, "100nF", None, PINS_CAP_0805,
         "100nF bypass.", phase=2),
    # tantalums (would normally be Cap_Tantalum_1206 but we're reusing 0805 mesh)
    comp("C3",  "Cap_ceramic_0805.glb", -7,  6, 0, "22µF tantalum", "tantalum_stripe", PINS_CAP_0805,
         "22µF tantalum near U1 (5V regulator). STRIPE side is POSITIVE. Match + to PCB marking.",
         warning="Tantalum caps CAN EXPLODE if installed backwards. Use ceramic if uncertain.",
         phase=2),
    comp("C5",  "Cap_ceramic_0805.glb", -7, -6, 0, "22µF tantalum", "tantalum_stripe", PINS_CAP_0805,
         "22µF tantalum near U2 (3.3V regulator). STRIPE = positive.",
         warning="Tantalum caps CAN EXPLODE if installed backwards.",
         phase=2),
]

# Phase 4 — semiconductors and power
PHASE4 = [
    comp("D1",  "SS34_SMA.glb",                -16, -4, 0, "SS34 Schottky", "diode_stripe", PINS_SMA,
         "SS34 Schottky. SILVER STRIPE = cathode. Stripe must match band marking on PCB silkscreen.",
         warning="BACKWARDS = NO REVERSE-POLARITY PROTECTION. Could damage the board.",
         phase=4),
    comp("Q1",  "2N7000_TO-92.glb",             22,  4, 0, "2N7000 MOSFET", "transistor_flat", PINS_TO92,
         "2N7000 MOSFET. FLAT side must match flat side on PCB silkscreen. Pins L→R: Source / Gate / Drain.",
         warning="Static-sensitive. Touch grounded metal first.",
         phase=4),
    comp("U1",  "AMS1117_SOT-223.glb",         -11,  6, 90, "AMS1117-5.0", "regulator_tab", PINS_SOT223,
         "AMS1117-5.0 regulator (5V). Metal TAB orientation matches PCB silkscreen.",
         warning="Don't swap with U2 — wrong voltage will fry the ESP32.",
         phase=4),
    comp("U2",  "AMS1117_SOT-223.glb",         -11, -6, 90, "AMS1117-3.3", "regulator_tab", PINS_SOT223,
         "AMS1117-3.3 regulator (3.3V). Tab orientation per silkscreen. Says '3.3' on package.",
         phase=4),
    comp("C1",  "Cap_470uF_electrolytic.glb", -18,  4, 0, "470µF 25V", "electrolytic_plus", PINS_RADIAL,
         "470µF radial electrolytic. WHITE STRIPE = NEGATIVE leg. LONGER leg = POSITIVE. Match + to PCB marking.",
         warning="Backwards installation can cause the cap to POP and leak.",
         phase=4),
]

# Phase 5 — connectors + tactile switches
PHASE5 = [
    comp("J2",  "USB-C_GCT_USB4500-03-0-A.glb", -27,  0, 90, "USB-C", None, PINS_USB_C,
         "USB-C receptacle. Push fully into PCB. Solder mounting tabs first, then signal pins.",
         phase=5),
    comp("J3",  "JST_B3B-XH-A_3pin.glb",         28, -10, 90, "3-pin XH", None, PINS_JST3,
         "JST-XH 3-pin. Laser power output. Plastic housing flat against PCB.",
         phase=5),
    comp("J4",  "JST_B6B-XH-A_6pin.glb",         28,   5, 90, "6-pin XH", None, PINS_JST6,
         "JST-XH 6-pin. Galvo driver connector. Make sure pins go in straight.",
         phase=5),
    comp("J5",  "FPC_24pin.glb",                 14,  16, 0, "24-pin FPC", None, PINS_FPC24,
         "FPC 24-pin connector for OV5640 camera. Use plenty of flux. Tack one corner first.",
         warning="Fine-pitch. Bridge two pins → desolder with wick before continuing.",
         phase=5),
    comp("J6",  "Header_1x04.glb",                4, -19, 0, "4-pin UART", None, PINS_HEADER4,
         "4-pin UART programming header. Pins TX/RX/3.3V/GND on silkscreen.",
         phase=5),
    comp("SW1", "Tactile_6mm.glb",                4, -14, 0, "BOOT button", None, PINS_TACTILE,
         "BOOT tactile switch. Hold during firmware flashing.",
         phase=5),
    comp("SW2", "Tactile_6mm.glb",               -2, -14, 0, "RESET button", None, PINS_TACTILE,
         "RESET tactile switch.",
         phase=5),
]

# Phase 6 — status LED
PHASE6 = [
    comp("LED1", "WS2812B.glb", -2, -8, 0, "WS2812B RGB", "led_notch", PINS_WS2812,
         "WS2812B addressable RGB LED. NOTCHED CORNER = pin 1 (VDD). Match notch to PCB silkscreen.",
         warning="Heat-sensitive — don't hold iron more than 2 seconds per pad.",
         phase=6),
]

# Phase 7 — ESP32 module (boss level)
PHASE7 = [
    comp("U3", "ESP32-S3-WROOM-1.glb", 4, 0, 90, "ESP32-S3-WROOM-1 N16R8", "ic_pin1_notch", PINS_ESP32_LONG,
         "ESP32-S3-WROOM-1 module. Castellated edge pads. Pre-tin all PCB pads first, then place module aligned to pin 1, tack-solder one corner, verify alignment, solder each castellation.",
         warning="Don't block the antenna — keep solder, copper, and components 10mm from antenna end. Take breaks; this step takes 20-30 minutes.",
         phase=7),
]

# Phase 8 — ICs into sockets
PHASE8 = [
    comp("U4", "DIP-8_body.glb", 14,  8, 90, "MCP4822 DAC", "ic_pin1_notch", PINS_DIP8,
         "MCP4822 dual DAC into DIP-8 socket. NOTCH on chip matches NOTCH on socket (and PCB).",
         warning="Don't put it in U5's socket. Read the chip markings.", phase=8),
    comp("U5", "DIP-8_body.glb", 14, -3, 90, "TL072 op-amp", "ic_pin1_notch", PINS_DIP8,
         "TL072 dual op-amp into DIP-8 socket at U5. Notch matches socket notch.",
         phase=8),
]


# External components (off-board, wired in)
EXTERNAL = [
    {
        "ref": "LASER",
        "name": "Laserland 4060-530D-200 — 200mW 520nm",
        "model": "models/external_laser_placeholder.glb",
        "position_mm": [75, -25, 8],
        "rotation_deg": 0,
        "wires": [
            {"from_pin": {"ref": "J3", "id": "1"}, "to_pin": {"ref": "LASER", "id": "+12V"},
             "color": "RED",   "spec": "+12V power"},
            {"from_pin": {"ref": "J3", "id": "2"}, "to_pin": {"ref": "LASER", "id": "TTL"},
             "color": "GREEN", "spec": "TTL modulation 15kHz"},
            {"from_pin": {"ref": "J3", "id": "3"}, "to_pin": {"ref": "LASER", "id": "GND"},
             "color": "BLACK", "spec": "Ground"},
        ],
    },
    {
        "ref": "GALVO",
        "name": "20K PPS dual-axis galvo + driver",
        "model": "models/external_galvo_placeholder.glb",
        "position_mm": [75, 20, 14],
        "rotation_deg": 0,
        "wires": [
            {"from_pin": {"ref": "J4", "id": "1"}, "to_pin": {"ref": "GALVO", "id": "X+"}, "color": "BLUE", "spec": "X-axis +"},
            {"from_pin": {"ref": "J4", "id": "2"}, "to_pin": {"ref": "GALVO", "id": "X-"}, "color": "BLUE", "spec": "X-axis −"},
            {"from_pin": {"ref": "J4", "id": "3"}, "to_pin": {"ref": "GALVO", "id": "Y+"}, "color": "BLUE", "spec": "Y-axis +"},
            {"from_pin": {"ref": "J4", "id": "4"}, "to_pin": {"ref": "GALVO", "id": "Y-"}, "color": "BLUE", "spec": "Y-axis −"},
            {"from_pin": {"ref": "J4", "id": "5"}, "to_pin": {"ref": "GALVO", "id": "+12V"}, "color": "RED", "spec": "+12V"},
            {"from_pin": {"ref": "J4", "id": "6"}, "to_pin": {"ref": "GALVO", "id": "GND"}, "color": "BLACK", "spec": "GND"},
        ],
    },
    {
        "ref": "CAMERA",
        "name": "OV5640 5MP wide-angle DVP",
        "model": "models/OV5640_Toradex_reference.glb",
        "position_mm": [14, 60, 8],
        "rotation_deg": 0,
        "wires": [
            {"from_pin": {"ref": "J5", "id": "1-24"}, "to_pin": {"ref": "CAMERA", "id": "FPC"},
             "color": "YELLOW", "spec": "24-pin FPC ribbon"},
        ],
    },
    {
        "ref": "SW3",
        "name": "Lid interlock microswitch (Omron D2F-01L)",
        "model": "models/Microswitch_Omron_D2F-01L.glb",
        "position_mm": [-25, 30, 4],
        "rotation_deg": 0,
        "wires": [
            {"from_pin": {"ref": "SW3-PAD", "id": "A"}, "to_pin": {"ref": "SW3", "id": "COM"},
             "color": "GREEN", "spec": "Safety signal"},
            {"from_pin": {"ref": "SW3-PAD", "id": "B"}, "to_pin": {"ref": "SW3", "id": "NC"},
             "color": "BLACK", "spec": "GND"},
        ],
    },
    {
        "ref": "PD",
        "name": "USB-C PD trigger board (12V output)",
        "model": "models/external_pd_placeholder.glb",
        "position_mm": [-50, 0, 2],
        "rotation_deg": 0,
        "wires": [
            {"from_pin": {"ref": "PD", "id": "VOUT+"}, "to_pin": {"ref": "J2", "id": "12V"}, "color": "RED", "spec": "+12V"},
            {"from_pin": {"ref": "PD", "id": "VOUT-"}, "to_pin": {"ref": "J2", "id": "GND"}, "color": "BLACK", "spec": "GND"},
        ],
    },
]


manifest = {
    "schema_version": 1,
    "product": "LayIt Laser",
    "id": "layit-laser-v1",
    "description": "USB-C powered 520nm 200mW laser projection system. ESP32-S3 controlled, galvo-scanned, camera-aligned tile pattern projector.",
    "units": "mm",
    "base": {
        "model": "models/perfboard.glb",
        "size_mm": [70, 50, 1.6],
        "anchor_mm": [0, 0, 0],
        "grid": {"type": "perfboard", "pitch_mm": 2.54, "cols": 28, "rows": 20}
    },
    "phases": [
        {"id": 1, "title": "Phase 1: Resistors",
         "description": "Resistors have NO polarity — perfect warm-up step. 13 components × 2 joints each = 26 joints.",
         "components": PHASE1},
        {"id": 2, "title": "Phase 2: Ceramic + tantalum caps",
         "description": "Ceramic caps have no polarity. Tantalums DO — stripe = positive.",
         "components": PHASE2},
        {"id": 4, "title": "Phase 4: Semiconductors + power",
         "description": "Polarity matters. Read each component's stripe / flat-side / + leg before soldering.",
         "components": PHASE4},
        {"id": 5, "title": "Phase 5: Connectors + switches",
         "description": "USB-C, JSTs, FPC, UART header, tactile buttons.",
         "components": PHASE5},
        {"id": 6, "title": "Phase 6: Status LED",
         "description": "WS2812B RGB. Notched corner = pin 1.",
         "components": PHASE6},
        {"id": 7, "title": "Phase 7: ESP32-S3 module",
         "description": "The boss level. ~40 castellated solder joints. Take your time.",
         "components": PHASE7},
        {"id": 8, "title": "Phase 8: ICs into sockets",
         "description": "MCP4822 + TL072. Just press them in. Notch must match socket notch.",
         "components": PHASE8},
    ],
    "external": EXTERNAL,
}


# Pretty-print
with open(OUT, "w") as f:
    json.dump(manifest, f, indent=2)

n_components = sum(len(p["components"]) for p in manifest["phases"])
n_pins = sum(len(c["pins"]) for p in manifest["phases"] for c in p["components"])
n_wires = sum(len(e.get("wires", [])) for e in manifest["external"])
size_kb = os.path.getsize(OUT) / 1024
print(f"✅ {OUT} ({size_kb:.1f} KB)")
print(f"   {len(manifest['phases'])} phases, {n_components} components, {n_pins} pins")
print(f"   {len(manifest['external'])} external + {n_wires} wires")
