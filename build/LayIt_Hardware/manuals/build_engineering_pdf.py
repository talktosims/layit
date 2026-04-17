#!/usr/bin/env python3
"""Generate LayIt Laser Engineering Schematic PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether
)
from reportlab.lib import colors
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "LayIt_Laser_Engineering_Schematic.pdf")

BRAND_DARK = HexColor("#1a1a2e")
BRAND_ACCENT = HexColor("#0f3460")
BRAND_HIGHLIGHT = HexColor("#e94560")
BRAND_LIGHT = HexColor("#f5f5f5")
TABLE_HEADER = HexColor("#2c3e50")
TABLE_ALT = HexColor("#ecf0f1")

def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=letter,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        leftMargin=0.75*inch, rightMargin=0.75*inch
    )
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle('CoverTitle', parent=styles['Title'],
        fontSize=28, leading=34, textColor=BRAND_DARK, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle('CoverSub', parent=styles['Normal'],
        fontSize=14, leading=18, textColor=BRAND_ACCENT, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle('SectionHead', parent=styles['Heading1'],
        fontSize=18, leading=22, textColor=BRAND_DARK, spaceBefore=20, spaceAfter=10,
        borderWidth=0, borderPadding=0))
    styles.add(ParagraphStyle('SubHead', parent=styles['Heading2'],
        fontSize=13, leading=16, textColor=BRAND_ACCENT, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9.5, leading=13, spaceAfter=6))
    styles.add(ParagraphStyle('Note', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=HexColor("#c0392b"), spaceAfter=6,
        leftIndent=12, borderLeftWidth=2, borderLeftColor=HexColor("#c0392b"), borderPadding=4))
    styles.add(ParagraphStyle('Mono', parent=styles['Normal'],
        fontName='Courier', fontSize=7.5, leading=10, spaceAfter=6))
    styles.add(ParagraphStyle('SmallBody', parent=styles['Normal'],
        fontSize=8.5, leading=11, spaceAfter=4))

    story = []

    # ─── COVER PAGE ───
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("LayIt Laser Projection System", styles['CoverTitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Engineering Schematic &amp; Circuit Reference", styles['CoverSub']))
    story.append(Spacer(1, 24))
    story.append(Paragraph("Rev 1.0 | March 2026", styles['CoverSub']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("CONFIDENTIAL — LayIt LLC", styles['CoverSub']))
    story.append(Spacer(1, 1.5*inch))

    info_data = [
        ["Document", "Engineering Schematic & Circuit Reference"],
        ["Revision", "1.0"],
        ["Date", "March 14, 2026"],
        ["MCU", "ESP32-S3-WROOM-1 (N16R8)"],
        ["Power", "12V DC 3A (Barrel Jack)"],
        ["Laser", "520nm 200mW (Laserland 4060-530D-200)"],
        ["Galvos", "20K PPS Dual-Axis Scanner Set"],
        ["Camera", "OV5640 5MP 160-degree DVP"],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), BRAND_ACCENT),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('RIGHTPADDING', (0, 0), (0, -1), 12),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, TABLE_ALT]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdc3c7")),
    ]))
    story.append(info_table)
    story.append(PageBreak())

    # ─── TABLE OF CONTENTS ───
    story.append(Paragraph("Table of Contents", styles['SectionHead']))
    toc_items = [
        "1. System Block Diagram",
        "2. Power Input & Protection",
        "3. Voltage Regulation",
        "4. ESP32-S3 Microcontroller — GPIO Pin Map",
        "5. DAC — MCP4822 (SPI, Dual 12-bit)",
        "6. Op-Amp Buffer/Amplifier — TL072",
        "7. Laser Module Driver",
        "8. Camera — OV5640 (DVP Interface)",
        "9. Safety Interlock",
        "10. Status LED — WS2812B",
        "11. USB-C (Debug/Firmware)",
        "12. Power Budget",
        "13. Complete Bill of Materials",
        "14. Design Review Checklist",
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles['Body']))
    story.append(PageBreak())

    # ─── 1. BLOCK DIAGRAM ───
    story.append(Paragraph("1. System Block Diagram", styles['SectionHead']))
    block_diagram = """\
                                +---------------------------------+
                                |       ESP32-S3-WROOM-1          |
                                |         (N16R8)                 |
  +----------+   +----------+  |                                 |
  | 12V DC   |-->| Reverse  |->| SPI Bus     +---------+        |
  | Barrel   |   | Polarity |  | (GPIO10-13) | MCP4822 |        |
  | Jack     |   | + Fuse   |  |             | Dual DAC|        |
  +----------+   +----------+  |             +----+----+        |
       |                       |                  |              |
       |         +--------+   |          +-------v-------+     |
       +-------->|AMS1117 |-->|  5V      |    TL072      |     |
       |         | -5.0   |   |          | Dual Op-Amp   |     |
       |         +--------+   |          +---+-------+---+     |
       |                      |              |       |          |
       |         +--------+   |        +-----v-+ +---v---+     |
       +-------->|AMS1117 |-->| 3.3V   |Galvo X| |Galvo Y|     |
       |         | -3.3   |   |        |Driver | |Driver |     |
       |         +--------+   |        +-------+ +-------+     |
       |                      |                                 |
       |    +-------------+   | GPIO14  +----------+            |
       +--->| 520nm 200mW |<--(MOSFET)--| Laser    |            |
       |    | Laser Module|   | TTL     | TTL Ctrl |            |
       |    +-------------+   |         +----------+            |
       |                      |  DVP Bus  +---------+           |
       |                      | (GPIO4-9  | OV5640  |           |
       |                      |  15-18    | Camera  |           |
       |                      |  45,46)   | 5MP 160 |           |
       |                      |           +---------+           |
       |    +----------+      | GPIO48    +----------+          |
       |    | USB-C    |      | (status)  | WS2812B  |          |
       |    | Debug    |--GPIO19,20       | RGB LED  |          |
       |    +----------+      |           +----------+          |
       |                      | GPIO47    +----------+          |
       |    | Safety   |      |(interlock)| BOOT/RST |          |
       |    | Switch   |      |           | Buttons  |          |
       |    +----------+      |           +----------+          |
       +------------------------------------------------------+"""
    story.append(Preformatted(block_diagram, styles['Mono']))
    story.append(PageBreak())

    # ─── 2. POWER INPUT & PROTECTION ───
    story.append(Paragraph("2. Power Input &amp; Protection", styles['SectionHead']))
    story.append(Paragraph("Components", styles['SubHead']))

    pwr_data = [
        ["Ref", "Part", "Value", "Purpose"],
        ["J1", "Barrel Jack", "5.5x2.1mm", "12V 3A DC input"],
        ["D1", "SS34 Schottky", "3A 40V", "Reverse polarity protection"],
        ["F1", "PTC Fuse", "3A hold", "Overcurrent protection (resettable)"],
        ["C1", "Electrolytic", "470uF 25V", "Bulk input filter"],
        ["C2", "Ceramic", "100nF 25V", "HF bypass"],
    ]
    story.append(make_table(pwr_data))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Circuit Path", styles['SubHead']))
    pwr_circuit = "J1 Pin1 (+) --> D1 Anode --> D1 Cathode --> F1 --> +12V RAIL\nJ1 Pin2 (-) --> GND RAIL"
    story.append(Preformatted(pwr_circuit, styles['Mono']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Design Notes:</b> SS34 drops ~0.4V under load (12V becomes ~11.6V at rail). "
        "PTC fuse protects against short circuits and resets automatically. "
        "470uF bulk cap handles galvo motor current transients.", styles['Body']))

    # ─── 3. VOLTAGE REGULATION ───
    story.append(Paragraph("3. Voltage Regulation", styles['SectionHead']))
    story.append(Paragraph("5V Rail (U1 - AMS1117-5.0)", styles['SubHead']))
    story.append(Paragraph("Powers: MCP4822 DAC (VDD), TL072 op-amp (V+)", styles['Body']))

    vreg5_data = [
        ["Ref", "Part", "Value", "Purpose"],
        ["U1", "AMS1117-5.0", "SOT-223", "12V to 5V LDO, 1A max"],
        ["C3", "Tantalum/Ceramic", "22uF 10V", "Output stability"],
        ["C4", "Ceramic", "100nF", "HF decoupling"],
    ]
    story.append(make_table(vreg5_data))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.3V Rail (U2 - AMS1117-3.3)", styles['SubHead']))
    story.append(Paragraph("Powers: ESP32-S3, Camera module, I2C pull-ups, status LED, safety interlock", styles['Body']))

    vreg3_data = [
        ["Ref", "Part", "Value", "Purpose"],
        ["U2", "AMS1117-3.3", "SOT-223", "5V to 3.3V LDO, 1A max"],
        ["C5", "Tantalum/Ceramic", "22uF 10V", "Output stability"],
        ["C6", "Ceramic", "100nF", "HF decoupling"],
    ]
    story.append(make_table(vreg3_data))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>ENGINEER NOTE - 5V to 3.3V Cascade:</b> U2 is fed from U1's 5V output (not directly from 12V). "
        "This reduces heat dissipation in U2. If U2 were fed from 12V directly: P = (12-3.3) x 0.7 = 6W "
        "(too hot for SOT-223). With 5V input: P = (5-3.3) x 0.7 = 1.2W (acceptable with thermal pad).",
        styles['Note']))

    # ─── 4. ESP32-S3 GPIO PIN MAP ───
    story.append(PageBreak())
    story.append(Paragraph("4. ESP32-S3 Microcontroller - GPIO Pin Map", styles['SectionHead']))

    gpio_data = [
        ["GPIO", "Function", "Dir", "Connected To", "Notes"],
        ["3V3", "Power", "IN", "+3.3V rail", "C7 (10uF) + C8 (100nF) bypass"],
        ["GND", "Ground", "-", "GND rail", "All ground pins connected"],
        ["EN", "Enable/Reset", "IN", "R1 (10K), C9, SW2", "Active HIGH"],
        ["0", "Boot Select", "IN", "R2 (10K), SW1", "LOW during reset = download"],
        ["1", "I2C SDA", "I/O", "Camera, R11 (4.7K)", "SCCB / I2C data"],
        ["2", "I2C SCL", "OUT", "Camera, R12 (4.7K)", "100/400kHz clock"],
        ["4", "CAM VSYNC", "IN", "Camera J5", "Frame sync"],
        ["5", "CAM HREF", "IN", "Camera J5", "Line valid"],
        ["6", "CAM PCLK", "IN", "Camera J5", "Pixel clock"],
        ["7", "CAM XCLK", "OUT", "Camera J5", "20MHz ref clock"],
        ["8", "CAM D6", "IN", "Camera J5", "Parallel data"],
        ["9", "CAM D7", "IN", "Camera J5", "Parallel data"],
        ["10", "SPI CS", "OUT", "MCP4822 /CS (pin 2)", "Active LOW"],
        ["11", "SPI MOSI", "OUT", "MCP4822 SDI (pin 4)", "Serial data to DAC"],
        ["12", "SPI CLK", "OUT", "MCP4822 SCK (pin 3)", "Up to 20MHz"],
        ["13", "DAC LDAC", "OUT", "MCP4822 /LDAC (pin 5)", "Latch pulse"],
        ["14", "LASER TTL", "OUT", "R10 (100R) to Q1", "HIGH=OFF, LOW=ON"],
        ["15", "CAM D2", "IN", "Camera J5", "Parallel data"],
        ["16", "CAM D3", "IN", "Camera J5", "Parallel data"],
        ["17", "CAM D4", "IN", "Camera J5", "Parallel data"],
        ["18", "CAM D5", "IN", "Camera J5", "Parallel data"],
        ["43", "UART TX", "OUT", "J6 TX pin", "Serial debug/FW upload"],
        ["44", "UART RX", "IN", "J6 RX pin", "Serial debug/FW upload"],
        ["45", "CAM D8", "IN", "Camera J5", "Parallel data"],
        ["46", "CAM D9", "IN", "Camera J5", "Parallel data"],
        ["47", "SAFETY", "IN", "SW3 + R15 (10K)", "LOW=safe, HIGH=kill"],
        ["48", "STATUS LED", "OUT", "WS2812B DIN", "Addressable RGB"],
    ]
    story.append(make_table(gpio_data, col_widths=[0.5*inch, 0.9*inch, 0.4*inch, 1.8*inch, 2.1*inch]))
    story.append(Spacer(1, 10))

    boot_data = [
        ["EN", "GPIO0", "Mode"],
        ["LOW", "X", "Reset (chip held in reset)"],
        ["HIGH", "HIGH", "Normal boot (run firmware)"],
        ["HIGH", "LOW", "Download mode (FW upload via UART)"],
    ]
    story.append(Paragraph("Boot Mode Selection", styles['SubHead']))
    story.append(make_table(boot_data))

    # ─── 5. DAC ───
    story.append(PageBreak())
    story.append(Paragraph("5. DAC - MCP4822 (SPI, Dual 12-bit)", styles['SectionHead']))
    story.append(Paragraph("Converts digital galvo coordinates into analog voltage for the galvo amplifier.", styles['Body']))

    dac_pins = [
        ["Pin", "Name", "Connection"],
        ["1", "VDD", "+5V rail + C10 (100nF bypass)"],
        ["2", "/CS", "ESP32 GPIO10"],
        ["3", "SCK", "ESP32 GPIO12"],
        ["4", "SDI", "ESP32 GPIO11"],
        ["5", "/LDAC", "ESP32 GPIO13"],
        ["6", "VOUTA", "R5 (10K) to TL072 Ch A (Galvo X)"],
        ["7", "VOUTB", "R7 (10K) to TL072 Ch B (Galvo Y)"],
        ["8", "VSS", "GND"],
    ]
    story.append(make_table(dac_pins))
    story.append(Spacer(1, 6))

    story.append(Paragraph("SPI Protocol", styles['SubHead']))
    story.append(Paragraph(
        "Mode 0,0 (CPOL=0, CPHA=0). 16-bit write format: [A/B][BUF][GA][SHDN][D11:D0]. "
        "Bit 15: Channel (0=A, 1=B). Bit 14: Buffered. Bit 13: Gain (0=2x for 0-4.096V). "
        "Bit 12: Shutdown (1=active). Bits 11-0: 12-bit data (0-4095).", styles['Body']))
    story.append(Paragraph(
        "Output: 0 to 4.096V, resolution 1mV/step. At 10MHz SPI, each write takes ~1.6us. "
        "Both channels + LDAC = ~4us per point = 250K pts/sec theoretical (galvo limited to 20K PPS).", styles['Body']))

    # ─── 6. OP-AMP ───
    story.append(Paragraph("6. Op-Amp Buffer/Amplifier - TL072", styles['SectionHead']))
    story.append(Paragraph("Scales MCP4822 output (0-4.096V) to voltage range required by galvo driver board.", styles['Body']))

    opamp_circuit = """\
              R6 (24K)
         +----/\\/\\/----+
         |             |
