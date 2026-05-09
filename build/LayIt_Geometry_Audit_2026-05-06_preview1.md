# LayIt Geometry Audit

Manifest: /Users/Sims/Desktop/expandit/products/layit/manifest.json
Product: LayIt Laser

## Summary

- Components: 21
- Procedural primitives: 12
- GLB models: 9
- Missing model_accuracy: 0
- Missing source_refs: 0
- Footprint overlaps found: 24
- Missing connection endpoints: 0

## Accuracy Counts

- estimated_package_model: 6
- logical_placeholder: 5
- photo_only_placeholder: 10

## Low-Trust Components

- Phase 1 12V_IN: logical_placeholder (primitive placeholder)
- Phase 1 U1: photo_only_placeholder (primitive placeholder)
- Phase 1 GALVO_PSU: photo_only_placeholder (primitive placeholder)
- Phase 2 U3: photo_only_placeholder (primitive placeholder)
- Phase 2 U4: estimated_package_model (model not yet source-verified)
- Phase 2 C10: estimated_package_model (model not yet source-verified)
- Phase 3 U5: estimated_package_model (model not yet source-verified)
- Phase 3 VREF: logical_placeholder (primitive placeholder)
- Phase 3 R_XY: logical_placeholder (model not yet source-verified)
- Phase 3 C_ANALOG: estimated_package_model (model not yet source-verified)
- Phase 4 GALVO_DRV: photo_only_placeholder (primitive placeholder)
- Phase 4 GALVOS: photo_only_placeholder (primitive placeholder)
- Phase 5 TEST_LASER: photo_only_placeholder (primitive placeholder)
- Phase 5 BEAM_STOP: logical_placeholder (primitive placeholder)
- Phase 6 Q1: estimated_package_model (model not yet source-verified)
- Phase 6 R9/R10/R16: logical_placeholder (model not yet source-verified)
- Phase 6 SW3: estimated_package_model (model not yet source-verified)
- Phase 6 KEY: photo_only_placeholder (primitive placeholder)
- Phase 6 LASER: photo_only_placeholder (primitive placeholder)
- Phase 7 CAM: photo_only_placeholder (model not yet source-verified)
- Phase 7 IMU: photo_only_placeholder (primitive placeholder)

## Footprint Overlaps

- 12V_IN vs U1: 1 x 14 mm
- 12V_IN vs U3: 19.5 x 3 mm
- U1 vs GALVO_PSU: 1 x 17 mm
- U1 vs U3: 22 x 4.5 mm
- GALVO_PSU vs U3: 15.5 x 8 mm
- GALVO_PSU vs Q1: 4.8 x 3.75 mm
- GALVO_PSU vs R9/R10/R16: 2 x 0.45 mm
- GALVO_PSU vs LASER: 24 x 10 mm
- U3 vs U5: 6.98 x 4.81 mm
- U3 vs VREF: 16 x 6 mm
- U3 vs R_XY: 2 x 0.45 mm
- U3 vs C_ANALOG: 0.5 x 1.25 mm
- U3 vs R9/R10/R16: 2 x 0.45 mm
- U3 vs CAM: 33 x 3.63 mm
- U5 vs GALVO_DRV: 6.98 x 0.81 mm
- VREF vs GALVO_DRV: 16 x 2 mm
- VREF vs CAM: 16 x 7.26 mm
- R_XY vs CAM: 0.5 x 0.45 mm
- GALVO_DRV vs GALVOS: 6 x 16 mm
- GALVO_DRV vs TEST_LASER: 19 x 8 mm
- GALVO_DRV vs CAM: 25.5 x 1.63 mm
- GALVO_DRV vs IMU: 20 x 15 mm
- TEST_LASER vs BEAM_STOP: 1 x 8 mm
- Q1 vs LASER: 2.4 x 3.75 mm

## Missing Connection Endpoints

None.
