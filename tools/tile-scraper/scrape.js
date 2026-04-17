/**
 * LayIt Tile Scraper
 *
 * Fetches tile product pages from retailers using headless Chrome (Puppeteer),
 * sends rendered content to Claude for spec extraction, and outputs preset JSON
 * files ready for the LayIt barcode database.
 *
 * Usage:
 *   node scrape.js <url>                    Scrape a single product page
 *   node scrape.js --batch urls.txt         Scrape multiple URLs from a file
 *
 * Environment:
 *   ANTHROPIC_API_KEY=sk-...                Required for Claude API calls
 *
 * First run:
 *   npm install                             Installs puppeteer + anthropic SDK
 */

import Anthropic from '@anthropic-ai/sdk';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';

puppeteer.use(StealthPlugin());
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Load .env file if it exists (no external dependency needed)
const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = join(__dirname, '.env');
if (existsSync(envPath)) {
  const envContent = readFileSync(envPath, 'utf-8');
  for (const line of envContent.split('\n')) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx > 0) {
        const key = trimmed.slice(0, eqIdx).trim();
        const val = trimmed.slice(eqIdx + 1).trim();
        if (!process.env[key]) process.env[key] = val;
      }
    }
  }
}

const client = new Anthropic();

// The prompt that tells Claude how to extract tile specs from a product page
const EXTRACTION_PROMPT = `You are a tile specification extraction agent for the LayIt tile layout app.

Given the text content of a retail product page for a tile, extract the following information and return it as a JSON object. Be precise — these values drive a rendering engine.

Required fields:
- barcode: UPC/EAN barcode number (string, 12-13 digits). Look for "UPC", "Item #", "Model #", "SKU", or "Internet #"
- name: Product name (string)
- brand: Manufacturer/brand name (string)
- shape: Tile shape category. Must be one of: "rectangle", "square", "mosaic"
  - Use "mosaic" for any sheet-mounted tiles (hex, fishscale, penny, etc.)
  - Use "square" for individual square tiles
  - Use "rectangle" for individual rectangular tiles (including subway)

For shape "rectangle" or "square":
- nomW: Nominal width in inches (e.g., 12 for a "12x24" tile)
- nomH: Nominal height in inches
- actW: Actual width in inches (if listed, otherwise estimate as nominal - 0.25)
- actH: Actual height in inches
- grout: Recommended grout joint width in inches (default 0.125 for 1/8")

For shape "mosaic":
- nomW: Nominal sheet width in inches (e.g., 12)
- nomH: Nominal sheet height in inches
- actW: Actual sheet width in inches (if listed, otherwise nominal - 0.25)
- actH: Actual sheet height in inches
- grout: Recommended grout joint for the sheet-to-sheet joints (default 0.125)
- subShape: Individual tile shape within the sheet. Must be one of:
  "hex", "square", "penny", "fishscale", "diamond", "rectangle"
- subW: Individual sub-tile width in inches
- subH: Individual sub-tile height in inches
- subGr: Grout spacing between sub-tiles in inches (default 0.0625 for 1/16")
- orient: For hex tiles only — "pointy" (pointy-top) or "flat" (flat-top). Default "pointy".

Additional fields (optional):
- material: "ceramic", "porcelain", "glass", "stone", "marble", etc.
- color: Primary color description
- finish: "matte", "glossy", "polished", "honed", "textured", etc.
- pricePerSqFt: Price per square foot if listed
- retailer: Which store (Home Depot, Lowe's, Floor & Decor, Daltile, MSI, TileBar, etc.)
- productUrl: The URL of the product page
- imageUrl: URL of the main product image

IMPORTANT RULES:
1. All dimensions MUST be in inches. Convert from mm or cm if needed (1 inch = 25.4mm).
2. "Nominal" size is what's marketed (e.g., "2 inch hex"). "Actual" is the measured tile size.
3. For mosaic sheets, the sheet size is the overall mesh-backed sheet, NOT the individual tile size.
4. Common sheet sizes: 12"x12", 11"x11", 12"x13", 11.4"x10.9", 10"x12"
5. Common sub-tile sizes: 1" hex, 2" hex, 1" penny round, 2" fishscale
6. If you can't determine a value with confidence, use null rather than guessing.
7. The barcode/UPC is critical — without it, the entry is useless.

Return ONLY the JSON object, no markdown formatting, no explanation.
If you cannot extract enough information to be useful, return: {"error": "reason"}`;

