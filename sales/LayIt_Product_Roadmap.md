# LayIt Laser — Product Roadmap & Revenue Streams

*Last updated: March 15, 2026*

---

## PHASE 1 — Launch Products (Now)

### Hardware
| Product | Price | Margin | Status |
|---------|-------|--------|--------|
| LayIt Laser (Flagship) | $499 | 38-53% | Prototype |
| LayIt Laser Pro (Battery) | $649 | 38-55% | Design complete |

### Software — LayIt App (PWA)

**Free Tier** (included with every unit):
- Full tile layout tool (all patterns, shapes, orientations)
- Wall/floor perimeter drawing + quick rectangle
- Void/niche management
- Cut count + waste % on layout screen
- Manual tile dimension entry
- Save/load projects locally
- Laser projection control + segment navigation
- DXF/SVG/JSON export

**LayIt Pro — $14.99/month**:
- Barcode scanner + photo label tile auto-populate
- Cloud sync across devices (Firebase)
- AI room scan (camera-based, no LiDAR)
- Project sharing (send layouts to clients/crew)
- Job cost tracking + invoicing templates
- Priority support
- Early access to new features

**Revenue math at scale:**
| Units Sold | Pro Conversion | Monthly ARR | Annual ARR | Valuation (15x) |
|-----------|---------------|-------------|------------|-----------------|
| 1,000 | 40% (400 subs) | $5,996 | $71,952 | $1.08M |
| 5,000 | 40% (2,000 subs) | $29,980 | $359,760 | $5.4M |
| 10,000 | 35% (3,500 subs) | $52,465 | $629,580 | $9.4M |
| 50,000 | 30% (15,000 subs) | $224,850 | $2.7M | $40.5M |

*Hardware revenue is on top of this. Subscription ARR valued at 10-20x by investors.*

---

## PHASE 2 — Revenue Channels Beyond Retail

### 1. DIY Rental Program — "LayIt for a Weekend"

**Problem:** DIYers doing one bathroom don't want to buy a $499 tool they'll use once.

**Model:**
- **$49/weekend** (Fri pickup → Mon return) or **$99/week**
- Rent through website, local tool rental shops, or partner with Home Depot/Lowe's rental departments
- Unit comes pre-loaded with tutorial, ships with prepaid return label
- Require credit card hold ($499) for damage/non-return
- Include one month of Pro subscription free with every rental

**Revenue:**
- Each rental unit does ~2 rentals/month = $98-198/month per unit
- 100 rental units in circulation = $9,800-19,800/month
- Unit pays for itself in 3-5 rentals
- Renters who love it → convert to buyers (upsell funnel)

**Partners:**
- Home Depot Tool Rental
- Lowe's Tool Rental
- Sunbelt Rentals
- United Rentals
- Local tile shops (consignment model — they get 20% of rental fee)

### 2. Union & Trade School Licensing

**Problem:** Unions and trade schools train thousands of tile setters annually. They need modern tools in curriculum.

**Model:**
- **Classroom License** — $2,499/year per school
  - 5 LayIt units + unlimited Pro app seats for students
  - Curriculum integration guide
  - Instructor training session (virtual)
  - Student discount code (20% off personal unit at graduation)
- **Union Hall License** — $4,999/year per local
  - 10 LayIt units for member checkout
  - Bulk Pro subscriptions for all members ($5.99/mo per member, billed to union)
  - Co-branded training materials
  - Priority support line

**Target unions:**
- BAC (Bricklayers and Allied Craftworkers) — 75,000+ members
- IUBAC local chapters
- Tile Contractors' Association of America (TCAA)
- National Tile Contractors Association (NTCA)
- INSTALL (International Standards & Training Alliance)

**Revenue:**
- 50 trade schools × $2,499 = $125K/year
- 20 union locals × $4,999 = $100K/year
- 2,000 union members × $5.99/mo = $144K/year ARR
- Total: ~$369K/year from institutional licensing alone

### 3. Contractor Fleet Program — "LayIt for Crews"

**Problem:** A tile company with 5 crews needs 5 units + centralized project management.

**Model:**
- **Fleet pricing:** $399/unit (20% off) for 5+ units
- **Fleet Pro subscription:** $7.99/mo per seat (volume discount)
- **Fleet dashboard:** (web portal)
  - Assign projects to crews
  - Track job progress across all units
  - Centralized tile product database
  - Material ordering integration
  - Time tracking per job

**Revenue:**
- 100 companies × 5 units × $399 = $199,500 hardware
- 500 seats × $7.99/mo = $47,940/year ARR
- Fleet dashboard: $49/mo per company = $58,800/year ARR

