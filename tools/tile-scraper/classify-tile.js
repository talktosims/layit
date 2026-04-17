/**
 * classify-tile.js
 *
 * Replaces extract-geometry.js with a classification-based approach.
 * Instead of asking AI to produce exact vertex coordinates (error-prone),
 * we ask Opus to CLASSIFY the pattern into a known type, then use
 * mathematically-derived geometry from our pattern library.
 *
 * Flow:
 *   1. User provides image URL or local file
 *   2. Opus classifies: pattern type, wallpaper group, dimensions, grout style
 *   3. Output is a compact preset that references our math library
 *   4. Stored in Firebase tiledb/{barcode} — no further API calls needed
 *
 * Usage:
 *   node classify-tile.js <image-url-or-path>
 *   node classify-tile.js --batch <file-with-urls>
 *   node classify-tile.js --url <product-page-url>   (fetches images from page)
 */

import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const envContent = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
const apiKeyMatch = envContent.match(/ANTHROPIC_API_KEY=(.+)/);
if (!apiKeyMatch) { console.error('No ANTHROPIC_API_KEY in .env'); process.exit(1); }
const client = new Anthropic({ apiKey: apiKeyMatch[1].trim() });

// All pattern types supported by LayIt's math library
const KNOWN_PATTERNS = {
  hex:         { wallpaperGroup: 'p6m', description: 'Hexagon (pointy-top or flat-top)' },
  penny:       { wallpaperGroup: 'p6m', description: 'Penny round / circle mosaic' },
  fishscale:   { wallpaperGroup: 'cmm', description: 'Fish scale / scallop / fan' },
  square:      { wallpaperGroup: 'p4m', description: 'Square grid' },
  diamond:     { wallpaperGroup: 'cmm', description: 'Diamond (45° rotated square)' },
  rectangle:   { wallpaperGroup: 'pmm', description: 'Rectangle / brick / subway' },
  herringbone: { wallpaperGroup: 'pgg', description: 'Herringbone (alternating 45° rectangles)' },
  chevron:     { wallpaperGroup: 'pmm', description: 'Chevron / V-pattern' },
  octdot:      { wallpaperGroup: 'p4m', description: 'Octagon and dot' },
  starcross:   { wallpaperGroup: 'p4m', description: 'Star and cross (4-pointed concave star + cross filler)' },
  arabesque:   { wallpaperGroup: 'p2',  description: 'Arabesque / lantern / Moorish' },
  ogee:        { wallpaperGroup: 'p2',  description: 'Ogee / Provençal / gothic arch' },
  leaf:        { wallpaperGroup: 'p2',  description: 'Leaf / teardrop / petal (double-pointed)' },
  kite:        { wallpaperGroup: 'p2',  description: 'Kite / elongated diamond' },
  picket:      { wallpaperGroup: 'p6m', description: 'Picket / elongated hexagon' },
  rhombus:     { wallpaperGroup: 'p6m', description: 'Rhombus / tumbling blocks / 3D cube' },
  triangle:    { wallpaperGroup: 'p6m', description: 'Equilateral triangle' },
  capsule:     { wallpaperGroup: 'p4m', description: 'Capsule / pill / stadium' },
  quatrefoil:  { wallpaperGroup: 'p4m', description: 'Quatrefoil / 4-lobe clover' },
  dragonscale: { wallpaperGroup: 'cmm', description: 'Dragon scale / pointed oval' },
  ledger:      { wallpaperGroup: 'pmm', description: 'Stacked ledger / splitface stone strips' },
};

const CLASSIFY_PROMPT = `You are a tile pattern classification expert. Look at this tile image and classify it.

IMPORTANT: You are NOT extracting geometry or coordinates. You are CLASSIFYING which pattern type this is from a known library.

Available pattern types:
${Object.entries(KNOWN_PATTERNS).map(([id, p]) => `- "${id}": ${p.description} (${p.wallpaperGroup})`).join('\n')}

Analyze the image and return ONLY valid JSON:
{
  "pattern_id": "one of the IDs above",
  "confidence": 0.0-1.0,
  "orientation": "pointy" or "flat" (for hex/picket) or "horizontal" or "vertical" (for rectangle/herringbone) or "standard",
  "sub_tile_width_inches": best estimate of individual tile width in inches (use grout lines and typical product sizes as reference),
  "sub_tile_height_inches": best estimate of individual tile height in inches,
  "grout_gap_inches": estimated grout gap (typically 0.0625 for mosaic, 0.125 for standard, 0.1875 for planks),
  "material": "ceramic" | "porcelain" | "marble" | "glass" | "cement" | "natural_stone" | "unknown",
  "color_description": "brief color description",
  "sheet_mounted": true/false (is this a mesh-backed mosaic sheet?),
  "sheet_width_inches": if sheet_mounted, estimated sheet width (typically 12),
  "sheet_height_inches": if sheet_mounted, estimated sheet height (typically 12),
  "product_name": "your best guess at product name/style",
  "notes": "any observations about the pattern, unusual features, or if it doesn't perfectly match any type"
}

Rules:
- If the pattern doesn't match any known type, use the closest match and note the difference
- For multi-shape patterns (like star+cross, octagon+dot), use the primary shape ID
- Estimate dimensions based on visual cues: grout line thickness relative to tile size, typical product sizes
- Standard mosaic tiles are usually 1-2" on a 12x12 sheet
- Standard wall/floor tiles are usually 3-12"
- Penny rounds are typically 3/4" to 1" diameter
- Hexagons are typically 1" (mosaic) or 6-8" (floor)`;

