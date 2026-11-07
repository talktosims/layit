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
- Stagger matches the preview: odd rows (pointy hex, brick) and odd columns (flat hex, herringbone). Patent 7.2.1 text says even. The file follows the preview so the picture and the file stay aligned. Do not flip parity in the compiler.

## Patent 7.2 rules this file uses

Square and rectangle: body is the actual tile size. Center spacing is size + grout, once. Nominal mode stores `actual = nominal - grout` and then spaces that actual size plus one grout. A nominal 12 in tile with 1/8 in grout is an 11.875 in body and a 0.125 in joint, pitch 12 in. It is not an 11.875 in body with a 0.250 in joint.

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

## Mosaic, left unresolved

Interactive preview draws the sub-tile field. This file, like projector mode, writes sheet outlines. Sheet body equals the sheet size. The gap between sheet centers is `subGr`. That split is the current product behavior. It was not changed.

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
