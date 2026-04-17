# UNITED STATES PROVISIONAL PATENT APPLICATION

---

## PROVISIONAL PATENT APPLICATION

> **Filing Notes:**
> - This provisional application establishes a priority date for the AI-based material geometry extraction and tessellation inference system.
> - This is related to but independent from the existing LayIt provisionals: camera room measurement (64/006,336) and laser projection (64/006,343).
> - Filing fee: $65 (micro-entity) as of 2026.
> - This provisional must be converted to a utility application within 12 months of filing.

---

## 1. TITLE OF THE INVENTION

Method and System for Automated Extraction of Material Geometry and Tessellation Parameters from Digital Images Using Computer Vision for Installation Layout Generation and Spatial Optimization

---

## 2. INVENTOR

Sole Inventor: Robert Frederick Sims

---

## 3. CROSS-REFERENCE TO RELATED APPLICATIONS

This application is related to:

(a) U.S. Provisional Application No. 64/006,336, filed March 15, 2026, entitled "Method and System for Automatic Room Geometry Extraction from Monocular Camera Images for Generation of Tile Installation Layouts," the entirety of which is incorporated herein by reference.

(b) U.S. Provisional Application No. 64/006,343, filed March 15, 2026, entitled "System and Method for Real-Time Laser Projection of Tile Installation Patterns with Vision-Based Self-Correcting Alignment," the entirety of which is incorporated herein by reference.

The present invention describes methods and systems for automatically determining the geometric shape, dimensions, and tessellation behavior of individual material units (such as tiles, pavers, panels, shingles, planks, or other modular building materials) from one or more digital images of the material, which geometry data is used to generate installation layout patterns for display in companion software, for projection by the laser system described in the related application (b), within room geometries measured by the system described in the related application (a), or for independent use in spatial optimization applications.

---

## 4. FIELD OF THE INVENTION

The present invention relates generally to computer vision-based systems for automated geometric analysis of modular materials, and more particularly to a method and system for extracting the precise two-dimensional shape geometry, dimensional parameters, and tessellation rules of individual material units from one or more digital photographs or product images, using artificial intelligence models including vision-language models and image segmentation neural networks, to automatically generate machine-usable geometric representations suitable for installation layout computation, laser projection guidance, CNC/laser cutting optimization, spatial packing optimization, or other applications requiring accurate geometric descriptions of repeating modular units.

---

## 5. BACKGROUND OF THE INVENTION

### 5.1 The Material Geometry Problem

Modular building materials — including ceramic tiles, natural stone tiles, porcelain mosaics, glass mosaics, brick pavers, roofing shingles, hardwood planks, vinyl planks, decorative panels, and similar products — are manufactured in thousands of distinct geometric shapes. While simple shapes such as rectangles and squares can be described by two dimensions (width and height), the building materials industry produces an enormous variety of complex shapes including:

(a) Octagons with interstitial dot tiles;
(b) Arabesque and lantern shapes with curved profiles;
(c) Elongated hexagons (picket tiles) with pointed terminations;
(d) Fishscale (fan) shapes with compound curved edges;
(e) Chevron and herringbone parallelograms;
(f) Rhombus shapes that create three-dimensional cube illusions;
(g) Random-width stacked strips (ledger stone, linear glass);
(h) Penny rounds and other circular forms;
(i) Irregular polygons with custom tessellation patterns.

Each of these shapes tessellates differently. A hexagonal tile offsets every other row by half a tile width. An arabesque tile interlocks through complementary curves. A rhombus cube pattern requires three distinct orientations per repeat unit. A stacked ledger panel uses randomized strip widths within a fixed sheet boundary.

### 5.2 Current Methods for Obtaining Material Geometry

**Manual specification.** Currently, when a software application (tile layout planner, laser projection system, CNC cutting optimizer) needs to render or compute layouts for a specific material, a human operator must manually measure the material, determine its geometric shape, identify its tessellation pattern, and encode this information as numeric parameters (vertex coordinates, spacing values, offset rules). This process requires geometric knowledge, measurement tools, and significant time per material type.

**Manufacturer data sheets.** Some manufacturers publish dimensional specifications for their products, but these specifications vary widely in format, completeness, and accessibility. Many list only nominal sheet dimensions without describing individual tile shapes within mosaic sheets. Specifications are scattered across hundreds of manufacturer websites, PDF catalogs, and retailer listings with no standardized format.

