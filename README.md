# BLR Duty Board

A small installable web app: Akasa Air departures from Bengaluru (BLR) for each medical-services duty shift, with the crew breath analyser (BA) report time (scheduled departure minus 1 h 15 min) and a countdown to the next BA.

- Shifts: Morning 06:30–15:00, Afternoon 13:30–22:00, Night 22:00–06:30 (India time).
- Data: public FlightStats schedule, refreshed every 3 hours by the GitHub Action in `.github/workflows/update-data.yml` (`tools/fetch_days.py` writes `data.json`). Scheduled times only; delays are not shown.
- Install: open the site in Chrome on Android → ⋮ → Install and create shortcut.

## Crew list (captain, first officer, cabin crew per flight)

- Under a flight that has a crew list there is one small line with two counts, `▸ Cockpit 1/2 · Cabin 3/5` (counts only, no names). Tap it to open the names and tick each one off; it closes by itself after 45 seconds, when another flight is opened, or when the app is left. When every name is ticked the flight's BA is marked done. "Change names" edits one flight on the phone.
- Late alert: a person not ticked 15 minutes after their report time (or the flight's BA time when they have none) gets a red report time; the flight's card and that group's count turn red. No alert once the flight is done or departed, or for people who reported before the viewed shift began.
- A person ticked under one flight counts as ticked under every flight of the same date (the BA test is done once per duty).
- Cockpit only button (next to Alerts, off by default, remembered on the phone): only pilots (CP, SPFO, FO) count. Alerts, red late marks and the "done" strike-out then follow the pilots only; cabin crew and cabin standby give no alerts but stay listed and can still be ticked.
- Alerts button (off by default, remembered on the phone): while the app is open it notifies, beeps and vibrates 5 minutes before each crew report time in the current shift, and once when people are still unticked 15 minutes after it. Alerts carry flight numbers and counts only, never names. They do not fire when the app is closed.
- Find crew: a search box above the flight table (shown only when a crew list is loaded) matches names, or a flight number with 3+ digits, across today's and the viewed shift's lists. Results have a tick box (same day-wide tick as the drop-down) and tapping a name opens that flight's list if it is in the shift on screen. The box clears itself after 60 s without use and when the app is left.
- This repository is public, so names are never stored here in plain text. The day's list is committed only as `crew.json`, locked (AES-256-GCM, key wrapped with RSA-OAEP) so that only phones listed in `crewkeys.json` can open it. The phone's private key is made in the app and never leaves it.
- One-time setup per phone: in the app tap "Crew list: set up this phone", copy the code (`DB1.…`), send it to Claude. Claude runs `python3 tools/lock_crew.py add-phone "DB1.…" "label"` and commits `crewkeys.json`.
- Daily ("today's crew list" + roster pictures in chat): Claude reads the pictures, writes a plain list **outside the repository** (scratchpad), runs `python3 tools/lock_crew.py lock <plain file>`, commits and pushes `crew.json` only, then deletes the plain file. Format and rules are in the docstring of `tools/lock_crew.py`. Flight keys are `YYYY-MM-DD|QP 1234` (India-time departure date, flight number as in `data.json`).
- Source roster columns used (photo of the Excel "Staff List"): First_Name + Last_Name, Crew_Rank (CP captain, FO first officer, IFM in-flight manager, CC1 / CC2 cabin crew), Flight_Number, STD date, Reporting_Time, Activity_Type. FLY rows go under their flight; DEADHEAD rows go under their flight with the tag; STANDBY and TRAVEL rows (no flight) go in the "Standby and no flight" group for their date, shown in the shift their report time falls in. Staff numbers and test ids are never stored. A person's report time shows next to the name only when it differs from the flight's BA time.
- Roster column names change between exports (17 Nov 2026: `STDISTDate` became `Flight_Activity_Date`). The app and `tools/crew_from_xlsx.py` find each column by any known name (`COLS`), ignoring case, spaces and underscores; add a new name there if an export renames a column again.
- A flight in the roster file that is missing from the public schedule (extra or charter flights, e.g. QP 6995 on 17 Nov) is added to the board from the file: STD from `Flight_Time`, destination from `Arrival_Airport` (BLR departures only), marked "· roster". It lives only on the phone with that day's crew list.
- Main daily route since 10 Nov: in the app, Crew list → "Load roster file" reads the roster .xlsx on the phone (`readRoster` in index.html, same rules as `tools/crew_from_xlsx.py`). Nothing is uploaded and no phone code is needed. The Claude route below stays as a backup.
- When the roster comes as the Excel file: `python3 -I tools/crew_from_xlsx.py ROSTER.xlsx <plain file outside the repo>`, then lock as above. Photos are the fallback (read by eye into the same plain format).
- Pilots (left column): CP, SPFO, FO. Cabin crew (right column): IFM, SCC, CC1, CC2, TCC and anything else.
- Never commit crew names in plain text anywhere: not in files, commit messages, branch names or pull requests.

## Removed (20 Nov 2026)

- The Roster, Stats and Verify tabs were removed from the app to keep it light. `roster.json` stays in the repository for the rostering work; the app no longer reads it.
