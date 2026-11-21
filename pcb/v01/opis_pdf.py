# -*- coding: utf-8 -*-
"""PDF-y opisu (sitodruku) z SVG KiCada — pakiet v0.1, 20.11.2026.

    python -I -X utf8 opis_pdf.py <katalog wyniki\\montaz> <commit>

Dlaczego nie `kicad-cli pcb export pdf`: ploter PDF KiCada 10.0.1 zapisuje napisy fontem Type3 słowo po słowie i każdą
spację rysuje szerzej niż w Gerberze (napisy wielowyrazowe dłuższe o 1,1–1,8 mm; w PDF „SI” wypadało na padach C20,
w Gerberze nie), a przy kolejności „F.Silkscreen,F.Cu” miedź zakrywała opis. SVG z `kicad-cli pcb export svg
--subtract-soldermask --drill-shape-opt 0` ma geometrię zgodną z Gerberem (opis jako wielokąty przycięte maską, jak
u producenta; bez rysowania otworów, bo KiCad kładzie je na wierzchu i przerywa nimi tusz nad zakrytymi przelotkami).
Skrypt bierze `opis_gora.svg` i `opis_dol.svg` (v01/eksport_v01.py), zmienia kolory warstw na czytelne w druku (opis czarny,
otwarcia maski = pady złote, miedź pod maską jasnoszara, krawędź szara) i składa A4 pionowo w skali dokładnie 2:1
z nagłówkiem, podziałką i etykietą SI. Geometria SVG nie jest zmieniana.
"""
import datetime
import os
import sys

import pymupdf

KOLORY = {
    "gora": {"#F2EDA1": "#000000", "#C83434": "#D6D6D6", "#D864FF": "#C9A227", "#D0D2CD": "#555555"},
    "dol": {"#E8B2A7": "#000000", "#4D7FC4": "#D6D6D6", "#02FFEE": "#C9A227", "#D0D2CD": "#555555"},
}
MASKA = {"gora": "#D864FF", "dol": "#02FFEE"}
MM = 72 / 25.4
SKALA = 2.0
CSS = "* {font-family: sans-serif; font-size: 8pt; line-height: 1.25; margin: 0;} h1 {font-size: 13pt; margin: 0;} " \
      ".ost {color: #BF3300; font-weight: bold; font-size: 9.5pt;} .k {font-size: 11pt;}"


def przekoloruj(svg, strona):
    t = open(svg, encoding="utf-8").read()
    T = t.upper()
    if ("FILL:#000000" in T.replace('<G STYLE="FILL:#000000; FILL-OPACITY:1.0000;STROKE:#000000;', "", 1)
            or "FILL:#FFFFFF" in T or "STROKE:#FFFFFF" in T):
        raise SystemExit("BŁĄD: %s ma narysowane otwory (czarne NPTH albo białe PTH/przelotki) — eksport bez "
                         "--drill-shape-opt 0?" % svg)
    m = MASKA[strona]
    n_maska = t.count("fill:%s; fill-opacity:0.4000" % m)
    if not n_maska:
        raise SystemExit("BŁĄD: %s — nie znalazłem otwarć maski (%s, krycie 0,4)" % (svg, m))
    t = t.replace("fill:%s; fill-opacity:0.4000" % m, "fill:%s; fill-opacity:1.0000" % m)
    for stary, nowy in KOLORY[strona].items():
        if stary not in t:
            raise SystemExit("BŁĄD: w %s brak koloru warstwy %s — zmienił się motyw KiCada?" % (svg, stary))
        t = t.replace(stary, nowy)
    return t, n_maska


def strona_pdf(doc, svg_txt, tytul, linie):
    src = pymupdf.open(stream=svg_txt.encode("utf-8"), filetype="svg")
    pdf_src = pymupdf.open("pdf", src.convert_to_pdf())
    w_mm, h_mm = pdf_src[0].rect.width / MM, pdf_src[0].rect.height / MM
    A4w, A4h = 210 * MM, 297 * MM
    pg = doc.new_page(width=A4w, height=A4h)
    bw, bh = w_mm * SKALA * MM, h_mm * SKALA * MM
    x0, y0 = (A4w - bw) / 2, 68 * MM
    if y0 + bh > A4h - 22 * MM:
        raise SystemExit("BŁĄD: płytka %.1f × %.1f mm nie mieści się na A4 w skali 2:1" % (w_mm, h_mm))
    pg.show_pdf_page(pymupdf.Rect(x0, y0, x0 + bw, y0 + bh), pdf_src, 0)
    pg.draw_rect(pymupdf.Rect(x0, y0, x0 + bw, y0 + bh), color=(0.6, 0.6, 0.6), width=0.3)
    html = "<h1>%s</h1><p class='ost'>SZKIC SI — NIE ZAMAWIAĆ przed przeglądem elektronika i decyzją zespołu projektu</p>" % tytul
    html += "".join("<p>%s</p>" % L for L in linie)
    html += ("<p><span class='k' style='color:#000000'>■</span> opis (sitodruk) &#160; "
             "<span class='k' style='color:#C9A227'>■</span> otwarcia maski (pady) &#160; "
             "<span class='k' style='color:#D6D6D6'>■</span> miedź pod maską &#160; "
             "<span class='k' style='color:#BBBBBB'>□</span> brak miedzi</p>")
    zapas, skala = pg.insert_htmlbox(pymupdf.Rect(15 * MM, 10 * MM, A4w - 15 * MM, y0 - 1.5 * MM), html, css=CSS,
                                     scale_low=1)
    if zapas < 0 or skala < 1:
        raise SystemExit("BŁĄD: nagłówek nie mieści się nad rysunkiem (zapas %.1f pt, skala %.3f)" % (zapas, skala))
    # podziałka: 10 mm płytki = 20 mm na kartce
    ys, xs = y0 + bh + 9 * MM, x0
    pg.draw_line((xs, ys), (xs + 10 * SKALA * MM, ys), color=(0, 0, 0), width=0.8)
    for k in range(11):
        h = 2.2 if k in (0, 5, 10) else 1.2
        x = xs + k * SKALA * MM
        pg.draw_line((x, ys), (x, ys - h * MM), color=(0, 0, 0), width=0.4)
    pg.insert_htmlbox(pymupdf.Rect(xs + 22 * MM, ys - 3.4 * MM, A4w - 15 * MM, ys + 6 * MM),
                      "<p>10 mm płytki (skala 2:1). Drukować w skali 100% — bez „dopasuj do strony”; po wydruku "
                      "podziałka ma mieć 20 mm.</p>", css=CSS)
    return w_mm, h_mm


