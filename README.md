# BLR Duty Board

A small installable web app: Akasa Air departures from Bengaluru (BLR) for each medical-services duty shift, with the crew breath analyser (BA) report time (scheduled departure minus 1 h 15 min) and a countdown to the next BA.

- Shifts: Morning 06:30–15:00, Afternoon 13:30–22:00, Night 22:00–06:30 (India time).
- Data: public FlightStats schedule, refreshed every 3 hours by the GitHub Action in `.github/workflows/update-data.yml` (`tools/fetch_days.py` writes `data.json`). Scheduled times only; delays are not shown.
- Install: open the site in Chrome on Android → ⋮ → Install and create shortcut.

## Roster tab

- The **Roster** tab shows the BLR medical team duty roster from `roster.json`: your shift today and tomorrow, who is on duty today, and a sideways-scrolling grid (dates across; Morning, Evening, Night, Off down each column).
- `roster.json` holds one entry per date: `status` (`roster` = from the official roster, `draft` = not approved yet) and each person's shift code — `M`/`M1` morning, `M2` morning Terminal 2, `G` general, `E`/`E1` evening, `E2` evening Terminal 2, `N` night, `O` off, `X` away.
- To load a new roster, add or replace the dates in `roster.json`; the flight-data Action does not touch this file.