DAC_A --R5(10K)--+(+)     |
                 |  TL072  +---> Galvo X+ (J4 Pin 1)
            +---+(-) |     |
            |   |         |
            +---+---------+

Gain = 1 + (R6/R5) = 1 + (24K/10K) = 3.4x"""
    story.append(Preformatted(opamp_circuit, styles['Mono']))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>ENGINEER NOTE:</b> Most hobby galvo drivers accept +/-5V analog input. Current design is "
        "single-supply (V+=12V, V-=GND), output range ~0-10V. If galvos need true +/-5V, add charge pump "
        "IC (ICL7660 or MAX1044) for -12V rail. Verify galvo driver input spec and adjust R5-R8 accordingly.",
        styles['Note']))

    # ─── 7. LASER DRIVER ───
    story.append(Paragraph("7. Laser Module Driver", styles['SectionHead']))

    laser_circuit = """\
ESP32 GPIO14 --R10(100R)--> Q1 Gate
                              |
                     Q1 (2N7000 N-MOSFET)
                              |
                   +12V --R9(4.7K)--+ Drain --> J3 Pin 2 (Laser TTL)
                                    |
                              Source --> GND"""
    story.append(Preformatted(laser_circuit, styles['Mono']))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>IMPORTANT - Active Level:</b> Laserland 4060-530D-200 is TTL active HIGH (12V = laser ON). "
        "ESP32 LOW -> MOSFET OFF -> R9 pulls TTL HIGH -> Laser ON. "
        "ESP32 HIGH -> MOSFET ON -> TTL pulled LOW -> Laser OFF. "
        "<b>Firmware must invert: digitalWrite(LASER_PIN, !laserState)</b>", styles['Note']))

    # ─── 8. CAMERA ───
    story.append(PageBreak())
    story.append(Paragraph("8. Camera - OV5640 (DVP Interface)", styles['SectionHead']))
    story.append(Paragraph(
        "8-bit DVP parallel interface. 8 data lines (D2-D9), VSYNC/HREF/PCLK sync, "
        "XCLK 20MHz ref clock from ESP32, SCCB (I2C) for register configuration.", styles['Body']))

    cam_pullups = [
        ["Ref", "Pin", "Value", "To", "Purpose"],
        ["R11", "SDA", "4.7K", "3.3V", "I2C pull-up"],
        ["R12", "SCL", "4.7K", "3.3V", "I2C pull-up"],
        ["R13", "RESET", "10K", "3.3V", "Keep camera out of reset"],
        ["R14", "PWDN", "10K", "GND", "Keep camera powered on"],
    ]
    story.append(make_table(cam_pullups))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Camera module has its own 1.8V and 2.8V regulators. Only needs 3.3V input from our board.", styles['Body']))

    # ─── 9. SAFETY INTERLOCK ───
    story.append(Paragraph("9. Safety Interlock", styles['SectionHead']))
    safety_circuit = """\