**Manual database construction.** Building a comprehensive database of material geometries requires manually researching, measuring, and encoding each product — a process that scales linearly with the number of products and becomes prohibitively expensive as the number of available materials grows (estimated at over 50,000 distinct tile products available through major U.S. retailers alone).

### 5.3 Limitations of Existing Approaches

No existing system automatically extracts the geometric shape, tessellation pattern, and dimensional parameters of a modular material from a photograph or product image. Existing computer vision systems for construction applications focus on:

(a) Detecting placed tiles on surfaces for alignment purposes (as in the related application 64/006,343, which detects tile edges for projection correction but does not determine tile geometry from product images);

(b) Measuring room dimensions from photographs (as in the related application 64/006,336, which extracts room geometry but does not analyze material geometry);

(c) Augmented reality visualization that overlays pre-known textures onto surfaces (which requires the material geometry to already be encoded in a database).

None of these systems address the fundamental problem of automatically determining the geometry of an unknown material from its visual appearance.

### 5.4 Broader Applicability Beyond Building Materials

The problem of extracting geometric shape and tessellation/packing parameters from images of modular units extends beyond building materials to numerous domains:

(a) **Roofing and cladding** — determining shingle or panel geometry for coverage optimization on irregular roof surfaces;

(b) **Textile and quilting** — extracting fabric piece geometry from pattern images for cutting optimization;

(c) **Solar panel installation** — determining panel geometry and optimal tessellation for maximum coverage on irregular roof surfaces;

(d) **CNC and laser cutting** — extracting part geometry from reference images for nesting optimization to minimize material waste;

(e) **Stained glass and decorative fabrication** — extracting individual piece geometry from design images for fabrication planning;

(f) **Packaging and palletizing** — determining object geometry from photographs for spatial packing optimization in containers, trucks, or pallets;

(g) **Agricultural planning** — extracting plot or planting unit geometry from aerial imagery for coverage optimization;

(h) **3D printing** — extracting surface tessellation geometry from reference images for generating printable mesh patterns;

(i) **Modular construction** — determining prefabricated component geometry for assembly planning and spatial optimization.

In all of these domains, the core problem is identical: given an image of a modular unit or repeating pattern, automatically determine the geometric shape, dimensions, and spatial arrangement rules necessary for a machine to compute optimal placement, coverage, cutting, or packing configurations.

### 5.5 Unmet Need

There exists a need for a system that can:

(a) Accept one or more digital images of a modular material (product photograph, catalog image, manufacturer spec sheet, or user-captured photograph of the physical product);

(b) Automatically identify and segment individual material units within the image, distinguishing the material geometry from background, grout lines, packaging, and other non-material elements;

(c) Extract the precise two-dimensional geometric shape of each unique material unit as a machine-usable representation (polygon vertices, parametric curves, or equivalent);

(d) Determine the dimensional parameters of each material unit (width, height, and any shape-specific parameters such as corner clip angle, curve radius, or point angle);

(e) Infer the tessellation or interlocking pattern — how adjacent material units relate spatially, including offset rules, rotation patterns, and multi-shape arrangements;

(f) Generate a complete geometric preset suitable for input to layout computation software, laser projection systems, CNC cutting optimizers, or spatial packing algorithms;

(g) Validate extracted geometry against known manufacturer specifications when available, and improve extraction accuracy over time through accumulated validation data; and

(h) Operate across the full range of material shapes, from simple rectangles to complex curved and multi-shape patterns, without requiring shape-specific programming for each new geometry encountered.

### 5.6 Distinction from Prior Art

The present invention is distinguished from existing systems in several fundamental respects:

(a) **Image-to-geometry extraction, not geometry-to-image rendering.** Existing tile visualization systems (augmented reality apps, layout planners) take known tile geometry and render it onto surfaces. The present invention solves the inverse problem: given an image containing tiles, extract the geometry. This inverse problem requires fundamentally different techniques — shape segmentation, curve fitting, tessellation inference — that have no equivalent in rendering-based systems.

(b) **Material geometry, not room geometry.** The related application 64/006,336 extracts room dimensions from photographs using depth estimation and plane detection. The present invention extracts material unit dimensions from photographs using shape segmentation and geometric analysis. The input, output, techniques, and purpose are entirely different: room measurement determines where materials go; material geometry extraction determines what the materials are.

