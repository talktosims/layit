#!/usr/bin/env bash
# LayIt Laser — login-required CAD source opener
# Opens each Tier B source in your default browser so you can batch-download.
# All sites require a free account (SnapMagic, McMaster) — sign up once,
# then it's one click per part.

URLS=(
  # JST XH series — KiCad's free repo doesn't have these
  "https://www.snapeda.com/parts/B3B-XH-A/JST/view-part/"     # J3 — laser power, 3-pin
  "https://www.snapeda.com/parts/B6B-XH-A/JST/view-part/"     # J4 — galvo driver, 6-pin

  # Microswitch (lid interlock SW3) — pick whichever Omron variant you sourced
  "https://www.snapeda.com/parts/D2F-01L/Omron/view-part/"

  # Hammond enclosure — choose the closest 6×4×3 from this index
  "https://www.hammfg.com/electronics/small-case/extruded/1455"

  # 1/4-20 brass threaded insert (tripod mount)
  "https://www.mcmaster.com/products/threaded-inserts/inch-brass-threaded-inserts/"

  # USB-C PD trigger board USB-C connector (BOM v3 superseded barrel jack)
  "https://www.snapeda.com/parts/USB4135-GF-0170/GCT/view-part/"

  # If you went with ArduCam OV5640 (instead of generic AliExpress)
  "https://www.arducam.com/product/arducam-5mp-ov5640-ufl-camera-module-with-jpeg/"
)

echo "Opening ${#URLS[@]} CAD source pages in default browser..."
echo "Sign in once (free) — then click 'Download' / 'Get STEP' on each."
echo ""

for url in "${URLS[@]}"; do
  echo "  → $url"
  open -a "Google Chrome" "$url"
  sleep 0.4  # give browser breathing room
done

echo ""
echo "Drop downloaded .step files into:"
echo "  models/manual/connectors/   — JST XH, USB-C"
echo "  models/manual/enclosure/    — Hammond"
echo "  models/manual/hardware/     — McMaster threaded insert"
echo ""
echo "Then run: ls -lh models/manual/*/  to confirm."