3.3V --R15(10K)--+---> ESP32 GPIO47
                  |
             SW3 (microswitch, normally closed when lid is shut)
                  |
                 GND

Lid closed: SW3 closed -> GPIO47 LOW  -> SAFE (laser can operate)
Lid opened: SW3 opens  -> GPIO47 HIGH -> UNSAFE (firmware kills laser)"""
    story.append(Preformatted(safety_circuit, styles['Mono']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("GPIO47 checked every scan cycle + configured as hardware interrupt for instant response.", styles['Body']))

    # ─── 10. STATUS LED ───
    story.append(Paragraph("10. Status LED - WS2812B", styles['SectionHead']))
    led_data = [
        ["Color", "Meaning"],
        ["Solid Green", "Ready, waiting for connection"],
        ["Pulsing Blue", "Connected to app, idle"],
        ["Solid Blue", "Projecting pattern"],
        ["Pulsing Amber", "Calibrating"],
        ["Solid Red", "Error (safety interlock, overtemp, etc.)"],
        ["Rainbow Cycle", "Firmware update in progress"],
    ]
    story.append(make_table(led_data))

    # ─── 11. UART PROGRAMMING HEADER ───
    story.append(Paragraph("11. UART Programming Header (J6)", styles['SectionHead']))
    uart_data = [
        ["J6 Pin", "Connection", "Notes"],
        ["TX", "ESP32 TX (GPIO43)", "Board TX to cable RX (crossover)"],
        ["RX", "ESP32 RX (GPIO44)", "Board RX to cable TX (crossover)"],
        ["3.3V", "+3.3V rail", "Optional - only if not powered via barrel jack"],
        ["GND", "GND rail", "Always connect"],
    ]
    story.append(make_table(uart_data))
    story.append(Spacer(1, 6))
    story.append(Paragraph("4-pin through-hole male header for firmware flashing via USB-to-TTL serial cable "
        "(Adafruit USB-to-TTL or CP2102-based). Hold BOOT (SW1) during RESET (SW2) to enter download mode. "
        "After initial flash, OTA updates available over WiFi.", styles['Body']))

    # ─── 12. POWER BUDGET ───
    story.append(PageBreak())
    story.append(Paragraph("12. Power Budget", styles['SectionHead']))
    power_data = [
        ["Consumer", "Voltage", "Peak Current", "Notes"],
        ["ESP32-S3", "3.3V", "500mA", "WiFi TX peaks"],
        ["OV5640 Camera", "3.3V", "140mA", "During capture"],
        ["MCP4822 DAC", "5V", "5mA", "Negligible"],
        ["TL072 Op-Amp", "12V", "10mA", "Negligible"],
        ["Laser Module", "12V", "1200mA", "Direct from 12V rail"],
        ["Galvo Driver", "12V", "500mA", "Motor current"],
        ["WS2812B LED", "3.3V", "60mA", "Full white"],
        ["Total 12V", "", "~1.7A", "Within 3A supply"],
        ["Total 5V", "", "~15mA", "Minimal load on U1"],
        ["Total 3.3V", "", "~700mA", "Within U2 1A rating"],
    ]
    story.append(make_table(power_data))

    # ─── 13. COMPLETE BOM ───
    story.append(Paragraph("13. Complete Bill of Materials", styles['SectionHead']))
    story.append(Paragraph("On-Board Components", styles['SubHead']))

    bom_data = [
        ["Ref", "Qty", "Part", "Value/Pkg", "Purpose", "Est. Cost"],
        ["J1", "1", "Barrel Jack", "5.5x2.1mm", "Power input", "$0.75"],
        ["J3", "1", "JST-XH 3-Pin", "2.5mm pitch", "Laser connector", "$0.20"],
        ["J4", "1", "JST-XH 6-Pin", "2.5mm pitch", "Galvo connector", "$0.25"],
        ["J5", "1", "FPC 24-Pin", "0.5mm SMD", "Camera ribbon", "$0.80"],
        ["J6", "1", "4-Pin Header", "2.54mm THT", "UART programming", "$0.10"],
        ["U1", "1", "AMS1117-5.0", "SOT-223", "5V regulator", "$0.45"],
        ["U2", "1", "AMS1117-3.3", "SOT-223", "3.3V regulator", "$0.45"],
        ["U3", "1", "ESP32-S3-WROOM-1", "N16R8", "MCU module", "$3.90"],
        ["U4", "1", "MCP4822", "DIP-8", "Dual 12-bit DAC", "$3.50"],
        ["U5", "1", "TL072", "DIP-8", "Dual op-amp", "$0.65"],
        ["Q1", "1", "2N7000", "TO-92", "Laser MOSFET", "$0.35"],
        ["D1", "1", "SS34", "SMA", "Polarity protection", "$0.30"],
        ["F1", "1", "PTC Fuse 3A", "1206", "Overcurrent", "$0.25"],
        ["LED1", "1", "WS2812B", "PLCC-4 5mm", "Status LED", "$0.15"],
        ["SW1,2", "2", "Tactile Switch", "6x6mm", "BOOT / RESET", "$0.10"],
        ["SW3", "1", "Microswitch", "Panel mount", "Safety interlock", "$1.50"],
        ["R1,2,5-15", "13", "Resistors", "0805 SMD", "Various values", "$0.13"],
        ["C1", "1", "Electrolytic", "470uF 25V", "Bulk filter", "$0.50"],
        ["C3,C5", "2", "Ceramic/Tant", "22uF 10V", "Reg output", "$0.30"],
        ["C7", "1", "Ceramic", "10uF 0805", "ESP32 bypass", "$0.08"],
        ["C2,4,6,8-12", "8", "Ceramic", "100nF 0805", "Decoupling", "$0.16"],
    ]
    story.append(make_table(bom_data, col_widths=[0.6*inch, 0.35*inch, 1.3*inch, 0.9*inch, 1.2*inch, 0.65*inch]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("External Components (not on PCB)", styles['SubHead']))
    ext_data = [
        ["Item", "Description", "Source", "Est. Cost"],
        ["Laser Module", "Laserland 4060-530D-200, 520nm 200mW", "laserlands.net", "$38.00"],
        ["Galvo Scanner Set", "20K PPS dual-axis + driver board", "AliExpress", "$70.00"],
        ["Camera Module", "OV5640 5MP 160-deg DVP", "AliExpress", "$15.00"],
        ["Power Adapter", "12V 3A DC, 5.5x2.1mm barrel", "Amazon", "$8.00"],
        ["Enclosure", "3D printed (PETG) + TPU sleeve", "Self-printed", "$5.00"],
        ["Tripod Insert", "1/4-20 brass threaded insert", "Amazon", "$2.00"],
        ["USB-TTL Cable", "Adafruit USB-to-TTL Serial", "Micro Center", "$15.99"],
    ]
    story.append(make_table(ext_data, col_widths=[1.2*inch, 2.5*inch, 1.2*inch, 0.8*inch]))

    # ─── 14. DESIGN REVIEW CHECKLIST ───
    story.append(PageBreak())
    story.append(Paragraph("14. Design Review Checklist", styles['SectionHead']))
    checklist = [
        "Verify galvo driver board input voltage range and adjust R5-R8 accordingly",
        "Decide on single-supply vs. split-supply for TL072 (affects output swing)",
        "Confirm OV5640 module pinout matches FPC connector assignment",
        "Verify laser module TTL polarity (active HIGH assumed - confirm with datasheet)",
        "Add thermal relief pads for U1, U2 on PCB layout",
        "Consider adding TVS diodes on 12V input for ESD protection",
        "Review ESP32-S3 antenna keepout zone (no copper/components within 10mm of antenna)",
        "Add test points for: +12V, +5V, +3.3V, GND, DAC_A, DAC_B, LASER_TTL",
        "Consider adding a power switch between J1 and D1",
        "Review ground plane continuity (single ground plane recommended)",
    ]
    for i, item in enumerate(checklist, 1):
        story.append(Paragraph(f"<b>[  ]  {i}.</b>  {item}", styles['Body']))

    story.append(Spacer(1, 24))
    story.append(Paragraph("--- END OF DOCUMENT ---", styles['CoverSub']))

    doc.build(story)
    print(f"Created: {OUTPUT}")


def make_table(data, col_widths=None):
    """Create a styled table."""
    if col_widths is None:
        available = 7 * inch
        num_cols = len(data[0])
        col_widths = [available / num_cols] * num_cols

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdc3c7")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]
    # Alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t


if __name__ == "__main__":
    build()