(c) **Tessellation inference, not pattern matching.** The present invention does not merely identify a tile shape by matching against a known database of shapes. It infers the tessellation rules — how the shape repeats, offsets, and interlocks — from the spatial relationships observed in the image. This enables the system to handle shapes it has never encountered before, including custom or artisanal materials with unique tessellation patterns.

(d) **Cross-reference validation with manufacturer data.** The system uniquely combines AI-based geometry extraction with lookup against manufacturer specification databases, using the manufacturer data to validate and refine the AI extraction. When manufacturer data is available, the system uses it as ground truth; when manufacturer data is unavailable, the system relies on the AI extraction. This hybrid approach achieves higher accuracy than either method alone.

(e) **Domain-general applicability.** Unlike systems designed for a single material type (tile layout planners, shingle calculators, fabric cutting optimizers), the present invention's geometry extraction pipeline is material-agnostic. The same system extracts geometry from tile images, paver images, shingle images, fabric pattern images, or any other modular material, requiring no domain-specific programming beyond the initial vision model prompt.

---

## 6. SUMMARY OF THE INVENTION

The present invention provides a method and system for automatically extracting the geometric shape, dimensional parameters, and tessellation rules of modular material units from one or more digital images, and generating machine-usable geometric representations suitable for layout computation, projection guidance, cutting optimization, or spatial packing.

In a preferred embodiment, the method comprises the following steps:

**Step 1: Image Acquisition.** The system receives one or more digital images containing the material to be analyzed. Image sources include:

(a) Product photographs from manufacturer websites or retailer listings, obtained via web scraping, API access, or manual URL input;

(b) User-captured photographs of physical material samples, taken with a standard smartphone camera;

(c) Manufacturer specification sheets or technical drawings in PDF, PNG, JPEG, or other standard image formats;

(d) Barcode or product identifier lookup that retrieves associated product images from a networked database.

**Step 2: Vision Model Analysis.** Each image is processed by a vision-language artificial intelligence model (such as a large multimodal model capable of analyzing images and producing structured text output). The vision model receives the image along with a structured prompt that instructs it to:

(a) Identify all unique material unit shapes visible in the image;

(b) For each shape, extract the outline as either a polygon (ordered list of vertex coordinates normalized to a unit bounding box) or a set of parametric curves (quadratic or cubic Bezier control points, arc specifications, or equivalent);

(c) Estimate the real-world dimensions of each shape in standard units (inches or millimeters), based on visual cues, known product conventions, and any dimensional annotations visible in the image;

(d) Determine the tessellation pattern — how adjacent units are arranged relative to each other, including: grid type (regular grid, brick offset, herringbone, random), offset magnitude and direction for staggered patterns, rotation angles for rotated arrangements, and the composition of the repeat unit (single shape or multiple shapes);

(e) Identify the repeat unit — the minimal rectangular region that, when tiled, reproduces the full pattern — and specify its dimensions;

(f) For multi-shape patterns (such as octagon-and-dot, or rhombus cube), enumerate all unique shapes and their relative positions, rotations, and scales within the repeat unit;

(g) Output all extracted information as structured data (preferably JSON) conforming to a predefined schema.

**Step 3: Geometric Normalization.** The raw geometry extracted by the vision model is normalized and validated:

(a) Vertex coordinates are normalized to a centered coordinate system with the shape origin at its centroid and maximum extent of 1.0 in each dimension;

(b) Curved shapes represented as Bezier control points are converted to polyline approximations at a configurable resolution for rendering compatibility;

(c) Dimensional estimates are validated against known physical constraints (minimum grout spacing, standard tile size ranges, mosaic sheet dimensions);

(d) Tessellation rules are validated by computing the arrangement over a sample area and verifying that adjacent units do not overlap and that gaps conform to expected grout spacing.

**Step 4: Cross-Reference Validation (Optional).** When a product identifier (barcode, SKU, model number, or manufacturer part number) is available:

(a) The system queries a manufacturer specification database for the product's published dimensions;

(b) If manufacturer data is found, the AI-extracted dimensions are compared against the published specifications;

(c) Discrepancies exceeding a tolerance threshold trigger a confidence flag, and the manufacturer specification is used as the authoritative source for dimensions while the AI-extracted shape geometry is retained for the outline;

