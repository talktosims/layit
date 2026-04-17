/**
 * Tessellation Geometry Validation & Computation Engine
 *
 * Mathematically validates tile specifications and computes tessellation
 * parameters for the LayIt tile layout system.
 *
 * Supports: hex (pointy/flat), penny round, fishscale, square, diamond,
 * rectangle/herringbone, octagon+dot, arabesque/lantern, elongated hex.
 *
 * Pure ES module, no external dependencies.
 */

const SQRT2 = Math.sqrt(2);
const SQRT3 = Math.sqrt(3);
const HALF_SQRT3 = SQRT3 / 2; // ~0.866

// ─────────────────────────────────────────────
// Shape constants and aspect ratio defaults
// ─────────────────────────────────────────────

const SHAPE_DEFAULTS = {
  hex:           { aspectRatio: 1.125, minAspect: 1.0, maxAspect: 1.2 },
  hexFlat:       { aspectRatio: 1.125, minAspect: 1.0, maxAspect: 1.2 },
  penny:         { aspectRatio: 1.0,   minAspect: 1.0, maxAspect: 1.0 },
  fishscale:     { aspectRatio: 1.125, minAspect: 1.0, maxAspect: 1.2 },
  square:        { aspectRatio: 1.0,   minAspect: 0.5, maxAspect: 2.0 },
  diamond:       { aspectRatio: 1.0,   minAspect: 0.8, maxAspect: 1.2 },
  rectangle:     { aspectRatio: 2.0,   minAspect: 1.5, maxAspect: 4.0 },
  octagonDot:    { aspectRatio: 1.0,   minAspect: 1.0, maxAspect: 1.0 },
  arabesque:     { aspectRatio: 1.0,   minAspect: 0.7, maxAspect: 1.4 },
  elongatedHex:  { aspectRatio: 3.0,   minAspect: 2.0, maxAspect: 4.0 },
};

// ─────────────────────────────────────────────
// computeSubTileHeight
// ─────────────────────────────────────────────

/**
 * Given a sub-tile shape and width, compute the correct height.
 * For shapes where height is derived from width (hex, penny, etc.).
 *
 * @param {string} subShape - One of the supported shape names
 * @param {number} subW - Sub-tile width in inches
 * @returns {number} Computed sub-tile height in inches
 */
export function computeSubTileHeight(subShape, subW) {
  switch (subShape) {
    case 'hex':
    case 'hexFlat':
      // Theoretical: subW * (2/sqrt3) ≈ 1.1547
      // Practical tiles: subW * 1.125
      return subW * 1.125;

    case 'penny':
      // Circles: height = width = diameter
      return subW;

    case 'fishscale':
      // Exact: dome radius = W/2, stem = dome radius → total height = W
      return subW;

    case 'square':
      return subW;

    case 'diamond':
      return subW;

    case 'rectangle':
      // Default 2:1 aspect for herringbone
      return subW / 2;

    case 'octagonDot':
      // Regular octagon: equal width and height
      return subW;

    case 'arabesque':
      // Roughly square bounding box
      return subW;

    case 'elongatedHex':
      // Stretched hex: height derived from width at 3:1 default
      return subW / 3;

    default:
      return subW;
  }
}

// ─────────────────────────────────────────────
// computeSubTileCoverage
// ─────────────────────────────────────────────

/**
 * Compute the effective coverage area of one sub-tile in square inches.
 * Accounts for shape geometry (hex is not a full rectangle, circle is pi*r^2, etc.)
 *
 * @param {string} subShape
 * @param {number} subW - Width in inches
 * @param {number} subH - Height in inches
 * @returns {number} Coverage area in square inches
 */
