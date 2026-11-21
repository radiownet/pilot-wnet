# -*- coding: utf-8 -*-
"""Czyszczenie pliku .kicad_pcb na tekście (bez pcbnew): usuwa ścieżki, łuki i przelotki, opcjonalnie strefy
na warstwach zewnętrznych, i ustawia typ warstw wewnętrznych. Rozmieszczenie, footprinty, obrys i strefy
wewnętrzne zostają bajt w bajt.

    python -I -X utf8 czysc_plytke.py <wej.kicad_pcb> <wyj.kicad_pcb> <tryb> [--bez-stref-zewn]

tryb: plaszczyzny (In1.Cu i In2.Cu jako „power”) | sygnal (bez zmiany typów)
Powód: w KiCadzie 10 (Python 3.11, SWIG) po BOARD.Remove(ścieżka) listy Tracks()/Zones() zwracają gołe
SwigPyObject, więc czyszczenie przez pcbnew nie działa (19.11.2026).
"""
import re
import sys


def elementy(tekst):
    """Dzieli zawartość głównego (kicad_pcb …) na elementy najwyższego poziomu: (start, koniec) w tekście."""
    i = tekst.index("(kicad_pcb") + 1
    glebokosc, start, wynik, w_napisie, esc = 1, None, [], False, False
    for k in range(i, len(tekst)):
        c = tekst[k]
        if w_napisie:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                w_napisie = False
            continue
        if c == '"':
            w_napisie = True
        elif c == "(":
            glebokosc += 1
            if glebokosc == 2:
                start = k
        elif c == ")":
            if glebokosc == 2:
                wynik.append((start, k + 1))
            glebokosc -= 1
            if glebokosc == 0:
                break
    return wynik


def glowa(el):
    return re.match(r"\(\s*([A-Za-z_]+)", el).group(1)


def main():
    wej, wyj, tryb = sys.argv[1], sys.argv[2], sys.argv[3]
    bez_zewn = "--bez-stref-zewn" in sys.argv
    zostaw = "--zostaw-sciezki" in sys.argv   # wariant „kontynuacja”: istniejąca trasa zostaje w DSN
    t = open(wej, "rb").read().decode("utf-8")
    usun, licz = [], {}
    for a, b in elementy(t):
        el = t[a:b]
        g = glowa(el)
        wyrzuc = g in ("segment", "via", "arc") and not zostaw
        if g == "zone" and bez_zewn:
            warstwy = re.search(r'\(layers?\s+((?:"[^"]*"\s*)+)\)', el)
            nazwy = re.findall(r'"([^"]*)"', warstwy.group(1)) if warstwy else []
            regula = "(keepout" in el or "(rule_area" in el
            if not regula and nazwy and all(n in ("F.Cu", "B.Cu") for n in nazwy):
                wyrzuc = True
        if wyrzuc:
            usun.append((a, b))
            licz[g] = licz.get(g, 0) + 1
    # usuwamy od końca razem z poprzedzającymi białymi znakami (wcięcie i koniec linii)
    for a, b in reversed(usun):
        a2 = a
        while a2 > 0 and t[a2 - 1] in " \t\r\n":
            a2 -= 1
        t = t[:a2] + t[b:]
    if tryb == "plaszczyzny":
        t, n = re.subn(r'\((4|6) "(In1\.Cu|In2\.Cu)" signal\)', r'(\1 "\2" power)', t)
        licz["warstwy_power"] = n
    elif tryb != "sygnal":
        sys.exit("tryb: plaszczyzny | sygnal")
    open(wyj, "wb").write(t.encode("utf-8"))
    print("usunięte:", licz)


if __name__ == "__main__":
    main()
