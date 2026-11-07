/**
 * Repeat-boundary clearances for the four decorative cases.
 * Chrome, real index.html. Not iOS. Does not rewrite .layit fixtures.
 */
import puppeteer from '/tmp/layit-probe/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
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
await page.goto('file://' + path.join(root, 'index.html'), { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => typeof draw === 'function');

const measured = await page.evaluate(() => {
  function cubic(p0, p1, p2, p3, t) {
    const u = 1 - t;
    return u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3;
  }
  function capture(shape, w, h, gr, wall) {
    const cmds = [];
    const names = ['beginPath', 'moveTo', 'lineTo', 'bezierCurveTo', 'quadraticCurveTo', 'closePath'];
    const saved = names.map(function(n) {
      const orig = cx[n];
      cx[n] = function() {
        cmds.push([n].concat(Array.prototype.slice.call(arguments)));
        return orig.apply(cx, arguments);
      };
      return [n, orig];
    });
    C.polygon = [{ x: 0, y: 0 }, { x: wall, y: 0 }, { x: wall, y: wall }, { x: 0, y: wall }];
    C.wall = { lH: wall, rV: 0, tW: wall, bV: 0 };
    C.voids = [];
    C.view.z = 10;
    C.view.oxInches = 1;
    C.view.oyInches = 1;
    C.tile = { sh: 'mosaic', or: 'pointy', w: 12, h: 12, gr: gr, pattern: 0, subShape: shape, subW: w, subH: h, subGr: gr };
    draw();
    saved.forEach(function(pair) { cx[pair[0]] = pair[1]; });
    const paths = [];
    let cur = null, x = 0, y = 0, sx = 0, sy = 0;
    cmds.forEach(function(c) {
      if (c[0] === 'beginPath') { cur = []; paths.push(cur); return; }
      if (!cur) return;
      if (c[0] === 'moveTo') { x = c[1]; y = c[2]; sx = x; sy = y; cur.push([x, y]); }
      else if (c[0] === 'lineTo') { x = c[1]; y = c[2]; cur.push([x, y]); }
      else if (c[0] === 'bezierCurveTo') {
        const x0 = x, y0 = y;
        for (let k = 1; k <= 24; k++) {
          const t = k / 24;
          cur.push([cubic(x0, c[1], c[3], c[5], t), cubic(y0, c[2], c[4], c[6], t)]);
        }
        x = c[5]; y = c[6];
      } else if (c[0] === 'closePath') cur.push([sx, sy]);
    });
    const scale = 10;
    const bodies = paths.filter(function(p) { return p && p.length > 2; }).map(function(pts) {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      pts.forEach(function(p) {
        minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]);
        minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
      });
      return { pts: pts, cx: (minX + maxX) / 2 / scale, cy: (minY + maxY) / 2 / scale, w: (maxX - minX) / scale, h: (maxY - minY) / scale };
    }).filter(function(b) { return b.w > 0.4 && b.h > 0.4 && b.w < w * 2.2 && b.h < h * 2.2; });
    function segDist(a, b) {
      function pointSeg(px, py, x1, y1, x2, y2) {
        const vx = x2 - x1, vy = y2 - y1, l2 = vx * vx + vy * vy;
        let t = l2 ? ((px - x1) * vx + (py - y1) * vy) / l2 : 0;
        t = Math.max(0, Math.min(1, t));
        return Math.hypot(px - (x1 + t * vx), py - (y1 + t * vy));
      }
      let best = Infinity;
      for (let i = 0; i < a.pts.length - 1; i++) {
        for (let j = 0; j < b.pts.length - 1; j++) {
          const ax = a.pts[i][0], ay = a.pts[i][1], bx = a.pts[i + 1][0], by = a.pts[i + 1][1];
          const cx0 = b.pts[j][0], cy0 = b.pts[j][1], dx = b.pts[j + 1][0], dy = b.pts[j + 1][1];
          best = Math.min(best, pointSeg(ax, ay, cx0, cy0, dx, dy), pointSeg(cx0, cy0, ax, ay, bx, by));
        }
      }
      return best / scale;
    }
    const contacts = [];
    for (let i = 0; i < bodies.length; i++) {
      for (let j = i + 1; j < bodies.length; j++) {
        const dx = bodies[j].cx - bodies[i].cx;
        const dy = bodies[j].cy - bodies[i].cy;
        if (Math.hypot(dx, dy) > Math.max(w, h) * 2.2) continue;
        contacts.push({
          dx: +dx.toFixed(3),
          dy: +dy.toFixed(3),
          gap: +segDist(bodies[i], bodies[j]).toFixed(4),
          aw: +bodies[i].w.toFixed(4),
          ah: +bodies[i].h.toFixed(4)
        });
      }
    }
    function bucket(list) {
      const uniq = [];
      list.sort(function(a, b) { return a.gap - b.gap; });
      list.forEach(function(c) {
        if (!uniq.some(function(u) { return Math.abs(u.dx - c.dx) < 0.05 && Math.abs(u.dy - c.dy) < 0.05 && Math.abs(u.gap - c.gap) < 0.005; })) uniq.push(c);
      });
      return uniq.slice(0, 4);
    }
    const sheet = buildLayItPattern();
    return {
      shape: shape,
      n: bodies.length,
      body: bodies[0] ? [+bodies[0].w.toFixed(4), +bodies[0].h.toFixed(4)] : null,
      horiz: bucket(contacts.filter(function(c) { return Math.abs(c.dy) < 0.35; })),
      vert: bucket(contacts.filter(function(c) { return Math.abs(c.dx) < 0.35; })),
      diag: bucket(contacts.filter(function(c) { return Math.abs(c.dx) > 0.35 && Math.abs(c.dy) > 0.35; })),
      file: sheet.tile.mosaicFile,
      flags: [sheet.hardwareCompile, sheet.hardwareReadyArtifact, sheet.laser, sheet.purchaseUsd]
    };
  }
  return {
    tri: capture('triangle', 2, 2, 0.125, 16),
    arab: capture('arabesque', 2, 2, 0.125, 12),
    ogee: capture('ogee', 3.5, 6.5, 0.125, 18),
    star: capture('starcross', 8, 8, 0.125, 28),
    star16: capture('starcross', 8, 8, 0.0625, 28),
    label: (function() {
      document.getElementById('tileShape').value = 'mosaic';
      onShape();
      document.getElementById('subShape').value = 'triangle';
      onSubShapeChange();
      updateMosaicPieceSummary();
      return document.getElementById('mosaicPieceSummary').textContent;
    })()
  };
});
await browser.close();