export function computeSubTileCoverage(subShape, subW, subH) {
  switch (subShape) {
    case 'hex':
    case 'hexFlat':
    case 'elongatedHex': {
      // Area of a regular hexagon with width W and height H:
      // For pointy-top: A = (sqrt(3)/2) * (W/2)^2 * 2... simplify:
      // Hex area = (3*sqrt(3)/2) * s^2 where s = side length
      // With bounding box W x H, effective area ≈ W * H * 0.866
      // More precisely for a regular hex: A = (3*sqrt(3)/8) * W^2 when W is flat-to-flat
      // But for practical tiles with given W,H: coverage ≈ 0.866 * W * H
      return subW * subH * HALF_SQRT3;
    }

    case 'penny': {
      // Circle: pi * r^2
      const r = subW / 2;
      return Math.PI * r * r;
    }

    case 'fishscale': {
      // Semicircular fan: approximately half a circle
      const r = subW / 2;
      return Math.PI * r * r * 0.5;
    }

    case 'square':
      return subW * subH;

    case 'diamond':
      // Diamond (rotated square): area = W * H / 2
      return (subW * subH) / 2;

    case 'rectangle':
      return subW * subH;

    case 'octagonDot': {
      // Regular octagon: A = 2 * (1 + sqrt(2)) * s^2
      // where s = subW / (1 + sqrt(2))
      const s = subW / (1 + SQRT2);
      const octArea = 2 * (1 + SQRT2) * s * s;
      // Plus the corner dot (small square): s * s
      return octArea + (s * s);
    }

    case 'arabesque':
      // Curvy shape in bounding box, roughly 70% fill
      return subW * subH * 0.70;

    default:
      return subW * subH;
  }
}

// ─────────────────────────────────────────────
// Tessellation spacing computations
// ─────────────────────────────────────────────

/**
 * Compute row and column spacing for a given shape + grout.
 * Returns { colSpacing, rowSpacing, oddRowOffsetX, oddColOffsetY }
 */
function computeSpacing(subShape, subW, subH, subGr) {
  switch (subShape) {
    case 'hex': {
      // Pointy-top hex
      const colSpacing = subW + subGr;
      const rowSpacing = subH * 0.75 + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: colSpacing / 2, oddColOffsetY: 0 };
    }

    case 'hexFlat': {
      // Flat-top hex (rotated 90 from pointy)
      const colSpacing = subW * 0.75 + subGr;
      const rowSpacing = subH + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: 0, oddColOffsetY: rowSpacing / 2 };
    }

    case 'penny': {
      // Hex-packed circles
      const diameter = subW;
      const colSpacing = diameter + subGr;
      const rowSpacing = diameter * HALF_SQRT3 + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: (diameter + subGr) / 2, oddColOffsetY: 0 };
    }

    case 'fishscale': {
      // Circular arc tessellation: stem = dome radius = W/2
      const colSpacing = subW + subGr;
      const rowSpacing = subW / 2 + subGr;  // stem length = dome radius
      return { colSpacing, rowSpacing, oddRowOffsetX: colSpacing / 2, oddColOffsetY: 0 };
    }

    case 'square': {
      return {
        colSpacing: subW + subGr,
        rowSpacing: subH + subGr,
        oddRowOffsetX: 0,
        oddColOffsetY: 0,
      };
    }

    case 'diamond': {
      // 45-degree rotated square
      // Effective width after rotation: diagonal = subW * sqrt(2)
      // But tiles are specified by face size, not diagonal
      const halfW = subW / 2;
      const halfH = subH / 2;
      const colSpacing = subW + subGr;
      const rowSpacing = subH / 2 + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: colSpacing / 2, oddColOffsetY: 0 };
    }

    case 'rectangle': {
      // Herringbone: alternating 90-degree rotated rectangles
      // Effective pattern unit: subW x subW (because rotated piece occupies subH x subW)
      const colSpacing = subW + subGr;
      const rowSpacing = subH + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: 0, oddColOffsetY: 0 };
    }

    case 'octagonDot': {
      // Octagon side length
      const side = subW / (1 + SQRT2);
      // Dot fills the gap: dot ≈ side
      // Center-to-center = subW + dot gap grout
      const colSpacing = subW + side + subGr;
      const rowSpacing = subH + side + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: 0, oddColOffsetY: 0 };
    }

    case 'arabesque': {
      // Lantern shape: staggered rows
      const colSpacing = subW + subGr;
      const rowSpacing = subH + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: colSpacing / 2, oddColOffsetY: 0 };
    }

    case 'elongatedHex': {
      // Same tessellation logic as pointy hex but elongated
      const colSpacing = subW + subGr;
      const rowSpacing = subH * 0.75 + subGr;
      return { colSpacing, rowSpacing, oddRowOffsetX: colSpacing / 2, oddColOffsetY: 0 };
    }

    default:
      return {
        colSpacing: subW + subGr,
        rowSpacing: subH + subGr,
        oddRowOffsetX: 0,
        oddColOffsetY: 0,
      };
  }
}

