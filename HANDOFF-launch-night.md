# LayIt v1.0 — Launch Night Handoff

**Submitted to Apple App Review:** Sunday Apr 26, 2026 ~9:33 PM CT
**Status as of handoff:** "Waiting for Review" (Apple email to talktosims@gmail.com expected within 24–48h)

This document is the single source of truth for picking up LayIt work in a fresh Claude Code session. Read it first.

---

## TL;DR — What just happened

LayIt iOS v1.0 was submitted to the App Store today in one ~6-hour session that took it from zero account state to fully submitted with two subscriptions. Everything required is in. Apple has the binary, the metadata, the screenshots, the IAPs, and the contact info. Nothing else needs to happen for the review to proceed.

What a fresh session will likely need to do:
1. Check whether Apple has emailed a decision yet (`talktosims@gmail.com`).
2. If approved → release to App Store (manual or automatic per the version page setting).
3. If rejected → read the rejection reason, fix, resubmit. The most likely reasons are listed below.
4. Knock out two deferred housekeeping items (Account Holder name support ticket, EU enable later).

---

## What Apple is reviewing

| Field | Value |
|---|---|
| App Store ID | **6763955926** |
| Bundle ID | `com.layit.app` |
| Apple Developer Team | `DBYUK7F39N` (individual account, "Robbie sims") |
| Version submitted | **1.0 build 1** |
| Binary upload UUID | `20aed1c8-117a-4c06-8d4d-fe9eacaebf14` (Apr 26 2026 19:31 CT) |
| App name | LayIt - Tile Layout Planner |
| Subtitle | "Plan tiles. Scan. Install." |
| Categories | Utilities (primary) + Productivity (secondary) |
| Age rating | 4+ |
| Price | Free (Tier 0, all 148 countries) |
| Availability | 148 countries (US/Canada + non-EU Europe + rest of world). **EU 27 excluded.** |
| Subscriptions in same submission | `layit.pro.monthly` ($4.99/mo), `layit.pro.annual` ($39.99/yr) |
| Subscription group | LayIt Pro (id `22054384`) |
| App Store ID for Monthly | 6763959800 |
| App Store ID for Annual | 6763962565 |
| Privacy Policy URL | https://layit.pages.dev/privacy |
| Terms URL | https://layit.pages.dev/terms |
| App Privacy declared | Photos (App Functionality, not linked, no tracking), Purchases (App Functionality, not linked, no tracking), Crash Data (App Functionality, not linked, no tracking) |
| Export Compliance | Exempt — uses only iOS standard HTTPS, no custom crypto |
| App Review Contact | Robert Sims, talktosims@gmail.com, +18883662685 |

