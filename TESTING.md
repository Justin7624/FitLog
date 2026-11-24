# FitLog 2.0 release checks

## Automated checks

- `node --check app.js`, `node --check library.js`, `node --check pro.js`, `node --check sw.js`
- `node tests/core.test.cjs` — simulated DOM and controlled-time integration tests, including mock cloud and IndexedDB operations.
- The fixture is generated from FitLog 1.0's original initialization; its tests modify a copy to verify the upgrade preserves a non-default note, actual weight, reps and session identity.

These checks do not constitute live browser testing. Chromium navigation to the local test server returned `ERR_BLOCKED_BY_ADMINISTRATOR` because this environment disallows navigation. No browser policies were changed. Native browser/PWA behavior and an actual Supabase account require manual verification.

## Manual acceptance checklist after deployment

1. Before upgrading, export the v1 JSON. Open the same Pages URL, confirm Arm Day's 18 exercises and history. Confirm your edited routines and prior logs remain.
2. On a phone, verify Today, Train, History, Progress, Body and Settings have readable layouts with no horizontal overflow. Test both themes and weight units.
3. In Ab Day add a library plank. Create two 3-second sets with 2 seconds rest; start guided mode. Confirm both intervals complete automatically, pause/resume works, and actual reps/weights/RPE can be edited. Save; confirm the History entry. Delete the test log if desired.
4. In Arm Day use Load video and chapter links; verify external link and embedding on your device. Test an interval with the screen visible; leaving the tab should pause. Reload and resume the active session.
5. Edit a muscle goal, tap front/back regions, filter progress and view the print report. Choose Save as PDF; confirm text/tables are readable.
6. In Body enter test same-date Waist 30 in and Hips 100 cm. Expected ratio: 0.76. Enter 185 lb and 15% body fat: estimated lean mass 157.25 lb. Delete test measurements after checking.
7. Add two nonsensitive test photos of the same view; compare, reload, verify persistence. Export a photo-inclusive backup, restore it, verify photos and workout history. Delete test photos. Keep your actual backup securely.
8. Test Settings export/import, and install on mobile. After an online visit, disconnect internet; local app should remain accessible. YouTube and cloud require internet.
9. If configuring Supabase, run SQL, create a test user, push and pull a test snapshot in two browser profiles. Confirm conflict warnings when both profiles attempt to push stale revisions. Confirm unauthenticated and other-account access is denied by RLS. Confirm photos are not included in the cloud payload. Never use a production secret/admin key.