let browser = null;

async function launchBrowser() {
  if (!browser) {
    console.log('Launching headless Chrome...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }
  return browser;
}

async function fetchPageContent(url) {
  console.log(`Fetching: ${url}`);
  const b = await launchBrowser();
  const page = await b.newPage();

  // Look like a real browser
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
  );
  await page.setViewport({ width: 1440, height: 900 });

  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

    // Wait a bit for any lazy-loaded content
    await new Promise(r => setTimeout(r, 2000));

    // Scroll down to trigger lazy loading of specs sections
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await new Promise(r => setTimeout(r, 1500));

    // Try clicking "Specifications" or "Details" tabs if they exist
    try {
      await page.evaluate(() => {
        const tabs = document.querySelectorAll('button, a, [role="tab"]');
        for (const tab of tabs) {
          const text = tab.textContent.toLowerCase();
          if (text.includes('specification') || text.includes('detail') || text.includes('product info')) {
            tab.click();
            break;
          }
        }
      });
      await new Promise(r => setTimeout(r, 1000));
    } catch (e) {
      // Tab click failed, that's fine
    }

    // Get rendered text content
    const text = await page.evaluate(() => {
      return document.body.innerText;
    });

    await page.close();

    // Truncate to ~30k chars to fit in context window
    return text.slice(0, 30000);
  } catch (err) {
    await page.close();
    throw err;
  }
}

async function extractTileSpecs(pageText, url) {
  console.log('Sending to Claude for extraction...');

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2000,
    messages: [{
      role: 'user',
      content: `${EXTRACTION_PROMPT}\n\nProduct page URL: ${url}\n\nPage content:\n${pageText}`
    }]
  });

  const text = response.content[0].text.trim();

  try {
    return JSON.parse(text);
  } catch (e) {
    // Try to extract JSON from the response
    const match = text.match(/\{[\s\S]*\}/);
    if (match) {
      return JSON.parse(match[0]);
    }
    throw new Error(`Failed to parse Claude response: ${text.slice(0, 200)}`);
  }
}

function validatePreset(preset) {
  const errors = [];

  if (!preset.barcode) errors.push('Missing barcode/UPC');
  if (!preset.name) errors.push('Missing product name');
  if (!preset.brand) errors.push('Missing brand');
  if (!preset.shape) errors.push('Missing shape');
  if (!preset.nomW || !preset.nomH) errors.push('Missing nominal dimensions');

  if (preset.shape === 'mosaic') {
    if (!preset.subShape) errors.push('Missing sub-tile shape (subShape)');
    if (!preset.subW || !preset.subH) errors.push('Missing sub-tile dimensions');
  }

  return {
    valid: errors.length === 0,
    errors,
    confidence: errors.length === 0 ? 0.9 : Math.max(0, 0.9 - errors.length * 0.2)
  };
}

function formatPresetForLayIt(preset) {
  // Convert to the format used in BARCODE_PRESETS in index.html
  const entry = {
    name: `${preset.brand} ${preset.name}`,
    brand: preset.brand,
    shape: preset.shape,
    nomW: preset.nomW,
    nomH: preset.nomH,
    actW: preset.actW || preset.nomW - 0.25,
    actH: preset.actH || preset.nomH - 0.25,
    grout: preset.grout || 0.125,
  };

  if (preset.shape === 'mosaic') {
    entry.subShape = preset.subShape;
    entry.subW = preset.subW;
    entry.subH = preset.subH;
    entry.subGr = preset.subGr || 0.0625;
    if (preset.subShape === 'hex' && preset.orient) {
      entry.orient = preset.orient;
    }
  }

  // Extra metadata (not used by renderer but useful for DB)
  const meta = {};
  if (preset.material) meta.material = preset.material;
  if (preset.color) meta.color = preset.color;
  if (preset.finish) meta.finish = preset.finish;
  if (preset.pricePerSqFt) meta.pricePerSqFt = preset.pricePerSqFt;
  if (preset.retailer) meta.retailer = preset.retailer;
  if (preset.productUrl) meta.productUrl = preset.productUrl;
  if (preset.imageUrl) meta.imageUrl = preset.imageUrl;

  return { entry, meta, barcode: preset.barcode };
}

