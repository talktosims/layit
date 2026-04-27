# LayIt App Store Launch — Paste Sheet

Open this file alongside Safari. Every field below is copy/paste ready. The order matches the 5 Safari tabs.

---

## Tab 1 — appleid.apple.com (Personal Information)

**Why:** Your Apple Dev account currently shows as "Robbie sims" (lowercase) which becomes the seller name on the App Store, and mismatches your tax return.

Sign in with your Apple ID. Click **Personal Information** → **Name**.

| Field | Change to |
|---|---|
| First Name | `Robert` |
| Last Name | `Sims` |
| Preferred Name (if separate field) | `Robbie` (optional — only this stays for display contexts) |

Save. This propagates into App Store Connect within minutes (sometimes you have to log out/in once).

---

## Tab 2 — App Store Connect → Agreements

**Confirm:** Paid Apps Agreement row says **Active** (was "New" before you signed it).

If it still says "New" or "Action Needed":
- Bank Account: complete it (Simco LLC checking is fine; Apple needs ACH routing + account #)
- Tax forms: the W-9 you submitted may show. If you want to re-edit it later (Robbie → Robert, EIN → SSN), use the **contact us** link in that page banner.

Once Active, move to Tab 3.

---

## Tab 3 — App Store Connect → Apps → "+" → New App

Click the blue **+** in the top left → **New App**.

| Field | Value |
|---|---|
| Platforms | ☑ **iOS** (only) |
| Name | `LayIt - Tile Layout Planner` |
| Primary Language | `English (U.S.)` |
| Bundle ID | `com.layit.app` (pick from dropdown) |
| SKU | `layit-ios-v1` |
| User Access | `Full Access` |

Click **Create**.

> ⚠️ If `com.layit.app` is NOT in the Bundle ID dropdown, jump to **Tab 4** first to register it, then come back here.

### Right after the app is created, fill these on the App Information page:

| Field | Value |
|---|---|
| Subtitle | `Plan tiles. Scan. Install.` |
| Privacy Policy URL | `https://layit.pages.dev/privacy` |
| Terms of Use URL (in EULA section if shown) | `https://layit.pages.dev/terms` |
| Category — Primary | `Utilities` |
| Category — Secondary | `Productivity` |
| Content Rights | "Does not contain, show, or access third-party content" → **Yes** (you own all the rendered tile graphics) |
| Age Rating Questionnaire | All "None" → results in **4+** |

### Then on Pricing and Availability:

| Field | Value |
|---|---|
| Price | **Free** (Tier 0) |
| Availability | Click **Edit** next to Countries/Regions → **Deselect All** → then re-check all **except** the 27 EU member states |

EU states to **uncheck**: Austria, Belgium, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden.

(Easier path: check **All** first, then uncheck just those 27. We re-enable EU later when the P.O. Box is set up.)

---

## Tab 3 (continued) — Subscriptions

Left sidebar inside the LayIt app → **Monetization → Subscriptions** → **+ Subscription Group**.

**Subscription Group**
- Reference Name: `LayIt Pro`
- Localizations (English U.S.):
  - Display Name: `LayIt Pro`
  - Description: `Access all LayIt Pro features`

**Subscription 1: Monthly**

| Field | Value |
|---|---|
| Reference Name | `LayIt Pro Monthly` |
| Product ID | `layit.pro.monthly` |
| Subscription Duration | `1 Month` |
| Price | `$4.99` (USD, US base) |
| Localization Display Name | `LayIt Pro Monthly` |
| Localization Description | `Full access to all Pro features, billed monthly` |
| Review Information → Screenshot | Upload a paywall screenshot (we'll capture later from TestFlight) |
| Review Notes | `Tap any Pro-only feature in the app to surface the paywall, then tap Monthly to test purchase. Sandbox tester credentials provided at the app review level.` |

**Subscription 2: Annual**

| Field | Value |
|---|---|
| Reference Name | `LayIt Pro Annual` |
| Product ID | `layit.pro.annual` |
| Subscription Duration | `1 Year` |
| Price | `$39.99` (USD, US base) |
| Localization Display Name | `LayIt Pro Annual` |
| Localization Description | `Full access to all Pro features, billed annually` |
| Review Information → Screenshot | Same paywall screenshot |
| Review Notes | `Same flow as monthly, tap Annual on the paywall.` |

> Both subscriptions need a **review screenshot** and **review notes** before they can be added to a submission. The screenshot can be added later — but the products can be created now.

> **Critical:** When you submit the app, you must also submit BOTH subscriptions in the **same submission**. First-time IAPs can't be submitted separately from the app version.

---

## Tab 4 — developer.apple.com → Identifiers (only if needed)

Use this only if `com.layit.app` doesn't appear in the Bundle ID dropdown on Tab 3.

Click **+** → **App IDs** → **App** → Continue.

| Field | Value |
|---|---|
| Description | `LayIt iOS App` |
| Bundle ID | **Explicit**, value: `com.layit.app` |
| Capabilities | ☑ In-App Purchase |

Save. Refresh Tab 3 — bundle should now appear.

---

## Tab 5 — developer.apple.com/contact (only if needed)

Use this if Apple has locked the W-9 from editing and you want to reset name (Robbie → Robert) and TIN (EIN → SSN) before payouts start.

- Topic: **Membership and Account**
- Sub-topic: **Update Account Information**
- Message: copy-paste this:

```
Hi Apple,

I need to update my account legal name and tax form. My W-9 currently shows "Robbie sims" but my tax return uses "Robert Sims" — I have updated my Apple ID to reflect this. I also submitted the W-9 with an EIN for my single-member LLC (Simco LLC), but per IRS instructions for disregarded entities the W-9 should use my SSN. Please reset my W-9 so I can resubmit with my correct legal name and SSN.

Thanks,
Robert Sims
Apple Dev Team ID: DBYUK7F39N
```

This is **non-blocking for app submission today** — only matters before payouts begin (~30 days after first sale).

---

## Reference: app description copy

If you need the long description for App Information → Description (paste exactly):

```
Stop guessing. Start laying.

LayIt is the tile layout planner that puts the power of a professional estimator in your pocket. Whether you're a seasoned installer or a first-time DIYer, LayIt gets you from "I like this tile" to "I know exactly what I need" in under 2 minutes.

SCAN ANY TILE
Point your camera at the box label. Our AI reads the specs — shape, size, material, everything — and fills it all in automatically. No manual entry. No measuring. Supports 20+ tile shapes including hex, subway, mosaic sheets, arabesque, fishscale, and more.

SEE YOUR LAYOUT INSTANTLY
Enter your room dimensions by drawing the perimeter on screen. Your tile layout renders in real-time — full tiles, cut tiles, waste — all calculated and color-coded. Drag to reposition the pattern. Tap Optimize to minimize cuts.

KNOW WHAT TO BUY
See exactly how many boxes you need. Compare prices across stores with one tap. Never over-buy or make a second trip.

PRO FEATURES
• Unlimited AI tile scanning
• Cut tracking with exact measurements
• Professional client reports (3-page printable PDF)
• Price comparison across retailers
• Company branding for shared reports

BUILT FOR THE JOB SITE
• Works offline with 45+ built-in tile presets
• Supports complex room shapes (L-shaped, nooks, angles)
• Cutout support for outlets, niches, windows
• 20+ tile shapes: hex, square, subway, penny, fishscale, mosaic, arabesque, octagon, and more
• Inches or centimeters

COMING SOON
• LayIt Laser — a WiFi laser projector that beams your tile pattern onto walls and floors at 1:1 scale
• AI room measurement from photos
• AR tile preview

Download LayIt and never guess at tile again.
```

**Promotional Text (170 chars, can update without new build):**

```
Snap a photo of any tile box — AI reads the specs instantly. See your layout in seconds. Know exactly how many boxes to buy before you leave the store.
```

**Keywords (100 chars, comma-separated, no spaces):**

```
tile,layout,calculator,planner,mosaic,hex,subway,backsplash,floor,install,grout,cut,estimate,scan
```

**Support URL:**

```
https://layit.pages.dev
```

(The legal page links to privacy + terms; that's enough.)

**Marketing URL (optional):**

```
https://layit.pages.dev
```

---

## App Privacy answers (App Privacy section in App Store Connect)

When App Store Connect asks "Do you or your third-party partners collect data from this app?" → **Yes**.

Then for each data category, answer:

| Category | Collected? | Linked to user? | Used for tracking? | Purpose |
|---|---|---|---|---|
| Photos (tile box photos) | Yes | No | No | App Functionality (sent to AI proxy for tile spec extraction; not stored after) |
| Photos (workspace photos) | No (stored on device only, never uploaded) | — | — | — |
| Crash data | Yes (if Apple's anonymous crash reporting is on) | No | No | App Functionality |
| Diagnostics | Yes | No | No | App Functionality |
| Purchases | Yes (Apple StoreKit) | Yes | No | App Functionality |

Everything else: **No**.

---

## App Review Notes (paste into "App Review Information")

Already drafted in `sales/APP_STORE_SUBMISSION_PACK.md` lines 45-67 — copy that block. Includes:
- Sandbox test credentials prompt
- Camera + AI proxy explanation
- Subscription product IDs
- "Verify measurements" disclaimer note

---

## What Claude can't do (you must)

- Apple ID password / 2FA
- Bank account / SSN entry
- Anything inside App Store Connect forms (auth-locked)
- Approve the legal entity declarations
- Take iPhone screenshots (needs your physical device)

## What Claude is doing in parallel

- Standing by to archive + upload from Xcode the moment your app record exists
- Standing by to capture + caption screenshots once you give me the iPhone
- Standing by to fill the App Privacy answers exactly per the table above (you read them; I confirm)
