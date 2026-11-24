# FitLog 3.0 verification

## Results in the build environment

- Node 22 syntax checks on all app JS and service worker: passed.
- `node tests/core.test.cjs`: 55 passing named checks (simulated DOM, simulated time, mocked IndexedDB and Supabase API). The full output is in `tests/results.txt`.
- Tests use the original v1 fixture and a v2 fixture produced by the original v2 source; they check migration, exact workout history and IDs, original Arm Day video/timestamps, theme and physique goals, preservation of mocked photo records, exercise library uniqueness, interval progression, history deletion/restore/duplicate cancellation, nutrition, scheduling, explicit load multiplier, RIR controls, backup validation, AES-GCM round-trip/wrong passphrase rejection, and three-way merges including a mocked API round trip.
- Browser launch was attempted with Playwright/Chromium at a 390 × 844 viewport, but navigation to the temporary local HTTP server returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. This is an environment restriction, not a passing end-to-end test. The full browser suite was prepared but cannot be executed here. It is included in the GitHub Actions workflow so it can run on a standard hosted runner; no claim is made that CI has run or passed yet.

## Browser acceptance checklist

Run `python tests/browser_test.py` after installing Playwright and Chromium, or inspect the GitHub Actions workflow logs. It exercises a real IndexedDB version-1 database upgrade and localStorage migration from a v2 fixture, native photo preservation, visible delete and undo, duplicate cancellation, exercise search/add, timed workout save, nutrition and program forms, PDF generation, encrypted export/import, reload persistence, and offline shell loading. If a browser test fails, investigate before using the release for new data.

Manual checks still required on the actual phone and GitHub Pages origin:

1. Back up the current installation with photos, deploy in place, close old tabs, open the original address and verify all real records, settings, routines and gallery. Never clear site data to force an update.
2. In History delete a duplicate, verify analytics and next rotation, undo, delete again, reload and restore from Recently deleted. Verify intentional same-day logging is allowed after confirmation. Test selecting two matching sessions for merge and restoring the prior revision.
3. Edit set type, RIR, tempo, unilateral side and load convention. Check saved values and warm-up exclusion. Create two same-group circuit exercises and verify interleaved order.
4. Play the embedded YouTube video on the deployed site, opt in to interval chapter commands and test pause/play/seek. Browser/YouTube can block this; verify timestamp link fallback. Test audio, speech, screen wake lock, timer interruption and resume.
5. Upload two matching-view photos, try the slider and timelapse; export/import an encrypted photo backup. Confirm photos stay local during cloud sync. Confirm browser quota errors do not silently imply a successful save.
6. Test real Supabase sign-in, row-level policies, conflict prompts and revision checks using two devices and a dedicated test account. Verify automatic sync only while signed in, offline changes reconcile after reconnect, and photos are excluded. Never test destructive sync with your only copy of real data.
7. Check the layout on mobile and desktop, light/dark contrast, keyboard operation, installation and service-worker update. Print reports and confirm the intended date range.

## Known limitations

Browser end-to-end and live services are unverified in this environment. Storage is still compatible with v2's localStorage-first design (not a complete DB rewrite); local snapshots are not off-device disaster recovery. The encyclopedia is expanded to 160 named entries, not 300–500. Reports use browser Print/Save as PDF. Video commands are best effort, no direct video playback analysis. Photo timelapse is an in-app slideshow. Nutrition entries are manual. Cloud sync requires a separately configured account, does not merge actively edited workouts, and does not sync photos. See README for more details.
