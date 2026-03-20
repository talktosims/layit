# LayIt
### Precision Tile Layout System
**Every tile in its perfect place.**

*SIMCO Inc. — Confidential — March 2026*

---

## What Is LayIt?

LayIt is the tile installation platform that turns any smartphone into a precision layout engine — and a laser projector into a life-size blueprint on your floor. Photograph your room. Scan your tile box. The app generates a pixel-perfect tile pattern, counts every cut, and tells you exactly where to mark. When you're ready to install, the LayIt Laser projects the pattern onto the actual surface at 1:1 scale. No chalk lines. No graph paper. No $200/hour installer guessing.

One app replaces the measuring tape, the tile calculator, the cut list, and the chalk line. The laser replaces the level, the spacers, and the hours of layout by hand.

---

## The Market Gap

Tile installation is a $15B+ industry in the U.S. alone. Every project — from a $300 backsplash to a $30,000 bathroom remodel — starts the same way: someone gets on their knees with a tape measure, draws lines on the floor, and hopes they get the cuts right. Three problems define the gap:

**1. Wasted Tile, Wasted Money** — The industry standard "buy 10-15% extra" exists because nobody plans cuts properly. On a $2,000 tile purchase, that's $200-$300 thrown away. Pros overbuy because returning unused tile is a hassle. DIYers underbuy, make three trips to the store, and sometimes find the lot number no longer matches.

**2. Layout Is the Hardest Part** — Ask any tiler: cutting is mechanical, grouting is tedious, but *layout* is where skill matters. Where does the pattern start? How do you minimize cuts? What happens at the corners? A bad starting point means slivers at the walls, asymmetric cuts, and a job that looks amateur. There is no consumer tool that answers these questions.

**3. No Bridge from Digital to Physical** — Apps exist that calculate tile quantities. They show you a pretty picture on screen. But when you're standing in front of a real wall holding a real tile, that picture is useless. You still need to measure, mark, and hope. The gap between "plan" and "execute" is entirely manual.

---

## How LayIt Works

### The App: Plan

**30 seconds to a complete tile layout.** One smartphone. No training required.

**Step 1: Measure Your Space**
Three options, same result:

- **Quick Rectangle** — Enter width and height. Done. Covers 80% of jobs (backsplash, shower wall, simple floor).
- **Draw Your Shape** — Tap corners on the canvas to trace an L-shaped room, angled wall, or irregular floor. Enter the real measurement for each wall segment. The app builds an exact polygon.
- **Photo Scan** *(Patent 2)* — Photograph your room. Monocular depth estimation via Apple Depth Pro extracts wall positions, niches, and obstacles automatically. No LiDAR required — works on any iPhone. Multiple photos fuse into a single high-confidence measurement with <1% error on direct wall-to-wall dimensions.

**Step 2: Identify Your Tile**
- **AI Label Scanner** — Photograph the spec sticker on the tile box. Claude Vision reads the dimensions, material, shape, grout joint, and pieces per box. Handles metric labels, bilingual text, mosaic sheets, and every major brand. First scan free, unlimited with Pro.
- **Barcode Lookup** — Scan the UPC barcode for instant identification from our database of 111+ verified products across 16 brands.
- **234 Built-In Presets** — Every common tile size from 2" hex mosaics to 8×48 wood-look planks. Square, rectangle, hexagon, herringbone, and 17 mosaic sub-tile shapes including arabesque, fish scale, penny round, octagon-and-dot, and dragon scale.
- **Custom Entry** — Any size, any shape. Nominal or actual dimensions with automatic grout calculation.

**Step 3: See Your Layout**
The layout renders instantly. Full tiles in green. Cuts in orange. Pinch to zoom. Drag to reposition the pattern. Tap **Optimize** and the engine runs a two-pass search (coarse grid + fine-tune) to find the starting position that minimizes cuts and waste. The waste percentage displays live in the info bar.

