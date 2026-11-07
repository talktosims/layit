/**
 * Walk the in-app guided tour. Speech events here are not audible proof.
 * Not iOS. Does not save, export, buy, or open the camera.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const art = '/opt/cursor/artifacts';
fs.mkdirSync(art, { recursive: true });
const failures = [];
function check(name, cond, detail) {
  if (!cond) failures.push(name + (detail ? ': ' + detail : ''));
  else console.log('ok', name);
}
function sha(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/local/bin/google-chrome',
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage']
});

async function openPage(width, height) {
  const page = await browser.newPage();
  await page.setViewport({ width: width, height: height });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof startLayitTour === 'function' && Array.isArray(LAYIT_TOUR_STEPS));
  return { page: page, errors: errors };
}

function overlap(a, b) {
  const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
  const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
  return w > 1 && h > 1;
}

const desktop = await openPage(1280, 800);
const page = desktop.page;
const before = await page.evaluate(() => ({
  name: document.getElementById('projName').value,
  w: document.getElementById('tileW').value,
  shape: document.getElementById('tileShape').value,
  c: JSON.stringify(C),
  cuts: JSON.stringify(cutTileStates)
}));
await page.click('#startGuidedTourBtn');
await page.waitForFunction(() => layitTourActive === true);
const steps = await page.evaluate(() => LAYIT_TOUR_STEPS.map((s) => ({ chapter: s.chapter, title: s.title, say: s.say, target: s.target, tab: s.tab, optional: !!s.optional })));
const seen = [];
for (let i = 0; i < steps.length; i++) {
  await new Promise((r) => setTimeout(r, 120));
  const row = await page.evaluate(() => {
    const step = LAYIT_TOUR_STEPS[layitTourIndex];
    const target = document.querySelector(step.target);
    const dock = document.getElementById('layitTourDock').getBoundingClientRect();
    const ring = document.getElementById('layitTourRing').getBoundingClientRect();
    const box = target ? target.getBoundingClientRect() : null;
    const style = target ? getComputedStyle(target) : null;
    return {
      index: layitTourIndex,
      title: document.getElementById('layitTourTitle').textContent,
      caption: document.getElementById('layitTourCaption').textContent,
      target: step.target,
      box: box ? { left: box.left, top: box.top, right: box.right, bottom: box.bottom, width: box.width, height: box.height } : null,
      ring: { left: ring.left, top: ring.top, right: ring.right, bottom: ring.bottom, width: ring.width, height: ring.height },
      dock: { left: dock.left, top: dock.top, right: dock.right, bottom: dock.bottom },
      shown: !!(style && style.display !== 'none' && style.visibility !== 'hidden'),
      inView: !!(box && box.bottom > 0 && box.top < window.innerHeight && box.right > 0 && box.left < window.innerWidth)
    };
  });
  seen.push(row);
  check('step ' + (i + 1) + ' target ' + steps[i].target, row.box && row.box.width > 2 && row.box.height > 2 && row.shown, JSON.stringify(row.box));
  check('step ' + (i + 1) + ' caption matches the script', row.caption === steps[i].say);
  check('step ' + (i + 1) + ' highlight is visible and clear of the dock', row.ring && row.ring.width > 20 && row.ring.height > 20 && row.ring.top >= -1 && row.ring.bottom <= 801 && !overlap(row.ring, row.dock), JSON.stringify({ ring: row.ring, dock: row.dock }));
  if (i === 0) await page.screenshot({ path: path.join(art, 'layit-tour-desktop.png') });
  if (i < steps.length - 1) await page.click('#layitTourNext');
}
check('tour walked every chapter', seen.length === steps.length, String(seen.length));
await page.click('#layitTourPrev');
const backTitle = await page.$eval('#layitTourTitle', (el) => el.textContent);
check('previous returns to the decorative step', backTitle === 'Decorative pieces', backTitle);
await page.click('#layitTourReplay');
const replayCaption = await page.$eval('#layitTourCaption', (el) => el.textContent);
check('replay keeps the same caption', replayCaption.indexOf('decorative pieces') >= 0, replayCaption.slice(0, 80));
await page.click('#layitTourPause');
const paused = await page.$eval('#layitTourVoice', (el) => el.textContent);
check('pause is labeled and is not a fake speaking state', paused === 'Paused.', paused);
await page.click('#layitTourPause');
await page.click('#layitTourEnd');
const closed = await page.evaluate(() => document.getElementById('layitTourDock').style.display === 'none' && layitTourActive === false);
check('end closes the tour', closed);
await page.evaluate(() => {
  showTab('settings');
  document.getElementById('replayGuidedTourBtn').click();
});
await page.waitForFunction(() => layitTourActive === true);
await page.keyboard.press('Escape');
const reclosed = await page.evaluate(() => layitTourActive === false);
check('escape ends a replay', reclosed);
const after = await page.evaluate(() => ({
  name: document.getElementById('projName').value,
  w: document.getElementById('tileW').value,
  shape: document.getElementById('tileShape').value,
  c: JSON.stringify(C),
  cuts: JSON.stringify(cutTileStates),
  tab: (document.querySelector('.panel.active') || {}).id
}));
check('project state is unchanged', before.name === after.name && before.w === after.w && before.shape === after.shape && before.c === after.c && before.cuts === after.cuts, after.tab);
const desktopErrors = desktop.errors.filter(function(e) { return e.indexOf('ServiceWorker') < 0; });
check('no script errors during the tour', desktopErrors.length === 0, desktopErrors.join(' | '));

const phone = await openPage(390, 844);
await phone.page.click('#startGuidedTourBtn');
await phone.page.waitForFunction(() => layitTourActive === true);
await new Promise((r) => setTimeout(r, 150));
const phoneRow = await phone.page.evaluate(() => {
  const step = LAYIT_TOUR_STEPS[0];
  const target = document.querySelector(step.target);
  const box = target.getBoundingClientRect();
  const dock = document.getElementById('layitTourDock').getBoundingClientRect();
  const next = document.getElementById('layitTourNext').getBoundingClientRect();
  return { box: { left: box.left, top: box.top, right: box.right, bottom: box.bottom, width: box.width, height: box.height }, dock: { top: dock.top, bottom: dock.bottom, left: dock.left, right: dock.right }, next: { top: next.top, bottom: next.bottom }, vh: window.innerHeight, caption: document.getElementById('layitTourCaption').textContent.length };
});
check('phone target is visible and clear of the dock', phoneRow.box.width > 2 && phoneRow.box.height > 2 && !overlap(phoneRow.box, phoneRow.dock) && phoneRow.caption > 20, JSON.stringify(phoneRow));
check('phone Next control is on screen', phoneRow.next.top >= 0 && phoneRow.next.bottom <= phoneRow.vh + 1, JSON.stringify(phoneRow.next));
await phone.page.screenshot({ path: path.join(art, 'layit-tour-phone.png') });
const phoneErrors = phone.errors.filter(function(e) { return e.indexOf('ServiceWorker') < 0; });
check('phone tour has no script errors', phoneErrors.length === 0, phoneErrors.join(' | '));

const denied = await openPage(1000, 700);
await denied.page.evaluate(() => {
  window.speechSynthesis = { speak: function() { throw new Error('blocked'); }, cancel: function() {}, getVoices: function() { return []; }, pause: function() {}, resume: function() {}, addEventListener: function() {} };
});
await denied.page.click('#startGuidedTourBtn');
await denied.page.waitForFunction(() => (document.getElementById('layitTourVoice').textContent || '').indexOf('available') >= 0);
const deniedText = await denied.page.$eval('#layitTourVoice', (el) => el.textContent);
const deniedCaption = await denied.page.$eval('#layitTourCaption', (el) => el.textContent.length);
check('blocked speech stays readable and does not claim it is speaking', deniedText.indexOf('isn\'t available') >= 0 && deniedText.indexOf('Speaking') < 0 && deniedCaption > 20, deniedText);

const sandboxPage = await browser.newPage();
const sandboxErrors = [];
sandboxPage.on('pageerror', (e) => sandboxErrors.push(String(e)));
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
await sandboxPage.setContent('<iframe id="preview" sandbox="allow-scripts" style="width:390px;height:700px;border:0"></iframe>', { waitUntil: 'domcontentloaded' });
await sandboxPage.evaluate((src) => { document.getElementById('preview').srcdoc = src; }, html);
const frame = await new Promise((resolve, reject) => {
  const start = Date.now();
  const timer = setInterval(() => {
    const found = sandboxPage.frames().find((f) => f !== sandboxPage.mainFrame());
    if (found) { clearInterval(timer); resolve(found); }
    else if (Date.now() - start > 8000) { clearInterval(timer); reject(new Error('no frame')); }
  }, 40);
});
await frame.waitForFunction(() => typeof startLayitTour === 'function', { timeout: 15000 });
const sand = await frame.evaluate(() => {
  const beforeC = JSON.stringify(C);
  startLayitTour();
  layitTourNext();
  const caption = document.getElementById('layitTourCaption').textContent;
  layitTourEnd();
  return { caption: caption, same: JSON.stringify(C) === beforeC, active: layitTourActive, persistent: layitStore.persistent() };
});
check('sandboxed preview can start and end the tour without changing the layout', sand.same && sand.active === false && sand.caption.length > 20 && sand.persistent === false, JSON.stringify(sand));
check('sandboxed tour has no script errors', sandboxErrors.length === 0, sandboxErrors.join(' | '));

const locked = {
  'square-12in-grout-eighth.layit': '6c2bd142c50bcdd138c26ed63655c5bb455bd42356bfde95d08a060247c93f9c',
  'hex-pointy-10x10-grout-eighth.layit': '86e80cad414d1479cc690ac67919c4fdbe6b1a612ad823f58e779e15db85de96',
  'herringbone-4x8-grout-eighth.layit': '9b622ca85d3ff2e267cf012c38430aec8dc6eac193051235ac1ad9e834c16fab',
  'square-voids-multi.layit': '51c69676e3cec76d663dfaab5244178d9a25aae57d7becfdd4a31cc59a0c0941',
  'mosaic-sheet-12-square-pieces.layit': '5fd0f66f8155266f005e9c89d8e73fecb4c79612dff95e6a45eed3e6fac0f001',
  'square-12in-entered-as-cm.layit': '6c2bd142c50bcdd138c26ed63655c5bb455bd42356bfde95d08a060247c93f9c'
};
Object.keys(locked).forEach(function(name) {
  const got = sha(path.join(root, 'tests/fixtures', name));
  check(name + ' unchanged', got === locked[name], got);
});

fs.writeFileSync(path.join(art, 'layit-tour-script.txt'), steps.map(function(s, i) {
  return (i + 1) + '. [' + s.chapter + '] ' + s.title + '\n' + s.say + '\n';
}).join('\n'));

await browser.close();
if (failures.length) {
  console.error('FAILED');
  failures.forEach(function(f) { console.error(' - ' + f); });
  process.exit(1);
}
console.log('guided tour passed', steps.length, 'steps');
