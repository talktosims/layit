const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak
} = require("docx");

// Colors
const GREEN = "2C5F2D";
const DARK = "1E1E1E";
const MID = "444444";
const LIGHT_BG = "F5F7F5";
const ACCENT = "3A8F3F";
const BORDER_COLOR = "CCCCCC";
const WHITE = "FFFFFF";

const border = { style: BorderStyle.SINGLE, size: 1, color: BORDER_COLOR };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function spacer(pts = 200) {
  return new Paragraph({ spacing: { before: pts } });
}

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: GREEN, space: 1 } },
  });
}

function featureBlock(number, title, bullets, pitch) {
  const children = [];

  // Feature heading
  children.push(new Paragraph({
    spacing: { before: 280, after: 120 },
    children: [
      new TextRun({ text: `${number}. `, font: "Arial", size: 26, bold: true, color: GREEN }),
      new TextRun({ text: title, font: "Arial", size: 26, bold: true, color: DARK }),
    ],
  }));

  // Bullets
  for (const b of bullets) {
    children.push(new Paragraph({
      numbering: { reference: "featureBullets", level: 0 },
      spacing: { after: 60 },
      children: [new TextRun({ text: b, font: "Arial", size: 22, color: MID })],
    }));
  }

  // Pitch it callout
  children.push(new Paragraph({
    spacing: { before: 100, after: 60 },
    indent: { left: 360 },
    children: [
      new TextRun({ text: "Pitch it: ", font: "Arial", size: 22, bold: true, italics: true, color: GREEN }),
      new TextRun({ text: `\u201C${pitch}\u201D`, font: "Arial", size: 22, italics: true, color: MID }),
    ],
  }));

  return children;
}

function tableRow(cells, isHeader = false) {
  return new TableRow({
    children: cells.map((text, idx) => new TableCell({
      borders,
      width: { size: idx === 0 ? 3120 : 6240, type: WidthType.DXA },
      shading: isHeader
        ? { fill: GREEN, type: ShadingType.CLEAR }
        : (idx === 0 ? { fill: LIGHT_BG, type: ShadingType.CLEAR } : undefined),
      margins: cellMargins,
      children: [new Paragraph({
        children: [new TextRun({
          text, font: "Arial",
          size: isHeader ? 22 : 20,
          bold: isHeader || idx === 0,
          color: isHeader ? WHITE : DARK,
        })],
      })],
    })),
  });
}

function compTableRow(cells, isHeader = false) {
  return new TableRow({
    children: cells.map((text, idx) => new TableCell({
      borders,
      width: { size: 4680, type: WidthType.DXA },
      shading: isHeader
        ? { fill: GREEN, type: ShadingType.CLEAR }
        : undefined,
      margins: cellMargins,
      children: [new Paragraph({
        children: [new TextRun({
          text, font: "Arial",
          size: isHeader ? 22 : 20,
          bold: isHeader,
          color: isHeader ? WHITE : DARK,
        })],
      })],
    })),
  });
}

