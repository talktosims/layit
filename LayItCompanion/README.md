# LayIt Companion App

Native iOS app for the LayIt tile layout laser system. Scans rooms with LiDAR and syncs dimensions to the web app.

## Requirements
- **Xcode 15+** (free from Mac App Store)
- **Apple Developer Account** ($99/yr at developer.apple.com) — needed for device testing and App Store
- **iOS 16+** device with LiDAR (iPhone 12 Pro or newer, iPad Pro)

## Quick Start

1. Open `LayItCompanion.xcodeproj` in Xcode
2. Set your **Development Team** in Signing & Capabilities (requires Apple Developer account)
3. Connect your iPhone/iPad via USB
4. Select your device as the build target
5. Hit **Run** (⌘R)

> **Note:** RoomPlan requires a physical LiDAR device — it won't work in the Simulator.

## Architecture

```
LayItCompanion/
├── LayItCompanionApp.swift     # App entry point
├── Info.plist                  # Permissions (camera, network)
├── Views/
│   ├── ContentView.swift       # Home screen: passphrase, scan, web app
│   ├── RoomScanView.swift      # RoomPlan scanning with live preview
│   ├── RoomResultView.swift    # Verify scanned room before syncing
│   └── WebAppView.swift        # WKWebView wrapper for full web app
├── Models/
│   ├── AppState.swift          # Global state (passphrase, scanned room)
│   └── ScannedRoom.swift       # Room polygon data model
└── Services/
    ├── RoomScanManager.swift   # RoomPlan session + polygon conversion
    └── FirebaseSyncService.swift  # Firebase RT Database sync
```

## How It Works

1. User enters the same **passphrase** used in the web app
2. Taps **Scan Room** → walks around with camera → RoomPlan detects walls
3. Reviews the scanned polygon with dimensions
4. Taps **Confirm & Sync** → room data pushed to Firebase
5. Web app receives the polygon via `window.onNativeRoomScan()` bridge
6. Web app auto-fills room dimensions and shows verification screen

## Firebase Sync

Uses the same database and path as the web app:
- **Database:** `https://paint-calc-sync-default-rtdb.firebaseio.com`
- **Path:** `sync/{hash}/layit/scannedRoom`
- **Hash:** FNV-based, matches the web app's JS implementation
- **No Firebase SDK required** — uses REST API directly

## Web App Integration

The companion app embeds the web app via WKWebView. It injects:
- `window.LAYIT_NATIVE = true` — web app knows it's in the native shell
- `window.LAYIT_HAS_LIDAR` — whether device has LiDAR
- `window.onNativeRoomScan(data)` — receives scanned room polygon
- `window.webkit.messageHandlers.layitNative` — JS→Native bridge

## TODO
- [ ] Sign up for Apple Developer account
- [ ] Set Development Team in Xcode
- [ ] Add app icon (1024x1024 for App Store)
- [ ] Bundle index.html + sw.js into Resources/WebApp/ for offline mode
- [ ] Test on LiDAR device
- [ ] Add Firebase listener in web app to receive scans without native bridge
- [ ] App Store submission (screenshots, description, review)
