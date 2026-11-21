# -*- coding: utf-8 -*-
"""Rysunki do cięcia laserowego/CNC obudowy Pilota Wnet (arcade) z projekt/arcade.toml.

    python -I -B -X utf8 arkusze_ciecia.py --geometria arcade.toml --wyjscie <katalog>

Wynik: jeden plik SVG na część (jednostki mm, 1 jednostka = 1 mm) i zestawienie czesci.json.
Konwencja kolorów (typowa w laserowniach): czerwony #FF0000 = cięcie na wylot, niebieski #0000FF =
grawer/linia pomocnicza (np. obrys płytki montażowej joysticka), czarny = opis (nie ciąć).
Łączenia: na styk, klej i wkręty — otwory pilotowe na wkręty zaznaczone jako cięcie Ø3.
"""
import argparse
import json
import math
import os
import tomllib

CIECIE = "#FF0000"
GRAWER = "#0000FF"


def svg(nazwa, w, h, elementy, opis):
    marg = 10
    W, H = w + 2 * marg, h + 2 * marg + 14
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="{-marg} {-marg} {W} {H}">',
           f'<title>{nazwa}</title>']
    out += elementy
    out.append(f'<text x="0" y="{h + 9}" font-family="Arial" font-size="5" fill="#000">{opis}</text>')
    out.append("</svg>")
    return "\n".join(out)


def prost(x, y, w, h, kol=CIECIE, r=0):
    return f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{r}" fill="none" stroke="{kol}" stroke-width="0.1"/>'


def kolo(cx, cy, r, kol=CIECIE):
    return f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="none" stroke="{kol}" stroke-width="0.1"/>'