async function processUrl(url) {
  try {
    const pageText = await fetchPageContent(url);
    const specs = await extractTileSpecs(pageText, url);

    if (specs.error) {
      console.error(`Extraction failed: ${specs.error}`);
      return null;
    }

    specs.productUrl = url;

    const validation = validatePreset(specs);
    const formatted = formatPresetForLayIt(specs);

    console.log('\n--- Extracted Tile ---');
    console.log(`Brand: ${specs.brand}`);
    console.log(`Name: ${specs.name}`);
    console.log(`Barcode: ${specs.barcode}`);
    console.log(`Shape: ${specs.shape}${specs.subShape ? ' / ' + specs.subShape : ''}`);
    console.log(`Dimensions: ${specs.nomW}" x ${specs.nomH}"`);
    if (specs.subW) console.log(`Sub-tile: ${specs.subW}" x ${specs.subH}"`);
    console.log(`Valid: ${validation.valid} (confidence: ${validation.confidence})`);
    if (!validation.valid) console.log(`Issues: ${validation.errors.join(', ')}`);
    console.log('');

    return {
      specs,
      formatted,
      validation,
    };

  } catch (err) {
    console.error(`Error processing ${url}: ${err.message}`);
    return null;
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('LayIt Tile Scraper');
    console.log('');
    console.log('Usage:');
    console.log('  node scrape.js <product-url>           Scrape a single product page');
    console.log('  node scrape.js --batch urls.txt        Scrape multiple URLs from a file');
    console.log('');
    console.log('Environment:');
    console.log('  ANTHROPIC_API_KEY=sk-...               Required for Claude API calls');
    console.log('');
    console.log('Output:');
    console.log('  Results are saved to ./output/ as JSON files');
    process.exit(0);
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable is required');
    console.error('');
    console.error('Get your key:');
    console.error('  1. Go to console.anthropic.com');
    console.error('  2. Sign up or log in');
    console.error('  3. Click "API Keys" → "Create Key"');
    console.error('  4. Copy the key and run:');
    console.error('');
    console.error('  export ANTHROPIC_API_KEY=sk-ant-your-key-here');
    console.error('');
    console.error('Cost: ~$0.01-0.02 per tile extraction');
    process.exit(1);
  }

  // Ensure output directory exists
  const outputDir = new URL('./output/', import.meta.url).pathname;
  if (!existsSync(outputDir)) mkdirSync(outputDir, { recursive: true });

  let urls = [];

  if (args[0] === '--batch' && args[1]) {
    const content = readFileSync(args[1], 'utf-8');
    urls = content.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
  } else {
    urls = args.filter(a => a.startsWith('http'));
  }

  if (urls.length === 0) {
    console.error('No URLs provided');
    process.exit(1);
  }

  console.log(`Processing ${urls.length} URL(s)...\n`);

  const results = [];

  for (const url of urls) {
    const result = await processUrl(url);
    if (result) {
      results.push(result);

      // Save individual result
      const filename = result.formatted.barcode || `unknown_${Date.now()}`;
      const filepath = `${outputDir}${filename}.json`;
      writeFileSync(filepath, JSON.stringify(result, null, 2));
      console.log(`Saved: ${filepath}\n`);
    }

    // Rate limit: wait 2s between requests
    if (urls.indexOf(url) < urls.length - 1) {
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  // Save combined results
  if (results.length > 0) {
    const allPresets = {};
    for (const r of results) {
      if (r.formatted.barcode) {
        allPresets[r.formatted.barcode] = r.formatted.entry;
      }
    }

    const combinedPath = `${outputDir}all_presets.json`;
    writeFileSync(combinedPath, JSON.stringify(allPresets, null, 2));
    console.log(`\nCombined presets saved to: ${combinedPath}`);
    console.log(`Total: ${results.length} tiles extracted, ${Object.keys(allPresets).length} with barcodes`);
  }

  // Close browser
  if (browser) await browser.close();
}

main();
