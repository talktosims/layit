"""
Promote 7 manifest components from photo_only_placeholder/estimated_package_model
to datasheet_parametric by attaching their freshly-built GLBs.

Preserves all existing fields (position_mm, pins, instructions, warnings, etc.)
and only swaps `primitive` -> `model`, bumps `model_accuracy`, replaces
`source_refs` with citations to the manufacturer mech drawings.

Backups the manifest first.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

MANIFEST = Path("/Users/Sims/Desktop/expandit/products/layit/manifest.json")
BACKUP = MANIFEST.with_suffix(
    f".pre-realmodels-{datetime.now().strftime('%Y-%m-%d')}.json"
)

# ref -> { glb filename, source_refs, optional measured_size_mm override, notes }
PROMOTIONS = {
    "U3": {
        "model": "models/ESP32-S3-DevKitC-1.glb",
        "source_refs": [
            "Espressif ESP32-S3-DevKitC-1 v1.1 user guide and Dimensions PDF/DXF",
            "Espressif ESP32-S3-WROOM-1 datasheet (module dimensions 18.0 x 25.5 x 3.1 mm)",
        ],
        "measured_size_mm": [57, 25.4, 14],  # PCB 56 + USB-C overhang ~1; height with module + USB-C
        "model_notes": "Built parametrically to Espressif's reference DevKitC-1 v1.1 dimensions. The Hosyond clone you ordered should match this layout but variant differences (header row count 2x18 vs 2x19 vs 2x21, USB-C variant) need physical clone-confirmation before solder-by-eye trust.",
    },
    "U4": {
        "model": "models/MCP4822_PDIP8.glb",
        "source_refs": [
            "Microchip MCP4822 datasheet DS22249, 8-Lead PDIP package drawing C04-018",
        ],
        "model_notes": "JEDEC PDIP-8 from Microchip MCP4822 datasheet (body 9.27 x 6.35 x 3.30 mm, lead pitch 2.54 mm, row spacing 7.62 mm).",
    },
    "U5": {
        "model": "models/TL072CP_PDIP8.glb",
        "source_refs": [
            "TI TL072 datasheet, PDIP-8 package P0008 (mechanical drawing)",
        ],
        "model_notes": "JEDEC PDIP-8, identical mechanical envelope to MCP4822. Use TL072CP (PDIP variant), not TL072CD (SOIC).",
    },
    "C10": {
        "model": "models/Cap_0805_ceramic_v2.glb",
        "source_refs": [
            "IPC SMD-A standard 0805 chip dimensions (2.0 x 1.25 x ~0.5 mm)",
            "Murata GRM21 series datasheet (representative 0805 X7R/X5R MLCC)",
        ],
        "model_notes": "Standard 0805 MLCC. Tan body + tin terminations.",
    },
    "Q1": {
        "model": "models/2N7000_TO92_v2.glb",
        "source_refs": [
            "Onsemi 2N7000 datasheet, TO-92 (TO-226-3) package mechanical drawing",
        ],
        "model_notes": "TO-226-3 case: body 4.5 x 3.7 x 5.2 mm, three leads at 1.27 mm pitch, 14.5 mm full lead length.",
    },
    "VREF": {
        "model": "models/LM4040_Adafruit2200.glb",
        "source_refs": [
            "Adafruit Precision LM4040 Voltage Reference Breakout (PRD 2200) product page mechanicals",
            "TI LM4040 datasheet (SOT-23-3 package on the breakout)",
        ],
        "measured_size_mm": [16.51, 10.16, 11],
        "model_notes": "Codex's recommended 2.048V reference for the analog command stage. Adafruit publishes EagleCAD mechanicals for this breakout.",
    },
    "IMU": {
        "model": "models/MPU6050_GY521.glb",
        "source_refs": [
            "InvenSense MPU-6050 datasheet (QFN-24, 4.0 x 4.0 x 0.9 mm)",
            "GY-521 module reference (community-documented 21.2 x 15.8 x 1.6 mm PCB, 8-pin 0.1\" header)",
        ],
        "measured_size_mm": [21.2, 15.8, 11],
        "model_notes": "GY-521 clone module is well-characterized; the variant you have should match these dims within +/-0.5 mm.",
    },
}


def main():
    if not MANIFEST.exists():
        print(f"manifest not found at {MANIFEST}", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(MANIFEST, BACKUP)
    print(f"backup -> {BACKUP}")

    manifest = json.loads(MANIFEST.read_text())

    promoted = 0
    not_found = []
    for phase in manifest.get("phases", []):
        for c in phase.get("components", []):
            ref = c.get("ref")
            if ref in PROMOTIONS:
                spec = PROMOTIONS[ref]
                # Drop the primitive block — we now have a real model.
                c.pop("primitive", None)
                c["model"] = spec["model"]
                c["model_accuracy"] = "datasheet_parametric"
                c["source_refs"] = spec["source_refs"]
                if "measured_size_mm" in spec:
                    c["measured_size_mm"] = spec["measured_size_mm"]
                # Don't blow away existing notes — append.
                existing_notes = c.get("model_notes", "")
                if existing_notes and spec["model_notes"] not in existing_notes:
                    c["model_notes"] = existing_notes + "\n\n" + spec["model_notes"]
                else:
                    c["model_notes"] = spec["model_notes"]
                # No longer needs modeling — we have it.
                c["needs_modeling"] = False
                promoted += 1
                print(f"  promoted {ref} -> {spec['model']}")

    expected = set(PROMOTIONS.keys())
    actual = {c.get("ref") for phase in manifest.get("phases", []) for c in phase.get("components", [])}
    not_found = expected - actual
    if not_found:
        print(f"  ! refs not found in manifest: {sorted(not_found)}", file=sys.stderr)

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {MANIFEST} ({promoted} components promoted)")


if __name__ == "__main__":
    main()
