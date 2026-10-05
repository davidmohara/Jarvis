#!/usr/bin/env python3
"""Build data/amazing-race/roster.json from the 2026 Teams.xlsx People sheet.

Maps every attendee (Name) to their numeric Racing Team. Output:
  {"by_name": {exact name: team}, "by_norm": {normalized key: team}}

David's instruction (2026-10-03, live event): use the roster to correlate
posts to a Team when the post does not include the team number. This reverses
the earlier exclude-roster decision.

Stdlib only (zipfile + ElementTree minimal xlsx reader).
"""

import json
import os
import re
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

IES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_PATH = os.path.join(IES_ROOT, "data", "amazing-race", "roster.json")
XLSX_PATH = os.path.join(os.path.dirname(IES_ROOT), "Corporate", "Retreat", "2026",
                         "2026 Teams.xlsx")


def normalize(name):
    """Lowercase, strip diacritics, collapse whitespace/punctuation for fuzzy match."""
    t = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def main():
    M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    z = zipfile.ZipFile(XLSX_PATH)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si"):
            ss.append("".join(t.text or "" for t in si.iter(M + "t")))

    def cellval(c):
        v = c.find(M + "v")
        if v is None:
            return "".join(x.text or "" for x in c.iter(M + "t"))
        if c.get("t") == "s":
            return ss[int(v.text)]
        return v.text

    sh = ET.fromstring(z.read("xl/worksheets/sheet2.xml"))  # People sheet
    rows = []
    for row in sh.iter(M + "row"):
        vals = {}
        for c in row.findall(M + "c"):
            col = re.match(r"([A-Z]+)", c.get("r")).group(1)
            vals[col] = cellval(c)
        rows.append(vals)
    header = rows[0]
    assert header.get("A") == "Name" and header.get("D") == "Team", header
    by_name, by_norm, skipped = {}, {}, 0
    for r in rows[1:]:
        name, team = (r.get("A") or "").strip(), r.get("D")
        try:
            team = int(team)
        except (TypeError, ValueError):
            skipped += 1
            continue
        if not name:
            continue
        by_name[name] = team
        by_norm.setdefault(normalize(name), team)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump({"by_name": by_name, "by_norm": by_norm, "source": XLSX_PATH,
                   "built": __import__("time").strftime("%Y-%m-%dT%H:%M:%S")}, f, indent=1)
    print(json.dumps({"ok": True, "people": len(by_name), "skipped": skipped,
                      "out": OUT_PATH}))


if __name__ == "__main__":
    main()