def main():
    kat, commit = sys.argv[1], sys.argv[2]
    # wersja KiCada z wyniki\kicad_wersja.txt (eksport_v01.py), jeśli jest — od 20.11 eksport w KiCadzie 10.0.8
    wersja = "10"
    plik_wersji = os.path.join(os.path.dirname(os.path.abspath(kat)), "kicad_wersja.txt")
    if os.path.exists(plik_wersji):
        wersja = open(plik_wersji, encoding="utf-8").read().strip() or wersja
    wspolne = [
        "Źródło: płytka Pilot Wnet Rev A @ %s; KiCad %s, "
        "eksport SVG z --subtract-soldermask (opis przycięty na otwarciach maski, jak u producenta) — geometria jak "
        "w Gerberze opisu. Otworów nie rysujemy: pady przewlekane i otwory H1–H4 są pełnymi złotymi polami, 4 złote koła "
        "bez miedzi przy J1 i J2 to otwory NPTH (kołki złączy). Przelotki są zakryte maską, więc tusz nad nimi jest "
        "ciągły — z wyjątkiem 12 przelotek termicznych w padzie masy modułu U1, które od góry są odsłonięte "
        "(okna maski w padzie)." % (commit, wersja),
        "Skala 2:1 (1 mm płytki = 2 mm na kartce). Kolory zmienione dla czytelności druku. Złożył: Claude (SI), 20.11.2026.",
    ]
    gotowe = []
    for strona, tyt, dop in (
        ("gora", "Pilot Wnet Rev A — opis, strona górna (F)", "Gerber: pilot_wnet-F_Silkscreen.gto, F_Mask.gts, F_Cu.gtl."),
        ("dol", "Pilot Wnet Rev A — opis, strona dolna (B), widok od spodu (lustrzany)",
         "Gerber: pilot_wnet-B_Silkscreen.gbo, B_Mask.gbs, B_Cu.gbl. Lewa krawędź rysunku = prawa krawędź płytki widzianej z góry."),
    ):
        svg = os.path.join(kat, "opis_%s.svg" % strona)
        txt, n_maska = przekoloruj(svg, strona)
        doc = pymupdf.open()
        w, h = strona_pdf(doc, txt, tyt, wspolne + [dop])
        n = datetime.datetime.now().astimezone()        # pymupdf.get_pdf_now() bierze strefę czasu letniego
        o = int(n.utcoffset().total_seconds() // 60)
        teraz = n.strftime("D:%Y%m%d%H%M%S") + ("+" if o >= 0 else "-") + "%02d'%02d'" % divmod(abs(o), 60)
        doc.set_metadata({"title": tyt, "author": "Claude (SI) — szkic do przeglądu elektronika",
                          "subject": "Podgląd opisu płytki z SVG KiCada, skala 2:1, commit %s" % commit,
                          "creator": "opis_pdf.py (pymupdf %s)" % pymupdf.VersionBind, "producer": "pymupdf",
                          "keywords": "SZKIC SI, NIE ZAMAWIAĆ", "creationDate": teraz, "modDate": teraz})
        doc.subset_fonts()
        doc.xref_set_key(doc.pdf_catalog(), "ViewerPreferences", "<</PrintScaling/None>>")   # druk w rzeczywistym rozmiarze
        gotowe.append((doc, os.path.join(kat, "opis_%s.pdf" % strona), w, h, n_maska))
    for doc, cel, w, h, n_maska in gotowe:   # zapis dopiero, gdy obie strony przeszły kontrole (para z jednego przebiegu)
        doc.save(cel + ".tmp", garbage=3, deflate=True)
    for doc, cel, w, h, n_maska in gotowe:
        os.replace(cel + ".tmp", cel)
        print("zapis", cel, "| płytka %.2f × %.2f mm, skala 2:1 | otwarć maski przekolorowanych: %d" % (w, h, n_maska))


if __name__ == "__main__":
    main()
