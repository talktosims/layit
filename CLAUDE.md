# LayIt — Project Memory

## Product Overview
- LayIt is a **tile layout app + laser projection system**
- App: single-file PWA (index.html, ~12K lines) wrapped in iOS WKWebView
- Laser: portable 200mW green galvo projector that beams tile patterns onto walls/floors at 1:1 scale
- Two laser models: **Flagship** (corded, ~$499) and **Pro** (corded + battery, ~$649)
- Three provisional patents filed March 2026 (shared with StageIt platform)

## File Structure
```
layit/                      ← Web app (git repo, pushed to GitHub)
├── index.html              ← THE app (~12K lines, vanilla JS PWA)
├── sw.js                   ← Service worker (cache: layit-v11)
├── manifest.json           ← PWA manifest
├── icon-*.png/svg          ← App icons
├── paint-calculator.html   ← Separate paint calc tool
├── build/                  ← Laser hardware docs
│   ├── assembly_diagrams/  ← SVG + PNG wiring diagrams (5 steps)
│   ├── Build Binder/       ← PDF build binder
│   ├── LayIt_Hardware/     ← Hardware package
│   ├── enclosure/          ← 3D enclosure files
│   └── *.docx/md           ← BOM, assembly guides, build partner posting
├── sales/                  ← Business docs
│   ├── LayIt_Product_Overview.md  ← Full product overview
│   ├── APP_STORE_LISTING.md
│   ├── ASO_KEYWORDS.md
│   └── *.pptx/docx/html    ← Pitch decks, sell sheets, roadmaps
├── patent/                 ← 3 provisional patent applications
│   ├── *_FILING_READY.pdf  ← Ready to file with USPTO
│   ├── *_Provisional.md    ← Source markdown
│   └── Patent_Evidence_Log.md
├── room_scan_prototype/    ← Python depth estimation prototype (Patent 2)
│   ├── ml-depth-pro/       ← Apple Depth Pro model (1.8GB, gitignored)
│   ├── venv/               ← Python venv (gitignored)
│   └── *.py/jpg/json       ← Test photos + scripts
└── tools/tile-scraper/     ← UPC barcode scraper

LayIt-iOS/                  ← Xcode project (NOT a git repo)
├── LayIt-iOS/
│   ├── WebAppView.swift    ← WKWebView + local HTTP server + purchase bridge
│   ├── ContentView.swift   ← Root SwiftUI view
│   ├── StoreManager.swift  ← StoreKit IAP
│   ├── BarcodeScannerView.swift ← AVFoundation barcode scanner
│   ├── index.html          ← Copy of web app (MUST sync with layit/index.html)
│   └── Resources/WebApp/
│       ├── index.html      ← Another copy (MUST sync)
│       └── sw.js           ← Service worker copy
```

## CRITICAL: File Copy Protocol
After ANY change to index.html, ALWAYS copy to BOTH iOS paths:
```
cp index.html /Users/Sims/Desktop/LayIt-iOS/LayIt-iOS/Resources/WebApp/index.html
cp index.html /Users/Sims/Desktop/LayIt-iOS/LayIt-iOS/index.html
```
Also copy sw.js to Resources/WebApp/ if changed.

## Core Hardware (Flagship BOM ~$237-$308)
- **MCU**: ESP32-S3-WROOM-1 (dual-core: Core 0 = vision/WiFi, Core 1 = galvo scan loop)
- **Laser**: 200mW 520nm green laser module with TTL driver
- **Galvo scanners**: 20Kpps XY galvanometer set with ILDA interface
- **Camera**: OV5640 5MP (for vision alignment system)
- **IMU**: MPU6050 6-axis (for bump detection)
- **DAC**: MCP4822 dual-channel SPI → TL072 op-amp buffer → galvo drivers
- **Power**: USB-C PD 12V → AMS1117-5.0 → AMS1117-3.3 (three voltage rails)
- Full BOM in: `build/LayIt_BOM_v3.md`

## Vision Alignment System (Patent 1)
- Uses **tile edge detection** (NOT fiducial markers)
- Every tile placed becomes a new reference point
- OpenCV: Canny edge detection → contour extraction → homography
- **Absolute positioning** — errors don't accumulate
- **Bump recovery**: IMU detects displacement, camera re-locks
- Spec: `build/LayIt_Vision_Alignment_Spec.md`

## AI Systems
- **Tile label scanner**: Claude Opus 4.6 via API. Reads box stickers, extracts specs. Handles metric, bilingual, mosaic sheets.
- **Spatial calibration pipeline**: When user takes workspace photo + enters manual measurements, Opus estimates dimensions in background. Both AI estimate and ground truth saved to Firebase `simco_spatial_calibration`. Accuracy metrics computed. Past calibration data injected into future prompts for self-improvement. Shared with StageIt (Patent 2 network effect).
- **API key**: Hardcoded in WebAppView.swift — MUST move to server proxy before App Store launch.

## Firebase
- **Project**: `paint-calc-sync` (shared with paint-calculator and StageIt)
- **Database URL**: `https://paint-calc-sync-default-rtdb.firebaseio.com`
- **Auth**: Anonymous sign-in
- **Paths used**:
  - `sync/{hash}/layit` — cloud sync (project state)
  - `tiledb/{barcode}` — crowdsourced tile database
  - `simco_spatial_calibration/` — shared spatial AI training data (LayIt + StageIt)
  - `waitlist/` — laser waitlist emails

## Patent Portfolio (3 provisionals, shared with StageIt)
1. **Laser Projection** — 27 claims. Vision-based self-correcting alignment, bump recovery, segmented projection.
2. **Camera Room Measurement** — 22 claims. Monocular depth estimation, RANSAC planes, calibration network effect.
3. **Material Geometry Extraction** — 22 claims. AI shape extraction from product images, tessellation inference.

## Key Lessons / Gotchas
- **WKWebView canvas repaint bug**: Canvas doesn't repaint on close. Fix: toggle wall panel `.active` class to force compositor teardown (mimics tab switch).
- `crypto.subtle` only works in secure contexts (HTTPS or localhost)
- Firebase security rules must match exact path
- Service worker cache: bump version in sw.js after changes (currently v11)
- Wood-look plank tiles use 3/16" grout (0.1875), not standard 1/8"
- `initCloudSync()` is a stub — cloud sync button exists but feature not wired up
- Two Pro upgrade modals existed — dead one removed, live one is `#proUpgradeModal`

## User Preferences
- Direct, no fluff
- Copy index.html to BOTH iOS paths after every change
- Test via Xcode: delete app, clean build (Shift+Cmd+K), rebuild
- Full permissions — no need to ask before changes
- Don't change UX decisions without asking
- Commit and push periodically
