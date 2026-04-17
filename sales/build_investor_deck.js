const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "LayIt Laser";
pres.title = "LayIt Laser — Investor Deck";

// Brand colors
const BG = "0D1117";
const BG2 = "161B22";
const GREEN = "4CAF50";
const GREEN_DK = "2E7D32";
const WHITE = "FFFFFF";
const GRAY = "8B949E";
const GRAY_LT = "C9D1D9";
const CARD = "1C2128";

// Helpers
const mkShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.3 });

// ============================================================
// SLIDE 1 — TITLE
// ============================================================
let s1 = pres.addSlide();
s1.background = { color: BG };
// Green accent bar at top
s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s1.addText("LayIt", { x: 0.8, y: 1.2, w: 8.4, h: 1.2, fontSize: 72, fontFace: "Arial Black", color: GREEN, bold: true, margin: 0 });
s1.addText("Pattern Projection Platform", { x: 0.8, y: 2.3, w: 8.4, h: 0.7, fontSize: 28, fontFace: "Arial", color: WHITE, margin: 0 });
s1.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.2, w: 1.5, h: 0.04, fill: { color: GREEN } });
s1.addText("Your exact tile layout. Projected by laser. Guided by vision.", { x: 0.8, y: 3.5, w: 8, h: 0.5, fontSize: 16, fontFace: "Arial", color: GRAY, italic: true, margin: 0 });
s1.addText("Confidential — March 2026", { x: 0.8, y: 5.0, w: 8, h: 0.4, fontSize: 11, fontFace: "Arial", color: GRAY, margin: 0 });

// ============================================================
// SLIDE 2 — THE PROBLEM
// ============================================================
let s2 = pres.addSlide();
s2.background = { color: BG };
s2.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s2.addText("The Problem", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

s2.addText("$148 Billion", { x: 0.8, y: 1.3, w: 5, h: 0.8, fontSize: 48, fontFace: "Arial Black", color: GREEN, margin: 0 });
s2.addText("in surface installation markets still rely on chalk lines, tape measures, and eyeballing.", { x: 0.8, y: 2.0, w: 5.5, h: 0.8, fontSize: 18, fontFace: "Arial", color: GRAY_LT, margin: 0 });

// Problem stats - right side cards
const problems = [
  ["40%", "of a tile installer's time is spent measuring and cutting — not installing"],
  ["15-20%", "material waste from imprecise layouts (industry average)"],
  ["$0", "affordable laser layout tools exist for tile — until now"]
];
problems.forEach((p, i) => {
  const y = 1.3 + i * 1.3;
  s2.addShape(pres.shapes.RECTANGLE, { x: 6.2, y: y, w: 3.4, h: 1.1, fill: { color: CARD }, shadow: mkShadow() });
  s2.addShape(pres.shapes.RECTANGLE, { x: 6.2, y: y, w: 0.06, h: 1.1, fill: { color: GREEN } });
  s2.addText(p[0], { x: 6.5, y: y + 0.08, w: 3, h: 0.45, fontSize: 28, fontFace: "Arial Black", color: GREEN, margin: 0 });
  s2.addText(p[1], { x: 6.5, y: y + 0.5, w: 2.9, h: 0.5, fontSize: 10, fontFace: "Arial", color: GRAY, margin: 0 });
});

// ============================================================
// SLIDE 3 — THE SOLUTION
// ============================================================
let s3 = pres.addSlide();
s3.background = { color: BG };
s3.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s3.addText("The Solution", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

const solutions = [
  ["COMPUTE", "App calculates every tile position, cut dimension, and grout line for any pattern — herringbone, hex, brick, grid"],
  ["PROJECT", "200mW green laser projects the exact layout onto floors, walls, and ceilings with automatic keystone correction"],
  ["ALIGN", "On-board camera watches tiles as you place them — self-calibrates using placed tile edges, gets MORE precise over time"]
];
solutions.forEach((sol, i) => {
  const x = 0.8 + i * 3.05;
  s3.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.3, w: 2.8, h: 3.5, fill: { color: CARD }, shadow: mkShadow() });
  s3.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.3, w: 2.8, h: 0.06, fill: { color: GREEN } });
  s3.addText(sol[0], { x: x + 0.2, y: 1.6, w: 2.4, h: 0.5, fontSize: 22, fontFace: "Arial Black", color: GREEN, margin: 0 });
  s3.addText(sol[1], { x: x + 0.2, y: 2.2, w: 2.4, h: 2.3, fontSize: 13, fontFace: "Arial", color: GRAY_LT, margin: 0 });
});

