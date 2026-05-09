"""
Build a real KiCad PCB layout for the LayIt Laser using pcbnew Python API.
Loads real KiCad footprints from the bundled library, places at approximate
positions (from binder text descriptions), and sets a board outline.

Run with KiCad's bundled Python:
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 build_pcb.py
"""
import pcbnew
import os
import sys
import math

KICAD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
OUT = "/Users/Sims/Desktop/layit/build/LayIt_Hardware/pcb/LayIt_Laser.kicad_pcb"

# Component list: (reference, footprint_lib, footprint_name, x_mm, y_mm, rotation_deg)
# Coordinates: mm in KiCad's frame. Origin at upper-left of the page.
# I'll use a centered placement around mm (150, 100), board 70x50mm.
CX, CY = 150, 100   # PCB center in KiCad page coords
COMPONENTS = [
    # Power input section (left side of board)
    ("J2",  "Connector_USB",            "USB_C_Receptacle_GCT_USB4085",  -27,  0,  90),
    # USB-C CC pull-down resistors (NEW — were missing in Rev 1.0; without them USB-C won't enumerate)
    ("R3",  "Resistor_SMD",             "R_0805_2012Metric",             -23,  3,  90),
    ("R4",  "Resistor_SMD",             "R_0805_2012Metric",             -23, -3,  90),
    # USB-C ESD protection
    ("TVS1","Package_TO_SOT_SMD",       "SOT-23-6",                      -25,  6,   0),
    ("F1",  "Fuse",                     "Fuse_1206_3216Metric",          -22, -3,   0),
    ("D1",  "Diode_SMD",                "D_SMA",                         -16, -4,   0),
    ("C1",  "Capacitor_THT",            "CP_Radial_D10.0mm_P5.00mm",     -18,  4,   0),
    # U1: MP1584 buck converter module (4-pin header) replaces AMS1117-5.0 — fixes overheating
    ("U1",  "Connector_PinHeader_2.54mm","PinHeader_1x04_P2.54mm_Vertical",-11, 6,  0),
    ("U2",  "Package_TO_SOT_SMD",       "SOT-223-3_TabPin2",             -11, -6,  90),
    ("C3",  "Capacitor_SMD",            "C_1206_3216Metric",              -7,  6,   0),
    ("C5",  "Capacitor_SMD",            "C_1206_3216Metric",              -7, -6,   0),

    # ESP32 main MCU, antenna toward +Y (FPC side)
    ("U3",  "RF_Module",                "ESP32-S3-WROOM-1",                4,  0,  90),
    ("SW1", "Button_Switch_SMD",        "SW_SPST_TL3342",                  4, -14,  0),
    ("SW2", "Button_Switch_SMD",        "SW_SPST_TL3342",                 -2, -14,  0),
    ("J6",  "Connector_PinHeader_2.54mm", "PinHeader_1x04_P2.54mm_Vertical", 4, -19,  0),

    # ICs
    ("U4",  "Package_DIP",              "DIP-8_W7.62mm",                  14,  8,  90),
    ("U5",  "Package_DIP",              "DIP-8_W7.62mm",                  14, -3,  90),

    # Laser MOSFET driver — R16 added as gate pull-up so laser is OFF at boot
    ("Q1",  "Package_TO_SOT_THT",       "TO-92_Inline",                   22,  4,   0),
    ("R16", "Resistor_SMD",             "R_0805_2012Metric",              20,  6,   0),
    # Laser-side ESD diode on J3 TTL pin
    ("TVS2","Diode_SMD",                "D_SOD-323",                      26, -10,  0),

    # External-facing connectors at right edge
    ("J3",  "Connector_JST",            "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical", 28, -10,  90),
    ("J4",  "Connector_JST",            "JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical", 28,   5,  90),

    # FPC camera, status LED + R17 (series resistor on data line — NEW)
    ("J5",  "Connector_FFC-FPC",        "TE_2-84952-4_1x24-1MP_P1.0mm_Horizontal", 14, 16, 0),
    ("LED1","LED_SMD",                  "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm",      -2, -8,  0),
    ("R17", "Resistor_SMD",             "R_0805_2012Metric",                        1, -8,  0),
    # MPU6050 IMU breakout — placed as 4-pin header connector to off-board GY-521 module
    ("IMU", "Connector_PinHeader_2.54mm","PinHeader_1x04_P2.54mm_Vertical",          8, -16, 0),

    # Resistors near respective ICs (per binder)
    ("R1",  "Resistor_SMD", "R_0805_2012Metric",  3,  -5,  0),
    ("R2",  "Resistor_SMD", "R_0805_2012Metric",  6,  -5,  0),
    # R5-R8 removed in Rev 1.1 — TL072 reconfigured as unity-gain voltage follower
    # (no input/feedback resistors needed; output ties directly to inverting input)
    ("R9",  "Resistor_SMD", "R_0805_2012Metric", 22,   8,  0),
    ("R10", "Resistor_SMD", "R_0805_2012Metric", 19,   8,  0),
    ("R11", "Resistor_SMD", "R_0805_2012Metric", 11,  16,  0),
    ("R12", "Resistor_SMD", "R_0805_2012Metric", 17,  19,  0),
    ("R13", "Resistor_SMD", "R_0805_2012Metric", 14,  16,  0),
    ("R14", "Resistor_SMD", "R_0805_2012Metric", 17,  16,  0),
    ("R15", "Resistor_SMD", "R_0805_2012Metric", -15, -10,  0),

    # Decoupling caps
    ("C2",  "Capacitor_SMD", "C_0805_2012Metric",  4,   2,  0),
    ("C4",  "Capacitor_SMD", "C_0805_2012Metric", 14,   3,  0),
    ("C6",  "Capacitor_SMD", "C_0805_2012Metric", 14,  -8,  0),
    ("C7",  "Capacitor_SMD", "C_0805_2012Metric",  4,  -2,  0),
    ("C8",  "Capacitor_SMD", "C_0805_2012Metric",-12,   8,  0),
    ("C9",  "Capacitor_SMD", "C_0805_2012Metric",-12,  -8,  0),
    ("C10", "Capacitor_SMD", "C_0805_2012Metric", 22,   1,  0),
    ("C11", "Capacitor_SMD", "C_0805_2012Metric", 14,  20,  0),
    ("C12", "Capacitor_SMD", "C_0805_2012Metric",-15,  -1,  0),
]


