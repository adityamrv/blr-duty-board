# BLR Duty Board

A small installable web app: Akasa Air departures from Bengaluru (BLR) for each medical-services duty shift, with the crew breath analyser (BA) report time (scheduled departure minus 1 h 15 min) and a countdown to the next BA.

- Shifts: Morning 06:30–15:00, Afternoon 13:30–22:00, Night 22:00–06:30 (India time).
- Data: public FlightStats schedule, refreshed every 3 hours by the GitHub Action in `.github/workflows/update-data.yml` (`tools/fetch_days.py` writes `data.json`). Scheduled times only; delays are not shown.
- Install: open the site in Chrome on Android → ⋮ → Install and create shortcut.

## Crew list (captain, first officer, cabin crew per flight)

- Under a flight that has a crew list there is one small line with two counts, `▸ Cockpit 1/2 · Cabin 3/5` (counts only, no names). Tap it to open the names and tick each one off; it closes by itself after 45 seconds, when another flight is opened, or when the app is left. When every name is ticked the flight's BA is marked done. "Change names" edits one flight on the phone.
- Late alert: a person not ticked 15 minutes after their report time (or the flight's BA time when they have none) gets a red report time; the flight's card and that group's count turn red. No alert once the flight is done or departed, or for people who reported before the viewed shift began.
- A person ticked under one flight counts as ticked under every flight of the same date (the BA test is done once per duty).
- This repository is public, so names are never stored here in plain text. The day's list is committed only as `crew.json`, locked (AES-256-GCM, key wrapped with RSA-OAEP) so that only phones listed in `crewkeys.json` can open it. The phone's private key is made in the app and never leaves it.
- One-time setup per phone: in the app tap "Crew list: set up this phone", copy the code (`DB1.…`), send it to Claude. Claude runs `python3 tools/lock_crew.py add-phone "DB1.…" "label"` and commits `crewkeys.json`.
- Daily ("today's crew list" + roster pictures in chat): Claude reads the pictures, writes a plain list **outside the repository** (scratchpad), runs `python3 tools/lock_crew.py lock <plain file>`, commits and pushes `crew.json` only, then deletes the plain file. Format and rules are in the docstring of `tools/lock_crew.py`. Flight keys are `YYYY-MM-DD|QP 1234` (India-time departure date, flight number as in `data.json`).
- Source roster columns used (photo of the Excel "Staff List"): First_Name + Last_Name, Crew_Rank (CP captain, FO first officer, IFM in-flight manager, CC1 / CC2 cabin crew), Flight_Number, STD date, Reporting_Time, Activity_Type. FLY rows go under their flight; DEADHEAD rows go under their flight with the tag; STANDBY and TRAVEL rows (no flight) go in the "Standby and no flight" group for their date, shown in the shift their report time falls in. Staff numbers and test ids are never stored. A person's report time shows next to the name only when it differs from the flight's BA time.
- When the roster comes as the Excel file: `python3 -I tools/crew_from_xlsx.py ROSTER.xlsx <plain file outside the repo>`, then lock as above. Photos are the fallback (read by eye into the same plain format).
- Pilots (left column): CP, SPFO, FO. Cabin crew (right column): IFM, SCC, CC1, CC2, TCC and anything else.
- Never commit crew names in plain text anywhere: not in files, commit messages, branch names or pull requests.

## Roster tab

- The **Roster** tab shows the BLR medical team duty roster from `roster.json`: your shift today and tomorrow, who is on duty today, and a sideways-scrolling grid (dates across; Morning, Evening, Night, Off / away down each column).
- `roster.json` keeps each cell exactly as written in the official roster (`T2 0600-1430`, `1330-2200`, `2200-0630`, `O`, `leave`, `comp off`, `PH`, `DEL`…), per person per date. The app sorts each cell into a shift by its start time; T2 cells go to the Terminal 2 row; anything that is not a time goes to Off / away.
- To load a new roster, add or replace the dates in `roster.json`; the flight-data Action does not touch this file.
- Mid-roster changes (swaps, call-ins, extra duties, leave) go in `changes` in `roster.json`, oldest first: `{"date":"2026-11-05","name":"Aditya","from":"1330-2200","to":"0630-1500","note":"swap with Dr Amit","logged":"2026-11-04T08:10+05:30"}`. The latest change for a person and date replaces the uploaded cell everywhere in the app; changed cells get an orange dot.

## Stats tab

- Pie chart of one person's duty split (morning, evening, night, off, leave, other), for "So far" (up to today) or the whole saved roster; team counts table (tap a name to see their pie); change log, newest first.

