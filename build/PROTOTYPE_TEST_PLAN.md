# LayIt Laser — Prototype Test Plan

## Phase 1: Breadboard Proof of Concept (~$50, 1 weekend)

### Goal
Validate the signal chain: ESP32 → DAC → Galvo → Laser can project a simple shape.

### Parts Needed
- ESP32-S3 dev board (~$10 on Amazon)
- MCP4822 DAC breakout or bare chip + breadboard ($5)
- 20Kpps galvo scanner set ($70-120 on AliExpress — order 2-3 weeks early)
- 5mW red laser pointer (DO NOT use 200mW for breadboard testing — safety)
- 12V 2A power supply ($8)
- Breadboard + jumper wires ($10)
- Multimeter

### Test Steps
1. Wire ESP32 SPI pins to MCP4822 (MOSI → SDI, SCK → SCK, CS → CS, LDAC → pull low)
2. Power MCP4822 from 5V (ESP32 VUSB or separate regulator)
3. Write simple firmware: output sine wave on channel A, cosine on channel B
4. Verify DAC output on oscilloscope or multimeter (should see 0-4V swing)
5. Connect DAC outputs to galvo driver analog inputs (check polarity!)
6. Power galvo driver from 12V supply
7. Attach laser pointer to galvo mirror mount
8. Power on — you should see a circle projected on the wall
9. Modify firmware to draw a square, then a hexagon
10. Measure projection accuracy: is the square actually square?

### Success Criteria
- [ ] DAC outputs clean analog signals (no noise, no glitches)
- [ ] Galvo mirrors respond to signal changes
- [ ] Projected shape is recognizable (square looks like a square)
- [ ] No visible flicker at 20Kpps
- [ ] Laser TTL blanking works (laser off between shapes)

### Common Issues
- **Galvo driver expects ±5V but DAC outputs 0-4V**: Need op-amp buffer (TL072) to shift/scale
- **Shape is distorted/skewed**: DAC channels have different gain — calibrate in firmware
- **Flicker**: Increase corner dwell time or reduce total point count
- **Mirrors oscillating/ringing**: Reduce scan speed or add damping

---

## Phase 2: Full Component Test (~$250, 1-2 weeks)

### Goal
Test all components together: camera, IMU, WiFi, laser, galvos, power system.

### Additional Parts
- 200mW 520nm green laser module (Laserland 4060-530D-200)
- OV5640 camera module with DVP ribbon cable
- MPU6050 IMU breakout
- TL072 op-amp + resistors for signal conditioning
- AMS1117-5.0 and AMS1117-3.3 voltage regulators
- USB-C PD trigger board
- Safety glasses OD4+ at 520nm (!!)

### Test Steps
1. Build power supply chain: USB-C PD → 12V → 5V (AMS1117) → 3.3V (AMS1117)
2. Verify all voltage rails with multimeter
3. Add TL072 op-amp buffer between DAC and galvo driver
4. Calibrate op-amp gain to match galvo input range
5. Swap red laser pointer for 200mW green module — PUT ON SAFETY GLASSES
6. Test laser TTL: ESP32 GPIO → MOSFET → Laser TTL (verify HIGH=off, LOW=on)
7. Connect OV5640 to ESP32 DVP pins — verify camera captures at VGA
8. Connect MPU6050 via I2C — verify accelerometer data reads
9. Test WiFi AP mode: ESP32 creates "LayIt-Laser" network
10. Load full firmware: connect from LayIt app, send tile pattern, verify projection

### Success Criteria
- [ ] 12V/5V/3.3V rails stable under load
- [ ] Green laser projects visible pattern in daylight
- [ ] Camera captures VGA frames at 2+ FPS
- [ ] IMU detects bumps (shake the breadboard)
- [ ] WiFi connects from phone, WebSocket exchanges data
- [ ] Tile pattern from app matches projected pattern on wall

---

## Phase 3: Vision Alignment Test

### Goal
Verify the camera-based alignment system can correct for projection errors.

### Test Steps
1. Place one white tile on a surface in the laser's field of view
2. Start camera capture on Core 0
3. Run Canny edge detection on captured frame
4. Detect tile edges → extract 4 corners
5. Compare detected corners vs. projected corners
6. Compute homography correction matrix
7. Apply correction to projection coordinates
8. Verify: projected outline now aligns with physical tile edges

### Success Criteria
- [ ] Camera detects tile edges reliably
- [ ] Homography correction reduces error to <2mm
- [ ] System maintains alignment after adding more tiles
- [ ] Bump detection triggers re-alignment within 1 second

---

## Phase 4: Enclosure & PCB (~$200-500)

### Goal
Move from breadboard to a proper enclosed unit.

### Steps
1. Design PCB (KiCad or EasyEDA) — 4-layer recommended
2. Order PCB from JLCPCB/PCBWay (~$20 for 5 boards)
3. Order all SMD components from DigiKey/Mouser
4. Assemble PCB (reflow oven or hot air station)
5. Drill Hammond enclosure for laser aperture, USB-C, camera lens, LED
6. Mount galvos, camera, laser module in enclosure
7. Add safety interlock microswitch on lid
8. Final assembly and full system test

### PCB Design Checklist
- [ ] 4-layer stackup with solid ground plane
- [ ] Thermal pads for AMS1117 regulators
- [ ] 10mm antenna keepout zone for ESP32-S3
- [ ] 0.1μF bypass caps on all IC power pins
- [ ] ESD protection diodes on external connectors
- [ ] Test points on all voltage rails
- [ ] Mounting holes aligned to Hammond 1455N1601BK

---

## Phase 5: Beta Testing (10 units)

### Goal
Get real installer feedback before production.

### Plan
1. Build 10 complete units
2. Recruit 10 tile installers (post on tile forums, local contractors)
3. Ship units with: laser, tripod, safety glasses, quick start guide
4. 30-day beta test period
5. Collect: video testimonials, accuracy measurements, feature requests, bug reports
6. Iterate firmware based on feedback
7. Document: average setup time, accuracy achieved, battery life measured

### Feedback Questions
1. How long did it take to set up? (target: <2 minutes)
2. Was the projected pattern accurate enough for real work?
3. Did the vision alignment work reliably?
4. Would you pay $499 for this?
5. What features are missing?
6. Would you recommend to other installers?

---

## Cost Summary

| Phase | Cost | Time |
|-------|------|------|
| Phase 1: Breadboard PoC | ~$50 | 1 weekend |
| Phase 2: Full Component | ~$250 | 1-2 weeks |
| Phase 3: Vision Test | $0 (same hardware) | 1 week |
| Phase 4: PCB + Enclosure | ~$200-500 | 2-4 weeks |
| Phase 5: Beta (10 units) | ~$3,000-4,000 | 4-6 weeks |
| **Total to beta** | **~$3,500-4,800** | **~10-14 weeks** |

## Timeline
- Fund Phase 1-2 from personal savings or app revenue ($300)
- Fund Phase 4-5 from app revenue (need ~$3K = ~600 Pro subscribers)
- Or seek angel investment / Kickstarter at this stage