// ─────────────────────────────────────────────
// computeSubTileCount
// ─────────────────────────────────────────────

/**
 * Compute how many sub-tiles fit in a sheet.
 *
 * @param {number} sheetW - Sheet width in inches
 * @param {number} sheetH - Sheet height in inches
 * @param {string} subShape - Sub-tile shape name
 * @param {number} subW - Sub-tile width in inches
 * @param {number} subH - Sub-tile height in inches
 * @param {number} subGr - Grout gap between sub-tiles in inches
 * @returns {{ cols: number, rows: number, total: number, coverage: number }}
 *   coverage is a ratio 0-1 of sheet area covered by sub-tiles
 */
export function computeSubTileCount(sheetW, sheetH, subShape, subW, subH, subGr) {
  const spacing = computeSpacing(subShape, subW, subH, subGr);
  const { colSpacing, rowSpacing, oddRowOffsetX, oddColOffsetY } = spacing;

  if (colSpacing <= 0 || rowSpacing <= 0) {
    return { cols: 0, rows: 0, total: 0, coverage: 0 };
  }

  // Special handling for herringbone rectangle
  if (subShape === 'rectangle') {
    return computeHerringboneCount(sheetW, sheetH, subW, subH, subGr);
  }

  // Special handling for octagon+dot
  if (subShape === 'octagonDot') {
    return computeOctDotCount(sheetW, sheetH, subW, subH, subGr);
  }

  // For standard grid and offset-grid patterns
  const rows = Math.floor((sheetH - subH) / rowSpacing) + 1;

  let total = 0;
  let baseCols = 0;

  for (let r = 0; r < rows; r++) {
    const isOddRow = r % 2 === 1;
    const effectiveW = isOddRow && oddRowOffsetX > 0
      ? sheetW - oddRowOffsetX
      : sheetW;

    // First tile occupies subW, each additional tile adds colSpacing
    const cols = effectiveW >= subW
      ? Math.floor((effectiveW - subW) / colSpacing) + 1
      : 0;

    if (r === 0) baseCols = cols;
    total += cols;
  }

  const tileCoverageEach = computeSubTileCoverage(subShape, subW, subH);
  const sheetArea = sheetW * sheetH;
  const coverage = sheetArea > 0 ? (total * tileCoverageEach) / sheetArea : 0;

  return {
    cols: baseCols,
    rows,
    total,
    coverage: Math.min(coverage, 1),
  };
}

/**
 * Herringbone rectangle sub-tile count.
 * Two rectangles form a unit: one horizontal, one vertical (rotated 90).
 */
function computeHerringboneCount(sheetW, sheetH, subW, subH, subGr) {
  // A herringbone unit cell is approximately subW x subW in size
  // (one horizontal rect + one vertical rect)
  const unitW = subW + subH + subGr;
  const unitH = subH + subGr;

  const unitCols = Math.floor(sheetW / unitW);
  const unitRows = Math.floor(sheetH / unitH);

  // Each unit contains 2 rectangles (one horizontal, one vertical)
  // But the vertical piece also occupies subW height, so rows interlock
  const horizRows = Math.floor((sheetH - subH) / (subH + subGr)) + 1;
  const vertRows = Math.floor((sheetH - subW) / (subH + subGr)) + 1;

  // Simplified: count pairs
  const pairCols = Math.floor((sheetW) / (subW + subGr));
  const pairRows = Math.floor((sheetH) / (subW + subGr));
  const total = pairCols * pairRows * 2;

  const tileArea = subW * subH;
  const sheetArea = sheetW * sheetH;
  const coverage = sheetArea > 0 ? (total * tileArea) / sheetArea : 0;

  return {
    cols: pairCols,
    rows: pairRows,
    total,
    coverage: Math.min(coverage, 1),
  };
}

/**
 * Octagon + dot sub-tile count.
 * Each octagon has associated corner dots shared with neighbors.
 */
