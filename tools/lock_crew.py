#!/usr/bin/env python3
"""Lock the day's crew list for the Duty Board.

The repository is public, so crew names are never stored in plain text. This script encrypts a
plain crew list so that only the phones whose codes are in crewkeys.json can open it, and writes
crew.json (the only crew file that is committed).

Usage:
  python3 tools/lock_crew.py add-phone "DB1.<code from the app>" [label]   # one-time per phone
  python3 tools/lock_crew.py lock /path/outside/the/repo/crew_plain.json   # every day

Plain list format (keep this file OUTSIDE the repository and delete it afterwards):
  {"flights": {"2026-11-10|QP 1262": {"capt": "Name", "fo": "Name", "cabin": ["Name", "Name"]}}}
Key = India-time departure date | flight number exactly as in data.json ("QP 1262").
Each lock replaces the list for the flights it contains; flights from earlier lists stay on the
phone for 3 days. To correct one flight, lock a list containing just that flight.
"""
import base64, hashlib, json, os, sys, time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS, OUT = os.path.join(ROOT, "crewkeys.json"), os.path.join(ROOT, "crew.json")
b64 = lambda b: base64.b64encode(b).decode()

def load_keys():
    return json.load(open(KEYS)) if os.path.exists(KEYS) else {"phones": []}

def add_phone(code, label):
    code = "".join(code.split())
    if not code.startswith("DB1."):
        sys.exit("Not a Duty Board code (must start with DB1.)")
    spki = base64.b64decode(code[4:])
    serialization.load_der_public_key(spki)          # fails loudly if the code is damaged
    kid = hashlib.sha256(spki).hexdigest()[:8]
    doc = load_keys()
    doc["phones"] = [p for p in doc["phones"] if p["kid"] != kid] + [{"kid": kid, "label": label, "spki": b64(spki)}]
    json.dump(doc, open(KEYS, "w"), indent=1)
    print(f"Added phone {kid} ({label}); {len(doc['phones'])} phone(s) can open the crew list")

def lock(path):
    if os.path.abspath(path).startswith(ROOT + os.sep):
        sys.exit("Keep the plain crew list outside the repository.")
    plain = json.load(open(path))
    flights = plain.get("flights") or {}
    days = json.load(open(os.path.join(ROOT, "data.json"))).get("days", {})
    for k, c in flights.items():
        date, no = k.split("|")
        known = {f["no"] for f in days.get(date, {}).get("flights", [])}
        if no not in known:
            print(f"WARNING: {k} is not in data.json for that date; it will not show in the app")
        if not isinstance(c.get("cabin", []), list):
            sys.exit(f"{k}: cabin must be a list")
    phones = load_keys()["phones"]
    if not phones:
        sys.exit("No phone set up yet: run add-phone first.")
    key, iv = AESGCM.generate_key(256), os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps({"flights": flights}, ensure_ascii=False).encode(), None)
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    ek = {p["kid"]: b64(serialization.load_der_public_key(base64.b64decode(p["spki"])).encrypt(key, oaep)) for p in phones}
    json.dump({"v": 1, "at": int(time.time() * 1000), "ek": ek, "iv": b64(iv), "ct": b64(ct)}, open(OUT, "w"))
    print(f"Locked {len(flights)} flight(s) for {len(phones)} phone(s) -> crew.json")

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "add-phone": add_phone(a[1], a[2] if len(a) > 2 else "phone")
    elif len(a) == 2 and a[0] == "lock": lock(a[1])
    else: sys.exit(__doc__)
