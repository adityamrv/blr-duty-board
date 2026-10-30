#!/usr/bin/env python3
"""Build data.json for the Duty Board: Akasa Air (QP / AKJ) departures from
Bengaluru (BLR), from FlightStats, for yesterday .. day after tomorrow (India time).
Usage: python3 tools/fetch_days.py [OUTPUT_PATH]   (default: data.json)
If a day fails completely, the previous data for that day is kept and marked stale."""
import json, sys, datetime as dt, os, urllib.request

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
UA = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36"

def fetch_window(day, hour):
    url = (f"https://www.flightstats.com/v2/flight-tracker/departures/BLR/AKJ"
           f"?year={day.year}&month={day.month}&date={day.day}&hour={hour}")
    label = f"{hour:02d}:00-{hour + 6:02d}:00"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        s = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"{label} failed to load ({type(e).__name__})"
    key = "__NEXT_DATA__ = "
    if key not in s:
        return None, f"{label} page format changed"
    d, _ = json.JSONDecoder().raw_decode(s[s.index(key) + len(key):])
    route = d["props"]["initialState"]["flightTracker"]["route"]
    if route.get("header", {}).get("date", "") != day.strftime("%d-%b-%Y"):
        return None, f"{label} returned the wrong date"
    rows = []
    for f in route.get("flights") or []:
        if f.get("operatedBy"):        # codeshare run by another airline
            continue
        rows.append({"no": "QP " + f["carrier"]["flightNumber"], "std": f["departureTime"]["time24"],
                     "to": f["airport"]["city"], "code": f["airport"]["fs"]})
    return rows, None

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    old = {}
    if os.path.exists(out):
        try:
            old = json.load(open(out)).get("days", {})
        except Exception:
            old = {}
    now = dt.datetime.now(IST)
    days = {}
    for off in range(-1, 3):
        day = now.date() + dt.timedelta(days=off)
        iso = day.isoformat()
        flights, gaps, seen, ok_windows = [], [], set(), 0
        for hour in (0, 6, 12, 18):
            rows, err = fetch_window(day, hour)
            if err:
                gaps.append(err)
            else:
                ok_windows += 1
            for r in rows or []:
                k = (r["no"], r["std"])
                if k not in seen:
                    seen.add(k); flights.append(r)
        flights.sort(key=lambda r: r["std"])
        if ok_windows == 0 and iso in old:   # total failure: keep last good data
            keep = dict(old[iso]); keep["stale"] = True
            days[iso] = keep
            print(iso, "FAILED - kept previous data")
            continue
        days[iso] = {"flights": flights, "complete": not gaps, "gaps": gaps,
                     "updatedAt": now.isoformat(timespec="seconds")}
        print(iso, len(flights), "flights", "complete" if not gaps else "GAPS: " + "; ".join(gaps))
    data = {"updatedAt": now.isoformat(timespec="seconds"), "source": "FlightStats", "days": days}
    with open(out, "w") as fh:
        json.dump(data, fh, separators=(",", ":"))

if __name__ == "__main__":
    main()
