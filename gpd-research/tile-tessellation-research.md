# Tile Tessellation Geometry Research

## Research Question
Derive mathematically exact tessellation geometry for decorative tile patterns used in the LayIt tile layout application. For each pattern, produce Canvas2D-compatible rendering code (bezier curves, vertex coordinates) and Python verification scripts that confirm zero-gap plane coverage.

## Target Patterns (Priority Order)

### 1. Leaf / Teardrop (URGENT - currently broken)
- Double-pointed shape (pointed top AND bottom)
- Fat plump belly at center, smooth S-curve sides
- Tiles interlock in brick-offset rows, alternating 180° rotation
- Real-world reference: marble leaf mosaic sheets (~2" x 3.5" per tile)
- Must produce: exact cubic bezier curves for Canvas2D `bezierCurveTo()`

### 2. Star & Cross (URGENT - currently broken)
- 4-pointed star tile with concave curved sides
- Separate cross tile fills gaps between 4 stars
- Both are individual tile pieces separated by grout
- Real-world reference: cement star & cross tiles (~6" each)
- Must produce: exact star shape + complementary cross shape + grid spacing

### 3. Arabesque / Lantern
- Curved lantern shape with pointed top/bottom, convex shoulders, concave waist
- Staggered rows, alternating 180° rotation
- Must interlock so adjacent tiles' curves complement each other

### 4. Ogee / Provençal
- Gothic arch shape — convex upper curve, concave lower curve
- Staggered rows with 180° alternation
- Adjacent tiles must interlock at shared boundary curves

### 5. Fish Scale / Scallop
- Semicircular dome top, concave narrowing sides to pointed stem
- Rows nest: each tile's dome sits in the gap between two tiles below

### 6. Chevron (not yet implemented)
- V-pattern from rectangular tiles at alternating angles
- Must produce: rotation angles, spacing, and vertex coordinates

## Constraints
- All geometry must be expressed as Canvas2D commands: `moveTo`, `lineTo`, `bezierCurveTo`, `arc`
- Coordinates normalized to half-width (hw) and half-height (hh) from tile center
- Must account for uniform grout gap parameter (g) between all tiles
- Must specify: grid spacing (colFactor, rowFactor), row offset, flip rules
- Each pattern must tile the plane completely (star+cross together, not individually)

## Verification Requirements
- Python script that renders each pattern to PNG and verifies:
  1. No gaps between tiles (complete plane coverage minus grout)
  2. No overlapping tiles
  3. Grout lines are uniform width everywhere
  4. Pattern matches reference images from real tile manufacturers

## Output Format
For each pattern, deliver:
1. LaTeX derivation with mathematical proof of tessellation correctness
2. Python verification script with visual output
3. JavaScript/Canvas2D code block ready to paste into LayIt index.html
4. Spacing parameters: `{ colFactor, rowFactor, oddRowOffsetX, flipOddRows }`
