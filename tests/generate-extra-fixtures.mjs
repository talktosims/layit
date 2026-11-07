/**
 * Generate void, mosaic, and centimeter-roundtrip .layit files by driving index.html.
 * Geometry is whatever buildLayItPattern returns. Nothing here is hand-built tile math.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outDir = path.join(root, 'tests/fixtures');
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});
const page = await browser.newPage();
await page.setRequestInterception(true);
page.on('request', (req) => {
  const url = req.url();
  if (/firebase|googleapis|gstatic|anthropic/i.test(url)) req.abort();
  else req.continue();
});
await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => typeof buildLayItPattern === 'function' && typeof addVoid === 'function');

const report = await page.evaluate(() => {
  function bbox(verts) {
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    verts.forEach(function(p) {
      minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
      minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
    });
    return { minX: minX, maxX: maxX, minY: minY, maxY: maxY, w: maxX - minX, h: maxY - minY };
  }
  function tileHitsRect(tile, rect) {
    var b = bbox(tile.verts);
    return !(b.maxX < rect.x || b.minX > rect.x + rect.w || b.maxY < rect.y || b.minY > rect.y + rect.h);
  }
  function addCutout(label, cx, cy, w, h) {
    var before = C.voids.length;
    document.getElementById('voidLabel').value = label;
    setLengthInputValue('voidX', cx);
    setLengthInputValue('voidY', cy);
    setLengthInputValue('voidW', w);
    setLengthInputValue('voidH', h);
    addVoid();
    return { label: label, added: C.voids.length === before + 1, stored: C.voids[C.voids.length - 1] };
  }

  document.getElementById('nominalMode').checked = false;
  document.getElementById('tileShape').value = 'square';
  onShape();
  setLengthInputValue('tileW', 12);
  setLengthInputValue('tileH', 12);
  document.getElementById('grout').value = '0.125';
  document.getElementById('tilePattern').value = '0';
  updateTile();
  document.getElementById('quickWidth').value = '48';
  document.getElementById('quickHeight').value = '36';
  applyQuickRectangle();
  C.view.oxInches = 6.0625;
  C.view.oyInches = 6.0625;
  C.voids = [];

  var adds = [];
  adds.push(addCutout('Inside', 24, 18, 6, 4));
  adds.push(addCutout('CrossLeft', 2, 18, 8, 6));
  adds.push(addCutout('OverlapInside', 25, 18, 6, 4));
  adds.push(addCutout('TouchLeftEdge', 3, 10, 6, 4));
  adds.push(addCutout('ZeroWidth', 10, 10, 0, 4));
  var beforeCover = buildLayItPattern().tiles.length;
  adds.push(addCutout('CoversTile', 6.5, 30, 13, 14));
  var voidPat = buildLayItPattern();
  var afterCover = voidPat.tiles.length;
  var voidSummary = voidPat.voids.map(function(v) {
    var hit = voidPat.tiles.filter(function(t) { return tileHitsRect(t, v); });
    var cut = hit.filter(function(t) { return t.isCut; });
    return {
      l: v.l, x: v.x, y: v.y, w: v.w, h: v.h,
      tilesTouchingBBox: hit.length,
      touchingMarkedCut: cut.length
    };
  });
  var omittedFullyInside = 0;
  voidPat.tiles.forEach(function() {});

  // Centimeter entry of the same 48 x 36 in room and 12 in tile.
  C.voids = [];
  toggleUnitsFromControl({ checked: true });
  document.getElementById('quickWidth').value = '121.92';
  document.getElementById('quickHeight').value = '91.44';
  applyQuickRectangle();
  document.getElementById('tileShape').value = 'square';
  document.getElementById('nominalMode').checked = false;
  document.getElementById('grout').value = '0.125';
  document.getElementById('tilePattern').value = '0';
  setLengthInputValue('tileW', 12);
  setLengthInputValue('tileH', 12);
  updateTile();
  C.view.oxInches = 6.0625;
  C.view.oyInches = 6.0625;
  var cmDisplay = document.getElementById('tileW').value;
  var inchesRead = readLengthInputValue('tileW');
  var cmPat = buildLayItPattern();
  var cmTile = cmPat.tiles.find(function(t) { return !t.isCut; });
  var cmBody = bbox(cmTile.verts);
  toggleUnitsFromControl({ checked: false });

  // Mosaic sheet export. Screen still draws pieces.
  document.getElementById('tileShape').value = 'mosaic';
  onShape();
  document.getElementById('subShape').value = 'square';
  setLengthInputValue('tileW', 12);
  setLengthInputValue('tileH', 12);
  setLengthInputValue('subW', 2);
  setLengthInputValue('subH', 2);
  document.getElementById('subGr').value = '0.125';
  document.getElementById('grout').value = '0.125';
  updateTile();
  document.getElementById('quickWidth').value = '36';
  document.getElementById('quickHeight').value = '24';
  applyQuickRectangle();
  C.view.oxInches = 6;
  C.view.oyInches = 6;
  C.voids = [];
  var rects = [];
  var orig = cx.rect;
  cx.rect = function(x, y, w, h) { rects.push({ x: x, y: y, w: w, h: h }); return orig.call(cx, x, y, w, h); };
  draw();
  cx.rect = orig;
  var mosaicPat = buildLayItPattern();
  var sheet = mosaicPat.tiles.find(function(t) { return !t.isCut; }) || mosaicPat.tiles[0];
  var sheetNext = mosaicPat.tiles.find(function(t) { return t.row === sheet.row && t.col === sheet.col + 1; });
  var sheetBox = bbox(sheet.verts);
  var piece = null;
  if (rects.length > 1) {
    var s = C.view.z;
    var bodies = rects.map(function(r) { return { w: r.w / s, h: r.h / s, x: r.x / s, y: r.y / s }; });
    bodies.sort(function(a, b) { return a.x - b.x; });
    for (var i = 1; i < bodies.length; i++) {
      if (Math.abs(bodies[i].y - bodies[0].y) < 0.05 && bodies[i].x > bodies[0].x) {
        piece = { bodyW: bodies[0].w, gap: bodies[i].x - (bodies[0].x + bodies[0].w) };
        break;
      }
    }
  }

  return {
    voidAdds: adds.map(function(a) { return { label: a.label, added: a.added, stored: a.stored }; }),
    voidCount: voidPat.voids.length,
    voidSummary: voidSummary,
    tileCount: voidPat.tiles.length,
    tilesBeforeCoveringVoid: beforeCover,
    tilesAfterCoveringVoid: afterCover,
    cutCount: voidPat.tiles.filter(function(t) { return t.isCut; }).length,
    voidPat: voidPat,
    cm: { display: cmDisplay, inches: inchesRead, wallW: cmPat.wall.width, wallH: cmPat.wall.height, body: cmBody, units: cmPat.units },
    cmPat: cmPat,
    mosaic: {
      file: mosaicPat.tile.mosaicFile,
      preview: mosaicPat.tile.mosaicPreview,
      sheetW: sheetBox.w,
      sheetH: sheetBox.h,
      pitch: sheetNext ? sheetNext.x - sheet.x : null,
      verts: sheet.verts.length,
      piece: piece,
      subW: mosaicPat.tile.subW,
      subGr: mosaicPat.tile.subGr
    },
    mosaicPat: mosaicPat
  };
});

await browser.close();

function write(name, obj) {
  const file = path.join(outDir, name);
  fs.writeFileSync(file, JSON.stringify(obj, null, 2));
  const hash = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  return { name: name, hash: hash };
}
const written = [
  write('square-voids-multi.layit', report.voidPat),
  write('square-12in-entered-as-cm.layit', report.cmPat),
  write('mosaic-sheet-12-square-pieces.layit', report.mosaicPat)
];
const summary = {
  written: written,
  voidAdds: report.voidAdds,
  voidSummary: report.voidSummary,
  tileCount: report.tileCount,
  cutCount: report.cutCount,
  cm: report.cm,
  mosaic: report.mosaic
};
fs.writeFileSync(path.join(outDir, 'extra-fixture-invariants.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