(d) The validation result (AI extraction accuracy relative to manufacturer data) is stored and used to improve future extractions through prompt refinement and confidence calibration.

**Step 5: Preset Generation.** The validated geometry is encoded as a machine-usable preset containing:

(a) Shape type classification (polygon, curved, compound/multi-shape);

(b) Vertex coordinates or parametric curve specifications for each unique shape;

(c) Real-world dimensions (width, height) for each shape;

(d) Tessellation type (grid, brick, herringbone, random-stack, multi-shape);

(e) Repeat unit dimensions and composition;

(f) Grout spacing (actual or estimated);

(g) Any shape-specific parameters (corner clip ratio for octagons, point angle for elongated hexagons, curve control points for arabesques);

(h) Confidence score for each extracted parameter;

(i) Source metadata (image URL, product identifier, manufacturer, extraction timestamp).

**Step 6: Layout Integration.** The generated preset is made available to downstream systems:

(a) A tile layout computation engine that uses the geometry to render accurate installation layouts;

(b) A laser projection system that uses the geometry to project material outlines onto work surfaces at 1:1 scale;

(c) A CNC or laser cutting system that uses the geometry to compute optimal nesting and cutting paths;

(d) A spatial packing algorithm that uses the geometry to compute optimal placement configurations;

(e) A cloud database that stores validated presets for retrieval by other users via barcode scan or product search.

### Key Advantages Over Prior Art

1. **Automated geometry extraction from images.** No existing system automatically determines material geometry from photographs. The present invention eliminates the need for manual measurement and encoding of each material type.

2. **Shape-agnostic operation.** The system handles any material geometry — from simple rectangles to complex curved multi-shape patterns — without requiring shape-specific programming. New shapes are handled by the vision model's general-purpose geometric reasoning capability.

3. **Tessellation inference.** The system determines not only what the shape is, but how it repeats. This tessellation inference is critical for layout computation and is not addressed by any known prior system.

4. **Hybrid AI + manufacturer validation.** The combination of AI-based extraction with manufacturer database cross-referencing produces higher accuracy than either method alone, and creates a self-improving system where each validation improves future extractions.

5. **Domain-general applicability.** The same extraction pipeline applies to tile, stone, brick, roofing, flooring, textile, packaging, and any other modular material, enabling a single system to serve multiple industries.

6. **Scalability.** The system can process thousands of product images autonomously, enabling rapid construction of comprehensive material geometry databases that would be prohibitively expensive to build manually.

7. **Integration with complementary systems.** The extracted geometry feeds directly into room measurement systems (related application 64/006,336), laser projection systems (related application 64/006,343), and other downstream applications, completing an end-to-end workflow from material identification to installed pattern.

---

## 7. DETAILED DESCRIPTION OF PREFERRED EMBODIMENTS

### 7.1 System Architecture

The material geometry extraction system comprises:

(a) An image acquisition module that receives digital images from one or more sources (web URLs, local file system, camera capture, barcode-triggered database lookup);

(b) A vision-language AI model (executing on a cloud server or locally on a computing device with sufficient processing capability) that analyzes images and produces structured geometric descriptions;

(c) A geometry normalization module that validates, normalizes, and formats the raw AI output into standardized geometric representations;

(d) A manufacturer cross-reference database containing published product specifications indexed by product identifier (barcode, SKU, model number);

(e) A preset storage system (local database, cloud database, or both) that stores validated geometric presets for retrieval by downstream applications;

(f) One or more downstream application interfaces for transmitting geometry data to layout engines, projection systems, cutting optimizers, or packing algorithms.

### 7.2 Image Analysis Pipeline

The image analysis pipeline operates as follows:

**Stage 1 — Image Preprocessing.** The input image is preprocessed to improve analysis quality:

(a) Resolution normalization — images are scaled to a target resolution (preferably 800-1200 pixels on the longest edge) that balances detail retention with processing efficiency;

(b) Color normalization — white balance and exposure are adjusted to ensure consistent material appearance across varying photography conditions;

(c) Perspective correction — if the image shows significant perspective distortion (material photographed at an oblique angle), keystone correction is applied using detected straight edges in the image;

(d) Background isolation — for product photographs with non-material backgrounds, the material sheet or tile is segmented from the background using contrast-based or AI-based segmentation.

**Stage 2 — Vision Model Geometry Extraction.** The preprocessed image is submitted to a vision-language AI model with a structured geometry extraction prompt. The prompt instructs the model to:

(a) Identify the repeating pattern visible in the image;

(b) Enumerate all unique shapes present in the pattern;

(c) For each shape, provide the outline as normalized vertex coordinates (for polygonal shapes) or parametric curve control points (for curved shapes);

(d) Specify the tessellation type and parameters;

(e) Estimate real-world dimensions;

(f) Return all data as structured JSON.

The prompt includes examples of expected output format for common shape types (hexagons, rectangles, octagons, arabesques) to guide the model toward consistent output formatting.

**Stage 3 — Geometric Validation.** The AI-extracted geometry is validated:

(a) **Closure check** — polygon vertices are verified to form a closed shape (last vertex connects to first vertex within tolerance);

(b) **Self-intersection check** — polygon edges are tested for self-intersection, which would indicate an extraction error;

(c) **Symmetry detection** — the extracted shape is analyzed for expected symmetries (most building materials have at least bilateral symmetry), and the vertex coordinates are refined to enforce detected symmetries;

(d) **Dimension plausibility** — estimated dimensions are compared against plausible ranges for the material type (e.g., individual mosaic sub-tiles are typically 0.5-4 inches, sheet mosaics are typically 10-13 inches);

(e) **Tessellation validation** — the extracted tessellation pattern is computed over a sample area (e.g., 5x5 repeat units) and the result is checked for overlaps, gaps, and visual consistency with the source image.

**Stage 4 — Cross-Reference Validation.** When a product identifier is available:

(a) The system queries the manufacturer database for published specifications;

(b) Published dimensions (nominal width, nominal height, actual width, actual height) are compared against AI-extracted dimensions;

(c) If the published specifications include shape information (e.g., "2-inch hexagon"), this is compared against the AI-extracted shape classification;

(d) Discrepancies are logged and used to compute a confidence score;

(e) For dimension discrepancies exceeding 10%, the manufacturer specification is preferred and the AI extraction is flagged for review;

(f) The validation outcome (match/mismatch, discrepancy magnitude) is stored for use in improving future extractions.

**Stage 5 — Preset Generation and Storage.** The validated geometry is encoded as a preset and stored:

(a) The preset includes all geometric data, dimensional data, tessellation rules, confidence scores, and source metadata;

(b) The preset is stored in a local database on the device and optionally synchronized to a cloud database;

(c) Cloud-stored presets are indexed by product identifier (barcode, SKU) and by geometric characteristics (shape type, approximate dimensions) to enable retrieval by barcode scan or visual similarity search;

(d) Presets that pass cross-reference validation with high confidence are marked as "verified" and made available to all users of the system;

(e) Presets extracted solely by AI (without cross-reference validation) are marked as "AI-extracted" with their confidence score, and may be subject to manual review before being made available to other users.

### 7.3 Handling Complex and Multi-Shape Patterns

Many building materials comprise multiple distinct shapes arranged in a repeating pattern. The system handles these multi-shape patterns as follows:

**Octagon-and-dot patterns:**
(a) The system identifies two shapes: a large octagon and a small square "dot";
(b) The repeat unit is one octagon plus one dot, with the dot positioned at the gap between four adjacent octagons;
(c) Both shapes are stored in the preset with their relative positions within the repeat unit.

**Rhombus cube (3D illusion) patterns:**
(a) The system identifies three rhombus (parallelogram) shapes at 120-degree rotations, creating a hexagonal repeat unit;
(b) Each rhombus is stored with its rotation angle relative to the repeat unit origin;
(c) The tessellation is specified as a hexagonal grid with three sub-tiles per repeat unit.

**Stacked ledger (random-width strip) patterns:**
(a) The system identifies a single shape type (rectangle) used at multiple widths;
(b) The repeat unit encompasses the full sheet panel (typically 6" x 24") and contains multiple rectangles of varying widths;
(c) Each rectangle's width, height, and position within the repeat unit is stored;
(d) The tessellation is specified as "random-stack" with the full sheet as the repeating element.

**Arabesque and other curved patterns:**
(a) The system extracts the curved outline as a series of quadratic or cubic Bezier curve segments;
(b) Each curve segment is defined by its start point, end point, and one or two control points;
(c) The tessellation rules specify how adjacent curved shapes interlock (the convex portion of one shape nests into the concave portion of the adjacent shape);
(d) For rendering and hit-testing purposes, curved shapes are also approximated as polylines at a configurable resolution.