function computeOctDotCount(sheetW, sheetH, subW, subH, subGr) {
  const side = subW / (1 + SQRT2);
  const dotSize = side;
  const pitch = subW + dotSize + subGr; // center-to-center

  const cols = pitch > 0 ? Math.floor((sheetW - subW) / pitch) + 1 : 0;
  const rows = pitch > 0 ? Math.floor((sheetH - subH) / pitch) + 1 : 0;

  const octCount = cols * rows;

  // Dots sit between octagons: (cols-1)*(rows-1) interior dots,
  // plus partial dots along edges. Simplified: dots ≈ octCount
  // More precisely: dots at every intersection = (cols-1)*(rows-1) interior
  // + edge dots partially within sheet
  const dotCols = Math.max(0, cols - 1);
  const dotRows = Math.max(0, rows - 1);
  const dotCount = dotCols * dotRows;

  const octArea = 2 * (1 + SQRT2) * side * side;
  const dotArea = dotSize * dotSize;
  const totalCoverage = octCount * octArea + dotCount * dotArea;
  const sheetArea = sheetW * sheetH;

  return {
    cols,
    rows,
    total: octCount + dotCount,
    totalOctagons: octCount,
    totalDots: dotCount,
    coverage: sheetArea > 0 ? Math.min(totalCoverage / sheetArea, 1) : 0,
  };
}

// ─────────────────────────────────────────────
// validateTileGeometry
// ─────────────────────────────────────────────

/**
 * Validate that a tile preset's geometry is self-consistent.
 *
 * @param {Object} preset - Tile preset with fields:
 *   { name, sheetW, sheetH, subShape, subW, subH, subGr, ... }
 * @returns {{ valid: boolean, errors: string[], warnings: string[], computed: Object }}
 */
export function validateTileGeometry(preset) {
  const errors = [];
  const warnings = [];
  const computed = {};

  const { sheetW, sheetH, subShape, subW, subH, subGr } = preset;

  // Basic sanity checks
  if (!subShape) {
    errors.push('subShape is required');
    return { valid: false, errors, warnings, computed };
  }

  if (!SHAPE_DEFAULTS[subShape]) {
    errors.push(`Unknown subShape: "${subShape}". Valid shapes: ${Object.keys(SHAPE_DEFAULTS).join(', ')}`);
    return { valid: false, errors, warnings, computed };
  }

  if (!subW || subW <= 0) errors.push('subW must be a positive number');
  if (!subH || subH <= 0) errors.push('subH must be a positive number');
  if (subGr == null || subGr < 0) errors.push('subGr must be >= 0');

  if (errors.length > 0) {
    return { valid: false, errors, warnings, computed };
  }

  // Check aspect ratio
  const aspect = subH / subW;
  const shapeDef = SHAPE_DEFAULTS[subShape];
  const expectedH = computeSubTileHeight(subShape, subW);
  const aspectDiff = Math.abs(subH - expectedH) / expectedH;

  computed.expectedSubH = round4(expectedH);
  computed.actualAspect = round4(aspect);
  computed.expectedAspect = round4(shapeDef.aspectRatio);
  computed.aspectDeviation = round4(aspectDiff);

  if (aspectDiff > 0.15) {
    warnings.push(
      `subH (${subH}) deviates ${(aspectDiff * 100).toFixed(1)}% from expected ${round4(expectedH)} for ${subShape}. ` +
      `Acceptable range: ${round4(subW * shapeDef.minAspect)} - ${round4(subW * shapeDef.maxAspect)}`
    );
  }

  // Check sub-tiles fit in sheet (if sheet dims provided)
  if (sheetW && sheetH) {
    if (subW > sheetW) errors.push(`subW (${subW}) exceeds sheetW (${sheetW})`);
    if (subH > sheetH) errors.push(`subH (${subH}) exceeds sheetH (${sheetH})`);

    if (errors.length === 0) {
      const count = computeSubTileCount(sheetW, sheetH, subShape, subW, subH, subGr);
      computed.tilesPerSheet = count;

      if (count.total === 0) {
        errors.push('No sub-tiles fit within the sheet dimensions');
      }

      if (count.coverage < 0.3) {
        warnings.push(
          `Low coverage: only ${(count.coverage * 100).toFixed(1)}% of sheet area is covered by sub-tiles`
        );
      }
    }
  }

  // Grout sanity
  if (subGr > subW * 0.5) {
    warnings.push(`Grout gap (${subGr}) is more than half the tile width — likely a mistake`);
  }

  // Shape-specific validations
  if (subShape === 'penny' && Math.abs(subW - subH) > 0.01) {
    errors.push(`Penny round must have subW === subH (circle). Got ${subW} x ${subH}`);
  }

  if (subShape === 'octagonDot' && Math.abs(subW - subH) > 0.01) {
    errors.push(`Octagon+dot must have subW === subH (square bounding box). Got ${subW} x ${subH}`);
  }

  if (subShape === 'elongatedHex') {
    const elongation = subW / subH;
    if (elongation < 1.5) {
      warnings.push(`Elongated hex has low elongation ratio (${round4(elongation)}:1). Consider using regular hex.`);
    }
  }

  // Spacing computation for reference
  const spacing = computeSpacing(subShape, subW, subH, subGr);
  computed.spacing = {
    colSpacing: round4(spacing.colSpacing),
    rowSpacing: round4(spacing.rowSpacing),
    oddRowOffsetX: round4(spacing.oddRowOffsetX),
    oddColOffsetY: round4(spacing.oddColOffsetY),
  };

  computed.tileCoverage = round4(computeSubTileCoverage(subShape, subW, subH));

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    computed,
  };
}

