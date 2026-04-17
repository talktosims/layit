/**
 * LayIt Manufacturer Tile Scraper
 *
 * Scrapes tile product data directly from manufacturer websites (not big box
 * retailers). Uses Puppeteer with stealth mode + Claude API for structured
 * spec extraction from manufacturer-specific page layouts.
 *
 * Supported manufacturers:
 *   daltile.com, msisurfaces.com, marazziusa.com, americanolean.com,
 *   bedrosians.com, emser.com, crossvilleinc.com
 *
 * Usage:
 *   node scrape-manufacturers.js <product-url>
 *   node scrape-manufacturers.js --batch urls.txt
 *   node scrape-manufacturers.js --catalog <catalog-page-url>
 *   node scrape-manufacturers.js --catalog <catalog-url> --max 20
 *   node scrape-manufacturers.js --catalog <catalog-url> --mosaic-only
 *
 * Environment:
 *   ANTHROPIC_API_KEY=sk-...    Required for Claude API calls
 *
 * Output:
 *   Results saved to ./output/manufacturers/ as individual JSON + combined file
 */

import Anthropic from '@anthropic-ai/sdk';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

puppeteer.use(StealthPlugin());

// ---------------------------------------------------------------------------
// .env loader (no external dependency)
// ---------------------------------------------------------------------------
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

// ---------------------------------------------------------------------------
// Manufacturer registry — domain detection + page-specific navigation
// ---------------------------------------------------------------------------
const MANUFACTURERS = {
  'daltile.com': {
    brand: 'Daltile',
    tabSelectors: [
      'Technical Information',
      'Specifications',
      'Product Details',
      'Features & Specs',
    ],
    specsSelectors: [
      '.tech-info-table',
      '.product-specs',
      '.specifications-table',
      '[data-section="specifications"]',
      '.pdp-specifications',
    ],
    catalogPaths: [
      '/products/mosaic',
      '/products/ceramic-and-porcelain-tile',
      '/collections',
    ],
    productLinkSelector: 'a[href*="/product/"], a[href*="/tile/"], .product-card a',
  },
  'msisurfaces.com': {
    brand: 'MSI',
    tabSelectors: [
      'Specifications',
      'Product Details',
      'Technical Details',
    ],
    specsSelectors: [
      '.product-specifications',
      '.specs-table',
      '.product-details-table',
      '[class*="specification"]',
      '.pdp-specs',
    ],
    catalogPaths: [
      '/mosaics',
      '/porcelain-tile',
      '/ceramic-tile',
    ],
    productLinkSelector: 'a[href*="/product-detail/"], .product-tile a, .product-card a',
  },
  'marazziusa.com': {
    brand: 'Marazzi',
    tabSelectors: [
      'Product Details',
      'Specifications',
      'Technical Info',
    ],
    specsSelectors: [
      '.product-specs',
      '.product-details',
      '[class*="spec"]',
      '.tab-content table',
    ],
    catalogPaths: [
      '/products/mosaic',
      '/products/tile',
    ],
    productLinkSelector: 'a[href*="/product/"], .product-card a, .tile-item a',
  },
  'americanolean.com': {
    brand: 'American Olean',
    tabSelectors: [
      'Technical Information',
      'Specifications',
      'Product Details',
    ],
    specsSelectors: [
      '.tech-info-table',
      '.product-specs',
      '.specifications-table',
      '[data-section="specifications"]',
    ],
    catalogPaths: [
      '/products/mosaics',
      '/products/ceramic-and-porcelain',
    ],
    productLinkSelector: 'a[href*="/product/"], a[href*="/tile/"], .product-card a',
  },
  'bedrosians.com': {
    brand: 'Bedrosians',
    tabSelectors: [
      'Specifications',
      'Details',
      'Product Info',
    ],
    specsSelectors: [
      '.product-specifications',
      '.product-detail__specs',
      '[class*="specifications"]',
      '.accordion-content table',
    ],
    catalogPaths: [
      '/tile/mosaics',
      '/tile',
    ],
    productLinkSelector: 'a[href*="/tile/"], .product-card a, .product-tile a',
  },
  'emser.com': {
    brand: 'Emser',
    tabSelectors: [
      'Specifications',
      'Technical Details',
      'Product Specs',
    ],
    specsSelectors: [
      '.product-specs',
      '.specifications',
      '[class*="spec"]',
      '.product-detail table',
    ],
    catalogPaths: [
      '/tile/mosaics',
      '/tile',
    ],
    productLinkSelector: 'a[href*="/tile/"], .product-card a',
  },
  'crossvilleinc.com': {
    brand: 'Crossville',
    tabSelectors: [
      'Specifications',
      'Technical Data',
      'Details',
    ],
    specsSelectors: [
      '.product-specifications',
      '.specs-section',
      '[class*="specification"]',
      '.product-info table',
    ],
    catalogPaths: [
      '/products/mosaics',
      '/products',
    ],
    productLinkSelector: 'a[href*="/product/"], a[href*="/products/"], .product-card a',
  },
};

