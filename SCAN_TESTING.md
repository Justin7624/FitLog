# FitLog 5.0 — verification record

## Executed in this environment

- JavaScript syntax checks for every root `.js` file: passed.
- Verified every runtime path in `index.html` and the service-worker precache list exists at the repository root: passed.
- Existing `tests/core.test.cjs`: passed (legacy migration, workout duplicate/delete/restore, interval, analytics and simulated sync/encryption logic).
- Existing `tests/body-fit.test.cjs`: 11 checks passed (continuous template topology, measurement fitting, unit conversion, normals/OBJ).
- Existing `tests/body_browser_inline.py`: passed in actual isolated Chromium, mobile viewport, Canvas renderer, simulated legacy storage. Existing history, Body Studio controls, photos references/goal storage logic and report paths are not replaced by scanner.
- `tests/scan-core.test.cjs`: 7 checks passed (angle coverage, invalid input, segmentation, photo sensitivity, manual fitting, correction, GLB structure). One synthetic example's projected edge RMSE fell from 1.489 to 0.154 cm. This is a controlled test using the same template family and approximate projections, **not independent accuracy or a claim about real-person measurements**.
- `tests/scan_browser_inline.py`: actual isolated Chromium (430×932), 12 synthetic PNG uploads, mask review/approval, photo-assisted reconstruction, Canvas render, section guide, OBJ/GLB/report downloads, goal isolation, scan library with mocked storage, comparison/heatmap/animation, original workout record retained, no uncaught page errors. Passed.
- Native-origin `tests/body_browser.py` attempted; administrator policy blocks localhost navigation (net::ERR_BLOCKED_BY_ADMINISTRATOR). This is an environment limitation, not a passing test.

## Included, not verified here

GitHub Actions runs the old regression tests, new scan unit tests, isolated Chromium UI tests and native-origin browser suites. `tests/scan_browser.py` exercises actual IndexedDB scan save/delete/encrypted restoration, offline reload and old history persistence. The existing `tests/browser_test.py` and `tests/body_browser.py` exercise original data migration, progress photos, and offline assets. These require unrestricted localhost navigation. CI results are not yet available. Camera access, voice guidance, video capture/seek behavior on real phones, WebGL hardware, native persistent scan DB and deployed service-worker updates require live-device testing.

## Manual deployment acceptance

1. Back up FitLog 4.0.1 (including old progress photos), upgrade at the same URL, verify existing Arm Day routine/video, history, body entries and photos.
2. Confirm new header and scan launch. Take 12 clothed images in a plain room and inspect masks; try a cropped image (must not approve until corrected). Test camera permissions/stop, retake, and video sample extraction separately.
3. Enter independently measured height/circumferences and reconstruct. Change one mask or side silhouette and reconstruct again; confirm 3D shape changes. Inspect raw and final residuals. Verify shoulder width/circumference field meaning.
4. Save two scans, reload, compare/animate/heatmap; export OBJ/GLB and open in a 3D viewer, download report and print to PDF. Try a hypothetical goal and ensure it doesn't overwrite the record.
5. Export encrypted scan backup, test incorrect passphrase, then restore in a disposable browser profile. Confirm records persist across reload and offline mode. Separately test old FitLog backup. Do not test by clearing real user data.
6. Validate repeatability across multiple independent captures and against direct tape or calibrated scan data before relying on any estimated dimensions. No such real-person test was completed for this release.
