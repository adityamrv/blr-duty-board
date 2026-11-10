# BLR Duty Board

A small installable web app: Akasa Air departures from Bengaluru (BLR) for each medical-services duty shift, with the crew breath analyser (BA) report time (scheduled departure minus 1 h 15 min) and a countdown to the next BA.

- Shifts: Morning 06:30–15:00, Afternoon 13:30–22:00, Night 22:00–06:30 (India time).
- Data: public FlightStats schedule, refreshed every 3 hours by the GitHub Action in `.github/workflows/update-data.yml` (`tools/fetch_days.py` writes `data.json`). Scheduled times only; delays are not shown.
- Install: open the site in Chrome on Android → ⋮ → Install and create shortcut.

## Captain and crew names

- Under each flight there is a line for the captain, first officer and cabin crew. Tap it to add or change the names.
- Names are saved on the phone only (browser storage), never in this repository, and are deleted 4 days after saving.

## Roster tab

- The **Roster** tab shows the BLR medical team duty roster from `roster.json`: your shift today and tomorrow, who is on duty today, and a sideways-scrolling grid (dates across; Morning, Evening, Night, Off / away down each column).
- `roster.json` keeps each cell exactly as written in the official roster (`T2 0600-1430`, `1330-2200`, `2200-0630`, `O`, `leave`, `comp off`, `PH`, `DEL`…), per person per date. The app sorts each cell into a shift by its start time; T2 cells go to the Terminal 2 row; anything that is not a time goes to Off / away.
- To load a new roster, add or replace the dates in `roster.json`; the flight-data Action does not touch this file.
- Mid-roster changes (swaps, call-ins, extra duties, leave) go in `changes` in `roster.json`, oldest first: `{"date":"2026-11-05","name":"Aditya","from":"1330-2200","to":"0630-1500","note":"swap with Dr Amit","logged":"2026-11-04T08:10+05:30"}`. The latest change for a person and date replaces the uploaded cell everywhere in the app; changed cells get an orange dot.

## Stats tab

- Pie chart of one person's duty split (morning, evening, night, off, leave, other), for "So far" (up to today) or the whole saved roster; team counts table (tap a name to see their pie); change log, newest first.

