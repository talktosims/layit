const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "LayIt LLC";
pres.title = "LayIt - Laser-Guided Tile Layout System";

// ── Brand Colors ──
const C = {
  bg:       "0A0A0A",
  bgCard:   "141414",
  bgLight:  "F5F5F5",
  green:    "4CAF50",
  greenDk:  "2E7D32",
  greenLt:  "81C784",
  red:      "E74C3C",
  white:    "FFFFFF",
  gray:     "888888",
  grayLt:   "CCCCCC",
  grayDk:   "444444",
  navy:     "1A2E1A",
};

// ── Helper: fresh shadow ──
const cardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.25 });

// ════════════════════════════════════════════════════════
// SLIDE 1: TITLE
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  // Green accent bar at top
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  // Logo
  s.addText([
    { text: "Lay", options: { color: C.white, fontSize: 60, fontFace: "Arial Black", bold: true } },
    { text: "It", options: { color: C.green, fontSize: 60, fontFace: "Arial Black", bold: true } },
  ], { x: 0.5, y: 1.2, w: 9, h: 1.2, align: "center", margin: 0 });

  // Tagline
  s.addText("Laser-Guided Tile Layout System", {
    x: 0.5, y: 2.3, w: 9, h: 0.6, align: "center",
    fontSize: 20, fontFace: "Calibri", color: C.gray, charSpacing: 3,
  });

  // One-liner
  s.addText("See the finished floor before you lay a single tile.", {
    x: 1.5, y: 3.2, w: 7, h: 0.8, align: "center",
    fontSize: 16, fontFace: "Calibri", color: C.grayLt, italic: true,
  });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.0, w: 10, h: 0.625, fill: { color: "111111" } });
  s.addText("Provisional Patents Pending  |  LayIt LLC  |  2026", {
    x: 0.5, y: 5.05, w: 9, h: 0.55, align: "center",
    fontSize: 10, fontFace: "Calibri", color: C.grayDk,
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 2: THE PROBLEM
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("The $35B Problem", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  s.addText("Tile installation still runs on chalk lines and tape measures.", {
    x: 0.6, y: 0.95, w: 8, h: 0.5,
    fontSize: 14, fontFace: "Calibri", color: C.gray,
  });

  const problems = [
    { icon: "X", title: "Chalk lines wash off", desc: "Thinset buries them. One spill and your reference is gone." },
    { icon: "X", title: "Errors compound", desc: "Small misalignment on row 1 becomes 1/2\" off by row 20." },
    { icon: "X", title: "Dry-laying wastes time", desc: "30-60 minutes per room just to preview the layout." },
    { icon: "X", title: "Cuts discovered too late", desc: "Bad slivers found AFTER cutting = wasted tile and money." },
    { icon: "X", title: "Skilled labor shortage", desc: "10+ years experience needed. Good tilers are booked months out." },
  ];

  problems.forEach((p, i) => {
    const yBase = 1.65 + i * 0.72;
    // Red circle with X
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: yBase + 0.05, w: 0.4, h: 0.4, fill: { color: C.red } });
    s.addText("X", { x: 0.6, y: yBase + 0.05, w: 0.4, h: 0.4, align: "center", valign: "middle", fontSize: 16, fontFace: "Arial Black", color: C.white, bold: true, margin: 0 });
    // Title + desc
    s.addText(p.title, { x: 1.15, y: yBase, w: 8, h: 0.35, fontSize: 15, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText(p.desc, { x: 1.15, y: yBase + 0.32, w: 8, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.gray, margin: 0 });
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 3: THE SOLUTION
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText([
    { text: "Lay", options: { color: C.white } },
    { text: "It", options: { color: C.green } },
    { text: " Solves It", options: { color: C.white } },
  ], { x: 0.6, y: 0.3, w: 9, h: 0.7, fontSize: 36, fontFace: "Arial Black", bold: true, margin: 0 });

  s.addText("A 200mW green laser projects your entire tile layout directly onto the work surface.", {
    x: 0.6, y: 0.95, w: 8, h: 0.5, fontSize: 14, fontFace: "Calibri", color: C.gray,
  });

  const solutions = [
    { title: "Every grout line visible", desc: "Full tile grid projected in real time — visible in broad daylight." },
    { title: "Every cut shown before cutting", desc: "See exactly where each tile goes, including edge cuts." },
    { title: "Auto-aligns to placed tiles", desc: "Camera tracks your progress. Gets MORE accurate as you work." },
    { title: "Any pattern: grid, brick, herringbone", desc: "The app handles the math. You just follow the lines." },
    { title: "Less skilled crew = same quality", desc: "Junior installers can lay tile accurately from day one." },
  ];

  solutions.forEach((p, i) => {
    const yBase = 1.65 + i * 0.72;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: yBase + 0.05, w: 0.4, h: 0.4, fill: { color: C.green } });
    s.addText("\u2713", { x: 0.6, y: yBase + 0.05, w: 0.4, h: 0.4, align: "center", valign: "middle", fontSize: 18, fontFace: "Arial", color: C.white, bold: true, margin: 0 });
    s.addText(p.title, { x: 1.15, y: yBase, w: 8, h: 0.35, fontSize: 15, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    s.addText(p.desc, { x: 1.15, y: yBase + 0.32, w: 8, h: 0.3, fontSize: 12, fontFace: "Calibri", color: C.grayLt, margin: 0 });
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 4: HOW IT WORKS (3 steps)
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("How It Works", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  const steps = [
    { num: "1", title: "Design on the App", desc: "Enter room dimensions, pick tile size, choose your pattern. The app calculates every tile and cut instantly." },
    { num: "2", title: "Set Up the Laser", desc: "Place the unit on a tripod, point at your surface. Camera auto-calibrates in 30 seconds. No manual setup." },
    { num: "3", title: "Follow the Lines", desc: "Green laser lines project onto the floor. Lay tile directly to the lines. Each tile strengthens alignment." },
  ];

  steps.forEach((step, i) => {
    const xBase = 0.45 + i * 3.15;
    // Card background
    s.addShape(pres.shapes.RECTANGLE, {
      x: xBase, y: 1.3, w: 2.85, h: 3.6,
      fill: { color: C.bgCard },
      shadow: cardShadow(),
    });
    // Number circle
    s.addShape(pres.shapes.OVAL, { x: xBase + 1.05, y: 1.6, w: 0.75, h: 0.75, fill: { color: C.green } });
    s.addText(step.num, { x: xBase + 1.05, y: 1.6, w: 0.75, h: 0.75, align: "center", valign: "middle", fontSize: 28, fontFace: "Arial Black", color: C.bg, bold: true, margin: 0 });
    // Title
    s.addText(step.title, { x: xBase + 0.2, y: 2.55, w: 2.45, h: 0.5, align: "center", fontSize: 16, fontFace: "Calibri", color: C.white, bold: true, margin: 0 });
    // Description
    s.addText(step.desc, { x: xBase + 0.2, y: 3.1, w: 2.45, h: 1.5, align: "center", fontSize: 12, fontFace: "Calibri", color: C.gray, margin: 0 });
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 5: KEY FEATURES (6 features in 2x3 grid)
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Built for Job Sites", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  const features = [
    { title: "Bump Recovery", desc: "6-axis IMU detects displacement. Camera re-locks in seconds. No user intervention." },
    { title: "Absolute Positioning", desc: "No error accumulation. Tile #50 is just as accurate as tile #1." },
    { title: "Keystone Correction", desc: "Floors, walls, ceilings. Tilt the tripod anywhere — lines stay true." },
    { title: "Drop-Resistant", desc: "Silicone sleeve + PETG shell + internal grommet isolation. Job-site tough." },
    { title: "WiFi App Control", desc: "Your phone is the remote. Works on any device with a browser. App is free forever." },
    { title: "All-Day Operation", desc: "Active cooling with 30mm fan. Continuous 8+ hour operation without overheating." },
  ];

  features.forEach((f, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const xBase = 0.4 + col * 3.15;
    const yBase = 1.2 + row * 2.05;

    s.addShape(pres.shapes.RECTANGLE, {
      x: xBase, y: yBase, w: 2.9, h: 1.75,
      fill: { color: C.bgCard },
      shadow: cardShadow(),
    });

    // Green left accent bar
    s.addShape(pres.shapes.RECTANGLE, { x: xBase, y: yBase, w: 0.06, h: 1.75, fill: { color: C.green } });

    s.addText(f.title, { x: xBase + 0.2, y: yBase + 0.15, w: 2.5, h: 0.4, fontSize: 14, fontFace: "Calibri", color: C.green, bold: true, margin: 0 });
    s.addText(f.desc, { x: xBase + 0.2, y: yBase + 0.55, w: 2.5, h: 1.0, fontSize: 11, fontFace: "Calibri", color: C.grayLt, margin: 0 });
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 6: CAMERA SCAN (new tech)
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("NEW: Camera-Based Room Scanning", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 32, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  s.addText("Snap a photo. Get wall dimensions. Start tiling.", {
    x: 0.6, y: 0.95, w: 8, h: 0.45,
    fontSize: 14, fontFace: "Calibri", color: C.gray,
  });

  // Left column: description
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.6, w: 4.3, h: 3.4,
    fill: { color: C.bgCard }, shadow: cardShadow(),
  });

  s.addText([
    { text: "No LiDAR. No tape measure. Just your phone camera.\n\n", options: { fontSize: 14, color: C.white, bold: true, breakLine: true } },
    { text: "AI-powered monocular depth estimation converts a single photo into precise wall measurements.\n\n", options: { fontSize: 12, color: C.grayLt, breakLine: true } },
    { text: "Automatic feature detection", options: { fontSize: 12, color: C.green, bold: true, bullet: true, breakLine: true } },
    { text: "Finds niches, windows, and protrusions", options: { fontSize: 11, color: C.grayLt, breakLine: true, indentLevel: 1 } },
    { text: "Constraint-aware auto-correction", options: { fontSize: 12, color: C.green, bold: true, bullet: true, breakLine: true } },
    { text: "Adjusts layout around fixed obstacles", options: { fontSize: 11, color: C.grayLt, breakLine: true, indentLevel: 1 } },
    { text: "Direct PWA integration", options: { fontSize: 12, color: C.green, bold: true, bullet: true, breakLine: true } },
    { text: "Photo to tile layout in under 60 seconds", options: { fontSize: 11, color: C.grayLt, indentLevel: 1 } },
  ], { x: 0.75, y: 1.8, w: 3.8, h: 3.0 });

  // Right column: stats
  const stats = [
    { num: "< 3%", label: "WIDTH ERROR" },
    { num: "< 5\"", label: "RESIDUAL AFTER\nCALIBRATION" },
    { num: "0.7%", label: "BEST ACCURACY\n(HEAD-ON WALL)" },
    { num: "8", label: "CALIBRATION\nRUNS" },
  ];

  stats.forEach((st, i) => {
    const yBase = 1.6 + i * 0.85;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.2, y: yBase, w: 4.3, h: 0.72,
      fill: { color: C.bgCard }, shadow: cardShadow(),
    });
    s.addText(st.num, { x: 5.35, y: yBase + 0.05, w: 1.6, h: 0.62, fontSize: 24, fontFace: "Arial Black", color: C.green, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(st.label, { x: 7.0, y: yBase + 0.05, w: 2.3, h: 0.62, fontSize: 10, fontFace: "Calibri", color: C.gray, valign: "middle", margin: 0, charSpacing: 1 });
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 7: COMPETITIVE COMPARISON
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Old Way vs. LayIt", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  const rows = [
    ["", "The Old Way", "LayIt"],
    ["Reference lines", "Chalk lines wash off, get buried", "Laser lines always visible"],
    ["Accuracy", "Errors compound over distance", "Absolute positioning - no accumulation"],
    ["Layout preview", "Dry-lay wastes 30-60 min/room", "See full layout projected instantly"],
    ["Cut planning", "Mistakes found AFTER cutting", "See every cut BEFORE you cut"],
    ["Progress tracking", "Re-measure every few rows", "Camera tracks tiles automatically"],
    ["Recovery", "Bump = ruined reference line", "Auto re-calibrates in seconds"],
    ["Skill required", "10+ years experience", "Junior installers can follow laser lines"],
  ];

  const tableRows = rows.map((row, i) => {
    if (i === 0) {
      return row.map((cell, j) => ({
        text: cell,
        options: {
          bold: true, fontSize: 11, fontFace: "Calibri",
          color: j === 0 ? C.gray : C.white,
          fill: { color: "1A1A1A" },
          align: j === 0 ? "left" : "center",
          valign: "middle",
        },
      }));
    }
    return row.map((cell, j) => ({
      text: cell,
      options: {
        fontSize: 11, fontFace: "Calibri",
        color: j === 2 ? C.green : j === 1 ? C.grayLt : C.gray,
        bold: j === 0,
        fill: { color: i % 2 === 0 ? C.bgCard : "1A1A1A" },
        align: j === 0 ? "left" : "left",
        valign: "middle",
      },
    }));
  });

  s.addTable(tableRows, {
    x: 0.5, y: 1.2, w: 9,
    colW: [1.8, 3.5, 3.7],
    rowH: Array(rows.length).fill(0.5),
    border: { pt: 0.5, color: "2A2A2A" },
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 8: PRODUCT & PRICING
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Product & Pricing", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  // Flagship card
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 4.3, h: 3.8, fill: { color: C.bgCard }, shadow: cardShadow() });
  s.addText("Flagship", { x: 0.5, y: 1.35, w: 4.3, h: 0.5, align: "center", fontSize: 22, fontFace: "Arial Black", color: C.white, bold: true, margin: 0 });
  s.addText("Corded Power", { x: 0.5, y: 1.8, w: 4.3, h: 0.3, align: "center", fontSize: 11, fontFace: "Calibri", color: C.gray, margin: 0 });
  s.addText("$499", { x: 0.5, y: 2.2, w: 4.3, h: 0.7, align: "center", fontSize: 48, fontFace: "Arial Black", color: C.green, bold: true, margin: 0 });
  s.addText("one-time purchase", { x: 0.5, y: 2.85, w: 4.3, h: 0.25, align: "center", fontSize: 10, fontFace: "Calibri", color: C.grayDk, margin: 0 });

  const flagFeatures = [
    "200mW green laser projector",
    "5MP vision alignment camera",
    "6-axis bump detection (IMU)",
    "WiFi phone sync & control",
    "12V DC adapter included",
    "Free tile planning app",
  ];
  s.addText(flagFeatures.map((f, i) => ({
    text: f, options: { bullet: true, breakLine: i < flagFeatures.length - 1, fontSize: 12, color: C.grayLt },
  })), { x: 1.0, y: 3.2, w: 3.3, h: 1.6, fontFace: "Calibri" });

  // Pro card (featured)
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.2, w: 4.3, h: 3.8, fill: { color: C.navy }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.2, w: 4.3, h: 0.04, fill: { color: C.green } });
  s.addText("Pro", { x: 5.2, y: 1.35, w: 4.3, h: 0.5, align: "center", fontSize: 22, fontFace: "Arial Black", color: C.white, bold: true, margin: 0 });
  s.addText("Corded + Battery", { x: 5.2, y: 1.8, w: 4.3, h: 0.3, align: "center", fontSize: 11, fontFace: "Calibri", color: C.gray, margin: 0 });
  s.addText("$649", { x: 5.2, y: 2.2, w: 4.3, h: 0.7, align: "center", fontSize: 48, fontFace: "Arial Black", color: C.green, bold: true, margin: 0 });
  s.addText("one-time purchase", { x: 5.2, y: 2.85, w: 4.3, h: 0.25, align: "center", fontSize: 10, fontFace: "Calibri", color: C.grayDk, margin: 0 });

  const proFeatures = [
    "Everything in Flagship, plus:",
    "2x swappable LiPo batteries",
    "1.5-2 hours cordless per battery",
    "USB-C PD charging",
    "Hot-swap: no interruption",
    "Go anywhere - no outlet needed",
  ];
  s.addText(proFeatures.map((f, i) => ({
    text: f, options: { bullet: true, breakLine: i < proFeatures.length - 1, fontSize: 12, color: i === 0 ? C.green : C.grayLt, bold: i === 0 },
  })), { x: 5.7, y: 3.2, w: 3.3, h: 1.6, fontFace: "Calibri" });
}

// ════════════════════════════════════════════════════════
// SLIDE 9: TECH SPECS
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Technical Specifications", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  const specs = [
    ["Laser", "200mW 520nm direct diode (Class 3B)"],
    ["Projection Speed", "20,000 points per second"],
    ["Camera", "5MP 160-degree wide-angle (OV5640)"],
    ["Processor", "ESP32-S3 dual-core (240MHz)"],
    ["Connectivity", "WiFi 802.11 b/g/n + Bluetooth 5.0 LE"],
    ["Power (Flagship)", "12V 3A DC adapter"],
    ["Power (Pro)", "12V DC + 3S 11.1V 3000mAh LiPo x2"],
    ["Battery Life", "1.5-2 hours per pack (Pro model)"],
    ["Dimensions", "~6 inches across x 3.3 inches tall"],
    ["Cooling", "30mm exhaust fan + passive vents"],
    ["Drop Protection", "Silicone + PETG + grommet isolation"],
    ["App", "Free PWA (works in any browser, any device)"],
  ];

  const tableRows = specs.map((row, i) => [
    { text: row[0], options: { fontSize: 12, fontFace: "Calibri", color: C.green, bold: true, fill: { color: i % 2 === 0 ? C.bgCard : "1A1A1A" }, valign: "middle" } },
    { text: row[1], options: { fontSize: 12, fontFace: "Calibri", color: C.grayLt, fill: { color: i % 2 === 0 ? C.bgCard : "1A1A1A" }, valign: "middle" } },
  ]);

  s.addTable(tableRows, {
    x: 0.5, y: 1.15, w: 9,
    colW: [2.5, 6.5],
    rowH: Array(specs.length).fill(0.36),
    border: { pt: 0.5, color: "2A2A2A" },
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 10: BUSINESS MODEL
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Business Model", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  // Big stat callouts - 3 across
  const bigStats = [
    { num: "40-50%", label: "Gross Margin" },
    { num: "$0", label: "Subscription Fee" },
    { num: "1 Job", label: "Pays for Itself" },
  ];

  bigStats.forEach((st, i) => {
    const xBase = 0.4 + i * 3.15;
    s.addShape(pres.shapes.RECTANGLE, { x: xBase, y: 1.2, w: 2.9, h: 1.5, fill: { color: C.bgCard }, shadow: cardShadow() });
    s.addText(st.num, { x: xBase, y: 1.3, w: 2.9, h: 0.8, align: "center", valign: "middle", fontSize: 32, fontFace: "Arial Black", color: C.green, bold: true, margin: 0 });
    s.addText(st.label, { x: xBase, y: 2.1, w: 2.9, h: 0.4, align: "center", fontSize: 12, fontFace: "Calibri", color: C.gray, charSpacing: 2, margin: 0 });
  });

  // Revenue model bullets
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 9, h: 2.2, fill: { color: C.bgCard }, shadow: cardShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 0.06, h: 2.2, fill: { color: C.green } });

  s.addText([
    { text: "Revenue Model\n", options: { fontSize: 16, color: C.white, bold: true, breakLine: true } },
    { text: "Hardware sales: Two SKUs at $499 and $649 with 40-50% gross margins", options: { fontSize: 12, color: C.grayLt, bullet: true, breakLine: true } },
    { text: "No subscription, no recurring fees — the app is free forever", options: { fontSize: 12, color: C.grayLt, bullet: true, breakLine: true } },
    { text: "One bad tile layout costs more than this tool. ROI on first job.", options: { fontSize: 12, color: C.grayLt, bullet: true, breakLine: true } },
    { text: "Target: tile installers, general contractors, advanced DIYers", options: { fontSize: 12, color: C.grayLt, bullet: true, breakLine: true } },
    { text: "Go-to-market: direct to installer via contractor networks, then retail", options: { fontSize: 12, color: C.grayLt, bullet: true } },
  ], { x: 0.8, y: 3.15, w: 8.4, h: 1.9, fontFace: "Calibri" });
}

// ════════════════════════════════════════════════════════
// SLIDE 11: IP & MOAT
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Intellectual Property & Moat", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  const ipItems = [
    { title: "Provisional Patent #1", desc: "Laser projection system for tile layout with computer vision auto-calibration, bump recovery, and absolute positioning." },
    { title: "Provisional Patent #2", desc: "Camera-based room scanning using monocular depth estimation, RANSAC plane fitting, automatic constraint detection, and AI-powered wall measurement." },
    { title: "Trade Secrets", desc: "Calibration algorithms, correction factors, edge detection pipeline — years of real-world tuning from actual tile installations." },
    { title: "First-Mover Advantage", desc: "No affordable laser tile layout system exists on the market. LayIt is creating the category." },
  ];

  ipItems.forEach((item, i) => {
    const yBase = 1.2 + i * 1.0;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: yBase, w: 9, h: 0.85, fill: { color: C.bgCard }, shadow: cardShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: yBase, w: 0.06, h: 0.85, fill: { color: C.green } });
    s.addText(item.title, { x: 0.75, y: yBase + 0.08, w: 8.5, h: 0.3, fontSize: 14, fontFace: "Calibri", color: C.green, bold: true, margin: 0 });
    s.addText(item.desc, { x: 0.75, y: yBase + 0.4, w: 8.5, h: 0.35, fontSize: 11, fontFace: "Calibri", color: C.grayLt, margin: 0 });
  });
}

// ════════════════════════════════════════════════════════
// SLIDE 12: ORIGIN STORY / FOUNDER
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green } });

  s.addText("Built by a Tradesman, for Tradesmen", {
    x: 0.6, y: 0.3, w: 9, h: 0.7,
    fontSize: 32, fontFace: "Arial Black", color: C.white, bold: true, margin: 0,
  });

  // Quote card
  s.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1.4, w: 8, h: 2.4, fill: { color: C.bgCard }, shadow: cardShadow() });

  s.addText([
    { text: '"', options: { fontSize: 72, color: C.green, fontFace: "Georgia" } },
  ], { x: 1.3, y: 1.2, w: 1, h: 1, margin: 0 });

  s.addText(
    "I wanted to tile my own bathroom without paying someone $15 a square foot. So I built a laser that shows me exactly where every tile goes. Then I realized every contractor could use one too.",
    { x: 2.0, y: 1.7, w: 6.5, h: 1.2, fontSize: 16, fontFace: "Georgia", color: C.grayLt, italic: true }
  );

  s.addText("Robbie  |  Founder, LayIt LLC  |  Minneapolis, MN", {
    x: 2.0, y: 3.0, w: 6.5, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.gray,
  });

  // Why now
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.1, w: 9, h: 1.2, fill: { color: C.navy } });
  s.addText([
    { text: "Why Now?  ", options: { fontSize: 14, color: C.green, bold: true } },
    { text: "ESP32 microcontrollers, precision galvos, and computer vision models are all commodity technology now. The pieces exist — no one has assembled them for tile installation until LayIt.", options: { fontSize: 12, color: C.grayLt } },
  ], { x: 0.8, y: 4.2, w: 8.4, h: 1.0, fontFace: "Calibri", valign: "middle" });
}