Add cutouts for windows, outlets, niches, or shower benches. The pattern tiles around them automatically — and the cut tracker shows you exactly what needs to be removed from each tile that touches an obstacle.

**Step 4: Track Your Cuts**
Lock the pattern. Tap any orange tile. LayIt shows a full-screen detail view of that exact tile: the original shape in yellow, the cut line in red, and precise measurements in inches and fractions — "Mark at 3-7/8" from the left edge." Interior cuts show X and Y coordinates from tile edges. Mosaic sheets show the red cut line across the full sheet with measurements from the sheet edge.

Mark each tile as you cut it — it turns red. Track your progress across the entire job. Never lose your place.

**Step 5: Share and Report**
- **Free Share** — Send the layout as an interactive HTML page to your installer, spouse, or client.
- **Client Report** *(Pro)* — Generate a 3-page print-ready B&W report with your company branding, workspace photo, layout diagram with dimension brackets, tile specs, and material counts.
- **Export/Import** — Backup projects as JSON. Move between devices. Cloud sync coming soon.

### The Laser: Execute

**Your layout, projected onto the actual surface at 1:1 scale.**

The LayIt Laser is a portable projection device that connects to the app via WiFi and beams your tile pattern directly onto the wall or floor. Green laser lines show exactly where every tile goes — full tiles, cut lines, grout lines, cutout boundaries — all at real-world dimensions.

**Hardware** *(Patent 1)*
- 200mW 520nm green laser — visible in daylight, safe for residential use
- Dual-axis galvanometer scanner (20Kpps) for smooth, flicker-free projection
- ESP32-S3 dual-core microcontroller: Core 0 handles WiFi, camera, and vision; Core 1 runs the real-time galvo scan loop
- OV5640 5MP camera for vision alignment
- MPU6050 6-axis IMU for bump detection
- Two models: **Flagship** (~$499, corded) and **Pro** (~$649, corded + 1.5-2hr battery)

**Vision-Based Self-Correcting Alignment** *(Patent 1)*
This is the breakthrough. The laser doesn't need manual calibration, tape-measure setup, or fiducial markers.

- **Cold start**: Point it at a wall corner or placed tile. The camera detects edges via Canny edge detection + contour extraction + homography.
- **Self-reinforcing grid**: Every tile you place becomes a new reference point. Accuracy improves from ±2-3mm at cold start to <0.3mm after 25+ tiles.
- **Bump recovery**: The IMU detects if someone kicks the unit. The camera automatically re-locks to existing tile edges. Green/Yellow/Red confidence indicator shows alignment status.
- **Absolute positioning**: Errors don't accumulate. Each frame references the actual placed tiles, not the previous frame.

**Segmented Projection for Large Surfaces**
A 3-foot projection window covers a standard work zone. For large floors, the app generates a serpentine path of segments. Complete one segment, move the laser to the next, and it auto-aligns to the tiles you already placed. Progress tracking shows which segments are done.

---

## The 30-Minute Job

Here's what a typical backsplash installation looks like with LayIt:

| Time | What Happens |
|------|-------------|
| 0:00 | Open app. Guided setup asks "What are you tiling?" |
| 0:30 | Enter 58" × 18" backsplash dimensions |
| 1:00 | Photograph the tile box label. AI fills all specs |
| 1:30 | Full layout rendered. Tap Optimize |
| 2:00 | Add cutout for electrical outlet (6" × 4" at position 27" × 9") |
| 3:00 | Layout finalized. 47 full tiles, 12 cuts, 8% waste |
| 3:30 | Set up LayIt Laser on countertop. It locks to the wall corner |
| 4:00 | Green laser lines show the exact tile grid on the wall |
| 5:00–25:00 | Install tiles following the projected lines. Tap each cut tile for measurements |
| 25:00–30:00 | Final row. Laser confirms alignment. Job done |

No chalk lines drawn. No tiles dry-laid to check the pattern. No measuring each cut individually. The laser showed you where everything goes, and the app told you every measurement before you picked up the tile saw.

