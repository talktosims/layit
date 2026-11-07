/**
 * Runtime checks against the LayIt page in headless Chrome.
 * These are not iOS/WKWebView tests.
 *
 *   node tests/geometry-contract.mjs
 * Requires puppeteer-core and Chrome. This environment uses
 * /tmp/layit-probe/node_modules/puppeteer-core and /usr/local/bin/google-chrome.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fixtureDir = path.join(root, 'tests', 'fixtures');
const evidenceDir = path.join(root, 'tests', 'evidence');
fs.mkdirSync(fixtureDir, { recursive: true });
fs.mkdirSync(evidenceDir, { recursive: true });

const failures = [];
function check(name, cond, detail) {
  if (!cond) failures.push(name + (detail ? ': ' + detail : ''));
  else console.log('ok', name);
}

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
});
const page = await browser.newPage();
await page.setViewport({ width: 1280, height: 900 });
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(String(e)));
page.on('dialog', (d) => d.accept());
await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded', timeout: 20000 });
await page.waitForFunction(() => typeof buildLayItPattern === 'function' && typeof draw === 'function');

const measured = await page.evaluate(() => {
  function bbox(verts) {
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    verts.forEach(function(p) {
      minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
      minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
    });
    return { minX: minX, maxX: maxX, minY: minY, maxY: maxY, w: maxX - minX, h: maxY - minY };
  }
  function strokeMatches(tile, flipH, tw, th) {
    var rec = [];
    var orig = { beginPath: cx.beginPath, moveTo: cx.moveTo, lineTo: cx.lineTo, closePath: cx.closePath, rect: cx.rect };
    cx.beginPath = function() {};
    cx.rect = function() {};
    cx.moveTo = function(x, y) { rec.push([x, y]); };
    cx.lineTo = function(x, y) { rec.push([x, y]); };
    cx.closePath = function() {};
    var fromLeft = tile.x;
    var fromTop = flipH - tile.y;
    drawTile(fromLeft, fromTop, tw, th, C.tile.gr, tile.row, tile.col);
    cx.beginPath = orig.beginPath; cx.moveTo = orig.moveTo; cx.lineTo = orig.lineTo;
    cx.closePath = orig.closePath; cx.rect = orig.rect;
    if (rec.length !== tile.verts.length) return false;
    for (var i = 0; i < rec.length; i++) {
      var upx = rec[i][0];
      var upy = flipH - rec[i][1];
      if (Math.abs(upx - tile.verts[i][0]) > 1e-6 || Math.abs(upy - tile.verts[i][1]) > 1e-6) return false;
    }
    return true;
  }
  function rectRoom(w, h) {
    C.polygon = [{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: h }, { x: 0, y: h }];
    C.wall = { lH: h, rV: 0, tW: w, bV: 0 };
    C.voids = [];
  }

  var initialFull = full;
  var initialPart = part;

  rectRoom(48, 36);
  C.tile = { sh: 'square', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0 };
  C.view.oxInches = 6.0625;
  C.view.oyInches = 6.0625;
  C.view.z = 4;
  draw();
  var squarePat = buildLayItPattern();
  var a = squarePat.tiles.find(function(t) { return t.col === 0 && t.row === 0; });
  var b = squarePat.tiles.find(function(t) { return t.col === 1 && t.row === 0; });
  var ba = bbox(a.verts);
  var bb = bbox(b.verts);
  var square = {
    bodyW: ba.w, bodyH: ba.h,
    gap: bb.minX - ba.maxX,
    pitch: b.x - a.x,
    centerY: a.y,
    count: squarePat.tiles.length,
    fullTiles: squarePat.tiles.filter(function(t) { return !t.isCut; }).length,
    drawFull: full, drawPart: part,
    opt: countTilesForOptimize(),
    stroke: strokeMatches(a, 36, 12, 12),
    flags: {
      hardwareCompile: squarePat.hardwareCompile,
      simulationOnly: squarePat.simulationOnly,
      laser: squarePat.laser,
      requirement: squarePat.requirement
    }
  };

  document.getElementById('tileShape').value = 'square';
  document.getElementById('nominalMode').checked = true;
  setLengthInputValue('tileW', 12);
  setLengthInputValue('tileH', 12);
  document.getElementById('grout').value = '0.125';
  updateTile();
  var nominalPat = buildLayItPattern();
  var na = nominalPat.tiles.find(function(t) { return t.col === 0 && t.row === 0; });
  var nb = nominalPat.tiles.find(function(t) { return t.col === 1 && t.row === 0; });
  var nba = bbox(na.verts);
  var nbb = bbox(nb.verts);
  var nominal = { storedW: C.tile.w, body: nba.w, gap: nbb.minX - nba.maxX, pitch: nb.x - na.x };

  var hexH = 10 * 2 / Math.sqrt(3);
  rectRoom(80, 80);
  C.tile = { sh: 'hexagon', or: 'pointy', w: 10, h: hexH, gr: 0.125, pattern: 0 };
  C.view.oxInches = 20;
  C.view.oyInches = 20;
  C.view.z = 4;
  var hexPat = buildLayItPattern();
  var ht = hexPat.tiles.find(function(t) { return !t.isCut; });
  var hb = bbox(ht.verts);
  var pitch = layoutPitchInches();
  var neighbor = hexPat.tiles.find(function(t) { return t.row === ht.row && t.col === ht.col + 1; });
  var hex = {
    bodyW: hb.w, bodyH: hb.h,
    pitchCol: pitch.col, pitchRow: pitch.row,
    centerDx: neighbor ? neighbor.x - ht.x : null,
    stroke: strokeMatches(ht, 80, 10, hexH),
    count: hexPat.tiles.length,
    oddRowShift: (function() {
      var even = null;
      for (var i = 0; i < hexPat.tiles.length; i++) {
        var t = hexPat.tiles[i];
        if (((t.row % 2 + 2) % 2) !== 0) continue;
        var odd = null;
        for (var j = 0; j < hexPat.tiles.length; j++) {
          var u = hexPat.tiles[j];
          if (u.col === t.col && u.row === t.row + 1) odd = u;
        }
        if (odd) { even = { dx: odd.x - t.x }; break; }
      }
      return even ? even.dx : null;
    })()
  };

  rectRoom(96, 60);
  C.tile = { sh: 'herringbone', or: 'pointy', w: 4, h: 8, gr: 0.125, pattern: 0 };
  C.view.oxInches = 12;
  C.view.oyInches = 12;
  var herringPat = buildLayItPattern();
  var hh = herringPat.tiles.find(function(t) { return !t.isCut; });
  var herring = {
    body: bbox(hh.verts),
    stroke: strokeMatches(hh, 60, 4, 8),
    count: herringPat.tiles.length
  };

  rectRoom(48, 48);
  C.tile = { sh: 'mosaic', or: 'pointy', w: 12, h: 12, gr: 0.0625, pattern: 0, subShape: 'square', subW: 2, subH: 2, subGr: 0.0625 };
  C.view.oxInches = 6;
  C.view.oyInches = 6;
  var mosaicPat = buildLayItPattern();
  var ms = mosaicPat.tiles.find(function(t) { return !t.isCut; });
  var ms2 = mosaicPat.tiles.find(function(t) { return t.row === ms.row && t.col === ms.col + 1; });
  var mosaic = {
    file: mosaicPat.tile.mosaicFile,
    preview: mosaicPat.tile.mosaicPreview,
    body: bbox(ms.verts),
    pitch: ms2.x - ms.x,
    count: mosaicPat.tiles.length
  };

  rectRoom(120, 96);
  C.tile = { sh: 'square', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0 };
  C.view.oxInches = 6;
  C.view.oyInches = 6;
  C.view.z = 8;
  var t0 = performance.now();
  draw();
  var largeMs = performance.now() - t0;
  var largePat = buildLayItPattern();
  var large = { drawFull: full, drawPart: part, exportCount: largePat.tiles.length, ms: largeMs };

  // pattern 0 must stay 0
  C.tile.pattern = 0;
  C.tile.sh = 'square';
  document.getElementById('tileShape').value = 'square';
  document.getElementById('tilePattern').value = (C.tile.pattern === 0 || C.tile.pattern) ? String(C.tile.pattern) : '0';
  var patternSelect = document.getElementById('tilePattern').value;

  // cm round trip
  document.getElementById('nominalMode').checked = false;
  setLengthInputValue('tileW', 12);
  toggleUnitsFromControl({ checked: true });
  var cmDisplay = document.getElementById('tileW').value;
  var inchesBack = readLengthInputValue('tileW');
  toggleUnitsFromControl({ checked: false });

  // projects
  unsavedChanges = false;
  currentProjectId = null;
  document.getElementById('projName').value = 'Alpha Keep';
  rectRoom(40, 30);
  C.tile = { sh: 'square', or: 'pointy', w: 10, h: 10, gr: 0.125, pattern: 0 };
  saveCurrentProject();
  var alphaId = currentProjectId;
  currentProjectId = null;
  document.getElementById('projName').value = 'Beta <script>Delete';
  C.tile.w = 8;
  saveCurrentProject();
  var betaId = currentProjectId;
  deleteProject(betaId);
  var projects = getProjects();
  var names = Object.keys(projects).map(function(id) { return projects[id].name; });

  // perimeter close
  addPerimeterPoint(40, 40);
  addPerimeterPoint(220, 55);
  addPerimeterPoint(190, 180);
  closePerimeter();

  return {
    initialFull: initialFull, initialPart: initialPart,
    square: square, nominal: nominal, hex: hex, herring: herring, mosaic: mosaic, large: large,
    patternSelect: patternSelect, cmDisplay: cmDisplay, inchesBack: inchesBack,
    alphaId: alphaId, betaId: betaId, names: names,
    squarePat: squarePat, hexPat: hexPat, herringPat: herringPat
  };
});

const extra = await page.evaluate(() => {
  function bbox(verts) {
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    verts.forEach(function(p) {
      minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
      minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
    });
    return { w: maxX - minX, h: maxY - minY };
  }
  C.polygon = [{ x: 0, y: 0 }, { x: 60, y: 0 }, { x: 60, y: 40 }, { x: 0, y: 40 }];
  C.wall = { lH: 40, rV: 0, tW: 60, bV: 0 };
  C.voids = [];
  C.tile = { sh: 'rectangle', or: 'flat', w: 4, h: 8, gr: 0.125, pattern: 0.5 };
  C.view.oxInches = 6;
  C.view.oyInches = 6;
  var brick = buildLayItPattern();
  var even = brick.tiles.filter(function(t) { return ((t.row % 2 + 2) % 2) === 0; })[0];
  var odd = null;
  brick.tiles.forEach(function(t) {
    if (t.col === even.col && t.row === even.row + 1) odd = t;
  });
  C.tile = { sh: 'hexagon', or: 'flat', w: 8, h: 7, gr: 0.125, pattern: 0 };
  var flatPitch = layoutPitchInches();
  var flatPat = buildLayItPattern();
  var ft = flatPat.tiles.find(function(t) { return !t.isCut; }) || flatPat.tiles[0];
  C.view.oxInches = 0;
  C.view.oyInches = 0;
  C.tile = { sh: 'square', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0 };
  C.polygon = [{ x: 0, y: 0 }, { x: 48, y: 0 }, { x: 48, y: 36 }, { x: 0, y: 36 }];
  C.wall = { lH: 36, rV: 0, tW: 48, bV: 0 };
  var edge = buildLayItPattern();
  var cut = edge.tiles.filter(function(t) { return t.isCut; })[0];
  var t0 = performance.now();
  C.polygon = [{ x: 0, y: 0 }, { x: 300, y: 0 }, { x: 300, y: 400 }, { x: 0, y: 400 }];
  C.wall = { lH: 400, rV: 0, tW: 300, bV: 0 };
  C.tile = { sh: 'square', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0 };
  C.view.z = 2;
  draw();
  var bigMs = performance.now() - t0;
  return {
    brickDx: odd.x - even.x,
    brickBody: bbox(even.verts),
    flatPitch: flatPitch,
    flatBody: bbox(ft.verts),
    cutBody: bbox(cut.verts),
    cutIsCut: cut.isCut,
    bigMs: bigMs,
    bigCount: full + part
  };
});

await new Promise((r) => setTimeout(r, 250));
const closePx = await page.evaluate(() => {
  var pts = perimeterState.points;
  var canvas = perimeterState.canvas;
  var ctx = perimeterState.ctx;
  var a = pts[0];
  var b = pts[pts.length - 1];
  var samples = [];
  for (var t = 0.3; t <= 0.7; t += 0.1) {
    var x = Math.round(a.x + (b.x - a.x) * t);
    var y = Math.round(a.y + (b.y - a.y) * t);
    var p = ctx.getImageData(x, y, 1, 1).data;
    samples.push([p[0], p[1], p[2]]);
  }
  return { closed: perimeterState.closed, samples: samples, n: pts.length, w: canvas.width };
});

// Screenshots of the full square and hex layouts.
await page.evaluate(() => {
  C.polygon = [{ x: 0, y: 0 }, { x: 48, y: 0 }, { x: 48, y: 36 }, { x: 0, y: 36 }];
  C.wall = { lH: 36, rV: 0, tW: 48, bV: 0 };
  C.voids = [];
  C.tile = { sh: 'square', or: 'pointy', w: 12, h: 12, gr: 0.125, pattern: 0 };
  C.view.oxInches = 6.0625;
  C.view.oyInches = 6.0625;
  C.view.z = 10;
  C.view.panX = 0; C.view.panY = 0;
  document.getElementById('nominalMode').checked = false;
  showTab('diagram');
  draw();
});
await page.screenshot({ path: path.join(evidenceDir, 'square-12-layout.png') });
await page.screenshot({ path: '/opt/cursor/artifacts/square-12-layout.png' });

await page.evaluate(() => {
  var hexH = 10 * 2 / Math.sqrt(3);
  C.polygon = [{ x: 0, y: 0 }, { x: 60, y: 0 }, { x: 60, y: 48 }, { x: 0, y: 48 }];
  C.wall = { lH: 48, rV: 0, tW: 60, bV: 0 };
  C.tile = { sh: 'hexagon', or: 'pointy', w: 10, h: hexH, gr: 0.125, pattern: 0 };
  C.view.oxInches = 8;
  C.view.oyInches = 8;
  C.view.z = 8;
  draw();
});
await page.screenshot({ path: path.join(evidenceDir, 'hex-pointy-10-layout.png') });
await page.screenshot({ path: '/opt/cursor/artifacts/hex-pointy-10-layout.png' });

await page.setViewport({ width: 390, height: 844 });
await page.evaluate(() => { draw(); });
await page.screenshot({ path: path.join(evidenceDir, 'hex-layout-phone.png') });
await page.screenshot({ path: '/opt/cursor/artifacts/hex-layout-phone.png' });

fs.writeFileSync(path.join(fixtureDir, 'square-12in-grout-eighth.layit'), JSON.stringify(measured.squarePat, null, 2));
fs.writeFileSync(path.join(fixtureDir, 'hex-pointy-10in-regular.layit'), JSON.stringify(measured.hexPat, null, 2));
fs.writeFileSync(path.join(fixtureDir, 'herringbone-4x8-grout-eighth.layit'), JSON.stringify(measured.herringPat, null, 2));

const s = measured.square;
check('square body is 12 in, not 11.875', Math.abs(s.bodyW - 12) < 1e-6 && Math.abs(s.bodyH - 12) < 1e-6, JSON.stringify(s));
check('square joint is 1/8 in, not 1/4', Math.abs(s.gap - 0.125) < 1e-6, String(s.gap));
check('square pitch is 12.125', Math.abs(s.pitch - 12.125) < 1e-6, String(s.pitch));
check('square preview stroke matches .layit verts', s.stroke === true);
check('square export is full layout and laser off', s.flags.hardwareCompile === false && s.flags.laser === 'off' && s.flags.simulationOnly === true && s.flags.requirement === 'F1-full-layout');
check('square Y origin is bottom-left (center near the top of a 36 in wall)', Math.abs(s.centerY - (36 - 6.0625)) < 1e-6, String(s.centerY));
check('draw count matches export count', s.drawFull + s.drawPart === s.count, s.drawFull + '+' + s.drawPart + ' vs ' + s.count);
check('optimizer count matches draw', s.opt.full + s.opt.cut === s.drawFull + s.drawPart, JSON.stringify(s.opt) + ' vs ' + s.drawFull + '+' + s.drawPart);

const n = measured.nominal;
check('nominal 12 minus one grout stores 11.875', Math.abs(n.storedW - 11.875) < 1e-6, String(n.storedW));
check('nominal joint is still one grout, not two', Math.abs(n.gap - 0.125) < 1e-6 && Math.abs(n.pitch - 12) < 1e-6, JSON.stringify(n));

const h = measured.hex;
const expectRow = (10 * 2 / Math.sqrt(3)) * 0.75 + 0.125;
check('pointy 10 in hex body width is 10, not about 5', Math.abs(h.bodyW - 10) < 1e-6, String(h.bodyW));
check('pointy hex column step is width + grout', Math.abs(h.pitchCol - 10.125) < 1e-6 && Math.abs(h.centerDx - 10.125) < 1e-6, JSON.stringify(h));
check('pointy hex row step is 0.75*height + grout', Math.abs(h.pitchRow - expectRow) < 1e-6, h.pitchRow + ' vs ' + expectRow);
check('hex preview stroke matches .layit verts', h.stroke === true);
check('odd hex rows are shifted by half a column', Math.abs(h.oddRowShift - 10.125 / 2) < 1e-6, String(h.oddRowShift));
check('half-bond shifts odd rows by half the pitch and keeps a 4 by 8 body', Math.abs(extra.brickDx - (8.125 / 2)) < 1e-6 && Math.abs(extra.brickBody.w - 8) < 1e-6 && Math.abs(extra.brickBody.h - 4) < 1e-6, JSON.stringify(extra));
check('flat hex pitch follows patent th*0.75+grout by tw+grout', Math.abs(extra.flatPitch.col - (7 * 0.75 + 0.125)) < 1e-6 && Math.abs(extra.flatPitch.row - (8 + 0.125)) < 1e-6, JSON.stringify(extra.flatPitch));
check('a cut tile is still the full 12 inch body for the compiler to clip', extra.cutIsCut === true && Math.abs(extra.cutBody.w - 12) < 1e-6 && Math.abs(extra.cutBody.h - 12) < 1e-6, JSON.stringify(extra.cutBody));
check('300 by 400 inch room at 12 inch tile still counts', extra.bigCount > 100 && extra.bigMs < 5000, extra.bigCount + ' in ' + extra.bigMs);

check('herringbone stroke matches export', measured.herring.stroke === true);
check('herringbone body is the full 45 degree tile, not grout-shrunk', measured.herring.body.w > 8.4, JSON.stringify(measured.herring.body));

check('mosaic file stays sheet outlines', measured.mosaic.file === 'sheet-outlines' && measured.mosaic.preview === 'sub-tile-field');
check('mosaic sheet body is the sheet size and the gap is sub-tile grout', Math.abs(measured.mosaic.body.w - 12) < 1e-6 && Math.abs(measured.mosaic.pitch - 12.0625) < 1e-6, JSON.stringify(measured.mosaic));

check('large layout count matches export', measured.large.drawFull + measured.large.drawPart === measured.large.exportCount, JSON.stringify(measured.large));
check('large 120x96 layout draws in under 2s', measured.large.ms < 2000, String(measured.large.ms));
check('stack-bond pattern 0 is not coerced to 0.5', measured.patternSelect === '0', measured.patternSelect);
check('cm display converts 12 in to 30.48 and reads back 12', measured.cmDisplay === '30.48' && Math.abs(measured.inchesBack - 12) < 1e-6, measured.cmDisplay + ' / ' + measured.inchesBack);
check('deleting one project leaves the other', measured.names.indexOf('Alpha Keep') >= 0 && measured.names.indexOf('Beta <script>Delete') < 0, JSON.stringify(measured.names));
check('default layout rendered tiles before the test changed state', measured.initialFull + measured.initialPart > 0, measured.initialFull + '+' + measured.initialPart);

var closeLit = closePx.samples.some(function(p) { return p[0] > 80 || p[1] > 80; });
check('closed perimeter draws the segment back to the first point', closePx.closed && closePx.n === 3 && closeLit, JSON.stringify(closePx));

const realErrors = pageErrors.filter(function(e) { return e.indexOf('ServiceWorker') < 0 && e.indexOf('manifest') < 0; });
check('no page script errors', realErrors.length === 0, realErrors.join(' | '));

await browser.close();

if (failures.length) {
  console.error('\nFAILED');
  failures.forEach(function(f) { console.error(' - ' + f); });
  process.exit(1);
}
console.log('\nAll geometry and UI checks passed.');