def wielokat(pts, kol=CIECIE):
    p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
    return f'<polygon points="{p}" fill="none" stroke="{kol}" stroke-width="0.1"/>'


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--geometria", required=True)
    a.add_argument("--wyjscie", required=True)
    arg = a.parse_args()
    d = tomllib.load(open(arg.geometria, "rb"))
    o, bl = d["obudowa"], d["blat"]
    W, D, t, tb = o["szerokosc"], o["glebokosc"], o["sciana"], o["dno"]
    kat = math.atan2(o["wys_tyl"] - o["wys_przod"], D)
    L = D / math.cos(kat)
    stos = bl["pleksi"] + bl["grafika"] + bl["plyta"]
    sp = stos / math.cos(kat)
    os.makedirs(arg.wyjscie, exist_ok=True)
    czesci = []

    def zapisz(nazwa, w, h, el, opis, material, grubosc, ilosc=1):
        with open(os.path.join(arg.wyjscie, f"{nazwa}.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg(nazwa, w, h, el, opis))
        czesci.append({"czesc": nazwa, "material": material, "grubosc_mm": grubosc, "wymiar_mm": [round(w, 1), round(h, 1)], "ilosc": ilosc})

    # Blat: u = x + W/2, v' = L/2 - v (rysunek od tyłu do przodu, góra arkusza = tył obudowy)
    def otwory(z_oled):
        el = []
        for p in d["przycisk"]:
            el.append(kolo(p["u"] + W / 2, L / 2 - p["v"], p["srednica"] / 2))
        j = d["joystick"]
        el.append(kolo(j["u"] + W / 2, L / 2 - j["v"], j["otwor"] / 2))
        pm = j["plytka_mont"]
        el.append(prost(j["u"] + W / 2 - pm[0] / 2, L / 2 - j["v"] - pm[1] / 2, pm[0], pm[1], GRAWER))
        if z_oled:
            ow, oh = bl["okno_oled"]
            ol = d["oled"]
            el.append(prost(ol["u"] + W / 2 - ow / 2, L / 2 - ol["v"] - oh / 2, ow, oh, CIECIE, r=1.5))
        return el

    zapisz("blat_1_pleksi", W, L, [prost(0, 0, W, L, r=2)] + otwory(False),
           f"Pleksi bezbarwna {bl['pleksi']} mm (PMMA wylewane), ciąć na wylot czerwone; okno OLED pod pleksi.", "PMMA bezbarwne", bl["pleksi"])
    zapisz("blat_2_grafika", W, L, [prost(0, 0, W, L, r=2)] + otwory(True),
           "Wydruk grafiki (folia/papier) pod pleksi, wycięcia jak w płycie; grafika marki w osobnym pliku.", "folia/papier fotograficzny", bl["grafika"])
    zapisz("blat_3_plyta_nosna", W, L, [prost(0, 0, W, L, r=2)] + otwory(True),
           f"Płyta nośna {bl['plyta']} mm pod przyciski zatrzaskowe (wariant W1, R2); obrys niebieski = płytka JLF-P1, otwory M4 dopiero po pomiarze próbki.", bl.get("material_plyty", "stal / aluminium"), bl["plyta"])
    # Boki: trapez w układzie (y od przodu, z od dołu)
    bok = [(0, 0), (D, 0), (D, o["wys_tyl"] - sp), (0, o["wys_przod"] - sp)]
    h_bok = o["wys_tyl"] - sp
    el_bok = [wielokat([(y, h_bok - z) for y, z in bok])]
    for y in (t / 2, D - t / 2):
        for z in (tb + 10, h_bok * 0.55):
            el_bok.append(kolo(y, h_bok - z, 1.5))
    zapisz("bok", D, h_bok, el_bok, f"Bok ze sklejki {t} mm ×2 (lustrzane odbicie dla prawego); otwory Ø3 = wkręty do przodu/tyłu.", o["material"], t, 2)
    # Przód i tył
    szer_wew = W - 2 * t
    h_p = o["wys_przod"] - sp - tb
    zapisz("przod", szer_wew, h_p, [prost(0, 0, szer_wew, h_p)], f"Przód, sklejka {t} mm; górna krawędź fazowana pod kątem {math.degrees(kat):.1f}°.", o["material"], t)
    h_t = o["wys_tyl"] - sp - tb
    ty = d["tyl"]
    el_t = [prost(0, 0, szer_wew, h_t)]
    for k in ("usb_c", "rj45"):
        c = ty[k]
        el_t.append(prost(c["x"] + szer_wew / 2 - c["w"] / 2, h_t - (c["z"] - tb) - c["h"] / 2, c["w"], c["h"], r=0.8))
    el_t.append(kolo(ty["sma"]["x"] + szer_wew / 2, h_t - (ty["sma"]["z"] - tb), ty["sma"]["d"] / 2))
    zapisz("tyl", szer_wew, h_t, el_t, f"Tył, sklejka {t} mm, wycięcia USB-C, RJ45, SMA (wymiary zweryfikować z płytką).", o["material"], t)
    # Dno
    st = d["stopki"]
    dw, dd = W - 2 * t, D - 2 * t
    el_d = [prost(0, 0, dw, dd)]
    for x in (8, dw / 2, dw - 8):
        for y in (8, dd - 8):
            el_d.append(kolo(x, y, 1.75))
    for dx in (-1, 1):
        for dy in (-1, 1):
            el_d.append(kolo(dw / 2 + dx * (W / 2 - st["odsuniecie"]), dd / 2 + dy * (D / 2 - st["odsuniecie"]), st["srednica"] / 2, GRAWER))
    p = d["plytka"]
    for dx in (-1, 1):
        for dy in (-1, 1):
            el_d.append(kolo(dw / 2 + p["x"] + dx * (p["szer"] / 2 - 4), dd / 2 - p["y"] - dy * (p["gleb"] / 2 - 4), 1.6))
    zapisz("dno", dw, dd, el_d, f"Dno, sklejka {tb} mm: Ø3,5 wkręty do listew, Ø3,2 tulejki płytki M3, niebieskie = stopki.", o["material"], tb)
    json.dump({"geometria": os.path.abspath(arg.geometria), "kat_blatu_deg": round(math.degrees(kat), 2), "czesci": czesci},
              open(os.path.join(arg.wyjscie, "czesci.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(czesci, ensure_ascii=False))


if __name__ == "__main__":
    main()
