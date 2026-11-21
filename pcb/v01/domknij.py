# -*- coding: utf-8 -*-
"""Domknięcie 5 połączeń zasilania i 3 odstępów (DRC 19.11, wariant końcowy) — planowanie tras (Python + numpy, bez KiCada).

    python -I -X utf8 domknij.py <geom.json> <zadania.json> <wyj.json>

zadania.json: lista {"id", "siec", "w", "start": [x, y, L], "cele": [[x, y, L, r], ...] | [], "cel_in2": bool,
                      "warstwy": [...], "usun_uuid": [...]}
Wynik: {"odcinki": [...], "przelotki": [...], "usun_uuid": [...], "raport": [...]} do wstawienia w plik płytki.
"""
import json
import math
import sys
import time

import numpy as np

from geom_v01 import WARSTWY, Plytka
from router_v01 import KLR, Okno, VIA_R, na_odcinki, trasuj, _wewnatrz, _d_odc


def maska_in2(okno, pl, siec="+3V3"):
    """Komórki wewnątrz NAJWIĘKSZEGO wypełnienia strefy +3V3 na In2 z marginesem 0,5 mm od brzegu."""
    best, pole = None, -1
    for z in pl.g["strefy"]:
        if z["siec"] == siec and z["warstwa"] == "In2.Cu":
            for o in z["wypelnienie"]:
                wk = o["zew"]
                a = abs(sum(wk[i][0] * wk[(i + 1) % len(wk)][1] - wk[(i + 1) % len(wk)][0] * wk[i][1] for i in range(len(wk)))) / 2
                if a > pole:
                    best, pole = o, a
    M = _wewnatrz(okno.X, okno.Y, best["zew"])
    for d in best["dziury"]:
        M &= ~_wewnatrz(okno.X, okno.Y, d)
    D = np.full(okno.X.shape, 99.0)
    for kontur in [best["zew"]] + best["dziury"]:
        n = len(kontur)
        x0, y0, x1, y1 = okno.bb
        for e in range(n):
            a, b = kontur[e], kontur[(e + 1) % n]
            if max(a[0], b[0]) < x0 - 1 or min(a[0], b[0]) > x1 + 1 or max(a[1], b[1]) < y0 - 1 or min(a[1], b[1]) > y1 + 1:
                continue
            D = np.minimum(D, _d_odc(okno.X, okno.Y, a, b))
    return M & (D >= 0.5), pole


def sprawdz(pl, odcinki, przelotki, siec, r):
    zle = []
    for a, b, L in odcinki:
        o = pl.odstep_kapsuly(L, a, b, r, siec)
        k = pl.odstep_krawedzi(a, b, r)
        if o < KLR - 1e-6 or k < 0.4:
            zle.append(("odcinek", a, b, L, round(o, 4), round(k, 4)))
    for v in przelotki:
        o = min(pl.odstep_kapsuly(L, v, v, VIA_R, siec) for L in WARSTWY)
        oo = min([math.dist((x, y), v) - ro - 0.15 for x, y, ro, s in pl.otwory if abs(x - v[0]) < 3 and abs(y - v[1]) < 3] or [9])
        smd = 99.0
        for wk, ebb in pl.smd:
            if ebb[0] - 2 < v[0] < ebb[2] + 2 and ebb[1] - 2 < v[1] < ebb[3] + 2:
                from geom_v01 import d_wiel_odc
                smd = min(smd, d_wiel_odc(wk, v, v) - VIA_R)
        if o < KLR - 1e-6 or oo < 0.25 or smd < 0.1:
            zle.append(("przelotka", v, round(o, 4), round(oo, 4), round(smd, 4)))
    return zle


def main():
    pl = Plytka(sys.argv[1])
    zadania = json.load(open(sys.argv[2], encoding="utf-8"))
    wynik = {"odcinki": [], "przelotki": [], "usun_uuid": [], "raport": []}
    for z in zadania:
        t0 = time.time()
        sx, sy, sL = z["start"]
        pts = [(sx, sy)] + [(c[0], c[1]) for c in z["cele"]]
        m = z.get("margines", 5.0)
        x0 = max(0.0, min(p[0] for p in pts) - m); y0 = max(0.0, min(p[1] for p in pts) - m)
        x1 = min(90.0, max(p[0] for p in pts) + m); y1 = min(100.0, max(p[1] for p in pts) + m)
        okno = Okno(pl, x0, y0, x1, y1)
        r = z["w"] / 2
        cel_mask = None
        if z.get("cel_in2"):
            cel_mask, pole = maska_in2(okno, pl)
        cele = [((c[0], c[1]), c[2], c[3]) for c in z["cele"]]
        path = trasuj(okno, z["siec"], r, ((sx, sy), sL), cele, warstwy=tuple(z["warstwy"]), cel_przelotka=cel_mask)
        if path is None:
            wynik["raport"].append({"id": z["id"], "wynik": "BRAK TRASY", "s": round(time.time() - t0, 1)})
            print(z["id"], "BRAK TRASY", flush=True)
            continue
        odc, via = na_odcinki(okno, path)
        # przyklej końce do dokładnych punktów startu i celu (siatka 0,05 mm)
        if odc:
            a, b, L = odc[0]
            odc[0] = ((sx, sy), b, L)
            if cele and path[-1][2] != "VIA_CEL":
                a, b, L = odc[-1]
                odc[-1] = (a, cele[0][0], L) if math.dist(b, cele[0][0]) <= cele[0][2] + 0.1 else (a, b, L)
        zle = sprawdz(pl, odc, via, z["siec"], r)
        wynik["raport"].append({"id": z["id"], "wynik": "OK" if not zle else "KOLIZJA", "odcinki": len(odc),
                                "przelotki": len(via), "dlugosc": round(sum(math.dist(a, b) for a, b, _ in odc), 2),
                                "zle": zle, "s": round(time.time() - t0, 1)})
        print(z["id"], "OK" if not zle else "KOLIZJA", len(odc), "odcinków", len(via), "przelotek", zle[:3], round(time.time() - t0, 1), "s", flush=True)
        if zle:
            continue
        for a, b, L in odc:
            wynik["odcinki"].append({"a": a, "b": b, "w": z["w"], "warstwa": L, "siec": z["siec"]})
            pl._dodaj(L, ("c", tuple(a), tuple(b), r), z["siec"], pl._bbox([a, b], r))
        for v in via:
            wynik["przelotki"].append({"poz": v, "siec": z["siec"]})
            for L in WARSTWY:
                pl._dodaj(L, ("c", tuple(v), tuple(v), VIA_R), z["siec"], pl._bbox([v], VIA_R))
            pl.otwory.append((v[0], v[1], 0.15, z["siec"]))
        wynik["usun_uuid"] += z.get("usun_uuid", [])
    json.dump(wynik, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