### 4. Tile Manufacturer Partnerships

**Problem:** Tile manufacturers want their products specified. LayIt's barcode database is a distribution channel.

**Model:**
- **Featured Listing** in tile database — $500/month per brand
  - Brand's full catalog pre-loaded in app
  - "Recommended by [Brand]" badge on scan
  - Direct link to purchase/sample from scan results
- **Sponsored Patterns** — $1,000 one-time
  - Brand's signature patterns pre-loaded as layout templates
  - "Designed by [Brand]" attribution
- **Data Licensing** — $2,000/month
  - Anonymous usage data: which tiles are most scanned, which patterns most used, regional trends
  - Helps manufacturers with product development and inventory planning

**Target manufacturers:**
- Daltile (largest US manufacturer)
- MSI Surfaces
- Florida Tile
- Marazzi
- American Olean
- Crossville
- Bedrosians

**Revenue:**
- 10 brands × $500/mo featured = $60K/year
- 20 sponsored patterns × $1,000 = $20K one-time
- 5 data licenses × $2,000/mo = $120K/year

### 5. General Contractor / GC Integration

**Problem:** GCs manage multiple subs. They want to see tile progress without visiting the site.

**Model:**
- **GC Portal** — $29/mo
  - View real-time progress of tile sub's LayIt projects
  - Photo documentation auto-generated
  - Material tracking and waste reporting
  - Integrates with Procore, PlanGrid, BuilderTrend
- **Enterprise** — custom pricing for national builders (Toll Brothers, Lennar, etc.)

---

## PHASE 3 — Future Products

### LayIt CutStation (Automated Tile Cutter)

**Concept:** Compact waterjet or diamond CNC that receives cut data directly from the LayIt app. No measuring, no marking, no operator programming.

**Workflow:**
1. App computes all cuts for the layout
2. Cut queue appears on screen: "Tile B7 — 4.25" × 11.5" trapezoid, left notch"
3. User places blank tile in spring-loaded brackets
4. Taps "Cut" — machine executes
5. Walk away, install previous tile, come back to finished cut

**Capabilities:**
- Straight cuts, angles, curves, radius corners
- Plumbing holes (toilet flange, shower valve, supply lines)
- Hex tile slivers that would shatter on a wet saw
- Notches for outlet boxes, niches, trim pieces
- Fits tiles up to 12" × 24" (or larger depending on model)

**Business model:**
- Option A: **License LayIt CutLink software** to existing waterjet/CNC manufacturers
  - They build the hardware, we provide the software brain
  - $50-100 per unit licensing fee + $14.99/mo software subscription
  - Partner with WAZER, Donatoni, Prussiani, or Chinese CNC OEMs
- Option B: **Co-branded product** — "LayIt CutStation powered by [Manufacturer]"
  - $2,999-4,999 retail
  - 30-40% margin on hardware + software subscription
- Option C: **Rental only** — don't sell, rent alongside LayIt Laser
  - $149/week rental
  - Prevents cheap knockoffs, maintains recurring revenue

**Market sizing:**
- 300,000+ tile contractors in US
- Average tile contractor spends $2,000-5,000/year on cutting equipment and blades
- Even 5% penetration = 15,000 units × $3,999 = $60M revenue opportunity

### CutStation Development Roadmap

**Phase 1 — CutLink Protocol (Now, $0 cost)**
Build the software specification that describes cuts in a machine-readable format. The LayIt app already computes every cut for a layout — CutLink formalizes this into a universal protocol that any CNC/waterjet can consume. This is the "USB standard" for tile cutting.

**Phase 2 — Reference Design (With Investment, $200-500K R&D)**
Partner with WAZER, a Chinese OEM, or a domestic CNC shop to build a jobsite-friendly reference prototype to our spec:
- Closed-loop water recycling — small onboard tank (5 gal), filter and recirculate, no garden hose
- Weight target: under 250 lbs with cart (comparable to a loaded miter saw station)
- Fold-flat wheeled cart (like DeWalt DW7440RS table saw stand) — tip back and roll through doorways
- Gurney-style flip-up loading — cart levels with truck bed height for slide-in/slide-out
- Locking casters for stability on subfloor
- 120V standard outlet power (standard jobsite power)
- Pre-loaded garnet cartridges instead of loose bags
- Drain bucket underneath for slurry/waste water
- Cutting bed sized for tiles up to 12" × 24"
- Wireless CutLink connection to LayIt app — zero operator programming
- The killer differentiator: the operator never touches a measuring tape. App sends the cut, machine executes.