// ---------------------------------------------------------------------------
// Detect manufacturer from URL
// ---------------------------------------------------------------------------
function detectManufacturer(url) {
  const hostname = new URL(url).hostname.replace('www.', '');
  for (const [domain, config] of Object.entries(MANUFACTURERS)) {
    if (hostname.includes(domain.replace('www.', ''))) {
      return { domain, ...config };
    }
  }
  return null;
}

// ---------------------------------------------------------------------------
// Claude extraction prompt — enhanced for manufacturer sites
// ---------------------------------------------------------------------------
const EXTRACTION_PROMPT = `You are a tile specification extraction agent for the LayIt tile layout app.
You are reading a MANUFACTURER product page (not a retailer like Home Depot). Manufacturer pages often have more detailed technical specifications.

Given the text content of a product page, extract the following information and return it as a JSON object. Be precise — these values drive a rendering engine.

Required fields:
- identifiers: Extract ALL of these you can find:
  - barcode: UPC/EAN barcode number (string, 12-13 digits)
  - sku: Manufacturer SKU or item number (string)
  - modelNumber: Model number (string)
  If only one identifier is found, use it for barcode too.
- name: Product name (string)
- brand: Manufacturer/brand name (string)
- shape: Tile shape category. Must be one of: "rectangle", "square", "mosaic"
  - Use "mosaic" for any sheet-mounted tiles (hex, fishscale, penny, etc.)
  - Use "square" for individual square tiles (equal width/height)
  - Use "rectangle" for individual rectangular tiles (including subway)
  - IMPORTANT: If the page describes individual tiles sold in boxes (NOT mesh-mounted sheets), use "square" or "rectangle"

For shape "rectangle" or "square":
- nomW: Nominal width in inches (e.g., 12 for a "12x24" tile)
- nomH: Nominal height in inches
- actW: Actual width in inches (manufacturers often list actual/calibrated size)
- actH: Actual height in inches
- grout: Recommended grout joint width in inches (default 0.125 for 1/8")

For shape "mosaic":
- nomW: Nominal sheet width in inches (e.g., 12)
- nomH: Nominal sheet height in inches
- actW: Actual sheet width in inches (if listed, otherwise nominal - 0.25)
- actH: Actual sheet height in inches
- grout: Grout joint for sheet-to-sheet joints (default 0.125)
- subShape: Individual tile shape within the sheet. Must be one of:
  "hex", "square", "penny", "fishscale", "diamond", "rectangle", "octagon", "arabesque", "elongated_hex"
  - "hex" = regular hexagon (6 equal sides)
  - "penny" = small circles / penny rounds
  - "fishscale" = fan / scallop shaped
  - "diamond" = rhombus / diagonal squares
  - "arabesque" = lantern / Moorish shapes
  - "elongated_hex" = stretched hexagon (picket fence style)
  - "octagon" = octagon with small square dot fills
- subW: Individual sub-tile width in inches
- subH: Individual sub-tile height in inches
- subGr: Grout spacing between sub-tiles in inches (default 0.0625 for 1/16")
- orient: For hex/elongated_hex tiles — "pointy" (pointy-top) or "flat" (flat-top). Default "pointy".

TESSELLATION GEOMETRY RULES (apply these when calculating subH from subW):
- Pointy-top hex: subH = subW * 1.125 (standard ratio for regular hex with vertex up)
- Flat-top hex: subH = subW * 0.866 (√3/2 ratio)
- Penny round: subH = subW (circles)
- Fishscale: subH = subW * 0.9 (slightly shorter than wide)
- Diamond: subH = subW * 1.414 (45-degree rotated square, √2 ratio)
- Square: subH = subW
- If the manufacturer lists exact sub-tile dimensions, use those instead of calculating.

Additional fields (extract if available):
- material: "ceramic", "porcelain", "glass", "stone", "marble", "natural_stone", "travertine", etc.
- color: Primary color description
- finish: "matte", "glossy", "polished", "honed", "textured", "satin", etc.
- pricePerSqFt: Price per square foot if listed
- piecesPerBox: Number of pieces/sheets per box
- sqFtPerBox: Square footage per box
- productUrl: (will be provided separately)
- imageUrl: URL of the main product image
- series: Collection/series name if listed
- application: "floor", "wall", "floor/wall", etc.

IMPORTANT RULES:
1. All dimensions MUST be in inches. Convert from mm or cm if needed (1 inch = 25.4mm).
2. "Nominal" size is what's marketed (e.g., "2 inch hex"). "Actual" is the measured tile size.
3. For mosaic sheets, the sheet size is the overall mesh-backed sheet, NOT the individual tile size.
4. Common sheet sizes: 12"x12", 11"x11", 12"x13", 11.4"x10.9", 10"x12"
5. Common sub-tile sizes: 1" hex, 2" hex, 3" hex, 1" penny round, 2" fishscale
6. If you can't determine a value with confidence, use null rather than guessing.
7. At least one identifier (barcode, SKU, or model number) is critical.
8. Manufacturer pages may list dimensions in mm — always convert to inches.
9. Look for "Piece Size", "Chip Size", "Individual Tile Size" for sub-tile dimensions.
10. Look for "Sheet Size", "Mesh Size", "Mounted Size" for overall mosaic sheet dimensions.

Return ONLY a valid JSON object, no markdown formatting, no explanation.
If you cannot extract enough information to be useful, return: {"error": "reason"}`;