### 7.4 Incremental Learning and Accuracy Improvement

The system improves its extraction accuracy over time through several mechanisms:

(a) **Validation feedback loop.** Each time an AI extraction is validated against manufacturer data, the discrepancy (if any) is stored. Accumulated discrepancy data is used to refine the extraction prompt — for example, if the system consistently overestimates hexagon height by 5%, a correction factor is incorporated into the prompt or post-processing.

(b) **Shape library accumulation.** As the system extracts and validates geometries for increasing numbers of products, it builds a library of known shapes. When a new product image is processed, the AI extraction is compared against the shape library to identify similar shapes, and the validated parameters of the closest match are used to constrain and refine the new extraction.

(c) **User correction integration.** When a user identifies an extraction error (e.g., a rendered layout that visibly does not match the physical material), the user's correction is stored and used to refine the geometry for that product and similar products.

(d) **Multi-source fusion.** For products with images available from multiple sources (manufacturer website, retailer listing, user photograph), the system extracts geometry from each image independently and computes a consensus geometry that is more accurate than any single extraction.

### 7.5 Downstream Application Integration

The extracted geometry integrates with downstream systems as follows:

**Tile layout computation:** The geometry preset is loaded into a layout engine that computes full installation layouts including pattern placement, cut tile identification, waste optimization, and material quantity estimation. The layout engine uses the vertex coordinates to draw accurate tile shapes on the layout diagram and the tessellation rules to determine spacing and offset patterns.

**Laser projection:** The geometry preset is transmitted to a laser projection system (as described in related application 64/006,343) which uses the vertex coordinates to compute galvanometer scan paths for projecting the material outlines onto work surfaces at 1:1 scale. Complex shapes (curves, multi-point polygons) are approximated as polyline segments at a resolution matched to the galvanometer's positioning accuracy.

**CNC/laser cutting optimization:** The geometry preset is used by a nesting algorithm that arranges material pieces on a stock sheet to minimize waste. The vertex coordinates define the cutting paths, and the tessellation rules inform the nesting algorithm about which orientations and arrangements are valid.

**Spatial packing:** The geometry preset is used by a packing algorithm that arranges three-dimensional objects (using the 2D geometry as the base footprint) into containers for shipping, storage, or installation optimization.

### 7.6 Barcode-Triggered Automated Extraction Pipeline

In a preferred embodiment for building material applications, the geometry extraction is triggered by barcode scanning:

(a) A user scans a product barcode using a mobile device camera;

(b) The system looks up the barcode in the manufacturer cross-reference database;

(c) If a validated preset exists for the product, it is returned immediately;

(d) If no preset exists, the system retrieves product images from the associated retailer or manufacturer product page;

(e) The product images are processed through the geometry extraction pipeline;

(f) The extracted geometry is presented to the user with a confidence indication;

(g) If the user confirms the extraction is correct (by visual comparison with the physical product), the preset is marked as user-validated and added to the shared database;

(h) If the user indicates the extraction is incorrect, the user may submit a photograph of the physical product for manual review and correction.

This barcode-triggered pipeline enables the system to continuously expand its material database as users scan new products, creating a network effect where each user's scan potentially benefits all future users.

---

## 8. CLAIMS

**Claim 1.** A method for automatically extracting geometric shape parameters of a modular material unit from a digital image, the method comprising:
(a) receiving a digital image containing one or more modular material units arranged in a repeating pattern;
(b) processing the digital image using a vision-language artificial intelligence model to identify individual material unit shapes within the image and extract for each identified shape a geometric representation comprising an ordered set of boundary coordinates defining the shape outline;
(c) determining tessellation parameters from the spatial relationships between material units observed in the image, the tessellation parameters comprising at least a repeat unit specification and an offset or rotation rule for adjacent units;
(d) normalizing the extracted boundary coordinates to a standardized coordinate system; and
(e) generating a machine-usable geometric preset comprising the normalized boundary coordinates, estimated real-world dimensions, and tessellation parameters.

**Claim 2.** The method of claim 1, wherein the geometric representation comprises polygon vertex coordinates for polygonal shapes and parametric curve control points for curved shapes, and wherein the method further comprises converting parametric curves to polyline approximations at a configurable resolution.

