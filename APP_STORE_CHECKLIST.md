# LayIt App Store Submission Checklist

## Status: NEARLY READY

### Done
- [x] App icon (1024x1024) — exists in Assets.xcassets
- [x] StoreKit products configured (monthly $4.99, annual $39.99)
- [x] Info.plist — camera permission, orientations, display name
- [x] Privacy policy — drafted in sales/APP_STORE_LISTING.md
- [x] Terms of service — drafted in sales/APP_STORE_LISTING.md
- [x] App description, keywords, subtitle — drafted
- [x] Bundle identifier: com.layit.app
- [x] Development team: DBYUK7F39N
- [x] Camera permission string set
- [x] Native barcode scanner built (BarcodeScannerView.swift)
- [x] StoreKit 2 purchase flow (StoreManager.swift)
- [x] Share sheet bridge (WebAppView.swift)
- [x] Paywall working correctly (no bypass)

### Needs User Action
- [ ] **App Store Connect setup** — log into appstoreconnect.apple.com
  - Create the app listing
  - Set up in-app purchase products (monthly + annual)
  - Upload the privacy policy URL (host on simcopaint.com or GitHub Pages)
  - Set age rating, category, pricing
- [ ] **Screenshots** — need 6.5" and 5.5" iPhone screenshots
  - Run on iPhone 15 Pro Max (6.7") for 6.5" class
  - Run on iPhone 8 Plus (5.5") or use simulator
  - 8 screenshots recommended (copy in APP_STORE_LISTING.md)
- [ ] **Archive & upload** — in Xcode: Product → Archive → Distribute
- [ ] **TestFlight** — test the build on real device before submission
  - Verify barcode scanner works on physical hardware
  - Verify StoreKit purchase flow with sandbox
  - Verify AI label scan works with real API key
  - Test offline mode (preset dropdown, manual entry)

### Optional But Recommended
- [ ] Launch screen — currently uses auto-generated. Could add branded splash.
- [ ] iPad layout — works but could be optimized for larger screen
- [ ] Accessibility — VoiceOver labels on key UI elements
- [ ] Localization — Spanish/French would expand market significantly
- [ ] App preview video (15-30 sec) — shows the scan → layout → box count flow

### Known Issues to Fix Before Submission
- [ ] Camera permission string should mention "tile label scanning" not just "barcodes"
- [ ] Verify the app works fully offline (no API key = no AI scan, but presets work)
- [ ] Test clean install experience (no localStorage, no projects)
- [ ] Verify "Restore Purchases" works with sandbox StoreKit

### Revenue Readiness
- [x] Free tier: layout + 1 scan + basic sharing
- [x] Pro tier: unlimited scans, cut tracking, client reports, price comparison, branding, cloud sync
- [x] First scan free messaging
- [x] "$47 savings" upgrade messaging
- [ ] Consider adding lifetime purchase option ($79.99)