// ---------------------------------------------------------------------------
// Catalog link extraction prompt
// ---------------------------------------------------------------------------
const CATALOG_PROMPT = `You are analyzing a tile manufacturer's catalog/product listing page.

From the page content below, identify all individual PRODUCT links (not category links, not navigation links).
A product link leads to a single tile product page where you can see specifications.

Return a JSON array of objects, each with:
- url: The full product URL
- name: Product name if visible
- isMosaic: true/false — whether it appears to be a mosaic/sheet tile

Return ONLY the JSON array, no markdown formatting, no explanation.
If no product links are found, return: []`;

// ---------------------------------------------------------------------------
// Browser management
// ---------------------------------------------------------------------------
let browser = null;

async function launchBrowser() {
  if (!browser) {
    console.log('Launching headless Chrome (stealth mode)...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
      ],
    });
  }
  return browser;
}

async function closeBrowser() {
  if (browser) {
    await browser.close();
    browser = null;
  }
}

// ---------------------------------------------------------------------------
// Page fetching with manufacturer-specific navigation
// ---------------------------------------------------------------------------
async function fetchProductPage(url, manufacturer) {
  console.log(`  Fetching: ${url}`);
  const b = await launchBrowser();
  const page = await b.newPage();

  // Realistic browser fingerprint
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  );
  await page.setViewport({ width: 1440, height: 900 });

  // Block unnecessary resources to speed up loading
  await page.setRequestInterception(true);
  page.on('request', (req) => {
    const type = req.resourceType();
    if (['image', 'font', 'media', 'stylesheet'].includes(type)) {
      req.abort();
    } else {
      req.continue();
    }
  });

  try {
    // Navigate with generous timeout for slow manufacturer sites
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 45000 });

    // Wait for dynamic content
    await delay(2500);

    // Handle cookie consent / popups that many manufacturer sites show
    await dismissPopups(page);

    // Scroll to load lazy content
    await autoScroll(page);

    // Click manufacturer-specific spec tabs
    if (manufacturer) {
      await clickSpecTabs(page, manufacturer.tabSelectors);
      await delay(1500);
    }

    // Generic tab clicking for unknown manufacturers
    await clickGenericSpecTabs(page);
    await delay(1000);

    // Try expanding any collapsed sections
    await expandCollapsedSections(page);
    await delay(1000);

    // Extract text content
    const text = await page.evaluate(() => document.body.innerText);

    // Also try to extract structured spec tables
    const tables = await page.evaluate(() => {
      const results = [];
      const allTables = document.querySelectorAll('table');
      for (const table of allTables) {
        const rows = [];
        for (const row of table.querySelectorAll('tr')) {
          const cells = Array.from(row.querySelectorAll('td, th')).map(c => c.innerText.trim());
          if (cells.length >= 2) rows.push(cells.join(': '));
        }
        if (rows.length > 0) results.push(rows.join('\n'));
      }
      // Also grab definition lists (dl/dt/dd) which some manufacturers use
      const dls = document.querySelectorAll('dl');
      for (const dl of dls) {
        const items = [];
        const dts = dl.querySelectorAll('dt');
        const dds = dl.querySelectorAll('dd');
        for (let i = 0; i < dts.length; i++) {
          const label = dts[i]?.innerText?.trim();
          const value = dds[i]?.innerText?.trim();
          if (label && value) items.push(`${label}: ${value}`);
        }
        if (items.length > 0) results.push(items.join('\n'));
      }
      return results;
    });

    // Get main product image URL
    const imageUrl = await page.evaluate(() => {
      const selectors = [
        '.product-image img',
        '.pdp-image img',
        '.gallery-image img',
        '[class*="product"] img[src*="tile"]',
        '[class*="product"] img[src*="mosaic"]',
        'img[alt*="tile"]',
        'img[alt*="mosaic"]',
        '.main-image img',
        '#product-image img',
      ];
      for (const sel of selectors) {
        const img = document.querySelector(sel);
        if (img && img.src) return img.src;
      }
      // Fallback: largest image on page
      const imgs = Array.from(document.querySelectorAll('img'))
        .filter(i => i.naturalWidth > 200 && i.src && !i.src.includes('logo'));
      if (imgs.length > 0) {
        imgs.sort((a, b) => (b.naturalWidth * b.naturalHeight) - (a.naturalWidth * a.naturalHeight));
        return imgs[0].src;
      }
      return null;
    });

    await page.close();

    // Combine text + structured tables
    let combined = text;
    if (tables.length > 0) {
      combined += '\n\n--- STRUCTURED SPEC TABLES ---\n' + tables.join('\n---\n');
    }

    // Truncate to fit context window
    return {
      text: combined.slice(0, 40000),
      imageUrl,
    };

  } catch (err) {
    await page.close();
    throw err;
  }
}