// ============================================================
// SLIDE 4 — PRODUCT LINE
// ============================================================
let s4 = pres.addSlide();
s4.background = { color: BG };
s4.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s4.addText("Product Line", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

// Flagship card
s4.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.3, w: 4, h: 3.8, fill: { color: CARD }, shadow: mkShadow() });
s4.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.3, w: 4, h: 0.06, fill: { color: GREEN } });
s4.addText("LayIt Laser", { x: 1.1, y: 1.5, w: 3.5, h: 0.5, fontSize: 24, fontFace: "Arial Black", color: WHITE, margin: 0 });
s4.addText("FLAGSHIP", { x: 1.1, y: 1.95, w: 3.5, h: 0.3, fontSize: 12, fontFace: "Arial", color: GREEN, bold: true, margin: 0 });
s4.addText("$499", { x: 1.1, y: 2.3, w: 3.5, h: 0.6, fontSize: 40, fontFace: "Arial Black", color: GREEN, margin: 0 });
s4.addText([
  { text: "200mW green laser (Class 3B)", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Dual-axis galvanometer projection", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Auto-calibration camera (OV5640)", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "USB-C PD powered", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "WiFi + BLE connectivity", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "38-53% gross margin", options: { bullet: true, fontSize: 12, color: GREEN } }
], { x: 1.1, y: 3.0, w: 3.5, h: 2.0, fontFace: "Arial", margin: 0 });

// Pro card
s4.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 4, h: 3.8, fill: { color: CARD }, shadow: mkShadow() });
s4.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 4, h: 0.06, fill: { color: GREEN } });
s4.addText("LayIt Laser Pro", { x: 5.5, y: 1.5, w: 3.5, h: 0.5, fontSize: 24, fontFace: "Arial Black", color: WHITE, margin: 0 });
s4.addText("CORDLESS", { x: 5.5, y: 1.95, w: 3.5, h: 0.3, fontSize: 12, fontFace: "Arial", color: GREEN, bold: true, margin: 0 });
s4.addText("$649", { x: 5.5, y: 2.3, w: 3.5, h: 0.6, fontSize: 40, fontFace: "Arial Black", color: GREEN, margin: 0 });
s4.addText([
  { text: "Everything in Flagship, plus:", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT, bold: true } },
  { text: "Swappable 3S LiPo battery packs", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "2 batteries included (1.5-2hr each)", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Auto cord/battery switchover", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Battery level indicator", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "38-55% gross margin", options: { bullet: true, fontSize: 12, color: GREEN } }
], { x: 5.5, y: 3.0, w: 3.5, h: 2.0, fontFace: "Arial", margin: 0 });