function near(v, target, tol) { return Math.abs(v - target) <= tol; }
const triH = measured.tri.horiz;
check('triangle body is the entered 2 by 2 in', measured.tri.body && near(measured.tri.body[0], 2, 0.02) && near(measured.tri.body[1], 2, 0.02), JSON.stringify(measured.tri.body));
check('triangle rows are one entered grout apart', measured.tri.vert[0] && near(measured.tri.vert[0].gap, 0.125, 0.02), JSON.stringify(measured.tri.vert));
check('triangle pair edges stay apart on both horizontal repeats', triH.length >= 2 && triH.every(function(c) { return c.gap > 0.5; }), JSON.stringify(triH));
check('arabesque body width is the entered 2 in', measured.arab.body && near(measured.arab.body[0], 2, 0.03), JSON.stringify(measured.arab.body));
check('arabesque same-row joint is the entered grout', measured.arab.horiz[0] && near(measured.arab.horiz[0].gap, 0.125, 0.02), JSON.stringify(measured.arab.horiz));
check('ogee body is the entered 3.5 by 6.5 in', measured.ogee.body && near(measured.ogee.body[0], 3.5, 0.05) && near(measured.ogee.body[1], 6.5, 0.05), JSON.stringify(measured.ogee.body));
check('ogee nearest horizontal contact is one grout', measured.ogee.horiz[0] && near(measured.ogee.horiz[0].gap, 0.125, 0.02) && near(measured.ogee.horiz[0].dx, 3.625, 0.05), JSON.stringify(measured.ogee.horiz));
check('ogee offset-row miss is a few hundredths, not the entered grout', measured.ogee.diag[0] && measured.ogee.diag[0].gap > 0.02 && measured.ogee.diag[0].gap < 0.06, JSON.stringify(measured.ogee.diag));
check('star clearance at 1/8 in is recorded from the running app', measured.star.horiz[0] && measured.star.horiz[0].gap > 0, JSON.stringify(measured.star.horiz));
check('star clearance moves with the entered grout', measured.star16.horiz[0] && Math.abs(measured.star16.horiz[0].gap - measured.star.horiz[0].gap) > 0.01, JSON.stringify({ eighth: measured.star.horiz[0], sixteenth: measured.star16.horiz[0] }));
check('mosaic file remains sheet outlines and hardware stays closed', measured.tri.file === 'sheet-outlines' && measured.tri.flags[0] === false && measured.tri.flags[1] === false && measured.tri.flags[2] === 'off' && measured.tri.flags[3] === 0);
check('triangle summary does not claim the pointed edges are one grout apart', measured.label.indexOf('farther apart') >= 0, measured.label);

const locked = {
  'square-12in-grout-eighth.layit': '6c2bd142c50bcdd138c26ed63655c5bb455bd42356bfde95d08a060247c93f9c',
  'hex-pointy-10x10-grout-eighth.layit': '86e80cad414d1479cc690ac67919c4fdbe6b1a612ad823f58e779e15db85de96',
  'hex-pointy-10in-regular.layit': 'fa3a8ac20513f47cdc815ba99738fb36aad27c64fe2da495cce5c60d3dd56383',
  'herringbone-4x8-grout-eighth.layit': '9b622ca85d3ff2e267cf012c38430aec8dc6eac193051235ac1ad9e834c16fab',
  'square-voids-multi.layit': '51c69676e3cec76d663dfaab5244178d9a25aae57d7becfdd4a31cc59a0c0941',
  'mosaic-sheet-12-square-pieces.layit': '1bb5710bc887a53b1c306645673894735ef5c0147e8cd6b0ebfdf8e808b402cb',
  'square-12in-entered-as-cm.layit': '6c2bd142c50bcdd138c26ed63655c5bb455bd42356bfde95d08a060247c93f9c'
};
Object.keys(locked).forEach(function(name) {
  const got = crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'tests/fixtures', name))).digest('hex');
  check(name + ' bytes unchanged', got === locked[name], got);
});

console.log(JSON.stringify({ arabDiag: measured.arab.diag, ogeeDiag: measured.ogee.diag, star: measured.star.horiz[0], star16: measured.star16.horiz[0], label: measured.label }, null, 2));
if (failures.length) {
  console.error('FAILED');
  failures.forEach(function(f) { console.error(' - ' + f); });
  process.exit(1);
}
console.log('closure clearance passed');
