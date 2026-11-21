# -*- coding: utf-8 -*-
"""Pilot Wnet Rev A — płytka z listy połączeń (pcbnew, KiCad 10, bez GUI).

    python plytka.py uloz   [--netlista kicad/pilot_wnet.net] [--wyjscie kicad]
    python plytka.py trasuj [--wyjscie kicad] [--przebiegi 30]

uloz:   obrys 90 × 100 mm, footprinty z listy połączeń (pola LCSC, DNP), rozmieszczenie z UKLAD,
        klasy sieci, strefy GND na obu warstwach, opisy na warstwie opisu, eksport Specctra DSN.
trasuj: Freerouting CLI (-da: bez danych analitycznych) → import SES → wypełnienie stref → zapis.

Układ współrzędnych płytki: początek w lewym tylnym rogu, x w prawo (90 mm), y do przodu (100 mm),
tylna krawędź (y = 0) leży przy tylnej ściance obudowy (złącza USB-C, RJ45, antena Wi-Fi modułu).
Decyzje: ../DECYZJE.md (D3 antena przy tylnej krawędzi, D7 obrys, D8 kieszeń w ściance).
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys

import pcbnew

from netlista import sexp, wczytaj_netliste, znajdz  # noqa: F401  (parser bez pcbnew)

TU = os.path.dirname(os.path.abspath(__file__))
FP_DIR = os.environ.get("KICAD10_FOOTPRINT_DIR", r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
# Freerouting 2.5.0 jako JAR na przenośnym JRE 25: natywny freerouting-cli.exe 2.5.0 wywraca się w pętli trasowania
# (GraalVM: brak konfiguracji serializacji ComponentOutline, 18.10.2026) i potem wisi bez zużycia CPU.
# JRE toru Rev A z 18.10: jdk-25.0.4.1+1; dotrasowanie v0.1 z 19.11: Temurin JRE 25.0.5+8 (v01/README_v01.md).
# Ścieżki: zmienne PILOT_JAVA i FREEROUTING, domyślnie java z PATH i narzedzia/ obok tego pliku (w .gitignore).
JAVA = os.environ.get("PILOT_JAVA") or shutil.which("java") or "java"
FREEROUTING = os.environ.get("FREEROUTING", os.path.join(TU, "narzedzia", "freerouting-2.5.0.jar"))
SZER, GLEB = 90.0, 100.0
MM = pcbnew.FromMM

# ------------------------------------------------------------------------- rozmieszczenie (mm, stopnie)
# Wartości wyliczone z geometrii footprintów (sonda_fp.py): czoło USB-C i RJ45 0,6/0,5 mm poza tylną
# krawędzią, antena WROOM-1 równo z krawędzią, jej strefa bez miedzi (z footprintu) x 42–90, y 0–6.
UKLAD = {
    # tylna krawędź
    "J1": (12.5, 3.10, 180), "J2": (34.5, 16.81, 180), "D2": (19.0, 1.9, 90), "R50": (19.0, 5.2, 90),
    "U1": (66.0, 12.8, 0),
    # zasilanie (lewy tył)
    "F1": (3.2, 12.5, 90), "D1": (7.6, 12.5, 90), "U2": (13.8, 11.6, 90), "R1": (17.6, 9.6, 90), "R2": (17.6, 12.4, 90),
    "U3": (6.0, 20.5, 0), "L1": (13.0, 20.5, 0), "C1": (2.6, 17.0, 90), "C2": (5.4, 17.0, 90),
    "C3": (13.4, 25.4, 0), "R3": (2.8, 23.6, 90), "R4": (4.8, 23.6, 90), "C4": (6.8, 23.6, 90),
    # Ethernet: tor MDI w trzech rzędach między gniazdem a U4; U4 obrócony pinami TX/RX (1–6) do gniazda
    "U4": (30.0, 34.5, 270),
    "R62": (22.0, 22.6, 0), "R64": (24.4, 22.6, 0), "R63": (26.8, 22.6, 0), "R65": (29.2, 22.6, 0),
    "R57": (31.6, 22.6, 0), "C42": (34.0, 22.6, 0), "C48": (44.5, 12.0, 90), "R82": (44.5, 16.6, 90),
    "R56": (22.0, 24.2, 0), "R54": (24.4, 24.2, 0), "R55": (26.8, 24.2, 0), "R53": (29.2, 24.2, 0),
    "C43": (31.6, 24.2, 0), "C46": (34.0, 24.2, 0), "C47": (36.4, 24.2, 0),
    "R66": (38.6, 25.8, 0), "R67": (38.6, 27.4, 0),
    "R60": (26.4, 28.3, 0), "C34": (33.6, 28.3, 0), "FB1": (21.6, 30.0, 90),
    "C30": (23.7, 32.0, 90), "C31": (23.7, 34.5, 90), "C38": (23.7, 37.3, 90), "C37": (21.9, 34.5, 90),
    "Y1": (30.0, 42.1, 0), "C40": (26.6, 42.1, 90), "C41": (33.4, 42.1, 90), "R59": (30.0, 45.0, 0), "R58": (33.0, 45.0, 0),
    "C32": (36.3, 31.5, 90), "C33": (36.3, 34.0, 90), "C35": (36.3, 36.5, 90), "C36": (38.6, 32.5, 90),
    "R61": (38.3, 38.1, 90), "C39": (40.3, 38.1, 90), "C44": (35.4, 40.2, 0), "C45": (38.0, 41.6, 90),
    "R68": (36.4, 45.0, 0), "R69": (38.8, 45.0, 0),
    # ESP32 (obrys zawężony do modułu w zawez_obrys_modulu): odsprzęganie, EN, USB, piny strapping
    "C5": (53.6, 8.0, 90), "C6": (55.4, 8.6, 90), "R5": (55.0, 10.4, 0), "C7": (55.0, 11.7, 0),
    "R6": (55.0, 22.8, 0), "R7": (55.0, 24.1, 0), "C8": (53.0, 22.8, 0), "C9": (53.0, 24.1, 0),
    "R78": (60.3, 29.2, 90), "R9": (77.5, 24.0, 0), "R51": (78.0, 9.0, 90), "R52": (80.0, 9.0, 90), "C21": (78.0, 12.0, 90),
    # LoRa E22 obrócony o 180°: piny SPI (13–19) do środka płytki, VCC/RXEN/TXEN do lewej krawędzi
    "U6": (13.0, 48.5, 180),
    "C50": (2.6, 54.0, 90), "C51": (2.6, 57.4, 90), "FB2": (10.0, 61.2, 0), "U7": (2.6, 49.5, 90), "C52": (2.6, 46.6, 90),
    "R79": (2.6, 44.6, 90), "R80": (2.6, 42.6, 90), "R76": (27.8, 53.2, 0), "R77": (27.8, 51.4, 0),
    # przyciski serwisowe i nagłówki (prawa krawędź)
    "SW1": (84.0, 32.5, 90), "SW2": (84.0, 42.5, 90),
    "J20": (87.2, 49.0, 0), "J19": (82.0, 49.0, 0),
    "J17": (85.0, 67.5, 90), "J18": (85.0, 76.5, 90),
    # podświetlenie (DNP)
    "U5": (62.0, 66.0, 90), "R30": (55.4, 61.0, 90), "R31": (57.4, 61.0, 90), "C20": (55.4, 66.0, 90),
    # złącza przycisków (przednia krawędź) i joysticka (lewa krawędź)
    "J10": (7.0, 95.5, 0), "J11": (21.0, 95.5, 0), "J12": (35.0, 95.5, 0), "J13": (49.0, 95.5, 0),
    "J14": (63.0, 95.5, 0), "J15": (77.0, 95.5, 0), "J16": (4.6, 72.5, 90),
    # otwory montażowe (H1 przy USB-C łączy płytę stalową z masą — D10)
    # 19.11 (v0.1): x/y 3,5 → 3,6 i 86,5 → 86,4 — pad M3 6,4 mm miał 0,30 mm miedzi od krawędzi przy regule 0,40
    "H1": (3.6, 3.6, 0), "H2": (86.4, 9.6, 0), "H3": (3.6, 86.0, 0), "H4": (86.4, 86.0, 0),
}
# siatki powtarzalnych elementów: (ref, x, y, obrót) dopisywane w zbuduj_uklad()
OTWORY = {"H1": "MountingHole:MountingHole_3.2mm_M3_Pad_Via", "H2": "MountingHole:MountingHole_3.2mm_M3_Pad_Via",
          "H3": "MountingHole:MountingHole_3.2mm_M3_Pad_Via", "H4": "MountingHole:MountingHole_3.2mm_M3_Pad_Via"}


def zbuduj_uklad():
    u = dict(UKLAD)
    # E22: rezystory 200 Ω naprzeciw pinów NSS, SCK, MOSI, MISO, BUSY, DIO1 (po obrocie x = 20), w dwóch kolumnach
    for i, y in enumerate((48.1, 49.4, 50.7, 51.9, 54.5, 55.7)):
        u[f"R{70 + i}"] = (23.0 if i % 2 == 0 else 25.4, y, 0)
    # wejścia: 1 kΩ, 10 kΩ, 10 nF — blok przy złączach, kolumna na kanał
    for i in range(10):
        x = 8.0 + 7.6 * i
        u[f"R{10 + i}"] = (x, 84.6, 90)
        u[f"R{20 + i}"] = (x + 1.9, 84.6, 90)
        u[f"C{10 + i}"] = (x + 3.8, 84.6, 90)
    for k in range(3):
        u[f"U{10 + k}"] = (17.75 + 28.0 * k, 88.8, 0)   # w przerwach między opisami złączy
    # podświetlenie: klucze i rezystory bramek nad złączami
    for i in range(6):
        x = 11.0 + 13.0 * i
        u[f"Q{1 + i}"] = (x, 76.6, 0)
        u[f"R{40 + i}"] = (x + 3.0, 76.6, 90)
    return u


# ------------------------------------------------------------------------- budowa płytki

def odcinek(b, x0, y0, x1, y1, warstwa, szer=0.1):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0)))
    s.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    s.SetLayer(warstwa)
    s.SetWidth(MM(szer))
    b.Add(s)


def napis(b, tekst, x, y, wys=1.0, warstwa=pcbnew.F_SilkS, obrot=0):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(tekst)
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetLayer(warstwa)
    t.SetTextSize(pcbnew.VECTOR2I(MM(wys), MM(wys)))
    t.SetTextThickness(MM(wys * 0.15))
    t.SetTextAngleDegrees(obrot)
    if warstwa == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


def strefa(b, siec, warstwa, margines=0.3):
    z = pcbnew.ZONE(b)
    z.SetLayer(warstwa)
    z.SetNet(siec)
    z.SetLocalClearance(MM(0.3))
    z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.3))
    z.SetThermalReliefSpokeWidth(MM(0.4))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((margines, margines), (SZER - margines, margines), (SZER - margines, GLEB - margines), (margines, GLEB - margines)):
        ol.Append(MM(x), MM(y))
    b.Add(z)
    return z


def zawez_obrys_modulu(f, margines=0.5):
    """Obrys montażowy WROOM-1 z biblioteki obejmuje 15 mm zapasu wokół anteny; ten zapas pilnuje strefa
    bez miedzi z footprintu. Obrys zostaje przy obudowie modułu (18 × 25,5 mm) + margines IPC."""
    for g in list(f.GraphicalItems()):
        if g.GetLayer() == pcbnew.F_CrtYd:
            f.Remove(g)
    x0, y0, x1, y1 = -9.0 - margines, -12.75 - margines, 9.0 + margines, 12.75 + margines
    for (a, b_, c, d) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        s = pcbnew.PCB_SHAPE(f)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a), MM(b_)))
        s.SetEnd(pcbnew.VECTOR2I(MM(c), MM(d)))
        s.SetLayer(pcbnew.F_CrtYd)
        s.SetWidth(MM(0.05))
        f.Add(s)


def klasy_sieci(b):
    ns = b.GetDesignSettings().m_NetSettings
    defs = {
        # 19.11 (v0.1): GND i +3V3 we własnej klasie 0,25 mm — prąd niosą płaszczyzny In1/In2, a Freerouting nie zwęża
        # ścieżek, więc 0,6 mm nie dochodziło do padów W5500 (LQFP-48, raster 0,5 mm); Zasilanie 0,6 → 0,4 mm
        # (+5V/VBUS do ok. 0,65 A z USB). Wynik: 40 → 5 niepołączonych (v01/README_v01.md).
        "Zasilanie": (0.4, 0.2, ["+5V", "VBUS_C", "BUCK_SW"]),
        "Plaszczyzny": (0.25, 0.2, ["+3V3", "GND"]),
        "Ethernet": (0.3, 0.2, ["ETH_TXP", "ETH_TXN", "ETH_RXP", "ETH_RXN"]),
        "USB": (0.3, 0.2, ["USB_D+", "USB_D-"]),
    }
    for nazwa, (szer, odst, sieci) in defs.items():
        nc = pcbnew.NETCLASS(nazwa)
        nc.SetTrackWidth(MM(szer))
        nc.SetClearance(MM(odst))
        nc.SetViaDiameter(MM(0.8 if nazwa == "Zasilanie" else 0.6))
        nc.SetViaDrill(MM(0.4 if nazwa == "Zasilanie" else 0.3))
        ns.SetNetclass(nazwa, nc)
        for s in sieci:
            ns.SetNetclassPatternAssignment(s, nazwa)
    d = ns.GetDefaultNetclass()
    d.SetTrackWidth(MM(0.2))
    d.SetClearance(MM(0.2))
    d.SetViaDiameter(MM(0.6))
    d.SetViaDrill(MM(0.3))


def uloz(arg):
    komp, sieci = wczytaj_netliste(arg.netlista)
    uklad = zbuduj_uklad()
    os.makedirs(arg.wyjscie, exist_ok=True)
    plik = os.path.join(arg.wyjscie, "pilot_wnet.kicad_pcb")
    b = pcbnew.NewBoard(plik)
    ds = b.GetDesignSettings()
    # 4 warstwy (DECYZJE D7, zmiana 18.10): In1 = GND, In2 = +3V3 — na 2 warstwach autorouter zostawiał 17–71 połączeń
    ds.SetCopperLayerCount(4)
    b.SetCopperLayerCount(4)
    ds.SetBoardThickness(MM(1.6))
    ds.m_TrackMinWidth = MM(0.15)
    ds.m_MinClearance = MM(0.15)
    ds.m_ViasMinSize = MM(0.5)
    ds.m_CopperEdgeClearance = MM(0.4)
    klasy_sieci(b)

    # obrys
    for (x0, y0, x1, y1) in ((0, 0, SZER, 0), (SZER, 0, SZER, GLEB), (SZER, GLEB, 0, GLEB), (0, GLEB, 0, 0)):
        odcinek(b, x0, y0, x1, y1, pcbnew.Edge_Cuts, 0.1)

    # sieci
    netinfo = {}
    for nazwa in sieci:
        ni = pcbnew.NETINFO_ITEM(b, nazwa)
        b.Add(ni)
        netinfo[nazwa] = ni
    pin_siec = {(r, p): n for n, lista in sieci.items() for r, p in lista}
    # piny bez sieci: nazwy jak w schemacie (schemat.py → piny_nc.json), żeby DRC widziało zgodność
    import json
    plik_nc = os.path.join(arg.wyjscie, "piny_nc.json")
    for klucz, nazwa_nc in (json.load(open(plik_nc, encoding="utf-8")).items() if os.path.exists(plik_nc) else []):
        r, p = klucz.split("/", 1)
        ni = pcbnew.NETINFO_ITEM(b, nazwa_nc)
        b.Add(ni)
        netinfo[nazwa_nc] = ni
        pin_siec[(r, p)] = nazwa_nc

    brak = []
    for ref, k in sorted(komp.items()):
        lib, nazwa = k["footprint"].split(":")
        sc = os.path.join(TU, "lib", lib + ".pretty") if lib == "pilot_jlc" else os.path.join(FP_DIR, lib + ".pretty")
        f = pcbnew.FootprintLoad(sc, nazwa)
        if f is None:
            brak.append(f"{ref}: {k['footprint']}")
            continue
        if ref == "U1":
            zawez_obrys_modulu(f)
        f.SetReference(ref)
        f.SetValue(k["wartosc"])
        f.SetFPIDAsString(k["footprint"])
        for pn, pw in k["pola"].items():
            if pn in ("LCSC",):
                f.SetField(pn, pw)
        if k["pola"].get("DNP") == "1":
            f.SetDNP(True)
            f.SetExcludedFromPosFiles(True)
        x, y, rot = uklad.get(ref, (45.0, 50.0, 0))
        if ref not in uklad:
            brak.append(f"{ref}: brak pozycji w UKLAD")
        b.Add(f)
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        f.SetOrientationDegrees(rot)
        for pad in f.Pads():
            n = pin_siec.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netinfo[n])
            # przelotki termiczne pod modułem: JLCPCB 2 warstwy — otwór min. 0,3 mm
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and pad.GetDrillSize().x < MM(0.3):
                pad.SetDrillSize(pcbnew.VECTOR2I(MM(0.3), MM(0.3)))
                try:
                    pad.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(MM(0.6), MM(0.6)))   # KiCad 10: stos padów per warstwa
                except TypeError:
                    pad.SetSize(pcbnew.VECTOR2I(MM(0.6), MM(0.6)))
        # oznaczenia drobnych elementów tylko na warstwie montażowej (Fab), opis zostaje czytelny
        if re.match(r"^(R|C)\d", ref) or ref.startswith(("Q", "D2")):
            f.Reference().SetVisible(False)
    # otwory montażowe (bez symbolu w schemacie); H1 z masą
    for ref, fp in OTWORY.items():
        lib, nazwa = fp.split(":")
        f = pcbnew.FootprintLoad(os.path.join(FP_DIR, lib + ".pretty"), nazwa)
        f.SetReference(ref)
        f.SetValue("M3")
        f.SetAttributes(f.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        b.Add(f)
        x, y, _ = uklad[ref]
        f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        for pad in f.Pads():
            pad.SetNet(netinfo["GND"])

    # opisy
    napis(b, "PILOT WNET Rev A", 40.0, 63.0, 1.6)
    napis(b, "Radio Wnet · 2026-10 · projekt wspomagany SI", 40.0, 65.5, 0.9)
    for ref, opis in (("J10", "REC"), ("J11", "PLAY"), ("J12", "WYSLIJ"), ("J13", "SPRAWDZ"), ("J14", "START"), ("J15", "STOP")):
        x, y, _ = uklad[ref]
        napis(b, opis, x + 3.75, y - 3.9, 1.0)
    napis(b, "JOY", 9.5, 67.5, 1.0, obrot=90)
    for ref, opis in (("J17", "OLED"), ("J18", "QWIIC"), ("J19", "EXP"), ("J20", "SERW"), ("SW1", "RST"), ("SW2", "BOOT")):
        x, y, _ = uklad[ref]
        napis(b, opis, x - 4.8, y, 0.9, obrot=90)
    napis(b, "1 GND 2 GORA 3 DOL 4 LEWO 5 PRAWO", 45.0, 50.0, 0.8, pcbnew.B_SilkS)
    napis(b, "Przyciski: 1 SYG 2 GND 3 LED+5V 4 LED-", 45.0, 52.0, 0.8, pcbnew.B_SilkS)

    # płaszczyzny wewnętrzne przed eksportem DSN: Freerouting łączy GND i +3V3 przelotkami do płaszczyzn,
    # a strefy GND na warstwach zewnętrznych dochodzą po eksporcie (wypełniają wolne miejsce)
    gnd = netinfo["GND"]
    strefa(b, gnd, pcbnew.In1_Cu)
    strefa(b, netinfo["+3V3"], pcbnew.In2_Cu)
    dsn = os.path.join(arg.wyjscie, "pilot_wnet.dsn")
    ok = pcbnew.ExportSpecctraDSN(b, dsn)
    strefa(b, gnd, pcbnew.F_Cu)
    strefa(b, gnd, pcbnew.B_Cu)
    pcbnew.SaveBoard(plik, b)
    with open(os.path.join(arg.wyjscie, "fp-lib-table"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('(fp_lib_table\n  (version 7)\n'
                 '  (lib (name "pilot_jlc")(type "KiCad")(uri "${KIPRJMOD}/../lib/pilot_jlc.pretty")(options "")'
                 '(descr "Pilot Wnet: części z biblioteki EasyEDA/LCSC"))\n)\n')
    print("ZAPIS", plik, "DSN", ok, "footprintów", len(list(b.GetFootprints())))
    for x in brak:
        print("UWAGA", x)


def trasuj(arg):
    plik = os.path.join(arg.wyjscie, "pilot_wnet.kicad_pcb")
    dsn = os.path.join(arg.wyjscie, "pilot_wnet.dsn")
    ses = os.path.join(arg.wyjscie, "pilot_wnet.ses")
    env = dict(os.environ, FREEROUTING__USAGE_AND_DIAGNOSTIC_DATA__DISABLE_ANALYTICS="true")
    r = subprocess.run([JAVA, "-jar", FREEROUTING, "--gui.enabled=false", "-de", dsn, "-do", ses,
                        "--router.autorouter.max_passes=" + str(arg.przebiegi), "-mt", "8", "-da", "-l", "en"],
                       stdin=subprocess.DEVNULL,
                       env=env, capture_output=True, text=True, timeout=3600)
    ogon = "\n".join((r.stdout + r.stderr).splitlines()[-25:])
    print(ogon)
    if not os.path.exists(ses):
        sys.exit("brak pliku SES")
    b = pcbnew.LoadBoard(plik)
    print("SES", pcbnew.ImportSpecctraSES(b, ses))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(plik, b)
    print("ZAPIS", plik, "ścieżek", len(list(b.GetTracks())))


def sciezki(arg):
    """Ścieżki footprintów = UUID symboli ze schemat.py (uuid5 z oznaczenia), żeby DRC sprawdzało
    zgodność ze schematem; bez zmiany rozmieszczenia i ścieżek."""
    from schemat import uid
    plik = os.path.join(arg.wyjscie, "pilot_wnet.kicad_pcb")
    b = pcbnew.LoadBoard(plik)
    n = 0
    for f in b.GetFootprints():
        ref = f.GetReference()
        # od 19.11 otwory H1–H4 mają symbole na schemacie (schemat.py OTWORY) — też dostają ścieżkę
        if ref.startswith("H"):
            f.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_3.2mm_M3_Pad_Via"))
        f.SetPath(pcbnew.KIID_PATH("/" + uid("symbol", ref)))
        n += 1
    pcbnew.SaveBoard(plik, b)
    print("ŚCIEŻKI", n)


REGULY_DRU = """(version 1)
# Pilot Wnet Rev A — reguły uzupełniające (możliwości JLCPCB 2 warstwy; strefy GND)
(rule "jedno_zebro_termiczne"
  (condition "A.Type == 'Zone'")
  (constraint min_resolved_spokes 1))
