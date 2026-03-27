#!/usr/bin/env python3
"""
Convert LayIt patent markdown files to USPTO-ready PDFs.
Generates separate PDFs for specification and figures.
"""

import os
import re
import sys
from pathlib import Path

# Use venv's fpdf2
SCRIPT_DIR = Path(__file__).parent
VENV_SITE = SCRIPT_DIR / "room_scan_prototype" / "venv" / "lib"
for p in VENV_SITE.glob("python*/site-packages"):
    sys.path.insert(0, str(p))

from fpdf import FPDF


class PatentPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 5, f'Page {self.page_no()}', align='C')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'{self.page_no()}', align='C')

    def chapter_title(self, title, level=1):
        if level == 1:
            self.set_font('Helvetica', 'B', 14)
            self.ln(5)
        elif level == 2:
            self.set_font('Helvetica', 'B', 12)
            self.ln(3)
        else:
            self.set_font('Helvetica', 'B', 10)
            self.ln(2)
        self.multi_cell(0, 7, title)
        self.ln(3)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        # Handle basic formatting
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bold_text(self, text):
        self.set_font('Helvetica', 'B', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def italic_text(self, text):
        self.set_font('Helvetica', 'I', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)


def clean_markdown(text):
    """Remove markdown formatting for plain text output."""
    # Remove bold markers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic markers
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove code backticks
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Convert special chars that fpdf can't handle
    text = text.replace('\u2014', '--')  # em dash
    text = text.replace('\u2013', '-')   # en dash
    text = text.replace('\u201c', '"')   # left double quote
    text = text.replace('\u201d', '"')   # right double quote
    text = text.replace('\u2018', "'")   # left single quote
    text = text.replace('\u2019', "'")   # right single quote
    text = text.replace('\u2026', '...')  # ellipsis
    text = text.replace('\u00a7', 'Section ')  # section sign
    text = text.replace('\u00b1', '+/-')  # plus-minus
    text = text.replace('\u2264', '<=')  # less than or equal
    text = text.replace('\u2265', '>=')  # greater than or equal
    text = text.replace('\u2192', '->')  # right arrow
    text = text.replace('\u2190', '<-')  # left arrow
    text = text.replace('\u2194', '<->')  # left-right arrow
    text = text.replace('\u2022', '*')  # bullet
    text = text.replace('\u25a0', '*')  # black square
    text = text.replace('\u2713', 'X')  # check mark
    text = text.replace('\u2717', ' ')  # ballot x
    # Strip any remaining non-latin-1 characters
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text


def markdown_to_pdf(md_path, pdf_path, title=None):
    """Convert a markdown file to a formatted PDF."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = PatentPDF()
    pdf.add_page()

    # Title page
    if title:
        pdf.set_font('Helvetica', 'B', 16)
        pdf.ln(30)
        pdf.multi_cell(0, 10, title, align='C')
        pdf.ln(10)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 8, 'PROVISIONAL PATENT APPLICATION', align='C')
        pdf.ln(20)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, 'Filed: [DATE]', align='C')
        pdf.ln(6)
        pdf.cell(0, 6, 'Inventor: [INVENTOR FULL LEGAL NAME]', align='C')
        pdf.add_page()

    # Parse markdown line by line
    lines = content.split('\n')
    in_blockquote = False
    in_code = False
    buffer = []

    for line_num, line in enumerate(lines, 1):
        clean_line = clean_markdown(line)
        # Reset x position to left margin before each line
        pdf.set_x(pdf.l_margin)

        # Skip the markdown formatting hints (> Filing Notes, ---, etc.)
        if line.strip().startswith('> '):
            note_text = clean_markdown(line.strip()[2:]).strip()
            if note_text:
                pdf.set_font('Helvetica', 'I', 9)
                pdf.multi_cell(0, 4.5, note_text)
            continue

        if line.strip() == '---':
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            continue

        if line.strip().startswith('```'):
            in_code = not in_code
            continue

        if in_code:
            pdf.set_font('Courier', '', 9)
            pdf.multi_cell(0, 4, '  ' + clean_line)
            continue

        # Headers
        if line.startswith('# '):
            pdf.chapter_title(clean_line[2:], level=1)
        elif line.startswith('## '):
            pdf.chapter_title(clean_line[3:], level=1)
        elif line.startswith('### '):
            pdf.chapter_title(clean_line[4:], level=2)
        elif line.startswith('#### '):
            pdf.chapter_title(clean_line[5:], level=3)
        elif line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
            # Checklist items
            checked = '[x]' in line
            item_text = clean_markdown(line.strip()[5:].strip())
            pdf.set_font('Helvetica', '', 9)
            prefix = '[X] ' if checked else '[ ] '
            pdf.multi_cell(0, 4.5, '  ' + prefix + item_text)
        elif line.strip().startswith('- '):
            # Bullet points
            item_text = clean_markdown(line.strip()[2:])
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 5, '  * ' + item_text)
        elif len(line.strip()) > 2 and line.strip().startswith('(') and line.strip()[1].isalpha() and line.strip()[2] == ')':
            # Lettered list items like (a), (b), etc.
            pdf.body_text('    ' + clean_line.strip())
        elif line.strip().startswith('**Claim'):
            pdf.ln(3)
            pdf.bold_text(clean_line.strip())
        elif line.strip().startswith('**Step'):
            pdf.ln(2)
            pdf.bold_text(clean_line.strip())
        elif line.strip().startswith('**'):
            pdf.bold_text(clean_line.strip())
        elif clean_line.strip():
            pdf.body_text(clean_line.strip())
        else:
            pdf.ln(2)

    pdf.output(pdf_path)
    print(f"  Generated: {pdf_path}")


def generate_figures_pdf(output_path):
    """Combine all patent figures into a single PDF."""
    pdf = FPDF()

    fig_dir = Path(__file__).parent
    figures = [
        ('patent_fig1_architecture.png', 'FIG. 1 - System Architecture Block Diagram'),
        ('patent_fig2_pipeline.png', 'FIG. 2 - Camera Scan Processing Pipeline'),
        ('patent_fig3_features.png', 'FIG. 3 - Feature Detection Concept Diagram'),
        ('patent_fig4_autocorrect.png', 'FIG. 4 - Constraint-Aware Auto-Correction Flowchart'),
    ]

    for filename, caption in figures:
        fig_path = fig_dir / filename
        if not fig_path.exists():
            print(f"  WARNING: {filename} not found, skipping")
            continue

        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, caption, align='C')
        pdf.ln(15)

        # Add image centered, scaled to fit page
        page_w = pdf.w - 2 * pdf.l_margin
        pdf.image(str(fig_path), x=pdf.l_margin, w=page_w)

    pdf.output(output_path)
    print(f"  Generated: {output_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent

    print("Generating USPTO-ready PDFs...")
    print()

    # Camera scan provisional
    print("1. Camera Scan Provisional Patent:")
    markdown_to_pdf(
        base_dir / 'LayIt_Patent_CameraScan_Provisional.md',
        base_dir / 'LayIt_Patent_CameraScan_FILING_READY.pdf',
        title='Method and System for Automatic Room Geometry Extraction\n'
              'from Monocular Camera Images for Generation of\n'
              'Tile Installation Layouts'
    )

    # Laser projection provisional
    print("\n2. Laser Projection Provisional Patent:")
    markdown_to_pdf(
        base_dir / 'LayIt_Patent_Description.md',
        base_dir / 'LayIt_Patent_LaserProjection_FILING_READY.pdf',
        title='System and Method for Real-Time Laser Projection of\n'
              'Tile Installation Patterns with Vision-Based\n'
              'Self-Correcting Alignment'
    )

    # Patent figures
    print("\n3. Patent Figures:")
    generate_figures_pdf(base_dir / 'LayIt_Patent_Figures.pdf')

    # Evidence log
    print("\n4. Evidence Log:")
    markdown_to_pdf(
        base_dir / 'Patent_Evidence_Log.md',
        base_dir / 'LayIt_Patent_Evidence_Log.pdf',
        title='LayIt Patent\nInvention Evidence Log'
    )

    print("\n" + "=" * 60)
    print("  ALL PDFs GENERATED")
    print("=" * 60)
    print(f"\n  Filing-ready documents in: {base_dir}")
    print(f"\n  Files:")
    print(f"    1. LayIt_Patent_CameraScan_FILING_READY.pdf")
    print(f"    2. LayIt_Patent_LaserProjection_FILING_READY.pdf")
    print(f"    3. LayIt_Patent_Figures.pdf")
    print(f"    4. LayIt_Patent_Evidence_Log.pdf")
    print(f"\n  To file:")
    print(f"    1. Go to https://patentcenter.uspto.gov/")
    print(f"    2. Create account / log in")
    print(f"    3. New Submission > Provisional Application")
    print(f"    4. Upload specification PDF + figures PDF")
    print(f"    5. Select micro-entity ($180)")
    print(f"    6. Pay and submit")
    print(f"    7. Repeat for second provisional")
    print()
