# -*- coding: utf-8 -*-
"""Plik pozycji (CPL) dla JLCPCB z korektami obrotu i środka — pakiet v0.1, 20.11.2026.

    python -I -X utf8 korekty_jlc.py <pozycje_kicad.csv> <cpl_jlcpcb.csv> <bom_jlcpcb.csv>
    python -I -X utf8 korekty_jlc.py --sprawdz <pozycje_kicad.csv> <bom_jlcpcb.csv> <cpl_wzorzec.csv>

Dlaczego: JLCPCB układa części według własnych footprintów (biblioteka EasyEDA/LCSC), a nie według footprintów KiCada.
Zero obrotu i punkt środka bywają w nich inne, i to zależnie od konkretnej części (ten sam SOT-23-6 ma 0° dla USBLC6-2SC6
i 180° dla SRV05-4). Surowy eksport KiCada postawiłby 7 układów obróconych (część z nich trafia wtedy na pady odwrotnie
i zwiera zasilanie 3,3 V), a moduł ESP32 i gniazdo USB-C obok padów.

Korekty są zapisane w układzie footprintu (przesunięcie dx, dy w mm w osiach elementu przed obrotem, Y w górę jak
w eksporcie pozycji KiCada) i przypisane do numeru LCSC — działają więc także po przesunięciu albo obróceniu elementu.
Źródło liczb: trzy niezależne wyliczenia z 20.11.2026 (dopasowanie padów footprintu KiCada do footprintu EasyEDA danej
części, nóżka po nóżce): audyt gotowości (montaz-01/02, weryfikator; docs/AUDYT_REV_A.md), krytyk audytu i niezależna recenzja — zgodne
w 128/128 pozycjach (0,05 mm, 0,1°). Ostateczną kontrolą jest podgląd montażu JLCPCB przed płatnością.
Części spoza tabeli: bez korekty (sprawdzone: bierne, D1, D2 = C72043 i C12065, F1, L1, FB1/FB2, Y1, SW1/SW2).
Pliku NIE wysyłać do PCBWay — tam idzie eksport KiCada (konwencja KiCada).
"""
import csv
import math
import sys

# LCSC → (dodatkowy obrót [°], dx [mm], dy [mm]) w układzie footprintu
KOREKTY = {
    "C2913202": (0, 0.0, -3.6269),     # U1 ESP32-S3-WROOM-1-N16R8: KiCad liczy środek z anteną, EasyEDA środek pól lutowniczych
    "C7519": (270, 0.0, 0.0),          # U2 USBLC6-2SC6 (SOT-23-6, wariant EasyEDA „-BL”)
    "C141836": (180, 0.0322, 0.0),     # U3 TLV62569DBVR (SOT-23-5)
    "C32843": (270, 0.0, 0.0),         # U4 W5500 (LQFP-48)
    "C10237": (180, 0.0, 0.0),         # U7 74LVC1G04GW (SOT-353)
    "C13612": (180, 0.0, 0.0),         # U10–U12 SRV05-4 (SOT-23-6, wariant EasyEDA „-BR”)
    "C165948": (0, 0.0, 1.5717),       # J1 USB-C HRO TYPE-C-31-M-12: środek wg rzędu padów SMD
    "C12074": (0, 4.4434, -4.3581),    # J2 RJ45 HanRun HR911105A (THT)
    "C144395": (180, 3.75, 0.0),       # J10–J15 JST B4B-XH-A (THT): korpus z kluczem
    "C157991": (180, 5.0, 0.0),        # J16 JST B5B-XH-A (THT)
    "C160404": (0, 0.0, 0.062),        # J17, J18 JST SM04B-SRSS-TB
    "C37208": (270, 0.0, -6.35),       # J19, J20 listwa 1×6 2,54 mm (THT)
}


def lcsc_z_bom(sciezka):
    m = {}
    for r in csv.DictReader(open(sciezka, encoding="utf-8-sig")):
        for d in r["Designator"].split(","):
            m[d.strip()] = r["LCSC Part #"].strip()
    return m


def koryguj(x, y, rot, lcsc):
    dr, dx, dy = KOREKTY.get(lcsc, (0, 0.0, 0.0))
    t = math.radians(rot)
    return (x + math.cos(t) * dx - math.sin(t) * dy,
            y + math.sin(t) * dx + math.cos(t) * dy,
            (rot + dr) % 360)


def cpl(poz_kicad, bom_jlc):
    """BOM jest obowiązkowy: bez numeru LCSC nie wiadomo, którą korektę zastosować — brak numeru dla któregokolwiek
    oznaczenia z pliku pozycji przerywa pracę (zamiast po cichu pominąć korektę)."""
    lcsc = lcsc_z_bom(bom_jlc)
    wej = list(csv.DictReader(open(poz_kicad, encoding="utf-8")))
    bez_lcsc = [r["Ref"] for r in wej if not lcsc.get(r["Ref"])]
    if bez_lcsc:
        raise SystemExit(f"oznaczenia z pliku pozycji bez numeru LCSC w BOM: {bez_lcsc}")
    wiersze = []
    for r in wej:
        x, y, rot = koryguj(float(r["PosX"]), float(r["PosY"]), float(r["Rot"]), lcsc[r["Ref"]])
        wiersze.append([r["Ref"], f"{x:.4f}mm", f"{y:.4f}mm", "Top" if r["Side"] == "top" else "Bottom", f"{rot:.1f}"])
    return wiersze


def zapisz(wiersze, cel):
    with open(cel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(wiersze)


def sprawdz(poz_kicad, bom_jlc, wzorzec, tol_mm=0.002):
    wz = {r["Designator"]: r for r in csv.DictReader(open(wzorzec, encoding="utf-8-sig"))}
    f = lambda s: float(s.replace("mm", ""))
    zle = []
    nowe = cpl(poz_kicad, bom_jlc)
    brak_w_nowym = sorted(set(wz) - {w[0] for w in nowe})
    zle += [(d, "brak w nowym CPL") for d in brak_w_nowym]
    for d, x, y, _, rot in nowe:
        r = wz.get(d)
        if r is None:
            zle.append((d, "brak we wzorcu"))
            continue
        drot = (float(rot) - float(r["Rotation"])) % 360
        if abs(f(x) - f(r["Mid X"])) > tol_mm or abs(f(y) - f(r["Mid Y"])) > tol_mm or min(drot, 360 - drot) > 0.05:
            zle.append((d, x, y, rot, r["Mid X"], r["Mid Y"], r["Rotation"]))
    return len(nowe), zle


if __name__ == "__main__":
    if sys.argv[1] == "--sprawdz":
        n, zle = sprawdz(*sys.argv[2:5])
        print(f"pozycji: {n}, niezgodnych z wzorcem: {len(zle)}")
        for z in zle:
            print("  ", z)
        sys.exit(1 if zle else 0)
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    w = cpl(sys.argv[1], sys.argv[3])
    zapisz(w, sys.argv[2])
    print(f"CPL JLC z korektami: {len(w)} pozycji → {sys.argv[2]}")
