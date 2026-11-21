# -*- coding: utf-8 -*-
"""Podsumowanie raportu DRC (JSON z kicad-cli): liczby błędów/ostrzeżeń według rodzaju, niepołączone według sieci.

    python -I -X utf8 drc_podsumuj_v01.py <drc.json> [<drc.json> ...]
"""
import json
import re
import sys
from collections import Counter


def podsumuj(p):
    d = json.load(open(p, encoding="utf-8"))
    v = d.get("violations", [])
    bledy = Counter(x["type"] for x in v if x["severity"] == "error")
    ostrz = Counter(x["type"] for x in v if x["severity"] == "warning")
    niep = Counter()
    for x in d.get("unconnected_items", []):
        m = re.search(r"\[([^\]]+)\]", x["items"][0]["description"])
        niep[m.group(1) if m else "?"] += 1
    par = Counter(x["type"] for x in d.get("schematic_parity", []))
    print(f"== {p} ({d.get('date')})")
    print(f"   błędy: {sum(bledy.values())} {dict(bledy)}")
    print(f"   ostrzeżenia: {sum(ostrz.values())} {dict(ostrz)}")
    print(f"   niepołączone: {sum(niep.values())} {dict(niep.most_common())}")
    print(f"   zgodność ze schematem: {dict(par)}")
    for x in v:
        if x["severity"] == "error":
            print("   ERR", x["type"], "|", " | ".join(i["description"][:70] for i in x["items"]))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        podsumuj(p)