// ---------------------------------------------------------------------------
// Catalog page scraping — find all product URLs
// ---------------------------------------------------------------------------
async function fetchCatalogLinks(url, manufacturer, options = {}) {
  console.log(`\nScraping catalog page: ${url}`);
  const b = await launchBrowser();
  const page = await b.newPage();

  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  );
  await page.setViewport({ width: 1440, height: 900 });

  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 45000 });
    await delay(3000);
    await dismissPopups(page);

    // Scroll to load all products (many sites use infinite scroll)
    let previousHeight = 0;
    let scrollAttempts = 0;
    const maxScrolls = options.maxScrolls || 10;

    while (scrollAttempts < maxScrolls) {
      const currentHeight = await page.evaluate(() => document.body.scrollHeight);
      if (currentHeight === previousHeight) break;
      previousHeight = currentHeight;
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await delay(2000);
      scrollAttempts++;

      // Click "Load More" / "Show More" buttons if present
      try {
        await page.evaluate(() => {
          const buttons = document.querySelectorAll('button, a');
          for (const btn of buttons) {
            const text = btn.textContent.toLowerCase().trim();
            if (text === 'load more' || text === 'show more' || text === 'view more' ||
                text === 'see more' || text === 'next page') {
              btn.click();
              break;
            }
          }
        });
      } catch (_) { /* ignore */ }
    }

    // Extract all product links
    const baseUrl = new URL(url).origin;
    const productSelector = manufacturer?.productLinkSelector || 'a[href*="product"], a[href*="tile"]';

    const links = await page.evaluate((sel, base) => {
      const anchors = document.querySelectorAll(sel);
      const seen = new Set();
      const results = [];
      for (const a of anchors) {
        let href = a.href;
        if (!href) continue;
        // Make absolute
        if (href.startsWith('/')) href = base + href;
        // Dedupe
        if (seen.has(href)) continue;
        seen.add(href);
        // Get surrounding text for context
        const name = a.textContent?.trim()?.slice(0, 100) || '';
        const parent = a.closest('.product-card, .product-tile, .product-item, li, article');
        const context = parent?.textContent?.trim()?.slice(0, 200) || name;
        results.push({ url: href, name, context });
      }
      return results;
    }, productSelector, baseUrl);

    await page.close();

    // Also get page text for Claude to analyze if direct selectors found nothing
    if (links.length === 0) {
      console.log('  No links found via selectors, using Claude to analyze page...');
      const page2 = await b.newPage();
      await page2.goto(url, { waitUntil: 'networkidle2', timeout: 45000 });
      const pageText = await page2.evaluate(() => document.body.innerText);

      // Also grab all links for Claude to analyze
      const allLinks = await page2.evaluate((base) => {
        return Array.from(document.querySelectorAll('a[href]')).map(a => {
          let href = a.href;
          if (href.startsWith('/')) href = base + href;
          return { url: href, text: a.textContent?.trim()?.slice(0, 80) || '' };
        }).filter(l => l.url.includes(base));
      }, baseUrl);

      await page2.close();

      const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4000,
        messages: [{
          role: 'user',
          content: `${CATALOG_PROMPT}\n\nBase URL: ${baseUrl}\n\nAll links on page:\n${JSON.stringify(allLinks.slice(0, 200), null, 1)}\n\nPage content:\n${pageText.slice(0, 20000)}`,
        }],
      });

      const text = response.content[0].text.trim();
      try {
        const parsed = JSON.parse(text.match(/\[[\s\S]*\]/)?.[0] || '[]');
        return parsed;
      } catch (_) {
        return [];
      }
    }

    // Filter for mosaic-only if requested
    if (options.mosaicOnly) {
      const mosaicKeywords = ['mosaic', 'hex', 'penny', 'fishscale', 'arabesque',
        'lantern', 'picket', 'diamond', 'octagon', 'sheet', 'mesh'];
      return links.filter(l => {
        const combined = (l.name + ' ' + l.context).toLowerCase();
        return mosaicKeywords.some(kw => combined.includes(kw));
      });
    }

    return links;

  } catch (err) {
    console.error(`  Error fetching catalog: ${err.message}`);
    return [];
  }
}