async function classifyFromUrl(imageUrl) {
  console.log(`\nClassifying: ${imageUrl}`);

  const response = await client.messages.create({
    model: 'claude-opus-4-20250514',
    max_tokens: 2048,
    messages: [{
      role: 'user',
      content: [
        { type: 'image', source: { type: 'url', url: imageUrl } },
        { type: 'text', text: CLASSIFY_PROMPT }
      ]
    }]
  });

  return parseResponse(response);
}

async function classifyFromFile(filePath) {
  console.log(`\nClassifying file: ${filePath}`);

  const imageData = fs.readFileSync(filePath);
  const base64 = imageData.toString('base64');
  const ext = path.extname(filePath).toLowerCase();
  const mediaType = ext === '.png' ? 'image/png' :
                    ext === '.webp' ? 'image/webp' :
                    ext === '.gif' ? 'image/gif' : 'image/jpeg';

  const response = await client.messages.create({
    model: 'claude-opus-4-20250514',
    max_tokens: 2048,
    messages: [{
      role: 'user',
      content: [
        { type: 'image', source: { type: 'base64', media_type: mediaType, data: base64 } },
        { type: 'text', text: CLASSIFY_PROMPT }
      ]
    }]
  });

  return parseResponse(response);
}

function parseResponse(response) {
  const text = response.content[0].text;
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    console.error('No JSON found in response');
    console.log('Raw response:', text);
    return null;
  }
  try {
    return JSON.parse(jsonMatch[0]);
  } catch (e) {
    console.error('Failed to parse JSON:', e.message);
    console.log('Raw JSON:', jsonMatch[0]);
    return null;
  }
}

/**
 * Convert classification result to a LayIt tile preset.
 * This is what gets stored in Firebase tiledb/{barcode}.
 * The math library in the app generates perfect geometry from these params.
 */
function classificationToPreset(classification, barcode) {
  if (!classification) return null;

  const pattern = KNOWN_PATTERNS[classification.pattern_id];
  if (!pattern) {
    console.warn(`Unknown pattern_id: ${classification.pattern_id}`);
    return null;
  }

  const preset = {
    // Identity
    barcode: barcode || null,
    name: classification.product_name || classification.pattern_id,
    classifiedBy: 'opus',
    classifiedAt: new Date().toISOString(),
    confidence: classification.confidence,

    // Pattern reference (the app's math library handles geometry)
    shape: classification.sheet_mounted ? 'mosaic' : classification.pattern_id,
    subShape: classification.pattern_id,
    wallpaperGroup: pattern.wallpaperGroup,
    orientation: classification.orientation,

    // Dimensions (inches)
    subW: classification.sub_tile_width_inches,
    subH: classification.sub_tile_height_inches,
    grout: classification.grout_gap_inches,

    // Sheet info (for mosaic)
    ...(classification.sheet_mounted && {
      nomW: classification.sheet_width_inches,
      nomH: classification.sheet_height_inches,
      actW: classification.sheet_width_inches - 0.125, // typical nominal→actual
      actH: classification.sheet_height_inches - 0.125,
    }),

    // Metadata
    material: classification.material,
    color: classification.color_description,
    notes: classification.notes,
  };

  return preset;
}

// --- Main ---
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage:');
    console.log('  node classify-tile.js <image-url-or-path>');
    console.log('  node classify-tile.js --batch <file-with-urls>');
    console.log('  node classify-tile.js --barcode <barcode> <image-url-or-path>');
    console.log('\nKnown patterns:');
    for (const [id, p] of Object.entries(KNOWN_PATTERNS)) {
      console.log(`  ${id.padEnd(14)} ${p.description}`);
    }
    process.exit(1);
  }

  let barcode = null;
  let inputs = [];

  // Parse args
  let i = 0;
  while (i < args.length) {
    if (args[i] === '--barcode' && args[i + 1]) {
      barcode = args[i + 1];
      i += 2;
    } else if (args[i] === '--batch' && args[i + 1]) {
      const lines = fs.readFileSync(args[i + 1], 'utf8')
        .split('\n').filter(l => l.trim() && !l.startsWith('#'));
      for (const line of lines) {
        const [id, url] = line.includes('\t') ? line.split('\t') : [null, line.trim()];
        inputs.push({ barcode: id, input: url });
      }
      i += 2;
    } else {
      inputs.push({ barcode, input: args[i] });
      i++;
    }
  }

  if (inputs.length === 0) {
    console.error('No inputs provided');
    process.exit(1);
  }

  const results = [];

  for (const { barcode: bc, input } of inputs) {
    try {
      const classification = input.startsWith('http')
        ? await classifyFromUrl(input)
        : await classifyFromFile(input);

      if (classification) {
        console.log('\n=== Classification ===');
        console.log(JSON.stringify(classification, null, 2));

        const preset = classificationToPreset(classification, bc);
        console.log('\n=== LayIt Preset ===');
        console.log(JSON.stringify(preset, null, 2));

        results.push(preset);
      }
    } catch (e) {
      console.error(`Failed: ${e.message}`);
    }
  }

  // Save results
  if (results.length > 0) {
    const outDir = path.join(__dirname, 'output');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    const outPath = path.join(outDir, 'classified_tiles.json');
    const existing = fs.existsSync(outPath) ? JSON.parse(fs.readFileSync(outPath, 'utf8')) : [];
    existing.push(...results);
    fs.writeFileSync(outPath, JSON.stringify(existing, null, 2));
    console.log(`\nSaved ${results.length} result(s) to ${outPath}`);
  }
}

main().catch(console.error);