**Claim 3.** The method of claim 1, wherein the vision-language artificial intelligence model receives a structured prompt instructing it to identify shape names, extract vertex coordinates normalized to a unit bounding box, determine tessellation type, estimate real-world dimensions, and output all extracted information as structured data conforming to a predefined schema.

**Claim 4.** The method of claim 1, further comprising:
(a) receiving a product identifier associated with the modular material unit;
(b) querying a manufacturer specification database using the product identifier;
(c) comparing the AI-extracted dimensions against manufacturer-published dimensions; and
(d) when the manufacturer-published dimensions are available, using the manufacturer dimensions as authoritative while retaining the AI-extracted shape geometry for the boundary outline.

**Claim 5.** The method of claim 4, further comprising storing the comparison result as validation data, and using accumulated validation data to improve the accuracy of future geometry extractions by refining extraction prompts or applying systematic correction factors.

**Claim 6.** The method of claim 1, wherein the digital image contains a multi-shape pattern comprising two or more geometrically distinct material unit shapes arranged in an interlocking configuration, and wherein the method further comprises:
(a) identifying each unique shape within the pattern;
(b) extracting boundary coordinates for each unique shape;
(c) determining the relative position, rotation, and scale of each shape within a repeat unit; and
(d) encoding the multi-shape arrangement in the geometric preset.

**Claim 7.** The method of claim 1, wherein the modular material unit has curved boundaries, and wherein extracting the geometric representation comprises determining quadratic or cubic Bezier curve control points that approximate the curved boundary, the control points being determined by the vision-language AI model from the visual curvature observed in the image.

**Claim 8.** The method of claim 1, further comprising validating the extracted geometry by:
(a) computing a tessellated arrangement of the extracted shape over a sample area using the determined tessellation parameters;
(b) verifying that adjacent material units in the computed arrangement do not overlap; and
(c) verifying that gaps between adjacent material units conform to an expected spacing range.

**Claim 9.** The method of claim 1, further comprising transmitting the geometric preset to a tile layout computation engine that renders an installation layout diagram using the extracted boundary coordinates and tessellation parameters, the layout diagram showing the material units arranged on a work surface with computed cut dimensions for partial units at boundaries.

**Claim 10.** The method of claim 1, further comprising transmitting the geometric preset to a laser projection system that uses the boundary coordinates to compute galvanometer scan paths for projecting the material unit outlines onto a physical work surface at 1:1 scale.

**Claim 11.** The method of claim 1, further comprising transmitting the geometric preset to a cutting optimization system that uses the boundary coordinates to compute optimal nesting arrangements of material pieces on stock sheets to minimize waste.

**Claim 12.** The method of claim 1, further comprising transmitting the geometric preset to a spatial packing algorithm that uses the geometric shape to compute optimal placement configurations for objects in a container.

**Claim 13.** A method for expanding a material geometry database using barcode-triggered automated extraction, the method comprising:
(a) scanning a product barcode using a mobile device camera;
(b) determining that no validated geometric preset exists in a database for the scanned product;
(c) retrieving one or more product images associated with the scanned barcode from a networked product information source;
(d) processing the retrieved product images using a vision-language artificial intelligence model to extract geometric shape parameters and tessellation rules;
(e) presenting the extracted geometry to the user for visual confirmation; and
(f) upon user confirmation, storing the validated geometric preset in the database, indexed by the scanned barcode, for retrieval by subsequent users who scan the same barcode.

**Claim 14.** The method of claim 13, wherein when the user indicates the extracted geometry is incorrect, the method further comprises receiving a user-captured photograph of the physical material and queuing the photograph for manual geometry extraction and validation.

**Claim 15.** A system for automated material geometry extraction, the system comprising:
(a) an image acquisition module configured to receive digital images from web URLs, local file systems, camera capture, or barcode-triggered database lookups;
(b) a vision-language AI model configured to analyze received images and produce structured geometric descriptions including boundary coordinates, dimensions, and tessellation parameters for material units identified in the images;
(c) a geometry normalization module configured to validate and normalize the AI-produced geometric descriptions;
(d) a preset storage module configured to store validated geometric presets indexed by product identifier and geometric characteristics; and
(e) one or more downstream application interfaces for transmitting geometric presets to layout computation engines, laser projection systems, cutting optimization systems, or spatial packing algorithms.