// ---------------------------------------------------------------------------
// Page interaction helpers
// ---------------------------------------------------------------------------
async function delay(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function dismissPopups(page) {
  try {
    await page.evaluate(() => {
      // Common cookie/popup dismiss patterns
      const dismissTexts = ['accept', 'got it', 'close', 'dismiss', 'no thanks',
        'i agree', 'accept all', 'accept cookies', 'allow all'];
      const buttons = document.querySelectorAll('button, a, [role="button"]');
      for (const btn of buttons) {
        const text = btn.textContent?.toLowerCase()?.trim();
        if (text && dismissTexts.some(dt => text.includes(dt))) {
          const rect = btn.getBoundingClientRect();
          // Only click if it looks like a popup button (small, near edges or center)
          if (rect.width < 300 && rect.height < 80) {
            btn.click();
            break;
          }
        }
      }
      // Close any overlay modals
      const overlays = document.querySelectorAll('[class*="modal"] [class*="close"], [class*="overlay"] [class*="close"], .close-button, .modal-close');
      for (const close of overlays) {
        close.click();
      }
    });
  } catch (_) { /* ignore */ }
}

async function autoScroll(page) {
  await page.evaluate(async () => {
    const distance = 400;
    const maxScrolls = 15;
    let scrolled = 0;
    while (scrolled < maxScrolls) {
      window.scrollBy(0, distance);
      await new Promise(r => setTimeout(r, 300));
      scrolled++;
    }
    // Scroll back to top
    window.scrollTo(0, 0);
  });
}

async function clickSpecTabs(page, tabNames) {
  if (!tabNames || tabNames.length === 0) return;

  try {
    await page.evaluate((names) => {
      const clickTargets = document.querySelectorAll(
        'button, a, [role="tab"], .tab, [class*="tab"], [class*="accordion"], summary, [data-toggle]'
      );
      for (const el of clickTargets) {
        const text = el.textContent?.trim()?.toLowerCase();
        if (!text) continue;
        for (const name of names) {
          if (text.includes(name.toLowerCase())) {
            el.click();
            return;
          }
        }
      }
    }, tabNames);
  } catch (_) { /* ignore */ }
}

async function clickGenericSpecTabs(page) {
  const genericNames = [
    'specifications', 'specs', 'technical', 'details', 'product details',
    'product info', 'product information', 'features', 'dimensions',
    'tech info', 'technical information', 'technical data',
  ];
  await clickSpecTabs(page, genericNames);
}

async function expandCollapsedSections(page) {
  try {
    await page.evaluate(() => {
      // Click all collapsed accordions
      const accordions = document.querySelectorAll(
        '[class*="accordion"]:not([class*="open"]):not([class*="active"]):not([class*="expanded"]),' +
        'details:not([open]),' +
        '[aria-expanded="false"],' +
        '[class*="collapse"]:not([class*="show"])'
      );
      for (const acc of accordions) {
        if (acc.tagName === 'DETAILS') {
          acc.setAttribute('open', '');
        } else {
          acc.click();
        }
      }
      // Click "Show More" / "Read More" within product details
      const moreButtons = document.querySelectorAll('[class*="more"], [class*="expand"]');
      for (const btn of moreButtons) {
        const text = btn.textContent?.toLowerCase()?.trim();
        if (text && (text.includes('show more') || text.includes('read more') ||
            text.includes('view more') || text === 'more' || text === '+')) {
          btn.click();
        }
      }
    });
  } catch (_) { /* ignore */ }
}

// ---------------------------------------------------------------------------
// Claude spec extraction
// ---------------------------------------------------------------------------
async function extractTileSpecs(pageText, url, manufacturer) {
  console.log('  Sending to Claude for extraction...');

  const manufacturerHint = manufacturer
    ? `\n\nThis is a ${manufacturer.brand} product page. Look for their specific spec format.`
    : '';

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 3000,
    messages: [{
      role: 'user',
      content: `${EXTRACTION_PROMPT}${manufacturerHint}\n\nProduct page URL: ${url}\n\nPage content:\n${pageText}`,
    }],
  });

  const text = response.content[0].text.trim();

  try {
    return JSON.parse(text);
  } catch (_) {
    const match = text.match(/\{[\s\S]*\}/);
    if (match) return JSON.parse(match[0]);
    throw new Error(`Failed to parse Claude response: ${text.slice(0, 300)}`);
  }
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------
function validatePreset(preset) {
  const errors = [];
  const warnings = [];

  // Must have at least one identifier
  const hasId = preset.barcode || preset.sku || preset.modelNumber;
  if (!hasId) errors.push('No identifier found (barcode, SKU, or model number)');
  if (!preset.name) errors.push('Missing product name');
  if (!preset.brand) errors.push('Missing brand');
  if (!preset.shape) errors.push('Missing shape');
  if (!preset.nomW || !preset.nomH) errors.push('Missing nominal dimensions');

  if (preset.shape === 'mosaic') {
    if (!preset.subShape) errors.push('Missing sub-tile shape (subShape)');
    if (!preset.subW || !preset.subH) errors.push('Missing sub-tile dimensions');
    if (preset.subShape === 'hex' && !preset.orient) warnings.push('Missing hex orientation, defaulting to pointy');
  }

  // Sanity checks
  if (preset.nomW && (preset.nomW < 0.5 || preset.nomW > 48)) warnings.push(`Unusual nomW: ${preset.nomW}"`);
  if (preset.nomH && (preset.nomH < 0.5 || preset.nomH > 48)) warnings.push(`Unusual nomH: ${preset.nomH}"`);
  if (preset.subW && preset.subW > preset.nomW) warnings.push('subW larger than nomW');
  if (preset.actW && preset.actW > preset.nomW + 1) warnings.push('actW significantly larger than nomW');

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    confidence: errors.length === 0
      ? (warnings.length === 0 ? 0.95 : 0.8)
      : Math.max(0.1, 0.7 - errors.length * 0.15),
  };
}

