# LayIt QA Test Plan — Pre-Launch

Run through these tests on a physical iPhone before App Store submission.

## 1. Fresh Install Experience
- [ ] Delete app from phone, reinstall from Xcode
- [ ] "Where are we starting?" modal appears
- [ ] Select "Identify My Tile" → scan instruction modal shows → camera opens
- [ ] Cancel → nudges to wall tab
- [ ] Select "Measure My Room" → wall tab opens
- [ ] Default layout (70×58 hex) shows on layout tab without any input

## 2. Wall Tab
- [ ] Draw box shows default rectangle with green lines
- [ ] Measurement inputs are tappable on each wall line
- [ ] Change a measurement → layout updates in background
- [ ] Clear → canvas re-enables drawing
- [ ] Draw 5-point polygon → Close → measurements appear
- [ ] "Update Layout" button validates before navigating
- [ ] in/cm toggle changes labels

## 3. Tile Tab
- [ ] "Identify Tile" shows FREE badge on first use
- [ ] Tap → scan instruction modal → camera opens
- [ ] Take photo of tile box label → AI reads specs → product found modal
- [ ] Apply → tile specs populate, layout updates
- [ ] Second scan attempt shows PRO badge / upgrade modal
- [ ] Browse button opens searchable tile browser
- [ ] Shape filter buttons work
- [ ] Preset dropdown applies correctly
- [ ] Grout color swatches change layout background
- [ ] Tile color swatches change full tile color
- [ ] Rotate button swaps width/height

## 4. Layout Tab
- [ ] Layout renders with tiles, wall border, cutouts
- [ ] Single finger drags pattern (when unlocked)
- [ ] Pinch to zoom works
- [ ] Two-finger pan works
- [ ] Lock button locks pattern
- [ ] Locked: single finger pans (doesn't move pattern)
- [ ] Optimize finds better position, shows toast with results
- [ ] START indicator shows when locked
- [ ] Full/Cut counts update correctly

## 5. Cut Tracking (Pro)
- [ ] Tap orange tile when unlocked → "Lock pattern first" toast
- [ ] Tap orange tile when locked → Pro check → detail view
- [ ] Detail view shows sub-tile breakdown for mosaic
- [ ] Detail view shows cut measurements
- [ ] Tap detail → yellow, tap again → red (done)
- [ ] Red tile → confirmation modal to reset
- [ ] Mosaic: entire sheet turns red when marked done

## 6. Calculator Tab
- [ ] Tile count auto-refreshes when tab opens
- [ ] Full + Cuts + Waste = Total display correct
- [ ] Box count shows when pieces-per-box is known
- [ ] Price field → cost updates live
- [ ] Compare Prices button opens Google Shopping
- [ ] Job cost estimator calculates materials + labor
- [ ] Shopping list generates correctly

## 7. Files Tab
- [ ] Current Project at top
- [ ] My Projects below
- [ ] Save project → appears in list
- [ ] Load project → restores everything (tile color, grout color, pattern position)
- [ ] Export → downloads JSON
- [ ] Import → loads JSON project
- [ ] Share with Friend → native share sheet
- [ ] Client Report → 3-page preview with outline layout
- [ ] Company Branding → hidden until Pro
- [ ] Cloud Sync → hidden until Pro
- [ ] Pro enabled → sections appear with New! badges

## 8. Client Report (Pro)
- [ ] Shows 3 pages in dark background viewer
- [ ] Page 1: brand header, workspace photo, project summary
- [ ] Page 2: B&W outline layout with dimension brackets
- [ ] Page 3: lined notes page
- [ ] Pinch to zoom works
- [ ] Zoom out → snaps to page view
- [ ] All text readable (no light gray)
- [ ] Share button works
- [ ] Project name appears as title (not "Tile Layout")

## 9. Settings Tab
- [ ] Pro status shows Free/Active correctly
- [ ] Feature guide dropdowns expand/collapse
- [ ] Project Sharing — no PRO badge
- [ ] Client Report Share — has PRO badge
- [ ] Restart Tutorial resets onboarding
- [ ] Send Feedback opens email

## 10. Edge Cases
- [ ] No internet → AI scan fails gracefully (toast message)
- [ ] Very small room (12×12) → layout renders correctly
- [ ] Very large room (300×400) → layout renders without lag
- [ ] Mosaic with tiny sub-tiles (1" hex) → renders without crashing
- [ ] All 20 tile shapes render without errors
- [ ] Save project with grout/tile colors → restore correctly
- [ ] Kill app → reopen → last state preserved