// Build document
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: GREEN },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "featureBullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "objBullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "LayIt Laser \u2014 Feature Pitch Guide", font: "Arial", size: 18, color: "999999", italics: true })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "LayIt Laser  \u2022  ", font: "Arial", size: 16, color: "999999" }),
            new TextRun({ text: "Page ", font: "Arial", size: 16, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" }),
          ],
        })],
      }),
    },
    children: [
      // ===== TITLE =====
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "LayIt Laser", font: "Arial", size: 48, bold: true, color: GREEN })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
        children: [new TextRun({ text: "Feature Pitch List", font: "Arial", size: 32, color: DARK })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "Everything You Need to Know When Talking About LayIt", font: "Arial", size: 22, italics: true, color: MID })],
      }),

      divider(),

      // ===== THE ONE-LINER =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("The One-Liner")],
      }),
      new Paragraph({
        spacing: { after: 200 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: GREEN, space: 8 } },
        children: [new TextRun({
          text: "\u201CLayIt projects your exact tile layout onto the floor with a laser \u2014 every cut, every grout line, before you lay a single tile.\u201D",
          font: "Arial", size: 24, italics: true, color: MID,
        })],
      }),

      divider(),

      // ===== CORE FEATURES =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Core Features")],
      }),

      ...featureBlock("1", "Live Laser Projection", [
        "A 200mW green laser draws your entire tile layout directly onto the floor or wall in real-time",
        "Every grout line, every cut line, every tile boundary \u2014 visible in broad daylight",
        "No more chalk lines, no more tape measures, no more \u201Ceyeballing it\u201D",
      ], "You see the finished floor before you start cutting."),

      ...featureBlock("2", "Auto-Calibration Camera (Point & Play)", [
        "Built-in 5MP wide-angle camera handles all alignment automatically",
        "Set the unit on a tripod, open the app, and it calibrates itself",
        "No manual measurements, no setup hassle, no surveyor skills needed",
        "Cold start against any wall or corner \u2014 camera finds the edges and locks in",
      ], "Set it up in 30 seconds. It figures out the room for you."),

      ...featureBlock("3", "Live Edge Detection", [
        "The camera watches tiles AS you place them",
        "Every tile you set down becomes a new reference point, strengthening accuracy",
        "The system gets MORE precise as you work, not less",
        "Uses computer vision (Canny edge detection + contour mapping) \u2014 not stickers or markers",
      ], "The more tiles you lay, the smarter it gets."),

      ...featureBlock("4", "Keystone Correction", [
        "Software automatically adjusts for the projection angle",
        "Tilt the tripod to project onto floors, walls, ceilings \u2014 laser lines stay geometrically perfect",
        "No manual calibration needed when you change the angle",
      ], "Aim it anywhere. The lines stay true."),

      ...featureBlock("5", "Internal Shock Absorption", [
        "Triple-layer impact protection: silicone sleeve + PETG shell + internal isolation mounts",
        "All sensitive components (galvos, laser, electronics) sit on silicone-grommeted mounting posts",
        "Galvo bay surrounded by foam-lined bumper channel \u2014 lateral drop protection",
        "Reinforced corner impact bosses inside the dome absorb energy at the most likely contact points",
        "Designed for the reality of job sites \u2014 this thing WILL get knocked off a tripod eventually",
      ], "Built for job sites, not labs. Drop-resistant by design."),

      ...featureBlock("6", "Bump Recovery", [
        "6-axis IMU (accelerometer + gyroscope) constantly monitors for movement",
        "If the unit gets bumped or shifted, it detects the displacement instantly",
        "Camera automatically re-locks to existing tile edges \u2014 no user intervention",
        "Confidence indicator: GREEN (locked), YELLOW (degraded), RED (re-scanning)",
      ], "Kick the tripod by accident? It re-calibrates itself in seconds."),

      ...featureBlock("7", "Absolute Positioning (No Error Accumulation)", [
        "Unlike tape-and-chalk methods where small errors compound across a room",
        "LayIt uses absolute coordinate mapping \u2014 each tile is positioned independently",
        "Tile #50 is just as accurate as tile #1",
      ], "No compounding errors. Tile 50 is dead-on just like tile 1."),

      ...featureBlock("8", "WiFi App Control (Free)", [
        "Control everything from your phone or tablet \u2014 no wires to the unit",
        "Design your layout in the app: choose tile size, pattern, grout width, starting corner",
        "See the projected layout update in real-time as you adjust settings",
        "Works on any device with a browser \u2014 iPhone, Android, iPad, laptop",
      ], "Your phone is the remote. The app is free forever."),

      ...featureBlock("9", "Cloud Sync", [
        "Save projects to the cloud and pick up where you left off on any device",
        "Start a layout on your phone, continue on your tablet",
        "Passphrase-based sync \u2014 no account needed, no login, just a simple passphrase",
      ], "Start on your phone, finish on your iPad. Your project follows you."),

      ...featureBlock("10", "Active Cooling (All-Day Operation)", [
        "30mm exhaust fan + passive vent slots on all faces",
        "Designed for continuous 8+ hour operation",
        "Tile a whole kitchen, bathroom, or commercial floor without overheating",
      ], "Run it all day. It won\u2019t overheat."),

      divider(),

      // ===== PRO MODEL =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Pro Model Extras")],
      }),
      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: "$649 Pro  vs.  $499 Flagship", font: "Arial", size: 24, bold: true, color: GREEN })],
      }),

      ...featureBlock("11", "Cordless Operation (Pro Only)", [
        "Swappable 3S LiPo battery packs \u2014 ~1.5\u20132 hours per charge",
        "Ships with 2 battery packs for continuous use (swap and keep going)",
        "Also accepts 12V DC cord (wall power takes priority, charges battery simultaneously)",
        "Hot-swap: automatic switchover between cord and battery, no interruption",
      ], "No outlet? No problem. Two batteries, all-day cordless."),

      ...featureBlock("12", "USB-C Charging (Pro Only)", [
        "Charge batteries via USB-C PD \u2014 same cable as your phone",
        "Charge from a truck outlet, power bank, or any USB-C charger",
      ], "Charge it like your phone."),

      divider(),
      new Paragraph({ children: [new PageBreak()] }),

      // ===== TECH SPECS TABLE =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Technical Specs")],
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 6240],
        rows: [
          tableRow(["Spec", "Value"], true),
          tableRow(["Laser", "200mW 520nm direct diode (Class 3B)"]),
          tableRow(["Projection Speed", "20,000 points per second"]),
          tableRow(["Camera", "5MP 160\u00B0 wide-angle (OV5640)"]),
          tableRow(["Processor", "ESP32-S3 dual-core (240MHz)"]),
          tableRow(["Connectivity", "WiFi 802.11 b/g/n + Bluetooth 5.0 LE"]),
          tableRow(["Power (Flagship)", "12V 3A DC adapter"]),
          tableRow(["Power (Pro)", "12V DC + 3S 11.1V 3000mAh LiPo (2 included)"]),
          tableRow(["Battery Life", "~1.5\u20132 hours per pack (Pro)"]),
          tableRow(["Dimensions", "~6\u201D across \u00D7 3.3\u201D tall"]),
          tableRow(["Weight", "Estimated ~2\u20133 lbs with sleeve"]),
          tableRow(["Operating Temp", "-15\u00B0C to 45\u00B0C"]),
          tableRow(["App", "Free PWA (works in any browser)"]),
          tableRow(["Cooling", "30mm exhaust fan + passive vents"]),
          tableRow(["Drop Protection", "Silicone sleeve + PETG shell + internal grommet isolation"]),
        ],
      }),

      spacer(300),
      divider(),

      // ===== COMPETITIVE ADVANTAGES =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Competitive Advantages")],
      }),
      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: "Why LayIt vs. The Old Way", font: "Arial", size: 22, italics: true, color: MID })],
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4680, 4680],
        rows: [
          compTableRow(["The Old Way", "LayIt"], true),
          compTableRow(["Chalk lines wash off, smudge, get buried under thinset", "Laser lines are always visible, never get covered"]),
          compTableRow(["Tape measures accumulate error over distance", "Absolute positioning \u2014 no error accumulation"]),
          compTableRow(["Dry-laying wastes 30\u201360 min per room", "Skip the dry lay \u2014 see the layout projected instantly"]),
          compTableRow(["Mistakes found AFTER cutting (waste $$$)", "See every cut BEFORE you cut"]),
          compTableRow(["Re-measuring after every few rows", "Camera tracks your progress automatically"]),
          compTableRow(["Layout dies when you bump the reference line", "Bump recovery re-calibrates in seconds"]),
          compTableRow(["One phone call and your chalk lines are ruined", "Laser projection is always there, always accurate"]),
        ],
      }),

      spacer(300),
      divider(),
      new Paragraph({ children: [new PageBreak()] }),

      // ===== ELEVATOR PITCHES =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Elevator Pitches")],
      }),
      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: "Pick your audience", font: "Arial", size: 22, italics: true, color: MID })],
      }),

      // Tile Installers
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("For Tile Installers")],
      }),
      new Paragraph({
        spacing: { after: 240 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: GREEN, space: 8 } },
        children: [new TextRun({
          text: "\u201CLayIt shows you exactly where every tile goes \u2014 projected right on the floor with a laser. No more chalk lines, no more dry-laying, no more guessing. You see the cuts before you make them.\u201D",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // GCs
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("For GCs / Project Managers")],
      }),
      new Paragraph({
        spacing: { after: 240 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: GREEN, space: 8 } },
        children: [new TextRun({
          text: "\u201CLayIt cuts tile layout time by 30\u201350%. Your tile guys see the exact pattern projected on the floor, make fewer cutting mistakes, and waste less material. Pays for itself on the first big job.\u201D",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // DIYers
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("For DIYers")],
      }),
      new Paragraph({
        spacing: { after: 240 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: GREEN, space: 8 } },
        children: [new TextRun({
          text: "\u201CEver tried tiling a bathroom and ended up with a weird sliver tile against the wall? LayIt shows you the whole layout before you start, so you can adjust and get it right the first time.\u201D",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // Investors
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("For Investors / Business Pitch")],
      }),
      new Paragraph({
        spacing: { after: 240 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: GREEN, space: 8 } },
        children: [new TextRun({
          text: "\u201CTile installation is a $35B market that still uses chalk lines and tape measures. LayIt is the first affordable laser projection system that automates tile layout with computer vision. Two SKUs at $499 and $649, 40\u201350% gross margins, no subscription \u2014 the tool pays for itself on one job.\u201D",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      divider(),

      // ===== OBJECTION HANDLING =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Objection Handling")],
      }),

      // Objection 1
      new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "\u201CI\u2019ve been tiling for 20 years, I don\u2019t need a laser.\u201D", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 200 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        children: [new TextRun({
          text: "Totally respect that. This isn\u2019t about replacing your skill \u2014 it\u2019s about speed. The guys who\u2019ve tried it say they skip the dry lay entirely and cut their layout time in half. More jobs per week.",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // Objection 2
      new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "\u201C$500 is a lot for a tool.\u201D", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 200 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        children: [new TextRun({
          text: "One bag of wasted tile from a bad layout costs $50\u2013100. One callback costs you a full day. This pays for itself inside the first month.",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // Objection 3
      new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "\u201CWhat if it breaks on the job site?\u201D", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 200 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        children: [new TextRun({
          text: "It\u2019s got a silicone impact sleeve, internal shock mounts, and if it gets bumped out of alignment, the camera re-calibrates itself in seconds. Built for job sites, not labs.",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // Objection 4
      new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "\u201CDo I need internet?\u201D", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 200 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        children: [new TextRun({
          text: "Nope. WiFi is just between your phone and the unit \u2014 no internet required. Works in a basement with no signal.",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),

      // Objection 5
      new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "\u201CWhat about walls / backsplashes?\u201D", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 200 },
        indent: { left: 360, right: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
        children: [new TextRun({
          text: "Same thing. Tilt the tripod, the keystone correction adjusts automatically. Works on floors, walls, shower niches \u2014 any flat surface.",
          font: "Arial", size: 22, italics: true, color: MID,
        })],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/Sims/Desktop/layit/sales/LayIt_Feature_Pitch.docx", buffer);
  console.log("Created: LayIt_Feature_Pitch.docx");
});