**Claim 16.** The system of claim 15, further comprising a manufacturer cross-reference database containing published product specifications indexed by product identifier, wherein the geometry normalization module is further configured to validate AI-extracted dimensions against manufacturer-published dimensions and to prefer manufacturer dimensions when available.

**Claim 17.** The system of claim 15, wherein the preset storage module synchronizes geometric presets to a cloud database, and wherein presets validated by one user are made available to all users of the system, creating a collaboratively expanding material geometry database.

**Claim 18.** The method of claim 1, wherein the modular material units comprise one or more of: ceramic tiles, porcelain tiles, natural stone tiles, glass tiles, mosaic tiles, brick pavers, concrete pavers, roofing shingles, metal roofing panels, hardwood flooring planks, vinyl flooring planks, decorative wall panels, architectural cladding panels, fabric pieces for quilting or garment construction, solar panels, or packaged goods for spatial optimization.

**Claim 19.** The method of claim 1, wherein the method further comprises:
(a) analyzing the shape symmetry of the extracted boundary coordinates;
(b) detecting one or more axes of symmetry; and
(c) refining the boundary coordinates to enforce the detected symmetry, thereby correcting asymmetric extraction errors introduced by perspective distortion or AI model imprecision.

**Claim 20.** The method of claim 1, wherein determining tessellation parameters comprises inferring one or more of:
(a) a grid offset pattern wherein alternating rows or columns of material units are displaced by a fraction of the unit width or height;
(b) a rotation pattern wherein adjacent material units are rotated by a fixed angle;
(c) a multi-shape interlocking pattern wherein two or more geometrically distinct shapes fit together without gaps;
(d) a random-variation pattern wherein material units of varying dimensions are arranged within a fixed repeat unit boundary; and
(e) a nesting pattern wherein convex regions of one material unit fit into concave regions of an adjacent unit.

**Claim 21.** The method of claim 1, further comprising:
(a) receiving from a user a digital image of a physical material sample captured by a smartphone camera;
(b) extracting geometric shape parameters from the user-captured image;
(c) comparing the extracted shape against a library of previously extracted and validated shapes;
(d) if a match is found in the shape library, applying the validated dimensional parameters of the matched shape to the current extraction; and
(e) if no match is found, storing the newly extracted geometry as a candidate shape for future validation.

**Claim 22.** The method of claim 1, wherein processing the digital image using a vision-language artificial intelligence model comprises:
(a) submitting the image to the model with a structured prompt specifying the expected output format;
(b) receiving from the model a structured data response containing geometric descriptions;
(c) parsing the structured data response to extract boundary coordinates, dimensions, and tessellation parameters; and
(d) handling extraction failures by requesting re-analysis with a modified prompt that provides additional guidance based on the failure mode.

---

## 9. ABSTRACT

A method and system for automatically extracting the geometric shape, dimensional parameters, and tessellation rules of modular material units from digital images using vision-language artificial intelligence models. The system receives a digital image containing one or more material units (such as tiles, pavers, shingles, panels, or other modular building materials) arranged in a repeating pattern, processes the image through an AI model that identifies individual shapes and extracts boundary coordinates as polygon vertices or parametric curve control points, infers tessellation parameters including repeat unit dimensions and offset/rotation rules, and generates machine-usable geometric presets. The system optionally validates extracted geometry against manufacturer specification databases, with discrepancies used to improve future extraction accuracy. Validated presets integrate with downstream layout computation engines, laser projection systems, CNC cutting optimizers, and spatial packing algorithms. A barcode-triggered extraction pipeline enables continuous database expansion as users scan new products, with validated presets shared across all users. The system handles complex geometries including curved shapes (arabesque, fishscale), multi-shape patterns (octagon-and-dot, rhombus cube), and random-variation patterns (stacked ledger) without shape-specific programming. Applications extend beyond building materials to roofing, textiles, solar installation, packaging, 3D printing, and other domains requiring automated geometric analysis of modular units.

---

## FILING CHECKLIST

- [ ] Review all claims for proper antecedent basis
- [ ] Verify inventor name matches USPTO account
- [ ] Prepare filing fee payment ($65 micro-entity)
- [ ] File via USPTO Patent Center (patentcenter.uspto.gov)
- [ ] Select "Provisional" application type
- [ ] Upload this document as the specification
- [ ] Record application number and confirmation number
- [ ] Set calendar reminder for 12-month conversion deadline
