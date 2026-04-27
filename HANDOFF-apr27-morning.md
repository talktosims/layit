# LayIt — Morning Handoff (Apr 27, 2026)

**Read this first.** Then read `HANDOFF-launch-night.md` for full context.

## Where things stand right now

- LayIt v1.0 was **submitted to App Review last night at 9:33 PM CT (Apr 26).**
- Apple sent the **"We've received your app for review"** confirmation email to `talktosims@gmail.com` (timestamp 9:34 PM, ~1 minute after submission).
- Status: **"Waiting for Review"** in App Store Connect.
- **No action needed on the submission itself** — Apple has the binary, metadata, screenshots, and IAPs. Everything is in their hands.

Apple's published review timing:
- 50% of apps reviewed in **24 hours**
- 90% reviewed in **48 hours**
- Realistic decision window for LayIt: **today (Apr 27) → tomorrow night (Apr 28)**

When Apple emails back:
- **Approved** → "Pending Developer Release" or "Ready for Distribution" → open the version page → click **"Release This Version"**
- **Rejected** → read message in App Store Connect Resolution Center → fix only what's flagged → resubmit (usually same build, just metadata change or written response)

Decision tree for both outcomes is in `HANDOFF-launch-night.md`.

## What to do TODAY (Apr 27, Monday — Apple support open)

This is the right window because Apple Developer Support is open during US business hours and Mondays are usually quick-turnaround.

### 1. File the Account Holder name support ticket (~3 min)

**Why:** Your Apple Developer Account currently displays as **"Robbie sims"** (lowercase 's'). When LayIt goes live, the App Store seller line will say "Robbie sims" — looks unprofessional. A casing fix to "Robert Sims" via Apple Developer Support resolves in 1 business day and updates the live listing automatically (no resubmission needed).

**How:**
1. Go to https://developer.apple.com/contact/topic/select
2. Pick **Membership and Account** → **Update Account Information**
3. Paste this exact message (copy-paste, do not edit):

```
Hi Apple,

My App Store Connect Account Holder name displays as "Robbie sims" 
but my correct legal name (matching my Apple ID and tax records) 
is "Robert Sims." This is a casing/preferred-name correction, 
not a legal name change. Please update my Account Holder name to 
"Robert Sims" so it displays correctly as the seller name on my 
upcoming first App Store submission.

Thank you,
Robert Sims
Apple Dev Team ID: DBYUK7F39N
```

4. Submit. You'll get a case number; Apple typically responds within 1 business day.

This is intentionally framed as a casing/preferred-name correction (not a legal name change) so it doesn't trigger ID re-verification.

### 2. (Optional) Start the D-U-N-S lookup for Simco LLC (~1 min, free)

**Why:** First step toward transferring the app to a Simco LLC organization Apple Developer account, which gives you (a) liability shield, (b) cleaner W-9 with EIN, (c) "Simco LLC" as seller name instead of any individual name, and (d) the ability to declare EU DSA trader and re-enable the 27 EU territories.

**How:**
1. Go to https://developer.apple.com/enroll/duns-lookup
2. Search for Simco LLC. If it doesn't exist, request a new one (free, ~1 business day).
3. Once D-U-N-S is issued, you can enroll Simco LLC as an Apple Developer Program organization ($99/yr, separate from the existing individual account). Apple verifies via D-U-N-S — 2-7 days.
4. After org enrollment is active, request **app transfer** of `com.layit.app` from the individual account to Simco LLC. No resubmission needed for the transfer.

Full details + post-transfer cleanup are in `APP_STORE_CHECKLIST.md` "Post-Launch Hardening" section.

### 3. Don't touch anything in App Store Connect

Specifically: **don't edit metadata, don't change screenshots, don't pull the app from review.** Any edit to the in-flight submission either bumps it back in the queue or restarts review entirely. The app is configured correctly — leave it alone until Apple responds.

## What to do when Apple emails a decision

### If Apple emails "Pending Developer Release" (approved with manual release)

1. Open https://appstoreconnect.apple.com/apps/6763955926/distribution
2. On the version page, scroll to **"Version Release"** at the bottom — should say "Manually release this version"
3. When you're ready (could be immediate, could wait for an announcement): click **"Release This Version"**
4. Goes live to all 148 territories within 1–24 hours (usually 2–6 hours)
5. Capture the App Store URL the moment it's live, share with network

### If Apple emails "Rejected"

1. Open the **Resolution Center** in App Store Connect (link in the email or under "App Review" in the sidebar)
2. Read Apple's message carefully — the rejection reason will be a Guideline number (e.g., 3.1.2, 5.1.1)
3. Most likely reasons + fixes are in `HANDOFF-launch-night.md` section "Likely Apple review outcomes"
4. **Don't immediately resubmit.** If anything is ambiguous, reply through Resolution Center asking for clarification. Apple reviewers often clarify within hours.
5. Fix only what's flagged → resubmit using the **same build** if the rejection is metadata-only (you can re-edit description/keywords/etc and resubmit without re-uploading the binary)

## Files to know

- `HANDOFF-launch-night.md` — full context (490 lines, all IDs, every decision tree)
- `LAUNCH-CHEATSHEET.md` — paste-ready strings for any field that needs re-entering
- `APP_STORE_CHECKLIST.md` — submission checklist + post-launch hardening (LLC transfer, EU enable, App Preview video)
- `CLAUDE.md` — project overview, file copy protocol (3 sync'd index.html copies)

## Memory to load (if you're a fresh Claude session)

- `~/.claude/projects/-Users-Sims-Desktop-stageit/memory/project_layit_submitted.md` — what got submitted and when
- `~/.claude/projects/-Users-Sims-Desktop-stageit/memory/reference_layit_launch_ids.md` — all permanent IDs (App Store ID 6763955926, bundle, ASC API key path, etc.)
- `~/.claude/projects/-Users-Sims-Desktop-stageit/memory/project_layit_post_launch_legal.md` — LLC transfer + EU enable plan

## Things NOT to worry about today

- The "Robbie sims" lowercase 's' on the Account Holder profile — support ticket above handles it.
- Apple potentially calling the +18883662685 contact number — that's a Twilio outbound number, but Apple almost never actually calls during review. They email instead.
- The 27 EU territories being excluded — deliberate to avoid DSA trader public-address disclosure. Re-enabled later via the post-launch hardening plan.
- The demo video — recording a fresh one is in the post-launch backlog, not blocking launch.

## State of the open browser tabs

Chrome (Robbie's primary):
- App Store Connect — version page (post-submit state, "Waiting for Review")
- App Store Connect — Business / Agreements (Paid Apps Active, bank verified)
- Apple Developer — Identifiers (com.layit.app present)
- Subscription group page (LayIt Pro, both products attached)
- Gmail — Apple's "We've received your app" email visible

Safari (mostly stale from yesterday's session) — can be closed.

## Bottom line for the new session

**Don't touch the submission. File the support ticket. Optionally kick off D-U-N-S. Watch for Apple's email.** When the email arrives, follow the decision tree above.
