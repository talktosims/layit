#!/usr/bin/env python3
"""Generate visual SVG wiring diagrams for the LayIt Laser assembly guide.
Creates block-by-block visual diagrams showing every component and connection."""

import os

OUTPUT_DIR = os.path.dirname(__file__)

# ─── Color palette ───
# Matched to TUOFENG 22 AWG 6-color wire kit: Red, Black, Yellow, Blue, Green, White
WIRE_COLORS = {
    '12v': '#e74c3c',      # RED wire      - 12V power
    '5v': '#aaaaaa',       # WHITE wire    - 5V power (shown as light gray on screen)
    '3v3': '#f1c40f',      # YELLOW wire   - 3.3V power
    'gnd': '#2c3e50',      # BLACK wire    - Ground
    'spi': '#3498db',      # BLUE wire     - SPI data bus
    'signal': '#27ae60',   # GREEN wire    - Digital signals (GPIO, TTL, I2C)
    'laser': '#e74c3c',    # RED wire      - Laser power (shares 12V rail)
    'i2c': '#27ae60',      # GREEN wire    - I2C bus (same as signal - both are digital)
    'analog': '#3498db',   # BLUE wire     - Analog signals (DAC/op-amp, same as SPI bus)
    'usb': '#aaaaaa',      # WHITE wire    - USB data
    'safety': '#27ae60',   # GREEN wire    - Safety interlock signal
}

COMP_FILL = '#f8f9fa'
COMP_STROKE = '#2c3e50'
IC_FILL = '#34495e'
IC_TEXT = '#ffffff'
BOARD_BG = '#fefefe'
LABEL_COLOR = '#2c3e50'


