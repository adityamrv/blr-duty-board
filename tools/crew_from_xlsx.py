#!/usr/bin/env python3
"""Turn the crew roster Excel file ("Staff List" sheet) into the plain crew list for lock_crew.py.

Usage: python3 tools/crew_from_xlsx.py ROSTER.xlsx OUT_PLAIN.json     (OUT must be outside the repository)
Then:  python3 tools/lock_crew.py lock OUT_PLAIN.json ; delete OUT_PLAIN.json ; commit crew.json only.

Columns used: First_Name, Last_Name, Crew_Rank, Flight_Number, STDISTDate, Reporting_Time, Activity_Type.
Rows with a flight go under that flight (tag = activity type unless it is FLY). Rows with no flight
(standby, travel) go under "other" for the roster date. Staff numbers, test ids and all other columns
are ignored. Prints counts only, never names.
"""
import collections, json, sys
import openpyxl

def main(src, out):
    ws = openpyxl.load_workbook(src, read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    ix = {h: i for i, h in enumerate(rows[0])}
    need = ["First_Name", "Last_Name", "Crew_Rank", "Flight_Number", "STDISTDate", "Reporting_Time", "Activity_Type"]
    missing = [c for c in need if c not in ix]
    if missing:
        sys.exit(f"Roster columns missing: {missing}")
    get = lambda r, c: ("" if r[ix[c]] is None else str(r[ix[c]]).strip())
    dates = collections.Counter(get(r, "STDISTDate")[:10] for r in rows[1:] if get(r, "STDISTDate"))
    day = dates.most_common(1)[0][0]
    flights, other, seen = {}, {}, set()
    for r in rows[1:]:
        name = " ".join((get(r, "First_Name") + " " + get(r, "Last_Name")).split())
        if not name:
            continue
        rank, no, rep, act = get(r, "Crew_Rank").upper(), " ".join(get(r, "Flight_Number").split()), get(r, "Reporting_Time")[:5], get(r, "Activity_Type").upper()
        date = get(r, "STDISTDate")[:10] or day
        key = (date, no, rank, name)
        if key in seen:
            continue
        seen.add(key)
        person = [rank, name, rep, "" if act == "FLY" else act]
        if no:
            flights.setdefault(f"{date}|{no}", []).append(person)
        else:
            other.setdefault(date, []).append(person)
    json.dump({"flights": flights, "other": other}, open(out, "w"), ensure_ascii=False)
    print(f"Roster date {day}: {sum(map(len, flights.values()))} people on {len(flights)} flights; "
          f"{sum(map(len, other.values()))} with no flight; dates in file: {dict(dates)}")
    sizes = collections.Counter(len(v) for v in flights.values())
    print("Crew per flight (size: number of flights):", dict(sorted(sizes.items())))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
