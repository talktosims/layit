#!/usr/bin/env node
/**
 * Scrape real UPC barcodes from upcitemdb.com for tile products.
 * Uses Puppeteer to search by product name and extract UPC numbers.
 *
 * Usage:
 *   node scrape-upcs.js
 */

import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

puppeteer.use(StealthPlugin());

const __dirname = dirname(fileURLToPath(import.meta.url));

// Products to search for — name, brand, expected shape
const PRODUCTS = [
  { brand: 'Daltile', query: 'Daltile Keystones 2 hex mosaic', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'Daltile', query: 'Daltile Keystones 1 hex mosaic', shape: 'mosaic', subShape: 'hex', subW: 1, subH: 1.125 },
  { brand: 'Daltile', query: 'Daltile Restore penny round mosaic', shape: 'mosaic', subShape: 'penny', subW: 0.75, subH: 0.75 },
  { brand: 'Daltile', query: 'Daltile octagon dot mosaic tile', shape: 'mosaic', subShape: 'octdot', subW: 2, subH: 2 },
  { brand: 'Daltile', query: 'Daltile Color Wheel hex mosaic', shape: 'mosaic', subShape: 'hex', subW: 1.5, subH: 1.6875 },
  { brand: 'Daltile', query: 'Daltile 12x24 porcelain tile', shape: 'rectangle', nomW: 12, nomH: 24 },
  { brand: 'MSI', query: 'MSI white hexagon mosaic tile', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'MSI', query: 'MSI Carrara hexagon mosaic marble', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'MSI', query: 'MSI penny round mosaic tile', shape: 'mosaic', subShape: 'penny', subW: 0.75, subH: 0.75 },
  { brand: 'MSI', query: 'MSI 3x6 white subway tile', shape: 'rectangle', nomW: 3, nomH: 6 },
  { brand: 'Merola', query: 'Merola Metro 2 hex matte white porcelain', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'Merola', query: 'Merola Metro 2 hex matte black', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'Merola', query: 'Merola Metro 1 hex mosaic', shape: 'mosaic', subShape: 'hex', subW: 1, subH: 1.125 },
  { brand: 'Merola', query: 'Merola Hudson penny round mosaic', shape: 'mosaic', subShape: 'penny', subW: 0.8, subH: 0.8 },
  { brand: 'Merola', query: 'Merola fish scale mosaic tile', shape: 'mosaic', subShape: 'fishscale', subW: 2, subH: 2.25 },
  { brand: 'Marazzi', query: 'Marazzi 12x24 porcelain floor tile', shape: 'rectangle', nomW: 12, nomH: 24 },
  { brand: 'Jeffrey Court', query: 'Jeffrey Court hex mosaic tile', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'Jeffrey Court', query: 'Jeffrey Court penny round mosaic', shape: 'mosaic', subShape: 'penny', subW: 0.75, subH: 0.75 },
  { brand: 'American Olean', query: 'American Olean penny round mosaic', shape: 'mosaic', subShape: 'penny', subW: 0.75, subH: 0.75 },
  { brand: 'American Olean', query: 'American Olean hex mosaic tile', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
  { brand: 'Florida Tile', query: 'Florida Tile subway 3x12', shape: 'rectangle', nomW: 3, nomH: 12 },
  { brand: 'Ceramiche Piemme', query: 'Ceramiche Piemme porcelain tile', shape: 'hexagon' },
  { brand: 'Apollo Tile', query: 'Apollo Tile fishscale fan mosaic', shape: 'mosaic', subShape: 'fishscale', subW: 2, subH: 2.25 },
  { brand: 'Bedrosians', query: 'Bedrosians hex mosaic tile', shape: 'mosaic', subShape: 'hex', subW: 2, subH: 2.25 },
];

async function searchUPC(browser, query) {
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');

  const results = [];

  try {
    // Try upcitemdb.com
    const searchUrl = `https://www.upcitemdb.com/query?s=${encodeURIComponent(query)}&type=2`;
    await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 15000 });
    await new Promise(r => setTimeout(r, 1500));

    // Extract UPC results
    const items = await page.evaluate(() => {
      const results = [];
      const rows = document.querySelectorAll('.rTable .rTableRow');
      rows.forEach(row => {
        const upcEl = row.querySelector('.rTableCell:first-child a');
        const nameEl = row.querySelector('.rTableCell:nth-child(2)');
        if (upcEl && nameEl) {
          const upc = upcEl.textContent.trim();
          const name = nameEl.textContent.trim();
          if (/^\d{12,13}$/.test(upc)) {
            results.push({ upc, name });
          }
        }
      });
      // Also try list items
      if (results.length === 0) {
        document.querySelectorAll('a[href*="/upc/"]').forEach(a => {
          const upc = a.textContent.trim();
          const parent = a.closest('li, tr, div');
          const name = parent ? parent.textContent.replace(upc, '').trim().substring(0, 100) : '';
          if (/^\d{12,13}$/.test(upc)) {
            results.push({ upc, name });
          }
        });
      }
      return results;
    });

    results.push(...items);
  } catch (e) {
    console.log(`  Error searching upcitemdb: ${e.message}`);
  }

  // Also try barcodelookup.com
  try {
    const searchUrl2 = `https://www.barcodelookup.com/${encodeURIComponent(query)}`;
    await page.goto(searchUrl2, { waitUntil: 'networkidle2', timeout: 15000 });
    await new Promise(r => setTimeout(r, 1500));

    const items2 = await page.evaluate(() => {
      const results = [];
      document.querySelectorAll('.product-info, .product-row').forEach(el => {
        const upcEl = el.querySelector('.barcode, .upc');
        const nameEl = el.querySelector('.product-name, h4, h5');
        if (upcEl && nameEl) {
          const upc = upcEl.textContent.trim().replace(/[^0-9]/g, '');
          if (/^\d{12,13}$/.test(upc)) {
            results.push({ upc, name: nameEl.textContent.trim() });
          }
        }
      });
      return results;
    });

    results.push(...items2);
  } catch (e) {
    // barcodelookup may block, that's fine
  }

  await page.close();
  return results;
}

async function main() {
  console.log('\nLayIt UPC Barcode Scraper');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━\n');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const allResults = {};
  let found = 0;

  for (const product of PRODUCTS) {
    console.log(`Searching: ${product.query}`);
    const results = await searchUPC(browser, product.query);

    if (results.length > 0) {
      console.log(`  Found ${results.length} UPC(s):`);
      for (const r of results.slice(0, 3)) { // Max 3 per product
        console.log(`    ${r.upc} — ${r.name.substring(0, 60)}`);

        const entry = {
          name: r.name,
          brand: product.brand,
          shape: product.shape,
          grout: 0.125,
          source: 'upc-verified'
        };

        if (product.nomW) { entry.nomW = product.nomW; entry.nomH = product.nomH; }
        if (product.subShape) {
          entry.subShape = product.subShape;
          entry.subW = product.subW;
          entry.subH = product.subH;
          entry.subGr = 0.0625;
        }

        allResults[r.upc] = entry;
        found++;
      }
    } else {
      console.log(`  No UPCs found`);
    }

    // Rate limit
    await new Promise(r => setTimeout(r, 2000));
  }

  await browser.close();

  // Save results
  const outPath = join(__dirname, 'output', 'real_upc_barcodes.json');
  writeFileSync(outPath, JSON.stringify(allResults, null, 2));

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Found: ${found} UPCs`);
  console.log(`Saved: ${outPath}\n`);
}

main().catch(console.error);