def svg_header(width, height, title):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<style>
  text {{ font-family: 'Helvetica Neue', Arial, sans-serif; }}
  .title {{ font-size: 22px; font-weight: bold; fill: #1a1a2e; }}
  .subtitle {{ font-size: 14px; fill: #0f3460; }}
  .comp-label {{ font-size: 11px; font-weight: bold; fill: {LABEL_COLOR}; }}
  .pin-label {{ font-size: 9px; fill: #555; }}
  .wire-label {{ font-size: 9px; font-weight: bold; }}
  .note {{ font-size: 10px; fill: #666; font-style: italic; }}
  .ic-label {{ font-size: 12px; font-weight: bold; fill: {IC_TEXT}; }}
  .ic-pin {{ font-size: 8px; fill: {IC_TEXT}; }}
  .ref {{ font-size: 9px; font-weight: bold; fill: #c0392b; }}
  .value {{ font-size: 9px; fill: #27ae60; }}
  .section-title {{ font-size: 16px; font-weight: bold; fill: #0f3460; }}
  .warning {{ font-size: 10px; font-weight: bold; fill: #e74c3c; }}
  .info {{ font-size: 10px; fill: #2980b9; }}
</style>
<rect width="{width}" height="{height}" fill="{BOARD_BG}" rx="8"/>
<text x="{width//2}" y="35" text-anchor="middle" class="title">{title}</text>
'''

def svg_footer():
    return '</svg>\n'


def draw_ic(x, y, w, h, name, pins_left, pins_right, ref=""):
    """Draw an IC/chip with pins labeled."""
    svg = f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{IC_FILL}" stroke="{COMP_STROKE}" stroke-width="2" rx="4"/>
<text x="{x + w//2}" y="{y + h//2 + 4}" text-anchor="middle" class="ic-label">{name}</text>
'''
    if ref:
        svg += f'<text x="{x + w//2}" y="{y - 6}" text-anchor="middle" class="ref">{ref}</text>\n'

    # Notch
    svg += f'<circle cx="{x + 12}" cy="{y + 8}" r="4" fill="#555" stroke="#777"/>\n'

    pin_spacing = h / (len(pins_left) + 1)
    for i, pin in enumerate(pins_left):
        py = y + pin_spacing * (i + 1)
        svg += f'<line x1="{x - 15}" y1="{py}" x2="{x}" y2="{py}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
        svg += f'<text x="{x + 6}" y="{py + 3}" class="ic-pin">{pin}</text>\n'
        svg += f'<circle cx="{x - 15}" cy="{py}" r="3" fill="{COMP_STROKE}"/>\n'

    pin_spacing = h / (len(pins_right) + 1)
    for i, pin in enumerate(pins_right):
        py = y + pin_spacing * (i + 1)
        svg += f'<line x1="{x + w}" y1="{py}" x2="{x + w + 15}" y2="{py}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
        svg += f'<text x="{x + w - 6}" y="{py + 3}" text-anchor="end" class="ic-pin">{pin}</text>\n'
        svg += f'<circle cx="{x + w + 15}" cy="{py}" r="3" fill="{COMP_STROKE}"/>\n'

    return svg


def draw_component(x, y, w, h, name, ref="", value="", color=COMP_FILL):
    """Draw a generic rectangular component."""
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="{COMP_STROKE}" stroke-width="1.5" rx="3"/>\n'
    svg += f'<text x="{x + w//2}" y="{y + h//2 + 4}" text-anchor="middle" class="comp-label">{name}</text>\n'
    if ref:
        svg += f'<text x="{x + w//2}" y="{y - 4}" text-anchor="middle" class="ref">{ref}</text>\n'
    if value:
        svg += f'<text x="{x + w//2}" y="{y + h + 12}" text-anchor="middle" class="value">{value}</text>\n'
    return svg


def draw_resistor(x, y, horizontal=True, ref="", value=""):
    """Draw a resistor symbol."""
    if horizontal:
        svg = f'''<line x1="{x}" y1="{y}" x2="{x+10}" y2="{y}" stroke="{COMP_STROKE}" stroke-width="2"/>
<rect x="{x+10}" y="{y-6}" width="30" height="12" fill="#ffe4b5" stroke="{COMP_STROKE}" stroke-width="1.5" rx="2"/>
<line x1="{x+40}" y1="{y}" x2="{x+50}" y2="{y}" stroke="{COMP_STROKE}" stroke-width="2"/>
<circle cx="{x}" cy="{y}" r="3" fill="{COMP_STROKE}"/>
<circle cx="{x+50}" cy="{y}" r="3" fill="{COMP_STROKE}"/>
'''
        if ref:
            svg += f'<text x="{x+25}" y="{y-10}" text-anchor="middle" class="ref">{ref}</text>\n'
        if value:
            svg += f'<text x="{x+25}" y="{y+3}" text-anchor="middle" class="value" style="font-size:8px">{value}</text>\n'
    return svg


def draw_capacitor(x, y, ref="", value="", electrolytic=False):
    """Draw a capacitor symbol."""
    svg = f'''<line x1="{x}" y1="{y-15}" x2="{x}" y2="{y-3}" stroke="{COMP_STROKE}" stroke-width="2"/>
<line x1="{x-10}" y1="{y-3}" x2="{x+10}" y2="{y-3}" stroke="{COMP_STROKE}" stroke-width="2.5"/>
<line x1="{x-10}" y1="{y+3}" x2="{x+10}" y2="{y+3}" stroke="{COMP_STROKE}" stroke-width="2.5"/>
<line x1="{x}" y1="{y+3}" x2="{x}" y2="{y+15}" stroke="{COMP_STROKE}" stroke-width="2"/>
<circle cx="{x}" cy="{y-15}" r="3" fill="{COMP_STROKE}"/>
<circle cx="{x}" cy="{y+15}" r="3" fill="{COMP_STROKE}"/>
'''
    if electrolytic:
        svg += f'<text x="{x+12}" y="{y-6}" class="warning" style="font-size:12px">+</text>\n'
    if ref:
        svg += f'<text x="{x+16}" y="{y-8}" class="ref">{ref}</text>\n'
    if value:
        svg += f'<text x="{x+16}" y="{y+8}" class="value">{value}</text>\n'
    return svg


def draw_wire(x1, y1, x2, y2, color='#2c3e50', label="", waypoints=None):
    """Draw a wire (straight or with waypoints)."""
    if waypoints:
        points = [(x1, y1)] + waypoints + [(x2, y2)]
        path = f'M {points[0][0]} {points[0][1]}'
        for p in points[1:]:
            path += f' L {p[0]} {p[1]}'
        svg = f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>\n'
    else:
        svg = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>\n'

    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        svg += f'<text x="{mx}" y="{my - 6}" text-anchor="middle" class="wire-label" fill="{color}">{label}</text>\n'
    return svg


def draw_connector(x, y, pins, name, ref="", orientation="right"):
    """Draw a multi-pin connector (JST, barrel jack, etc.)."""
    h = len(pins) * 22 + 10
    w = 60
    svg = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ecf0f1" stroke="{COMP_STROKE}" stroke-width="2" rx="3"/>\n'
    svg += f'<text x="{x + w//2}" y="{y - 6}" text-anchor="middle" class="comp-label">{name}</text>\n'
    if ref:
        svg += f'<text x="{x + w//2}" y="{y - 18}" text-anchor="middle" class="ref">{ref}</text>\n'

    for i, pin in enumerate(pins):
        py = y + 16 + i * 22
        if orientation == "right":
            svg += f'<circle cx="{x + w + 12}" cy="{py}" r="4" fill="{COMP_STROKE}"/>\n'
            svg += f'<line x1="{x + w}" y1="{py}" x2="{x + w + 12}" y2="{py}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
            svg += f'<text x="{x + w - 6}" y="{py + 3}" text-anchor="end" class="pin-label">{pin}</text>\n'
        else:
            svg += f'<circle cx="{x - 12}" cy="{py}" r="4" fill="{COMP_STROKE}"/>\n'
            svg += f'<line x1="{x - 12}" y1="{py}" x2="{x}" y2="{py}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
            svg += f'<text x="{x + 6}" y="{py + 3}" class="pin-label">{pin}</text>\n'

    return svg


def draw_regulator(x, y, name, ref, vin_label, vout_label):
    """Draw a voltage regulator (3-pin with tab)."""
    svg = f'''<rect x="{x}" y="{y}" width="70" height="40" fill="#555" stroke="{COMP_STROKE}" stroke-width="2" rx="3"/>
<rect x="{x+5}" y="{y-8}" width="60" height="10" fill="#777" stroke="{COMP_STROKE}" stroke-width="1" rx="2"/>
<text x="{x+35}" y="{y+24}" text-anchor="middle" class="ic-label" style="font-size:10px">{name}</text>
<text x="{x+35}" y="{y-14}" text-anchor="middle" class="ref">{ref}</text>
'''
    # Pins: IN, GND, OUT
    svg += f'<line x1="{x-15}" y1="{y+13}" x2="{x}" y2="{y+13}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
    svg += f'<circle cx="{x-15}" cy="{y+13}" r="3" fill="{COMP_STROKE}"/>\n'
    svg += f'<text x="{x-18}" y="{y+10}" text-anchor="end" class="pin-label">{vin_label}</text>\n'

    svg += f'<line x1="{x+35}" y1="{y+40}" x2="{x+35}" y2="{y+55}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
    svg += f'<circle cx="{x+35}" cy="{y+55}" r="3" fill="{COMP_STROKE}"/>\n'
    svg += f'<text x="{x+45}" y="{y+55}" class="pin-label">GND</text>\n'

    svg += f'<line x1="{x+70}" y1="{y+13}" x2="{x+85}" y2="{y+13}" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
    svg += f'<circle cx="{x+85}" cy="{y+13}" r="3" fill="{COMP_STROKE}"/>\n'
    svg += f'<text x="{x+88}" y="{y+10}" class="pin-label">{vout_label}</text>\n'

    return svg


# ═══════════════════════════════════════════════════════════
# DIAGRAM 1: FULL SYSTEM OVERVIEW
# ═══════════════════════════════════════════════════════════
def create_system_overview():
    W, H = 1100, 850
    svg = svg_header(W, H, "LayIt Laser - Complete System Wiring Diagram")
    svg += '<text x="550" y="58" text-anchor="middle" class="subtitle">Every connection in one view. Wire colors match the assembly guide.</text>\n'

    # ── Power Input (left side) ──
    svg += draw_connector(30, 100, ["+12V", "GND"], "12V DC IN", "J1", "right")

    # Diode
    svg += f'<text x="140" y="100" class="ref">D1 (SS34)</text>\n'
    svg += f'<polygon points="130,116 160,108 160,124" fill="none" stroke="{COMP_STROKE}" stroke-width="2"/>\n'
    svg += f'<line x1="160" y1="108" x2="160" y2="124" stroke="{COMP_STROKE}" stroke-width="3"/>\n'
    svg += draw_wire(102, 116, 130, 116, WIRE_COLORS['12v'])
    svg += draw_wire(160, 116, 190, 116, WIRE_COLORS['12v'])

    # Fuse
    svg += draw_component(190, 106, 50, 20, "3A", "F1", "PTC Fuse", "#ffe4b5")
    svg += draw_wire(240, 116, 280, 116, WIRE_COLORS['12v'], "+12V RAIL")

    # GND rail
    svg += draw_wire(102, 138, 280, 138, WIRE_COLORS['gnd'], "GND RAIL")

    # ── 12V Rail (horizontal line across) ──
    svg += draw_wire(280, 116, 1050, 116, WIRE_COLORS['12v'])
    svg += f'<text x="660" y="108" class="wire-label" fill="{WIRE_COLORS["12v"]}">+12V RAIL</text>\n'

    # GND Rail
    svg += draw_wire(280, 790, 1050, 790, WIRE_COLORS['gnd'])
    svg += f'<text x="660" y="808" class="wire-label" fill="{WIRE_COLORS["gnd"]}">GND RAIL</text>\n'
    svg += draw_wire(280, 138, 280, 790, WIRE_COLORS['gnd'])

    # ── Voltage Regulators ──
    svg += draw_regulator(320, 170, "AMS1117", "U1", "12V", "5V")
    svg += draw_wire(320, 116, 320, 183, WIRE_COLORS['12v'])  # 12V to U1 input
    svg += draw_wire(305, 183, 320, 183, WIRE_COLORS['12v'])
    svg += draw_wire(355, 225, 355, 790, WIRE_COLORS['gnd'])  # U1 GND
    svg += draw_wire(405, 183, 450, 183, WIRE_COLORS['5v'])    # 5V output
    svg += f'<text x="430" y="175" class="wire-label" fill="{WIRE_COLORS["5v"]}">+5V</text>\n'

    # 5V rail segment
    svg += draw_wire(450, 183, 450, 300, WIRE_COLORS['5v'])

    svg += draw_regulator(320, 260, "AMS1117", "U2", "5V", "3.3V")
    svg += draw_wire(450, 273, 405, 273, WIRE_COLORS['5v'])  # 5V to U2
    svg += draw_wire(355, 315, 355, 790, WIRE_COLORS['gnd'])  # U2 GND
    svg += draw_wire(305, 273, 280, 273, WIRE_COLORS['5v'])
    svg += draw_wire(280, 183, 280, 273, WIRE_COLORS['5v'])
    # Bypass caps
    svg += draw_capacitor(430, 218, "C3", "22uF")
    svg += draw_capacitor(460, 218, "C4", "100nF")
    svg += draw_capacitor(430, 308, "C5", "22uF")
    svg += draw_capacitor(460, 308, "C6", "100nF")

    svg += draw_wire(405, 273, 500, 273, '#f1c40f')    # 3.3V output
    svg += f'<text x="470" y="265" class="wire-label" fill="{WIRE_COLORS["3v3"]}">+3.3V</text>\n'

    # 3.3V rail
    svg += draw_wire(500, 273, 500, 700, WIRE_COLORS['3v3'])

    # ── ESP32-S3 (center) ──
    esp_x, esp_y = 530, 350
    svg += draw_ic(esp_x, esp_y, 180, 300, "ESP32-S3",
        ["GPIO0", "GPIO1", "GPIO2", "GPIO10", "GPIO11", "GPIO12", "GPIO13", "GPIO14", "GPIO47", "GPIO48"],
        ["GPIO4", "GPIO5", "GPIO6", "GPIO7", "GPIO8/9", "GPIO15-18", "GPIO45/46", "GPIO19", "GPIO20", "3V3/GND"],
        "U3")

    # 3.3V to ESP32
    svg += draw_wire(500, 400, 530, 400, WIRE_COLORS['3v3'])

    # Bypass caps for ESP32
    svg += draw_capacitor(505, 430, "C7", "10uF")
    svg += draw_capacitor(505, 470, "C8", "100nF")

    # ── MCP4822 DAC (above ESP32) ──
    dac_x, dac_y = 300, 420
    svg += draw_ic(dac_x, dac_y, 100, 140, "MCP4822",
        ["VDD", "/CS", "SCK", "SDI"],
        ["VOUTA", "VOUTB", "/LDAC", "VSS"],
        "U4")

    # SPI wires from ESP32 to DAC
    svg += draw_wire(515, 430, 415, 430, WIRE_COLORS['spi'])  # CS
    svg += draw_wire(515, 465, 400, 465, WIRE_COLORS['spi'])  # SCK
    svg += draw_wire(400, 465, 400, 500, WIRE_COLORS['spi'])
    svg += draw_wire(400, 500, 415, 500, WIRE_COLORS['spi'])
    svg += draw_wire(515, 500, 420, 525, WIRE_COLORS['spi'])  # MOSI
    svg += f'<text x="460" y="425" class="wire-label" fill="{WIRE_COLORS["spi"]}">SPI Bus</text>\n'

    # DAC power
    svg += draw_wire(285, 455, 300, 455, WIRE_COLORS['5v'])
    svg += draw_capacitor(270, 455, "C10", "100nF")

    # ── TL072 Op-Amp ──
    opamp_x, opamp_y = 100, 420
    svg += draw_ic(opamp_x, opamp_y, 100, 120, "TL072",
        ["OUT A", "IN- A", "IN+ A", "V-"],
        ["V+", "IN+ B", "IN- B", "OUT B"],
        "U5")

    # DAC to Op-Amp via resistors
    svg += draw_wire(285, 460, 250, 460, WIRE_COLORS['analog'])  # VOUTA
    svg += draw_resistor(215, 460, ref="R5", value="10K")
    svg += draw_wire(215, 460, 215, 480, WIRE_COLORS['analog'])

    svg += draw_wire(285, 495, 250, 495, WIRE_COLORS['analog'])  # VOUTB
    svg += draw_resistor(215, 495, ref="R7", value="10K")

    # Op-amp output labels
    svg += f'<text x="60" y="450" class="comp-label" fill="{WIRE_COLORS["analog"]}">To Galvo X</text>\n'
    svg += f'<text x="230" y="525" class="comp-label" fill="{WIRE_COLORS["analog"]}">To Galvo Y</text>\n'

    # ── Galvo Connector ──
    svg += draw_connector(20, 560, ["X+", "X-", "Y+", "Y-", "+12V", "GND"], "GALVO", "J4", "right")
    svg += draw_wire(92, 576, 85, 455, WIRE_COLORS['analog'])  # X signal

    # ── Laser Driver Circuit ──
    svg += f'<text x="850" y="200" class="section-title">Laser Driver</text>\n'

    # MOSFET
    svg += draw_component(850, 220, 60, 35, "2N7000", "Q1", "", "#ddd")
    svg += f'<text x="880" y="275" class="pin-label">S    G    D</text>\n'

    # Resistors
    svg += draw_resistor(770, 238, ref="R10", value="100R")
    svg += draw_resistor(930, 220, ref="R9", value="4.7K")

    # Wire from ESP32 GPIO14 to MOSFET
    svg += draw_wire(515, 570, 480, 570, WIRE_COLORS['laser'])
    svg += draw_wire(480, 570, 480, 238, WIRE_COLORS['laser'])
    svg += draw_wire(480, 238, 770, 238, WIRE_COLORS['laser'])
    svg += f'<text x="600" y="232" class="wire-label" fill="{WIRE_COLORS["laser"]}">GPIO14 (Laser TTL)</text>\n'

    # Laser connector
    svg += draw_connector(980, 210, ["+12V", "TTL", "GND"], "LASER", "J3", "left")

    # ── Camera ──
    svg += f'<text x="850" y="380" class="section-title">Camera (DVP)</text>\n'
    svg += draw_component(830, 400, 120, 80, "OV5640\n5MP 160deg", "J5", "", "#d5e8d4")

    # Camera data bus
    svg += draw_wire(725, 430, 830, 430, WIRE_COLORS['signal'])
    svg += draw_wire(725, 460, 830, 460, WIRE_COLORS['signal'])
    svg += f'<text x="770" y="425" class="wire-label" fill="{WIRE_COLORS["signal"]}">8-bit DVP</text>\n'
    svg += f'<text x="770" y="475" class="wire-label" fill="{WIRE_COLORS["i2c"]}">I2C (SDA/SCL)</text>\n'

    # I2C pull-ups
    svg += draw_resistor(770, 500, ref="R11", value="4.7K")
    svg += draw_resistor(770, 520, ref="R12", value="4.7K")

    # ── Safety Interlock ──
    svg += f'<text x="850" y="540" class="section-title">Safety</text>\n'
    svg += draw_component(850, 560, 80, 35, "SW3", "", "Lid Switch", "#fadbd8")
    svg += draw_wire(725, 605, 850, 605, WIRE_COLORS['safety'])
    svg += draw_wire(850, 578, 850, 605, WIRE_COLORS['safety'])
    svg += draw_resistor(790, 560, ref="R15", value="10K")
    svg += f'<text x="790" y="548" class="info">GPIO47</text>\n'

    # ── Status LED ──
    svg += f'<text x="850" y="640" class="section-title">Status LED</text>\n'
    svg += f'<rect x="860" y="660" width="30" height="30" fill="#27ae60" stroke="{COMP_STROKE}" stroke-width="2" rx="2"/>\n'
    svg += f'<text x="875" y="680" text-anchor="middle" class="ic-label" style="font-size:8px">LED</text>\n'
    svg += f'<text x="875" y="700" text-anchor="middle" class="ref">LED1</text>\n'
    svg += f'<text x="875" y="712" text-anchor="middle" class="value">WS2812B</text>\n'
    svg += draw_wire(725, 640, 860, 640, WIRE_COLORS['signal'])
    svg += draw_wire(860, 640, 860, 660, WIRE_COLORS['signal'])
    svg += f'<text x="790" y="635" class="info">GPIO48</text>\n'

    # ── Bulk Input Cap ──
    svg += draw_capacitor(310, 145, "C1", "470uF", electrolytic=True)

    # ── Legend ──
    legend_x, legend_y = 30, 720
    svg += f'<rect x="{legend_x}" y="{legend_y}" width="240" height="115" fill="white" stroke="#ccc" stroke-width="1" rx="4"/>\n'
    svg += f'<text x="{legend_x + 10}" y="{legend_y + 18}" class="comp-label">WIRE COLOR LEGEND</text>\n'

    legend_items = [
        (WIRE_COLORS['12v'], "RED wire → +12V Power"),
        (WIRE_COLORS['5v'], "WHITE wire → +5V Power"),
        (WIRE_COLORS['3v3'], "YELLOW wire → +3.3V Power"),
        (WIRE_COLORS['gnd'], "BLACK wire → Ground (GND)"),
        (WIRE_COLORS['spi'], "BLUE wire → SPI / Analog Signals"),
        (WIRE_COLORS['signal'], "GREEN wire → Digital / I2C / Safety"),
    ]
    for i, (color, label) in enumerate(legend_items):
        ly = legend_y + 35 + i * 12
        svg += f'<line x1="{legend_x + 10}" y1="{ly}" x2="{legend_x + 40}" y2="{ly}" stroke="{color}" stroke-width="3"/>\n'
        svg += f'<text x="{legend_x + 48}" y="{ly + 4}" class="pin-label">{label}</text>\n'

    svg += svg_footer()
    return svg


# ═══════════════════════════════════════════════════════════
# DIAGRAM 2: POWER SECTION DETAIL
# ═══════════════════════════════════════════════════════════
def create_power_detail():
    W, H = 900, 500
    svg = svg_header(W, H, "Power Section - Detailed Wiring")
    svg += '<text x="450" y="58" text-anchor="middle" class="subtitle">12V input through protection, regulation to 5V and 3.3V rails</text>\n'

    # Barrel Jack
    svg += draw_connector(30, 120, ["+12V IN", "GND"], "12V 3A\nAdapter", "J1", "right")

    # Arrow showing plug direction
    svg += f'<text x="30" y="105" class="info">Plug in here</text>\n'

    # Diode with clear labels
    svg += f'<rect x="140" y="116" width="60" height="30" fill="#fadbd8" stroke="{COMP_STROKE}" stroke-width="1.5" rx="3"/>\n'
    svg += f'<text x="170" y="135" text-anchor="middle" class="comp-label">SS34</text>\n'
    svg += f'<text x="170" y="106" text-anchor="middle" class="ref">D1</text>\n'
    svg += f'<text x="170" y="160" text-anchor="middle" class="warning">SILVER STRIPE THIS END --&gt;</text>\n'
    svg += draw_wire(102, 136, 140, 136, WIRE_COLORS['12v'])
    svg += draw_wire(200, 136, 240, 136, WIRE_COLORS['12v'])

    # Fuse
    svg += f'<rect x="240" y="124" width="60" height="24" fill="#ffe4b5" stroke="{COMP_STROKE}" stroke-width="1.5" rx="3"/>\n'
    svg += f'<text x="270" y="140" text-anchor="middle" class="comp-label">PTC 3A</text>\n'
    svg += f'<text x="270" y="114" text-anchor="middle" class="ref">F1</text>\n'
    svg += draw_wire(300, 136, 360, 136, WIRE_COLORS['12v'])

    # Bulk cap
    svg += draw_capacitor(340, 180, "C1", "470uF", electrolytic=True)
    svg += f'<text x="370" y="178" class="warning">+ LEG IN + HOLE!</text>\n'

    # 12V rail label
    svg += f'<rect x="360" y="126" width="100" height="22" fill="{WIRE_COLORS["12v"]}" rx="4"/>\n'
    svg += f'<text x="410" y="141" text-anchor="middle" style="fill:white; font-weight:bold; font-size:12px">+12V RAIL</text>\n'

    # GND rail
    svg += draw_wire(102, 158, 460, 158, WIRE_COLORS['gnd'])
    svg += draw_wire(460, 158, 460, 420, WIRE_COLORS['gnd'])
    svg += f'<rect x="360" y="410" width="100" height="22" fill="{WIRE_COLORS["gnd"]}" rx="4"/>\n'
    svg += f'<text x="410" y="425" text-anchor="middle" style="fill:white; font-weight:bold; font-size:12px">GND RAIL</text>\n'

    # 5V Regulator
    svg += draw_regulator(520, 180, "AMS1117-5.0", "U1", "12V IN", "5V OUT")
    svg += draw_wire(460, 136, 460, 193, WIRE_COLORS['12v'])
    svg += draw_wire(460, 193, 505, 193, WIRE_COLORS['12v'])
    svg += draw_wire(555, 235, 555, 420, WIRE_COLORS['gnd'])

    # 5V output with caps
    svg += draw_wire(605, 193, 680, 193, WIRE_COLORS['5v'])
    svg += draw_capacitor(640, 230, "C3", "22uF")
    svg += draw_capacitor(670, 230, "C4", "100nF")
    svg += draw_wire(640, 245, 640, 420, WIRE_COLORS['gnd'])
    svg += draw_wire(670, 245, 670, 420, WIRE_COLORS['gnd'])

    svg += f'<rect x="680" y="183" width="80" height="22" fill="{WIRE_COLORS["5v"]}" rx="4"/>\n'
    svg += f'<text x="720" y="198" text-anchor="middle" style="fill:white; font-weight:bold; font-size:12px">+5V RAIL</text>\n'

    # 3.3V Regulator
    svg += draw_regulator(520, 300, "AMS1117-3.3", "U2", "5V IN", "3.3V OUT")
    svg += draw_wire(680, 193, 680, 313, WIRE_COLORS['5v'])
    svg += draw_wire(680, 313, 605, 313, WIRE_COLORS['5v'])
    # Also feed from 5V
    svg += draw_wire(505, 313, 460, 313, WIRE_COLORS['5v'])
    svg += draw_wire(460, 193, 460, 313, WIRE_COLORS['5v'])
    svg += draw_wire(555, 355, 555, 420, WIRE_COLORS['gnd'])

    # 3.3V output with caps
    svg += draw_wire(605, 313, 760, 313, WIRE_COLORS['3v3'])
    svg += draw_capacitor(720, 350, "C5", "22uF")
    svg += draw_capacitor(750, 350, "C6", "100nF")
    svg += draw_wire(720, 365, 720, 420, WIRE_COLORS['gnd'])
    svg += draw_wire(750, 365, 750, 420, WIRE_COLORS['gnd'])

    svg += f'<rect x="760" y="303" width="90" height="22" fill="{WIRE_COLORS["3v3"]}" rx="4"/>\n'
    svg += f'<text x="805" y="318" text-anchor="middle" style="fill:white; font-weight:bold; font-size:12px">+3.3V RAIL</text>\n'

    # Note
    svg += f'<text x="520" y="470" class="note">5V feeds into 3.3V regulator (cascade design) to reduce heat</text>\n'

    # GND rail line
    svg += draw_wire(460, 420, 780, 420, WIRE_COLORS['gnd'])

    svg += svg_footer()
    return svg


# ═══════════════════════════════════════════════════════════
# DIAGRAM 3: LASER DRIVER DETAIL
# ═══════════════════════════════════════════════════════════
def create_laser_detail():
    W, H = 800, 450
    svg = svg_header(W, H, "Laser Driver Circuit - Step by Step")
    svg += '<text x="400" y="58" text-anchor="middle" class="subtitle">GPIO14 controls laser via MOSFET level shifter</text>\n'

    # ESP32 pin
    svg += f'<rect x="40" y="170" width="100" height="50" fill="{IC_FILL}" stroke="{COMP_STROKE}" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="90" y="195" text-anchor="middle" class="ic-label" style="font-size:10px">ESP32</text>\n'
    svg += f'<text x="90" y="210" text-anchor="middle" class="ic-pin">GPIO14</text>\n'
    svg += f'<text x="90" y="160" text-anchor="middle" class="ref">U3</text>\n'

    # Wire to gate resistor
    svg += draw_wire(140, 195, 200, 195, WIRE_COLORS['signal'])
    svg += f'<text x="170" y="185" class="info">3.3V signal</text>\n'

    # Gate resistor R10
    svg += draw_resistor(200, 195, ref="R10", value="100 Ohm")
    svg += draw_wire(250, 195, 310, 195, WIRE_COLORS['signal'])

    # MOSFET - drawn larger for clarity
    svg += f'<rect x="310" y="140" width="80" height="110" fill="#ecf0f1" stroke="{COMP_STROKE}" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="350" y="170" text-anchor="middle" class="comp-label">2N7000</text>\n'
    svg += f'<text x="350" y="185" text-anchor="middle" class="comp-label">N-MOSFET</text>\n'
    svg += f'<text x="350" y="130" text-anchor="middle" class="ref">Q1</text>\n'

    # Pin labels on MOSFET
    svg += f'<text x="310" y="198" text-anchor="end" class="pin-label">G (Gate)</text>\n'
    svg += f'<text x="350" y="260" text-anchor="middle" class="pin-label">S (Source)</text>\n'
    svg += f'<text x="350" y="130" text-anchor="middle" class="pin-label">D (Drain)</text>\n'

    # Flat side indicator
    svg += f'<text x="350" y="235" text-anchor="middle" class="warning">FLAT SIDE</text>\n'
    svg += f'<text x="350" y="247" text-anchor="middle" class="warning">FACES YOU</text>\n'

    # Source to GND
    svg += draw_wire(350, 250, 350, 380, WIRE_COLORS['gnd'])
    svg += f'<rect x="300" y="370" width="100" height="22" fill="{WIRE_COLORS["gnd"]}" rx="4"/>\n'
    svg += f'<text x="350" y="385" text-anchor="middle" style="fill:white; font-weight:bold; font-size:11px">GND</text>\n'

    # Drain up to pull-up resistor
    svg += draw_wire(350, 140, 350, 100, WIRE_COLORS['signal'])

    # Pull-up resistor R9 to 12V
    svg += draw_resistor(320, 85, ref="R9", value="4.7K")
    svg += draw_wire(320, 85, 280, 85, WIRE_COLORS['12v'])
    svg += f'<rect x="230" y="75" width="50" height="22" fill="{WIRE_COLORS["12v"]}" rx="4"/>\n'
    svg += f'<text x="255" y="90" text-anchor="middle" style="fill:white; font-weight:bold; font-size:11px">+12V</text>\n'

    # TTL output to laser connector
    svg += draw_wire(370, 85, 500, 85, WIRE_COLORS['laser'])
    svg += f'<text x="435" y="78" class="wire-label" fill="{WIRE_COLORS["laser"]}">TTL Signal (0V or 12V)</text>\n'

    # Laser connector J3
    svg += draw_connector(540, 80, ["+12V", "TTL", "GND"], "LASER\nMODULE", "J3", "left")

    # 12V to laser power
    svg += draw_wire(528, 96, 500, 96, WIRE_COLORS['12v'])
    svg += draw_wire(500, 96, 500, 85, WIRE_COLORS['12v'])

    # GND to laser
    svg += draw_wire(528, 140, 500, 140, WIRE_COLORS['gnd'])
    svg += draw_wire(500, 140, 500, 380, WIRE_COLORS['gnd'])

    # Logic explanation box
    svg += f'<rect x="450" y="250" width="310" height="140" fill="#eaf2f8" stroke="#2980b9" stroke-width="1.5" rx="6"/>\n'
    svg += f'<text x="605" y="275" text-anchor="middle" class="section-title" style="font-size:13px">How It Works</text>\n'
    svg += f'<text x="465" y="298" class="info">ESP32 GPIO14 HIGH = MOSFET ON</text>\n'
    svg += f'<text x="485" y="313" class="info">= Drain pulled to GND = TTL LOW</text>\n'
    svg += f'<text x="485" y="328" class="info">= Laser OFF</text>\n'
    svg += f'<text x="465" y="352" class="info">ESP32 GPIO14 LOW = MOSFET OFF</text>\n'
    svg += f'<text x="485" y="367" class="info">= R9 pulls TTL to 12V = TTL HIGH</text>\n'
    svg += f'<text x="485" y="382" class="info">= Laser ON</text>\n'

    svg += svg_footer()
    return svg


# ═══════════════════════════════════════════════════════════
# DIAGRAM 4: DAC + OP-AMP + GALVO
# ═══════════════════════════════════════════════════════════
def create_dac_galvo_detail():
    W, H = 900, 500
    svg = svg_header(W, H, "DAC + Op-Amp + Galvo Signal Path")
    svg += '<text x="450" y="58" text-anchor="middle" class="subtitle">SPI from ESP32 to DAC, amplified by op-amp, drives galvo motors</text>\n'

    # ESP32 SPI pins
    svg += f'<rect x="30" y="140" width="120" height="160" fill="{IC_FILL}" stroke="{COMP_STROKE}" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="90" y="200" text-anchor="middle" class="ic-label">ESP32-S3</text>\n'
    svg += f'<text x="90" y="130" text-anchor="middle" class="ref">U3</text>\n'

    esp_pins = [("GPIO10", 170, "/CS"), ("GPIO11", 200, "MOSI"), ("GPIO12", 230, "CLK"), ("GPIO13", 260, "/LDAC")]
    for name, y, desc in esp_pins:
        svg += f'<text x="140" y="{y+3}" class="pin-label">{name}</text>\n'
        svg += draw_wire(150, y, 260, y, WIRE_COLORS['spi'])
        svg += f'<text x="200" y="{y-5}" class="wire-label" fill="{WIRE_COLORS["spi"]}">{desc}</text>\n'

    # MCP4822 DAC
    svg += draw_ic(260, 140, 120, 180, "MCP4822",
        ["VDD", "/CS", "SCK", "SDI"],
        ["VOUTA", "VOUTB", "/LDAC", "VSS"],
        "U4")

    # DAC bypass cap
    svg += draw_capacitor(240, 130, "C10", "100nF")

    # DAC outputs to op-amp
    svg += draw_wire(395, 175, 440, 175, WIRE_COLORS['analog'])
    svg += f'<text x="420" y="168" class="wire-label" fill="{WIRE_COLORS["analog"]}">Ch A (X)</text>\n'
    svg += draw_wire(395, 215, 440, 215, WIRE_COLORS['analog'])
    svg += f'<text x="420" y="208" class="wire-label" fill="{WIRE_COLORS["analog"]}">Ch B (Y)</text>\n'

    # Input resistors
    svg += draw_resistor(440, 175, ref="R5", value="10K")
    svg += draw_resistor(440, 215, ref="R7", value="10K")

    # TL072 Op-Amp
    svg += draw_ic(520, 140, 120, 180, "TL072",
        ["OUT A", "IN- A", "IN+ A", "V-"],
        ["V+", "IN+ B", "IN- B", "OUT B"],
        "U5")

    # Feedback resistors
    svg += draw_resistor(530, 115, ref="R6", value="24K")
    svg += draw_resistor(530, 340, ref="R8", value="24K")
    svg += f'<text x="555" y="105" class="note">Gain = 1 + 24K/10K = 3.4x</text>\n'

    # Op-amp outputs to galvo connector
    svg += draw_wire(505, 175, 480, 175, WIRE_COLORS['analog'])
    svg += draw_wire(480, 175, 480, 380, WIRE_COLORS['analog'])
    svg += draw_wire(480, 380, 700, 380, WIRE_COLORS['analog'])
    svg += f'<text x="580" y="373" class="wire-label" fill="{WIRE_COLORS["analog"]}">Galvo X Signal</text>\n'

    svg += draw_wire(655, 295, 680, 295, WIRE_COLORS['analog'])
    svg += draw_wire(680, 295, 680, 402, WIRE_COLORS['analog'])
    svg += draw_wire(680, 402, 700, 402, WIRE_COLORS['analog'])
    svg += f'<text x="690" y="415" class="wire-label" fill="{WIRE_COLORS["analog"]}">Galvo Y Signal</text>\n'

    # Galvo connector
    svg += draw_connector(700, 350, ["X+", "X-", "Y+", "Y-", "+12V", "GND"], "GALVO\nDRIVER", "J4", "right")

    # Power connections
    svg += draw_wire(762, 460, 800, 460, WIRE_COLORS['12v'])
    svg += f'<text x="800" y="455" class="wire-label" fill="{WIRE_COLORS["12v"]}">+12V</text>\n'
    svg += draw_wire(762, 482, 800, 482, WIRE_COLORS['gnd'])
    svg += f'<text x="800" y="477" class="wire-label" fill="{WIRE_COLORS["gnd"]}">GND</text>\n'

    svg += svg_footer()
    return svg


# ═══════════════════════════════════════════════════════════
# DIAGRAM 5: SAFETY + LED + CAMERA
# ═══════════════════════════════════════════════════════════
def create_peripherals_detail():
    W, H = 900, 550
    svg = svg_header(W, H, "Camera, Safety Interlock & Status LED")
    svg += '<text x="450" y="58" text-anchor="middle" class="subtitle">Peripheral connections to ESP32</text>\n'

    # ESP32
    svg += f'<rect x="350" y="100" width="150" height="400" fill="{IC_FILL}" stroke="{COMP_STROKE}" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="425" y="290" text-anchor="middle" class="ic-label">ESP32-S3</text>\n'
    svg += f'<text x="425" y="310" text-anchor="middle" class="ic-label">WROOM-1</text>\n'
    svg += f'<text x="425" y="90" text-anchor="middle" class="ref">U3</text>\n'

    # ── Camera Section (right side) ──
    svg += f'<rect x="620" y="100" width="230" height="200" fill="#d5e8d4" stroke="{COMP_STROKE}" stroke-width="2" rx="6"/>\n'
    svg += f'<text x="735" y="125" text-anchor="middle" class="comp-label" style="font-size:14px">OV5640 Camera Module</text>\n'
    svg += f'<text x="735" y="145" text-anchor="middle" class="info">5MP 160-degree Wide Angle</text>\n'
    svg += f'<text x="735" y="165" text-anchor="middle" class="ref">Connected via 24-pin FPC ribbon (J5)</text>\n'

    cam_signals = [
        ("GPIO1 (SDA)", 130, "I2C Data", WIRE_COLORS['i2c']),
        ("GPIO2 (SCL)", 155, "I2C Clock", WIRE_COLORS['i2c']),
        ("GPIO4 (VSYNC)", 180, "Frame Sync", WIRE_COLORS['signal']),
        ("GPIO5 (HREF)", 200, "Line Valid", WIRE_COLORS['signal']),
        ("GPIO6 (PCLK)", 220, "Pixel Clock", WIRE_COLORS['signal']),
        ("GPIO7 (XCLK)", 240, "20MHz Ref", WIRE_COLORS['signal']),
        ("D2-D9", 265, "8-bit Data", WIRE_COLORS['signal']),
    ]
    for label, y, desc, color in cam_signals:
        svg += draw_wire(500, y, 620, y, color)
        svg += f'<text x="510" y="{y-4}" class="pin-label">{label}</text>\n'
        svg += f'<text x="625" y="{y+4}" class="pin-label">{desc}</text>\n'

    # I2C pull-ups
    svg += f'<text x="555" y="115" class="ref">R11, R12 (4.7K pull-ups to 3.3V)</text>\n'
    svg += draw_resistor(540, 120, ref="", value="4.7K")
    svg += draw_resistor(540, 140, ref="", value="4.7K")

    # Camera power
    svg += f'<text x="735" y="285" text-anchor="middle" class="info">Powered by 3.3V rail</text>\n'

    # ── Safety Interlock (bottom left) ──
    svg += f'<rect x="40" y="360" width="250" height="150" fill="#fadbd8" stroke="#e74c3c" stroke-width="2" rx="6"/>\n'
    svg += f'<text x="165" y="390" text-anchor="middle" class="comp-label" style="font-size:14px">Safety Interlock Circuit</text>\n'

    svg += f'<text x="60" y="420" class="info">3.3V ---[R15 10K]---+--- GPIO47</text>\n'
    svg += f'<text x="60" y="440" class="info">                    |</text>\n'
    svg += f'<text x="60" y="460" class="info">                   SW3 (lid switch)</text>\n'
    svg += f'<text x="60" y="480" class="info">                    |</text>\n'
    svg += f'<text x="60" y="500" class="info">                   GND</text>\n'

    svg += draw_wire(350, 440, 290, 440, WIRE_COLORS['safety'])
    svg += f'<text x="315" y="435" class="pin-label">GPIO47</text>\n'

    svg += f'<text x="165" y="420" text-anchor="middle" class="warning">Lid ON = LOW = SAFE</text>\n'
    svg += f'<text x="165" y="438" text-anchor="middle" class="warning">Lid OFF = HIGH = LASER KILLED</text>\n'

    # ── Status LED (bottom right) ──
    svg += f'<rect x="620" y="360" width="230" height="140" fill="#d5f5e3" stroke="#27ae60" stroke-width="2" rx="6"/>\n'
    svg += f'<text x="735" y="390" text-anchor="middle" class="comp-label" style="font-size:14px">Status LED (WS2812B)</text>\n'

    svg += draw_wire(500, 460, 620, 460, WIRE_COLORS['signal'])
    svg += f'<text x="520" y="455" class="pin-label">GPIO48</text>\n'
    svg += f'<text x="625" y="465" class="pin-label">DIN</text>\n'

    led_colors = [
        ("Green = Ready", "#27ae60"),
        ("Blue = Connected/Projecting", "#2980b9"),
        ("Amber = Calibrating", "#f39c12"),
        ("Red = Error", "#e74c3c"),
    ]
    for i, (desc, color) in enumerate(led_colors):
        ly = 415 + i * 20
        svg += f'<circle cx="640" cy="{ly}" r="6" fill="{color}"/>\n'
        svg += f'<text x="655" y="{ly+4}" class="pin-label">{desc}</text>\n'

    # Notch indicator
    svg += f'<text x="735" y="500" text-anchor="middle" class="warning">Match notched corner to PCB marking!</text>\n'

    svg += svg_footer()
    return svg


def main():
    diagrams = {
        "01_System_Overview.svg": create_system_overview(),
        "02_Power_Section.svg": create_power_detail(),
        "03_Laser_Driver.svg": create_laser_detail(),
        "04_DAC_Galvo_Signal.svg": create_dac_galvo_detail(),
        "05_Camera_Safety_LED.svg": create_peripherals_detail(),
    }

    diagrams_dir = os.path.join(OUTPUT_DIR, "wiring_diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)

    for filename, content in diagrams.items():
        filepath = os.path.join(diagrams_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Created: {filepath}")

    # Create an index HTML to view all diagrams
    html = '''<!DOCTYPE html>
<html><head>
<title>LayIt Laser - Wiring Diagrams</title>
<style>
body { font-family: 'Helvetica Neue', Arial, sans-serif; background: #f5f5f5; padding: 40px; }
h1 { color: #1a1a2e; }
h2 { color: #0f3460; margin-top: 40px; }
.diagram { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
           padding: 20px; margin: 20px 0; max-width: 100%; overflow-x: auto; }
img { max-width: 100%; height: auto; }
.note { color: #666; font-style: italic; }
</style>
</head><body>
<h1>LayIt Laser - Visual Wiring Guide</h1>
<p class="note">Open this file in any browser. Print it out and keep it next to your workbench!</p>

<h2>1. Complete System Overview</h2>
<div class="diagram"><img src="01_System_Overview.svg" alt="System Overview"></div>

<h2>2. Power Section Detail</h2>
<div class="diagram"><img src="02_Power_Section.svg" alt="Power Section"></div>

<h2>3. Laser Driver Circuit</h2>
<div class="diagram"><img src="03_Laser_Driver.svg" alt="Laser Driver"></div>

<h2>4. DAC + Op-Amp + Galvo Signal Path</h2>
<div class="diagram"><img src="04_DAC_Galvo_Signal.svg" alt="DAC and Galvo"></div>

<h2>5. Camera, Safety & Status LED</h2>
<div class="diagram"><img src="05_Camera_Safety_LED.svg" alt="Peripherals"></div>

<hr>
<p class="note">Generated for LayIt LLC | March 2026 | Use with LayIt_Laser_Assembly_Guide.pdf</p>
</body></html>'''

    html_path = os.path.join(diagrams_dir, "index.html")
    with open(html_path, 'w') as f:
        f.write(html)
    print(f"\nCreated viewer: {html_path}")
    print("Open this in any browser to see all diagrams!")


if __name__ == "__main__":
    main()
