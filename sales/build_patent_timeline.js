const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak
} = require("docx");

const GREEN = "2C5F2D";
const DARK = "1E1E1E";
const MID = "444444";
const LIGHT_BG = "F5F7F5";
const NAVY = "1E2761";
const AMBER = "B85042";
const BORDER_COLOR = "CCCCCC";
const WHITE = "FFFFFF";

const border = { style: BorderStyle.SINGLE, size: 1, color: BORDER_COLOR };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: NAVY, space: 1 } },
  });
}

function spacer(pts = 120) {
  return new Paragraph({ spacing: { before: pts } });
}

function monthBlock(title, color, items) {
  const children = [];
  children.push(new Paragraph({
    spacing: { before: 280, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: color, space: 4 } },
    children: [new TextRun({ text: title, font: "Arial", size: 28, bold: true, color: color })],
  }));
  for (const item of items) {
    if (typeof item === "string") {
      children.push(new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { after: 60 },
        children: [new TextRun({ text: item, font: "Arial", size: 22, color: MID })],
      }));
    } else if (item.bold) {
      children.push(new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { after: 60 },
        children: [
          new TextRun({ text: item.bold, font: "Arial", size: 22, bold: true, color: DARK }),
          new TextRun({ text: " " + item.rest, font: "Arial", size: 22, color: MID }),
        ],
      }));
    }
  }
  return children;
}

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
        run: { size: 28, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "subBullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2013", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
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
          children: [new TextRun({ text: "LayIt Laser \u2014 Patent Action Plan", font: "Arial", size: 18, color: "999999", italics: true })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "CONFIDENTIAL  \u2022  ", font: "Arial", size: 16, color: "999999" }),
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
        children: [new TextRun({ text: "LayIt Laser", font: "Arial", size: 48, bold: true, color: NAVY })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
        children: [new TextRun({ text: "Patent Filing Action Plan", font: "Arial", size: 32, color: DARK })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "12-Month Roadmap from Provisional to Utility", font: "Arial", size: 22, italics: true, color: MID })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "Last updated: March 15, 2026", font: "Arial", size: 20, color: "999999" })],
      }),

      divider(),

      // ===== OVERVIEW =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Overview")],
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({
          text: "You have two provisional patents ready to file. Filing starts a 12-month clock \u2014 by the end of that window, you convert to full utility patents. Here\u2019s the month-by-month game plan.",
          font: "Arial", size: 22, color: MID,
        })],
      }),

      // Two patents summary
      new Paragraph({
        spacing: { before: 160, after: 60 },
        children: [new TextRun({ text: "Patent #1: ", font: "Arial", size: 22, bold: true, color: NAVY }),
          new TextRun({ text: "Camera-Based Room Measurement for Tile Layout (22 claims)", font: "Arial", size: 22, color: MID })],
      }),
      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun({ text: "Patent #2: ", font: "Arial", size: 22, bold: true, color: NAVY }),
          new TextRun({ text: "Laser Projection Tile Installation System (27 claims)", font: "Arial", size: 22, color: MID })],
      }),

      divider(),

      // ===== MONTH-BY-MONTH TIMELINE =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Month-by-Month Timeline")],
      }),

      // MONTH 1
      ...monthBlock("Month 1  \u2014  File Provisionals (March 2026)", NAVY, [
        { bold: "File both provisional patents", rest: "via USPTO EFS-Web" },
        { bold: "Cost:", rest: "$80 per filing ($160 total) \u2014 micro-entity rate (80% off standard fees)" },
        "Select micro-entity status (you qualify as a solo inventor)",
        "Upload specification PDF + figures PDF for each patent",
        "Pay via credit/debit card and click Submit",
        { bold: "Record your application numbers and filing dates immediately", rest: "" },
        { bold: "Calendar the 12-month deadline", rest: "(March 2027) for utility conversion" },
        "Save confirmation receipts somewhere safe",
      ]),

      // MONTHS 2-4
      ...monthBlock("Months 2\u20134  \u2014  Build & Document (April\u2013June 2026)", GREEN, [
        "Continue developing the product \u2014 every improvement strengthens your patent position",
        "Keep the Patent Evidence Log updated with dated entries",
        "Save all calibration data, test results, and accuracy measurements",
        "Screenshot or video-record every milestone demo",
        "Commit code regularly with descriptive messages (these are timestamped evidence)",
        "Start collecting real-world test data from actual tile jobs",
        { bold: "Key goal:", rest: "Build a body of evidence showing reduction to practice" },
      ]),

      // MONTHS 5-7
      ...monthBlock("Months 5\u20137  \u2014  Refine & Demo (July\u2013September 2026)", GREEN, [
        "Have a working prototype you can demo to people",
        "Get video of the system working on a real tile job (huge for patent and marketing)",
        "Document any new features or improvements \u2014 these can be added to the utility filing",
        { bold: "Budget check:", rest: "Start setting aside ~$400 for PowerPatent + ~$860 for USPTO utility filing fees ($430 each, micro-entity)" },
      ]),

      // MONTHS 8-9
      ...monthBlock("Months 8\u20139  \u2014  Utility Prep (November\u2013December 2026)", AMBER, [
        { bold: "Use PowerPatent AI (~$199)", rest: "to convert your provisionals into full utility patent drafts" },
        "PowerPatent generates the utility application from your provisional \u2014 you review and refine",
        "Add any new claims for features developed since the provisional filing",
        "Export patent figures from your OpenSCAD models \u2014 free, already built",
        { bold: "Total prep cost:", rest: "~$400 for AI drafting, figures are free from your CAD files" },
      ]),

      // MONTHS 10-11
      ...monthBlock("Months 10\u201311  \u2014  File Utility Patents (January\u2013February 2027)", AMBER, [
        { bold: "File utility patent applications", rest: "before the 12-month provisional deadline" },
        "Claim priority from your provisional filing date",
        { bold: "Consider Track One prioritized examination", rest: "($625 per patent, micro-entity) \u2014 gets you a first action in ~6 months instead of 2+ years" },
        "Utility filing fee per patent (micro-entity): $70 filing + $160 search + $200 exam = $430",
        { bold: "Optional:", rest: "File PCT (international) if you want protection outside the US (~$3,000\u20134,000)" },
        "Double-check all claims match your current product capabilities",
      ]),

      // MONTH 12
      ...monthBlock("Month 12  \u2014  Provisionals Expire (March 2027)", NAVY, [
        { bold: "Your provisional patents expire", rest: "\u2014 this is normal and expected" },
        "All protection now comes from the utility patents you filed in months 10\u201311",
        "If you didn\u2019t file utility patents, you lose your priority date and patent-pending status",
        "Respond to any USPTO office actions promptly (usually 3-month deadline)",
      ]),

      // MONTHS 12-18
      ...monthBlock("Months 12\u201318  \u2014  Examination & Grant (March\u2013September 2027)", GREEN, [
        "USPTO examiner reviews your utility application",
        { bold: "With Track One:", rest: "First office action in ~6 months, possible grant in 6\u201312 months" },
        { bold: "Without Track One:", rest: "First office action in 18\u201324 months" },
        "Respond to any rejections or requests for clarification",
        "May need to narrow some claims \u2014 this is normal back-and-forth",
        { bold: "Goal:", rest: "Granted utility patents with strong claims covering your core technology" },
      ]),

      divider(),

      // ===== COST SUMMARY =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Cost Summary")],
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [5460, 2340, 1560],
        rows: [
          new TableRow({
            children: ["Item", "Cost", "When"].map((text, idx) => new TableCell({
              borders,
              width: { size: [5460, 2340, 1560][idx], type: WidthType.DXA },
              shading: { fill: NAVY, type: ShadingType.CLEAR },
              margins: cellMargins,
              children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: WHITE })] })],
            })),
          }),
          ...([
            ["File 2 provisional patents (micro-entity)", "$160", "Month 1"],
            ["PowerPatent AI utility drafts (x2)", "~$400", "Month 8\u20139"],
            ["Patent figures (exported from OpenSCAD)", "Free", "Month 8\u20139"],
            ["File 2 utility patents (micro-entity, $430 each)", "$860", "Month 10\u201311"],
            ["Track One prioritized exam (optional, $625 each x2)", "$1,250", "Month 10\u201311"],
            ["PCT international filing (optional)", "$3,000\u20134,000", "Month 10\u201311"],
          ]).map(cells => new TableRow({
            children: cells.map((text, idx) => new TableCell({
              borders,
              width: { size: [5460, 2340, 1560][idx], type: WidthType.DXA },
              shading: idx === 0 ? { fill: LIGHT_BG, type: ShadingType.CLEAR } : undefined,
              margins: cellMargins,
              children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20, bold: idx === 0, color: DARK })] })],
            })),
          })),
          // TOTAL ROW - Minimum
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 5460, type: WidthType.DXA },
                shading: { fill: "E8F0E8", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "TOTAL \u2014 Minimum path (no Track One, no PCT)", font: "Arial", size: 20, bold: true, color: GREEN })] })],
              }),
              new TableCell({
                borders, width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "E8F0E8", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "$1,420", font: "Arial", size: 20, bold: true, color: GREEN })] })],
              }),
              new TableCell({
                borders, width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "E8F0E8", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "", font: "Arial", size: 20 })] })],
              }),
            ],
          }),
          // TOTAL ROW - With Track One
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 5460, type: WidthType.DXA },
                shading: { fill: "E8F0E8", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "TOTAL \u2014 With Track One (recommended)", font: "Arial", size: 20, bold: true, color: GREEN })] })],
              }),
              new TableCell({
                borders, width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "E8F0E8", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "$2,670", font: "Arial", size: 20, bold: true, color: GREEN })] })],
              }),
              new TableCell({
                borders, width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "E8F0E8", type: ShadingType.CLEAR }, margins: cellMargins,
                children: [new Paragraph({ children: [new TextRun({ text: "", font: "Arial", size: 20 })] })],
              }),
            ],
          }),
        ],
      }),

      spacer(200),

      // Cost tiers
      new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "Minimum to protect your IP right now:", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 60 },
        indent: { left: 360 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: GREEN, space: 8 } },
        children: [new TextRun({ text: "$160 \u2014 file both provisionals this month", font: "Arial", size: 24, bold: true, color: GREEN })],
      }),

      spacer(),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Full path with AI drafting + Track One:", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 60 },
        indent: { left: 360 },
        children: [new TextRun({ text: "~$2,670 total over 12 months", font: "Arial", size: 22, color: MID })],
      }),

      new Paragraph({
        spacing: { after: 80 },
        children: [new TextRun({ text: "Minimum path (no Track One, no PCT):", font: "Arial", size: 22, bold: true, color: DARK })],
      }),
      new Paragraph({
        spacing: { after: 60 },
        indent: { left: 360 },
        children: [new TextRun({ text: "~$1,420 total over 12 months", font: "Arial", size: 22, color: MID })],
      }),

      divider(),

      // ===== FILING CHECKLIST =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Filing Checklist (Month 1)")],
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "Do this for EACH of the two patents:", font: "Arial", size: 22, italics: true, color: MID })],
      }),

      ...([
        "Go to USPTO EFS-Web (efs-my.uspto.gov)",
        "Create an account if you don\u2019t have one",
        "Start a new provisional patent application",
        "Upload the specification PDF (the patent document)",
        "Upload the figures PDF (patent drawings)",
        "Select \u201CMicro Entity\u201D status ($80 filing fee)",
        "Fill in inventor info (your name, address)",
        "Pay $80 via credit/debit card",
        "Click Submit",
        "Save the confirmation page and application number",
        "Calendar March 2027 as your utility conversion deadline",
        "You\u2019re done \u2014 you now have \u201CPatent Pending\u201D status",
      ]).map((text, idx) => new Paragraph({
        numbering: { reference: "numbers", level: 0 },
        spacing: { after: 60 },
        children: [new TextRun({ text, font: "Arial", size: 22, color: MID })],
      })),

      divider(),

      // ===== KEY DATES =====
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Key Dates to Remember")],
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 6240],
        rows: [
          new TableRow({
            children: ["Date", "Action"].map((text, idx) => new TableCell({
              borders,
              width: { size: [3120, 6240][idx], type: WidthType.DXA },
              shading: { fill: NAVY, type: ShadingType.CLEAR },
              margins: cellMargins,
              children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: WHITE })] })],
            })),
          }),
          ...([
            ["March 2026", "File both provisional patents ($160)"],
            ["March 2027", "DEADLINE: File utility patents or lose priority date"],
            ["~September 2027", "Expected first office action (with Track One)"],
            ["~March 2028", "Possible patent grant (with Track One)"],
          ]).map(cells => new TableRow({
            children: cells.map((text, idx) => new TableCell({
              borders,
              width: { size: [3120, 6240][idx], type: WidthType.DXA },
              margins: cellMargins,
              children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20, bold: idx === 0, color: DARK })] })],
            })),
          })),
        ],
      }),

      spacer(300),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200 },
        children: [new TextRun({ text: "Step one: file the provisionals. Everything else follows from there.", font: "Arial", size: 24, italics: true, color: NAVY })],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/Sims/Desktop/layit/patent/LayIt_Patent_Action_Plan.docx", buffer);
  console.log("Created: LayIt_Patent_Action_Plan.docx");
});
