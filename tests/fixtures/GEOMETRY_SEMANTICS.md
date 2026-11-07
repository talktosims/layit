# LayIt layout export semantics (app geometryRevision 1.1-patent-7.2)

Authoritative generator: `talktosims/layit` commit `998142ff3ee360a8cd055e2d834be891035298d0` on branch `cursor/layit-app-audit-fixes-1c7b`.
The running page is `index.html`. Headless Chrome produced the `.layit` files in this folder. That is not an iOS or WKWebView run.

Hub commits `971473c`, `1f20960`, and `d4dac01` (PRs 1 and 2) were not readable from this environment (GitHub 404 on the private hub). The notes below use the in-repo patent, the in-repo WebSocket protocol, measurements of this app, and the parent’s description of the compiler.

## What the compiler should do with these files

`compiler.doNotApplyLegacyCompensation` is true.

- Clip the supplied `tiles[].verts` to the wall. Do not rebuild the tile shape from width, height, and grout.
- Do not apply the legacy hub compensation. That path was for older exports that were already wrong.

Those older exports, measured on this app before the fix and reported from hub snapshots, were:

| Case | Old buggy export | This 1.1 file |
|---|---|---|
| 12 in square, grout 1/8 in | body 11.875 in, joint 0.250 in | body 12 in, joint 0.125 in, center pitch 12.125 in |
| Pointy hex width 10 in | outline about half of 10 in, column step `0.75*width+grout` | outline width 10 in, column step `width+grout`, row step `0.75*height+grout` |

Applying that old fix to a 1.1 file would double-compensate.

`isCut: true` means the full outline crosses the wall or a void. The vertices are still the full body. Protocol section 8 in `build/LayIt_WebSocket_Protocol.md` said cut vertices were already clipped. This file does not pre-clip. One compiler clip is the cut.

## Coordinate system

- Units: inches.
- Origin: bottom-left of the wall.
- +x to the right, +y up.
- The on-screen canvas is y-down from the top-left. Export flips y with `wallY = flipH - fromTop`.
- Preview stroke and `tiles[].verts` are the same polygon after that flip. Checked in Chrome.
- Stagger matches the preview and the 2026-11-07 cross-system contract: odd rows (pointy hex, brick) and odd columns (flat hex, herringbone). Patent 7.2.1 prose says even. `CROSS_SYSTEM_INTERFACES.md` at hub commit `1f20960` locks the odd shift. This app does not flip saved layouts to even.

## Patent 7.2 rules this file uses

Square and rectangle: body is the actual tile size. Center spacing is size + grout, once. Nominal mode stores `actual = nominal - grout` and then spaces that actual size plus one grout. A nominal 12 in tile with 1/8 in grout is an 11.875 in body and a 0.125 in joint, pitch 12 in. It is not an 11.875 in body with a 0.250 in joint.

The 1f20960 contract’s locked hex case is pointy 10 by 10 inches, grout 1/8 inch: width extent 10, column step 10.125, row step 7.625, shoulders at ±width/2. That file is `hex-pointy-10x10-grout-eighth.layit`. The regular-hex file is a second case, not that lock.

Pointy hex vertices in the file use y-up. The patent list writes the top point as `cy - height/2` because that list is y-down. Here the top point is `centerY + height/2`. Width, shoulder x, and both steps still match `pointyHexContract`.

Pointy hex, width flat-to-flat `tw`, height point-to-point `th`:

```
(cx, cy - th/2), (cx + tw/2, cy - th/4), (cx + tw/2, cy + th/4),
(cx, cy + th/2), (cx - tw/2, cy + th/4), (cx - tw/2, cy - th/4)
```

`colSp = tw + grout`, `rowSp = th * 0.75 + grout`. In the file, y is up, so the point that was “top” on screen has the larger y.

Flat hex uses the patent spacing `colSp = th * 0.75 + grout`, `rowSp = tw + grout`, with the preview’s swapped vertex formula.

Herringbone uses the patent diagonal pitch of the full tile and does not add grout again. The body is the full rotated rectangle. The old inset-by-grout stroke is gone so the stroke matches the file.

## Full layout

`requirement` is `F1-full-layout`. `tiles[]` is every tile that meets the wall. It is not one edge and it is not only the current projection segment. F8 edge and tile modes are extras. They do not replace this file.

`hardwareCompile` is false, `simulationOnly` is true, and `laser` is `"off"`. The download does not connect to hardware.

## Mosaic, chosen in the open

The 1f20960 contract says the screen draws sub-tiles and the old export drew a sheet, and that the app has to say which polygons are in the file. This file contains sheet outlines only. They are not the sub-tile grout pattern. The compiler clips those sheet polygons and does not invent the piece joints. The interactive preview still draws the pieces. Sheet body equals the sheet size. The gap between sheet centers is `subGr`.

`hardwareCompile`, `hardwareReadyArtifact`, and purchase authority stay false and $0. The model numbers below are simulations from hub commit `1f20960`, not hardware proof.

## Projection notes that are not measurements from this app