---

## Use Cases

### DIY Homeowners
The largest market. 65% of backsplash installations and 40% of bathroom floors are DIY. These people watch 3 hours of YouTube, buy 20% extra tile "just in case," and still end up with slivers at the edges because they started in the wrong place.

LayIt turns them into competent tilers on their first project. The app handles the hard part (layout math) and the laser handles the scary part (will this line be straight?). The emotional payoff is enormous — they feel like a pro.

### Professional Installers
Pros don't need help *cutting*. They need help *selling*. A branded client report with a 3D-accurate layout, material list, and cost estimate closes the deal before the first tile is placed.

On the job, the laser saves 30-60 minutes of layout time per job. At 3 jobs per week, that's 2-3 extra billable hours. The cut tracker eliminates the sticky-note system most pros use to track progress on complex jobs.

### Tile Retailers (Home Depot, Floor & Decor, Lowe's)
Retailers sell the tile but lose the customer at "now what?" LayIt closes the loop. A QR code on the tile display opens the app with that exact tile pre-loaded. Customer scans the box, enters their room size, and sees the layout in 30 seconds — while standing in the store.

The laser becomes a premium add-on or rental. "Buy 200 sq ft of this tile and rent the LayIt Laser for the weekend — $49."

### Commercial / Multi-Unit
Property managers tiling 50 identical bathrooms. Design the layout once. Push it to the laser. Every unit is identical. The installer doesn't even need the app — just the laser and the project file.

---

## Intellectual Property

Three provisional patent applications protect the complete LayIt system:

### Patent 1: Laser Projection System
*System and Method for Real-Time Laser Projection of Tile Installation Patterns with Vision-Based Self-Correcting Alignment*

**27 claims** covering:
- Portable laser + galvanometer + dual-core MCU architecture
- Vision-based alignment using placed tile edges (no fiducials)
- Self-reinforcing reference grid that improves with each tile placed
- IMU-triggered bump recovery with automatic camera re-lock
- Segmented projection with serpentine path traversal
- Multi-tile pattern support (hex, herringbone, mosaic)
- Hardware safety systems (interlock, firmware checks, auto-timeout)

### Patent 2: Camera-Based Room Measurement
*Method and System for Automatic Room Geometry Extraction from Monocular Camera Images for Generation of Tile Installation Layouts*

**22 claims** covering:
- Monocular depth estimation via Apple Depth Pro (no LiDAR required)
- RANSAC plane detection for wall/floor/ceiling classification
- Out-of-square wall detection (measuring parallelism at 10+ points)
- Automatic detection of niches, windows, shelves from depth anomalies
- Confidence-weighted multi-photo fusion (best-of-N per dimension)
- Constraint-aware auto-correction preventing grout alignment breaks
- Calibration network effect (accuracy improves across users/devices)
- Demonstrated <1% error on direct wall-to-wall measurements

### Patent 3: Material Geometry Extraction
*Method and System for Automated Extraction of Material Geometry and Tessellation Parameters from Digital Images*

**22 claims** covering:
- Vision-language AI model extracting shape geometry from product images
- Barcode-triggered automated extraction pipeline
- Tessellation inference (offset, rotation, multi-shape interlocking)
- Hybrid AI + manufacturer database validation
- Domain-general applicability (tiles, pavers, shingles, panels, fabric)
- Multi-shape pattern handling (octagon-and-dot, arabesque, ledger stone)
- Incremental learning from accumulated validation data

**Filing status:** All three filed March 2026. 12-month utility conversion deadline March 2027. Micro-entity filing.

