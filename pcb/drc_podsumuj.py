# -*- coding: utf-8 -*-
"""Podsumowanie raportu DRC/ERC kicad-cli (JSON): liczba naruszeń według typu, przykłady."""
import json
import sys
from collections import Counter

d = json.load(open(sys.argv[1], encoding="utf-8"))
pomin = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()
lista = d.get("violations", []) + [v for s in d.get("sheets", []) for v in s.get("violations", [])]
lista += [dict(v, type="unconnected_items") for v in d.get("unconnected_items", [])]
lista += [dict(v, type="schematic_parity") for v in d.get("schematic_parity", [])]
c = Counter((v.get("severity"), v["type"]) for v in lista)
for (sev, typ), n in c.most_common():
    print(f"{n:4d} {sev:8s} {typ}")
for typ in sorted({v["type"] for v in lista} - pomin):
    for v in [v for v in lista if v["type"] == typ][:4]:
        print(f"  [{typ}] {v.get('description','')} :: " + " | ".join(i.get("description", "") for i in v.get("items", [])))