// ─────────────────────────────────────────────
// autoCorrectPreset
// ─────────────────────────────────────────────

/**
 * Validate and auto-correct a preset's geometry.
 * Returns a new preset object with corrections applied.
 *
 * @param {Object} preset - The original preset
 * @returns {{ corrected: Object, changes: string[] }}
 */
export function autoCorrectPreset(preset) {
  const corrected = { ...preset };
  const changes = [];

  const { subShape, subW, subH, subGr } = corrected;

  if (!subShape || !SHAPE_DEFAULTS[subShape]) {
    return { corrected, changes: ['Unknown or missing subShape — cannot auto-correct'] };
  }

  // Fix missing subH
  if (!subH || subH <= 0) {
    corrected.subH = computeSubTileHeight(subShape, subW);
    changes.push(`Set subH to ${corrected.subH} (computed from subW=${subW} for ${subShape})`);
  }

  // Fix missing grout
  if (subGr == null || subGr < 0) {
    corrected.subGr = 0.125; // 1/8" default grout
    changes.push(`Set subGr to 0.125 (default 1/8")`);
  }

  // Force equal dimensions for penny and octagonDot
  if (subShape === 'penny' && corrected.subW !== corrected.subH) {
    corrected.subH = corrected.subW;
    changes.push(`Set subH = subW = ${corrected.subW} (penny round must be circular)`);
  }

  if (subShape === 'octagonDot' && corrected.subW !== corrected.subH) {
    corrected.subH = corrected.subW;
    changes.push(`Set subH = subW = ${corrected.subW} (octagon+dot must be square)`);
  }

  // Check if subH is way off and suggest correction
  const expectedH = computeSubTileHeight(subShape, corrected.subW);
  const deviation = Math.abs(corrected.subH - expectedH) / expectedH;

  if (deviation > 0.2 && subShape !== 'square' && subShape !== 'rectangle') {
    const oldH = corrected.subH;
    corrected.subH = round4(expectedH);
    changes.push(
      `Corrected subH from ${oldH} to ${corrected.subH} ` +
      `(${(deviation * 100).toFixed(1)}% deviation from expected for ${subShape})`
    );
  }

  // Ensure sub-tiles fit in sheet
  if (corrected.sheetW && corrected.sheetH) {
    if (corrected.subW > corrected.sheetW) {
      changes.push(`WARNING: subW (${corrected.subW}) exceeds sheetW (${corrected.sheetW}) — cannot auto-correct`);
    }
    if (corrected.subH > corrected.sheetH) {
      changes.push(`WARNING: subH (${corrected.subH}) exceeds sheetH (${corrected.sheetH}) — cannot auto-correct`);
    }
  }

  return { corrected, changes };
}

// ─────────────────────────────────────────────
// computeSheetCutGeometry
// ─────────────────────────────────────────────