// ============================================================
// SLIDE 5 — THE APP
// ============================================================
let s5 = pres.addSlide();
s5.background = { color: BG };
s5.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s5.addText("The App — Free + Pro", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

// Free tier
s5.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.3, w: 4, h: 3.8, fill: { color: CARD }, shadow: mkShadow() });
s5.addText("FREE", { x: 1.1, y: 1.5, w: 3.5, h: 0.4, fontSize: 20, fontFace: "Arial Black", color: WHITE, margin: 0 });
s5.addText("Included with every unit", { x: 1.1, y: 1.85, w: 3.5, h: 0.3, fontSize: 11, fontFace: "Arial", color: GRAY, margin: 0 });
s5.addText([
  { text: "Full tile layout tool", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "All patterns & shapes", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Wall/floor perimeter drawing", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Void/niche management", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Cut count + waste %", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Save/load projects locally", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Laser projection control", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "DXF / SVG / JSON export", options: { bullet: true, fontSize: 11, color: GRAY_LT } }
], { x: 1.1, y: 2.2, w: 3.5, h: 2.8, fontFace: "Arial", margin: 0 });

// Pro tier
s5.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 4, h: 3.8, fill: { color: GREEN_DK }, shadow: mkShadow() });
s5.addText("PRO — $14.99/mo", { x: 5.5, y: 1.5, w: 3.5, h: 0.4, fontSize: 20, fontFace: "Arial Black", color: WHITE, margin: 0 });
s5.addText("One price. No tiers.", { x: 5.5, y: 1.85, w: 3.5, h: 0.3, fontSize: 11, fontFace: "Arial", color: "A5D6A7", margin: 0 });
s5.addText([
  { text: "Barcode scanner + auto-populate", options: { bullet: true, breakLine: true, fontSize: 11, color: WHITE } },
  { text: "Cloud sync across devices", options: { bullet: true, breakLine: true, fontSize: 11, color: WHITE } },
  { text: "AI room scan (no LiDAR)", options: { bullet: true, breakLine: true, fontSize: 11, color: WHITE } },
  { text: "Project sharing with clients", options: { bullet: true, breakLine: true, fontSize: 11, color: WHITE } },
  { text: "Job cost tracking + invoicing", options: { bullet: true, breakLine: true, fontSize: 11, color: WHITE } },
  { text: "Priority support", options: { bullet: true, breakLine: true, fontSize: 11, color: WHITE } },
  { text: "Early access to new features", options: { bullet: true, fontSize: 11, color: WHITE } }
], { x: 5.5, y: 2.2, w: 3.5, h: 2.8, fontFace: "Arial", margin: 0 });

// ============================================================
// SLIDE 6 — REVENUE MODEL (6 streams)
// ============================================================
let s6 = pres.addSlide();
s6.background = { color: BG };
s6.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s6.addText("6 Revenue Streams", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

const streams = [
  ["Hardware Sales", "$499-649/unit\n40-55% margins", "5,000 units → $2.75M"],
  ["App Subscriptions", "$14.99/mo Pro tier\n40% conversion", "2,000 subs → $360K ARR"],
  ["DIY Rentals", "$49/weekend\n$99/week", "100 units → $120-240K/yr"],
  ["Union & Trade Schools", "$2.5-5K/yr licenses\nBulk member subs", "70 institutions → $369K/yr"],
  ["Fleet Program", "$399/unit bulk\n$7.99/seat + dashboard", "100 companies → $307K/yr"],
  ["Manufacturer Partners", "Featured listings\nData licensing", "10 brands → $200K/yr"]
];
streams.forEach((s, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.8 + col * 3.05;
  const y = 1.2 + row * 2.15;
  s6.addShape(pres.shapes.RECTANGLE, { x: x, y: y, w: 2.8, h: 1.9, fill: { color: CARD }, shadow: mkShadow() });
  s6.addShape(pres.shapes.RECTANGLE, { x: x, y: y, w: 2.8, h: 0.06, fill: { color: GREEN } });
  s6.addText(s[0], { x: x + 0.15, y: y + 0.15, w: 2.5, h: 0.35, fontSize: 14, fontFace: "Arial", color: GREEN, bold: true, margin: 0 });
  s6.addText(s[1], { x: x + 0.15, y: y + 0.5, w: 2.5, h: 0.7, fontSize: 11, fontFace: "Arial", color: GRAY_LT, margin: 0 });
  s6.addText(s[2], { x: x + 0.15, y: y + 1.3, w: 2.5, h: 0.4, fontSize: 11, fontFace: "Arial", color: GREEN, bold: true, italic: true, margin: 0 });
});

// ============================================================
// SLIDE 7 — REVENUE PROJECTIONS
// ============================================================
let s7 = pres.addSlide();
s7.background = { color: BG };
s7.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s7.addText("Year 3 Projections", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

// Big numbers
const bigNums = [
  ["$4.1-4.5M", "Total Revenue"],
  ["$1.4M+", "Recurring ARR"],
  ["$27-32M", "Valuation (15x ARR)"]
];
bigNums.forEach((n, i) => {
  const x = 0.8 + i * 3.05;
  s7.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.2, w: 2.8, h: 1.4, fill: { color: CARD }, shadow: mkShadow() });
  s7.addText(n[0], { x: x, y: 1.3, w: 2.8, h: 0.7, fontSize: 30, fontFace: "Arial Black", color: GREEN, align: "center", margin: 0 });
  s7.addText(n[1], { x: x, y: 2.0, w: 2.8, h: 0.4, fontSize: 12, fontFace: "Arial", color: GRAY, align: "center", margin: 0 });
});

