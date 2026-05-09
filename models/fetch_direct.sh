#!/usr/bin/env bash
# LayIt Laser — direct STEP fetch script
# Pulls all open-source CAD models that don't require login.
# Run from /Users/Sims/Desktop/layit/models/

set -u
cd "$(dirname "$0")"

ESP="https://raw.githubusercontent.com/espressif/kicad-libraries/main/3dmodels/espressif.3dshapes"
KI="https://raw.githubusercontent.com/KiCad/kicad-packages3D/master"

# format: src_url|dest_path|ref_designator|description
PARTS=(
  "${ESP}/ESP32-S3-WROOM-1.STEP|auto/pcb_ics/ESP32-S3-WROOM-1.step|U3|ESP32-S3 module"
  "${KI}/Package_TO_SOT_SMD.3dshapes/SOT-223.step|auto/pcb_ics/AMS1117_SOT-223.step|U1+U2|AMS1117 5V/3.3V regulators (same body)"
  "${KI}/Package_TO_SOT_THT.3dshapes/TO-92-2.step|auto/pcb_ics/2N7000_TO-92.step|Q1|2N7000 MOSFET"
  "${KI}/Package_DIP.3dshapes/DIP-8-N6_W7.62mm.step|auto/pcb_ics/DIP-8_body.step|U4+U5|MCP4822 DAC + TL072 op-amp body"
  "${KI}/Diode_SMD.3dshapes/D_SMA.step|auto/pcb_ics/SS34_SMA.step|D1|SS34 Schottky diode"
  "${KI}/LED_SMD.3dshapes/LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm.step|auto/pcb_ics/WS2812B.step|LED1|Status RGB LED"
  "${KI}/Button_Switch_THT.3dshapes/SW_PUSH_6mm_H4.3mm.step|auto/switches/Tactile_6mm.step|SW1+SW2|BOOT + RESET buttons"
  "${KI}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step|auto/connectors/Header_1x04.step|J6|UART programming header"
  "${KI}/Connector_FFC-FPC.3dshapes/TE_2-84952-4_1x24-1MP_P1.0mm_Horizontal.step|auto/connectors/FPC_24pin.step|J5|Camera ribbon connector"
  "${KI}/Capacitor_THT.3dshapes/CP_Radial_D10.0mm_P5.00mm.step|auto/pcb_passives/Cap_470uF_electrolytic.step|C1|470µF tall electrolytic"
  "${KI}/Capacitor_SMD.3dshapes/C_0805_2012Metric.step|auto/pcb_passives/Cap_ceramic_0805.step|C2-C12|Generic ceramic caps"
  "${KI}/Resistor_SMD.3dshapes/R_0805_2012Metric.step|auto/pcb_passives/Resistor_0805.step|R1-R15|Generic resistors"
)

TOTAL=${#PARTS[@]}
OK=0
FAIL=0
FAILED_LIST=()

echo "Fetching ${TOTAL} parts..."
echo ""

for entry in "${PARTS[@]}"; do
  IFS='|' read -r url dest ref desc <<< "$entry"
  printf "  [%-9s] %-45s ... " "$ref" "$desc"

  http_code=$(curl -sL -w "%{http_code}" -o "$dest" "$url" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    size=$(stat -f%z "$dest" 2>/dev/null || echo "0")
    if [[ "$size" -gt 1000 ]]; then
      printf "✅ (%s bytes)\n" "$size"
      OK=$((OK+1))
    else
      printf "❌ (file too small: %s bytes)\n" "$size"
      FAIL=$((FAIL+1))
      FAILED_LIST+=("$ref → $url")
      rm -f "$dest"
    fi
  else
    printf "❌ (HTTP %s)\n" "$http_code"
    FAIL=$((FAIL+1))
    FAILED_LIST+=("$ref → $url (HTTP $http_code)")
    rm -f "$dest"
  fi
done

echo ""
echo "─────────────────────────────────────"
echo "Done: ${OK}/${TOTAL} succeeded, ${FAIL} failed"
echo ""

if [[ ${#FAILED_LIST[@]} -gt 0 ]]; then
  echo "Failed parts (URL drift in upstream repo? Check filename in git tree):"
  for f in "${FAILED_LIST[@]}"; do
    echo "  • $f"
  done
  echo ""
fi

echo "Next steps:"
echo "  1. Run ./open_sources.sh to batch-open login-required sources in browser"
echo "  2. Drop reference photos for laser/galvos/camera into reference_photos/"
echo "  3. See SOURCING.md for the full manifest"
