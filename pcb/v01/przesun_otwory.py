# -*- coding: utf-8 -*-
"""Przesuwa otwory montażowe H1–H4 o 0,1 mm do środka płytki (DRC: miedź padu 0,30 mm od krawędzi przy regule 0,40).

    python -I -X utf8 przesun_otwory.py <plik.kicad_pcb>

Nowe położenia (mm): H1 (3,6; 3,6), H2 (86,4; 9,6), H3 (3,6; 86,0), H4 (86,4; 86,0) — dotąd 3,5 / 86,5 (plytka.py UKLAD).
Zmienia tylko pierwsze `(at …)` footprintu (pady są względne). Obudowa (`projekt\arcade.toml`) nie zapisuje tych
współrzędnych; 0,1 mm mieści się w luzie otworu M3 3,2 mm na śrubę M3.
"""
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from czysc_plytke import elementy, glowa  # noqa: E402

NOWE = {"H1": (3.6, 3.6), "H2": (86.4, 9.6), "H3": (3.6, 86.0), "H4": (86.4, 86.0)}


def main():
    p = sys.argv[1]
    t = open(p, "rb").read().decode("utf-8")
    zmiany = []
    for a, b in reversed(elementy(t)):
        el = t[a:b]
        if glowa(el) != "footprint":
            continue
        m = re.search(r'\(property "Reference" "(H[1-4])"', el)
        if not m:
            continue
        ref = m.group(1)
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", el)
        x, y = NOWE[ref]
        nowe_at = f"(at {x:g} {y:g}" + (f" {at.group(3)}" if at.group(3) else "") + ")"
        zmiany.append((ref, at.group(0), nowe_at))
        el = el[:at.start()] + nowe_at + el[at.end():]
        t = t[:a] + el + t[b:]
    open(p, "wb").write(t.encode("utf-8"))
    for z in sorted(zmiany):
        print(*z)


if __name__ == "__main__":
    main()
