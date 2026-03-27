#!/usr/bin/env python3
"""Convert patent markdown files to clean filing-ready PDFs using reportlab."""

import re
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Preformatted, Table, TableStyle, KeepTogether
)
from reportlab.lib import colors


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'PatentTitle', parent=styles['Title'],
        fontSize=16, leading=20, spaceAfter=6,
        fontName='Times-Bold', alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        'PatentHeading1', parent=styles['Heading1'],
        fontSize=14, leading=18, spaceBefore=18, spaceAfter=8,
        fontName='Times-Bold', textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        'PatentHeading2', parent=styles['Heading2'],
        fontSize=12, leading=16, spaceBefore=14, spaceAfter=6,
        fontName='Times-Bold', textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        'PatentHeading3', parent=styles['Heading3'],
        fontSize=11, leading=14, spaceBefore=10, spaceAfter=4,
        fontName='Times-Bold', textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        'PatentBody', parent=styles['Normal'],
        fontSize=11, leading=14, spaceAfter=6,
        fontName='Times-Roman', alignment=TA_JUSTIFY,
        firstLineIndent=0
    ))
    styles.add(ParagraphStyle(
        'PatentIndent', parent=styles['Normal'],
        fontSize=11, leading=14, spaceAfter=4,
        fontName='Times-Roman', leftIndent=36,
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        'PatentCode', parent=styles['Normal'],
        fontSize=9, leading=12, spaceAfter=6,
        fontName='Courier', leftIndent=36,
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        'PatentBlockquote', parent=styles['Normal'],
        fontSize=10, leading=13, spaceAfter=6,
        fontName='Times-Italic', leftIndent=36, rightIndent=36,
        alignment=TA_LEFT, textColor=colors.Color(0.3, 0.3, 0.3)
    ))
    styles.add(ParagraphStyle(
        'PatentBullet', parent=styles['Normal'],
        fontSize=11, leading=14, spaceAfter=3,
        fontName='Times-Roman', leftIndent=36, bulletIndent=18,
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        'PatentSubBullet', parent=styles['Normal'],
        fontSize=11, leading=14, spaceAfter=3,
        fontName='Times-Roman', leftIndent=54, bulletIndent=36,
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        'HRule', parent=styles['Normal'],
        fontSize=2, leading=4, spaceBefore=8, spaceAfter=8,
    ))

    return styles