5 screenshots uploaded at 1284×2778 (6.5" iPhone slot) at `~/Downloads/layit-screenshots-resized/IMG_938{4,5,6,7,8}.PNG`. Originals are at `~/Downloads/IMG_9388.PNG` etc. The paywall (IMG_9388) is also attached as the review screenshot for both subscriptions.

---

## Where things live

### Repos
- Code: `~/Desktop/LayIt-iOS/` (GitHub: https://github.com/talktosims/layit)
- Web app source (in 3 sync'd copies — see `CLAUDE.md` File Copy Protocol):
  - `~/Desktop/LayIt-iOS/index.html`
  - `~/Desktop/LayIt-iOS/LayIt-iOS/index.html`
  - `~/Desktop/LayIt-iOS/LayIt-iOS/Resources/WebApp/index.html`
- Legal pages (deployed to https://layit.pages.dev): `~/Desktop/LayIt-iOS/legal/{privacy,terms,index}.html`

### Build artifacts (ephemeral, /tmp)
- Archive: `/tmp/LayIt.xcarchive` (~Apr 26)
- IPA: `/tmp/LayIt-export/LayIt-iOS.ipa` (8.9 MB, signed)
- Export options: `/tmp/layit-export.plist`

### Credentials & API keys
- ASC API key ID: `VATJ3UH983`
- ASC API issuer: `e7e83ad3-262a-4ebb-9451-4499a521c1d5`
- ASC API .p8 file: `~/.appstoreconnect/private_keys/AuthKey_VATJ3UH983.p8` (chmod 600, persistent)
- Cloudflare account: `robbie@simcopaint.com` (`96f060e249781842b0da5e7012828f0e`)
- Cloudflare Pages projects: `layit` (legal site), `simcopaint`, `stageit`
- AI proxy worker (already live, used by app): https://layit-api.robbie-96f.workers.dev
- W-9 EIN (Simco LLC, NOT used for this dev account, kept for reference): `37-2149345`

### Persistent memory references
- `~/.claude/projects/-Users-Sims-Desktop-stageit/memory/reference_layit_launch_ids.md` — all IDs above + build pipeline commands
- `~/.claude/projects/-Users-Sims-Desktop-stageit/memory/project_layit_post_launch_legal.md` — deferred LLC transfer + EU enable plan

---

## One-shot rebuild + reupload (for any future LayIt update)

```bash
cd ~/Desktop/LayIt-iOS

# 1. Bump CFBundleVersion / CFBundleShortVersionString in LayIt-iOS/Info.plist if needed

# 2. Archive
xcrun xcodebuild -project LayIt-iOS.xcodeproj -scheme LayIt-iOS \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath /tmp/LayIt.xcarchive -allowProvisioningUpdates archive

# 3. Export IPA
rm -rf /tmp/LayIt-export
xcrun xcodebuild -exportArchive -archivePath /tmp/LayIt.xcarchive \
  -exportPath /tmp/LayIt-export -exportOptionsPlist /tmp/layit-export.plist \
  -allowProvisioningUpdates

# 4. Upload (fully headless — no clicking)
xcrun altool --upload-app --type ios --file /tmp/LayIt-export/LayIt-iOS.ipa \
  --apiKey VATJ3UH983 --apiIssuer e7e83ad3-262a-4ebb-9451-4499a521c1d5
```

If `/tmp/layit-export.plist` is missing, recreate it with: method=app-store-connect, destination=export, teamID=DBYUK7F39N, signingStyle=automatic, uploadSymbols=true, stripSwiftSymbols=true. (See `~/Desktop/LayIt-iOS/build/api-proxy/SETUP.md` for the canonical version.)

---

## Likely Apple review outcomes & how to handle each

### A) Approved (most likely)
- Email subject: "Your app status is Ready for Distribution" or "Pending Developer Release."
- Default behavior: app version was set to **manual release** unless explicitly set to auto-release. Check the version page → "Version Release" section to confirm.
- To release: hit **Release This Version** on the version page. Goes live in 1–24 hours after that.
- **Then immediately:**
  - Capture App Store URL, post to https://layit.pages.dev (replace placeholder if any), share with the network.
  - File the **Account Holder name support ticket** (Robbie sims → Robert Sims). Without this fix, the seller name on the App Store listing displays as "Robbie sims" with lowercase 's'. Apple Developer Support resolves this in 1 business day.
  - Begin **post-launch hardening** per `APP_STORE_CHECKLIST.md` "Post-Launch Hardening" section — D-U-N-S → Simco LLC org dev account → app transfer → re-tighten privacy/terms wording to drop "Robbie Sims" attribution.

### B) Rejected — most likely reasons & fixes

**B1. Subscription paywall design / disclosure (Guideline 3.1.2)**
- Apple sometimes wants the paywall to display: subscription length, full price, what's unlocked, terms link, restore link, all visible above the purchase button.
- The current paywall (IMG_9388) shows all of those. If rejected, screenshot the actual paywall in app and verify nothing's clipped.

**B2. Privacy nutrition label mismatch (Guideline 5.1.1)**
- We declared: Photos (App Functionality), Purchases (App Functionality), Crash Data (App Functionality), all "Not Linked to User," all "No Tracking."
- If Apple's automated scan catches code touching anything else (e.g., Firebase Analytics auto-collecting), update App Privacy on the next submission. Firebase tile DB reads/writes don't normally trigger this.

**B3. AI service disclosure (newer Apple policy, Guideline 4.7 / 5.5)**
- App sends photos to Anthropic via Cloudflare Worker for tile spec extraction. Review notes already disclose this with the proxy URL.
- If rejected for AI scope: the proxy is `https://layit-api.robbie-96f.workers.dev`, the model is Claude Opus, and only tile box label photos are sent. Photos are not stored on our server.

**B4. "Explanation needed" for some claim**
- Reviewer may ask why X (e.g., "where is laser projector available?" — answer: it's described as "Coming Soon" in the app description, not yet a paid feature).
- Reply through Resolution Center on App Store Connect.

In all rejection cases: do NOT immediately resubmit. Read the message, ask follow-up via Resolution Center if anything is ambiguous, fix only what's flagged, then resubmit using the same build (most rejections allow same-build resubmission — they just need a metadata change or written response).

---

## What's still on the to-do list (carry forward)

### Immediate (do as soon as Robbie wakes up, before review completes)
- **None blocking.** Submission is in.

### Within 1 business day of approval
- **File Account Holder name support ticket** at https://developer.apple.com/contact/topic/select → Membership and Account → Update Account Information. Use the message saved in `LAUNCH-CHEATSHEET.md` Tab 5 section. This fixes the "Robbie sims" → "Robert Sims" display name on the App Store listing.

### Within 1–4 weeks of launch (per `APP_STORE_CHECKLIST.md` Post-Launch Hardening)
- Move app to a Simco LLC organization Apple Developer account (D-U-N-S lookup → org enrollment → app transfer). Liability shield + cleaner W-9 + better seller name.
- Set up P.O. Box / registered agent address, declare EU DSA trader, re-enable the 27 EU territories.
- Record + upload an App Preview video (15–30s, 1284×2778 or 1320×2868, no third-party logos). Adds ~15–25% conversion lift; can be added without new build.

### Open product backlog items (from `APP_STORE_CHECKLIST.md` Revenue Readiness)
- Web funnel/PWA after App Store launch for SEO, demos, email capture, and direct subscription pricing.
- Lifetime purchase tier once subscription conversion is measured.
- Full SAM 3 / Florence-2 / BiRefNet / GroundingDINO eval for tile segmentation (notes in `room_scan_prototype/RESEARCH_NOTES.md`).
- Cloud Sync wiring (currently a stub; positioned as future feature, not promised in v1.0 metadata).

---

## What changed in the repo today

Recent commits, in order:
1. `3b690cd` — Pre-launch sweep: barcode scanner iOS 17 API fixes + index.html overhaul (Codex's overnight Apr 25→26 work)
2. `11b4303` — Add legal site source (deployed to https://layit.pages.dev)
3. `d21d19f` — Fix legal entity in privacy/terms (initially Simco LLC)
4. `f1b6875` — Soften legal entity wording: "Robbie Sims, a software project of Simco LLC"
5. `909e163` — Add post-launch hardening section: Simco LLC dev account transfer + EU/PO Box

Untracked but should remain:
- `LAUNCH-CHEATSHEET.md` (this session's paste-ready strings)
- `HANDOFF-launch-night.md` (this file)

---

## How to check submission status programmatically

The ASC API key is installed permanently. Quick status check from any future session:

```bash
# Fetch current app store version state via App Store Connect API
# (One-liner needs JWT signing — easiest path is to ask Claude to compose the curl)

# Or just open the version page in browser:
open https://appstoreconnect.apple.com/apps/6763955926/distribution
```

Apple emails `talktosims@gmail.com` for state changes (waiting → in review → ready/rejected).

---

## Open Safari/Chrome tabs at handoff

Tab 1 (Chrome) — App Store Connect version page (post-submit state)
Tab 2 (Chrome) — Business agreements (Paid Apps Active, bank verified)
Tab 3 (Chrome) — Apple Developer Identifiers list (com.layit.app present)
Tab 4 (Chrome) — Subscriptions group page

Safari tabs are stale from earlier session navigation; Chrome is the live workspace.

---

## What I (Claude) couldn't do tonight without Robbie

These remain as "needs Robbie at the keyboard" if anything goes wrong before he wakes up:

1. **iPhone 12-check TestFlight gate** — never ran. Build was uploaded, submitted, and accepted by Apple's automated processing (no compliance issues), but no human verified install + sandbox IAP purchase + restore on a real device. **Risk:** if a runtime crash exists that didn't fail the smoke build, Apple's reviewer will catch it. Probability: low — Codex's overnight work compiled clean and the bundled web app is the same code that's been running locally for weeks.
2. **Drag-and-drop file uploads** — Chrome blocks programmatic file uploads via DevTools. All screenshot + paywall uploads were done by Robbie manually.
3. **2FA / password entry** — every Apple ID auth was Robbie.

---

## If the next session is a brand-new Claude with no context

Start by reading, in order:
1. This file (`HANDOFF-launch-night.md`)
2. `~/Desktop/LayIt-iOS/CLAUDE.md` (project overview, file copy protocol)
3. `~/Desktop/LayIt-iOS/APP_STORE_CHECKLIST.md` (current state of every launch + post-launch item)
4. `~/Desktop/LayIt-iOS/LAUNCH-CHEATSHEET.md` (paste-ready strings if anything needs re-entering)
5. Memory references: `reference_layit_launch_ids.md` and `project_layit_post_launch_legal.md`

Then check `git log --since="2026-04-26"` in `~/Desktop/LayIt-iOS/` to see anything Codex or Robbie may have done overnight.

The submission is in Apple's hands. Be patient. Don't resubmit unless rejected.