/**
 * Compute which sub-tiles are affected by a cut at a given position,
 * and describe the cut line geometry.
 *
 * Used for cut tracking: when a sheet is placed at the edge of the layout,
 * some sub-tiles are cut. This tells you which ones and where the cut falls.
 *
 * @param {number} sheetW - Sheet width in inches
 * @param {number} sheetH - Sheet height in inches
 * @param {string} subShape - Sub-tile shape
 * @param {number} subW - Sub-tile width in inches
 * @param {number} subH - Sub-tile height in inches
 * @param {number} subGr - Grout gap in inches
 * @param {{ x: number, y: number, angle: number }} cutPosition
 *   x, y: position of the cut line relative to the sheet origin (top-left)
 *   angle: cut angle in degrees (0 = vertical cut, 90 = horizontal cut)
 * @returns {{ cutLine: Object, affectedSubTiles: Array }}
 */
export function computeSheetCutGeometry(sheetW, sheetH, subShape, subW, subH, subGr, cutPosition) {
  const { x: cutX, y: cutY, angle: cutAngle } = cutPosition;
  const angleRad = (cutAngle || 0) * Math.PI / 180;

  const spacing = computeSpacing(subShape, subW, subH, subGr);
  const { colSpacing, rowSpacing, oddRowOffsetX } = spacing;

  // Build the sub-tile grid positions
  const tiles = [];
  const rows = rowSpacing > 0 ? Math.floor((sheetH - subH) / rowSpacing) + 1 : 0;

  for (let r = 0; r < rows; r++) {
    const isOddRow = r % 2 === 1;
    const rowOffsetX = isOddRow ? oddRowOffsetX : 0;
    const tileY = r * rowSpacing;

    const effectiveW = isOddRow && oddRowOffsetX > 0 ? sheetW - oddRowOffsetX : sheetW;
    const cols = colSpacing > 0 && effectiveW >= subW
      ? Math.floor((effectiveW - subW) / colSpacing) + 1
      : 0;

    for (let c = 0; c < cols; c++) {
      const tileX = rowOffsetX + c * colSpacing;
      tiles.push({
        row: r,
        col: c,
        x: round4(tileX),
        y: round4(tileY),
        w: subW,
        h: subH,
      });
    }
  }

  // Determine which tiles the cut line intersects
  // Cut line: point (cutX, cutY) with angle cutAngle
  // For a vertical cut (angle=0): all tiles whose x-range spans cutX
  // For a horizontal cut (angle=90): all tiles whose y-range spans cutY
  // General: use line intersection with tile bounding box

  const affectedSubTiles = [];

  for (const tile of tiles) {
    if (tileIntersectsCutLine(tile, cutX, cutY, angleRad)) {
      // Compute how much of this tile is on each side of the cut
      const cutInfo = computeTileCutFraction(tile, cutX, cutY, angleRad);
      affectedSubTiles.push({
        ...tile,
        cutFractionKept: round4(cutInfo.kept),
        cutFractionRemoved: round4(cutInfo.removed),
        cutEdgeLength: round4(cutInfo.edgeLength),
      });
    }
  }

  // Cut line definition (start and end points within sheet bounds)
  const cutLine = computeCutLineEndpoints(sheetW, sheetH, cutX, cutY, angleRad);

  return {
    cutLine,
    affectedSubTiles,
    totalTiles: tiles.length,
    cutTiles: affectedSubTiles.length,
    wholeTilesKept: tiles.length - affectedSubTiles.length,
  };
}

/**
 * Check if a tile's bounding box intersects a cut line.
 */
function tileIntersectsCutLine(tile, cutX, cutY, angleRad) {
  const cos = Math.cos(angleRad);
  const sin = Math.sin(angleRad);

  // The cut line passes through (cutX, cutY) with direction (sin, -cos)
  // (perpendicular: normal is (cos, sin))
  // A point is on one side if dot((px-cutX, py-cutY), (cos, sin)) > 0

  // Check the 4 corners of the tile bounding box
  const corners = [
    [tile.x, tile.y],
    [tile.x + tile.w, tile.y],
    [tile.x, tile.y + tile.h],
    [tile.x + tile.w, tile.y + tile.h],
  ];

  let hasPositive = false;
  let hasNegative = false;

  for (const [px, py] of corners) {
    const d = (px - cutX) * cos + (py - cutY) * sin;
    if (d > 0.001) hasPositive = true;
    if (d < -0.001) hasNegative = true;
  }

  // Tile is intersected if corners are on both sides of the line
  return hasPositive && hasNegative;
}

