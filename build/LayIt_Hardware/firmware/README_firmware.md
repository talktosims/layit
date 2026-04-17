# LayIt Laser — Firmware Build Instructions

## Arduino IDE Setup

### Board Manager
1. Open Arduino IDE → File → Preferences
2. Add to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Tools → Board Manager → Search "esp32" → Install **esp32 by Espressif Systems** (v3.x+)

### Board Selection
- Board: **ESP32S3 Dev Module**
- USB CDC On Boot: **Enabled**
- USB Mode: **Hardware CDC and JTAG**
- Flash Size: **16MB (128Mb)**
- PSRAM: **OPI PSRAM**
- Partition Scheme: **Huge APP (3MB No OTA / 1MB SPIFFS)**
- Upload Speed: **921600**

### Required Libraries
Install via Library Manager (Sketch → Include Library → Manage Libraries):

| Library | Author | Version | Purpose |
|---------|--------|---------|---------|
| **ArduinoJson** | Benoit Blanchon | 7.x | JSON parsing for .layit format |
| **WebSockets** | Markus Sattler | 2.x | WebSocket server for app comms |
| **Adafruit NeoPixel** | Adafruit | 1.x | WS2812B status LED control |

The `esp_camera` library is included with the ESP32 board package (no separate install needed).

### Compile & Upload
1. Connect ESP32-S3 via USB-C cable
2. Hold BOOT button, press RESET, release BOOT (enters download mode)
3. Select correct COM port in Tools → Port
4. Click Upload (→)
5. Press RESET after upload completes

## WebSocket Protocol

The firmware acts as a WebSocket server. The LayIt app connects to:
```
ws://<device-ip>:81
```

### Messages FROM App → Device (JSON)

#### Load Pattern
```json
{
  "type": "load_pattern",
  "wall": { "width": 48, "height": 96 },
  "tile": { "shape": "herringbone", "width": 2, "height": 4, "grout": 0.125 },
  "voids": [{ "x": 10, "y": 20, "w": 12, "h": 8 }],
  "tiles": [
    { "verts": [[0,0], [2,0], [2,4], [0,4]] },
    ...
  ]
}
```

#### Set Segment
```json
{ "type": "set_segment", "x": 0, "y": 0, "width": 36, "height": 36 }
```

#### Set Distance
```json
{ "type": "set_distance", "distance": 6.2 }
```

#### Start/Stop Projection
```json
{ "type": "start" }
{ "type": "stop" }
```

#### Calibrate
```json
{ "type": "calibrate", "size": 12 }
```

### Messages FROM Device → App (JSON)

```json
{ "type": "device_info", "name": "LayIt Laser", "version": "1.0", "safety": true }
{ "type": "pattern_loaded", "tiles": 150, "points": 8500 }
{ "type": "segment_set", "points": 3200 }
{ "type": "distance_set", "coverage": 54.2 }
{ "type": "projecting", "active": true }
{ "type": "safety_stop", "msg": "Enclosure opened" }
{ "type": "error", "msg": "No pattern loaded" }
{ "type": "pong" }
```

## Safety Notes

- The firmware checks the safety interlock switch every scan cycle AND via hardware interrupt
- If the enclosure lid is opened, the laser is disabled within microseconds (ISR-driven)
- The laser auto-disables after 5 minutes of no communication from the app
- The laser cannot be enabled if the safety interlock is open
- All laser control goes through the `laserOn()` / `laserOff()` functions which check safety state

## Testing Without Hardware

For bench testing the firmware logic without the full laser/galvo assembly:
1. Connect just the ESP32-S3 via USB
2. Open Serial Monitor at 115200 baud
3. Connect to the "LayIt-Laser" WiFi network from your phone
4. Open the status page at http://192.168.4.1
5. Use a WebSocket client (like "Simple WebSocket Client" browser extension) to send test messages

The DAC/galvo/laser outputs can be verified with an oscilloscope on the SPI and GPIO14 pins.