// ---------------------------------------------------------------------------
// Format for LayIt master_presets.json
// ---------------------------------------------------------------------------
function formatPresetForLayIt(specs) {
  // Determine the best identifier to use as the key
  const key = specs.barcode || specs.sku || specs.modelNumber || `unknown_${Date.now()}`;

  // Build display name
  let displayName = specs.name || 'Unknown Tile';
  if (specs.shape === 'mosaic' && specs.nomW && specs.nomH) {
    // Add sheet dimensions to name if not already there
    const dimStr = `${specs.nomW}x${specs.nomH}`;
    if (!displayName.includes(dimStr) && !displayName.includes(`${specs.nomW}"`) &&
        !displayName.includes(`${specs.nomH}"`)) {
      displayName += ` (${specs.nomW}x${specs.nomH})`;
    }
  }

  const entry = {
    name: displayName,
    brand: specs.brand || 'Unknown',
    shape: specs.shape,
    nomW: specs.nomW,
    nomH: specs.nomH,
    actW: specs.actW || (specs.nomW ? specs.nomW - 0.25 : null),
    actH: specs.actH || (specs.nomH ? specs.nomH - 0.25 : null),
    grout: specs.grout || 0.125,
  };

  // Mosaic sub-tile fields
  if (specs.shape === 'mosaic') {
    entry.subShape = specs.subShape;
    entry.subW = specs.subW;
    entry.subH = specs.subH;
    entry.subGr = specs.subGr || 0.0625;
    if (specs.subShape === 'hex' || specs.subShape === 'elongated_hex') {
      entry.orient = specs.orient || 'pointy';
    }
  }

  // Metadata fields
  if (specs.material) entry.material = specs.material;
  if (specs.color) entry.color = specs.color;
  if (specs.finish) entry.finish = specs.finish;
  entry.retailer = 'Manufacturer Direct';
  entry.source = 'manufacturer';

  // Extended metadata (stored separately for reference)
  const meta = {};
  if (specs.sku) meta.sku = specs.sku;
  if (specs.modelNumber) meta.modelNumber = specs.modelNumber;
  if (specs.barcode && specs.barcode !== key) meta.barcode = specs.barcode;
  if (specs.pricePerSqFt) meta.pricePerSqFt = specs.pricePerSqFt;
  if (specs.piecesPerBox) meta.piecesPerBox = specs.piecesPerBox;
  if (specs.sqFtPerBox) meta.sqFtPerBox = specs.sqFtPerBox;
  if (specs.productUrl) meta.productUrl = specs.productUrl;
  if (specs.imageUrl) meta.imageUrl = specs.imageUrl;
  if (specs.series) meta.series = specs.series;
  if (specs.application) meta.application = specs.application;

  return { key, entry, meta };
}

// ---------------------------------------------------------------------------
// Process a single product URL
// ---------------------------------------------------------------------------
async function processProductUrl(url) {
  const manufacturer = detectManufacturer(url);
  const brandLabel = manufacturer?.brand || 'Unknown manufacturer';

  console.log(`\n[${brandLabel}] Processing product page...`);

  try {
    const { text: pageText, imageUrl } = await fetchProductPage(url, manufacturer);

    if (pageText.length < 100) {
      console.error('  Page content too short — may be blocked or empty');
      return null;
    }

    const specs = await extractTileSpecs(pageText, url, manufacturer);

    if (specs.error) {
      console.error(`  Extraction failed: ${specs.error}`);
      return null;
    }

    // Add URL and image
    specs.productUrl = url;
    if (imageUrl && !specs.imageUrl) specs.imageUrl = imageUrl;

    // Override brand if we know the manufacturer
    if (manufacturer && !specs.brand) specs.brand = manufacturer.brand;

    const validation = validatePreset(specs);
    const formatted = formatPresetForLayIt(specs);

    // Log results
    console.log(`  Brand: ${specs.brand}`);
    console.log(`  Name: ${specs.name}`);
    console.log(`  ID: ${formatted.key} (${specs.barcode ? 'UPC' : specs.sku ? 'SKU' : 'Model#'})`);
    console.log(`  Shape: ${specs.shape}${specs.subShape ? ' / ' + specs.subShape : ''}`);
    console.log(`  Sheet: ${specs.nomW}" x ${specs.nomH}"`);
    if (specs.subW) console.log(`  Sub-tile: ${specs.subW}" x ${specs.subH}"`);
    if (specs.material) console.log(`  Material: ${specs.material}`);
    console.log(`  Valid: ${validation.valid} (confidence: ${validation.confidence})`);
    if (validation.errors.length > 0) console.log(`  Errors: ${validation.errors.join(', ')}`);
    if (validation.warnings.length > 0) console.log(`  Warnings: ${validation.warnings.join(', ')}`);

    return { specs, formatted, validation };

  } catch (err) {
    console.error(`  Error: ${err.message}`);
    return null;
  }
}

