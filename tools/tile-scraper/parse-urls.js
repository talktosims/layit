#!/usr/bin/env node
/**
 * parse-urls.js — URL-based tile spec parser for LayIt
 *
 * Parses tile specifications directly from Home Depot / Lowe's / Floor & Decor
 * product URL slugs. No network requests needed — all specs are in the URL text.
 *
 * Usage:
 *   node parse-urls.js urls-expanded.txt
 *   node parse-urls.js urls-expanded.txt --out output/url_parsed_presets.json
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';

// ─── Fraction parser ──────────────────────────────────────────────────────────
// Converts URL fraction patterns like "11-1-8" → 11.125, "12-5-8" → 12.625
// Also handles "11-1-2" → 11.5, "3-4" as ¾ when in size context, etc.

function parseFraction(str) {
  // Try patterns like "11-1-8" (11 + 1/8), "12-5-8" (12 + 5/8)
  const wholeFracMatch = str.match(/^(\d+)-(\d+)-(\d+)$/);
  if (wholeFracMatch) {
    const whole = parseInt(wholeFracMatch[1]);
    const num = parseInt(wholeFracMatch[2]);
    const den = parseInt(wholeFracMatch[3]);
    if (den > 0) return whole + num / den;
  }
  // Decimal-ish pattern: "11-3" could mean 11.3 (not a fraction)
  // Distinguish from fractions: if denominator would be < 10 and > numerator, it's a fraction
  // But in URL context "11-3" means 11.3 (HD uses this for decimal dimensions)
  const twoPartMatch = str.match(/^(\d+)-(\d+)$/);
  if (twoPartMatch) {
    const a = parseInt(twoPartMatch[1]);
    const b = parseInt(twoPartMatch[2]);
    // If b < 10, treat as decimal (11-3 = 11.3)
    if (b < 10) return parseFloat(`${a}.${b}`);
    return a; // fallback to just the first number
  }
  // Plain number
  const plain = parseFloat(str);
  if (!isNaN(plain)) return plain;
  return null;
}

// Parse a dimension string that might contain fractions
// e.g. "11-1-8-in" → 11.125, "12-in" → 12, "3-in" → 3
function parseDimension(s) {
  // Remove trailing "-in" or "-inch"
  s = s.replace(/-(in|inch)$/i, '');
  return parseFraction(s);
}

// ─── Retailer detection ───────────────────────────────────────────────────────

function detectRetailer(url) {
  if (url.includes('homedepot.com')) return 'Home Depot';
  if (url.includes('lowes.com')) return "Lowe's";
  if (url.includes('flooranddecor.com')) return 'Floor & Decor';
  return 'Unknown';
}

// ─── Barcode extraction ───────────────────────────────────────────────────────

function extractBarcode(url, retailer) {
  if (retailer === 'Home Depot') {
    // Last path segment after the final "/"
    const match = url.match(/\/(\d{6,})(?:\?|$)/);
    if (match) return match[1];
    // Or just the last segment
    const parts = url.split('/');
    const last = parts[parts.length - 1].split('?')[0];
    if (/^\d{6,}$/.test(last)) return last;
  }
  if (retailer === "Lowe's") {
    // Lowe's URLs have item numbers in the path
    const match = url.match(/\/(\d{6,})/);
    if (match) return match[1];
  }
  if (retailer === 'Floor & Decor') {
    const match = url.match(/\/(\d{6,})/);
    if (match) return match[1];
  }
  return null;
}

// ─── Model number extraction ──────────────────────────────────────────────────

function extractModel(slug) {
  // Model is usually the last hyphenated token before the internet number
  // e.g. "FXLM2HMW" in the slug
  // Look for all-caps alphanumeric tokens that look like model numbers
  const tokens = slug.split('-');
  for (let i = tokens.length - 1; i >= 0; i--) {
    const t = tokens[i];
    if (/^[A-Z0-9]{4,}[A-Z]/.test(t) && !/^(Case|Tile|Mosaic|Porcelain|Ceramic|Glass|Marble|Mounted|Glazed)$/i.test(t)) {
      return t;
    }
  }
  return null;
}

// ─── Sub-tile shape detection ─────────────────────────────────────────────────

function detectSubShape(slug) {
  const lower = slug.toLowerCase();

  if (/\bhex\b|\bhexagon\b|\bhexagonal\b/.test(lower)) return 'hex';
  if (/\bpenny[\s-]?round\b|\bpenny\b/.test(lower)) return 'penny';
  if (/\bfish[\s-]?scale\b|\bfan[\s-]?shape\b|\bscallop\b/.test(lower)) return 'fishscale';
  if (/\bdiamond\b/.test(lower)) return 'diamond';
  if (/\bherringbone\b/.test(lower)) return null; // herringbone is a layout pattern, not sub-shape
  if (/\barbaresque\b|\blantern\b/.test(lower)) return 'arabesque';
  if (/\bbasketweave\b/.test(lower)) return null;
  if (/\bchevron\b/.test(lower)) return null;

  return null;
}

// ─── Tile shape detection ─────────────────────────────────────────────────────

function detectTileShape(slug, isMosaic) {
  const lower = slug.toLowerCase();

  if (/\bherringbone\b/.test(lower)) return 'herringbone';
  if (/\bchevron\b/.test(lower)) return 'chevron';
  if (/\bbasketweave\b/.test(lower)) return 'basketweave';
  if (isMosaic) return 'mosaic';

  // Standard tiles — detect from dimensions
  return 'rectangle'; // will be refined later
}

// ─── Material detection ───────────────────────────────────────────────────────

function detectMaterial(slug) {
  const lower = slug.toLowerCase();
  if (/\bporcelain\b/.test(lower)) return 'porcelain';
  if (/\bceramic\b/.test(lower)) return 'ceramic';
  if (/\bglass\b/.test(lower)) return 'glass';
  if (/\bmarble\b/.test(lower)) return 'marble';
  if (/\btravertine\b/.test(lower)) return 'travertine';
  if (/\bstone\b/.test(lower)) return 'stone';
  if (/\bslate\b/.test(lower)) return 'slate';
  if (/\blimestone\b/.test(lower)) return 'limestone';
  if (/\bgranite\b/.test(lower)) return 'granite';
  return 'ceramic'; // default
}

// ─── Color extraction ─────────────────────────────────────────────────────────

const KNOWN_COLORS = [
  'White', 'Black', 'Gray', 'Grey', 'Blue', 'Beige', 'Cream', 'Ivory',
  'Brown', 'Tan', 'Taupe', 'Green', 'Red', 'Yellow', 'Gold', 'Silver',
  'Bianco', 'Nero', 'Grigio', 'Carrara', 'Calacatta', 'Arabescato',
  'Espresso', 'Charcoal', 'Smoke', 'Sand', 'Bone', 'Almond', 'Biscuit',
  'Arctic', 'Ice', 'Snow', 'Pearl', 'Frost', 'Cloud', 'Storm', 'Midnight',
  'Navy', 'Cobalt', 'Sage', 'Mint', 'Emerald', 'Terracotta', 'Rust',
  'Warm', 'Cool', 'Natural'
];

const COLOR_MODIFIERS = [
  'Matte', 'Glossy', 'Gloss', 'Satin', 'Polished', 'Honed', 'Bright',
  'Dark', 'Light', 'Medium', 'Antique', 'Vintage', 'Classic', 'Modern'
];

function extractColor(slug) {
  const tokens = slug.split('-');
  const colorParts = [];

  for (const token of tokens) {
    const cap = token.charAt(0).toUpperCase() + token.slice(1).toLowerCase();
    if (KNOWN_COLORS.includes(cap) || COLOR_MODIFIERS.includes(cap)) {
      colorParts.push(cap);
    }
  }

  // Combine modifier + color (e.g. "Matte White", "Dark Gray")
  if (colorParts.length > 0) return colorParts.join(' ');
  return null;
}

// ─── Brand extraction ─────────────────────────────────────────────────────────

const KNOWN_BRANDS = [
  'Merola Tile', 'Merola', 'MSI', 'Daltile', 'Marazzi', 'Jeffrey Court',
  'SomerTile', 'Elida Ceramica', 'Ivy Hill Tile', 'Giorbello',
  'Florida Tile', 'Satori', 'American Olean', 'Bedrosians', 'Emser',
  'Anatolia', 'Shaw', 'Mohawk', 'LifeProof', 'TrafficMaster',
  'Corso Italia', 'MSI Premium', 'Apollo Tile', 'Abolos'
];

function extractBrand(slug) {
  const lower = slug.toLowerCase();

  // Check multi-word brands first
  for (const brand of KNOWN_BRANDS) {
    const brandSlug = brand.toLowerCase().replace(/\s+/g, '-');
    if (lower.startsWith(brandSlug)) return brand;
  }

  // Check single-word brands
  const firstToken = slug.split('-')[0];
  for (const brand of KNOWN_BRANDS) {
    if (brand.toLowerCase() === firstToken.toLowerCase()) return brand;
  }

  // Fallback: capitalize first token
  return firstToken.charAt(0).toUpperCase() + firstToken.slice(1);
}

// ─── Dimension extraction from URL slug ───────────────────────────────────────

/**
 * Extract dimensions from slug patterns like:
 *   "3-in-x-6-in" → [3, 6]
 *   "11-1-8-in-x-12-5-8-in" → [11.125, 12.625]
 *   "12-in-x-24-in" → [12, 24]
 *   "10-1-4-in-x-11-3-4-in" → [10.25, 11.75]
 */
