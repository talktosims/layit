# Tier C — Photo-Modeling Dimensions Reference

Specs collected from manufacturer pages. When the parts arrive, verify with calipers and update.

## Laser Module — Laserland 4060-530D-200
- **Wavelength:** 520nm green
- **Output:** 200mW
- **Voltage:** 12VDC, <1.2A
- **Beam diameter:** 12-15mm (head aperture)
- **TTL:** 15kHz
- **Body shape:** Cube housing (per Laserland page)
- **Pigtail:** 3 wires (12V red, TTL green, GND black) — exit point + length to be measured on receipt
- **Photos:** `reference_photos/laser/`
- **Source:** [laserlands.net](https://www.laserlands.net/4060-530d-200-12v-ttl.html)

## Galvanometer Set — 20K PPS dual-axis
- **Mirror size:** 7mm × 11mm × 0.6mm
- **Driver board:** 80mm × 50mm × 28mm
- **Motor type:** Closed-loop moving magnet
- **Power:** ±15V (1.0A / 0.6A)
- **Input signal:** ±5V differential, 200kΩ
- **Optical range:** ±30°
- **Photos:** `reference_photos/galvos/`
- **Source:** [laser-parts.com](http://laser-parts.com/20kpps-galvanometer-set.html)

## USB-C PD Trigger Board — ZY12PDN (YZX Studio)
- **PCB:** 31mm × 15mm × 4mm
- **USB-C connector:** at one end (use the GCT USB4500 STEP from `models/manual/connectors/`)
- **Output:** solder pads at opposite end (12V + GND)
- **Photos:** `reference_photos/usb_c_pd_trigger/`
- **Source:** [joy-it.net](https://joy-it.net/en/products/COM-ZY12PDN)

## Camera — OV5640 24-pin DVP wide-angle
- **PCB:** 14mm × 70mm × 13.85mm (long, narrow form factor)
- **Lens:** Wide-angle, ~160-220° field of view, fixed focus
- **Interface:** 24-pin DVP via 0.5mm pitch FPC
- **Reference STEP:** `photo_model/camera/OV5640_Toradex_reference.step` (Toradex CSI variant — different PCB, but the OV5640 sensor + lens stack is the same)
- **Photos:** `reference_photos/camera/`
- **Source:** [yxfcamera.com](https://www.yxfcamera.com/products/DVP-Camera-Module/5mp-esp32-cam-ultra-wide-angle-low-noise-ov5640-dvp-camera-module.html)

## Modeling priority for wire routing

For each part, the modeling priority is **connectors first, body shape second**:

| Part | Critical for wire routing | Less critical |
|---|---|---|
| Laser module | 3-wire pigtail exit point | Exact body curvature |
| Galvos (×2) | Motor base mounting holes, mirror axis | Body cosmetic detail |
| Galvo driver board | Input header (J4 6-pin XH), output to galvo motors | Component placement on PCB |
| USB-C trigger | USB-C connector position + 12V/GND output pads | Solder mask color |
| OV5640 | 24-pin FPC connector position + ribbon entry direction | Lens housing detail |

Once parts arrive, verify dimensions against calipers and the binder dim drawings before finalizing the .blend file.