Patent 7.4’s example repeats every polygon in a segment at about 0.7–2 Hz. “Static” means the lines stay fixed on the wall, not that the scan is 30 Hz.

Patent ±20° optics fit a 36 in field at 6 ft. F3 does not pin 36 in to 3 ft.

The two-mirror model needs a full 2D command map. Homography-only is not the whole correction.

The engineering review’s smooth simulated model, including 12 LSB bow, is about 0.013 in on a 13×13 grid. That is a simulation, not a held-out measurement, and this app did not invent measured data. Hardware acceptance remains held-out error ≤ 1/64 in and three-visit repeat ≤ 1/32 in.

## Files

- `square-12in-grout-eighth.layit` — 48×36 in wall, actual 12×12 in, grout 1/8 in, origin inset 6.0625 in from the top-left.
- `hex-pointy-10in-regular.layit` — pointy regular hex, flat-to-flat 10 in, grout 1/8 in.
- `herringbone-4x8-grout-eighth.layit` — 4×8 in herringbone, grout stored but not added to the patent pitch.

Fish-scale outlines can exceed the protocol’s 8-vertex limit. `limits.exceedsProtocolVertexLimit` is set when that happens. Vertices are not dropped.

## Saved projects

This change does not rewrite project JSON and does not bump the local bootstrap seed (`2026-04-18f`), so opening the new page does not wipe existing projects. Stored width, height, grout, pattern, and `oxInches` / `oyInches` stay as saved. Stagger parity stays odd-row / odd-column. It is not flipped to the patent’s “even” wording.

Reopening an old project does change the picture: the same stored 12 inch tile is drawn at 12 inches with a 0.125 inch joint, not at 11.875 inches with a 0.250 inch joint. That is the bugfix, not a second copy of the dimensions in the save file.

## Fixture hashes

SHA-256 of the `.layit` bytes is in `SHA256SUMS.txt` inside the review zip. Geometry code started at `998142ff3ee360a8cd055e2d834be891035298d0`. Later commits on this branch only add the safety flags and this note. Vertex formulas are unchanged.

- `square-12in-grout-eighth.layit` — 48×36 in wall, actual 12×12, grout 1/8. Contract: body 12, joint 0.125, pitch 12.125.
- `hex-pointy-10x10-grout-eighth.layit` — the 1f20960 lock. Width 10, height 10, grout 1/8. Column step 10.125, row step 7.625.
- `hex-pointy-10in-regular.layit` — regular pointy hex, flat-to-flat 10 in, height `10 * 2 / sqrt(3)`.
- `herringbone-4x8-grout-eighth.layit` — patent diagonal pitch, full rotated body, grout not added again.
- `square-voids-multi.layit` — same 12 in square room, five cutouts entered through Add Cutout. SHA-256 `51c69676e3cec76d663dfaab5244178d9a25aae57d7becfdd4a31cc59a0c0941`.
- `square-12in-entered-as-cm.layit` — the user typed 121.92 cm by 91.44 cm and a 30.48 cm tile. SHA-256 `6c2bd142c50bcdd138c26ed63655c5bb455bd42356bfde95d08a060247c93f9c`, the same bytes as `square-12in-grout-eighth.layit`.
- `mosaic-sheet-12-square-pieces.layit` — 12 in sheets, 2 in square pieces, 1/8 in piece grout. SHA-256 `1bb5710bc887a53b1c306645673894735ef5c0147e8cd6b0ebfdf8e808b402cb`.

## Voids

Cutout X and Y are the center, measured from the left and bottom edges. The file stores the lower-left corner: `x = centerX - width/2`, `y = centerY - height/2`, y up. Overlapping cutouts are kept as separate rectangles. They are not rejected and not merged. A zero width is rejected and is absent from the file.

`square-voids-multi.layit` was produced by Add Cutout, then `buildLayItPattern`:

| Label | Center in, size | Stored lower-left |
|---|---|---|
| Inside | (24, 18), 6×4 | (21, 16) |
| CrossLeft | (2, 18), 8×6 | (−2, 15), crosses the left wall |
| OverlapInside | (25, 18), 6×4 | (22, 16), overlaps Inside |
| TouchLeftEdge | (3, 10), 6×4 | (0, 8), left edge on the wall |
| CoversTile | (6.5, 30), 13×14 | (0, 23) |

Zero-width was refused. The file has 5 voids, 11 tiles, 10 with `isCut`. One tile is missing because every vertex is inside CoversTile. Other voids do not keep that tile in the list. Tile outlines are still the full 12 in body. The compiler clips them against each void.

## Mosaic sheet file and screen pieces

`mosaic-sheet-12-square-pieces.layit` has 4-vertex sheet rectangles, 12 by 12 in, center pitch 12.125 in. `tile.mosaicFile` is `sheet-outlines`. The screen, measured in the same session, drew 2 in pieces with a 0.125 in gap, which is one `subGr`, not two. The file does not contain those piece polygons.

## Centimeter roundtrip

121.92 cm by 91.44 cm is 48 in by 36 in. The tile field showed 30.48 cm and `readLengthInputValue` returned 12 in. The exported file is inches and matches the inch square fixture byte for byte.