// ---------------------------------------------------------------------------
// Save results
// ---------------------------------------------------------------------------
function ensureOutputDir() {
  const outputDir = join(__dirname, 'output', 'manufacturers');
  if (!existsSync(outputDir)) mkdirSync(outputDir, { recursive: true });
  return outputDir;
}

function saveResult(result, outputDir) {
  const filename = `${result.formatted.key}.json`;
  const filepath = join(outputDir, filename);
  writeFileSync(filepath, JSON.stringify(result, null, 2));
  console.log(`  Saved: ${filepath}`);
  return filepath;
}

function saveCombined(results, outputDir) {
  const presets = {};
  const meta = {};

  for (const r of results) {
    presets[r.formatted.key] = r.formatted.entry;
    if (Object.keys(r.formatted.meta).length > 0) {
      meta[r.formatted.key] = r.formatted.meta;
    }
  }

  // Save preset file (can be merged into master_presets.json)
  const presetsPath = join(outputDir, 'scraped_presets.json');
  writeFileSync(presetsPath, JSON.stringify(presets, null, 2));

  // Save metadata file
  const metaPath = join(outputDir, 'scraped_meta.json');
  writeFileSync(metaPath, JSON.stringify(meta, null, 2));

  // Save a merge-ready file that combines both
  const fullPath = join(outputDir, 'scraped_full.json');
  const full = {};
  for (const [key, entry] of Object.entries(presets)) {
    full[key] = { ...entry, ...(meta[key] || {}) };
  }
  writeFileSync(fullPath, JSON.stringify(full, null, 2));

  return { presetsPath, metaPath, fullPath };
}