function extractDimensions(slug) {
  const dims = [];

  // Pattern: dimension-in-x-dimension-in (with optional fractions or decimals)
  // Match patterns like "11-1-8-in", "12-in", "11-3-in" (decimal 11.3)
  // The dimension part can be: "12", "11-3" (decimal), "11-1-8" (fraction)
  const dimPattern = /(\d+(?:-\d+(?:-\d+)?)?)-in-x-(\d+(?:-\d+(?:-\d+)?)?)-in/gi;
  let match;

  while ((match = dimPattern.exec(slug)) !== null) {
    const w = parseDimension(match[1] + '-in');
    const h = parseDimension(match[2] + '-in');
    if (w !== null && h !== null) {
      dims.push([w, h]);
    }
  }

  return dims;
}

/**
 * Extract sub-tile size from slug
 * e.g. "2-in-Hex" → 2, "1-in-Hex" → 1, "3-in-x-6-in-Subway" → [3, 6]
 */
function extractSubTileSize(slug) {
  // "N-in-Hex" or "N-in-Hexagon" patterns (single dimension sub-tile)
  const singleMatch = slug.match(/(\d+(?:-\d+-\d+)?)-in-(?:Hex|Hexagon|Hexagonal)\b/i);
  if (singleMatch) {
    const size = parseDimension(singleMatch[1] + '-in');
    // Sub-tiles are small — reject if >= 6" (that's a sheet dimension)
    if (size && size < 6) return [size];
  }

  // "Penny-Round-N-in" pattern — but only if it's a real sub-tile (< 3")
  const pennySizeMatch = slug.match(/(?:Penny-Round|Penny)[- ](\d+(?:-\d+-\d+)?)-in/i);
  if (pennySizeMatch) {
    const size = parseDimension(pennySizeMatch[1] + '-in');
    if (size && size < 3) return [size];
  }

  // For rectangular sub-tiles in mosaics like "2-in-x-2-in" before "Mosaic"
  // We need the FIRST dimension pair (sub-tile) vs the SECOND (sheet size)
  return null;
}

