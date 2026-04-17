#!/usr/bin/env python3
"""Generate LayIt Laser LEGO-Style Assembly Guide PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether, HRFlowable
)
from reportlab.lib import colors
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "LayIt_Laser_Assembly_Guide.pdf")

# Colors
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#0f3460")
GREEN = HexColor("#27ae60")
RED = HexColor("#e74c3c")
AMBER = HexColor("#f39c12")
BLUE = HexColor("#2980b9")
LIGHT = HexColor("#f5f5f5")
TABLE_HDR = HexColor("#2c3e50")
TABLE_ALT = HexColor("#ecf0f1")
STEP_BG = HexColor("#eaf2f8")
CHECK_GREEN = HexColor("#d5f5e3")
WARN_BG = HexColor("#fdedec")


def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=letter,
        topMargin=0.7*inch, bottomMargin=0.6*inch,
        leftMargin=0.7*inch, rightMargin=0.7*inch
    )
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle('CoverTitle', parent=styles['Title'],
        fontSize=30, leading=36, textColor=DARK, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle('CoverSub', parent=styles['Normal'],
        fontSize=16, leading=20, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('CoverTagline', parent=styles['Normal'],
        fontSize=12, leading=16, textColor=GREEN, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('Section', parent=styles['Heading1'],
        fontSize=20, leading=24, textColor=DARK, spaceBefore=16, spaceAfter=10))
    styles.add(ParagraphStyle('Sub', parent=styles['Heading2'],
        fontSize=13, leading=16, textColor=ACCENT, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6))
    styles.add(ParagraphStyle('BodyBold', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('StepTitle', parent=styles['Normal'],
        fontSize=14, leading=18, textColor=white, fontName='Helvetica-Bold',
        spaceAfter=4))
    styles.add(ParagraphStyle('StepBody', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=3, leftIndent=8))
    styles.add(ParagraphStyle('Check', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=GREEN, spaceAfter=3, leftIndent=8,
        fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('Warn', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=RED, spaceAfter=3, leftIndent=8,
        fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('Tip', parent=styles['Normal'],
        fontSize=9.5, leading=13, textColor=BLUE, spaceAfter=6, leftIndent=8,
        fontName='Helvetica-Oblique'))
    styles.add(ParagraphStyle('ChecklistItem', parent=styles['Normal'],
        fontSize=10, leading=16, spaceAfter=2))
    styles.add(ParagraphStyle('Mono', parent=styles['Normal'],
        fontName='Courier', fontSize=8, leading=11, spaceAfter=6))

    story = []

    # ═══════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("LayIt Laser", styles['CoverTitle']))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Build Guide", styles['CoverSub']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("If You Can Build LEGO, You Can Build This.", styles['CoverTagline']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("A step-by-step soldering &amp; assembly manual", styles['Body']))
    story.append(Paragraph("designed for beginners. One connection at a time.", styles['Body']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Total build time: 2-3 hours", styles['Body']))
    story.append(Paragraph("Difficulty: Beginner-Intermediate", styles['Body']))
    story.append(Paragraph("Total solder joints: ~80", styles['Body']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Rev 1.1 | March 2026 | LayIt LLC", styles['CoverSub']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # BEFORE YOU START
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Before You Start", styles['Section']))
    story.append(Paragraph(
        "This guide walks you through building the LayIt Laser from a bag of parts to a working "
        "laser projection system. Every single solder joint is covered. We go in order from easiest "
        "to hardest, so by the time you reach the tricky parts, you'll have plenty of practice.",
        styles['Body']))
    story.append(Paragraph(
        "Take your time. A good solder joint takes 3 seconds. A bad one takes 30 minutes to fix. "
        "If something doesn't look right, stop and re-read the step. You've got this.",
        styles['Body']))
    story.append(Spacer(1, 6))

    # Golden rules
    story.append(Paragraph("The 5 Golden Rules of Soldering", styles['Sub']))
    rules = [
        "<b>1. Heat the pad AND the pin, not the solder.</b> Touch your iron to where the component leg meets the copper pad. Hold for 1-2 seconds. Then touch solder to the heated joint (not the iron). It should flow like water.",
        "<b>2. A good joint is shiny and volcano-shaped.</b> If it looks like a dull gray blob, reheat it.",
        "<b>3. Don't hold the iron on too long.</b> 3-5 seconds max. If it's not working, pull away, let it cool, and try again.",
        "<b>4. Short legs = happy life.</b> After soldering through-hole parts, clip the excess leg flush with the solder joint using flush cutters.",
        "<b>5. Check your work after every step.</b> It's 10x easier to fix a mistake right after you made it than after the whole board is assembled.",
    ]
    for r in rules:
        story.append(Paragraph(r, styles['Body']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 1: TOOLS
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 1: Tools You'll Need", styles['Section']))

    tools = [
        ["Tool", "Why You Need It", "Budget Option"],
        ["Soldering iron (temp controlled)", "The main event. Set to 350C / 660F.", "Pinecil ($26) or Hakko FX-888D ($100)"],
        ["Solder wire (0.8mm)", "60/40 or 63/37 leaded is MUCH easier for beginners than lead-free", "Any brand, 0.8mm diameter"],
        ["Flux pen (rosin)", "Makes solder flow better. Essential for the ESP32 module.", "MG Chemicals or Kester #951"],
        ["Flush cutters", "For trimming component legs after soldering", "Any $5-10 pair works"],
        ["Multimeter", "For checking your work. Continuity mode is your best friend.", "Any $15-20 meter with beep mode"],
        ["Helping hands / PCB holder", "Holds the board steady while you solder", "Third-hand tool or PCB vise"],
        ["Solder wick (desoldering braid)", "For fixing mistakes. Absorbs excess solder.", "Any brand, 2mm width"],
        ["Safety glasses", "Hot solder can spit. Protect your eyes.", "Any clear safety glasses"],
        ["Wire strippers", "For preparing wires to external components", "Any adjustable stripper"],
        ["Isopropyl alcohol + brush", "For cleaning flux residue when done", "90%+ IPA from pharmacy"],
    ]
    story.append(make_table(tools, col_widths=[1.8*inch, 2.5*inch, 2.5*inch]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 2: PARTS CHECKLIST
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 2: Parts Checklist", styles['Section']))
    story.append(Paragraph(
        "Lay out ALL your parts before starting. Check each one off. If anything is missing, "
        "don't start building - order the missing part first.", styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Resistors (tiny rectangles, usually tan/brown with markings)", styles['Sub']))
    resistors = [
        ["[  ]", "Qty", "Value", "Refs", "What It Does"],
        ["[  ]", "5", "10K Ohm", "R1, R2, R13, R14, R15", "Pull-up/pull-down resistors. Keep signals stable."],
        ["[  ]", "2", "10K Ohm", "R5, R7", "Op-amp input resistors. Set the signal level."],
        ["[  ]", "2", "24K Ohm", "R6, R8", "Op-amp feedback resistors. Set the gain (amplification)."],
        ["[  ]", "1", "4.7K Ohm", "R9", "Pulls laser TTL signal high when MOSFET is off."],
        ["[  ]", "1", "100 Ohm", "R10", "Limits current spike to MOSFET gate. Prevents ringing."],
        ["[  ]", "2", "4.7K Ohm", "R11, R12", "I2C pull-ups for camera communication."],
    ]
    story.append(make_table(resistors, col_widths=[0.4*inch, 0.4*inch, 0.8*inch, 1.5*inch, 3.5*inch]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Capacitors", styles['Sub']))
    caps = [
        ["[  ]", "Qty", "Value", "Refs", "What It Looks Like"],
        ["[  ]", "8", "100nF ceramic", "C2,C4,C6,C8,C9,C10,C11,C12", "Tiny tan/yellow rectangles. May say '104' on them."],
        ["[  ]", "1", "10uF ceramic", "C7", "Small tan rectangle, slightly bigger. May say '106'."],
        ["[  ]", "2", "22uF ceramic/tant.", "C3, C5", "Small rectangles or teardrop shapes (if tantalum)."],
        ["[  ]", "1", "470uF electrolytic", "C1", "TALL black cylinder with a white stripe. Has + and - legs!"],
    ]
    story.append(make_table(caps, col_widths=[0.4*inch, 0.4*inch, 1.1*inch, 1.8*inch, 3*inch]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("ICs &amp; Semiconductors", styles['Sub']))
    ics = [
        ["[  ]", "Qty", "Part", "Ref", "What It Looks Like"],
        ["[  ]", "1", "ESP32-S3-WROOM-1 N16R8", "U3", "Silver metal can with antenna. The brain of the whole thing."],
        ["[  ]", "1", "MCP4822 Dual DAC", "U4", "Black rectangle, 8 pins (4 per side). Has a dot/notch at pin 1."],
        ["[  ]", "1", "TL072 Dual Op-Amp", "U5", "Black rectangle, 8 pins (4 per side). Has a dot/notch at pin 1."],
        ["[  ]", "1", "AMS1117-5.0 regulator", "U1", "Small black part, 3 pins + big tab. Says '1117' and '5.0' on it."],
        ["[  ]", "1", "AMS1117-3.3 regulator", "U2", "Same as above but says '3.3'. Don't mix them up!"],
        ["[  ]", "1", "2N7000 MOSFET", "Q1", "Tiny black part, 3 pins, flat on one side. Controls the laser."],
        ["[  ]", "1", "SS34 Schottky Diode", "D1", "Small black rectangle with a SILVER STRIPE on one end."],
        ["[  ]", "1", "WS2812B RGB LED", "LED1", "Tiny white square (5mm) with 4 pads. Has a notched corner."],
    ]
    story.append(make_table(ics, col_widths=[0.4*inch, 0.35*inch, 1.8*inch, 0.4*inch, 3.7*inch]))

    story.append(PageBreak())
    story.append(Paragraph("Connectors &amp; Switches", styles['Sub']))
    conns = [
        ["[  ]", "Qty", "Part", "Ref", "What It Looks Like"],
        ["[  ]", "1", "DC Barrel Jack 5.5x2.1mm", "J1", "Metal cylinder, 3 pins. Where the power plugs in."],
        ["[  ]", "1", "JST-XH 3-Pin Header", "J3", "White plastic block with 3 metal pins. Laser plugs in here."],
        ["[  ]", "1", "JST-XH 6-Pin Header", "J4", "White plastic block with 6 metal pins. Galvos plug in here."],
        ["[  ]", "1", "FPC 24-Pin Connector", "J5", "Thin black connector with flip-up latch. Camera ribbon cable."],
        ["[  ]", "1", "4-Pin Male Header (UART)", "J6", "Strip of 4 straight pins. For programming the ESP32."],
        ["[  ]", "2", "Tactile Push Button", "SW1, SW2", "Small square buttons (6x6mm). BOOT and RESET."],
        ["[  ]", "1", "Microswitch", "SW3", "Small switch with lever. Safety interlock for the lid."],
        ["[  ]", "1", "PTC Fuse 3A", "F1", "Tiny orange/yellow rectangle. Resets itself after overcurrent."],
    ]
    story.append(make_table(conns, col_widths=[0.4*inch, 0.35*inch, 1.8*inch, 0.4*inch, 3.7*inch]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("External Components (connected with wires, not soldered to PCB)", styles['Sub']))
    ext = [
        ["[  ]", "Qty", "Part", "Notes"],
        ["[  ]", "1", "520nm 200mW Laser Module (Laserland 4060-530D-200)", "3 wires: +12V, TTL, GND"],
        ["[  ]", "1", "20K PPS Galvo Scanner Set + Driver Board", "Includes 2 motors, 2 mirrors, 1 driver"],
        ["[  ]", "1", "OV5640 5MP 160-degree Camera Module", "24-pin ribbon cable"],
        ["[  ]", "1", "12V 3A DC Power Adapter (5.5x2.1mm barrel)", "Wall adapter, center-positive"],
        ["[  ]", "2", "DIP-8 IC Socket (RECOMMENDED)", "For MCP4822 and TL072. Swap chips without desoldering!"],
        ["[  ]", "1", "USB-to-TTL Serial Cable (Adafruit or CP2102)", "For flashing firmware to the ESP32. Micro Center has them."],
    ]
    story.append(make_table(ext, col_widths=[0.4*inch, 0.35*inch, 3.5*inch, 2.5*inch]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 3: STEP-BY-STEP ASSEMBLY
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 3: Step-by-Step Assembly", styles['Section']))
    story.append(Paragraph(
        "We start with the easiest parts (resistors - impossible to mess up) and work our way "
        "to the hardest (ESP32 module). By the time you get there, you'll be a soldering pro.",
        styles['Body']))
    story.append(Spacer(1, 6))

    # ── PHASE 1: RESISTORS ──
    story.append(Paragraph("PHASE 1: Resistors", styles['Sub']))
    story.append(Paragraph(
        "Resistors have NO polarity - you literally cannot put them in backwards. "
        "They're the perfect warm-up. Think of them as training wheels for your soldering iron.",
        styles['Tip']))

    add_step(story, styles, 1, "Install the 10K Pull-Up Resistors",
        grab="5x 10K Ohm resistors (R1, R2, R13, R14, R15) - tiny rectangles, usually marked '1002' or '10K'",
        where="R1, R2 near the ESP32 footprint. R13, R14 near the camera connector. R15 near the safety switch.",
        how="No polarity! Either direction works. Bend the legs 90 degrees, push through the holes, flip the board, solder both legs, then clip the excess.",
        solder=10,
        check="Each resistor sits flat against the board. Both legs have shiny volcano-shaped joints.",
        watch="Don't accidentally bridge two nearby pads with excess solder.")

    add_step(story, styles, 2, "Install the Op-Amp Resistors",
        grab="2x 10K (R5, R7) and 2x 24K (R6, R8) - DON'T MIX THEM UP! Check markings.",
        where="R5, R6 near one half of the TL072. R7, R8 near the other half. These set the gain for the galvo signals.",
        how="No polarity. R5 and R7 are the INPUT resistors (10K). R6 and R8 are the FEEDBACK resistors (24K). Make sure you put the right value in the right spot!",
        solder=8,
        check="Verify values are in correct positions: 10K in R5/R7, 24K in R6/R8.",
        watch="Swapping R5/R6 or R7/R8 will give wrong galvo voltage. Double-check the markings!")

    add_step(story, styles, 3, "Install the Remaining Resistors",
        grab="1x 4.7K (R9), 1x 100 Ohm (R10), 2x 4.7K (R11, R12)",
        where="R9 near the laser circuit area. R10 near the MOSFET. R11, R12 near the camera connector.",
        how="No polarity. R10 (100 Ohm) is a different value - don't mix it with the 4.7K ones!",
        solder=8,
        check="All 13 resistors installed. Board should look like it's growing tiny metal caterpillars.",
        tip="You've just completed 26 solder joints. You're basically a pro now.")

    story.append(PageBreak())

    # ── PHASE 2: CERAMIC CAPACITORS ──
    story.append(Paragraph("PHASE 2: Ceramic Capacitors", styles['Sub']))
    story.append(Paragraph(
        "Like resistors, ceramic caps have NO polarity. They're the little 'shock absorbers' "
        "that keep electrical noise from messing up your circuits. Think of them like the "
        "suspension on a car - you don't notice them until they're missing.",
        styles['Tip']))

    add_step(story, styles, 4, "Install the 100nF Bypass Capacitors",
        grab="8x 100nF ceramic capacitors (C2, C4, C6, C8, C9, C10, C11, C12) - tiny, may say '104'",
        where="Scattered across the board, usually near each IC's power pins. One near each chip.",
        how="No polarity! Same technique as resistors. Place CLOSE to the IC they serve.",
        solder=16,
        check="All 8 caps seated flat. Each IC position has its bypass cap nearby.",
        watch="These are small and like to fly away. Hold them down while you solder the first leg.")

    add_step(story, styles, 5, "Install the 10uF and 22uF Capacitors",
        grab="1x 10uF ceramic (C7), 2x 22uF ceramic or tantalum (C3, C5)",
        where="C7 near the ESP32. C3 near U1 (5V regulator). C5 near U2 (3.3V regulator).",
        how="Ceramic = no polarity. If tantalum (teardrop shape with stripe): STRIPE MARKS POSITIVE. Match + to the + marking on the board.",
        solder=6,
        check="If using tantalum caps, stripe (positive) matches board marking.",
        watch="Tantalum caps CAN EXPLODE if installed backwards. If in doubt, use ceramic.")

    # ── PHASE 3: IC SOCKETS ──
    story.append(Paragraph("PHASE 3: IC Sockets (Highly Recommended!)", styles['Sub']))
    story.append(Paragraph(
        "DIP sockets let you plug ICs in and out without soldering them directly. If a chip "
        "is bad, you just pull it out and pop in a new one. It's like a seat for your chip.",
        styles['Tip']))

    add_step(story, styles, 6, "Install DIP-8 Socket for MCP4822 DAC",
        grab="1x DIP-8 socket - black plastic rectangle with 8 holes and a NOTCH on one end",
        where="U4 position on the PCB (where the MCP4822 will eventually live).",
        how="NOTCH ON THE SOCKET MUST MATCH THE NOTCH MARKING ON THE PCB. This sets the orientation for pin 1. Tack-solder one corner pin first, check alignment, then solder the rest.",
        solder=8,
        check="Socket sits flat. Notch matches PCB marking. All 8 pins soldered.")

    add_step(story, styles, 7, "Install DIP-8 Socket for TL072 Op-Amp",
        grab="1x DIP-8 socket (identical to the one you just did)",
        where="U5 position on the PCB.",
        how="Same as Step 6. NOTCH MATCHES PCB MARKING.",
        solder=8,
        check="Both sockets installed. Both notches oriented correctly.")

    story.append(PageBreak())

    # ── PHASE 4: SEMICONDUCTORS ──
    story.append(Paragraph("PHASE 4: Semiconductors (Polarity Matters!)", styles['Sub']))
    story.append(Paragraph(
        "From here on, ORIENTATION MATTERS. These parts can be damaged if installed backwards. "
        "Read each step carefully. When in doubt, don't solder - ask someone or look up the datasheet.",
        styles['Tip']))

    add_step(story, styles, 8, "Install the SS34 Schottky Diode",
        grab="1x SS34 diode (D1) - small black rectangle with a SILVER STRIPE on one end",
        where="D1 position, near the barrel jack / power input area.",
        how="THE SILVER STRIPE MUST MATCH THE BAND MARKING ON THE PCB. The stripe indicates the cathode (negative) end. This is your reverse-polarity protection - it saves the board if someone plugs power in backwards.",
        solder=2,
        check="Silver stripe on the diode matches the band/line on the PCB silkscreen.",
        watch="BACKWARDS = NO PROTECTION. Your board could be damaged by reverse polarity.")

    add_step(story, styles, 9, "Install the 2N7000 MOSFET",
        grab="1x 2N7000 (Q1) - tiny black part with 3 legs and one FLAT side",
        where="Q1 position, near the laser driver circuit.",
        how="THE FLAT SIDE MUST MATCH THE FLAT SIDE ON THE PCB SILKSCREEN. Pins from left to right (flat side facing you): Source, Gate, Drain. This little guy switches 12V to control the laser.",
        solder=3,
        check="Flat side matches PCB marking. Part doesn't wobble.",
        watch="This part is static-sensitive. Touch a grounded metal object before handling it.")

    add_step(story, styles, 10, "Install the Voltage Regulators",
        grab="1x AMS1117-5.0 (U1) and 1x AMS1117-3.3 (U2) - small black parts with 3 pins and a big metal tab",
        where="U1 and U2 positions. Usually near each other, between the power input and the ESP32.",
        how="THE METAL TAB ORIENTATION MUST MATCH THE PCB SILKSCREEN. The tab also serves as a heatsink. U1 says '5.0' on it. U2 says '3.3'. DON'T SWAP THEM.",
        solder=6,
        check="U1 (5.0) and U2 (3.3) are in the correct positions. Tabs match board marking.",
        watch="If you swap them, 5V will go where 3.3V should be and you'll fry the ESP32. Check twice!")

    add_step(story, styles, 11, "Install the PTC Fuse",
        grab="1x PTC Fuse 3A (F1) - small orange/yellow rectangle",
        where="F1 position, in the power input path between the diode and the 12V rail.",
        how="No polarity - either direction works. This is your overcurrent protection. If something shorts, it heats up and stops conducting. When the short is fixed, it cools down and resets itself. Like a self-healing circuit breaker.",
        solder=2,
        check="Seated flat. Good joints on both pads.")

    # ── BIG CAPACITOR ──
    add_step(story, styles, 12, "Install the Electrolytic Capacitor",
        grab="1x 470uF 25V electrolytic (C1) - the BIG black cylinder with a white stripe",
        where="C1 position, near the power input section.",
        how="THIS HAS POLARITY! The white stripe on the cap marks the NEGATIVE (-) leg. The LONGER leg is POSITIVE (+). Match the + leg to the + marking on the PCB.",
        solder=2,
        check="White stripe (negative) matches the - side on the PCB. Longer leg in the + hole.",
        watch="Installing backwards can cause the cap to POP and leak. Not dangerous but unpleasant and smelly.")

    story.append(PageBreak())

    # ── PHASE 5: CONNECTORS ──
    story.append(Paragraph("PHASE 5: Connectors", styles['Sub']))
    story.append(Paragraph(
        "Connectors are bulky but easy. They usually only fit one way. "
        "Solder one pin first, check alignment, then do the rest.",
        styles['Tip']))

    add_step(story, styles, 13, "Install the DC Barrel Jack",
        grab="1x DC Barrel Jack (J1) - metal cylinder with 3 through-hole pins",
        where="J1 position, usually at the edge of the board.",
        how="Push it in until it clicks/sits flush. It only fits one way. This is where you plug in the 12V power adapter.",
        solder=3,
        check="Jack is flush with the board edge. Solid joints on all 3 pins.")

    add_step(story, styles, 14, "Install the JST-XH Headers",
        grab="1x 3-pin JST-XH (J3) and 1x 6-pin JST-XH (J4) - white plastic blocks with pins",
        where="J3 connects to the laser module. J4 connects to the galvo driver board.",
        how="Push fully into holes. The plastic housing should sit flat on the board. Solder one pin, check alignment, then the rest.",
        solder=9,
        check="Both connectors are straight and fully seated.",
        watch="If they go in crooked, your cables won't plug in properly later.")

    add_step(story, styles, 15, "Install the UART Programming Header",
        grab="1x 4-pin male header strip (J6) - break off 4 pins from your header strip",
        where="J6 position, near the ESP32. This is how you'll connect the USB-to-TTL serial cable to flash firmware.",
        how="Push the 4 pins through the holes (long side up, short side soldered to PCB). Solder all 4 pins. The pins are labeled TX, RX, 3.3V, GND on the silkscreen.",
        solder=4,
        check="All 4 pins straight and solidly soldered. Header sits flat.",
        tip="This replaces USB-C for programming. Way easier to solder and works great with a $16 Adafruit USB-to-TTL cable from Micro Center.")

    add_step(story, styles, 16, "Install the Tactile Switches",
        grab="2x tactile push buttons (SW1, SW2) - small square buttons, 6x6mm",
        where="SW1 = BOOT button. SW2 = RESET button. Both near the ESP32.",
        how="They snap into place - pins only fit one way. Push down firmly until flush.",
        solder=8,
        check="Both buttons click when pressed and spring back.")

    add_step(story, styles, 17, "Install the FPC Camera Connector",
        grab="1x FPC 24-pin connector (J5) - thin black connector with a flip-up latch",
        where="J5 position. This is where the camera ribbon cable plugs in.",
        how="This has very fine pins. Use flux! Tack one end pin first, verify alignment under magnification if possible, then solder the rest one at a time.",
        solder=24,
        check="All pins soldered with no bridges between them. Latch still flips up and down freely.",
        watch="This is fiddly. Use plenty of flux. If you bridge two pins, use solder wick to clean up.")

    story.append(PageBreak())

    # ── PHASE 6: LED ──
    story.append(Paragraph("PHASE 6: Status LED", styles['Sub']))

    add_step(story, styles, 18, "Install the WS2812B RGB LED",
        grab="1x WS2812B (LED1) - tiny white/clear square (5x5mm) with a notched corner",
        where="LED1 position. This is the status indicator that shows what the system is doing.",
        how="THE NOTCHED CORNER INDICATES PIN 1 (usually GND or VDD - check your PCB silkscreen). Use flux on the pads. This is an SMD part - apply solder to one pad first, then place the LED and reheat to tack it down. Then solder the remaining 3 pads.",
        solder=4,
        check="Notched corner matches PCB marking. All 4 pads soldered with no bridges.",
        watch="Heat-sensitive! Don't hold the iron on for more than 2 seconds per pad.")

    # ── PHASE 7: THE BIG ONE - ESP32 ──
    story.append(Paragraph("PHASE 7: The ESP32 Module (The Boss Level)", styles['Sub']))
    story.append(Paragraph(
        "You've been training for this. 60+ solder joints of practice have led to this moment. "
        "The ESP32-S3 module has castellated pads (half-moon shaped pads on the edges). "
        "It's not as scary as it looks. Deep breath. Flux is your best friend here.",
        styles['Tip']))

    add_step(story, styles, 19, "Install the ESP32-S3-WROOM-1 Module",
        grab="1x ESP32-S3-WROOM-1 N16R8 (U3) - the silver metal can with the antenna sticking out",
        where="U3 position. The biggest footprint on the board. The antenna end should face toward the edge of the board (away from other components).",
        how="""This is a surface-mount module with castellated edge pads. Here's the technique:

1. Apply flux generously to ALL the PCB pads
2. Pre-tin (add a thin layer of solder to) each PCB pad
3. Place the module on the pads, carefully aligning pin 1 (marked with a dot)
4. Tack-solder ONE corner pad to hold the module in place
5. Check alignment - all pads should line up with their castellations
6. If misaligned, reheat the tacked pad and gently nudge the module
7. Once aligned, solder each pad one at a time
8. Use the tip of the iron against both the PCB pad and the module castellation
9. Touch solder to the joint - it should wick into the castellation
10. Also solder the large ground pad on the bottom (if accessible)""",
        solder="~40 (varies by module variant)",
        check="Every castellation has a visible solder fillet connecting it to its PCB pad. No bridges between adjacent pads. Module is flat and level.",
        watch="Don't block the antenna! No copper, solder, or components within 10mm of the antenna end. Also: take breaks. This step might take 20-30 minutes and that's totally fine.")

    story.append(PageBreak())

    # ── PHASE 8: INSERT ICs ──
    story.append(Paragraph("PHASE 8: Insert the ICs into Their Sockets", styles['Sub']))
    story.append(Paragraph(
        "If you installed DIP sockets (Steps 6-7), now is the fun part - just push the chips in! "
        "No soldering needed. If you didn't use sockets, solder the ICs directly using the "
        "same technique as the sockets (notch orientation matters!).",
        styles['Tip']))

    add_step(story, styles, 20, "Insert the MCP4822 DAC into its Socket",
        grab="1x MCP4822 chip (U4) - 8-pin DIP with a dot/notch at pin 1",
        where="The DIP-8 socket at U4 that you soldered in Step 6.",
        how="NOTCH ON THE CHIP MUST MATCH THE NOTCH ON THE SOCKET (which matches the PCB). You may need to gently bend the legs slightly inward so they line up with the socket holes. Press firmly and evenly until it's fully seated.",
        solder=0,
        check="Chip is fully seated in socket. No pins are bent under. Notch matches.")

    add_step(story, styles, 21, "Insert the TL072 Op-Amp into its Socket",
        grab="1x TL072 chip (U5) - 8-pin DIP, looks identical to the MCP4822",
        where="The DIP-8 socket at U5.",
        how="Same as Step 20. Notch matches socket notch. DON'T PUT IT IN THE WRONG SOCKET!",
        solder=0,
        check="Both ICs installed in correct sockets. Both notches correct. Both fully seated.")

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 4: WIRING EXTERNAL COMPONENTS
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 4: Wiring External Components", styles['Section']))
    story.append(Paragraph(
        "The PCB is done! Now we connect the external modules. Grab your TUOFENG wire kit - "
        "we use all 6 colors. Here's what each color means:",
        styles['Body']))
    story.append(Spacer(1, 6))

    wire_cheat = [
        ["Wire Color", "What It Carries", "Easy Way to Remember"],
        ["RED", "+12V Power", "Red = hot = high voltage"],
        ["WHITE", "+5V Power", "White = calm = medium voltage"],
        ["YELLOW", "+3.3V Power", "Yellow = gentle = low voltage"],
        ["BLACK", "Ground (GND)", "Black = zero = return path"],
        ["BLUE", "SPI / Analog signals", "Blue = data highway (fast signals)"],
        ["GREEN", "Digital / I2C / Safety", "Green = go signal (on/off controls)"],
    ]
    story.append(make_table(wire_cheat))
    story.append(Paragraph(
        "<b>Pro tip:</b> Cut your wires to length BEFORE stripping and soldering. "
        "Leave an extra inch on each end - you can always trim shorter but you can't make a wire longer! "
        "Strip about 5mm (1/4 inch) of insulation off each end.",
        styles['Body']))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Use the JST connectors - "
        "they're designed to only plug in one way, so you can't mess up the orientation.",
        styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Laser Module (J3 - 3 Pin JST-XH)", styles['Sub']))
    laser_wiring = [
        ["J3 Pin", "Wire Color (typical)", "Connects To"],
        ["Pin 1", "RED wire (+12V)", "Laser module + (power)"],
        ["Pin 2", "GREEN wire (TTL signal)", "Laser module TTL input"],
        ["Pin 3", "BLACK wire (GND)", "Laser module - (ground)"],
    ]
    story.append(make_table(laser_wiring))
    story.append(Paragraph(
        "The Laserland 4060-530D-200 should come with a wiring diagram. Match the colors. "
        "If your wires are different colors, use a multimeter to identify +, TTL, and GND.",
        styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Galvo Driver Board (J4 - 6 Pin JST-XH)", styles['Sub']))
    galvo_wiring = [
        ["J4 Pin", "Wire Color", "Signal", "Connects To"],
        ["Pin 1", "BLUE wire", "X+ (analog)", "Galvo driver X-axis input +"],
        ["Pin 2", "BLUE wire", "X- (analog gnd)", "Galvo driver X-axis input -"],
        ["Pin 3", "BLUE wire", "Y+ (analog)", "Galvo driver Y-axis input +"],
        ["Pin 4", "BLUE wire", "Y- (analog gnd)", "Galvo driver Y-axis input -"],
        ["Pin 5", "RED wire", "+12V", "Galvo driver board power +"],
        ["Pin 6", "BLACK wire", "GND", "Galvo driver board power -"],
    ]
    story.append(make_table(galvo_wiring))
    story.append(Paragraph(
        "Your galvo driver board documentation will show its input pinout. Match the signals. "
        "The analog signals (X+/X-, Y+/Y-) come from the op-amp output through J4.",
        styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Camera Module (J5 - 24 Pin FPC)", styles['Sub']))
    story.append(Paragraph(
        "<b>1.</b> Flip up the FPC connector latch (the small brown/black tab on J5).<br/>"
        "<b>2.</b> Slide the camera ribbon cable in, contacts facing DOWN (toward the board).<br/>"
        "<b>3.</b> Push the latch back down to lock the cable in place.<br/>"
        "<b>4.</b> Gently tug the cable to confirm it's held securely.",
        styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Safety Interlock Switch (SW3)", styles['Sub']))
    story.append(Paragraph(
        "Mount the microswitch on the enclosure lid so that:<br/>"
        "<b>Lid ON</b> = switch is pressed (contacts CLOSED) = GPIO47 reads LOW = safe<br/>"
        "<b>Lid OFF</b> = switch released (contacts OPEN) = GPIO47 reads HIGH = laser killed<br/><br/>"
        "Connect the switch's COM and NC (Normally Closed) terminals to the SW3 pads on the PCB. "
        "Use about 6 inches of wire so the lid can open fully.",
        styles['Body']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 5: FLASHING FIRMWARE
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 5: Flashing Firmware", styles['Section']))
    story.append(Paragraph(
        "Before testing, you need to load the LayIt firmware onto the ESP32. "
        "This is done through the UART header (J6) using your USB-to-TTL serial cable.",
        styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Connecting the USB-to-TTL Cable", styles['Sub']))
    uart_wiring = [
        ["UART Header Pin (J6)", "Cable Wire", "Notes"],
        ["TX", "RX (receive)", "Board's TX connects to cable's RX (they cross over)"],
        ["RX", "TX (transmit)", "Board's RX connects to cable's TX"],
        ["3.3V", "3.3V (or VCC)", "Only if board is NOT powered by barrel jack"],
        ["GND", "GND", "Always connect this one"],
    ]
    story.append(make_table(uart_wiring))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>IMPORTANT:</b> TX and RX CROSS OVER. The board's TX pin talks TO the cable's RX pin, "
        "and vice versa. If you mix them up, nothing will happen (no damage, just no communication). "
        "Swap them and try again.",
        styles['Body']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Entering Download Mode", styles['Sub']))
    story.append(Paragraph(
        "<b>1.</b> Connect the USB-to-TTL cable to J6 (match the pins above).<br/>"
        "<b>2.</b> Plug the USB end into your computer.<br/>"
        "<b>3.</b> Hold down the BOOT button (SW1).<br/>"
        "<b>4.</b> While holding BOOT, press and release the RESET button (SW2).<br/>"
        "<b>5.</b> Release the BOOT button.<br/>"
        "<b>6.</b> The ESP32 is now in download mode, ready to receive firmware.<br/>"
        "<b>7.</b> Use the LayIt firmware tool (or esptool.py) to flash the firmware.<br/>"
        "<b>8.</b> After flashing, press RESET to boot into normal mode.",
        styles['Body']))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "After the first flash, future firmware updates can be done over WiFi (OTA) - "
        "no cable needed!",
        styles['Tip']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 6: TESTING YOUR BUILD
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 6: Testing Your Build", styles['Section']))
    story.append(Paragraph(
        "DO NOT plug in power yet! First, we check for mistakes. A few minutes of testing now "
        "can save you from letting the magic smoke out of your components.",
        styles['Body']))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Pre-Power Checks (Multimeter in Continuity/Beep Mode)", styles['Sub']))
    checks = [
        "[  ]  Check +12V rail to GND: should NOT beep (no short circuit)",
        "[  ]  Check +5V rail to GND: should NOT beep (no short)",
        "[  ]  Check +3.3V rail to GND: should NOT beep (no short)",
        "[  ]  Check barrel jack + to +12V rail (after diode): SHOULD beep (connected)",
        "[  ]  Check each IC socket: no adjacent pins beeping (no solder bridges)",
        "[  ]  Visual inspection: look for solder bridges, cold joints, missing connections",
    ]
    for c in checks:
        story.append(Paragraph(c, styles['ChecklistItem']))
    story.append(Spacer(1, 10))

    story.append(Paragraph("The Smoke Test (First Power-On)", styles['Sub']))
    story.append(Paragraph(
        "<b>1.</b> Remove the laser module from J3 (we test the board first, laser later).<br/>"
        "<b>2.</b> Remove the galvo connector from J4.<br/>"
        "<b>3.</b> Have your finger on the power adapter plug, ready to yank it out.<br/>"
        "<b>4.</b> Plug in the 12V adapter.<br/>"
        "<b>5.</b> WATCH and SMELL. If you see smoke or smell burning, UNPLUG IMMEDIATELY.<br/>"
        "<b>6.</b> If no smoke after 5 seconds, quickly check voltages:",
        styles['Body']))

    voltage_checks = [
        ["Test Point", "Expected", "Acceptable Range", "If Wrong"],
        ["+12V rail to GND", "~11.6V", "11.0-12.5V", "Check D1, F1, J1"],
        ["+5V rail to GND", "5.0V", "4.8-5.2V", "Check U1, C3, C4"],
        ["+3.3V rail to GND", "3.3V", "3.2-3.4V", "Check U2, C5, C6"],
    ]
    story.append(make_table(voltage_checks))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "If all three voltages check out: <b>CONGRATULATIONS!</b> Your power section works. "
        "The ESP32 should boot (you might see the status LED briefly flash). "
        "If not, check the 3.3V rail and the ESP32 solder joints.",
        styles['Body']))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════
    # SECTION 7: TROUBLESHOOTING
    # ═══════════════════════════════════════════════════
    story.append(Paragraph("Section 7: Troubleshooting", styles['Section']))
    story.append(Paragraph(
        "Something not working? Don't panic. 90% of problems are bad solder joints. "
        "Here's a quick diagnostic guide:", styles['Body']))
    story.append(Spacer(1, 8))

    troubles = [
        ["Symptom", "Most Likely Cause", "Fix"],
        ["No lights, nothing happens", "Power not reaching the board", "Check barrel jack solder. Check D1 orientation (silver stripe). Check F1. Verify 12V at the rail."],
        ["12V OK, but no 5V", "U1 (5V regulator) issue", "Check U1 solder joints and orientation (tab direction). Check C3. Verify U1 says '5.0' not '3.3'."],
        ["5V OK, but no 3.3V", "U2 (3.3V regulator) issue", "Check U2 solder joints. Verify U2 says '3.3'. Check C5."],
        ["ESP32 doesn't boot", "Bad solder joint on module", "Reflow all ESP32 castellated pads with flux. Check 3.3V at ESP32 power pin. Press RESET button."],
        ["Can't flash firmware", "UART wiring or boot mode", "Check TX/RX are crossed. Hold BOOT, press RESET, release BOOT. Try swapping TX/RX wires."],
        ["Status LED doesn't light", "LED orientation or bad joint", "Check notched corner orientation. Reflow pads. Verify 3.3V at LED power pin."],
        ["Laser doesn't fire", "MOSFET or wiring issue", "Check Q1 orientation (flat side). Check R9, R10. Verify TTL signal with multimeter. Check J3 wiring order."],
        ["Galvos don't move", "DAC or op-amp issue", "Check MCP4822 is in socket correctly (notch). Check TL072 (notch). Verify SPI connections. Check J4 wiring."],
        ["Galvos jitter/vibrate", "Noise on analog signal", "Add 100nF cap at galvo driver input. Check ground connections. Keep analog wires away from digital/power."],
        ["Camera not detected", "Ribbon cable or I2C issue", "Re-seat FPC ribbon (contacts down). Check R11, R12 pull-ups. Verify 3.3V at camera."],
    ]
    story.append(make_table(troubles, col_widths=[1.3*inch, 1.6*inch, 3.8*inch]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Still Stuck?", styles['Sub']))
    story.append(Paragraph(
        "Take a photo of your board (both sides) and your solder joints. Post it to the LayIt "
        "community or send it to support. A fresh pair of eyes almost always spots the issue. "
        "Remember: everyone's first board has a few hiccups. That's how you learn!",
        styles['Body']))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="80%", thickness=2, color=GREEN))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "You did it. From a bag of parts to a working laser projection system. "
        "Now slide it into the 3D-printed enclosure, put on its rubber jacket, "
        "and go project some tile layouts!",
        styles['Body']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Happy Building!", styles['CoverSub']))
    story.append(Paragraph("- The LayIt Team", styles['CoverTagline']))

    doc.build(story)
    print(f"Created: {OUTPUT}")


def add_step(story, styles, num, title, grab, where, how, solder, check, watch=None, tip=None):
    """Add a formatted assembly step."""
    elements = []

    # Step header
    header_data = [[Paragraph(f"STEP {num}: {title}", styles['StepTitle'])]]
    header_table = Table(header_data, colWidths=[6.8*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6, 6, 0, 0]),
    ]))
    elements.append(header_table)

    # Step body
    body_items = []
    body_items.append(Paragraph(f"<b>GRAB:</b> {grab}", styles['StepBody']))
    body_items.append(Paragraph(f"<b>WHERE:</b> {where}", styles['StepBody']))
    body_items.append(Paragraph(f"<b>HOW:</b> {how}", styles['StepBody']))
    body_items.append(Paragraph(f"<b>SOLDER:</b> {solder} joints", styles['StepBody']))
    body_items.append(Spacer(1, 4))
    body_items.append(Paragraph(f"CHECK: {check}", styles['Check']))
    if watch:
        body_items.append(Paragraph(f"WATCH OUT: {watch}", styles['Warn']))
    if tip:
        body_items.append(Paragraph(f"TIP: {tip}", styles['Tip']))

    body_data = [[body_items]]
    # Can't easily nest flowables in table cells with platypus, so just append directly
    elements.append(Spacer(1, 2))
    for item in body_items:
        elements.append(item)
    elements.append(Spacer(1, 10))

    story.extend(elements)


def make_table(data, col_widths=None):
    """Create a styled table."""
    if col_widths is None:
        available = 6.8 * inch
        num_cols = len(data[0])
        col_widths = [available / num_cols] * num_cols

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HDR),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdc3c7")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t


if __name__ == "__main__":
    build()
