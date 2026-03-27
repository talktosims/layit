/**
 * extract-geometry.js
 *
 * Takes a tile product image URL, sends it to Claude Vision API,
 * and extracts the tile geometry as normalized vertex paths.
 *
 * Usage:
 *   node extract-geometry.js <image-url>
 *   node extract-geometry.js <local-image-path>
 *   node extract-geometry.js --batch tiles-to-extract.txt
 *
 * Output: JSON preset with tilePath vertices for custom rendering
 */

import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load API key from .env
const envContent = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
const apiKeyMatch = envContent.match(/ANTHROPIC_API_KEY=(.+)/);
if (!apiKeyMatch) { console.error('No ANTHROPIC_API_KEY in .env'); process.exit(1); }
const client = new Anthropic({ apiKey: apiKeyMatch[1].trim() });

const GEOMETRY_PROMPT = `You are a tile geometry extraction expert. Analyze this mosaic tile image and extract the repeating tile pattern.

For EACH unique tile shape in the pattern, provide:

1. **shape_name**: A descriptive name (e.g., "octagon", "dot_square", "ledger_strip", "arabesque", "rhombus", "elongated_hex", "picket")

2. **vertices**: Normalized polygon vertices as an array of [x, y] pairs.
   - Center the shape at [0, 0]
   - Scale so the shape fits in a -0.5 to +0.5 range on both axes
   - For curved shapes (arabesque, fishscale, penny), use "arcs" array instead
   - Go clockwise from the top

3. **tessellation**: How the tiles repeat:
   - "grid" — simple row/column grid
   - "brick" — offset every other row by half
   - "herringbone" — alternating 90° rotations
   - "random_stack" — random-width strips stacked (for ledger/splitface)
   - "multi_shape" — multiple shapes interlock (like oct+dot)

4. **repeat_unit**: The bounding box of one repeating unit in inches [width, height]

5. **sub_tiles**: Array of tiles within one repeat unit, each with:
   - shape_ref: which shape_name
   - offset: [x, y] offset within the repeat unit (normalized 0-1)
   - rotation: degrees of rotation (0 if none)
   - scale: [sx, sy] relative scale within the repeat unit (1.0 = full size)

6. **estimated_dimensions**: Your best guess at sub-tile dimensions in inches based on typical products

Return ONLY valid JSON in this exact format:
{
  "pattern_name": "descriptive name",
  "shapes": [
    {
      "shape_name": "name",
      "vertices": [[x,y], [x,y], ...],
      "width_inches": 0,
      "height_inches": 0
    }
  ],
  "tessellation": "type",
  "repeat_unit": [width, height],
  "sub_tiles": [
    {
      "shape_ref": "name",
      "offset": [x, y],
      "rotation": 0,
      "scale": [1, 1]
    }
  ],
  "notes": "any relevant observations about the pattern"
}`;

async function extractFromUrl(imageUrl) {
    console.log(`\nExtracting geometry from: ${imageUrl}`);

    const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4096,
        messages: [{
            role: 'user',
            content: [
                {
                    type: 'image',
                    source: {
                        type: 'url',
                        url: imageUrl
                    }
                },
                {
                    type: 'text',
                    text: GEOMETRY_PROMPT
                }
            ]
        }]
    });

    const text = response.content[0].text;
    // Extract JSON from response (may be wrapped in markdown code block)
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

async function extractFromFile(filePath) {
    console.log(`\nExtracting geometry from file: ${filePath}`);

    const imageData = fs.readFileSync(filePath);
    const base64 = imageData.toString('base64');
    const ext = path.extname(filePath).toLowerCase();
    const mediaType = ext === '.png' ? 'image/png' :
                      ext === '.webp' ? 'image/webp' :
                      ext === '.gif' ? 'image/gif' : 'image/jpeg';

    const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4096,
        messages: [{
            role: 'user',
            content: [
                {
                    type: 'image',
                    source: {
                        type: 'base64',
                        media_type: mediaType,
                        data: base64
                    }
                },
                {
                    type: 'text',
                    text: GEOMETRY_PROMPT
                }
            ]
        }]
    });

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

function geometryToPreset(geometry, productId) {
    if (!geometry) return null;

    // Convert extracted geometry into a LayIt preset format
    const preset = {
        name: geometry.pattern_name,
        shape: 'mosaic',
        subShape: 'custom',
        tessellation: geometry.tessellation,
        shapes: geometry.shapes.map(s => ({
            name: s.shape_name,
            vertices: s.vertices,
            widthIn: s.width_inches,
            heightIn: s.height_inches
        })),
        repeatUnit: geometry.repeat_unit,
        subTiles: geometry.sub_tiles,
        notes: geometry.notes
    };

    return preset;
}

// --- Main ---
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log('Usage:');
        console.log('  node extract-geometry.js <image-url-or-path>');
        console.log('  node extract-geometry.js --batch <file-with-urls>');
        process.exit(1);
    }

    const results = {};

    if (args[0] === '--batch') {
        const batchFile = args[1];
        const lines = fs.readFileSync(batchFile, 'utf8').split('\n').filter(l => l.trim() && !l.startsWith('#'));

        for (const line of lines) {
            const [id, url] = line.includes('\t') ? line.split('\t') : [path.basename(line, path.extname(line)), line];
            try {
                const geometry = url.startsWith('http') ?
                    await extractFromUrl(url) :
                    await extractFromFile(url);
                results[id] = geometryToPreset(geometry, id);
                console.log(`✓ ${id}: ${geometry?.pattern_name || 'failed'}`);
            } catch (e) {
                console.error(`✗ ${id}: ${e.message}`);
            }
        }
    } else {
        const input = args[0];
        const geometry = input.startsWith('http') ?
            await extractFromUrl(input) :
            await extractFromFile(input);

        if (geometry) {
            console.log('\n=== Extracted Geometry ===');
            console.log(JSON.stringify(geometry, null, 2));

            const preset = geometryToPreset(geometry, 'test');
            console.log('\n=== LayIt Preset ===');
            console.log(JSON.stringify(preset, null, 2));

            results['test'] = preset;
        }
    }

    // Save results
    const outPath = path.join(__dirname, 'output', 'extracted_geometry.json');
    const existing = fs.existsSync(outPath) ? JSON.parse(fs.readFileSync(outPath, 'utf8')) : {};
    Object.assign(existing, results);
    fs.writeFileSync(outPath, JSON.stringify(existing, null, 2));
    console.log(`\nSaved to ${outPath}`);
}

main().catch(console.error);