def mm_to_kiu(mm):
    return int(mm * 1_000_000)   # KiCad internal unit = nm


def add_footprint(board, ref, lib_name, fp_name, x_mm, y_mm, rot_deg):
    lib_path = os.path.join(KICAD_FP, f"{lib_name}.pretty")
    if not os.path.isdir(lib_path):
        print(f"  ❌ {ref}: library {lib_name} not found")
        return None
    try:
        fp = pcbnew.FootprintLoad(lib_path, fp_name)
    except Exception as e:
        print(f"  ❌ {ref}: failed to load {lib_name}:{fp_name} — {e}")
        return None
    if fp is None:
        # Try listing the library to suggest alternatives
        candidates = [f.replace(".kicad_mod", "") for f in os.listdir(lib_path) if f.endswith(".kicad_mod")]
        near = [c for c in candidates if any(part in c.lower() for part in fp_name.lower().split("_")[:2])]
        print(f"  ❌ {ref}: footprint {fp_name} not in {lib_name}. Near matches: {near[:5]}")
        return None
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(mm_to_kiu(CX + x_mm), mm_to_kiu(CY + y_mm)))
    if rot_deg != 0:
        fp.Rotate(fp.GetPosition(), pcbnew.EDA_ANGLE(rot_deg, pcbnew.DEGREES_T))
    board.Add(fp)
    return fp


def add_board_outline(board, w_mm, h_mm):
    """Draw rectangular board outline on Edge.Cuts layer."""
    edge_layer = board.GetLayerID("Edge.Cuts")
    x0 = mm_to_kiu(CX - w_mm / 2)
    x1 = mm_to_kiu(CX + w_mm / 2)
    y0 = mm_to_kiu(CY - h_mm / 2)
    y1 = mm_to_kiu(CY + h_mm / 2)
    for (a, b) in [((x0, y0), (x1, y0)),
                   ((x1, y0), (x1, y1)),
                   ((x1, y1), (x0, y1)),
                   ((x0, y1), (x0, y0))]:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(*a))
        seg.SetEnd(pcbnew.VECTOR2I(*b))
        seg.SetLayer(edge_layer)
        seg.SetWidth(mm_to_kiu(0.15))
        board.Add(seg)


def main():
    board = pcbnew.NewBoard(OUT)

    # Board outline 70x50mm
    add_board_outline(board, 70, 50)

    # Place all footprints
    print(f"Placing {len(COMPONENTS)} footprints...")
    placed, failed = 0, 0
    for ref, lib, fp, x, y, rot in COMPONENTS:
        result = add_footprint(board, ref, lib, fp, x, y, rot)
        if result is not None:
            placed += 1
        else:
            failed += 1

    # Save
    pcbnew.SaveBoard(OUT, board)
    size = os.path.getsize(OUT) / 1024
    print(f"\n✅ Saved {OUT} ({size:.1f} KB)")
    print(f"   {placed} placed, {failed} failed")


if __name__ == "__main__":
    main()
