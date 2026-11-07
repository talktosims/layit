/**
 * Reproduce a Grok-style preview: sandboxed iframe, scripts allowed,
 * same-origin and storage denied. Also checks a normal file:// page still persists.
 * This is not iOS/WKWebView.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';

const htmlPath = process.argv[2] || path.join(path.resolve(path.dirname(new URL(import.meta.url).pathname), '..'), 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
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

const sandboxPage = await browser.newPage();
const sandboxErrors = [];
sandboxPage.on('pageerror', (e) => sandboxErrors.push(String(e)));
await sandboxPage.setContent('<iframe id="preview" sandbox="allow-scripts" style="width:390px;height:700px;border:0"></iframe>', { waitUntil: 'domcontentloaded' });
await sandboxPage.evaluate((src) => {
  document.getElementById('preview').srcdoc = src;
}, html);
const frame = await new Promise((resolve, reject) => {
  const start = Date.now();
  const timer = setInterval(() => {
    const found = sandboxPage.frames().find((f) => f !== sandboxPage.mainFrame());
    if (found) { clearInterval(timer); resolve(found); }
    else if (Date.now() - start > 8000) { clearInterval(timer); reject(new Error('no child frame')); }
  }, 50);
});
await frame.waitForFunction(() => typeof buildLayItPattern === 'function' && typeof layitStore !== 'undefined', { timeout: 15000 });
const sand = await frame.evaluate(() => {
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
  const pat = buildLayItPattern();
  const tile = pat.tiles.find((t) => !t.isCut) || pat.tiles[0];
  let minX = Infinity, maxX = -Infinity;
  tile.verts.forEach((p) => { minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]); });
  document.getElementById('projName').value = 'Preview Job';
  saveCurrentProject();
  const projects = getProjects();
  const notice = document.getElementById('storageNotice');
  const status = document.getElementById('saveStatus') ? document.getElementById('saveStatus').textContent : '';
  return {
    persistent: layitStore.persistent(),
    pro: isProUser(),
    hw: pat.hardwareCompile,
    ready: pat.hardwareReadyArtifact,
    sim: pat.simulationOnly,
    laser: pat.laser,
    body: maxX - minX,
    tiles: pat.tiles.length,
    projectKept: !!(projects && Object.keys(projects).some((id) => projects[id].name === 'Preview Job')),
    notice: notice ? notice.textContent : '',
    status: status,
    full: full,
    part: part
  };
});

const normal = await browser.newPage();
const normalErrors = [];
normal.on('pageerror', (e) => normalErrors.push(String(e)));
await normal.goto('file://' + htmlPath, { waitUntil: 'domcontentloaded' });
await normal.waitForFunction(() => typeof layitStore !== 'undefined');
const disk = await normal.evaluate(() => {
  document.getElementById('projName').value = 'Disk Job';
  saveCurrentProject();
  return {
    persistent: layitStore.persistent(),
    notice: !!document.getElementById('storageNotice'),
    raw: window['local' + 'Storage'].getItem('tileProjects') || ''
  };
});
await browser.close();

check('sandbox page boots', sand && sand.tiles > 0, JSON.stringify(sand));
check('sandbox storage is not persistent', sand.persistent === false);
check('sandbox does not grant Pro', sand.pro === false);
check('sandbox export stays fail-closed', sand.hw === false && sand.ready === false && sand.sim === true && sand.laser === 'off');
check('sandbox layout body is 12 in', Math.abs(sand.body - 12) < 1e-6, String(sand.body));
check('sandbox save does not claim device storage', sand.projectKept === true && sand.notice.indexOf('cannot store') >= 0 && sand.status.indexOf('Not saved') >= 0, sand.status + ' | ' + sand.notice);
check('sandbox has no localStorage crash', sandboxErrors.every((e) => e.indexOf('localStorage') < 0 && e.indexOf('ServiceWorker') < 0), sandboxErrors.join(' | '));
check('normal file page still persists projects', disk.persistent === true && disk.raw.indexOf('Disk Job') >= 0 && disk.notice === false, JSON.stringify(disk));
check('normal file page has no storage crash', normalErrors.every((e) => e.indexOf('localStorage') < 0), normalErrors.join(' | '));

if (failures.length) {
  console.error('FAILED');
  failures.forEach((f) => console.error(' - ' + f));
  process.exit(1);
}
console.log('sandbox preview passed for', htmlPath);
