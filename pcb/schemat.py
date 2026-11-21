# -*- coding: utf-8 -*-
"""Pilot Wnet Rev A — schemat KiCada 10 z listy połączeń (bez przewodów między częściami).

    python schemat.py [--netlista kicad/pilot_wnet.net] [--wyjscie kicad/pilot_wnet.kicad_sch]

Każdy pin dostaje etykietę sieci na swoim końcu, piny bez sieci — znacznik „nie podłączać”. Symbole stoją
na siatce 2,54 mm w blokach funkcjonalnych (BLOKI). Brak przewodów oznacza, że układ graficzny nie może
przypadkowo zewrzeć sieci (to zrobił schematizer 0.2.0: +3V3 z GND w ERC, 18.10.2026).
UUID symboli liczone z oznaczeń (uuid5), tak samo jak ścieżki footprintów w plytka.py — DRC sprawdza
zgodność płytki ze schematem (--schematic-parity).
"""
import argparse
import os
import re
import sys
import uuid

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
from netlista import sexp, wczytaj_netliste, znajdz  # noqa: E402

KICAD_SYM = os.environ.get("KICAD10_SYMBOL_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
NS = uuid.UUID("6f1c1a0e-0b5e-4a57-9c7e-5049c07a0001")
SIATKA = 2.54


def uid(*klucz):
    return str(uuid.uuid5(NS, "/".join(klucz)))


def wyrownaj(v):
    return round(round(v / SIATKA) * SIATKA, 4)


# (tytuł, wzorzec oznaczeń, kolumna arkusza)
BLOKI = [
    ("Zasilanie: USB-C, ochrona, 3,3 V", r"^(J1|F1|D1|U2|R1|R2|U3|L1|C1|C2|C3|C4|R3|R4)$", 0),
    ("ESP32-S3-WROOM-1-N16R8", r"^(U1|C5|C6|C7|C8|C9|C21|R5|R6|R7|R9|R50|R51|R52|R78|SW1|SW2|D2)$", 0),
    ("LoRa 868 MHz: Ebyte E22-900M22S", r"^(U6|U7|FB2|C5[0-2]|R7\d|R80)$", 0),
    ("Ethernet: W5500 + HR911105A (referencja WIZnet)", r"^(U4|J2|Y1|FB1|R5[3-9]|R6\d|R82|C3\d|C4[0-8])$", 1),
    ("OLED, rozszerzenia, serwis", r"^(J1[7-9]|J20)$", 1),
    ("Wejścia: joystick i przyciski (ESD, filtr RC)", r"^(J1[0-6]|U1[0-2]|R1\d|R2\d|C1\d)$", 2),
    ("Podświetlenie przycisków (DNP)", r"^(U5|C20|R3[01]|Q\d|R4\d)$", 2),
]
FLAGI = ["+5V", "+3V3", "+3V3A", "+3V3_RF", "VBUS_C", "GND"]
OTWORY = ["H1", "H2", "H3", "H4"]                          # otwory montażowe M3 z padem GND (plytka.py OTWORY)
OTWOR_FP = "MountingHole:MountingHole_3.2mm_M3_Pad_Via"


# ------------------------------------------------------------------------- symbole z bibliotek

class Biblioteki:
    def __init__(self):
        self.pliki = {}

    def tekst(self, lib):
        if lib not in self.pliki:
            p = os.path.join(TU, "lib", lib + ".kicad_sym") if lib == "pilot_jlc" else os.path.join(KICAD_SYM, lib + ".kicad_sym")
            self.pliki[lib] = open(p, encoding="utf-8").read()
        return self.pliki[lib]

    def symbol(self, lib, nazwa):
        """Definicja do lib_symbols (spłaszczona, z nazwą Lib:Nazwa) i lista pinów."""
        txt = self.tekst(lib)
        s = wytnij(txt, f'(symbol "{nazwa}"')
        m = re.search(r'\(extends "([^"]+)"\)', s)
        if m:
            rodzic = wytnij(txt, f'(symbol "{m.group(1)}"')
            # ciało rodzica (jednostki *_0_1, *_1_1 i flagi), właściwości dziecka
            props = "".join(wytnij_wszystkie(s, "(property "))
            ciala = "".join(x.replace(f'(symbol "{m.group(1)}_', f'(symbol "{nazwa}_') for x in wytnij_wszystkie(rodzic, '(symbol "', glebokosc=2))
            flagi = "".join(wytnij_wszystkie(rodzic, "(pin_names ") + wytnij_wszystkie(rodzic, "(pin_numbers ") + wytnij_wszystkie(rodzic, "(power"))
            s = f'(symbol "{nazwa}" {flagi} (exclude_from_sim no) (in_bom yes) (on_board yes) {props} {ciala})'
        piny = []
        for p in re.finditer(r'\(pin (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(length ([-\d.]+)\)(.*?)\(name "([^"]*)".*?\(number "([^"]*)"', s, re.S):
            typ, _, x, y, kat, dl, _, nazwa_p, num = p.groups()
            piny.append({"typ": typ, "x": float(x), "y": float(y), "kat": int(float(kat or 0)), "num": num, "nazwa": nazwa_p})
        punkty = [(float(x), float(y)) for x, y in re.findall(r"\((?:start|end|xy|center) ([-\d.]+) ([-\d.]+)\)", s)]
        punkty += [(p["x"], p["y"]) for p in piny]
        xs, ys = [q[0] for q in punkty] or [0.0], [q[1] for q in punkty] or [0.0]
        ramka = (min(xs), min(ys), max(xs), max(ys))
        definicja = s.replace(f'(symbol "{nazwa}"', f'(symbol "{lib}:{nazwa}"', 1)
        return definicja, piny, ramka


def wytnij(txt, naglowek, od=0):
    i = txt.find(naglowek, od)
    if i < 0:
        return None
    d, instr, j = 0, False, i
    while j < len(txt):
        c = txt[j]
        if instr:
            if c == "\\":
                j += 2
                continue
            if c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "(":
            d += 1
        elif c == ")":
            d -= 1
            if d == 0:
                return txt[i:j + 1]
        j += 1
    return None


def wytnij_wszystkie(txt, naglowek, glebokosc=None):
    out, od = [], 1
    while True:
        i = txt.find(naglowek, od)
        if i < 0:
            return out
        w = wytnij(txt, naglowek, i)
        out.append(w)
        od = i + len(w)


# ------------------------------------------------------------------------- elementy pliku

def tekst_pola(nazwa, wart, x, y, ukryte=False, just="left"):
    return (f'(property "{nazwa}" "{wart}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27))'
            f'{" (justify " + just + ")" if just else ""}{" (hide yes)" if ukryte else ""}))')


def etykieta(siec, x, y, kat):
    just = "left bottom" if kat in (0, 90) else "right bottom"
    # etykieta globalna: nazwa sieci bez przedrostka arkusza „/”, tak jak w liście połączeń i na płytce
    return (f'(global_label "{siec}" (shape passive) (at {x:.2f} {y:.2f} {kat}) (fields_autoplaced yes) '
            f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid("etykieta", siec, f"{x:.2f}", f"{y:.2f}")}") '
            f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes))))')