**Note:** Patents 1, 2, and 3 are shared with the StageIt platform (SIMCO's retail merchandising product). Patent 2 (room scanning) powers both LayIt's room measurement and StageIt's store scanning. Patent 3 (geometry extraction) powers both LayIt's tile identification and StageIt's product recognition. This dual application doubles the value of each patent across two distinct markets.

---

## Pricing

### App (iOS, PWA)

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | Full layout engine, 234 presets, first AI scan free, project save/load, free sharing |
| **Pro** | $4.99/mo or $39.99/yr | Unlimited AI scanning, cut tracking with measurements, branded client reports, barcode scanner, cloud sync, company branding |

### Laser Hardware

| Model | Price | Specs |
|-------|-------|-------|
| **Flagship** | ~$499 | Corded (12V 3A), 200mW green laser, WiFi, vision alignment, bump recovery |
| **Pro** | ~$649 | Corded + battery (1.5-2hr), same laser and vision system, portable for job sites |

**BOM cost:** $237-$308 (Flagship), $302-$413 (Pro). Target 40-50% gross margin on hardware.

---

## Go-to-Market: Brand Awareness & User Acquisition

### Phase 1: Content-Led Organic Growth (Months 1-3)

**TikTok / Instagram Reels / YouTube Shorts — The "Magic Moment" Videos**
The LayIt Laser projecting a tile pattern onto a real wall is inherently viral. A 15-second video of green laser lines appearing on a blank wall, then tiles being placed perfectly along those lines, is the kind of content that stops the scroll.

Content pillars:
- **"Watch this"** — Laser projection time-lapses. 10 seconds of setup → 1 minute of perfect installation at 4x speed. Pure visual satisfaction.
- **"I saved $X"** — DIYers showing their first tile job vs. what a pro quoted them. LayIt makes the before/after dramatic.
- **"Cut tracker"** — Satisfying compilation of orange tiles turning red one by one as a job progresses. ASMR for the home improvement crowd.
- **"AI scanned it"** — Point phone at tile box → specs auto-fill → layout appears. The scan-to-layout flow in 8 seconds.

**Target:** 3-5 videos per week. Aim for 1M+ combined views in first 90 days. The laser content has the highest viral coefficient — it looks like science fiction but it's a real product.

**YouTube Long-Form — "Build With Me" Series**
Full job walkthroughs: backsplash, shower floor, fireplace surround, outdoor patio. Show the entire process from empty wall to finished tile. Each video naturally demonstrates every LayIt feature without being an ad. Link the app in every description.

**SEO / Content Marketing**
- "How to tile a backsplash" gets 33,000 monthly searches
- "Tile layout calculator" gets 12,000
- "How many tiles do I need" gets 8,000

Create definitive guides for each query. Embed the LayIt web app (PWA) directly in the article — readers can enter their dimensions and see a layout *inside the blog post*. Convert readers to users without leaving the page.

### Phase 2: Community & Partnerships (Months 2-6)

**Reddit / Facebook Groups**
- r/HomeImprovement (3.5M members), r/DIY (22M members), r/TilePorn
- Facebook: "DIY Home Improvement," "Tile Setters & Tile Contractors"
- Don't spam. Answer real questions. "Here's how I calculated my cuts" with a screenshot of the cut tracker. Let the product sell itself.

**Pro Installer Referral Loop**
Every client report includes "Powered by LayIt" branding. Every shared layout page has a "Get LayIt free" link. Pros become distribution channels — they send branded reports to clients, clients download the app to view the layout, clients become users for their next project.

Target: 100 active Pro users generating 300+ client reports/month = 300 branded touchpoints reaching homeowners.

**Tile Retailer Partnerships**
Approach Floor & Decor, independent tile showrooms, and Home Depot's Pro desk:
- "Put a QR code on your tile displays. Customer scans it, sees the layout in 30 seconds, and buys with confidence instead of going home to 'think about it.'"
- Reduces return rate (right tile count), increases basket size (they add grout, spacers, tools), and differentiates the retailer.
- The laser becomes a rental/add-on revenue stream for the retailer.

### Phase 3: Paid Acquisition (Month 4+)

**Meta Ads (Instagram/Facebook)**
Target: Homeowners who follow home improvement accounts, recently moved (address change signal), or searched for tile-related terms. The laser projection video as the ad creative. CPA target: $3-5 per app install.

**Google Ads**
Capture intent: "tile layout tool," "tile calculator app," "how to plan tile layout." These are users actively looking for the solution. CPA target: $2-4.

**Apple Search Ads**
"Tile calculator," "tile layout," "tile planner" — capture users searching the App Store directly. Highest intent, lowest funnel.

### Phase 4: Hardware Launch & PR (Month 6+)

**Kickstarter / Indiegogo**
The laser is perfect for crowdfunding. It's visual, demonstrable, and solves a clear problem. A 60-second video of the laser in action, backed by a working app with thousands of users, is a compelling campaign.

Target: $100K raise, 200-300 units pre-sold. This validates demand and funds the first production run.

**Press & Media**
- The Verge, Wired, Engadget: "This $499 laser projects your tile layout onto the wall"
- This Old House, Family Handyman: "We tested the LayIt Laser on a real bathroom remodel"
- Tech press for the AI angle. Home improvement press for the practical angle.

**Trade Shows**
- TISE (The International Surfaces Event) — Jan 2027 in Las Vegas. The tile industry's biggest show.
- CES — The laser is consumer electronics that crosses into construction tech.
- National Hardware Show — Reaches retailers and distributors.

### The Flywheel

```
Users create layouts → Layouts generate branded reports → Reports reach clients →
Clients download app → Users buy laser → Laser videos go viral →
Viral videos drive app installs → More users create more layouts → ...
```

Every user is a distribution channel. Every client report is an ad. Every laser video is a demo. The product markets itself through use.

---

## Competition

**There is no direct competitor combining tile layout + laser projection + AI scanning.**

The closest alternatives:

| Product | What It Does | What It Doesn't Do |
|---------|-------------|-------------------|
| Tile calculators (apps) | Square footage math | No visual layout, no cut tracking, no optimization, no projection |
| Roomsketcher / Planner5D | Room planning in 3D | Not tile-specific, no cut measurements, no real-world projection |
| Bosch GLM laser measure | Measures distances | Doesn't generate layouts, doesn't project patterns |
| LaserTile (academic) | Research prototype | Not a commercial product, no vision alignment, no app |
| Chalk lines (manual) | Marks straight lines on surfaces | One line at a time, requires measuring each mark, no pattern intelligence |

LayIt's moat is the full stack: AI-powered input → intelligent layout engine → precision laser output, protected by three provisional patents. No competitor has more than one layer.

---

## Metrics to Watch

| Metric | Target (Year 1) | Why It Matters |
|--------|-----------------|---------------|
| App installs | 50,000 | Market validation |
| Monthly active users | 15,000 | Retention / product-market fit |
| Pro subscriptions | 2,000 | Revenue ($8K-$10K MRR) |
| AI scans per month | 10,000+ | Engagement depth |
| Client reports generated | 1,000/month | Pro value + distribution channel |
| Laser pre-orders | 500+ | Hardware demand validation |
| Cut tiles tracked | 100,000+ | Feature stickiness |
| UPC database entries | 500+ | Barcode scan reliability |

---

## The Vision

Today, LayIt is an app that plans tile layouts and a laser that projects them.

Tomorrow, it's the operating system for surface installation. Tile. Hardwood. LVP. Pavers. Shingles. Wallpaper. Any material that repeats in a pattern on a surface can be planned, optimized, and projected.

The three patents cover not just tile — they cover *any material geometry extraction from images*, *any room measurement from photos*, and *any pattern projection with vision alignment*. The IP is domain-general by design.

The camera scan patent (Patent 2) is already shared with SIMCO's StageIt retail platform, proving the dual-market applicability. LayIt and StageIt share a technology core but address entirely different markets: construction vs. retail. Two products, one patent portfolio, compounding value.

**LayIt — Every tile in its perfect place.**

*SIMCO Inc. | layitapp@gmail.com | Patent Pending*