// Revenue breakdown table
const tblHeader = [
  [
    { text: "Revenue Stream", options: { fill: { color: GREEN_DK }, color: WHITE, bold: true, fontSize: 11 } },
    { text: "Annual Revenue", options: { fill: { color: GREEN_DK }, color: WHITE, bold: true, fontSize: 11 } },
    { text: "Type", options: { fill: { color: GREEN_DK }, color: WHITE, bold: true, fontSize: 11 } }
  ]
];
const tblRows = [
  ["Hardware sales (5,000 units)", "$2.75M", "One-time"],
  ["App Pro subscriptions (2,000)", "$360K", "Recurring"],
  ["DIY rentals (100 units)", "$120-240K", "Recurring"],
  ["Union/trade school licensing", "$369K", "Recurring"],
  ["Contractor fleet program", "$307K", "Recurring"],
  ["Manufacturer partnerships", "$200K", "Recurring"]
].map(r => r.map(c => ({ text: c, options: { fill: { color: CARD }, color: GRAY_LT, fontSize: 10, border: [{ pt: 0.5, color: BG2 }] } })));

s7.addTable([...tblHeader, ...tblRows], { x: 0.8, y: 3.0, w: 8.4, colW: [4.2, 2.1, 2.1] });

// ============================================================
// SLIDE 8 — THE KEY SLIDE: NOT A TILE COMPANY
// ============================================================
let s8 = pres.addSlide();
s8.background = { color: BG };
s8.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });

s8.addText("We're Not a Tile Company.", { x: 0.8, y: 0.6, w: 9, h: 0.9, fontSize: 40, fontFace: "Arial Black", color: WHITE, margin: 0 });
s8.addText("We're a Pattern Projection Platform.", { x: 0.8, y: 1.4, w: 9, h: 0.7, fontSize: 32, fontFace: "Arial Black", color: GREEN, margin: 0 });

s8.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 2.3, w: 8.4, h: 0.04, fill: { color: GREEN } });

s8.addText("$148B", { x: 0.8, y: 2.6, w: 4, h: 1.0, fontSize: 64, fontFace: "Arial Black", color: GREEN, margin: 0 });
s8.addText("Total Addressable Market\nacross 12+ applications", { x: 0.8, y: 3.5, w: 4, h: 0.7, fontSize: 16, fontFace: "Arial", color: GRAY_LT, margin: 0 });

// Key points on the right
s8.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 2.6, w: 4.2, h: 2.5, fill: { color: CARD }, shadow: mkShadow() });
s8.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 2.6, w: 0.06, h: 2.5, fill: { color: GREEN } });
s8.addText([
  { text: "Every new market is a software update — not a new product.", options: { breakLine: true, bold: true, fontSize: 14, color: WHITE } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "Near-zero marginal cost to expand into new verticals.", options: { breakLine: true, bold: true, fontSize: 14, color: WHITE } },
  { text: "", options: { breakLine: true, fontSize: 8 } },
  { text: "Same $499 hardware. Same subscription. Tile is just the beachhead.", options: { fontSize: 14, color: GREEN } }
], { x: 5.5, y: 2.8, w: 3.7, h: 2.2, fontFace: "Arial", margin: 0 });

