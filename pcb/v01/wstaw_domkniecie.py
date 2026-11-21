# -*- coding: utf-8 -*-
"""Wstawia wynik domknij.py do pliku .kicad_pcb (na tekście): usuwa odcinki po uuid, dopisuje odcinki i przelotki.

    python -I -X utf8 wstaw_domkniecie.py <wej.kicad_pcb> <domkniecie.json> <wyj.kicad_pcb>

Przelotki 0,6/0,3 mm F.Cu–B.Cu (przelotowe). Strefy trzeba potem wypełnić (Python KiCada: ZONE_FILLER).
"""
import json
import re
import sys
import uuid

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from czysc_plytke import elementy, glowa  # noqa: E402


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def main():
    t = open(sys.argv[1], "rb").read().decode("utf-8")
    d = json.load(open(sys.argv[2], encoding="utf-8"))
    usun = set(d["usun_uuid"])
    wyc = []
    for a, b in elementy(t):
        el = t[a:b]
        if glowa(el) == "segment":
            m = re.search(r'\(uuid "([^"]+)"\)', el)
            if m and m.group(1) in usun:
                wyc.append((a, b))
    if len(wyc) != len(usun):
        sys.exit(f"znaleziono {len(wyc)} z {len(usun)} odcinków do usunięcia — przerywam")
    for a, b in reversed(wyc):
        a2 = a
        while a2 > 0 and t[a2 - 1] in " \t\r\n":
            a2 -= 1
        t = t[:a2] + t[b:]
    nl = "\r\n" if "\r\n" in t else "\n"
    nowe = []
    for o in d["odcinki"]:
        nowe.append(f'\t(segment (start {f(o["a"][0])} {f(o["a"][1])}) (end {f(o["b"][0])} {f(o["b"][1])}) (width {f(o["w"])}) '
                    f'(layer "{o["warstwa"]}") (net "{o["siec"]}") (uuid "{uuid.uuid4()}"))')
    for v in d["przelotki"]:
        nowe.append(f'\t(via (at {f(v["poz"][0])} {f(v["poz"][1])}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") '
                    f'(net "{v["siec"]}") (uuid "{uuid.uuid4()}"))')
    koniec = t.rstrip().rfind(")")
    t = t[:koniec].rstrip() + nl + nl.join(nowe) + nl + ")" + nl
    open(sys.argv[3], "wb").write(t.encode("utf-8"))
    print("usunięte", len(wyc), "dodane odcinki", len(d["odcinki"]), "przelotki", len(d["przelotki"]))


if __name__ == "__main__":
    main()
