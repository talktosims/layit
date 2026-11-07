/**
 * Build the portable review zip from the real app, unzip it, and test that copy.
 * Not an iOS run. Not a hosted deploy.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const art = '/opt/cursor/artifacts';
const stage = '/tmp/layit-review-stage';
const unpacked = '/tmp/layit-review-unpacked';
fs.mkdirSync(art, { recursive: true });
fs.rmSync(stage, { recursive: true, force: true });
fs.mkdirSync(stage, { recursive: true });

const appFiles = ['index.html', 'manifest.json', 'sw.js', 'icon-192.png', 'icon-512.png', 'icon-layit.svg'];
for (const f of appFiles) fs.copyFileSync(path.join(root, f), path.join(stage, f));
fs.cpSync(path.join(root, 'tests/fixtures'), path.join(stage, 'fixtures'), { recursive: true });
fs.cpSync(path.join(root, 'tests/evidence'), path.join(stage, 'screenshots'), { recursive: true });

const review = `LayIt review build
Geometry code commit: 998142ff3ee360a8cd055e2d834be891035298d0
Branch: cursor/layit-app-audit-fixes-1c7b

This zip is the real index.html app, not a mock UI.

How to open
1. Unzip.
2. Open index.html in Chrome (file:// is enough). No server and no install.
3. Layout, tile size, grout, save, and Download full layout (.layit) run locally.
4. Fixtures and GEOMETRY_SEMANTICS.md are in fixtures/.

Limits
- Not iOS, not WKWebView, not a laser.
- file:// does not register the service worker. manifest.json warns on file://. Ignore both.
- Firebase (barcode, cloud) needs network and is not part of this check. Layout does not need it.
- hardwareCompile is false. The .layit download does not turn a laser on.
- Do not host this publicly and do not merge from this package.
- Saved projects are not rewritten. Stagger stays odd-row / odd-column.
- Compiler: clip verts once. Do not rebuild shapes. Do not apply the old 11.875 / half-hex compensation.
`;
fs.writeFileSync(path.join(stage, 'REVIEW.txt'), review);

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

const genBrowser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});
const genPage = await genBrowser.newPage();
await genPage.goto('file://' + path.join(stage, 'index.html'), { waitUntil: 'domcontentloaded', timeout: 20000 });
await genPage.waitForFunction(() => typeof buildLayItPattern === 'function');
const hex10 = await genPage.evaluate(() => {
  C.polygon = [{ x: 0, y: 0 }, { x: 80, y: 0 }, { x: 80, y: 80 }, { x: 0, y: 80 }];
  C.wall = { lH: 80, rV: 0, tW: 80, bV: 0 };
  C.voids = [];
  C.tile = { sh: 'hexagon', or: 'pointy', w: 10, h: 10, gr: 0.125, pattern: 0 };
  C.view.oxInches = 20;
  C.view.oyInches = 20;
  C.view.z = 4;
  const pat = buildLayItPattern();
  function bbox(verts) {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    verts.forEach(function(p) {
      minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
      minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
    });
    return { minX, maxX, minY, maxY, w: maxX - minX, h: maxY - minY };
  }
  var full = null, right = null, below = null;
  for (var i = 0; i < pat.tiles.length; i++) {
    var t = pat.tiles[i];
    if (t.isCut || ((t.row % 2 + 2) % 2) !== 0) continue;
    var r = null, d = null;
    for (var j = 0; j < pat.tiles.length; j++) {
      var u = pat.tiles[j];
      if (u.row === t.row && u.col === t.col + 1) r = u;
      if (u.col === t.col && u.row === t.row + 1) d = u;
    }
    if (r && d) { full = t; right = r; below = d; break; }
  }
  const b = bbox(full.verts);
  const shoulder = full.verts.filter(function(p) { return Math.abs(p[0] - (full.x + 5)) < 1e-6; });
  return {
    pat: pat,
    width: b.w,
    height: b.h,
    col: right.x - full.x,
    row: below ? Math.abs(below.y - full.y) : null,
    shoulders: shoulder.length,
    topIsUp: Math.max.apply(null, full.verts.map(function(p) { return p[1]; })) > full.y,
    ready: pat.hardwareReadyArtifact,
    purchase: pat.purchaseUsd
  };
});
if (Math.abs(hex10.width - 10) > 1e-9 || Math.abs(hex10.height - 10) > 1e-9) throw new Error('10x10 hex extent ' + hex10.width + 'x' + hex10.height);
if (Math.abs(hex10.col - 10.125) > 1e-9) throw new Error('10x10 column step ' + hex10.col);
if (Math.abs(hex10.row - 7.625) > 1e-9) throw new Error('10x10 row step ' + hex10.row);
if (hex10.shoulders < 2 || !hex10.topIsUp) throw new Error('10x10 shoulders/y ' + JSON.stringify(hex10));
if (hex10.ready !== false || hex10.purchase !== 0) throw new Error('safety flags');
const hexPath = path.join(stage, 'fixtures/hex-pointy-10x10-grout-eighth.layit');
fs.writeFileSync(hexPath, JSON.stringify(hex10.pat, null, 2));
fs.copyFileSync(hexPath, path.join(root, 'tests/fixtures/hex-pointy-10x10-grout-eighth.layit'));
await genBrowser.close();
console.log('generated 10x10 fixture', hex10.width, hex10.col, hex10.row);
const hashes = [];
function walk(dir, base) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    if (fs.statSync(p).isDirectory()) walk(p, base);
    else hashes.push(sha256(p) + '  ' + path.relative(base, p));
  }
}
walk(stage, stage);
hashes.sort();
fs.writeFileSync(path.join(stage, 'SHA256SUMS.txt'), hashes.join('\n') + '\n');

const fixtureZip = path.join(art, 'layit-fixtures-qa2.zip');
const appZip = path.join(art, 'layit-review-app-qa2.zip');
execSync(`rm -f ${JSON.stringify(fixtureZip)} ${JSON.stringify(appZip)}`);
execSync(`cd ${JSON.stringify(stage)} && zip -q -r ${JSON.stringify(fixtureZip)} fixtures REVIEW.txt SHA256SUMS.txt`);
execSync(`cd ${JSON.stringify(stage)} && zip -q -r ${JSON.stringify(appZip)} .`);

fs.rmSync(unpacked, { recursive: true, force: true });
fs.mkdirSync(unpacked);
execSync(`unzip -q ${JSON.stringify(appZip)} -d ${JSON.stringify(unpacked)}`);
const unpackedHtml = path.join(unpacked, 'index.html');
if (sha256(unpackedHtml) !== sha256(path.join(root, 'index.html'))) {
  throw new Error('unzipped index.html does not match the repo app');
}

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
const dialogs = [];
page.on('dialog', (d) => { dialogs.push(d.message()); return d.accept(); });
const pageErrors = [];
page.on('pageerror', (e) => pageErrors.push(String(e)));
await page.goto('file://' + unpackedHtml, { waitUntil: 'domcontentloaded', timeout: 20000 });
await page.waitForFunction(() => typeof buildLayItPattern === 'function');

await page.evaluate(() => {
  var hexH = 10 * 2 / Math.sqrt(3);
  var config = {
    wall: { lH: 80, rV: 0, tW: 80, bV: 0 },
    polygon: [{ x: 0, y: 0 }, { x: 80, y: 0 }, { x: 80, y: 80 }, { x: 0, y: 80 }],
    tile: { sh: 'hexagon', or: 'pointy', w: 10, h: hexH, gr: 0.125, pattern: 0 },
    voids: [],
    view: { z: 5, ox: 0, oy: 0, oxInches: 20, oyInches: 20 }
  };
  var project = {
    id: 'proj_old_1', name: 'Old Hex', config: config,
    cutTileStates: {}, patternLocked: false,
    groutColor: '#ffffff', tileColor: '#4CAF50', tileStroke: '#2E7D32',
    savedAt: 1700000000000
  };
  var projects = {};
  projects[project.id] = project;
  localStorage.setItem('tileProjects', JSON.stringify(projects));
  localStorage.setItem('layit_autosave', JSON.stringify({
    C: config, cutTileStates: {}, patternLocked: false, savedPatternPosition: null, timestamp: Date.now()
  }));
});
await page.reload({ waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => typeof buildLayItPattern === 'function' && C && C.tile && C.tile.w === 10);

const restored = await page.evaluate(() => {
  function bbox(verts) {
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    verts.forEach(function(p) {
      minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
      minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
    });
    return { w: maxX - minX, h: maxY - minY };
  }
  var stored = JSON.parse(localStorage.getItem('tileProjects')).proj_old_1;
  var pat = buildLayItPattern();
  var even = null, odd = null;
  for (var i = 0; i < pat.tiles.length && !odd; i++) {
    var t = pat.tiles[i];
    if (((t.row % 2 + 2) % 2) !== 0) continue;
    for (var j = 0; j < pat.tiles.length; j++) {
      var u = pat.tiles[j];
      if (u.col === t.col && u.row === t.row + 1) { even = t; odd = u; break; }
    }
  }
  var fullTile = pat.tiles.find(function(t) { return !t.isCut; });
  document.getElementById('projName').value = '   ';
  saveCurrentProject();
  var beforeW = C.tile.w;
  document.getElementById('tileShape').value = 'square';
  document.getElementById('nominalMode').checked = false;
  setLengthInputValue('tileW', 0);
  setLengthInputValue('tileH', 0);
  updateTile();
  return {
    storedW: stored.config.tile.w,
    storedPattern: stored.config.tile.pattern,
    storedOx: stored.config.view.oxInches,
    liveW: C.tile.w,
    livePattern: C.tile.pattern,
    liveOx: C.view.oxInches,
    select: document.getElementById('tilePattern').value,
    shift: odd.x - even.x,
    body: bbox(fullTile.verts),
    revision: pat.compiler.geometryRevision,
    noLegacy: pat.compiler.doNotApplyLegacyCompensation,
    clip: pat.compiler.clipSuppliedVertices,
    rebuild: pat.compiler.rebuildShapes,
    laser: pat.laser,
    hw: pat.hardwareCompile,
    ready: pat.hardwareReadyArtifact,
    purchase: pat.purchaseUsd,
    frac: toFractionInches(3.875),
    zeroFrac: toFractionInches(0.02),
    afterBadUpdate: beforeW,
    stillW: C.tile.w
  };
});

const importResult = await page.evaluate(() => new Promise(function(resolve) {
  var before = C.tile.w;
  var input = document.getElementById('importFile');
  var payload = JSON.stringify({ type: 'layit-laser', version: '1.1', tile: { width: 1 } });
  var file = new File([payload], 'pattern.layit', { type: 'application/json' });
  var dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
  setTimeout(function() { resolve({ before: before, after: C.tile.w }); }, 400);
}));

await page.screenshot({ path: path.join(art, 'artifact-restored-hex.png') });
await browser.close();

check('artifact restored stored width 10', restored.storedW === 10 && restored.liveW === 10, JSON.stringify(restored));
check('artifact kept pattern 0 and offset 20', restored.storedPattern === 0 && restored.livePattern === 0 && restored.liveOx === 20 && restored.select === '0');
check('artifact did not flip stagger', Math.abs(restored.shift - 10.125 / 2) < 1e-6, String(restored.shift));
check('artifact draws patent 10 in hex body', Math.abs(restored.body.w - 10) < 1e-6, JSON.stringify(restored.body));
check('artifact flags clip-once and no legacy compensation', restored.revision === '1.1-patent-7.2' && restored.noLegacy === true && restored.clip === true && restored.rebuild === false && restored.laser === 'off' && restored.hw === false && restored.ready === false && restored.purchase === 0);
check('blank project name does not save', dialogs.some(function(m) { return m.indexOf('project name') >= 0; }), dialogs.join(' | '));
check('zero tile size does not replace the restored tile', restored.stillW === 10, String(restored.stillW));
check('laser file import does not replace the open project', importResult.before === 10 && importResult.after === 10);
const realErrors = pageErrors.filter(function(e) { return e.indexOf('ServiceWorker') < 0; });
check('artifact page has no script errors besides file:// worker', realErrors.length === 0, realErrors.join(' | '));

const summary = {
  geometryCommit: '998142ff3ee360a8cd055e2d834be891035298d0',
  fixtureZip: fixtureZip,
  appZip: appZip,
  fixtureZipSha256: sha256(fixtureZip),
  appZipSha256: sha256(appZip),
  layit: {
    'square-12in-grout-eighth.layit': sha256(path.join(unpacked, 'fixtures/square-12in-grout-eighth.layit')),
    'hex-pointy-10in-regular.layit': sha256(path.join(unpacked, 'fixtures/hex-pointy-10in-regular.layit')),
    'herringbone-4x8-grout-eighth.layit': sha256(path.join(unpacked, 'fixtures/herringbone-4x8-grout-eighth.layit'))
  },
  failures: failures
};
fs.writeFileSync(path.join(art, 'layit-artifact-test-result.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
if (failures.length) process.exit(1);