// ---------------------------------------------------------------------------
// Merge into master_presets.json
// ---------------------------------------------------------------------------
function mergeIntoMaster(results) {
  const masterPath = join(__dirname, 'output', 'master_presets.json');
  let master = {};

  if (existsSync(masterPath)) {
    try {
      master = JSON.parse(readFileSync(masterPath, 'utf-8'));
    } catch (_) {
      console.warn('  Warning: Could not parse existing master_presets.json, starting fresh');
    }
  }

  let added = 0;
  let updated = 0;

  for (const r of results) {
    const key = r.formatted.key;
    if (key.startsWith('unknown_')) continue; // Skip entries with no real identifier

    if (master[key]) {
      updated++;
    } else {
      added++;
    }
    master[key] = r.formatted.entry;
  }

  // Update meta
  if (master._meta) {
    master._meta.lastUpdated = new Date().toISOString().split('T')[0];
    master._meta.totalPresets = Object.keys(master).filter(k => k !== '_meta').length;
  }

  writeFileSync(masterPath, JSON.stringify(master, null, 2));
  console.log(`\nMaster presets updated: ${added} added, ${updated} updated`);
  console.log(`  Total presets: ${Object.keys(master).filter(k => k !== '_meta').length}`);
  console.log(`  File: ${masterPath}`);
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
function printUsage() {
  console.log('LayIt Manufacturer Tile Scraper');
  console.log('');
  console.log('Usage:');
  console.log('  node scrape-manufacturers.js <product-url>');
  console.log('  node scrape-manufacturers.js <url1> <url2> ...');
  console.log('  node scrape-manufacturers.js --batch urls.txt');
  console.log('  node scrape-manufacturers.js --catalog <catalog-page-url>');
  console.log('');
  console.log('Options:');
  console.log('  --batch <file>       Process URLs from a text file (one per line)');
  console.log('  --catalog <url>      Scrape a catalog page for product links, then process each');
  console.log('  --max <n>            Maximum number of products to process (default: unlimited)');
  console.log('  --mosaic-only        In catalog mode, only scrape mosaic/sheet tiles');
  console.log('  --merge              Merge results into master_presets.json');
  console.log('  --delay <ms>         Delay between requests in ms (default: 3000)');
  console.log('  --help               Show this help message');
  console.log('');
  console.log('Supported manufacturers:');
  for (const [domain, config] of Object.entries(MANUFACTURERS)) {
    console.log(`  ${config.brand.padEnd(18)} ${domain}`);
  }
  console.log('  (Other sites are attempted with generic extraction)');
  console.log('');
  console.log('Environment:');
  console.log('  ANTHROPIC_API_KEY    Required for Claude API calls (~$0.01-0.03 per extraction)');
  console.log('');
  console.log('Examples:');
  console.log('  node scrape-manufacturers.js https://www.daltile.com/product/some-tile');
  console.log('  node scrape-manufacturers.js --catalog https://www.msisurfaces.com/mosaics --mosaic-only --max 10');
  console.log('  node scrape-manufacturers.js --batch manufacturer-urls.txt --merge');
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help')) {
    printUsage();
    process.exit(0);
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable is required');
    console.error('Set it in .env or run: export ANTHROPIC_API_KEY=sk-ant-...');
    process.exit(1);
  }

  // Parse options
  const options = {
    merge: args.includes('--merge'),
    mosaicOnly: args.includes('--mosaic-only'),
    max: Infinity,
    delayMs: 3000,
  };

  const maxIdx = args.indexOf('--max');
  if (maxIdx !== -1 && args[maxIdx + 1]) {
    options.max = parseInt(args[maxIdx + 1], 10);
  }

  const delayIdx = args.indexOf('--delay');
  if (delayIdx !== -1 && args[delayIdx + 1]) {
    options.delayMs = parseInt(args[delayIdx + 1], 10);
  }

  const outputDir = ensureOutputDir();
  let urls = [];

  // Mode: catalog
  const catalogIdx = args.indexOf('--catalog');
  if (catalogIdx !== -1 && args[catalogIdx + 1]) {
    const catalogUrl = args[catalogIdx + 1];
    const manufacturer = detectManufacturer(catalogUrl);

    const links = await fetchCatalogLinks(catalogUrl, manufacturer, {
      mosaicOnly: options.mosaicOnly,
    });

    if (links.length === 0) {
      console.error('\nNo product links found on catalog page.');
      console.error('Try providing individual product URLs instead.');
      await closeBrowser();
      process.exit(1);
    }

    console.log(`\nFound ${links.length} product links`);
    const limitedLinks = links.slice(0, options.max);
    if (limitedLinks.length < links.length) {
      console.log(`Processing first ${limitedLinks.length} (--max ${options.max})`);
    }

    urls = limitedLinks.map(l => l.url);
  }

  // Mode: batch file
  const batchIdx = args.indexOf('--batch');
  if (batchIdx !== -1 && args[batchIdx + 1]) {
    const batchFile = args[batchIdx + 1];
    if (!existsSync(batchFile)) {
      console.error(`Batch file not found: ${batchFile}`);
      process.exit(1);
    }
    const content = readFileSync(batchFile, 'utf-8');
    const batchUrls = content.split('\n')
      .map(l => l.trim())
      .filter(l => l && !l.startsWith('#') && l.startsWith('http'));
    urls.push(...batchUrls);
  }

  // Mode: direct URLs
  const directUrls = args.filter(a => a.startsWith('http'));
  urls.push(...directUrls);

  // Dedupe
  urls = [...new Set(urls)];

  if (urls.length === 0) {
    console.error('No URLs to process.');
    printUsage();
    process.exit(1);
  }

  // Apply max limit
  if (urls.length > options.max) {
    urls = urls.slice(0, options.max);
  }

  console.log(`\nProcessing ${urls.length} product URL(s)...\n`);
  console.log('─'.repeat(60));

  const results = [];
  let processed = 0;
  let succeeded = 0;
  let failed = 0;

  for (const url of urls) {
    processed++;
    console.log(`\n[${processed}/${urls.length}] ─────────────────────────────`);

    const result = await processProductUrl(url);

    if (result) {
      results.push(result);
      saveResult(result, outputDir);
      succeeded++;
    } else {
      failed++;
    }

    // Rate limit between requests
    if (processed < urls.length) {
      console.log(`\n  Waiting ${options.delayMs / 1000}s before next request...`);
      await delay(options.delayMs);
    }
  }

  // Save combined results
  console.log('\n' + '═'.repeat(60));
  console.log('RESULTS SUMMARY');
  console.log('═'.repeat(60));
  console.log(`  Processed: ${processed}`);
  console.log(`  Succeeded: ${succeeded}`);
  console.log(`  Failed:    ${failed}`);

  if (results.length > 0) {
    const { presetsPath, fullPath } = saveCombined(results, outputDir);
    console.log(`\n  Presets: ${presetsPath}`);
    console.log(`  Full:    ${fullPath}`);

    // Merge into master if requested
    if (options.merge) {
      mergeIntoMaster(results);
    }

    // Show all extracted tiles in a table
    console.log('\nExtracted tiles:');
    console.log('─'.repeat(80));
    console.log(
      'ID'.padEnd(18) +
      'Brand'.padEnd(16) +
      'Shape'.padEnd(10) +
      'Sub'.padEnd(12) +
      'Size'.padEnd(12) +
      'Conf.'
    );
    console.log('─'.repeat(80));
    for (const r of results) {
      const f = r.formatted;
      console.log(
        f.key.slice(0, 16).padEnd(18) +
        (f.entry.brand || '').slice(0, 14).padEnd(16) +
        (f.entry.shape || '').padEnd(10) +
        (f.entry.subShape || '-').padEnd(12) +
        `${f.entry.nomW}x${f.entry.nomH}`.padEnd(12) +
        r.validation.confidence.toFixed(2)
      );
    }
    console.log('─'.repeat(80));
  } else {
    console.log('\n  No tiles were successfully extracted.');
  }

  await closeBrowser();
  console.log('\nDone.');
}

main().catch(err => {
  console.error(`\nFatal error: ${err.message}`);
  closeBrowser().then(() => process.exit(1));
});
