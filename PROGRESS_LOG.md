# LayIt Work Session — March 19, 2026

## Session Summary
Massive day. Tile database 3x expansion, 20 tile shape renderers, native barcode scanner, AI label scanning, client report, complete onboarding redesign, paywall fixes, App Store prep.

---

## Database
- **45 → 195 presets** in master_presets.json
- **33 + 12 = 45 entries** in TILE_DB_LOCAL (offline)
- **37 real UPC barcodes** scraped from upcitemdb.com
- **All uploaded to Firebase** (164 + 31 = 195 total)
- Brands: Daltile, MSI, Merola, Marazzi, Jeffrey Court, American Olean, Bedrosians, Emser, Apollo Tile, Ivy Hill, Sunwings, ABOLOS

## New Tile Shapes (20 total)
Previously: square, rectangle, hexagon, herringbone, penny, fishscale, diamond
Added: octagon+dot, arabesque, picket, rhombus/3D cube, triangle, capsule/pill, quatrefoil, ogee/provenzal, star & cross, kite, leaf/teardrop, dragon scale, chevron

## AI Label Scanner
- Primary tile identification method (replaces barcode as default)
- User photographs box label → Claude Vision API extracts all specs
- Auto-populates shape, dimensions, grout, material
- Saves to Firebase so next person gets instant match
- First scan free, Pro required after
- Instruction modal tells user exactly what to photograph

## Native iOS Barcode Scanner
- BarcodeScannerView.swift using AVFoundation
- Full-screen camera with viewfinder, scan line, haptic feedback
- Wired via scanBarcode message handler
- Preserved as fallback when DB hits 500+ verified UPCs

## Client Report (Pro)
- 3-page B&W print-ready report
- Page 1: Company branding, workspace photo, project summary
- Page 2: Outline-only layout (clipped to perimeter, dimension brackets), tile specs + materials side-by-side
- Page 3: Additional notes (lined)
- Pinch-to-zoom viewer with snap-to-page on zoom out
- Dark background print-preview look

## Onboarding Redesign
- Replaced 7-step wizard with "Where are we starting?" two-choice modal
- Options: "Measure My Room" or "Identify My Tile"
- Cascading workflow: finish one → nudged to the other
- First-visit tab modals: centered overlay with dim background

## UI Changes
- Wall tab: removed Quick Rectangle, removed measurement status cards
- in/cm unit toggle in wall tab header
- Perimeter draw box auto-populates rectangle from existing dimensions
- Overlay measurement inputs on perimeter lines
- "Update Layout" button with validation
- Files tab: Current Project → My Projects → Backup → Client Report → Pro sections
- Calc tab: visual Full+Cuts+Waste=Total display, box count, live cost, price comparison
- Mosaic sheets turn fully red when marked as cut
- Cutout tab: descriptive labels on size fields
- Calculator icon changed from abacus to match tab

## Bug Fixes
- Paywall bypass: removed duplicate handleProPurchase() that granted free Pro
- Duplicate element IDs: removed proUpgradeBtn/proManageBtn from Laser tab
- Dead code: removed toggleCuts(), showCuts variable
- Duplicate functions: consolidated showUpgradeModal, requirePro, closeUpgradeModal
- Firebase path mismatch: layit/tiledb → tiledb
- Canvas capture: diagram panel shown offscreen for toDataURL
- Report text visibility: forced dark colors on all report text
- Cut tracking: Pro check before lock check on tile tap

## App Store Prep
- Full App Store listing draft (sales/APP_STORE_LISTING.md)
- Privacy policy
- Terms of service
- Screenshot copy for 8 screens
- API key moved out of source code to native bridge

## Tools Built
- scrape-manufacturers.js (1,197 lines) — Puppeteer + Claude API
- tessellation-engine.js (824 lines) — geometry validation
- upload-rest.js — Firebase REST API uploader
- scrape-upcs.js — UPC barcode scraper

## Commits (all pushed to GitHub)
17 commits on main, all pushed to origin