"""


def wykoncz(arg):
    """Po trasowaniu: poszerzenie przewężeń Freeroutingu do 0,15 mm (JLCPCB min. 0,127 mm), przelotki
    zszywające masę na siatce 3 mm tam, gdzie nie ma kolizji, ponowne wypełnienie stref, reguły DRU."""
    plik = os.path.join(arg.wyjscie, "pilot_wnet.kicad_pcb")
    b = pcbnew.LoadBoard(plik)
    # pole LCSC tylko w danych (BOM), nie na warstwie opisu
    for f in b.GetFootprints():
        if f.HasField("LCSC"):
            f.GetField("LCSC").SetVisible(False)
    poszerzone = 0
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetWidth() < MM(0.15):
            t.SetWidth(MM(0.15))
            poszerzone += 1
    gnd = b.FindNet("GND")
    przeszkody = [t for t in b.GetTracks() if t.GetNetCode() != gnd.GetNetCode() or t.GetClass() == "PCB_VIA"]
    pady = [p for f in b.GetFootprints() for p in f.Pads()]
    strefy_zakazu = [z for z in b.Zones() if z.GetIsRuleArea()]
    for f in b.GetFootprints():
        strefy_zakazu += [z for z in f.Zones() if z.GetIsRuleArea()]
    srednica, otwor, odstep = MM(0.6), MM(0.3), MM(0.3)
    nowe = 0
    krok = 3.0
    y = 2.0
    while y < GLEB - 1.5:
        x = 2.0
        while x < SZER - 1.5:
            p = pcbnew.VECTOR2I(MM(x), MM(y))
            if not any(z.GetBoundingBox().Contains(p) for z in strefy_zakazu):
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(p)
                v.SetWidth(srednica)
                v.SetDrill(otwor)
                v.SetNet(gnd)
                ksztalt = v.GetEffectiveShape(pcbnew.F_Cu)
                kolizja = any(o.GetEffectiveShape(pcbnew.F_Cu if o.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu).Collide(ksztalt, odstep)
                              for o in przeszkody if o.GetBoundingBox().GetInflated(MM(1)).Contains(p))
                if not kolizja:
                    # każdy pad jest przeszkodą — także pad SMD sieci GND (do 20.11 pomijany: przelotki wpadały
                    # w pady R4, R52, C48 i pady elementów DNP; audyt fab-02/layout-16 — docs/AUDYT_REV_A.md, poprawka v01/zamowienie_v01.py)
                    kolizja = any(pd.GetEffectiveShape(pcbnew.F_Cu if pd.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu).Collide(ksztalt, odstep)
                                  for pd in pady if pd.GetBoundingBox().GetInflated(MM(1.5)).Contains(p))
                if not kolizja:
                    b.Add(v)
                    przeszkody.append(v)
                    nowe += 1
            x += krok
        y += krok
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(plik, b)
    with open(os.path.join(arg.wyjscie, "pilot_wnet.kicad_dru"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(REGULY_DRU)
    print("POSZERZONE", poszerzone, "PRZELOTKI GND", nowe)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("etap", choices=["uloz", "trasuj", "sciezki", "wykoncz"])
    a.add_argument("--netlista", default="kicad/pilot_wnet.net")
    a.add_argument("--wyjscie", default="kicad", help="katalog projektu KiCada (biblioteki: ${KIPRJMOD}/../lib)")
    a.add_argument("--raporty", default="wyniki")
    a.add_argument("--przebiegi", type=int, default=30)
    arg = a.parse_args()
    {"uloz": uloz, "trasuj": trasuj, "sciezki": sciezki, "wykoncz": wykoncz}[arg.etap](arg)


if __name__ == "__main__":
    main()
