/**
 * ============================================================================
 * LayIt Laser — Firmware v1.2
 * ============================================================================
 *
 * Tile Pattern Laser Projection System
 * Hardware: ESP32-S3-WROOM-1 (N16R8) + MCP4822 DAC + Galvo Scanner + 520nm Laser
 *
 * This firmware:
 *   1. Creates a WiFi Access Point (or connects to existing network)
 *   2. Runs a WebSocket server to receive pattern data from the LayIt app
 *   3. Parses tile vertex data from .layit JSON format
 *   4. Converts tile outlines into optimized galvo scan paths (point lists)
 *   5. Drives the MCP4822 DAC via SPI to control galvo XY mirrors
 *   6. Controls laser blanking (on/off) via GPIO for TTL
 *   7. Monitors safety interlock switch
 *   8. Provides status via WS2812B RGB LED
 *   9. IMU-based bump detection and tilt compensation (MPU6050)
 *  10. Nearest-neighbor scan path optimization for reduced flicker
 *  11. Cut-line highlighting with dashed projection for cut tiles
 *  12. Auto-distance detection via onboard camera
 *  13. Adaptive grout rendering (DUAL/SINGLE/MINIMAL auto-selected by beam size)
 *  14. Priority-based line rendering with point budget enforcement
 *
 * License: MIT
 * Author: LayIt / Generated with Claude
 * Date: March 2026
 *
 * ============================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <SPI.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <esp_camera.h>
#include <math.h>

// ============================================================================
// PIN DEFINITIONS (Match schematic Rev 1.0)
// ============================================================================

// SPI to MCP4822 DAC
#define PIN_SPI_CS    10    // GPIO10 → MCP4822 /CS
#define PIN_SPI_MOSI  11    // GPIO11 → MCP4822 SDI
#define PIN_SPI_CLK   12    // GPIO12 → MCP4822 SCK
#define PIN_DAC_LDAC  13    // GPIO13 → MCP4822 /LDAC (simultaneous latch)

// Laser TTL Control
#define PIN_LASER_TTL 14    // GPIO14 → MOSFET gate (inverted: HIGH=laser OFF)

// Camera DVP Pins
#define PIN_CAM_VSYNC  4
#define PIN_CAM_HREF   5
#define PIN_CAM_PCLK   6
#define PIN_CAM_XCLK   7
#define PIN_CAM_D2    15
#define PIN_CAM_D3    16
#define PIN_CAM_D4    17
#define PIN_CAM_D5    18
#define PIN_CAM_D6     8
#define PIN_CAM_D7     9
#define PIN_CAM_D8    45
#define PIN_CAM_D9    46
#define PIN_CAM_SDA    1
#define PIN_CAM_SCL    2

// Status LED
#define PIN_STATUS_LED 48   // GPIO48 → WS2812B DIN

// Safety Interlock
#define PIN_SAFETY     47   // GPIO47 → Lid switch (LOW = safe, HIGH = kill)

// ============================================================================
// CONFIGURATION
// ============================================================================

// WiFi - Access Point mode (device creates its own network)
#define WIFI_AP_SSID     "LayIt-Laser"
#define WIFI_AP_PASSWORD "layitlaser"  // Min 8 chars for WPA2
#define WIFI_AP_CHANNEL  1
#define WIFI_AP_MAX_CONN 2

// WiFi - Station mode (connect to existing network) - optional
// Set USE_STATION_MODE to true and fill in your network credentials
#define USE_STATION_MODE false
#define WIFI_STA_SSID    "YourNetwork"
#define WIFI_STA_PASS    "YourPassword"

// WebSocket server port
#define WS_PORT 81
#define HTTP_PORT 80

// Galvo / DAC Configuration
#define DAC_RESOLUTION   4096     // 12-bit DAC: 0-4095
#define DAC_CENTER       2048     // Midpoint = 0° deflection
#define GALVO_MAX_ANGLE  20.0f    // ±20 degrees scan range
#define SPI_SPEED        10000000 // 10 MHz SPI clock

// Scan Timing
#define POINTS_PER_SECOND  20000   // 20K PPS (match galvo spec)
#define POINT_DELAY_US     50      // 1,000,000 / 20000 = 50μs per point
#define BLANKING_DELAY_US  100     // Extra settle time when laser is off (moving)
#define CORNER_DWELL       3       // Repeat corner points for brighter corners

// Projection
#define MAX_TILES          500     // Max tiles in pattern
#define MAX_VERTS_PER_TILE 8       // Hexagon = 6, Square = 4, Herringbone = 4
#define MAX_SCAN_POINTS    20000   // Max points in scan buffer
#define MAX_VOIDS          20      // Max void regions

// Safety
#define SAFETY_CHECK_MS    10      // Check interlock every 10ms
#define LASER_TIMEOUT_MS   300000  // Auto-off after 5 minutes of no data

// LED colors
#define COLOR_READY       0x00FF00  // Green - ready for connection
#define COLOR_CONNECTED   0x0044FF  // Blue - connected to app
#define COLOR_PROJECTING  0x0088FF  // Bright blue - actively projecting
#define COLOR_CALIBRATING 0xFF8800  // Amber - calibrating
#define COLOR_BUMP        0xFF4400  // Orange - bump detected
#define COLOR_ERROR       0xFF0000  // Red - error state
#define COLOR_OFF         0x000000  // Off

// ── IMU (MPU6050) ──
#define IMU_ADDR            0x68    // MPU6050 I2C address (AD0 = GND)
#define IMU_REG_PWR_MGMT_1  0x6B    // Power management register
#define IMU_REG_ACCEL_CFG   0x1C    // Accelerometer config (range)
#define IMU_REG_GYRO_CFG    0x1B    // Gyroscope config (range)
#define IMU_REG_ACCEL_XOUT  0x3B    // First accel data register (14 bytes: accel+temp+gyro)
#define BUMP_THRESHOLD_G    0.5f    // Acceleration spike above 1g to count as bump
#define IMU_POLL_MS         10      // Poll IMU every 10ms (100Hz)
#define TILT_CORRECT_MAX    5.0f    // Max degrees of tilt we'll correct for
#define BUMP_COOLDOWN_MS    500     // Ignore bumps for 500ms after one is detected

// ── Cut-Line Highlighting ──
#define DASH_LENGTH_DAC     80      // ~2° galvo movement per dash segment
#define DASH_GAP_DAC        40      // Gap between dashes (half-length)
#define CUT_CORNER_DWELL    5       // Extra dwell on cut tile corners (vs 3 for full tiles)

// ── Auto-Distance Detection ──
#define CAL_SETTLE_MS       500     // Wait for galvos to settle during auto-distance
#define LASER_BRIGHT_THRESH 200     // Pixel brightness threshold for laser detection (0-255)
#define MIN_BRIGHT_PIXELS   50      // Minimum bright pixels for valid detection
#define CAM_FOV_DEGREES     160.0f  // OV5640 lens FOV
#define CAM_WIDTH_PX        640     // VGA width
#define CAM_HEIGHT_PX       480     // VGA height

// ── Adaptive Grout Rendering ──
#define BEAM_DIVERGENCE_MRAD 1.5f    // Typical 200mW 520nm module beam divergence
#define GROUT_DUAL_RATIO     0.6f    // beamSpot/groutWidth < this → DUAL mode (two lines per grout)
#define GROUT_MINIMAL_RATIO  1.5f    // beamSpot/groutWidth > this → MINIMAL mode (corner dots)
#define EDGE_QUANT_PRECISION 100     // 1/100th inch quantization for edge dedup keys
#define MAX_DRAWN_EDGES      2000    // Max edges to track for deduplication in SINGLE mode
#define CORNER_DOT_DWELL     6       // Dwell points at each corner in MINIMAL mode

// ── Priority-Based Line Rendering ──
#define POINT_BUDGET_RATIO   0.80f   // Use at most 80% of MAX_SCAN_POINTS (= 16000)
#define POINTS_PER_TILE_FULL 60      // Estimated scan points for a full tile outline
#define POINTS_PER_TILE_CORNER 24    // Estimated scan points for corners-only rendering

// ============================================================================
// GLOBAL STATE
// ============================================================================

// Hardware Objects
SPIClass *dacSPI = NULL;
WebServer httpServer(HTTP_PORT);
WebSocketsServer wsServer(WS_PORT);
Adafruit_NeoPixel statusLED(1, PIN_STATUS_LED, NEO_GRB + NEO_KHZ800);

// ── Projection Data ──

// A single point in the scan buffer
struct ScanPoint {
  uint16_t x;       // DAC value 0-4095
  uint16_t y;       // DAC value 0-4095
  bool     laserOn; // true = beam visible, false = blanked (moving)
};

// Tile vertex data (received from app)
struct TileData {
  float verts[MAX_VERTS_PER_TILE][2]; // [x,y] in inches
  uint8_t vertCount;
  bool isCut;       // true if tile needs cutting (clipped by wall/void)
};

// Void region (area to skip)
struct VoidRegion {
  float x, y, w, h; // in inches
};

// Pattern configuration
struct PatternConfig {
  float wallWidth;      // inches
  float wallHeight;     // inches
  float tileWidth;      // inches
  float tileHeight;     // inches
  float groutSize;      // inches
  char  tileShape[16];  // "herringbone", "hexagon", "square", "rectangle"
};

// Projection state
PatternConfig   pattern;
TileData        tiles[MAX_TILES];
uint16_t        tileCount = 0;
VoidRegion      voids[MAX_VOIDS];
uint8_t         voidCount = 0;

// Scan buffer (pre-computed DAC values)
ScanPoint       scanBuffer[MAX_SCAN_POINTS];
uint32_t        scanPointCount = 0;
volatile bool   projecting = false;
volatile bool   patternLoaded = false;

// Calibration
float           projectionDistanceFt = 6.0f;  // Default 6 feet
float           coverageInches = 0.0f;        // Computed from distance
float           inchesToDac = 1.0f;            // Conversion factor
float           originX = 0.0f;                // Projection origin offset X (inches)
float           originY = 0.0f;                // Projection origin offset Y (inches)

// Segment projection
float           segmentX = 0.0f;              // Current segment origin X (inches)
float           segmentY = 0.0f;              // Current segment origin Y (inches)
float           segmentW = 36.0f;             // Segment width (inches)
float           segmentH = 36.0f;             // Segment height (inches)

// Safety
volatile bool   safetyOK = false;
volatile bool   laserEnabled = false;
unsigned long   lastDataTime = 0;

// Connection
bool            clientConnected = false;
uint8_t         connectedClient = 0;

// LED animation
unsigned long   lastLEDUpdate = 0;
uint8_t         ledPulsePhase = 0;

// ── IMU State ──
bool            imuReady = false;
float           baselinePitch = 0.0f;    // Pitch at setup (radians)
float           baselineRoll = 0.0f;     // Roll at setup (radians)
float           currentPitch = 0.0f;     // Current pitch (radians)
float           currentRoll = 0.0f;      // Current roll (radians)
float           tiltCorrectionX = 0.0f;  // DAC correction for tilt (X axis)
float           tiltCorrectionY = 0.0f;  // DAC correction for tilt (Y axis)
bool            bumpDetected = false;
unsigned long   lastIMUPoll = 0;
unsigned long   lastBumpTime = 0;
unsigned long   lastIMUReport = 0;

// ── Scan Path Optimization ──
struct TileCenter {
  uint16_t tileIdx;   // Index into tiles[] array
  float cx, cy;       // Center position in inches
  bool visited;
};
TileCenter      tileCenters[MAX_TILES];
uint16_t        tileOrder[MAX_TILES];    // Optimized drawing order
uint16_t        segmentTileCount = 0;    // Tiles in current segment

// ── Camera State ──
bool            cameraReady = false;

// ── Adaptive Grout Rendering ──
enum GroutMode { GROUT_DUAL, GROUT_SINGLE, GROUT_MINIMAL };
GroutMode       currentGroutMode = GROUT_DUAL;
bool            groutModeAuto = true;  // Auto-select mode based on beam/grout ratio

// Edge deduplication for GROUT_SINGLE mode — prevents drawing shared edges twice
struct EdgeKey {
  int32_t x1, y1, x2, y2;  // Quantized vertex pairs (hundredths of an inch)
};
EdgeKey         drawnEdges[MAX_DRAWN_EDGES];
uint16_t        drawnEdgeCount = 0;

// ── Priority-Based Line Rendering ──
enum TilePriority { PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW };
TilePriority    tilePriorities[MAX_TILES];
uint16_t        pointBudget = 0;

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=== LayIt Laser v1.2 ===");
  Serial.println("Initializing...\n");

  // ── Pin Setup ──
  pinMode(PIN_LASER_TTL, OUTPUT);
  digitalWrite(PIN_LASER_TTL, HIGH);  // HIGH = MOSFET ON = TTL LOW = Laser OFF (safe default)

  pinMode(PIN_DAC_LDAC, OUTPUT);
  digitalWrite(PIN_DAC_LDAC, HIGH);   // HIGH = hold (don't latch yet)

  pinMode(PIN_SAFETY, INPUT);         // External pull-up R15

  // ── Status LED ──
  statusLED.begin();
  statusLED.setBrightness(40);  // Not blinding
  setStatusColor(COLOR_ERROR);   // Red until initialized

  // ── Safety Check ──
  safetyOK = (digitalRead(PIN_SAFETY) == LOW);
  if (!safetyOK) {
    Serial.println("WARNING: Safety interlock OPEN. Close enclosure lid.");
  }

  // ── SPI for DAC ──
  dacSPI = new SPIClass(HSPI);
  dacSPI->begin(PIN_SPI_CLK, -1, PIN_SPI_MOSI, PIN_SPI_CS);
  pinMode(PIN_SPI_CS, OUTPUT);
  digitalWrite(PIN_SPI_CS, HIGH);  // Deselect DAC

  // Center the galvos at startup
  writeDACBoth(DAC_CENTER, DAC_CENTER);
  Serial.println("DAC initialized, galvos centered.");

  // ── IMU (MPU6050) ──
  setupIMU();

  // ── Camera (OV5640) ──
  setupCamera();

  // ── WiFi ──
  setupWiFi();

  // ── HTTP Server (for status page) ──
  setupHTTPServer();
  httpServer.begin();
  Serial.println("HTTP server started on port 80");

  // ── WebSocket Server ──
  wsServer.begin();
  wsServer.onEvent(onWebSocketEvent);
  Serial.println("WebSocket server started on port 81");

  // ── Safety Interrupt ──
  attachInterrupt(digitalPinToInterrupt(PIN_SAFETY), safetyISR, CHANGE);

  // ── Ready ──
  setStatusColor(COLOR_READY);
  lastDataTime = millis();

  Serial.println("\n=== LayIt Laser READY ===");
  Serial.printf("Connect to WiFi: %s\n", WIFI_AP_SSID);
  Serial.printf("Password: %s\n", WIFI_AP_PASSWORD);
  Serial.printf("WebSocket: ws://%s:%d\n", WiFi.softAPIP().toString().c_str(), WS_PORT);
  Serial.printf("IMU: %s | Camera: %s\n",
                imuReady ? "OK" : "NOT FOUND",
                cameraReady ? "OK" : "NOT FOUND");
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // Handle network
  httpServer.handleClient();
  wsServer.loop();

  // Safety check (redundant with ISR, but belt-and-suspenders)
  safetyOK = (digitalRead(PIN_SAFETY) == LOW);

  // Auto-timeout: disable laser if no data for 5 minutes
  if (millis() - lastDataTime > LASER_TIMEOUT_MS && laserEnabled) {
    Serial.println("TIMEOUT: No data for 5 minutes. Laser disabled.");
    stopProjection();
  }

  // ── IMU polling (100Hz) ──
  if (imuReady && millis() - lastIMUPoll >= IMU_POLL_MS) {
    lastIMUPoll = millis();
    readIMU();
  }

  // If projecting, run the scan loop
  if (projecting && patternLoaded && safetyOK) {
    runScanLoop();
  } else if (projecting && !safetyOK) {
    // Safety tripped during projection
    emergencyStop();
  }

  // Update LED animation
  updateStatusLED();
}

// ============================================================================
// IMU — MPU6050 Bump Detection & Tilt Compensation
// ============================================================================

void setupIMU() {
  // I2C bus shared with camera SCCB (GPIO1=SDA, GPIO2=SCL)
  Wire.begin(PIN_CAM_SDA, PIN_CAM_SCL);
  Wire.setClock(400000); // 400kHz I2C

  // Check if MPU6050 is present
  Wire.beginTransmission(IMU_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println("[IMU] MPU6050 not found at 0x68");
    imuReady = false;
    return;
  }

  // Wake up MPU6050 (clear sleep bit)
  writeIMUReg(IMU_REG_PWR_MGMT_1, 0x00);
  delay(10);

  // Set accelerometer range to ±4g (register 0x1C, bits 4:3 = 01)
  writeIMUReg(IMU_REG_ACCEL_CFG, 0x08);

  // Set gyroscope range to ±500°/s (register 0x1B, bits 4:3 = 01)
  writeIMUReg(IMU_REG_GYRO_CFG, 0x08);

  delay(50); // Let sensor stabilize

  // Read baseline tilt
  float ax, ay, az;
  readAccel(ax, ay, az);
  baselinePitch = atan2f(ax, az);
  baselineRoll = atan2f(ay, az);

  imuReady = true;
  Serial.printf("[IMU] MPU6050 initialized. Baseline pitch=%.2f° roll=%.2f°\n",
                baselinePitch * 180.0f / M_PI, baselineRoll * 180.0f / M_PI);
}

void writeIMUReg(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

void readAccel(float &ax, float &ay, float &az) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(IMU_REG_ACCEL_XOUT);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)IMU_ADDR, (uint8_t)6);

  int16_t rawAx = (Wire.read() << 8) | Wire.read();
  int16_t rawAy = (Wire.read() << 8) | Wire.read();
  int16_t rawAz = (Wire.read() << 8) | Wire.read();

  // Convert to g (±4g range → sensitivity = 8192 LSB/g)
  ax = (float)rawAx / 8192.0f;
  ay = (float)rawAy / 8192.0f;
  az = (float)rawAz / 8192.0f;
}

void readIMU() {
  float ax, ay, az;
  readAccel(ax, ay, az);

  // Compute acceleration magnitude
  float magnitude = sqrtf(ax * ax + ay * ay + az * az);

  // ── Bump Detection ──
  // A bump causes magnitude to deviate significantly from 1g
  if (fabsf(magnitude - 1.0f) > BUMP_THRESHOLD_G &&
      millis() - lastBumpTime > BUMP_COOLDOWN_MS) {
    bumpDetected = true;
    lastBumpTime = millis();

    Serial.printf("[IMU] BUMP detected! magnitude=%.2fg\n", magnitude);

    // Notify app via WebSocket
    if (clientConnected) {
      String msg = "{\"type\":\"bump_detected\",\"magnitude\":" + String(magnitude, 2) + "}";
      wsServer.sendTXT(connectedClient, msg);
    }

    // Visual feedback
    setStatusColor(COLOR_BUMP);

    // After bump, update tilt baseline (unit may have shifted)
    delay(100); // Brief settle
    readAccel(ax, ay, az);
    baselinePitch = atan2f(ax, az);
    baselineRoll = atan2f(ay, az);
    tiltCorrectionX = 0.0f;
    tiltCorrectionY = 0.0f;

    // Rebuild scan buffer with new baseline
    if (patternLoaded) {
      buildScanBuffer();
    }

    bumpDetected = false;
    if (projecting) setStatusColor(COLOR_PROJECTING);

    return;
  }

  // ── Tilt Compensation ──
  // Compute current pitch and roll
  currentPitch = atan2f(ax, az);
  currentRoll = atan2f(ay, az);

  // Delta from baseline
  float deltaPitch = currentPitch - baselinePitch;
  float deltaRoll = currentRoll - baselineRoll;

  // Clamp to max correction range
  float maxRad = TILT_CORRECT_MAX * M_PI / 180.0f;
  if (deltaPitch > maxRad) deltaPitch = maxRad;
  if (deltaPitch < -maxRad) deltaPitch = -maxRad;
  if (deltaRoll > maxRad) deltaRoll = maxRad;
  if (deltaRoll < -maxRad) deltaRoll = -maxRad;

  // Convert tilt angle to DAC offset
  // At projection distance d, a tilt of angle θ shifts the projection by d*tan(θ)
  float distInches = projectionDistanceFt * 12.0f;
  tiltCorrectionX = tanf(deltaRoll) * distInches * inchesToDac;
  tiltCorrectionY = tanf(deltaPitch) * distInches * inchesToDac;

  // ── Periodic IMU telemetry (every 2 seconds) ──
  if (clientConnected && millis() - lastIMUReport > 2000) {
    lastIMUReport = millis();
    String msg = "{\"type\":\"imu_status\",\"pitch\":" + String(deltaPitch * 180.0f / M_PI, 1)
               + ",\"roll\":" + String(deltaRoll * 180.0f / M_PI, 1)
               + ",\"tilt_corrected\":" + String((fabsf(tiltCorrectionX) > 1 || fabsf(tiltCorrectionY) > 1) ? "true" : "false")
               + "}";
    wsServer.sendTXT(connectedClient, msg);
  }
}

// ============================================================================
// CAMERA — OV5640 Setup & Auto-Distance Detection
// ============================================================================

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = PIN_CAM_D2;   // DVP D2 maps to driver D0
  config.pin_d1 = PIN_CAM_D3;
  config.pin_d2 = PIN_CAM_D4;
  config.pin_d3 = PIN_CAM_D5;
  config.pin_d4 = PIN_CAM_D6;
  config.pin_d5 = PIN_CAM_D7;
  config.pin_d6 = PIN_CAM_D8;
  config.pin_d7 = PIN_CAM_D9;
  config.pin_xclk = PIN_CAM_XCLK;
  config.pin_pclk = PIN_CAM_PCLK;
  config.pin_vsync = PIN_CAM_VSYNC;
  config.pin_href = PIN_CAM_HREF;
  config.pin_sccb_sda = PIN_CAM_SDA;
  config.pin_sccb_scl = PIN_CAM_SCL;
  config.pin_pwdn = -1;     // Not connected (R14 pulls PWDN low)
  config.pin_reset = -1;    // Not connected (R13 pulls RESET high)
  config.xclk_freq_hz = 20000000;  // 20MHz XCLK
  config.pixel_format = PIXFORMAT_GRAYSCALE;  // Grayscale for processing
  config.frame_size = FRAMESIZE_VGA;  // 640x480
  config.jpeg_quality = 12;
  config.fb_count = 2;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.grab_mode = CAMERA_GRAB_LATEST;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CAM] Camera init failed: 0x%x\n", err);
    cameraReady = false;
    return;
  }

  cameraReady = true;
  Serial.println("[CAM] OV5640 initialized (VGA grayscale)");
}

// Bounding box result for bright region detection
struct BrightRegion {
  uint16_t minX, minY, maxX, maxY;
  uint32_t pixelCount;
  bool valid;
};

// Find the bounding box of bright pixels (laser reflection) in a grayscale frame
BrightRegion findBrightRegion(uint8_t *buf, uint16_t width, uint16_t height) {
  BrightRegion region = {width, height, 0, 0, 0, false};

  for (uint16_t y = 0; y < height; y++) {
    for (uint16_t x = 0; x < width; x++) {
      uint8_t pixel = buf[y * width + x];
      if (pixel >= LASER_BRIGHT_THRESH) {
        if (x < region.minX) region.minX = x;
        if (x > region.maxX) region.maxX = x;
        if (y < region.minY) region.minY = y;
        if (y > region.maxY) region.maxY = y;
        region.pixelCount++;
      }
    }
  }

  region.valid = (region.pixelCount >= MIN_BRIGHT_PIXELS &&
                  region.maxX > region.minX &&
                  region.maxY > region.minY);
  return region;
}

// Auto-detect projection distance using camera
// Projects a known 12" calibration square, captures it, measures pixel size
void measureProjectionDistance() {
  if (!cameraReady) {
    Serial.println("[CAM] Camera not available for auto-distance");
    if (clientConnected) {
      wsServer.sendTXT(connectedClient, "{\"type\":\"error\",\"msg\":\"Camera not available\"}");
    }
    return;
  }

  Serial.println("[CAM] Starting auto-distance measurement...");
  setStatusColor(COLOR_CALIBRATING);

  // Step 1: Project a 12" calibration square
  float calSizeInches = 12.0f;
  buildCalibrationPattern(calSizeInches);
  projecting = true;
  laserEnabled = true;

  // Step 2: Run the scan loop a few times to let the projection stabilize
  for (int frame = 0; frame < 10; frame++) {
    if (safetyOK) runScanLoop();
  }
  delay(CAL_SETTLE_MS);

  // Step 3: Capture a camera frame while laser is projecting
  // Run one more scan frame, then quickly grab camera
  if (safetyOK) runScanLoop();

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[CAM] Frame capture failed");
    stopProjection();
    if (clientConnected) {
      wsServer.sendTXT(connectedClient, "{\"type\":\"error\",\"msg\":\"Camera capture failed\"}");
    }
    return;
  }

  // Step 4: Find bright region (laser reflection)
  BrightRegion region = findBrightRegion(fb->buf, fb->width, fb->height);
  esp_camera_fb_return(fb);

  // Stop calibration projection
  stopProjection();

  if (!region.valid) {
    Serial.printf("[CAM] Insufficient bright pixels: %u (need %d)\n",
                  region.pixelCount, MIN_BRIGHT_PIXELS);
    if (clientConnected) {
      wsServer.sendTXT(connectedClient,
        "{\"type\":\"auto_distance\",\"success\":false,\"msg\":\"Could not detect laser pattern\"}");
    }
    return;
  }

  // Step 5: Calculate distance from known geometry
  // The calibration square is calSizeInches wide.
  // Camera FOV is CAM_FOV_DEGREES across CAM_WIDTH_PX pixels.
  float pixelWidth = (float)(region.maxX - region.minX);
  float pixelHeight = (float)(region.maxY - region.minY);
  float avgPixelSize = (pixelWidth + pixelHeight) / 2.0f;

  // Pixels per degree
  float pixPerDeg = (float)CAM_WIDTH_PX / CAM_FOV_DEGREES;

  // Apparent angular size of the calibration square in degrees
  float apparentAngleDeg = avgPixelSize / pixPerDeg;
  float apparentAngleRad = apparentAngleDeg * M_PI / 180.0f;

  // Distance = (known_half_size) / tan(apparent_half_angle)
  float halfSizeInches = calSizeInches / 2.0f;
  float halfAngleRad = apparentAngleRad / 2.0f;

  if (halfAngleRad <= 0.001f) {
    Serial.println("[CAM] Angle too small for reliable measurement");
    if (clientConnected) {
      wsServer.sendTXT(connectedClient,
        "{\"type\":\"auto_distance\",\"success\":false,\"msg\":\"Pattern too small to measure\"}");
    }
    return;
  }

  float distInches = halfSizeInches / tanf(halfAngleRad);
  float distFeet = distInches / 12.0f;

  // Sanity check: clamp to reasonable range (2-20 feet)
  if (distFeet < 2.0f || distFeet > 20.0f) {
    Serial.printf("[CAM] Distance %.1f ft out of range (2-20ft)\n", distFeet);
    if (clientConnected) {
      String msg = "{\"type\":\"auto_distance\",\"success\":false,\"msg\":\"Distance "
                 + String(distFeet, 1) + "ft out of range\"}";
      wsServer.sendTXT(connectedClient, msg);
    }
    return;
  }

  // Step 6: Apply the computed distance
  projectionDistanceFt = distFeet;
  computeProjectionMapping();
  if (patternLoaded) {
    buildScanBuffer();
  }

  // Confidence based on pixel count (more pixels = more reliable)
  float confidence = (float)region.pixelCount / 1000.0f;
  if (confidence > 1.0f) confidence = 1.0f;

  Serial.printf("[CAM] Auto-distance: %.1f ft (%.0f\" coverage), confidence=%.0f%%, %u bright pixels\n",
                distFeet, coverageInches, confidence * 100.0f, region.pixelCount);

  // Step 7: Notify app
  if (clientConnected) {
    String msg = "{\"type\":\"auto_distance\",\"success\":true,\"distance_ft\":"
               + String(distFeet, 2)
               + ",\"coverage_in\":" + String(coverageInches, 1)
               + ",\"confidence\":" + String(confidence, 2)
               + ",\"bright_pixels\":" + String(region.pixelCount)
               + "}";
    wsServer.sendTXT(connectedClient, msg);
  }

  if (clientConnected) setStatusColor(COLOR_CONNECTED);
}

// ============================================================================
// WiFi SETUP
// ============================================================================

void setupWiFi() {
  if (USE_STATION_MODE) {
    // Connect to existing network
    Serial.printf("Connecting to WiFi: %s\n", WIFI_STA_SSID);
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin(WIFI_STA_SSID, WIFI_STA_PASS);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("\nConnected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
      Serial.println("\nFailed to connect. Falling back to AP mode.");
    }
  }

  // Always create AP (even in station mode, for direct connection)
  WiFi.softAP(WIFI_AP_SSID, WIFI_AP_PASSWORD, WIFI_AP_CHANNEL, 0, WIFI_AP_MAX_CONN);
  Serial.printf("AP started: %s @ %s\n", WIFI_AP_SSID, WiFi.softAPIP().toString().c_str());
}

// ============================================================================
// HTTP SERVER (Status Page)
// ============================================================================

void setupHTTPServer() {
  httpServer.on("/", HTTP_GET, []() {
    String html = "<!DOCTYPE html><html><head><title>LayIt Laser</title>";
    html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
    html += "<style>body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px;max-width:600px;margin:0 auto;}";
    html += "h1{color:#4ade80;}.s{color:#8b949e;}.v{color:#f0a000;font-size:1.2em;}</style></head>";
    html += "<body><h1>&#x2B22; LayIt Laser</h1>";
    html += "<p class='s'>Status Page — v1.2</p><hr>";
    html += "<p>Safety Interlock: <span class='v'>" + String(safetyOK ? "OK (Closed)" : "OPEN - Laser Disabled") + "</span></p>";
    html += "<p>Client Connected: <span class='v'>" + String(clientConnected ? "Yes" : "No") + "</span></p>";
    html += "<p>Pattern Loaded: <span class='v'>" + String(patternLoaded ? "Yes" : "No") + "</span></p>";
    html += "<p>Projecting: <span class='v'>" + String(projecting ? "Yes" : "No") + "</span></p>";
    html += "<p>Tiles: <span class='v'>" + String(tileCount) + "</span></p>";
    html += "<p>Scan Points: <span class='v'>" + String(scanPointCount) + "</span></p>";
    html += "<p>Distance: <span class='v'>" + String(projectionDistanceFt, 1) + " ft</span></p>";
    html += "<p>Coverage: <span class='v'>" + String(coverageInches, 0) + " inches</span></p>";
    html += "<p>IMU: <span class='v'>" + String(imuReady ? "OK" : "N/A") + "</span></p>";
    html += "<p>Camera: <span class='v'>" + String(cameraReady ? "OK" : "N/A") + "</span></p>";
    html += "<p>Grout Mode: <span class='v'>" + String(groutModeStr(currentGroutMode))
         + (groutModeAuto ? " (auto)" : " (manual)") + "</span></p>";
    html += "<hr><p class='s'>WebSocket: ws://" + WiFi.softAPIP().toString() + ":81</p>";
    html += "</body></html>";
    httpServer.send(200, "text/html", html);
  });

  httpServer.on("/status", HTTP_GET, []() {
    String json = "{";
    json += "\"safety\":" + String(safetyOK ? "true" : "false") + ",";
    json += "\"connected\":" + String(clientConnected ? "true" : "false") + ",";
    json += "\"projecting\":" + String(projecting ? "true" : "false") + ",";
    json += "\"tiles\":" + String(tileCount) + ",";
    json += "\"distance\":" + String(projectionDistanceFt, 2) + ",";
    json += "\"imu\":" + String(imuReady ? "true" : "false") + ",";
    json += "\"camera\":" + String(cameraReady ? "true" : "false") + ",";
    json += "\"grout_mode\":\"" + String(groutModeStr(currentGroutMode)) + "\",";
    json += "\"grout_auto\":" + String(groutModeAuto ? "true" : "false");
    json += "}";
    httpServer.send(200, "application/json", json);
  });
}

// ============================================================================
// WEBSOCKET HANDLER
// ============================================================================

void onWebSocketEvent(uint8_t clientNum, WStype_t type, uint8_t *payload, size_t length) {
  switch (type) {

    case WStype_CONNECTED: {
      IPAddress ip = wsServer.remoteIP(clientNum);
      Serial.printf("[WS] Client #%u connected from %s\n", clientNum, ip.toString().c_str());
      clientConnected = true;
      connectedClient = clientNum;
      setStatusColor(COLOR_CONNECTED);
      lastDataTime = millis();

      // Send device info to app (now includes IMU and camera status)
      String info = "{\"type\":\"device_info\",\"name\":\"LayIt Laser\",\"version\":\"1.2\",\"safety\":"
                    + String(safetyOK ? "true" : "false")
                    + ",\"imu\":" + String(imuReady ? "true" : "false")
                    + ",\"camera\":" + String(cameraReady ? "true" : "false")
                    + ",\"grout_mode\":\"" + String(groutModeStr(currentGroutMode))
                    + "\",\"grout_auto\":" + String(groutModeAuto ? "true" : "false")
                    + "}";
      wsServer.sendTXT(clientNum, info);
      break;
    }

    case WStype_DISCONNECTED: {
      Serial.printf("[WS] Client #%u disconnected\n", clientNum);
      clientConnected = false;
      stopProjection();
      setStatusColor(COLOR_READY);
      break;
    }

    case WStype_TEXT: {
      lastDataTime = millis();
      handleMessage(clientNum, (char*)payload, length);
      break;
    }

    case WStype_BIN: {
      // Binary data not used currently
      Serial.printf("[WS] Received %u bytes binary (ignored)\n", length);
      break;
    }

    case WStype_PING:
    case WStype_PONG:
      break;
  }
}

// ============================================================================
// MESSAGE HANDLER — Parses commands from the LayIt app
// ============================================================================

void handleMessage(uint8_t clientNum, char *payload, size_t length) {
  // Parse JSON
  // Using ArduinoJson v7 — allocate on PSRAM if available
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.printf("[MSG] JSON parse error: %s\n", error.c_str());
    wsServer.sendTXT(clientNum, "{\"type\":\"error\",\"msg\":\"Invalid JSON\"}");
    return;
  }

  const char *type = doc["type"];
  if (!type) {
    wsServer.sendTXT(clientNum, "{\"type\":\"error\",\"msg\":\"Missing type field\"}");
    return;
  }

  // ── LOAD PATTERN ──
  // Receives the full .layit format from the app
  if (strcmp(type, "load_pattern") == 0) {
    Serial.println("[MSG] Loading pattern...");

    stopProjection(); // Stop current projection if any

    // Parse wall dimensions
    pattern.wallWidth  = doc["wall"]["width"] | 48.0f;
    pattern.wallHeight = doc["wall"]["height"] | 48.0f;

    // Parse tile info
    pattern.tileWidth  = doc["tile"]["width"] | 12.0f;
    pattern.tileHeight = doc["tile"]["height"] | 12.0f;
    pattern.groutSize  = doc["tile"]["grout"] | 0.125f;
    strlcpy(pattern.tileShape, doc["tile"]["shape"] | "square", sizeof(pattern.tileShape));

    // Parse voids
    voidCount = 0;
    JsonArray voidsArr = doc["voids"].as<JsonArray>();
    if (voidsArr) {
      for (JsonObject v : voidsArr) {
        if (voidCount >= MAX_VOIDS) break;
        voids[voidCount].x = v["x"] | 0.0f;
        voids[voidCount].y = v["y"] | 0.0f;
        voids[voidCount].w = v["w"] | 0.0f;
        voids[voidCount].h = v["h"] | 0.0f;
        voidCount++;
      }
    }

    // Parse tiles (array of objects with verts arrays + isCut flag)
    tileCount = 0;
    JsonArray tilesArr = doc["tiles"].as<JsonArray>();
    if (tilesArr) {
      for (JsonObject t : tilesArr) {
        if (tileCount >= MAX_TILES) break;

        JsonArray vertsArr = t["verts"].as<JsonArray>();
        tiles[tileCount].vertCount = 0;
        tiles[tileCount].isCut = t["isCut"] | false;

        if (vertsArr) {
          for (JsonArray vert : vertsArr) {
            uint8_t vi = tiles[tileCount].vertCount;
            if (vi >= MAX_VERTS_PER_TILE) break;

            tiles[tileCount].verts[vi][0] = vert[0] | 0.0f;  // x in inches
            tiles[tileCount].verts[vi][1] = vert[1] | 0.0f;  // y in inches
            tiles[tileCount].vertCount++;
          }
        }
        tileCount++;
      }
    }

    // Count cut tiles
    uint16_t cutCount = 0;
    for (uint16_t i = 0; i < tileCount; i++) {
      if (tiles[i].isCut) cutCount++;
    }

    Serial.printf("[MSG] Loaded: %d tiles (%d cut), %d voids, wall %.0fx%.0f\"\n",
                  tileCount, cutCount, voidCount, pattern.wallWidth, pattern.wallHeight);

    // Compute projection mapping
    computeProjectionMapping();

    // Build scan buffer (with path optimization)
    buildScanBuffer();

    patternLoaded = true;

    // Acknowledge to app
    String ack = "{\"type\":\"pattern_loaded\",\"tiles\":" + String(tileCount)
                 + ",\"cut_tiles\":" + String(cutCount)
                 + ",\"points\":" + String(scanPointCount)
                 + ",\"grout_mode\":\"" + String(groutModeStr(currentGroutMode))
                 + "\",\"grout_auto\":" + String(groutModeAuto ? "true" : "false") + "}";
    wsServer.sendTXT(clientNum, ack);

    // Send guardrail advisories if distance or segment is pushing limits
    sendProjectionAdvisory(clientNum);

    setStatusColor(COLOR_CONNECTED);
  }

  // ── SET SEGMENT ──
  // App tells us which 36"x36" segment to project
  else if (strcmp(type, "set_segment") == 0) {
    segmentX = doc["x"] | 0.0f;
    segmentY = doc["y"] | 0.0f;
    segmentW = doc["width"] | 36.0f;
    segmentH = doc["height"] | 36.0f;

    Serial.printf("[MSG] Segment: origin(%.1f, %.1f) size(%.1fx%.1f)\n",
                  segmentX, segmentY, segmentW, segmentH);

    // Rebuild scan buffer for this segment
    if (patternLoaded) {
      buildScanBuffer();
      wsServer.sendTXT(clientNum, "{\"type\":\"segment_set\",\"points\":" + String(scanPointCount) + "}");
      sendProjectionAdvisory(clientNum);
    }
  }

  // ── SET DISTANCE ──
  // App sets projection distance (from camera or manual input)
  else if (strcmp(type, "set_distance") == 0) {
    projectionDistanceFt = doc["distance"] | 6.0f;
    Serial.printf("[MSG] Distance set: %.1f ft\n", projectionDistanceFt);

    computeProjectionMapping();
    if (patternLoaded) {
      buildScanBuffer();
    }

    wsServer.sendTXT(clientNum, "{\"type\":\"distance_set\",\"coverage\":" + String(coverageInches, 1) + "}");
    sendProjectionAdvisory(clientNum);
  }

  // ── AUTO DISTANCE ──
  // Trigger camera-based auto-distance measurement
  else if (strcmp(type, "auto_distance") == 0) {
    Serial.println("[MSG] Auto-distance requested");
    measureProjectionDistance();
  }

  // ── START PROJECTION ──
  else if (strcmp(type, "start") == 0) {
    if (!patternLoaded) {
      wsServer.sendTXT(clientNum, "{\"type\":\"error\",\"msg\":\"No pattern loaded\"}");
      return;
    }
    if (!safetyOK) {
      wsServer.sendTXT(clientNum, "{\"type\":\"error\",\"msg\":\"Safety interlock open\"}");
      return;
    }

    Serial.println("[MSG] Starting projection");
    projecting = true;
    laserEnabled = true;
    setStatusColor(COLOR_PROJECTING);
    wsServer.sendTXT(clientNum, "{\"type\":\"projecting\",\"active\":true}");
  }

  // ── STOP PROJECTION ──
  else if (strcmp(type, "stop") == 0) {
    Serial.println("[MSG] Stopping projection");
    stopProjection();
    wsServer.sendTXT(clientNum, "{\"type\":\"projecting\",\"active\":false}");
    if (clientConnected) setStatusColor(COLOR_CONNECTED);
  }

  // ── CALIBRATE ──
  // Project a known-size square for the user to measure
  else if (strcmp(type, "calibrate") == 0) {
    float calSize = doc["size"] | 12.0f; // Default 12" calibration square
    Serial.printf("[MSG] Calibration: %.0f\" square\n", calSize);
    setStatusColor(COLOR_CALIBRATING);
    buildCalibrationPattern(calSize);
    projecting = true;
    laserEnabled = true;
  }

  // ── RECALIBRATE IMU ──
  // Reset IMU baseline from current position
  else if (strcmp(type, "recalibrate_imu") == 0) {
    if (imuReady) {
      float ax, ay, az;
      readAccel(ax, ay, az);
      baselinePitch = atan2f(ax, az);
      baselineRoll = atan2f(ay, az);
      tiltCorrectionX = 0.0f;
      tiltCorrectionY = 0.0f;
      Serial.printf("[IMU] Baseline recalibrated: pitch=%.2f° roll=%.2f°\n",
                    baselinePitch * 180.0f / M_PI, baselineRoll * 180.0f / M_PI);
      wsServer.sendTXT(clientNum, "{\"type\":\"imu_recalibrated\"}");
    } else {
      wsServer.sendTXT(clientNum, "{\"type\":\"error\",\"msg\":\"IMU not available\"}");
    }
  }

  // ── SET GROUT MODE ──
  // 0=auto, 1=DUAL, 2=SINGLE, 3=MINIMAL
  else if (strcmp(type, "set_grout_mode") == 0) {
    int mode = doc["mode"] | -1;
    if (mode == 0) {
      groutModeAuto = true;
      Serial.println("[GROUT] Mode: AUTO");
    } else if (mode >= 1 && mode <= 3) {
      groutModeAuto = false;
      currentGroutMode = (GroutMode)(mode - 1);
      Serial.printf("[GROUT] Mode: %s (manual override)\n", groutModeStr(currentGroutMode));
    } else {
      wsServer.sendTXT(clientNum, "{\"type\":\"error\",\"msg\":\"Invalid grout mode (0-3)\"}");
      return;
    }

    // Rebuild scan buffer with new grout mode
    if (patternLoaded) {
      buildScanBuffer();
    }

    String ack = "{\"type\":\"grout_mode_set\",\"mode\":" + String((int)currentGroutMode)
                 + ",\"mode_name\":\"" + String(groutModeStr(currentGroutMode))
                 + "\",\"auto\":" + String(groutModeAuto ? "true" : "false")
                 + ",\"points\":" + String(scanPointCount) + "}";
    wsServer.sendTXT(clientNum, ack);
  }

  // ── PING ──
  else if (strcmp(type, "ping") == 0) {
    wsServer.sendTXT(clientNum, "{\"type\":\"pong\"}");
  }

  else {
    Serial.printf("[MSG] Unknown type: %s\n", type);
  }
}

// ============================================================================
// PROJECTION MAPPING — Converts inches to DAC values
// ============================================================================

void computeProjectionMapping() {
  // At distance d (feet), coverage = d * 12 * 0.73 (inches)
  // Based on ±20° galvo scan angle: 2 * tan(20°) ≈ 0.73
  coverageInches = projectionDistanceFt * 12.0f * 0.728f;

  // DAC values per inch of projection
  // Full DAC range (0-4095) maps to full coverage
  inchesToDac = (float)DAC_RESOLUTION / coverageInches;

  Serial.printf("[MAP] Distance: %.1f ft, Coverage: %.1f\", Scale: %.1f DAC/inch\n",
                projectionDistanceFt, coverageInches, inchesToDac);
}

// Convert wall coordinates (inches) to DAC values
// Returns false if the point is outside the projection area
bool inchesToDAC(float xInch, float yInch, uint16_t &dacX, uint16_t &dacY) {
  // Translate relative to current segment origin
  float relX = xInch - segmentX - originX;
  float relY = yInch - segmentY - originY;

  // Convert to DAC values (centered at DAC_CENTER)
  float dx = relX * inchesToDac;
  float dy = relY * inchesToDac;

  // Map to DAC range: center ± half range
  int32_t rawX = DAC_CENTER + (int32_t)dx;
  int32_t rawY = DAC_CENTER + (int32_t)dy;

  // Apply tilt correction from IMU
  if (imuReady) {
    rawX += (int32_t)tiltCorrectionX;
    rawY += (int32_t)tiltCorrectionY;
  }

  // Clamp to valid range
  if (rawX < 0 || rawX >= DAC_RESOLUTION || rawY < 0 || rawY >= DAC_RESOLUTION) {
    return false; // Outside projection area
  }

  dacX = (uint16_t)rawX;
  dacY = (uint16_t)rawY;
  return true;
}

// ============================================================================
// PROJECTION GUARDRAILS — Distance & segment size advisories
// ============================================================================

// Recommended limits for best results
#define RECOMMENDED_MAX_DISTANCE_FT  8.0f   // Beyond this, beam gets fat and lines merge
#define RECOMMENDED_MAX_SEGMENT_IN   48.0f  // 4ft × 4ft is a comfortable working area
#define DISTANCE_WARNING_FT          10.0f  // Hard warning: quality degrades significantly

// Send advisory messages to the app when projection settings are pushing limits.
// These are informational — the laser still works, but the app can show guidance
// to help first-time users get the best experience.
void sendProjectionAdvisory(uint8_t clientNum) {
  if (!clientConnected) return;

  // ── Distance advisory ──
  if (projectionDistanceFt > DISTANCE_WARNING_FT) {
    // Hard warning: you're really far away
    String msg = "{\"type\":\"advisory\",\"level\":\"warning\""
                 ",\"category\":\"distance\""
                 ",\"message\":\"Laser is " + String(projectionDistanceFt, 1)
                 + "ft from the surface. At this distance the beam is too wide for crisp grout lines. "
                 "Move the laser closer (6-8ft recommended) for the best projection quality.\""
                 ",\"distance_ft\":" + String(projectionDistanceFt, 1)
                 + ",\"recommended_max\":" + String(RECOMMENDED_MAX_DISTANCE_FT, 1)
                 + "}";
    wsServer.sendTXT(clientNum, msg);
  } else if (projectionDistanceFt > RECOMMENDED_MAX_DISTANCE_FT) {
    // Soft suggestion: getting far, still works but not ideal
    String msg = "{\"type\":\"advisory\",\"level\":\"suggestion\""
                 ",\"category\":\"distance\""
                 ",\"message\":\"At " + String(projectionDistanceFt, 1)
                 + "ft the laser works but grout lines may appear merged. "
                 "For sharper detail, try 6-8ft.\""
                 ",\"distance_ft\":" + String(projectionDistanceFt, 1)
                 + ",\"recommended_max\":" + String(RECOMMENDED_MAX_DISTANCE_FT, 1)
                 + "}";
    wsServer.sendTXT(clientNum, msg);
  }

  // ── Segment size advisory ──
  float segMaxDim = (segmentW > segmentH) ? segmentW : segmentH;
  if (segMaxDim > RECOMMENDED_MAX_SEGMENT_IN) {
    // Count how many tiles are in this segment
    uint16_t tilesInSeg = segmentTileCount;
    // Check if budget enforcement had to demote tiles
    uint16_t demotedCount = 0;
    for (uint16_t i = 0; i < segmentTileCount; i++) {
      if (tilePriorities[tileOrder[i]] == PRIORITY_LOW) demotedCount++;
    }

    String msg = "{\"type\":\"advisory\",\"level\":\"" + String(demotedCount > 0 ? "warning" : "suggestion")
                 + "\",\"category\":\"segment_size\""
                 ",\"message\":\"" + String(demotedCount > 0
                   ? "Large segment (" + String(segmentW, 0) + "x" + String(segmentH, 0)
                     + "\\\" with " + String(tilesInSeg) + " tiles). "
                     + String(demotedCount) + " interior tiles simplified to corners to maintain brightness. "
                     "Try a smaller segment (36x36\\\" recommended) for full tile outlines everywhere."
                   : "Segment is " + String(segmentW, 0) + "x" + String(segmentH, 0)
                     + "\\\". For the crispest lines, try 36x36\\\" segments.")
                 + "\",\"segment_w\":" + String(segmentW, 0)
                 + ",\"segment_h\":" + String(segmentH, 0)
                 + ",\"tiles_in_segment\":" + String(tilesInSeg)
                 + ",\"tiles_simplified\":" + String(demotedCount)
                 + "}";
    wsServer.sendTXT(clientNum, msg);
  }
}

// ============================================================================
// ADAPTIVE GROUT RENDERING — Mode selection + edge deduplication
// ============================================================================

// Return a string name for the current grout mode (for logging)
const char* groutModeStr(GroutMode mode) {
  switch (mode) {
    case GROUT_DUAL:    return "DUAL";
    case GROUT_SINGLE:  return "SINGLE";
    case GROUT_MINIMAL: return "MINIMAL";
    default:            return "UNKNOWN";
  }
}

// Compute optimal grout rendering mode based on beam-spot-to-grout-width ratio
// Called from buildScanBuffer() when groutModeAuto is true
//
// NOTE: Auto-selection only chooses between DUAL and SINGLE.
// GROUT_MINIMAL is never auto-selected — it only activates via:
//   1. Manual override (set_grout_mode WebSocket command)
//   2. Point budget pressure (enforcePointBudget demotes tiles to corners-only)
// This prevents confusing first-time users with a field of dots.
void computeGroutMode() {
  // Beam spot size at current distance (mm)
  // beamSpot = distance_meters × divergence_mrad
  float distMeters = projectionDistanceFt * 0.3048f;
  float beamSpotMM = distMeters * BEAM_DIVERGENCE_MRAD;

  // Grout size in mm
  float groutMM = pattern.groutSize * 25.4f;

  // Avoid division by zero for zero grout
  if (groutMM < 0.1f) {
    currentGroutMode = GROUT_DUAL;
    Serial.println("[GROUT] Zero grout → DUAL mode");
    return;
  }

  float ratio = beamSpotMM / groutMM;

  // Auto only picks DUAL or SINGLE — never MINIMAL
  // DUAL: beam is thin enough to show two distinct grout channel edges
  // SINGLE: beam ≈ grout width, deduplicate shared edges (looks identical, half the work)
  if (ratio < GROUT_DUAL_RATIO) {
    currentGroutMode = GROUT_DUAL;
  } else {
    currentGroutMode = GROUT_SINGLE;
  }

  Serial.printf("[GROUT] mode=%s (auto), beamSpot=%.2fmm, grout=%.2fmm, ratio=%.2f\n",
                groutModeStr(currentGroutMode), beamSpotMM, groutMM, ratio);
}

// Create a canonical (order-independent) edge key from two vertex positions
// Vertices are quantized to hundredths of an inch for reliable matching
EdgeKey makeEdgeKey(float ax, float ay, float bx, float by) {
  EdgeKey ek;
  int32_t qax = (int32_t)(ax * EDGE_QUANT_PRECISION);
  int32_t qay = (int32_t)(ay * EDGE_QUANT_PRECISION);
  int32_t qbx = (int32_t)(bx * EDGE_QUANT_PRECISION);
  int32_t qby = (int32_t)(by * EDGE_QUANT_PRECISION);

  // Sort endpoints so the key is order-independent
  // (edge A→B is the same as edge B→A)
  if (qax < qbx || (qax == qbx && qay < qby)) {
    ek.x1 = qax; ek.y1 = qay;
    ek.x2 = qbx; ek.y2 = qby;
  } else {
    ek.x1 = qbx; ek.y1 = qby;
    ek.x2 = qax; ek.y2 = qay;
  }
  return ek;
}

// Check if an edge has already been drawn (linear scan)
bool isEdgeDrawn(EdgeKey &ek) {
  for (uint16_t i = 0; i < drawnEdgeCount; i++) {
    if (drawnEdges[i].x1 == ek.x1 && drawnEdges[i].y1 == ek.y1 &&
        drawnEdges[i].x2 == ek.x2 && drawnEdges[i].y2 == ek.y2) {
      return true;
    }
  }
  return false;
}

// Record an edge as drawn for deduplication
void markEdgeDrawn(EdgeKey &ek) {
  if (drawnEdgeCount < MAX_DRAWN_EDGES) {
    drawnEdges[drawnEdgeCount] = ek;
    drawnEdgeCount++;
  }
}

// Check if a tile is on the boundary of the current segment
// Boundary tiles are within 1 tile-width of the segment edge
bool isBoundaryTile(uint16_t tileIdx) {
  float margin = pattern.tileWidth; // 1 tile-width from edge = boundary

  for (uint8_t v = 0; v < tiles[tileIdx].vertCount; v++) {
    float x = tiles[tileIdx].verts[v][0];
    float y = tiles[tileIdx].verts[v][1];

    // Check if vertex is near any segment edge
    if (x < segmentX + margin || x > segmentX + segmentW - margin ||
        y < segmentY + margin || y > segmentY + segmentH - margin) {
      return true;
    }
  }
  return false;
}

// Render only the corners of a tile as bright dots (no connecting lines)
// Used for GROUT_MINIMAL mode on interior full tiles, and for LOW priority tiles
void addCornersOnly(uint16_t tileIdx) {
  TileData &tile = tiles[tileIdx];

  for (uint8_t v = 0; v < tile.vertCount; v++) {
    uint16_t dacX, dacY;
    if (!inchesToDAC(tile.verts[v][0], tile.verts[v][1], dacX, dacY)) continue;

    // Blanking move to corner
    addScanPoint(dacX, dacY, false);

    // Dwell at corner with laser on — creates a bright dot
    for (uint8_t d = 0; d < CORNER_DOT_DWELL; d++) {
      addScanPoint(dacX, dacY, true);
    }

    // Blank after dot
    addScanPoint(dacX, dacY, false);
  }
}

// ============================================================================
// PRIORITY-BASED LINE RENDERING — Budget enforcement
// ============================================================================

// Assign priority to each tile in the current segment
void assignTilePriorities() {
  for (uint16_t i = 0; i < segmentTileCount; i++) {
    uint16_t idx = tileOrder[i];

    if (tiles[idx].isCut) {
      tilePriorities[idx] = PRIORITY_CRITICAL;
    } else if (isBoundaryTile(idx)) {
      tilePriorities[idx] = PRIORITY_HIGH;
    } else {
      tilePriorities[idx] = PRIORITY_MEDIUM;
    }
  }
}

// Estimate how many scan points a tile will consume
uint16_t estimateTilePoints(uint16_t tileIdx, bool cornersOnly) {
  if (cornersOnly) {
    // corners: blank + dwell + blank per vertex
    return tiles[tileIdx].vertCount * (CORNER_DOT_DWELL + 2);
  }
  // Full outline: approximate based on typical tile rendering
  return POINTS_PER_TILE_FULL;
}

// Enforce the scan point budget by demoting lower-priority tiles to corners-only
// CRITICAL tiles are never demoted. MEDIUM tiles are demoted first, then HIGH.
void enforcePointBudget() {
  pointBudget = (uint16_t)(MAX_SCAN_POINTS * POINT_BUDGET_RATIO);

  // First pass: estimate total points at current rendering levels
  uint32_t totalPoints = 0;
  for (uint16_t i = 0; i < segmentTileCount; i++) {
    uint16_t idx = tileOrder[i];
    TilePriority pri = tilePriorities[idx];

    // In GROUT_MINIMAL mode, interior non-cut tiles already use corners-only
    bool useCorners = (pri == PRIORITY_LOW) ||
                      (currentGroutMode == GROUT_MINIMAL && !tiles[idx].isCut &&
                       pri >= PRIORITY_MEDIUM);

    totalPoints += estimateTilePoints(idx, useCorners);
  }

  if (totalPoints <= pointBudget) {
    Serial.printf("[BUDGET] OK: %lu/%u points estimated\n", totalPoints, pointBudget);
    return; // Within budget, no demotions needed
  }

  // Over budget — demote MEDIUM tiles to LOW (corners-only) until within budget
  uint16_t demotedCount = 0;

  // Pass 1: Demote MEDIUM tiles
  for (uint16_t i = 0; i < segmentTileCount && totalPoints > pointBudget; i++) {
    uint16_t idx = tileOrder[i];
    if (tilePriorities[idx] != PRIORITY_MEDIUM) continue;

    // Calculate savings from demotion
    uint16_t fullPts = estimateTilePoints(idx, false);
    uint16_t cornerPts = estimateTilePoints(idx, true);
    uint16_t saved = fullPts - cornerPts;

    tilePriorities[idx] = PRIORITY_LOW;
    totalPoints -= saved;
    demotedCount++;
  }

  // Pass 2: If still over budget, demote HIGH tiles (boundary tiles)
  if (totalPoints > pointBudget) {
    for (uint16_t i = 0; i < segmentTileCount && totalPoints > pointBudget; i++) {
      uint16_t idx = tileOrder[i];
      if (tilePriorities[idx] != PRIORITY_HIGH) continue;

      uint16_t fullPts = estimateTilePoints(idx, false);
      uint16_t cornerPts = estimateTilePoints(idx, true);
      uint16_t saved = fullPts - cornerPts;

      tilePriorities[idx] = PRIORITY_LOW;
      totalPoints -= saved;
      demotedCount++;
    }
  }

  Serial.printf("[BUDGET] Adjusted: ~%lu/%u points, demoted %u tiles to corners-only\n",
                totalPoints, pointBudget, demotedCount);
}

// ============================================================================
// SCAN PATH OPTIMIZATION — Nearest-neighbor tile ordering
// ============================================================================

void optimizeTileOrder() {
  segmentTileCount = 0;

  // First pass: collect all tiles in the current segment and compute centers
  for (uint16_t t = 0; t < tileCount; t++) {
    if (tiles[t].vertCount < 3) continue;
    if (!tileInSegment(t)) continue;

    // Compute center of this tile
    float cx = 0, cy = 0;
    for (uint8_t v = 0; v < tiles[t].vertCount; v++) {
      cx += tiles[t].verts[v][0];
      cy += tiles[t].verts[v][1];
    }
    cx /= tiles[t].vertCount;
    cy /= tiles[t].vertCount;

    tileCenters[segmentTileCount].tileIdx = t;
    tileCenters[segmentTileCount].cx = cx;
    tileCenters[segmentTileCount].cy = cy;
    tileCenters[segmentTileCount].visited = false;
    segmentTileCount++;
  }

  if (segmentTileCount <= 1) {
    // No optimization needed
    for (uint16_t i = 0; i < segmentTileCount; i++) {
      tileOrder[i] = tileCenters[i].tileIdx;
    }
    return;
  }

  // Find the tile nearest to the segment origin (top-left) as starting point
  float startX = segmentX;
  float startY = segmentY;
  float bestDist = 1e9f;
  uint16_t bestIdx = 0;

  for (uint16_t i = 0; i < segmentTileCount; i++) {
    float dx = tileCenters[i].cx - startX;
    float dy = tileCenters[i].cy - startY;
    float dist = dx * dx + dy * dy; // Squared distance (no sqrt needed for comparison)
    if (dist < bestDist) {
      bestDist = dist;
      bestIdx = i;
    }
  }

  // Nearest-neighbor traversal
  tileCenters[bestIdx].visited = true;
  tileOrder[0] = tileCenters[bestIdx].tileIdx;
  uint16_t currentIdx = bestIdx;

  for (uint16_t step = 1; step < segmentTileCount; step++) {
    bestDist = 1e9f;
    bestIdx = 0;

    float curX = tileCenters[currentIdx].cx;
    float curY = tileCenters[currentIdx].cy;

    for (uint16_t i = 0; i < segmentTileCount; i++) {
      if (tileCenters[i].visited) continue;

      float dx = tileCenters[i].cx - curX;
      float dy = tileCenters[i].cy - curY;
      float dist = dx * dx + dy * dy;
      if (dist < bestDist) {
        bestDist = dist;
        bestIdx = i;
      }
    }

    tileCenters[bestIdx].visited = true;
    tileOrder[step] = tileCenters[bestIdx].tileIdx;
    currentIdx = bestIdx;
  }

  Serial.printf("[OPT] Path optimized: %u tiles in segment\n", segmentTileCount);
}

// ============================================================================
// SCAN BUFFER BUILDER — Converts tile data into optimized scan path
// ============================================================================

void buildScanBuffer() {
  scanPointCount = 0;

  if (tileCount == 0) return;

  Serial.printf("[SCAN] Building scan buffer for %d tiles, segment(%.0f,%.0f)...\n",
                tileCount, segmentX, segmentY);

  // Step 1: Optimize tile drawing order (nearest-neighbor)
  optimizeTileOrder();

  // Step 2: Select grout rendering mode based on beam/grout ratio
  if (groutModeAuto) computeGroutMode();

  // Step 3: Reset edge deduplication tracking
  drawnEdgeCount = 0;

  // Step 4: Assign priorities to each tile in the segment
  assignTilePriorities();

  // Step 5: Enforce point budget — demote lower-priority tiles if over budget
  enforcePointBudget();

  // Step 6: Draw tiles in optimized order with mode-appropriate rendering
  for (uint16_t i = 0; i < segmentTileCount; i++) {
    addTileToScanBuffer(tileOrder[i]);
  }

  Serial.printf("[SCAN] Buffer: %u points, %u tiles, grout=%s\n",
                scanPointCount, segmentTileCount, groutModeStr(currentGroutMode));
}

bool tileInSegment(uint16_t tileIdx) {
  // Check if any vertex of this tile is within the segment bounds
  // (with a small margin for partial tiles)
  float margin = 1.0f; // 1 inch margin

  for (uint8_t v = 0; v < tiles[tileIdx].vertCount; v++) {
    float x = tiles[tileIdx].verts[v][0];
    float y = tiles[tileIdx].verts[v][1];

    if (x >= segmentX - margin && x <= segmentX + segmentW + margin &&
        y >= segmentY - margin && y <= segmentY + segmentH + margin) {
      return true;
    }
  }
  return false;
}

void addTileToScanBuffer(uint16_t tileIdx) {
  TileData &tile = tiles[tileIdx];
  TilePriority priority = tilePriorities[tileIdx];
  bool cutTile = tile.isCut;

  // LOW priority tiles (demoted by budget enforcement) → corners only
  if (priority == PRIORITY_LOW) {
    addCornersOnly(tileIdx);
    return;
  }

  // GROUT_MINIMAL mode (manual override only — never auto-selected):
  // Non-cut interior tiles → corners only. Boundary and cut tiles keep full outlines.
  if (currentGroutMode == GROUT_MINIMAL && !cutTile && priority >= PRIORITY_MEDIUM) {
    addCornersOnly(tileIdx);
    return;
  }

  uint8_t dwell = cutTile ? CUT_CORNER_DWELL : CORNER_DWELL;

  // Move to first vertex (blanked)
  uint16_t dacX, dacY;
  if (!inchesToDAC(tile.verts[0][0], tile.verts[0][1], dacX, dacY)) return;

  // Blanking move to start position
  addScanPoint(dacX, dacY, false);
  addScanPoint(dacX, dacY, false); // Extra settle time

  // Draw tile outline
  for (uint8_t v = 0; v < tile.vertCount; v++) {
    if (!inchesToDAC(tile.verts[v][0], tile.verts[v][1], dacX, dacY)) continue;

    // Corner dwell: repeat point for brighter corners
    // Cut tiles get extra dwell for measurement reference visibility
    for (uint8_t d = 0; d < dwell; d++) {
      addScanPoint(dacX, dacY, true);
    }

    // Interpolate line to next vertex for smoother lines
    uint8_t nextV = (v + 1) % tile.vertCount;
    uint16_t nextDacX, nextDacY;
    if (inchesToDAC(tile.verts[nextV][0], tile.verts[nextV][1], nextDacX, nextDacY)) {
      // GROUT_SINGLE edge deduplication: skip shared edges already drawn by neighbor
      if (currentGroutMode == GROUT_SINGLE && !cutTile) {
        EdgeKey ek = makeEdgeKey(tile.verts[v][0], tile.verts[v][1],
                                 tile.verts[nextV][0], tile.verts[nextV][1]);
        if (isEdgeDrawn(ek)) {
          continue; // Skip — already drawn by adjacent tile
        }
        markEdgeDrawn(ek);
      }

      if (cutTile) {
        // Dashed line for cut tiles — visually distinct
        interpolateDashedLine(dacX, dacY, nextDacX, nextDacY);
      } else {
        // Solid line for full tiles
        interpolateLine(dacX, dacY, nextDacX, nextDacY, true);
      }
    }
  }

  // Close the shape: return to first vertex
  if (inchesToDAC(tile.verts[0][0], tile.verts[0][1], dacX, dacY)) {
    for (uint8_t d = 0; d < dwell; d++) {
      addScanPoint(dacX, dacY, true);
    }
  }

  // Blank after tile
  addScanPoint(dacX, dacY, false);
}

// Interpolate between two points for smoother galvo movement
void interpolateLine(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2, bool laser) {
  int32_t dx = (int32_t)x2 - (int32_t)x1;
  int32_t dy = (int32_t)y2 - (int32_t)y1;

  // Calculate distance in DAC units
  float dist = sqrtf((float)(dx * dx + dy * dy));

  // Add intermediate points every ~50 DAC units (about 1° galvo movement)
  // This ensures smooth lines even for long segments
  int steps = (int)(dist / 50.0f);
  if (steps < 1) steps = 1;
  if (steps > 100) steps = 100; // Cap to prevent buffer overflow

  for (int s = 1; s <= steps; s++) {
    float t = (float)s / (float)(steps + 1);
    uint16_t ix = x1 + (uint16_t)(t * dx);
    uint16_t iy = y1 + (uint16_t)(t * dy);
    addScanPoint(ix, iy, laser);
  }
}

// Interpolate a dashed line between two points
// Alternates between laser ON (dash) and laser OFF (gap) segments
void interpolateDashedLine(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2) {
  int32_t dx = (int32_t)x2 - (int32_t)x1;
  int32_t dy = (int32_t)y2 - (int32_t)y1;

  // Calculate total distance in DAC units
  float dist = sqrtf((float)(dx * dx + dy * dy));
  if (dist < 1.0f) return;

  // Unit direction vector
  float ux = (float)dx / dist;
  float uy = (float)dy / dist;

  // Walk along the line, alternating dash/gap
  float pos = 0.0f;
  bool dashOn = true;  // Start with dash (laser on)

  while (pos < dist) {
    float segLen = dashOn ? (float)DASH_LENGTH_DAC : (float)DASH_GAP_DAC;
    float segEnd = pos + segLen;
    if (segEnd > dist) segEnd = dist;

    // Interpolate points within this dash/gap segment (~50 DAC units apart)
    float segDist = segEnd - pos;
    int steps = (int)(segDist / 50.0f);
    if (steps < 1) steps = 1;

    for (int s = 0; s <= steps; s++) {
      float t = pos + (segDist * (float)s / (float)steps);
      uint16_t px = x1 + (uint16_t)(ux * t);
      uint16_t py = y1 + (uint16_t)(uy * t);
      addScanPoint(px, py, dashOn);
    }

    pos = segEnd;
    dashOn = !dashOn; // Toggle dash/gap
  }
}

void addScanPoint(uint16_t x, uint16_t y, bool laserOn) {
  if (scanPointCount >= MAX_SCAN_POINTS) return;

  scanBuffer[scanPointCount].x = x;
  scanBuffer[scanPointCount].y = y;
  scanBuffer[scanPointCount].laserOn = laserOn;
  scanPointCount++;
}

// Build a calibration square pattern (for verifying projection size)
void buildCalibrationPattern(float sizeInches) {
  scanPointCount = 0;

  float halfSize = sizeInches / 2.0f;

  // Center of projection
  float cx = segmentX + segmentW / 2.0f;
  float cy = segmentY + segmentH / 2.0f;

  // Four corners of calibration square
  float corners[4][2] = {
    {cx - halfSize, cy - halfSize},  // Bottom-left
    {cx + halfSize, cy - halfSize},  // Bottom-right
    {cx + halfSize, cy + halfSize},  // Top-right
    {cx - halfSize, cy + halfSize}   // Top-left
  };

  // Draw square
  uint16_t dacX, dacY;

  for (int c = 0; c < 4; c++) {
    if (!inchesToDAC(corners[c][0], corners[c][1], dacX, dacY)) continue;

    // Move to corner (blanked if first)
    bool laser = (c > 0);
    for (int d = 0; d < CORNER_DWELL * 2; d++) {
      addScanPoint(dacX, dacY, laser);
    }

    // Line to next corner
    int nextC = (c + 1) % 4;
    uint16_t nextX, nextY;
    if (inchesToDAC(corners[nextC][0], corners[nextC][1], nextX, nextY)) {
      interpolateLine(dacX, dacY, nextX, nextY, true);
    }
  }

  // Close the square
  if (inchesToDAC(corners[0][0], corners[0][1], dacX, dacY)) {
    for (int d = 0; d < CORNER_DWELL * 2; d++) {
      addScanPoint(dacX, dacY, true);
    }
  }

  // Add crosshair at center
  uint16_t cxDac, cyDac;
  if (inchesToDAC(cx, cy, cxDac, cyDac)) {
    // Horizontal line through center
    uint16_t lx, rx, ty, by2;
    if (inchesToDAC(cx - halfSize * 0.3f, cy, lx, ty) &&
        inchesToDAC(cx + halfSize * 0.3f, cy, rx, by2)) {
      addScanPoint(lx, ty, false);
      addScanPoint(lx, ty, false);
      interpolateLine(lx, ty, rx, ty, true);
      addScanPoint(rx, ty, true);
    }
    // Vertical line through center
    uint16_t bx, tx;
    if (inchesToDAC(cx, cy - halfSize * 0.3f, bx, by2) &&
        inchesToDAC(cx, cy + halfSize * 0.3f, tx, ty)) {
      addScanPoint(bx, by2, false);
      addScanPoint(bx, by2, false);
      interpolateLine(bx, by2, bx, ty, true);
      addScanPoint(bx, ty, true);
    }
  }

  Serial.printf("[CAL] Calibration pattern: %.0f\" square, %u points\n", sizeInches, scanPointCount);
}

// ============================================================================
// SCAN LOOP — Outputs points to DAC at 20K PPS
// ============================================================================

void runScanLoop() {
  if (scanPointCount == 0) return;

  // Run through the entire scan buffer once per call
  // This should be called from loop() — it blocks for the duration of one frame

  for (uint32_t i = 0; i < scanPointCount; i++) {
    // Safety check mid-scan
    if (!safetyOK || !projecting) {
      laserOff();
      return;
    }

    ScanPoint &pt = scanBuffer[i];

    // Set laser state
    if (pt.laserOn && laserEnabled) {
      laserOn();
    } else {
      laserOff();
    }

    // Write X and Y to DAC simultaneously
    writeDACBoth(pt.x, pt.y);

    // Timing: maintain consistent point rate
    if (pt.laserOn) {
      delayMicroseconds(POINT_DELAY_US);
    } else {
      delayMicroseconds(BLANKING_DELAY_US); // Longer delay for blanking moves
    }
  }

  // After full frame, brief blank before restart
  laserOff();
  delayMicroseconds(BLANKING_DELAY_US * 2);
}

// ============================================================================
// DAC CONTROL — MCP4822 via SPI
// ============================================================================

// Write to a single DAC channel
// channel: 0 = A (Galvo X), 1 = B (Galvo Y)
// value: 0-4095 (12-bit)
void writeDAC(uint8_t channel, uint16_t value) {
  if (value > 4095) value = 4095;

  // MCP4822 16-bit command:
  // Bit 15:    Channel (0=A, 1=B)
  // Bit 14:    Buffer (1=buffered)
  // Bit 13:    Gain (0=2x → 0-4.096V, 1=1x → 0-2.048V)
  // Bit 12:    Shutdown (1=active)
  // Bits 11-0: Data

  uint16_t command = 0;
  command |= (channel & 0x01) << 15;  // Channel select
  command |= 0x01 << 14;               // Buffered
  command |= 0x00 << 13;               // 2x gain (full 0-4.096V range)
  command |= 0x01 << 12;               // Active (not shutdown)
  command |= (value & 0x0FFF);         // 12-bit data

  dacSPI->beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE0));
  digitalWrite(PIN_SPI_CS, LOW);
  dacSPI->transfer16(command);
  digitalWrite(PIN_SPI_CS, HIGH);
  dacSPI->endTransaction();
}

// Write both channels and latch simultaneously
void writeDACBoth(uint16_t valueA, uint16_t valueB) {
  // Hold LDAC high (don't latch yet)
  digitalWrite(PIN_DAC_LDAC, HIGH);

  // Write Channel A (Galvo X)
  writeDAC(0, valueA);

  // Write Channel B (Galvo Y)
  writeDAC(1, valueB);

  // Pulse LDAC low to latch both channels simultaneously
  // This ensures X and Y update at the exact same moment
  digitalWrite(PIN_DAC_LDAC, LOW);
  delayMicroseconds(1); // Minimum pulse width: 100ns
  digitalWrite(PIN_DAC_LDAC, HIGH);
}

// ============================================================================
// LASER CONTROL
// ============================================================================

// NOTE: The MOSFET inverts the signal.
// ESP32 HIGH → MOSFET ON → TTL LOW → Laser OFF
// ESP32 LOW  → MOSFET OFF → TTL HIGH → Laser ON

void laserOn() {
  if (!safetyOK || !laserEnabled) return;
  digitalWrite(PIN_LASER_TTL, LOW);   // Inverted: LOW turns laser ON
}

void laserOff() {
  digitalWrite(PIN_LASER_TTL, HIGH);  // Inverted: HIGH turns laser OFF
}

void stopProjection() {
  projecting = false;
  laserEnabled = false;
  laserOff();
  // Center galvos
  writeDACBoth(DAC_CENTER, DAC_CENTER);
  Serial.println("[PROJ] Projection stopped.");
}

void emergencyStop() {
  laserOff();
  projecting = false;
  laserEnabled = false;
  writeDACBoth(DAC_CENTER, DAC_CENTER);
  setStatusColor(COLOR_ERROR);
  Serial.println("[SAFETY] EMERGENCY STOP - Interlock opened!");

  if (clientConnected) {
    wsServer.sendTXT(connectedClient, "{\"type\":\"safety_stop\",\"msg\":\"Enclosure opened\"}");
  }
}

// ============================================================================
// SAFETY INTERLOCK ISR
// ============================================================================

void IRAM_ATTR safetyISR() {
  // Read safety pin
  safetyOK = (digitalRead(PIN_SAFETY) == LOW);

  // If unsafe, immediately disable laser (in ISR context for minimum latency)
  if (!safetyOK) {
    digitalWrite(PIN_LASER_TTL, HIGH); // Laser OFF immediately
    laserEnabled = false;
  }
}

// ============================================================================
// STATUS LED
// ============================================================================

void setStatusColor(uint32_t color) {
  statusLED.setPixelColor(0, color);
  statusLED.show();
}

void updateStatusLED() {
  if (millis() - lastLEDUpdate < 50) return; // 20Hz LED update rate
  lastLEDUpdate = millis();

  ledPulsePhase += 4;

  // Pulsing effect for certain states
  if (!safetyOK) {
    // Fast red blink for safety error
    uint8_t brightness = (millis() / 200) % 2 ? 255 : 0;
    statusLED.setPixelColor(0, statusLED.Color(brightness, 0, 0));
  }
  else if (bumpDetected) {
    // Fast orange blink for bump
    uint8_t brightness = (millis() / 150) % 2 ? 255 : 0;
    statusLED.setPixelColor(0, statusLED.Color(brightness, brightness / 4, 0));
  }
  else if (projecting) {
    // Solid bright blue while projecting
    statusLED.setPixelColor(0, COLOR_PROJECTING);
  }
  else if (clientConnected) {
    // Slow blue pulse when connected but idle
    uint8_t brightness = (sin(ledPulsePhase * 0.05f) + 1.0f) * 64;
    statusLED.setPixelColor(0, statusLED.Color(0, brightness / 4, brightness));
  }
  else {
    // Slow green pulse when ready
    uint8_t brightness = (sin(ledPulsePhase * 0.03f) + 1.0f) * 64;
    statusLED.setPixelColor(0, statusLED.Color(0, brightness, 0));
  }

  statusLED.show();
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

// Check if a point is inside any void region
bool isInVoid(float x, float y) {
  for (uint8_t v = 0; v < voidCount; v++) {
    if (x >= voids[v].x && x <= voids[v].x + voids[v].w &&
        y >= voids[v].y && y <= voids[v].y + voids[v].h) {
      return true;
    }
  }
  return false;
}

// Calculate distance between two scan points (for path optimization)
float pointDistance(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2) {
  int32_t dx = (int32_t)x2 - (int32_t)x1;
  int32_t dy = (int32_t)y2 - (int32_t)y1;
  return sqrtf((float)(dx * dx + dy * dy));
}
