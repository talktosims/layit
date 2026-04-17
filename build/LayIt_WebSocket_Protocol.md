# LayIt Laser WebSocket Protocol Specification

**Firmware version:** 1.2
**Date:** March 2026
**Hardware:** ESP32-S3-WROOM-1 + MCP4822 DAC + Galvo Scanner + 520nm Laser

---

## 1. Connection

### WiFi Access Point

| Parameter   | Value           |
|-------------|-----------------|
| SSID        | `LayIt-Laser`   |
| Password    | `layitlaser`    |
| Auth        | WPA2            |
| Channel     | 1               |
| Max clients | 2               |

The device always creates its own AP. If `USE_STATION_MODE` is enabled in firmware, the device also connects to an existing network (dual AP+STA mode), but the AP is always available.

### WebSocket Endpoint

```
ws://192.168.4.1:81
```

Default AP IP is `192.168.4.1`. Connect on port **81** using a standard WebSocket client. The firmware uses the `WebSocketsServer` library (text frames, JSON payloads).

### HTTP Status Endpoints

| Endpoint  | Method | Description                          |
|-----------|--------|--------------------------------------|
| `/`       | GET    | HTML status page (human-readable)    |
| `/status` | GET    | JSON status object (machine-readable)|

`/status` response:

```json
{
  "safety": true,
  "connected": true,
  "projecting": false,
  "tiles": 42,
  "distance": 6.00,
  "imu": true,
  "camera": true,
  "grout_mode": "SINGLE",
  "grout_auto": true
}
```

---

## 2. Commands (App to Laser)

All commands are JSON text frames with a required `"type"` field.

### 2.1 `load_pattern` — Load tile pattern

Sends the complete `.layit` pattern data to the device. Stops any active projection before loading.