// ─── Coverage extraction ──────────────────────────────────────────────────────

function extractCoverage(slug) {
  // "10-0-sq-ft" → 10.0, "8-56-sq-ft" → 8.56
  const match = slug.match(/(\d+)-(\d+)-sq-ft/i);
  if (match) {
    return parseFloat(`${match[1]}.${match[2]}`);
  }
  // "0-76-sq-ft" → 0.76
  const match2 = slug.match(/(\d+)-sq-ft/i);
  if (match2) return parseFloat(match2[1]);
  return null;
}

// ─── Fraction to Unicode ──────────────────────────────────────────────────────

const UNICODE_FRACS = {
  '0.125': '⅛', '0.25': '¼', '0.375': '⅜', '0.5': '½',
  '0.625': '⅝', '0.75': '¾', '0.875': '⅞',
  '0.333': '⅓', '0.667': '⅔'
};

function dimToDisplay(val) {
  const whole = Math.floor(val);
  const frac = (val - whole).toFixed(3);
  const unicodeFrac = UNICODE_FRACS[frac];

  if (val === whole) return `${whole}`;
  if (unicodeFrac) return whole > 0 ? `${whole}${unicodeFrac}` : unicodeFrac;
  return val.toString();
}

// ─── Nominal size rounding ────────────────────────────────────────────────────

