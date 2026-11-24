# FitLog — Training Journal

Mobile-first, local-first workout tracking. Plain HTML, CSS and JavaScript; no build tools, accounts, API keys or paid services required.

## Deploy on GitHub Pages

1. Extract the ZIP. Create a new GitHub repository (e.g. `fitlog`). A public repository supports free GitHub Pages.
2. Upload **all files inside the ZIP to the root of the repository** (not inside another folder), then commit. `index.html` must be at the root.
3. In the repository, open **Settings → Pages**. Under Build and deployment, select **Deploy from a branch**. Choose `main` and `/(root)`; save.
4. Open the site URL shown in Pages when deployment is complete (usually `https://YOUR-USERNAME.github.io/fitlog/`).
5. On a phone, use Safari Share → Add to Home Screen (iPhone), or your Android browser menu → Install app / Add to Home screen. Offline support requires a successful first online visit; YouTube videos need internet. Browser timers may be delayed when the app is backgrounded or the phone is locked.

## Using the app

- **Today:** shows the next split based on the latest saved session, recent activity and weekly goal. Resume an unsaved session if needed.
- **Routines:** Arm Day (all 18 fitbymik exercises), Ab Day and Leg Day. Add, remove, rename and reorder exercises, configure sets, weights, reps, time, rest intervals, muscle groups, notes and video links. Create additional routines without a fixed limit. Changing a routine does not change past logs.
- **Workout:** start a routine, adjust actual values, use the timer, and tap the check beside each completed set. Record set type or RPE if desired. For circuits you performed with the video, use Mark all complete after verifying values. Save the session or optionally update the routine. A partially completed workout can be saved after confirmation.
- **History:** calendar, session details, edit, repeat or delete past workouts. Use Log past workout for a previous date, and enter the total duration if known.
- **Progress:** weekly frequency, completed sets, personal bests, best-set trend charts (latest 12 recorded sessions), recorded rep volume, timed work, primary muscle-group distribution, and optional body measurement records.
- **Settings:** theme, lb/kg, weekly target, auto rest timer, CSV export, full JSON backup/import.

## Your imported Arm Day

Video: https://youtu.be/ruoCYrZCBeY — fitbymik, 20 min STANDING ARM WORKOUT | Plus Barre Arms | 2 Sets Of Dumbbells | No Planks or Pushups.

The supplied chapter screenshots establish the 18 exercise names and timestamps. Each exercise is configured as one 45-second working set and a 15-second rest. Total planned working time: 13:30. Weights on the routine are editable **suggestions** based on 10 lb light and 12 lb heavy dumbbells, not verified per-exercise observations. A completed historical Arm Day dated November 23, 2026 is preloaded with the prescribed intervals and notes about the two weights used; exact per-exercise weights and repetitions are intentionally blank. Edit that log if you remember the values.

## Data and privacy

Data lives in browser localStorage on the app's origin. No automatic cloud sync or server database. Clearing site data, switching browsers, or changing the URL can remove or separate your logs. Export JSON backups regularly and import them on another device. Import replaces existing data after confirmation. CSV contains workout rows, not the complete backup. The public repository includes the initial Arm Day template and seed log, so remove the sample history in `initial()` in `app.js` before publishing if you do not want that initial session included publicly. Your subsequent edits and personal logs are not uploaded to GitHub. Do not commit exported backup files to a public repository.

Weights are stored in pounds and converted for display; use one consistent load convention per exercise (per dumbbell for the Arm Day). Volume is entered weight × recorded reps; timed sets without reps are excluded. Muscle groups are primary classifications, not physiological recovery estimates. RPE is optional subjective effort (1–10). No calorie estimates or automatic AI coaching are included.

## Reference inspiration

- Hevy: https://help.hevyapp.com/hc/en-us/articles/33106320824727-Everything-You-Need-to-Know-About-the-Hevy-App-2026-Features-Guide
- Strong: https://apps.apple.com/us/app/strong-workout-tracker-gym-log/id464254577
- Fitbod: https://help.fitbod.me/hc/en-us/sections/1500000536822-Progress-Performance-Tracking

FitLog is independent and does not use those apps' proprietary code or data.