```json
{
  "type": "load_pattern",
  "wall": {
    "width": 96.0,
    "height": 48.0
  },
  "tile": {
    "width": 12.0,
    "height": 12.0,
    "grout": 0.125,
    "shape": "square"
  },
  "voids": [
    { "x": 24.0, "y": 12.0, "w": 18.0, "h": 24.0 }
  ],
  "tiles": [
    {
      "verts": [[0.0, 0.0], [12.0, 0.0], [12.0, 12.0], [0.0, 12.0]],
      "isCut": false
    },
    {
      "verts": [[0.0, 0.0], [6.5, 0.0], [6.5, 12.0], [0.0, 12.0]],
      "isCut": true
    }
  ]
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `wall.width` | float | 48.0 | Wall width in inches |
| `wall.height` | float | 48.0 | Wall height in inches |
| `tile.width` | float | 12.0 | Tile width in inches |
| `tile.height` | float | 12.0 | Tile height in inches |
| `tile.grout` | float | 0.125 | Grout gap in inches |
| `tile.shape` | string | `"square"` | One of: `"square"`, `"rectangle"`, `"hexagon"`, `"herringbone"` |
| `voids` | array | `[]` | Void regions (toilets, drains, etc.) to skip |
| `voids[].x, .y, .w, .h` | float | 0.0 | Void bounding box in inches |
| `tiles` | array | required | Array of tile objects |
| `tiles[].verts` | array | required | Array of `[x, y]` vertex pairs in inches (max 8 vertices) |
| `tiles[].isCut` | bool | false | Whether this tile needs cutting (clipped by wall/void) |

**Limits:** Max 500 tiles, max 8 vertices per tile, max 20 voids.

**Response:** `pattern_loaded` (see section 3.1)

### 2.2 `set_segment` — Set projection segment

Selects which region of the overall pattern to project. The laser can only project a limited area at once (typically 36x36 inches at 6 feet).

```json
{
  "type": "set_segment",
  "x": 36.0,
  "y": 0.0,
  "width": 36.0,
  "height": 36.0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `x` | float | 0.0 | Segment origin X in inches |
| `y` | float | 0.0 | Segment origin Y in inches |
| `width` | float | 36.0 | Segment width in inches |
| `height` | float | 36.0 | Segment height in inches |

**Response:** `segment_set` (see section 3.2). May also trigger `advisory` messages.

### 2.3 `set_distance` — Set projection distance

Manually set how far the laser is from the projection surface. Recomputes the inches-to-DAC mapping and rebuilds the scan buffer.

```json
{
  "type": "set_distance",
  "distance": 8.0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `distance` | float | 6.0 | Distance from laser to surface in feet |

**Response:** `distance_set` (see section 3.3). May also trigger `advisory` messages.

### 2.4 `auto_distance` — Auto-detect distance via camera

Triggers the onboard camera to measure the projection distance automatically. The device projects a 12-inch calibration square, captures a frame, and calculates distance from the apparent angular size.

```json
{
  "type": "auto_distance"
}
```

No parameters.

**Response:** `auto_distance` (see section 3.4), or `error` if camera is unavailable.

### 2.5 `start` — Start projection

Begins projecting the loaded pattern. Requires a pattern to be loaded and the safety interlock to be closed.

```json
{
  "type": "start"
}
```

**Response:** `projecting` with `active: true` (see section 3.5), or `error` if no pattern is loaded or safety interlock is open.

### 2.6 `stop` — Stop projection

Stops the laser and returns galvos to center position.

```json
{
  "type": "stop"
}
```

**Response:** `projecting` with `active: false`.

### 2.7 `calibrate` — Project calibration square

Projects a known-size square with crosshair for manual distance verification.

```json
{
  "type": "calibrate",
  "size": 12.0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `size` | float | 12.0 | Side length of calibration square in inches |

**Response:** None (the laser begins projecting the calibration pattern immediately).

### 2.8 `recalibrate_imu` — Reset IMU baseline

Resets the tilt compensation baseline to the current device orientation. Use after intentionally repositioning the laser.

```json
{
  "type": "recalibrate_imu"
}
```

**Response:** `imu_recalibrated` (see section 3.6), or `error` if IMU is not available.

### 2.9 `set_grout_mode` — Set grout rendering mode

Override or restore auto-selection of the grout rendering algorithm.

```json
{
  "type": "set_grout_mode",
  "mode": 0
}
```

| Mode | Name | Description |
|------|------|-------------|
| 0 | AUTO | Auto-select DUAL or SINGLE based on beam-to-grout ratio (default) |
| 1 | DUAL | Two lines per grout channel (beam is thin relative to grout) |
| 2 | SINGLE | One line per grout channel with shared-edge deduplication |
| 3 | MINIMAL | Corner dots only for interior tiles (manual override only, never auto-selected) |

**Response:** `grout_mode_set` (see section 3.7), or `error` if mode is out of range.

### 2.10 `ping` — Keepalive

```json
{
  "type": "ping"
}
```

**Response:** `pong` (see section 3.8).

---

## 3. Responses and Events (Laser to App)

All responses are JSON text frames with a `"type"` field.

### 3.1 `device_info` — Sent on connection

Sent automatically when a WebSocket client connects.

```json
{
  "type": "device_info",
  "name": "LayIt Laser",
  "version": "1.2",
  "safety": true,
  "imu": true,
  "camera": true,
  "grout_mode": "DUAL",
  "grout_auto": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Always `"LayIt Laser"` |
| `version` | string | Firmware version |
| `safety` | bool | Safety interlock state (true = closed/safe) |
| `imu` | bool | Whether MPU6050 IMU was detected |
| `camera` | bool | Whether OV5640 camera was detected |
| `grout_mode` | string | Current grout mode: `"DUAL"`, `"SINGLE"`, or `"MINIMAL"` |
| `grout_auto` | bool | Whether grout mode is auto-selected |

### 3.2 `pattern_loaded` — Pattern load acknowledgment

```json
{
  "type": "pattern_loaded",
  "tiles": 42,
  "cut_tiles": 6,
  "points": 8400,
  "grout_mode": "SINGLE",
  "grout_auto": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tiles` | int | Total tile count loaded |
| `cut_tiles` | int | Number of cut tiles |
| `points` | int | Scan buffer point count |
| `grout_mode` | string | Active grout rendering mode |
| `grout_auto` | bool | Whether mode was auto-selected |

### 3.3 `segment_set` — Segment change acknowledgment

```json
{
  "type": "segment_set",
  "points": 5200
}
```

| Field | Type | Description |
|-------|------|-------------|
| `points` | int | Scan buffer point count for this segment |

### 3.4 `distance_set` — Distance change acknowledgment

```json
{
  "type": "distance_set",
  "coverage": 52.4
}
```

| Field | Type | Description |
|-------|------|-------------|
| `coverage` | float | Projection coverage area in inches (computed from distance and galvo angle) |

### 3.5 `auto_distance` — Auto-distance measurement result

Success:

```json
{
  "type": "auto_distance",
  "success": true,
  "distance_ft": 6.25,
  "coverage_in": 54.6,
  "confidence": 0.85,
  "bright_pixels": 850
}
```

Failure:

```json
{
  "type": "auto_distance",
  "success": false,
  "msg": "Could not detect laser pattern"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether measurement succeeded |
| `distance_ft` | float | Measured distance in feet (2.0 - 20.0 valid range) |
| `coverage_in` | float | Computed projection coverage in inches |
| `confidence` | float | 0.0 - 1.0, based on bright pixel count (more pixels = more reliable) |
| `bright_pixels` | int | Number of bright pixels detected in camera frame |
| `msg` | string | Error message (only present on failure) |

### 3.6 `projecting` — Projection state change

```json
{
  "type": "projecting",
  "active": true
}
```

### 3.7 `imu_recalibrated` — IMU baseline reset confirmation

```json
{
  "type": "imu_recalibrated"
}
```

### 3.8 `grout_mode_set` — Grout mode change acknowledgment

```json
{
  "type": "grout_mode_set",
  "mode": 1,
  "mode_name": "SINGLE",
  "auto": false,
  "points": 6800
}
```

| Field | Type | Description |
|-------|------|-------------|
| `mode` | int | Numeric mode (0 = DUAL, 1 = SINGLE, 2 = MINIMAL) |
| `mode_name` | string | Human-readable mode name |
| `auto` | bool | Whether auto-selection is active |
| `points` | int | Updated scan buffer point count |

### 3.9 `pong` — Ping response

```json
{
  "type": "pong"
}
```

---

## 4. Safety Messages

### 4.1 `safety_stop` — Emergency stop

Sent when the safety interlock is opened while projecting. The laser is immediately disabled by hardware interrupt (ISR) before this message is sent.

```json
{
  "type": "safety_stop",
  "msg": "Enclosure opened"
}
```

The client must send `start` again after the interlock is closed to resume projection.

---

## 5. IMU Telemetry

### 5.1 `imu_status` — Periodic tilt report

Sent every **2 seconds** while a client is connected and the IMU is active.

```json
{
  "type": "imu_status",
  "pitch": 0.3,
  "roll": -0.1,
  "tilt_corrected": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `pitch` | float | Current pitch delta from baseline in degrees |
| `roll` | float | Current roll delta from baseline in degrees |
| `tilt_corrected` | bool | Whether tilt correction is actively being applied (true if DAC correction > 1 unit on either axis) |

The firmware automatically compensates for tilt up to 5 degrees. Beyond that, corrections are clamped.

### 5.2 `bump_detected` — Bump event

Sent when accelerometer detects a spike exceeding 0.5g above resting 1g. After a bump, the IMU baseline is automatically recalibrated and the scan buffer is rebuilt. A 500ms cooldown prevents duplicate detections.

```json
{
  "type": "bump_detected",
  "magnitude": 1.73
}
```

| Field | Type | Description |
|-------|------|-------------|
| `magnitude` | float | Total acceleration magnitude in g (resting = 1.0, bump > 1.5) |

---

## 6. Advisory Messages

Informational messages sent after `load_pattern`, `set_segment`, or `set_distance` when projection settings are suboptimal. The laser still functions -- these help the app guide the user.

```json
{
  "type": "advisory",
  "level": "warning",
  "category": "distance",
  "message": "Laser is 11.0ft from the surface...",
  "distance_ft": 11.0,
  "recommended_max": 8.0
}
```

### Levels

| Level | Meaning |
|-------|---------|
| `"suggestion"` | Soft guidance, things still work fine |
| `"warning"` | Quality is noticeably degraded |

### Categories

#### `"distance"` — Projection distance advisory

Triggered when distance exceeds 8 feet (suggestion) or 10 feet (warning).

| Field | Type | Description |
|-------|------|-------------|
| `distance_ft` | float | Current distance |
| `recommended_max` | float | Recommended max distance (8.0 ft) |

#### `"segment_size"` — Segment too large

Triggered when the largest segment dimension exceeds 48 inches.

| Field | Type | Description |
|-------|------|-------------|
| `segment_w` | float | Current segment width in inches |
| `segment_h` | float | Current segment height in inches |
| `tiles_in_segment` | int | Number of tiles in the segment |
| `tiles_simplified` | int | Number of tiles demoted to corner-dot rendering by point budget |

---

## 7. Error Handling

All errors use the same format:

```json
{
  "type": "error",
  "msg": "Description of the error"
}
```

### Known error messages

| Message | Trigger |
|---------|---------|
| `"Invalid JSON"` | Malformed JSON payload |
| `"Missing type field"` | JSON object has no `type` key |
| `"No pattern loaded"` | `start` sent before `load_pattern` |
| `"Safety interlock open"` | `start` sent while enclosure lid is open |
| `"Camera not available"` | `auto_distance` sent but OV5640 not detected |
| `"Camera capture failed"` | Camera frame grab failed during auto-distance |
| `"IMU not available"` | `recalibrate_imu` sent but MPU6050 not detected |
| `"Invalid grout mode (0-3)"` | `set_grout_mode` with mode outside 0-3 |

---

## 8. `.layit` JSON Format

The `.layit` format is the payload of the `load_pattern` command. It is a self-contained description of a tile layout.

### Schema

```json
{
  "type": "load_pattern",

  "wall": {
    "width": 96.0,
    "height": 48.0
  },

  "tile": {
    "width": 12.0,
    "height": 12.0,
    "grout": 0.125,
    "shape": "herringbone"
  },

  "voids": [
    { "x": 0.0, "y": 0.0, "w": 6.0, "h": 6.0 }
  ],

  "tiles": [
    {
      "verts": [[0.0, 0.0], [12.0, 0.0], [12.0, 12.0], [0.0, 12.0]],
      "isCut": false
    }
  ]
}
```

### Coordinate system

- All measurements are in **inches**.
- Origin `(0, 0)` is the bottom-left corner of the wall.
- Vertices are specified as `[x, y]` pairs.
- Tiles are pre-computed by the app, including any rotation, offset, and clipping.
- Cut tiles (`isCut: true`) have vertices that define the clipped polygon (not the original full tile).

### Tile shapes and vertex counts

| Shape | Vertices |
|-------|----------|
| `"square"` | 4 |
| `"rectangle"` | 4 |
| `"herringbone"` | 4 |
| `"hexagon"` | 6 |

### Grout sizes (common values)

| Grout | Inches | Use case |
|-------|--------|----------|
| 1/16" | 0.0625 | Rectified porcelain, minimal grout |
| 1/8"  | 0.125  | Standard ceramic tile |
| 3/16" | 0.1875 | Wood-look plank tiles |
| 1/4"  | 0.25   | Stone, outdoor tile |

---

## 9. Typical Message Flow

```
Client                              Laser
  |                                   |
  |--- WebSocket connect ------------>|
  |<-- device_info -------------------|
  |                                   |
  |--- load_pattern ----------------->|
  |<-- pattern_loaded ----------------|
  |<-- advisory (if applicable) ------|
  |                                   |
  |--- set_distance ----------------->|
  |<-- distance_set ------------------|
  |<-- advisory (if applicable) ------|
  |                                   |
  |--- set_segment ------------------>|
  |<-- segment_set -------------------|
  |<-- advisory (if applicable) ------|
  |                                   |
  |--- start ------------------------>|
  |<-- projecting {active: true} -----|
  |                                   |
  |<-- imu_status (every 2s) ---------|
  |<-- bump_detected (if bumped) -----|
  |                                   |
  |--- stop ------------------------->|
  |<-- projecting {active: false} ----|
  |                                   |
  |--- disconnect ------------------->|
```

---

## 10. Device Timeouts and Limits

| Parameter | Value |
|-----------|-------|
| Auto-off timeout | 5 minutes of no WebSocket data |
| Max tiles | 500 |
| Max vertices per tile | 8 |
| Max voids | 20 |
| Max scan points | 20,000 |
| Point budget (80%) | 16,000 |
| Scan rate | 20,000 points/sec |
| IMU poll rate | 100 Hz |
| IMU telemetry rate | Every 2 seconds |
| Bump threshold | 0.5g above resting |
| Bump cooldown | 500ms |
| Max tilt correction | 5 degrees |
| Valid auto-distance range | 2 - 20 feet |