**Phase 3 — License & Scale**
- License CutLink protocol to every CNC/waterjet manufacturer who wants access to the LayIt install base
- Hardware manufacturers compete on portability, price, and reliability
- LayIt collects per-unit licensing fee ($50-100) + monthly software subscription ($14.99/mo)
- Co-branded options: "LayIt CutStation powered by [Manufacturer]"
- Rental fleet option for markets where ownership doesn't make sense

### CutVan — Mobile Cutting as a Service

**Concept: "Uber for tile cuts"**

A Sprinter van with a CutStation permanently mounted inside — plumbed water recirculation, garnet storage bins, scrap collection, climate-controlled cutting in any weather. The van operator doesn't lay tile — they're a dedicated mobile fabrication service.

**How it works:**
1. Tile crew on the jobsite uses LayIt app to generate the cut queue for their layout
2. They share the cut file to the CutVan operator via the app
3. Van rolls up, parks out front, backdoors open
4. Operator loads blank tiles, machine executes every cut — curves, notches, flanges, hex slivers
5. Crew never stops setting tile. No walking to the wet saw, no measuring, no marking
6. CutVan moves to the next jobsite. One van can service 3-5 jobs/day in a metro area

**Who operates a CutVan:**
- **Tile companies with multiple crews** — mount it in their own Sprinter, dispatch it between jobsites. Crews never slow down waiting on cuts. Cut in rain, snow, 100°F sun — doesn't matter, you're in a box.
- **Independent CutVan operators** — don't need to be skilled tile setters. Load blanks, machine does the rest. Low skill floor, high throughput.
- **LayIt franchise fleet** — branded "LayIt CutVan" network, nationally scaled.

**Revenue model:**
- CutVan operators charge per cut ($1-3/cut) or per hour ($75-150/hr)
- LayIt sells/leases CutStation units to van operators
- Monthly CutLink software subscription per van ($49-99/mo fleet tier)
- Per-cut transaction fee through the app ($0.10-0.25/cut)
- Franchise licensing fee for "LayIt CutVan" branding

**Franchise economics:**
- Startup: $50-75K (used Sprinter + CutStation + plumbing + branding)
- Operator revenue: $500-1,000/day servicing 3-5 crews
- LayIt collects recurring software + per-cut fees from every van in the network
- National network of CutVans = massive install base locked into LayIt ecosystem

**Why this works:**
- Current tile wet saws ($300-800) only do straight cuts and simple diagonals
- Anything complex (curves, notches, toilet flanges, hex slivers) requires nippers or outsourcing
- A CutVan eliminates ALL of that without any crew needing to own or operate the machine
- The van operator doesn't need tile skills — LayIt software is the brain
- Every CutVan on the road is a rolling billboard for LayIt
- A $3-5K CutStation owned by a crew pays for itself in weeks doing 3+ jobs/month
- A CutVan franchise pays for itself in 2-3 months at full utilization

### LayIt Vision (AI Room Scan)

**Status:** Provisional patent filed, prototype built, calibration data collected.
- Phone camera → depth estimation → room dimensions
- No LiDAR required
- Replaces manual wall measurement entirely

### LayIt Pro+ Hardware

**Potential future SKU ($899-999):**
- Built-in LiDAR sensor (skip phone camera entirely)
- Higher power laser (500mW) for outdoor/bright conditions
- Built-in display (no phone needed for basic operation)
- Integrated CutLink port for direct connection to CutStation

---

## REVENUE SUMMARY — Year 3 Projection

| Stream | Annual Revenue | Type |
|--------|---------------|------|
| Hardware sales (5,000 units avg $550) | $2.75M | One-time |
| App Pro subscriptions (2,000 subs) | $360K | Recurring |
| DIY rentals (100 units) | $120-240K | Recurring |
| Union/trade school licensing | $369K | Recurring |
| Contractor fleet program | $307K | Recurring |
| Tile manufacturer partnerships | $200K | Recurring |
| GC portal | $50K | Recurring |
| **TOTAL** | **$4.1-4.5M** | |
| **Recurring ARR** | **$1.4M+** | |
| **Company valuation (15x ARR + 2x hardware)** | **$27-32M** | |

---

## NOTES
- All projections assume Year 3 (post-launch maturity)
- Hardware margins improve 10-15% at volume (1,000+ units)
- Subscription churn assumed at 5-8% monthly for DIY, 2-3% for contractors
- CutStation revenue not included in Year 3 (Phase 3 product)
- Patent protection covers core technology through 2046 (20-year utility patent term)
