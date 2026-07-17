import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const indexPath = new URL('../index.html', import.meta.url);
const html = await readFile(indexPath);
const server = createServer((request, response) => {
  const pathname = new URL(request.url, 'http://localhost').pathname;
  if (pathname === '/' || pathname === '/index.html') {
    response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    response.end(html);
    return;
  }
  response.writeHead(404);
  response.end();
});

await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const { port } = server.address();
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ serviceWorkers: 'block' });
const page = await context.newPage();
const pageErrors = [];
page.on('pageerror', (error) => pageErrors.push(error.message));

try {
  await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'load' });

  const savedProjects = [{ id: 'keep-me', name: 'Customer shower' }];
  await page.evaluate(({ savedProjects }) => {
    localStorage.setItem('layit_projects', JSON.stringify(savedProjects));
    localStorage.setItem('layit_build_seed', 'an-older-build');
    localStorage.setItem('layit_onboarded', '1');
    localStorage.setItem('layit_autosave', JSON.stringify({
      C: {
        wall: { lH: 96, rV: 0, tW: 123, bV: 0 },
        tile: { sh: 'rectangle', or: 'flat', w: 3, h: 12, gr: 0.125, pattern: 0.5 },
        voids: [],
        view: { z: 4, ox: 0, oy: 0 },
      },
      cutTileStates: {},
      patternLocked: false,
      savedPatternPosition: null,
      timestamp: Date.now() - (30 * 24 * 60 * 60 * 1000),
    }));
  }, { savedProjects });

  await page.reload({ waitUntil: 'load' });
  await page.waitForTimeout(300);

  assert.deepEqual(
    JSON.parse(await page.evaluate(() => localStorage.getItem('layit_projects'))),
    savedProjects,
    'an app update must not delete saved projects',
  );
  assert.equal(
    await page.evaluate(() => C.wall.tW),
    123,
    'autosave older than seven days must still restore',
  );
  assert.equal(
    await page.evaluate(() => localStorage.getItem('layit_data_schema_version')),
    '1',
    'the non-destructive data schema marker should be present',
  );

  await page.evaluate(() => {
    window._nativeApp = true;
    setSubscriptionProducts([
      { id: 'layit.pro.annual', displayPrice: '£34.99', periodLabel: 'year' },
      { id: 'layit.pro.monthly', displayPrice: '£4.49', periodLabel: 'month' },
    ]);
    showUpgradeModal();
  });

  assert.equal(await page.locator('#proAnnualPrice').textContent(), '£34.99/year');
  assert.equal(await page.locator('#proMonthlyPrice').textContent(), '£4.49/month');
  assert.match(await page.locator('#proSubscribeButtons').innerText(), /auto-renewable subscription/i);
  assert.match(await page.locator('#proSubscribeButtons').innerText(), /renews automatically/i);
  await assertLegalLink(page, 'https://layit.pages.dev/terms');
  await assertLegalLink(page, 'https://layit.pages.dev/privacy');

  assert.equal(await page.locator('#proManageBtn').textContent(), 'Manage Subscription');
  assert.equal(await page.locator('script[src]').count(), 0, 'release must not load remote scripts');
  assert.equal(await page.locator('canvas:not([aria-label])').count(), 0, 'every canvas needs an accessible label');
  assert.equal(await page.locator('.tab[data-tab="laser"]').count(), 0, 'unfinished Laser UI must not ship');
  assert.deepEqual(pageErrors, [], `page errors: ${pageErrors.join('; ')}`);

  console.log('LayIt release smoke test passed');
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}

async function assertLegalLink(page, href) {
  const link = page.locator(`a[href="${href}"]`).first();
  assert.equal(await link.getAttribute('href'), href);
  assert.match(await link.getAttribute('onclick'), /openLayItLegalLink/);
}
