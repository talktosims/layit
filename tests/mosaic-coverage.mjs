/**
 * Mosaic export must say sheet-outlines-only and that F1 is not satisfied.
 * Regenerates only mosaic-sheet-12-square-pieces.layit. Other fixture bytes stay.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fixturePath = path.join(root, 'tests/fixtures/mosaic-sheet-12-square-pieces.layit');
const prior = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
const failures = [];
function check(name, cond, detail) {
  if (!cond) failures.push(name + (detail ? ': ' + detail : ''));
  else console.log('ok', name);
}
function sha(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }

const stable = [
  'square-12in-grout-eighth.layit',
  'hex-pointy-10x10-grout-eighth.layit',
  'hex-pointy-10in-regular.layit',
  'herringbone-4x8-grout-eighth.layit',
  'square-voids-multi.layit',
  'square-12in-entered-as-cm.layit'
];
const before = {};
stable.forEach(function(name) {
  before[name] = sha(fs.readFileSync(path.join(root, 'tests/fixtures', name)));
});

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});
const page = await browser.newPage();
await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => typeof buildLayItPattern === 'function');

const out = await page.evaluate(() => {
  document.getElementById('tileShape').value = 'square';
  onShape();
  const square = buildLayItPattern();
  const squareLimit = document.getElementById('layitExportLimit').style.display;
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
  const mosaic = buildLayItPattern();
  return {
    squareReq: square.requirement,
    squareCoverage: square.coverage || null,
    squarePiece: square.tile.pieceGroutInFile,
    limitShown: document.getElementById('layitExportLimit').style.display,
    limitText: document.getElementById('layitExportLimit').textContent,
    squareLimit: squareLimit,
    mosaic: mosaic
  };
});
await browser.close();

const fresh = out.mosaic;
check('square export still claims F1 and has no mosaic coverage block', out.squareReq === 'F1-full-layout' && out.squareCoverage === null && out.squarePiece !== false);
check('mosaic requirement is not an F1 pass', fresh.requirement === 'F1-full-layout-not-satisfied' && fresh.requirement !== 'F1-full-layout');
check('coverage says sheet outlines and piece grout is absent', fresh.coverage && fresh.coverage.polygons === 'sheet-outlines-only' && fresh.coverage.pieceGroutInFile === false && fresh.coverage.f1FullLayoutSatisfied === false && fresh.coverage.unmetRequirement === 'F1-full-layout');
check('tile flag matches the coverage block', fresh.tile.pieceGroutInFile === false && fresh.tile.mosaicFile === 'sheet-outlines');
check('export limitation is visible only for mosaic', out.squareLimit === 'none' && out.limitShown === 'block' && out.limitText.indexOf('Individual mosaic piece grout is not exported or projected') >= 0, out.limitText);
check('hardware flags stay closed', fresh.hardwareCompile === false && fresh.hardwareReadyArtifact === false && fresh.laser === 'off' && fresh.purchaseUsd === 0 && fresh.simulationOnly === true);

function body(tile) {
  const copy = Object.assign({}, tile);
  delete copy.pieceGroutInFile;
  return copy;
}
check('sheet identity matches the prior fixture', JSON.stringify(body(fresh.tile)) === JSON.stringify(body(prior.tile)));
check('sheet polygons match the prior fixture', JSON.stringify(fresh.tiles) === JSON.stringify(prior.tiles));
check('wall, placement, and voids match the prior fixture', JSON.stringify(fresh.wall) === JSON.stringify(prior.wall) && JSON.stringify(fresh.placement) === JSON.stringify(prior.placement) && JSON.stringify(fresh.voids) === JSON.stringify(prior.voids));
check('no piece vertices were added', fresh.tiles.every(function(t) { return t.verts.length === 4; }) && fresh.tiles.length === prior.tiles.length);

fs.writeFileSync(fixturePath, JSON.stringify(fresh, null, 2));
const next = sha(fs.readFileSync(fixturePath));
const priorHash = '1bb5710bc887a53b1c306645673894735ef5c0147e8cd6b0ebfdf8e808b402cb';
check('mosaic fixture hash changed because the coverage fields changed', next !== priorHash, next);
stable.forEach(function(name) {
  const got = sha(fs.readFileSync(path.join(root, 'tests/fixtures', name)));
  check(name + ' bytes unchanged', got === before[name], got);
});

console.log(JSON.stringify({ mosaicHash: next, tiles: fresh.tiles.length, requirement: fresh.requirement, coverage: fresh.coverage }, null, 2));
if (failures.length) {
  console.error('FAILED');
  failures.forEach(function(f) { console.error(' - ' + f); });
  process.exit(1);
}
console.log('mosaic coverage passed');
