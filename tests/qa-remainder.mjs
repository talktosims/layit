/**
 * Offline checks for scan, purchase, share, mosaic pieces, cut fractions, and project roundtrip.
 * Firebase, paid AI, purchases, and client-report sending are blocked or not invoked.
 * Chrome file:// is not iOS/WKWebView.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = 'file://' + path.join(root, 'index.html');
const failures = [];
function check(name, cond, detail) {
  if (!cond) failures.push(name + (detail ? ': ' + detail : ''));
  else console.log('ok', name);
}

function expectFraction(inches) {
  if (!(inches > 0)) return '0"';
  let whole = Math.floor(inches + 1e-9);
  let rem = inches - whole;
  let sixteenths = Math.round(rem * 16);
  if (sixteenths === 16) { whole += 1; sixteenths = 0; }
  if (sixteenths === 0) return whole + '"';
  let num = sixteenths, den = 16;
  while (num % 2 === 0 && den % 2 === 0) { num /= 2; den /= 2; }
  const frac = num + '/' + den + '"';
  return whole === 0 ? frac : whole + '-' + frac;
}

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
});
const page = await browser.newPage();
const blocked = [];
await page.setRequestInterception(true);
page.on('request', (req) => {
  const url = req.url();
  if (/firebase|googleapis|gstatic|anthropic|openai|claude|identitytoolkit/i.test(url)) {
    blocked.push(url.split('?')[0]);
    req.abort();
  } else req.continue();
});
const dialogs = [];
page.on('dialog', (d) => { dialogs.push(d.message()); return d.accept(); });
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(String(e)));
await page.goto(html, { waitUntil: 'domcontentloaded', timeout: 20000 });
await page.waitForFunction(() => typeof toFractionInches === 'function' && typeof draw === 'function');

const result = await page.evaluate(() => {
  const out = {};
  const samples = [0, 0.0625, 0.125, 0.1875, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1, 1.0625, 3.875, 6.125, 12, 0.03125, 0.02];
  out.fractions = samples.map(function(n) { return [n, toFractionInches(n)]; });

  C.polygon = [{ x: 0, y: 0 }, { x: 48, y: 0 }, { x: 48, y: 36 }, { x: 0, y: 36 }];
  C.wall = { lH: 36, rV: 0, tW: 48, bV: 0 };
  C.voids = [];
  C.tile = { sh: 'square', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0 };
  const scale = 10;
  const wall = [[0, 0], [48 * scale, 0], [48 * scale, 36 * scale], [0, 36 * scale]];
  const verts = [[-30, 0], [90, 0], [90, 120], [-30, 120]];
  out.cutLabel = getCutDimensions(verts, wall, [], scale, 'square', 'pointy', 0);

  const shapes = ['square', 'rectangle', 'hex', 'penny', 'fishscale', 'arabesque', 'picket', 'octdot', 'diamond', 'rhombus', 'triangle', 'capsule', 'starcross'];
  out.shapes = [];
  shapes.forEach(function(shape) {
    try {
      C.tile = { sh: 'mosaic', or: 'pointy', w: 12, h: 12, gr: 0.0625, pattern: 0, subShape: shape, subW: 2, subH: 2, subGr: 0.125 };
      C.view.z = 8;
      C.view.oxInches = 1;
      C.view.oyInches = 1;
      const before = cx.rect;
      const rects = [];
      if (shape === 'square') {
        cx.rect = function(x, y, w, h) { rects.push([w, h]); return before.call(cx, x, y, w, h); };
      }
      draw();
      cx.rect = before;
      out.shapes.push({ shape: shape, full: full, part: part, threw: false, rect: rects[0] || null, option: !!document.querySelector('#subShape option[value="' + shape + '"]') });
    } catch (err) {
      out.shapes.push({ shape: shape, threw: String(err), option: !!document.querySelector('#subShape option[value="' + shape + '"]') });
    }
  });

  localStorage.removeItem('layit_pro');
  proUser = false;
  out.freePurchaseSetsPro = false;
  handleProPurchase('monthly');
  out.proAfterPurchaseAttempt = localStorage.getItem('layit_pro');
  out.upgradeOpen = document.getElementById('proUpgradeModal').classList.contains('active');
  closeUpgradeModal();
  const shareBlocked = requirePro('Share Project') === false;
  out.shareBlocked = shareBlocked;
  out.shareOverlay = !!document.getElementById('sharePreviewOverlay');

  openBarcodeScanner();
  out.barcodeBlocked = document.getElementById('proUpgradeModal').classList.contains('active');
  closeUpgradeModal();

  localStorage.setItem('layit_pro', 'true');
  proUser = true;
  updateProUI();
  openBarcodeScanner();
  out.scannerOpen = document.getElementById('scannerOverlay').classList.contains('active');
  closeBarcodeScanner();

  _tileDbReady = false;
  _tileDbRef = null;
  const known = lookupBarcode('203684368');
  out.knownFound = document.getElementById('productFoundModal') ? document.getElementById('productFoundModal').classList.contains('active') : null;
  const foundText = document.getElementById('productFoundDetails') ? document.getElementById('productFoundDetails').textContent : '';
  out.knownText = foundText;
  if (document.getElementById('productFoundModal')) document.getElementById('productFoundModal').classList.remove('active');
  lookupBarcode('000000000000');
  out.unknownOpen = document.getElementById('productNotFoundModal').classList.contains('active');
  closeProductNotFound();

  applyScannedProduct(TILE_DB_LOCAL['100116061']);
  out.appliedSub = document.getElementById('subShape').value;
  out.appliedW = C.tile.subW;
  out.appliedH = C.tile.subH;

  _AI_PROXY_URL = '';
  const input = document.getElementById('tileScanPhoto');
  const png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
  return fetch(png).then(function(r) { return r.blob(); }).then(function(blob) {
    const file = new File([blob], 'label.png', { type: 'image/png' });
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    handleAILabelScan(input);
    return new Promise(function(resolve) {
      setTimeout(function() {
        out.aiStatus = document.getElementById('aiScanStatus').textContent;
        const project = {
          schemaVersion: 1,
          name: 'Round Trip',
          config: JSON.parse(JSON.stringify(C)),
          cutTileStates: { '1,2': 2 },
          patternLocked: false,
          groutColor: '#eeeeee',
          tileColor: '#2255aa',
          tileStroke: '#112244',
          exportedAt: 1
        };
        project.config.tile.pattern = 0;
        project.config.view.oxInches = 3.25;
        const imp = document.getElementById('importFile');
        const f = new File([JSON.stringify(project)], 'round.json', { type: 'application/json' });
        const d2 = new DataTransfer();
        d2.items.add(f);
        imp.files = d2.files;
        imp.dispatchEvent(new Event('change', { bubbles: true }));
        setTimeout(function() {
          out.round = {
            pattern: C.tile.pattern,
            ox: C.view.oxInches,
            color: tileColor,
            sub: C.tile.subShape,
            cut: cutTileStates['1,2'] || null
          };
          const bad = new File(['{'], 'bad.json', { type: 'application/json' });
          const d3 = new DataTransfer();
          d3.items.add(bad);
          imp.files = d3.files;
          imp.dispatchEvent(new Event('change', { bubbles: true }));
          setTimeout(function() { resolve(out); }, 300);
        }, 400);
      }, 400);
    });
  });
});

await browser.close();

const fractionMismatches = result.fractions.filter(function(pair) {
  return pair[1] !== expectFraction(pair[0]);
});
check('cut fractions match nearest 1/16 independent of the page', fractionMismatches.length === 0, JSON.stringify(fractionMismatches));
check('a 12 in tile crossing x=0 keeps a 9 by 12 in remainder', result.cutLabel === '9" × 12"', result.cutLabel);
result.shapes.forEach(function(row) {
  check('mosaic ' + row.shape + ' draws without throwing', row.threw === false, row.threw);
  check('mosaic ' + row.shape + ' is selectable', row.option === true);
  if (row.shape === 'square' && row.rect) {
    const body = row.rect[0] / 8;
    check('square mosaic piece is 2 in, not 2 minus grout', Math.abs(body - 2) < 0.05, String(body));
  }
});
check('web purchase does not set Pro or charge', result.proAfterPurchaseAttempt !== 'true');
check('free share opens upgrade and does not build a report', result.shareBlocked === true && result.shareOverlay === false);
check('barcode stays behind Pro until the local flag is set', result.barcodeBlocked === true);
check('camera path opens and can be closed when Pro is only a local flag', result.scannerOpen === true);
check('offline built-in barcode resolves without Firebase', result.knownText.indexOf('Merola') >= 0, result.knownText);
check('unknown barcode offline opens not-found and does not write Firebase', result.unknownOpen === true);
check('herringbone mosaic barcode keeps rectangle pieces', result.appliedSub === 'rectangle' && result.appliedW === 1 && result.appliedH === 3, JSON.stringify(result));
check('AI scan without a proxy does not call a model', (result.aiStatus || '').indexOf('not configured') >= 0, result.aiStatus);
check('project import roundtrip keeps pattern 0, offset, color, and cut state', result.round && result.round.pattern === 0 && result.round.ox === 3.25 && result.round.color === '#2255aa' && result.round.cut === 2, JSON.stringify(result.round));
check('bad JSON import reports an error and stays on the page', dialogs.some(function(m) { return /import|JSON/i.test(m); }), dialogs.join(' | '));
const realErrors = pageErrors.filter(function(e) { return e.indexOf('ServiceWorker') < 0 && e.indexOf('firebase') < 0; });
check('no unexpected script errors', realErrors.length === 0, realErrors.join(' | '));
check('firebase and AI hosts were not contacted', blocked.every(function(u) { return /firebase|googleapis|gstatic|anthropic/i.test(u); }) || blocked.length === 0, blocked.slice(0, 5).join(' '));

if (failures.length) {
  console.error('FAILED');
  failures.forEach(function(f) { console.error(' - ' + f); });
  console.error(JSON.stringify({ fractions: result.fractions, cut: result.cutLabel, shapes: result.shapes, ai: result.aiStatus, round: result.round, dialogs: dialogs, errors: pageErrors.slice(0, 8) }, null, 2));
  process.exit(1);
}
console.log('remainder QA passed');
console.log('blocked hosts', blocked.length);
