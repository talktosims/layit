# LayIt App Store Launch Checklist

## Status: Launch Candidate, Pending Account Setup + Real-Device QA

The codebase is close enough to start App Store Connect setup and TestFlight. Do not submit for public review until the physical iPhone checks and StoreKit sandbox checks below pass.

## Code Audit Complete

- [x] Release build passes with code signing disabled for CI/local audit
- [x] Bundled web app loads in a mobile browser smoke test
- [x] Core tabs open: Wall, Tile, Layout/Calc, Projects, Settings
- [x] App icon exists at 1024x1024
- [x] Bundle ID is `com.layit.app`
- [x] Team ID is `DBYUK7F39N`
- [x] Version/build is `1.0` / `1`
- [x] Camera usage string is present
- [x] StoreKit 2 purchase/restore bridge is implemented
- [x] StoreKit product IDs are configured in `LayIt.storekit`
- [x] Native barcode scanner is implemented
- [x] Share sheet bridge is implemented
- [x] Debug Pro override is disabled in Release builds
- [x] No AI API key is embedded in the app binary
- [x] AI calls require the configured Cloudflare Worker proxy
- [x] Firebase tile geometry read failures fall back without breaking app load
- [x] Cloud Sync is no longer marketed as a live Pro feature
- [x] iPhone-only v1 target set to reduce screenshot/review surface

## Must Do Before App Review

- [ ] Create the App Store Connect app record
  - Name: `LayIt - Tile Layout Planner`
  - Bundle ID: `com.layit.app`
  - SKU: `layit-ios-v1`
  - Platform: iOS
  - Primary language: English (U.S.)
- [ ] Accept any pending Apple agreements and complete tax/banking
- [ ] Create subscriptions in App Store Connect
  - `layit.pro.monthly` — LayIt Pro Monthly — $4.99/month
  - `layit.pro.annual` — LayIt Pro Annual — $39.99/year
- [ ] Add the subscriptions to the first app version submission
- [ ] Host the privacy policy and terms at public HTTPS URLs
- [ ] Complete App Privacy answers in App Store Connect
- [ ] Capture iPhone screenshots, 1-10 images. Use the largest iPhone screenshot size App Store Connect requests first, currently 6.9-inch; 6.5-inch screenshots can scale when accepted by Media Manager.
- [ ] Archive and upload from Xcode
- [ ] Run TestFlight on a physical iPhone
- [ ] Submit app + subscriptions together for review

## Physical iPhone TestFlight Gate

- [ ] Fresh install opens onboarding cleanly
- [ ] Camera permission prompt appears with correct wording
- [ ] Barcode scanner opens, scans a real UPC/EAN, and returns to app
- [ ] Label/photo AI scan works through `https://layit-api.robbie-96f.workers.dev`
- [ ] No-internet AI failure is graceful and manual tile entry still works
- [ ] Layout renders after manual room/tile entry
- [ ] Save, load, export, import project all work
- [ ] Share sheet opens from project/report sharing
- [ ] Monthly subscription purchase succeeds with sandbox tester
- [ ] Annual subscription purchase succeeds with sandbox tester
- [ ] Restore Purchases updates Pro status correctly
- [ ] Pro-only controls unlock only after sandbox purchase/restore

## Known Launch Risks

- [ ] Cloudflare Worker endpoint is publicly callable. Add Cloudflare rate limiting and monitor usage before spending ad money.
- [ ] Firebase security rules should be reviewed so anonymous users can only read/write intended paths.
- [ ] App Store privacy labels must match the app exactly: camera photos for AI scanning, local project data, Firebase tile database/feedback/waitlist, StoreKit purchases.
- [ ] AI extraction can be wrong. App copy and review notes should keep the "verify measurements/specs" disclaimer.

## Revenue Readiness

- [x] Free tier: layout planning, manual tile entry, limited AI scanning, project saving/export
- [x] Pro tier: unlimited AI scanning, cut tracking, client reports, price comparison, company branding
- [x] Cloud Sync is positioned as future/waitlist, not a paid live feature
- [x] App Store first is the recommended v1 route for trust, install friction, and iOS discovery
- [ ] Add a web funnel/PWA after App Store launch for SEO, demos, email capture, and lower-fee direct subscriptions
- [ ] Consider a lifetime purchase after subscription conversion is measured

## Post-Launch Hardening (do AFTER first version is live)

These were deliberately deferred on launch day (Apr 25, 2026) to ship faster. Both should be done within 1–4 weeks of launch.

### Move app to Simco LLC organization Apple Developer account
- [ ] Request a free D-U-N-S number for Simco LLC at https://developer.apple.com/enroll/duns-lookup (1 business day)
- [ ] Enroll Simco LLC as an Apple Developer Program organization ($99/yr, separate from individual account). Apple verifies via D-U-N-S, takes 2–7 days.
- [ ] In App Store Connect, request **app transfer** of `com.layit.app` from the individual account ("Robbie sims") to the Simco LLC team. Apple supports this without resubmission.
- [ ] After transfer, update privacy/terms wording on https://layit.pages.dev to drop the "Robbie Sims" attribution and say "Simco LLC" cleanly.
- **Why:** liability shield (app reviews, refund disputes, lawsuits all hit the LLC, not Robbie personally), cleaner tax flow (W-9 on EIN, not SSN), more professional seller name on the App Store ("Simco LLC" vs "Robbie sims") for B2B buyers (Floor & Decor, contractors), app becomes a transferable LLC asset.

### Enable EU launch with private address
- [ ] Set up a P.O. Box or registered agent in Minneapolis (USPS PO Box ~$100/yr; commercial registered agent ~$100–200/yr but accepts non-mail like service of process). Use the Simco LLC registered business address if it's already public on MN Secretary of State filings — that satisfies DSA without exposing the home address further than it already is.
- [ ] In App Store Connect → Business → "Complete Compliance Requirements," declare **trader** status and supply the P.O. Box or business address (NOT home address).
- [ ] In the LayIt app's Pricing and Availability, re-enable all 27 EU member states.
- **Why:** EU DSA requires public display of trader name + address on EU listing pages for any IAP/paid app. Home address (4307 Oliver Ave N) was kept private at launch by excluding EU territories. EU has ~450M iOS users — meaningful TAM once safe to enable.