// ============================================================
// SLIDE 9 — DOWNSTREAM APPLICATIONS
// ============================================================
let s9 = pres.addSlide();
s9.background = { color: BG };
s9.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s9.addText("12+ Markets, One Device", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

const markets = [
  ["Ceramic Tile", "$12B", true],
  ["Hardwood", "$28B", false],
  ["Vinyl (LVP)", "$12B", false],
  ["Brick & Pavers", "$8B", false],
  ["Natural Stone", "$5B", false],
  ["Ceiling Tile", "$3B", false],
  ["Wallpaper", "$3B", false],
  ["Carpet Tile", "$2B", false],
  ["Solar Panels", "$30B", false],
  ["Drywall", "$15B", false],
  ["Cabinets", "$20B", false],
  ["Insulation", "$10B", false]
];
markets.forEach((m, i) => {
  const col = i % 4;
  const row = Math.floor(i / 4);
  const x = 0.8 + col * 2.25;
  const y = 1.2 + row * 1.45;
  const isLaunch = m[2];
  s9.addShape(pres.shapes.RECTANGLE, { x: x, y: y, w: 2.0, h: 1.2, fill: { color: isLaunch ? GREEN_DK : CARD }, shadow: mkShadow() });
  s9.addText(m[0], { x: x, y: y + 0.15, w: 2.0, h: 0.4, fontSize: 13, fontFace: "Arial", color: WHITE, bold: true, align: "center", margin: 0 });
  s9.addText(m[1], { x: x, y: y + 0.55, w: 2.0, h: 0.4, fontSize: 22, fontFace: "Arial Black", color: isLaunch ? WHITE : GREEN, align: "center", margin: 0 });
  if (isLaunch) {
    s9.addText("LAUNCH MARKET", { x: x, y: y + 0.9, w: 2.0, h: 0.25, fontSize: 8, fontFace: "Arial", color: "A5D6A7", align: "center", bold: true, margin: 0 });
  }
});

// ============================================================
// SLIDE 10 — CUTSTATION
// ============================================================
let s10 = pres.addSlide();
s10.background = { color: BG };
s10.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s10.addText("Future: LayIt CutStation", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });
s10.addText("Automated tile cutting, driven by LayIt software", { x: 0.8, y: 0.9, w: 9, h: 0.4, fontSize: 16, fontFace: "Arial", color: GRAY, italic: true, margin: 0 });

// Workflow steps
const steps = [
  ["1", "App computes\nall cuts"],
  ["2", "Cut queue\non screen"],
  ["3", "Place tile\nin brackets"],
  ["4", "Tap 'Cut'\nmachine goes"],
  ["5", "Walk away\ninstall last tile"]
];
steps.forEach((st, i) => {
  const x = 0.5 + i * 1.9;
  s10.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.5, w: 1.7, h: 1.5, fill: { color: CARD }, shadow: mkShadow() });
  s10.addText(st[0], { x: x, y: 1.55, w: 1.7, h: 0.5, fontSize: 28, fontFace: "Arial Black", color: GREEN, align: "center", margin: 0 });
  s10.addText(st[1], { x: x, y: 2.1, w: 1.7, h: 0.8, fontSize: 11, fontFace: "Arial", color: GRAY_LT, align: "center", margin: 0 });
});

// Opportunity
s10.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.3, w: 8.4, h: 1.8, fill: { color: CARD }, shadow: mkShadow() });
s10.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 3.3, w: 8.4, h: 0.06, fill: { color: GREEN } });
s10.addText("$60M", { x: 1.1, y: 3.5, w: 2.5, h: 0.7, fontSize: 44, fontFace: "Arial Black", color: GREEN, margin: 0 });
s10.addText("revenue opportunity", { x: 1.1, y: 4.1, w: 2.5, h: 0.3, fontSize: 12, fontFace: "Arial", color: GRAY, margin: 0 });
s10.addText([
  { text: "300,000+ tile contractors in the US", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Average $2-5K/year on cutting equipment", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "License software to CNC manufacturers — they build, we brain", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Curves, plumbing holes, hex slivers — cuts a wet saw can't make", options: { bullet: true, fontSize: 12, color: GREEN } }
], { x: 4.0, y: 3.5, w: 5, h: 1.5, fontFace: "Arial", margin: 0 });