// ════════════════════════════════════════════════════════
// SLIDE 13: CLOSING / CTA
// ════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  // Full green band in middle
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.5, w: 10, h: 2.6, fill: { color: C.greenDk } });

  s.addText([
    { text: "Lay", options: { color: C.white } },
    { text: "It", options: { color: C.bg } },
  ], { x: 0.5, y: 1.7, w: 9, h: 0.9, align: "center", fontSize: 52, fontFace: "Arial Black", bold: true, margin: 0 });

  s.addText("The tool that pays for itself on the first job.", {
    x: 1.5, y: 2.6, w: 7, h: 0.6, align: "center",
    fontSize: 18, fontFace: "Calibri", color: C.white, italic: true,
  });

  s.addText("Robbie@LayIt.com  |  LayIt LLC  |  Minneapolis, MN", {
    x: 1.5, y: 3.3, w: 7, h: 0.4, align: "center",
    fontSize: 12, fontFace: "Calibri", color: "1A4A1A",
  });

  // Bottom
  s.addText("Provisional Patents Pending  |  2026", {
    x: 0.5, y: 4.8, w: 9, h: 0.4, align: "center",
    fontSize: 10, fontFace: "Calibri", color: C.grayDk,
  });
}

// ── Save ──
pres.writeFile({ fileName: "/Users/Sims/Desktop/layit/sales/LayIt_Pitch_Deck.pptx" })
  .then(() => console.log("Saved: LayIt_Pitch_Deck.pptx"))
  .catch(err => console.error(err));