KAT_ETYKIETY = {0: 180, 180: 0, 90: 270, 270: 90}   # kąt pinu w bibliotece → kierunek napisu od końca pinu


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--netlista", default=os.path.join("kicad", "pilot_wnet.net"))
    a.add_argument("--wyjscie", default=os.path.join("kicad", "pilot_wnet.kicad_sch"))
    arg = a.parse_args()
    drzewo = sexp(open(arg.netlista, encoding="utf-8").read())
    komp, sieci = wczytaj_netliste(arg.netlista)
    zrodla = {}
    for c in znajdz(znajdz(drzewo, "components")[0], "comp"):
        ref = next(x[1] for x in c if isinstance(x, list) and x[0] == "ref")
        ls = znajdz(c, "libsource")[0]
        zrodla[ref] = (next(x[1] for x in ls if x[0] == "lib"), next(x[1] for x in ls if x[0] == "part"))
    pin_siec = {(r, p): n for n, lista in sieci.items() for r, p in lista}
    nc_siec = {}

    bib = Biblioteki()
    definicje, elementy = {}, []
    korzen = uid("arkusz", "pilot_wnet")

    def blok_dla(ref):
        for i, (_, wz, _k) in enumerate(BLOKI):
            if re.match(wz, ref):
                return i
        return len(BLOKI)

    grupy = {}
    for ref in sorted(komp, key=lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0))):
        grupy.setdefault(blok_dla(ref), []).append(ref)
    tytuly = [t for t, _, _ in BLOKI] + ["Inne"]
    kolumny = [k for _, _, k in BLOKI] + [1]

    # układ: bloki w kolumnach (szerokość kolumny 200 mm), w bloku pakowanie rzędami
    KOL_SZER, MARG = 380.0, 25.4
    kol_y_ost = {}
    for bi in sorted(grupy, key=lambda b: (kolumny[b], b)):
        refs = grupy[bi]
        kol_x = MARG + KOL_SZER * kolumny[bi]
        kol_y = kol_y_ost.get(kolumny[bi], MARG)
        elementy.append(f'(text "{tytuly[bi]}" (exclude_from_sim no) (at {kol_x:.2f} {kol_y:.2f} 0) '
                        f'(effects (font (size 2.54 2.54) (thickness 0.5) (bold yes)) (justify left bottom)) (uuid "{uid("tytul", str(bi))}"))')
        x, y, wys_rzedu = kol_x, kol_y + 10.16, 0.0
        for ref in refs:
            lib, part = zrodla[ref]
            klucz = f"{lib}:{part}"
            if klucz not in definicje:
                definicje[klucz] = bib.symbol(lib, part)
            _, piny, (x0, y0, x1, y1) = definicje[klucz]
            # komórka: ramka symbolu + miejsce na etykiety (ok. 18 mm z boków z pinami)
            lewe = any(p["kat"] == 0 for p in piny)
            prawe = any(p["kat"] == 180 for p in piny)
            gora = any(p["kat"] == 270 for p in piny)
            dol = any(p["kat"] == 90 for p in piny)
            szer = (x1 - x0) + (20.32 if lewe else 2.54) + (20.32 if prawe else 2.54) + 12.7
            wys = (y1 - y0) + (17.78 if gora else 2.54) + (17.78 if dol else 2.54) + 5.08
            if x + szer > kol_x + KOL_SZER - 5 and x > kol_x:
                x, y, wys_rzedu = kol_x, y + wys_rzedu, 0.0
            sx = wyrownaj(x + (20.32 if lewe else 2.54) - x0)
            sy = wyrownaj(y + (17.78 if gora else 2.54) + y1 + 5.08)
            wys_rzedu = max(wys_rzedu, wys)
            x += szer
            k = komp[ref]
            dnp = k["pola"].get("DNP") == "1"
            pola = [tekst_pola("Reference", ref, sx + x1 + 1.27, sy - y1 - 2.54),
                    tekst_pola("Value", k["wartosc"], sx + x1 + 1.27, sy - y1 - 0.0),
                    tekst_pola("Footprint", k["footprint"], sx, sy, True, None),
                    tekst_pola("Datasheet", "~", sx, sy, True, None),
                    tekst_pola("LCSC", k["pola"].get("LCSC", ""), sx, sy, True, None)]
            piny_uuid = " ".join(f'(pin "{p["num"]}" (uuid "{uid("pin", ref, p["num"])}"))' for p in piny)
            elementy.append(
                f'(symbol (lib_id "{klucz}") (at {sx:.2f} {sy:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) '
                f'(dnp {"yes" if dnp else "no"}) (uuid "{uid("symbol", ref)}") {" ".join(pola)} {piny_uuid} '
                f'(instances (project "pilot_wnet" (path "/{korzen}" (reference "{ref}") (unit 1)))))')
            for p in piny:
                px, py = sx + p["x"], sy - p["y"]
                n = pin_siec.get((ref, p["num"]))
                if n:
                    elementy.append(etykieta(n, px, py, KAT_ETYKIETY.get(p["kat"], 0)))
                else:
                    elementy.append(f'(no_connect (at {px:.2f} {py:.2f}) (uuid "{uid("nc", ref, p["num"])}"))')
                    # nazwa sieci, jaką KiCad nadaje niepodłączonemu pinowi — dla zgodności płytki ze schematem
                    nc_siec[f"{ref}/{p['num']}"] = f"unconnected-({ref}-{p['nazwa']}-Pad{p['num']})"
        kol_y = y + wys_rzedu + 12.7
        kol_y_ost[kolumny[bi]] = kol_y
    kol_x, kol_y = MARG + KOL_SZER, kol_y_ost.get(1, MARG)

    # flagi zasilania (sieci zasilane z elementów biernych: PTC, koraliki ferrytowe)
    defi, piny, _ = bib.symbol("power", "PWR_FLAG")
    definicje["power:PWR_FLAG"] = (defi, piny, None)
    elementy.append(f'(text "Flagi zasilania (ERC)" (exclude_from_sim no) (at {kol_x:.2f} {kol_y:.2f} 0) '
                    f'(effects (font (size 2.54 2.54) (thickness 0.5) (bold yes)) (justify left bottom)) (uuid "{uid("tytul", "flagi")}"))')
    for i, n in enumerate(FLAGI):
        sx, sy = wyrownaj(kol_x + 15.24 + 25.4 * i), wyrownaj(kol_y + 15.24)
        ref = f"#FLG0{i + 1}"
        elementy.append(
            f'(symbol (lib_id "power:PWR_FLAG") (at {sx:.2f} {sy:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) '
            f'(dnp no) (uuid "{uid("flaga", n)}") {tekst_pola("Reference", ref, sx, sy - 6.35, True, None)} '
            f'{tekst_pola("Value", "PWR_FLAG", sx, sy - 3.81, False, None)} {tekst_pola("Footprint", "", sx, sy, True, None)} '
            f'{tekst_pola("Datasheet", "~", sx, sy, True, None)} (pin "1" (uuid "{uid("flaga_pin", n)}")) '
            f'(instances (project "pilot_wnet" (path "/{korzen}" (reference "{ref}") (unit 1)))))')
        elementy.append(etykieta(n, sx, sy, 270))

    # otwory montażowe H1–H4 (pad połączony z GND) — symbole dla zgodności płytki ze schematem (19.11.2026);
    # bez BOM, footprint z plytka.OTWORY, uuid jak pozostałe symbole (ścieżka footprintu = /uid("symbol", ref))
    defi, piny, _ = bib.symbol("Mechanical", "MountingHole_Pad")
    definicje["Mechanical:MountingHole_Pad"] = (defi, piny, None)
    oy = kol_y + 40.64
    elementy.append(f'(text "Otwory montażowe M3 (pad GND)" (exclude_from_sim no) (at {kol_x:.2f} {oy:.2f} 0) '
                    f'(effects (font (size 2.54 2.54) (thickness 0.5) (bold yes)) (justify left bottom)) (uuid "{uid("tytul", "otwory")}"))')
    for i, ref in enumerate(OTWORY):
        sx, sy = wyrownaj(kol_x + 15.24 + 25.4 * i), wyrownaj(oy + 20.32)
        piny_uuid = " ".join(f'(pin "{p["num"]}" (uuid "{uid("pin", ref, p["num"])}"))' for p in piny)
        elementy.append(
            f'(symbol (lib_id "Mechanical:MountingHole_Pad") (at {sx:.2f} {sy:.2f} 0) (unit 1) (exclude_from_sim yes) (in_bom no) (on_board yes) '
            f'(dnp no) (uuid "{uid("symbol", ref)}") {tekst_pola("Reference", ref, sx + 2.54, sy - 2.54)} '
            f'{tekst_pola("Value", "M3", sx + 2.54, sy)} {tekst_pola("Footprint", OTWOR_FP, sx, sy, True, None)} '
            f'{tekst_pola("Datasheet", "~", sx, sy, True, None)} {piny_uuid} '
            f'(instances (project "pilot_wnet" (path "/{korzen}" (reference "{ref}") (unit 1)))))')
        for p in piny:
            elementy.append(etykieta("GND", sx + p["x"], sy - p["y"], KAT_ETYKIETY.get(p["kat"], 0)))

    lib_symbols = "\n".join(d for d, _, _ in definicje.values())
    # strona „User” dopasowana do treści (3 kolumny bloków) zamiast pustej połowy A0
    szer_str = MARG * 2 + KOL_SZER * 3
    wys_str = max(max(kol_y_ost.values()), kol_y + 40.0) + 50.0
    plik = (f'(kicad_sch (version 20250114) (generator "pilot_wnet_schemat") (generator_version "1.0") (uuid "{korzen}") '
            f'(paper "User" {szer_str:.1f} {wys_str:.1f})\n'
            f'(title_block (title "Pilot Wnet Rev A") (date "2026-10-18") (rev "A") (company "Radio Wnet")'
            f' (comment 1 "Schemat wygenerowany z pcb/obwod.py (SKiDL) przez pcb/schemat.py — projekt wspomagany SI")'
            f' (comment 2 "Etykiety sieci zamiast przewodów; DNP = bez montażu w fabryce"))\n'
            f'(lib_symbols\n{lib_symbols}\n)\n' + "\n".join(elementy) +
            '\n(sheet_instances (path "/" (page "1")))\n(embedded_fonts no)\n)\n')
    with open(arg.wyjscie, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(plik)
    import json
    with open(os.path.join(os.path.dirname(arg.wyjscie), "piny_nc.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(nc_siec, fh, ensure_ascii=False, indent=0, sort_keys=True)
    with open(os.path.join(os.path.dirname(arg.wyjscie), "sym-lib-table"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('(sym_lib_table\n  (version 7)\n  (lib (name "pilot_jlc")(type "KiCad")(uri "${KIPRJMOD}/../lib/pilot_jlc.kicad_sym")'
                 '(options "")(descr "Pilot Wnet: symbole z biblioteki EasyEDA/LCSC"))\n)\n')
    print("SCHEMAT", arg.wyjscie, "symboli", sum(1 for e in elementy if e.startswith("(symbol")), "etykiet", sum(1 for e in elementy if e.startswith("(global_label")))


if __name__ == "__main__":
    main()