// ============================================================
// SLIDE 11 — IP PROTECTION
// ============================================================
let s11 = pres.addSlide();
s11.background = { color: BG };
s11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s11.addText("IP Protection", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

// Patent cards
const patents = [
  ["Patent #1", "Camera-Based Room Measurement\nfor Tile Layout", "22 Claims", "Vision transformer depth estimation\nDepth anomaly detection\nConstraint-aware auto-correction\nNo LiDAR, no stereo, no vanishing points"],
  ["Patent #2", "Laser Projection Tile\nInstallation System", "27 Claims", "Tile-specific pattern computation\nPlaced-tile vision alignment\nGrout line projection with cut management\nMarker-free self-reinforcing calibration"]
];
patents.forEach((p, i) => {
  const x = 0.8 + i * 4.5;
  s11.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.2, w: 4.1, h: 3.8, fill: { color: CARD }, shadow: mkShadow() });
  s11.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.2, w: 4.1, h: 0.06, fill: { color: GREEN } });
  s11.addText(p[0], { x: x + 0.2, y: 1.4, w: 3.7, h: 0.35, fontSize: 14, fontFace: "Arial", color: GREEN, bold: true, margin: 0 });
  s11.addText(p[1], { x: x + 0.2, y: 1.75, w: 3.7, h: 0.6, fontSize: 16, fontFace: "Arial Black", color: WHITE, margin: 0 });
  s11.addText(p[2], { x: x + 0.2, y: 2.4, w: 3.7, h: 0.4, fontSize: 24, fontFace: "Arial Black", color: GREEN, margin: 0 });
  s11.addText(p[3], { x: x + 0.2, y: 2.9, w: 3.7, h: 1.8, fontSize: 11, fontFace: "Arial", color: GRAY_LT, margin: 0 });
});

s11.addText("49 total claims  |  Prior art differentiation documented against 5 existing patents  |  20-year protection through 2046", { x: 0.8, y: 5.1, w: 8.4, h: 0.3, fontSize: 10, fontFace: "Arial", color: GRAY, align: "center", margin: 0 });