def escape_xml(text):
    """Escape XML special chars but preserve our markup tags."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def process_inline(text):
    """Process inline markdown: bold, italic, code."""
    # Escape XML first
    text = escape_xml(text)

    # Bold+italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="9">\1</font>', text)
    # Em dash
    text = text.replace('&amp;mdash;', '\u2014')
    text = text.replace('&amp;ndash;', '\u2013')

    return text


def md_to_story(md_text, styles):
    """Convert markdown text to a list of reportlab flowables."""
    story = []
    lines = md_text.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                if code_text.strip():
                    story.append(Preformatted(code_text, styles['PatentCode']))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table detection
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                # Separator row, skip
                i += 1
                continue
            table_rows.append(cells)
            # Check if next line is also a table row
            if i + 1 < len(lines) and '|' in lines[i + 1] and lines[i + 1].strip().startswith('|'):
                i += 1
                continue
            else:
                # End of table, render it
                if table_rows:
                    # Process inline formatting in cells
                    processed_rows = []
                    for row in table_rows:
                        processed_rows.append([
                            Paragraph(process_inline(cell), styles['PatentBody'])
                            for cell in row
                        ])

                    num_cols = max(len(r) for r in processed_rows)
                    col_width = (6.5 * inch) / max(num_cols, 1)
                    col_widths = [col_width] * num_cols

                    # Pad rows to same length
                    for row in processed_rows:
                        while len(row) < num_cols:
                            row.append(Paragraph('', styles['PatentBody']))

                    t = Table(processed_rows, colWidths=col_widths)
                    t.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 6))
                    table_rows = []
                i += 1
                continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped in ('---', '***', '___'):
            story.append(Spacer(1, 4))
            # Draw a thin line using a table
            t = Table([['']], colWidths=[6.5 * inch], rowHeights=[1])
            t.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Headings
        if stripped.startswith('# '):
            text = process_inline(stripped[2:])
            story.append(Paragraph(text, styles['PatentTitle']))
            i += 1
            continue
        if stripped.startswith('## '):
            text = process_inline(stripped[3:])
            story.append(Paragraph(text, styles['PatentHeading1']))
            i += 1
            continue
        if stripped.startswith('### '):
            text = process_inline(stripped[4:])
            story.append(Paragraph(text, styles['PatentHeading2']))
            i += 1
            continue
        if stripped.startswith('#### '):
            text = process_inline(stripped[5:])
            story.append(Paragraph(text, styles['PatentHeading3']))
            i += 1
            continue

        # Blockquote
        if stripped.startswith('> '):
            quote_text = process_inline(stripped[2:])
            story.append(Paragraph(quote_text, styles['PatentBlockquote']))
            i += 1
            continue

        # Bullet/list items
        if stripped.startswith('- ') or stripped.startswith('* '):
            bullet_text = process_inline(stripped[2:])
            # Check indent level
            indent = len(line) - len(line.lstrip())
            if indent >= 2:
                story.append(Paragraph(
                    '\u2013 ' + bullet_text, styles['PatentSubBullet']
                ))
            else:
                story.append(Paragraph(
                    '\u2022 ' + bullet_text, styles['PatentBullet']
                ))
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            num = num_match.group(1)
            text = process_inline(num_match.group(2))
            story.append(Paragraph(
                f'{num}. {text}', styles['PatentBullet']
            ))
            i += 1
            continue

        # Indented code/preformatted (4+ spaces)
        if line.startswith('    ') and not stripped.startswith('-'):
            code_chunk = []
            while i < len(lines) and (lines[i].startswith('    ') or not lines[i].strip()):
                if lines[i].strip():
                    code_chunk.append(lines[i][4:])  # Remove 4-space indent
                else:
                    code_chunk.append('')
                i += 1
            # Remove trailing empty lines
            while code_chunk and not code_chunk[-1].strip():
                code_chunk.pop()
            if code_chunk:
                code_text = '\n'.join(code_chunk)
                story.append(Preformatted(escape_xml(code_text), styles['PatentCode']))
            continue

        # Checkbox items (from filing checklist)
        if stripped.startswith('- ['):
            check = '\u2611' if stripped.startswith('- [x]') else '\u2610'
            text = process_inline(stripped[5:].strip())
            story.append(Paragraph(
                f'{check} {text}', styles['PatentBullet']
            ))
            i += 1
            continue

        # Regular paragraph - collect continuation lines
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                break
            if next_line.startswith('#') or next_line.startswith('- ') or \
               next_line.startswith('* ') or next_line.startswith('> ') or \
               next_line in ('---', '***', '___') or \
               next_line.startswith('```') or \
               next_line.startswith('|') or \
               re.match(r'^\d+\.\s+', next_line) or \
               next_line.startswith('- ['):
                break
            # Check if it's indented code
            if lines[i].startswith('    '):
                break
            para_lines.append(next_line)
            i += 1

        full_text = ' '.join(para_lines)
        # Handle lettered sub-items like (a), (b), etc.
        if re.match(r'^\([a-z]\)', full_text):
            story.append(Paragraph(process_inline(full_text), styles['PatentIndent']))
        else:
            story.append(Paragraph(process_inline(full_text), styles['PatentBody']))

    return story


def convert_md_to_pdf(md_path, pdf_path, title="Patent Application"):
    """Convert a markdown file to a professional PDF."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    styles = create_styles()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        title=title,
        author="LayIt Laser"
    )

    story = md_to_story(md_text, styles)

    # Add page numbers
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawCentredString(letter[0] / 2, 0.5 * inch, text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Created: {pdf_path}")


if __name__ == '__main__':
    import os

    base = '/Users/Sims/Desktop/layit/patent'

    # Camera Scan Patent
    convert_md_to_pdf(
        os.path.join(base, 'LayIt_Patent_CameraScan_Provisional.md'),
        os.path.join(base, 'LayIt_Patent_CameraScan_Provisional.pdf'),
        title='Camera-Based Room Measurement for Tile Layout - Provisional Patent Application'
    )

    # Laser Projection Patent
    convert_md_to_pdf(
        os.path.join(base, 'LayIt_Patent_Description.md'),
        os.path.join(base, 'LayIt_Patent_LaserProjection_Provisional.pdf'),
        title='Laser Projection Tile Installation System - Provisional Patent Application'
    )