/**
 * Compute what fraction of a tile is kept vs removed by a cut line.
 * Simplified: uses bounding box approximation.
 */
function computeTileCutFraction(tile, cutX, cutY, angleRad) {
  const cos = Math.cos(angleRad);
  const sin = Math.sin(angleRad);

  // Sample points across the tile to estimate fraction
  const samples = 10;
  let keptCount = 0;
  const totalSamples = samples * samples;

  for (let i = 0; i < samples; i++) {
    for (let j = 0; j < samples; j++) {
      const px = tile.x + (tile.w * (i + 0.5)) / samples;
      const py = tile.y + (tile.h * (j + 0.5)) / samples;
      const d = (px - cutX) * cos + (py - cutY) * sin;
      if (d <= 0) keptCount++;
    }
  }

  const kept = keptCount / totalSamples;

  // Approximate cut edge length through the tile
  // For a simple bounding box, the cut line length through a rectangle
  // depends on the angle. Simplified estimate:
  let edgeLength;
  if (Math.abs(cos) < 0.01) {
    // Nearly horizontal cut
    edgeLength = tile.w;
  } else if (Math.abs(sin) < 0.01) {
    // Nearly vertical cut
    edgeLength = tile.h;
  } else {
    // Diagonal: approximate
    edgeLength = Math.min(tile.w / Math.abs(sin), tile.h / Math.abs(cos));
  }

  return {
    kept,
    removed: 1 - kept,
    edgeLength,
  };
}

/**
 * Compute where the cut line enters and exits the sheet bounds.
 */
function computeCutLineEndpoints(sheetW, sheetH, cutX, cutY, angleRad) {
  // Direction along the cut line
  const dx = Math.sin(angleRad);
  const dy = -Math.cos(angleRad);

  // Find intersections with sheet boundary (0,0)-(sheetW, sheetH)
  const intersections = [];

  // Left edge (x=0)
  if (Math.abs(dx) > 1e-10) {
    const t = (0 - cutX) / dx;
    const y = cutY + t * dy;
    if (y >= 0 && y <= sheetH) intersections.push({ x: 0, y: round4(y), edge: 'left' });
  }

  // Right edge (x=sheetW)
  if (Math.abs(dx) > 1e-10) {
    const t = (sheetW - cutX) / dx;
    const y = cutY + t * dy;
    if (y >= 0 && y <= sheetH) intersections.push({ x: sheetW, y: round4(y), edge: 'right' });
  }

  // Top edge (y=0)
  if (Math.abs(dy) > 1e-10) {
    const t = (0 - cutY) / dy;
    const x = cutX + t * dx;
    if (x >= 0 && x <= sheetW) intersections.push({ x: round4(x), y: 0, edge: 'top' });
  }

  // Bottom edge (y=sheetH)
  if (Math.abs(dy) > 1e-10) {
    const t = (sheetH - cutY) / dy;
    const x = cutX + t * dx;
    if (x >= 0 && x <= sheetW) intersections.push({ x: round4(x), y: sheetH, edge: 'bottom' });
  }

  // Deduplicate corner intersections
  const unique = [];
  for (const pt of intersections) {
    const isDup = unique.some(u => Math.abs(u.x - pt.x) < 0.001 && Math.abs(u.y - pt.y) < 0.001);
    if (!isDup) unique.push(pt);
  }

  return {
    start: unique[0] || null,
    end: unique[1] || null,
    length: unique.length >= 2
      ? round4(Math.hypot(unique[1].x - unique[0].x, unique[1].y - unique[0].y))
      : 0,
  };
}

// ─────────────────────────────────────────────
// Utility
// ─────────────────────────────────────────────

function round4(n) {
  return Math.round(n * 10000) / 10000;
}

// ─────────────────────────────────────────────
// Default export for convenience
// ─────────────────────────────────────────────

export default {
  validateTileGeometry,
  computeSubTileCount,
  computeSubTileHeight,
  computeSubTileCoverage,
  autoCorrectPreset,
  computeSheetCutGeometry,
  SHAPE_DEFAULTS,
};