// ============================================================
// SLIDE 12 — THE TEAM
// ============================================================
let s12 = pres.addSlide();
s12.background = { color: BG };
s12.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s12.addText("The Team", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

s12.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.3, w: 4, h: 3.5, fill: { color: CARD }, shadow: mkShadow() });
s12.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 1.3, w: 0.06, h: 3.5, fill: { color: GREEN } });
s12.addText("Robert Sims", { x: 1.2, y: 1.5, w: 3.4, h: 0.5, fontSize: 24, fontFace: "Arial Black", color: WHITE, margin: 0 });
s12.addText("Founder & CEO", { x: 1.2, y: 2.0, w: 3.4, h: 0.3, fontSize: 14, fontFace: "Arial", color: GREEN, margin: 0 });
s12.addText([
  { text: "Paint contractor and DIYer who didn't want to call his buddy to tile his bathroom — so he built a laser that does it for anyone", options: { breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "", options: { breakLine: true, fontSize: 6 } },
  { text: "Domain expertise in tile installation", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Hardware + software development", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Patent inventor (2 provisionals filed)", options: { bullet: true, breakLine: true, fontSize: 11, color: GRAY_LT } },
  { text: "Product design & prototyping", options: { bullet: true, fontSize: 11, color: GRAY_LT } }
], { x: 1.2, y: 2.5, w: 3.4, h: 2.2, fontFace: "Arial", margin: 0 });

s12.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 4, h: 3.5, fill: { color: CARD }, shadow: mkShadow() });
s12.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.3, w: 0.06, h: 3.5, fill: { color: GREEN } });
s12.addText("Key Hires Needed", { x: 5.6, y: 1.5, w: 3.4, h: 0.5, fontSize: 24, fontFace: "Arial Black", color: WHITE, margin: 0 });
s12.addText("Growth Stage", { x: 5.6, y: 2.0, w: 3.4, h: 0.3, fontSize: 14, fontFace: "Arial", color: GREEN, margin: 0 });
s12.addText([
  { text: "Embedded Systems Engineer", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Mobile / PWA Developer", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Computer Vision / ML Engineer", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Sales & Partnerships (trade shows)", options: { bullet: true, breakLine: true, fontSize: 12, color: GRAY_LT } },
  { text: "Operations & Manufacturing", options: { bullet: true, fontSize: 12, color: GRAY_LT } }
], { x: 5.6, y: 2.5, w: 3.4, h: 2.0, fontFace: "Arial", margin: 0 });

// ============================================================
// SLIDE 13 — THE ASK
// ============================================================
let s13 = pres.addSlide();
s13.background = { color: BG };
s13.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
s13.addText("The Ask", { x: 0.8, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", color: WHITE, margin: 0 });

s13.addText("[$ Amount]", { x: 0.8, y: 1.2, w: 8.4, h: 0.8, fontSize: 48, fontFace: "Arial Black", color: GREEN, align: "center", margin: 0 });
s13.addText("Seed Round", { x: 0.8, y: 1.9, w: 8.4, h: 0.4, fontSize: 18, fontFace: "Arial", color: GRAY, align: "center", margin: 0 });

const uses = [
  ["Manufacturing", "First production run (500 units)", "40%"],
  ["Engineering", "Embedded firmware + app development", "25%"],
  ["IP & Legal", "Utility patent filing + trademark", "10%"],
  ["Sales", "Trade shows (TISE, Coverings) + partnerships", "15%"],
  ["Operations", "Inventory, fulfillment, support setup", "10%"]
];
uses.forEach((u, i) => {
  const y = 2.6 + i * 0.55;
  s13.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: y, w: 8.4, h: 0.45, fill: { color: i % 2 === 0 ? CARD : BG2 } });
  s13.addText(u[0], { x: 1.0, y: y, w: 2.5, h: 0.45, fontSize: 12, fontFace: "Arial", color: GREEN, bold: true, valign: "middle", margin: 0 });
  s13.addText(u[1], { x: 3.5, y: y, w: 4.2, h: 0.45, fontSize: 12, fontFace: "Arial", color: GRAY_LT, valign: "middle", margin: 0 });
  s13.addText(u[2], { x: 7.7, y: y, w: 1.3, h: 0.45, fontSize: 14, fontFace: "Arial Black", color: GREEN, valign: "middle", align: "right", margin: 0 });
});

// ============================================================
// SLIDE 14 — CLOSING
// ============================================================
let s14 = pres.addSlide();
s14.background = { color: BG };
s14.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });

s14.addText("LayIt", { x: 0.8, y: 1.5, w: 8.4, h: 1.0, fontSize: 64, fontFace: "Arial Black", color: GREEN, align: "center", margin: 0 });
s14.addText("Every new market is a software update.\nNot a new product.", { x: 0.8, y: 2.5, w: 8.4, h: 0.8, fontSize: 20, fontFace: "Arial", color: WHITE, align: "center", italic: true, margin: 0 });

s14.addShape(pres.shapes.RECTANGLE, { x: 3.5, y: 3.5, w: 3, h: 0.04, fill: { color: GREEN } });

s14.addText("Robert Sims  |  talktosims@gmail.com", { x: 0.8, y: 3.8, w: 8.4, h: 0.4, fontSize: 14, fontFace: "Arial", color: GRAY_LT, align: "center", margin: 0 });
s14.addText("Confidential — March 2026", { x: 0.8, y: 4.5, w: 8.4, h: 0.3, fontSize: 10, fontFace: "Arial", color: GRAY, align: "center", margin: 0 });

pres.writeFile({ fileName: "/Users/Sims/Desktop/layit/sales/LayIt_Investor_Deck.pptx" })
  .then(() => console.log("Investor deck created!"))
  .catch(e => console.error(e));