function toNominal(actual) {
  // Tile nominal size = the standard advertised size
  // Mosaic sheets are often slightly over their nominal (11⅛ → 12, 12⅝ → 12)
  // Standard tiles match or are slightly under their nominal (11.75 → 12)
  // Standard tile nominal sizes (no 13 — not a real tile size)
  const standards = [1, 2, 3, 4, 6, 8, 10, 12, 16, 18, 20, 24, 32, 36, 48];

  let closest = standards[0];
  let minDiff = Math.abs(actual - closest);
  for (const s of standards) {
    const diff = Math.abs(actual - s);
    // On ties, prefer rounding up (11" → 12 nominal, not 10)
    if (diff < minDiff || (diff === minDiff && s > closest)) {
      minDiff = diff;
      closest = s;
    }
  }
  return closest;
}

// ─── Main URL parser ──────────────────────────────────────────────────────────

function parseUrl(url) {
  url = url.trim();
  if (!url || url.startsWith('#')) return null;

  const retailer = detectRetailer(url);
  const barcode = extractBarcode(url, retailer);
  if (!barcode) {
    console.warn(`  ⚠ No barcode found: ${url.substring(0, 80)}...`);
    return null;
  }

  // Extract the slug portion from the URL
  let slug = '';
  if (retailer === 'Home Depot') {
    // /p/Brand-Name-Size-Material-Type-Model/InternetNumber
    const pMatch = url.match(/\/p\/([^/]+)\//);
    if (pMatch) slug = pMatch[1];
  } else if (retailer === "Lowe's") {
    const pathMatch = url.match(/\/pl\/([^/]+)/);
    if (pathMatch) slug = pathMatch[1];
  }

  if (!slug) {
    // Fallback: use full path
    const urlObj = new URL(url);
    slug = urlObj.pathname.replace(/\//g, '-').replace(/^-|-$/g, '');
  }

  // Detect properties from slug
  const brand = extractBrand(slug);
  const material = detectMaterial(slug);
  const color = extractColor(slug);
  const subShape = detectSubShape(slug);
  const isMosaic = /mosaic/i.test(slug) || subShape !== null;
  const tileShape = detectTileShape(slug, isMosaic);
  const model = extractModel(slug);
  const coverage = extractCoverage(slug);

  // Extract dimensions
  const allDims = extractDimensions(slug);
  const subSize = extractSubTileSize(slug);

  let actW, actH, subW, subH;

  if (isMosaic && allDims.length >= 1) {
    // For mosaics: if we have two dimension sets, first is sub-tile,
    // the larger one is the sheet size
    if (allDims.length >= 2) {
      // Sort by area — larger is sheet, smaller might be sub-tile dims
      const sorted = [...allDims].sort((a, b) => (b[0] * b[1]) - (a[0] * a[1]));
      actW = sorted[0][0];
      actH = sorted[0][1];

      // If the smaller dims look like sub-tile size (< 6"), use them
      if (sorted[1][0] <= 6 && sorted[1][1] <= 6) {
        subW = sorted[1][0];
        subH = sorted[1][1];
        // nothing extra needed here
      }
    } else {
      actW = allDims[0][0];
      actH = allDims[0][1];
    }

    // Sub-tile from explicit pattern if not yet found
    if (!subW && subSize) {
      subW = subSize[0];
    }
  } else if (allDims.length >= 1) {
    // Standard tile: use first dimension pair
    actW = allDims[0][0];
    actH = allDims[0][1];
  }

  // Default sub-tile sizes when shape detected but size not found
  if (subShape === 'hex' && !subW) {
    subW = 2; // default 2" hex
  }
  if (subShape === 'penny' && !subW) {
    subW = 0.75; // standard penny round
  }
  if (subShape === 'fishscale' && !subW) {
    subW = 2; // default fishscale
  }

  // If we found sub-tile dimensions but no subShape, and it's mosaic, infer square
  if (isMosaic && subW && subH && !subShape && Math.abs(subW - subH) < 0.1) {
    // Square sub-tiles on a mosaic sheet — keep subW/subH but don't force a shape name
    // (the LayIt renderer handles square mosaics as regular grid)
  }

  // Calculate sub-tile dimensions based on shape
  if (subShape === 'hex' && subW && !subH) {
    subH = +(subW * 1.125).toFixed(4);
  } else if (subShape === 'penny' && subW && !subH) {
    subH = subW;
  } else if (subShape === 'fishscale' && subW && !subH) {
    subH = subW;
  }

  // Default sub-tile grout
  const subGr = subShape ? 0.0625 : undefined;

  // Nominal sizes
  const nomW = actW ? toNominal(actW) : undefined;
  const nomH = actH ? toNominal(actH) : undefined;

  // Build display name
  let displayName = '';
  const brandShort = brand.replace(' Tile', '');
  if (subShape && subW) {
    displayName = `${subW}" ${subShape.charAt(0).toUpperCase() + subShape.slice(1)}`;
  } else if (actW && actH) {
    displayName = `${dimToDisplay(actW)}x${dimToDisplay(actH)}`;
  }
  if (color) displayName += ` ${color}`;
  if (actW && actH) {
    displayName += ` (${dimToDisplay(actW)}×${dimToDisplay(actH)})`;
  }

  // Determine orient for hex
  const orient = subShape === 'hex' ? 'pointy' : undefined;

  // Determine shape for non-mosaic standard tiles
  let finalShape = tileShape;
  if (!isMosaic && actW && actH) {
    if (Math.abs(actW - actH) < 0.5) {
      finalShape = 'square';
    } else {
      finalShape = 'rectangle';
    }
  }

  // Build preset
  const preset = {
    barcode,
    name: displayName.trim(),
    brand: brandShort,
    shape: finalShape,
  };

  if (nomW) preset.nomW = nomW;
  if (nomH) preset.nomH = nomH;
  if (actW) preset.actW = actW;
  if (actH) preset.actH = actH;
  preset.grout = 0.125;

  if (subShape) {
    preset.subShape = subShape;
  }
  if (subW) preset.subW = subW;
  if (subH) preset.subH = subH;
  if (subShape || subW) {
    preset.subGr = subGr || 0.0625;
  }

  if (orient) preset.orient = orient;
  if (material) preset.material = material;
  if (color) preset.color = color;
  if (model) preset.model = model;
  if (coverage) preset.coverageSqFt = coverage;
  preset.retailer = retailer;
  preset.source = 'url-parsed';

  return preset;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node parse-urls.js <urls-file> [--out <output-file>]');
    console.log('');
    console.log('Parses tile specs from retailer product URLs.');
    console.log('Input file: one URL per line, # for comments.');
    process.exit(1);
  }

  const inputFile = resolve(args[0]);
  let outputFile = resolve('output/url_parsed_presets.json');
  const outIdx = args.indexOf('--out');
  if (outIdx !== -1 && args[outIdx + 1]) {
    outputFile = resolve(args[outIdx + 1]);
  }

  console.log(`\nLayIt URL Tile Parser`);
  console.log(`━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Input:  ${inputFile}`);
  console.log(`Output: ${outputFile}\n`);

  const content = readFileSync(inputFile, 'utf-8');
  const lines = content.split('\n')
    .map(l => l.trim())
    .filter(l => l && !l.startsWith('#'));

  console.log(`Found ${lines.length} URLs to parse.\n`);

  const results = {};
  let parsed = 0;
  let failed = 0;

  for (const url of lines) {
    try {
      const preset = parseUrl(url);
      if (preset) {
        results[preset.barcode] = preset;
        console.log(`  ✓ ${preset.barcode} — ${preset.name}`);
        parsed++;
      } else {
        failed++;
      }
    } catch (err) {
      console.warn(`  ✗ Error parsing: ${url.substring(0, 60)}...`);
      console.warn(`    ${err.message}`);
      failed++;
    }
  }

  // Ensure output directory exists
  mkdirSync(dirname(outputFile), { recursive: true });
  writeFileSync(outputFile, JSON.stringify(results, null, 2));

  console.log(`\n━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Parsed: ${parsed}  |  Failed: ${failed}  |  Total: ${lines.length}`);
  console.log(`Output: ${outputFile}`);
  console.log(`Presets: ${Object.keys(results).length}\n`);
}

main();
