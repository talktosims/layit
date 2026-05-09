#!/usr/bin/env bash
# Convert each STEP to OBJ, then render a preview PNG. ONE PART AT A TIME.
# Each part = two short subprocess invocations, so memory clears between parts.
#
# Usage: ./process_all.sh
#        ./process_all.sh <pattern>   # process only paths matching pattern
#
# Output:
#   meshes/<name>.obj    — converted mesh
#   renders/<name>.png   — 800x800 preview

cd "$(dirname "$0")/.."   # cd into models/

PATTERN="${1:-}"

FREECAD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
BLENDER="/opt/homebrew/bin/blender"

if [[ ! -x "$FREECAD" ]]; then
  echo "ERROR: freecadcmd not found at $FREECAD"
  echo "Install with: brew install --cask freecad"
  exit 1
fi
if [[ ! -x "$BLENDER" ]]; then
  echo "ERROR: blender not found at $BLENDER"
  exit 1
fi

# Collect all STEPs from auto/, manual/, and the Toradex reference in photo_model/
STEPS=()
while IFS= read -r line; do
  if [[ -z "$PATTERN" ]] || [[ "$line" == *"$PATTERN"* ]]; then
    STEPS+=("$line")
  fi
done < <(find auto manual photo_model -type f \( -name "*.step" -o -name "*.STEP" -o -name "*.stp" \) | sort)

TOTAL=${#STEPS[@]}
echo "Processing ${TOTAL} STEP files, one at a time..."
echo ""

idx=0
for step in "${STEPS[@]}"; do
  idx=$((idx+1))
  name="$(basename "$step")"
  name="${name%.*}"
  obj="meshes/${name}.obj"
  png="renders/${name}.png"

  printf "[%2d/%2d] %s\n" "$idx" "$TOTAL" "$name"

  # Skip if already done
  if [[ -f "$png" ]]; then
    echo "       (already rendered, skipping)"
    continue
  fi

  # Convert STEP -> OBJ
  echo "       converting..."
  if ! "$FREECAD" scripts/step_to_obj.py -- "$step" "$obj" 2>&1 | grep -E '^\s+->|ERROR' ; then
    echo "       (conversion silent — may have succeeded; checking)"
  fi
  if [[ ! -f "$obj" ]]; then
    echo "       ❌ conversion failed"
    continue
  fi

  # Render single preview PNG
  echo "       rendering..."
  "$BLENDER" --background --python scripts/render_one.py -- "$obj" "$png" \
    > /tmp/blender_render.log 2>&1
  if [[ -f "$png" ]]; then
    sz=$(stat -f%z "$png")
    echo "       ✅ ${png} (${sz} bytes)"
  else
    echo "       ❌ render failed (see /tmp/blender_render.log)"
  fi
  echo ""
done

echo "Done. Renders in models/renders/, meshes in models/meshes/"
