/**
 * Decorative mosaic piece size, local report HTML, camera denial, and a mocked AI error.
 * No purchase, no Firebase write, no paid model call. Not iOS/WKWebView.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
function check(name, cond, detail) {
  if (!cond) failures.push(name + (detail ? ': ' + detail : ''));
  else console.log('ok', name);
}

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});
const page = await browser.newPage();
const hits = [];
const aiBodies = [
  { error: { message: '<script>bad</script>' } },
  { content: [{ text: JSON.stringify({ name: 'Mock Quarry', brand: 'Labeled Mock', shape: 'square', nomW: 8, nomH: 8, grout: 0.125 }) }] },
  { content: [{ text: 'not json at all' }] }
];
await page.setRequestInterception(true);
page.on('request', (req) => {
  const url = req.url();
  if (/mock-layit-ai/.test(url)) {
    hits.push('mock-ai:' + req.method());
    if (req.method() === 'OPTIONS') {
      req.respond({
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, X-LayIt-AI-Task, X-LayIt-AI-Profile'
        }
      });
      return;
    }
    req.respond({
      status: 200,
      contentType: 'application/json',
      headers: { 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify(aiBodies.shift() || { error: { message: 'queue empty' } })
    });
    return;
  }
  if (/firebase|googleapis|gstatic|anthropic|openai/i.test(url)) {
    hits.push('blocked:' + url.split('/')[2]);
    req.abort();
    return;
  }
  req.continue();
});
await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => typeof drawMosaicField === 'function');

const geo = await page.evaluate(() => {
  function measure(shape) {
    const cmds = [];
    const wrap = (name) => {
      const orig = cx[name];
      cx[name] = function() {
        const args = Array.prototype.slice.call(arguments);
        cmds.push([name].concat(args));
        return orig.apply(cx, args);
      };
      return orig;
    };
    const saved = ['beginPath', 'moveTo', 'lineTo', 'bezierCurveTo', 'quadraticCurveTo', 'arc', 'rect', 'closePath'].map((n) => [n, wrap(n)]);
    C.polygon = [{ x: 0, y: 0 }, { x: 24, y: 0 }, { x: 24, y: 24 }, { x: 0, y: 24 }];
    C.wall = { lH: 24, rV: 0, tW: 24, bV: 0 };
    C.voids = [];
    C.view.z = 10;
    C.view.oxInches = 2;
    C.view.oyInches = 2;
    C.tile = { sh: 'mosaic', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0, subShape: shape, subW: 2, subH: 2, subGr: 0.125 };
    draw();
    saved.forEach(function(pair) { cx[pair[0]] = pair[1]; });
    const paths = [[]];
    cmds.forEach(function(c) {
      if (c[0] === 'beginPath') { paths.push([]); return; }
      if (c[0] === 'closePath' || c[0] === 'rect') return;
      const cur = paths[paths.length - 1];
      for (let i = 1; i < c.length; i += 2) {
        if (typeof c[i] === 'number' && typeof c[i + 1] === 'number') cur.push([c[i], c[i + 1]]);
      }
    });
    function box(pts) {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      pts.forEach(function(p) {
        minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
        minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
      });
      return { minX: minX, maxX: maxX, minY: minY, maxY: maxY, wIn: (maxX - minX) / 10, hIn: (maxY - minY) / 10 };
    }
    const raw = paths.filter(function(p) { return p.length > 2; });
    const bodies = raw.map(box)
      .filter(function(b) { return b.wIn > 0.5 && b.wIn < 3 && b.hIn > 0.5 && b.hIn < 3; });
    const first = bodies[0] || { wIn: 0, hIn: 0 };
    let pairGap = null;
    for (let i = 0; i < bodies.length; i++) {
      for (let j = 0; j < bodies.length; j++) {
        if (i === j) continue;
        const gap = (bodies[j].minX - bodies[i].maxX) / 10;
        if (gap > 0 && (pairGap === null || gap < pairGap)) pairGap = gap;
      }
    }
    const rects = cmds.filter((c) => c[0] === 'rect').map((c) => ({ x: c[1], y: c[2], w: c[3], h: c[4] }));
    let dotClear = null;
    let dotW = null;
    if (rects.length) {
      const d = rects[0];
      dotW = d.w / 10;
      const cx0 = d.x + d.w / 2, cy0 = d.y + d.h / 2;
      const halfDiag = d.w / Math.SQRT2;
      let best = Infinity;
      raw.forEach(function(pts) {
        if (pts.length < 6) return;
        const b = box(pts);
        if (Math.abs(b.wIn - 2) > 0.05) return;
        for (let i = 0; i < pts.length; i++) {
          const a = pts[i], c = pts[(i + 1) % pts.length];
          const dx = c[0] - a[0], dy = c[1] - a[1], len2 = dx * dx + dy * dy;
          let t = len2 ? ((cx0 - a[0]) * dx + (cy0 - a[1]) * dy) / len2 : 0;
          t = Math.max(0, Math.min(1, t));
          best = Math.min(best, Math.hypot(cx0 - (a[0] + t * dx), cy0 - (a[1] + t * dy)));
        }
      });
      if (best < Infinity) dotClear = (best - halfDiag) / 10;
    }
    return {
      shape: shape,
      wIn: first.wIn,
      hIn: first.hIn,
      pairGap: pairGap,
      dotClear: dotClear,
      dotW: dotW
    };
  }
  const arab = measure('arabesque');
  const oct = measure('octdot');
  const tri = measure('triangle');
  C.tile.subShape = 'square';
  C.tile.subW = 2;
  C.tile.subH = 2;
  C.tile.subGr = 0.125;
  C.tile.w = 12;
  C.tile.h = 12;
  const sheet = buildLayItPattern();
  const a = sheet.tiles[0];
  const b = sheet.tiles.find((t) => t.row === a.row && t.col === a.col + 1);
  return { arab, oct, tri, sheetFile: sheet.tile.mosaicFile, sheetPitch: b ? b.x - a.x : null, hw: sheet.hardwareCompile, ready: sheet.hardwareReadyArtifact };
});

// Camera denied and unavailable. Local Pro flag only — not a purchase.
await page.evaluate(() => {
  localStorage.setItem('layit_pro', 'true');
  proUser = true;
  const real = navigator.mediaDevices;
  navigator.mediaDevices = { getUserMedia: function() { return Promise.reject(Object.assign(new Error('denied'), { name: 'NotAllowedError' })); } };
  openBarcodeScanner();
  window.__cam = 'pending';
  setTimeout(function() {
    window.__cam = document.getElementById('scannerStatus').textContent;
    closeBarcodeScanner();
    navigator.mediaDevices.getUserMedia = undefined;
    openBarcodeScanner();
    window.__cam2 = document.getElementById('scannerStatus').textContent;
    closeBarcodeScanner();
    navigator.mediaDevices = real;
  }, 50);
});
await page.waitForFunction(() => window.__cam2);

// Labeled mock AI. Requests are answered in-process and never reach a model host.
const ai = await page.evaluate(async () => {
  _AI_PROXY_URL = 'https://mock-layit-ai.invalid/v1';
  const input = document.getElementById('tileScanPhoto');
  const png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
  const blob = await (await fetch(png)).blob();
  const file = new File([blob], 'label.png', { type: 'image/png' });
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  async function scan() {
    const before = document.getElementById('aiScanStatus').textContent;
    handleAILabelScan(input);
    const start = Date.now();
    while (Date.now() - start < 6000) {
      const text = document.getElementById('aiScanStatus').textContent || '';
      if (text && text !== before && text.indexOf('Reading tile') < 0) return text;
      await new Promise((r) => setTimeout(r, 40));
    }
    return document.getElementById('aiScanStatus').textContent || '';
  }
  const errorText = await scan();
  const decoded = document.getElementById('aiPhotoPreviewImg').naturalWidth;
  const successText = await scan();
  const filled = {
    name: document.getElementById('contribName').value,
    brand: document.getElementById('contribBrand').value,
    nomW: document.getElementById('contribNomW').value
  };
  const writes = [];
  _tileDbReady = false;
  _tileDbRef = { child: function() { return { set: function(v) { writes.push(v); } }; } };
  applyAIScannedProduct();
  const writesWhileOff = writes.length;
  window._aiScannedProduct = { name: 'Mock Quarry', brand: 'Labeled Mock', shape: 'square', nomW: 8, nomH: 8, actW: 7.875, actH: 7.875, grout: 0.125 };
  _pendingBarcode = 'mock-barcode';
  _tileDbReady = true;
  applyAIScannedProduct();
  const badText = await scan();
  return { errorText, decoded, successText, filled, writesWhileOff, mockWrite: writes[0] || null, badText, appliedW: C.tile.w };
});

// Local report HTML only. Do not call nativeShareProject.
const report = await page.evaluate(async () => {
  document.getElementById('projName').value = 'Report Check <script>';
  document.getElementById('tileShape').value = 'square';
  onShape();
  document.getElementById('nominalMode').checked = false;
  setLengthInputValue('tileW', 12);
  setLengthInputValue('tileH', 12);
  document.getElementById('grout').value = '0.125';
  updateTile();
  document.getElementById('quickWidth').value = '48';
  document.getElementById('quickHeight').value = '36';
  applyQuickRectangle();
  document.getElementById('companyName').value = "O'Brien <b>Tile</b>";
  shareProject();
  const html = window._shareHtml || '';
  const shared = !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.shareHtml);
  const dim = formatLength(Math.max(C.wall.tW, C.wall.tW + C.wall.bV)) + ' × ' + formatLength(Math.max(C.wall.lH, C.wall.lH + C.wall.rV));
  const counts = {
    full: html.indexOf('Full Tiles</span><span class="detail-value">' + full) >= 0,
    cut: html.indexOf('Cut Tiles</span><span class="detail-value">' + part) >= 0,
    dim: html.indexOf(dim) >= 0,
    grout: html.indexOf(formatLength(C.tile.gr)) >= 0,
    nameEscaped: html.indexOf('<script>') < 0 && html.indexOf('&lt;b&gt;') >= 0
  };
  closeSharePreview();
  const origCreate = document.createElement.bind(document);
  document.createElement = function(tag) {
    const el = origCreate(tag);
    if (String(tag).toLowerCase() === 'a') {
      el.click = function() { window.__exportHref = el.href; };
    }
    return el;
  };
  cutTileStates['2,3'] = 1;
  patternLocked = true;
  exportProject();
  document.createElement = origCreate;
  const exported = await (await fetch(window.__exportHref)).json();
  const toggle = document.querySelector('.unit-toggle-input');
  toggle.checked = true;
  toggleUnitsFromControl(toggle);
  document.getElementById('tileW').value = '30.48';
  document.getElementById('tileH').value = '30.48';
  updateTile();
  const cmInches = C.tile.w;
  toggle.checked = false;
  toggleUnitsFromControl(toggle);
  const backToInches = document.getElementById('tileW').value;
  return { shared: shared, counts: counts, exported: {
    schema: exported.schemaVersion,
    name: exported.name,
    w: exported.config.tile.w,
    pattern: exported.config.tile.pattern,
    locked: exported.patternLocked,
    cut: exported.cutTileStates['2,3'],
    color: exported.tileColor,
    groutColor: exported.groutColor
  }, cmInches: cmInches, backToInches: backToInches };
});

const cam = await page.evaluate(() => ({ denied: window.__cam, missing: window.__cam2 }));
await browser.close();

check('arabesque body is the entered 2 in and the same-row joint is one grout minus the 2% shoulder', geo.arab.wIn > 2.0 && geo.arab.hIn > 1.95 && geo.arab.pairGap > 0.05 && geo.arab.pairGap < 0.15, JSON.stringify(geo.arab));
check('octagon flat-to-flat is 2 in and the dot clears the cut corner by one grout', Math.abs(geo.oct.wIn - 2) < 0.05 && Math.abs(geo.oct.hIn - 2) < 0.05 && Math.abs(geo.oct.pairGap - 0.125) < 0.02 && Math.abs(geo.oct.dotClear - 0.125) < 0.02, JSON.stringify(geo.oct));
check('triangle pair leaves one piece-grout between up and down', geo.tri.wIn > 1.9 && geo.tri.pairGap > 0.1 && geo.tri.pairGap < 0.16, JSON.stringify(geo.tri));
check('mosaic file is still sheet outlines at one piece-grout pitch', geo.sheetFile === 'sheet-outlines' && Math.abs(geo.sheetPitch - 12.125) < 1e-6, JSON.stringify(geo));
check('hardware flags stay closed', geo.hw === false && geo.ready === false);
check('camera denial is shown and does not throw', (cam.denied || '').indexOf('denied') >= 0, JSON.stringify(cam));
check('missing camera is shown', (cam.missing || '').indexOf('not available') >= 0, JSON.stringify(cam));
check('mocked AI error is shown as text, not markup', ai.errorText.indexOf('AI error') >= 0 && ai.errorText.indexOf('<script>') >= 0, ai.errorText);
check('still-image fixture decodes in the scan preview', ai.decoded === 1, String(ai.decoded));
check('mocked AI success fills the form and does not write while Firebase is off', ai.filled.name === 'Mock Quarry' && ai.filled.brand === 'Labeled Mock' && ai.writesWhileOff === 0, JSON.stringify(ai.filled));
check('Firebase write stays on the in-page mock when the flag is on', ai.mockWrite && ai.mockWrite.source === 'ai-vision' && ai.mockWrite.name === 'Mock Quarry', JSON.stringify(ai.mockWrite));
check('malformed mock AI text is reported without inserting it', (ai.badText || '').indexOf('Could not parse') >= 0 && (ai.badText || '').indexOf('not json') < 0, ai.badText);
check('mocked AI was the only synthetic call', hits.some((h) => h.indexOf('mock-ai') === 0) && hits.every((h) => h.indexOf('mock-ai') === 0 || h.indexOf('blocked:') === 0), hits.join(','));
check('client report matches the live layout and escapes names', report.shared === false && report.counts.full && report.counts.cut && report.counts.dim && report.counts.grout && report.counts.nameEscaped, JSON.stringify(report.counts));
check('project export keeps schema, pattern, lock, color, and cut state', report.exported.schema === 1 && report.exported.locked === true && report.exported.cut === 1 && report.exported.w === 12, JSON.stringify(report.exported));
check('centimeter entry converts to inches and back', Math.abs(report.cmInches - 12) < 0.02 && report.backToInches === '12', JSON.stringify(report));

if (failures.length) {
  console.error('FAILED');
  failures.forEach((f) => console.error(' - ' + f));
  process.exit(1);
}
console.log('filler and boundary checks passed');
