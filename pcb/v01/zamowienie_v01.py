# -*- coding: utf-8 -*-
"""Poprawki płytki przed zamówieniem — pakiet v0.1, 20.11.2026 (Python KiCada 10; sprawdzone w KiCadzie 10.0.8).

    python zamowienie_v01.py kontrola <plik.kicad_pcb> <raport.json>   (tylko odczyt)
    python zamowienie_v01.py popraw   <plik.kicad_pcb> <raport.json>   (zapis płytki)

Poprawki z audytu gotowości i niezależnej recenzji z 20.11.2026 (decyzja zespołu projektu; streszczenie audytu:
docs/AUDYT_REV_A.md). Zakres (bez zmian ścieżek sygnałowych i rozmieszczenia):
  1. Przelotki zszywające GND w padach SMD albo bliżej niż 0,2 mm od miedzi padu SMD (audyt fab-02, layout-03/16,
     recenzja W3): usunięte, jeśli to przelotki masy bez własnych ścieżek (masa padów idzie strefami F/B/In1).
     „Własna ścieżka” = koniec ścieżki w otworze przelotki (promień otworu, nie miedzi): ścieżka padu, która tylko
     przechodzi przez pierścień przelotki (np. R4.2 → (3,872; 22,162)), nie czyni jej przelotką trasowaną. Że po
     usunięciu nic się nie rozłączyło, rozstrzyga DRC (0 niepołączonych), nie ta heurystyka.
     Inne przelotki przy padach (sieci sygnałowe i zasilania z dołączonymi ścieżkami, bez nakładania miedzi) zostają.
  2. Pasta na padach elementów DNP (audyt fab-05/montaz-08, recenzja W2): warstwa F.Paste/B.Paste zdjęta z padów SMD
     footprintów z atrybutem DNP — szablon nie nałoży cyny na pady, których fabryka nie obsadza.
  3. D2 (zielona LED): LCSC C72043 (stan 0 w JLC i LCSC) → C12065 (LITEON LTST-C193TGKT-5A; ten sam footprint
     EasyEDA LED0603-RD i ta sama biegunowość — audyt montaz-03, recenzja W5).
  4. Opis poniżej minimów fabryk (JLC: wysokość 1,0 mm, kreska 0,15 mm; audyt fab-04, recenzja D2): napisy płytki
     mniejsze niż 1,0 / 0,15 mm podniesione do 1,0 / 0,15 mm (SERW, EXP, RST, BOOT, OLED, QWIIC, napis Radio Wnet,
     legendy pinów na stronie B; SERW 0,8 mm — wyjątek niżej). Położenie bez zmian — kolizje rozwiązuje potem
     `opis2_v01.py popraw` (20.11 przesunął „Radio Wnet · …” i „QWIIC”); na końcu toru `zamowienie_v01.py kontrola`
     musi pokazać male_napisy = 0 (opis2 ma awaryjne 0,8 mm, które mogłoby cofnąć minimum).
  5. Tabliczka: tytuł, rewizja A, data, firma Radio Wnet i komentarz „Pakiet v0.1 — szkic wspomagany SI…”
     (w pliku zadania Gerbera było „rev?” — recenzja D4).
Uwaga: „Aktualizuj footprinty z biblioteki” w KiCadzie przywróci pastę na padach DNP — po takiej operacji uruchomić
`popraw` ponownie (21 ostrzeżeń DRC lib_footprint_mismatch dla DNP to skutek pkt 2, zamierzony).
"""
import json
import sys

import pcbnew

MM = pcbnew.FromMM


def mm(v):
    return round(pcbnew.ToMM(v), 4)


def xy(p):
    return (mm(p.x), mm(p.y))


ODSTEP_PRZELOTKA_PAD = 0.2      # mm, miedź przelotki od miedzi padu SMD
MIN_WYS, MIN_KRESKA = 1.0, 0.15  # mm
# „SERW” stoi między listwami J19 i J20 (5,2 mm): przy 1,0 mm opis2_v01.py nie znalazł miejsca (0,109 mm od linii J20).
# Zostaje 0,8 mm (minimum PCBWay; JLC zaleca 1,0) z kreską 0,15 mm.
MIN_WYS_WYJATKI = {"SERW": 0.8}
D2_STARY, D2_NOWY = "C72043", "C12065"


def przelotki_przy_padach(b):
    sciezki = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
    pady = [p for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    wynik = []
    for v in [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]:
        poz = v.GetPosition()
        ksz = v.GetEffectiveShape(pcbnew.F_Cu)
        trafienia = []
        for p in pady:
            if not p.GetBoundingBox().GetInflated(MM(1)).Contains(poz):
                continue
            lay = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            if p.GetEffectiveShape(lay).Collide(ksz, MM(ODSTEP_PRZELOTKA_PAD)):
                f = p.GetParentFootprint()
                trafienia.append({"pad": f"{f.GetReference()}.{p.GetNumber()}", "siec_padu": p.GetNetname(),
                                  "dnp": bool(f.IsDNP()), "nachodzi": bool(p.GetEffectiveShape(lay).Collide(ksz, 0))})
        if not trafienia:
            continue
        # ścieżka „własna” przelotki = koniec ścieżki w otworze przelotki (nie tylko w pobliżu)
        wlasne = [t for t in sciezki if (t.GetStart() - poz).EuclideanNorm() <= v.GetDrillValue() // 2
                  or (t.GetEnd() - poz).EuclideanNorm() <= v.GetDrillValue() // 2]
        zszywajaca = v.GetNetname() == "GND" and not wlasne
        wynik.append({"przelotka": v, "poz": xy(poz), "siec": v.GetNetname(), "pady": trafienia,
                      "wlasne_sciezki": len(wlasne), "do_usuniecia": zszywajaca})
    return wynik


def pasta_dnp(b):
    lista = []
    for f in b.GetFootprints():
        if not f.IsDNP():
            continue
        for p in f.Pads():
            for warstwa in (pcbnew.F_Paste, pcbnew.B_Paste):
                if p.IsOnLayer(warstwa):
                    lista.append((f, p, warstwa))
    return lista


def male_napisy(b):
    return [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT"
            and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
            and (pcbnew.ToMM(d.GetTextHeight()) < MIN_WYS_WYJATKI.get(d.GetText(), MIN_WYS) - 1e-6
                 or pcbnew.ToMM(d.GetTextThickness()) < MIN_KRESKA - 1e-6)]


def raport(b):
    d2 = [f for f in b.GetFootprints() if f.GetReference() == "D2"][0]
    tb = b.GetTitleBlock()
    return {
        "przelotki_przy_padach": [{k: v for k, v in r.items() if k != "przelotka"} for r in przelotki_przy_padach(b)],
        "pady_dnp_z_pasta": [f"{f.GetReference()}.{p.GetNumber()}:{pcbnew.LayerName(w)}" for f, p, w in pasta_dnp(b)],
        "male_napisy": [{"tekst": d.GetText(), "warstwa": pcbnew.LayerName(d.GetLayer()), "wys": mm(d.GetTextHeight()),
                         "kreska": mm(d.GetTextThickness())} for d in male_napisy(b)],
        "d2_lcsc": d2.GetField("LCSC").GetText() if d2.HasField("LCSC") else None,
        "tabliczka": {"tytul": tb.GetTitle(), "rewizja": tb.GetRevision(), "data": tb.GetDate(), "firma": tb.GetCompany()},
    }


def popraw(b):
    """Zmiany przez pcbnew bez usuwania obiektów. Przelotki do usunięcia zwracane jako uuid — usuwa je
    usun_przelotki() na tekście pliku, bo w KiCadzie 10 po BOARD.Remove() listy obiektów (GetFootprints, Zones)
    zwracają gołe SwigPyObject (zob. czysc_plytke.py)."""
    zmiany = {"usuniete_przelotki": [], "pozostawione_przelotki": [], "pasta_zdjeta": 0, "napisy": [], "d2": None,
              "uuid_do_usuniecia": []}
    for r in przelotki_przy_padach(b):
        opis = {k: v for k, v in r.items() if k not in ("przelotka", "do_usuniecia")}
        if r["do_usuniecia"]:
            zmiany["uuid_do_usuniecia"].append(r["przelotka"].m_Uuid.AsString())
            zmiany["usuniete_przelotki"].append(opis)
        else:
            zmiany["pozostawione_przelotki"].append(opis)
    for f, p, w in pasta_dnp(b):
        ls = p.GetLayerSet()
        ls.RemoveLayer(w)
        p.SetLayerSet(ls)
        zmiany["pasta_zdjeta"] += 1
    for d in male_napisy(b):
        przed = (mm(d.GetTextHeight()), mm(d.GetTextThickness()))
        wys = max(pcbnew.ToMM(d.GetTextHeight()), MIN_WYS_WYJATKI.get(d.GetText(), MIN_WYS))
        d.SetTextSize(pcbnew.VECTOR2I(MM(wys), MM(wys)))
        d.SetTextThickness(MM(max(pcbnew.ToMM(d.GetTextThickness()), MIN_KRESKA)))
        zmiany["napisy"].append({"tekst": d.GetText(), "przed": przed, "po": (mm(d.GetTextHeight()), mm(d.GetTextThickness()))})
    d2 = [f for f in b.GetFootprints() if f.GetReference() == "D2"][0]
    if d2.GetField("LCSC").GetText() == D2_STARY:
        d2.GetField("LCSC").SetText(D2_NOWY)
        zmiany["d2"] = f"{D2_STARY} -> {D2_NOWY}"
    tb = b.GetTitleBlock()
    tb.SetTitle("Pilot Wnet")
    tb.SetRevision("A")
    tb.SetDate("2026-11-20")
    tb.SetCompany("Radio Wnet")
    tb.SetComment(0, "Pakiet v0.1 — szkic wspomagany SI, do przeglądu przed zamówieniem")
    b.SetTitleBlock(tb)
    return zmiany


def usun_przelotki(plik, uuidy):
    """Usuwa bloki (via …) o podanych uuid z tekstu płytki; każdy uuid musi wystąpić dokładnie raz."""
    import re
    t = open(plik, encoding="utf-8").read()
    for u in uuidy:
        wzor = re.compile(r"\n\t\(via\n(?:\t\t[^\n]*\n)*?\t\t\(uuid \"" + re.escape(u) + r"\"\)\n\t\)")
        trafienia = wzor.findall(t)
        assert len(trafienia) == 1, (u, len(trafienia))
        t = wzor.sub("", t, count=1)
    with open(plik, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(t)


if __name__ == "__main__":
    tryb, plik, cel = sys.argv[1:4]
    b = pcbnew.LoadBoard(plik)
    wynik = {"przed": raport(b)}
    if tryb == "popraw":
        wynik["zmiany"] = popraw(b)
        pcbnew.SaveBoard(plik, b)
        usun_przelotki(plik, wynik["zmiany"]["uuid_do_usuniecia"])
        b2 = pcbnew.LoadBoard(plik)
        pcbnew.ZONE_FILLER(b2).Fill(b2.Zones())
        pcbnew.SaveBoard(plik, b2)
        wynik["po"] = raport(pcbnew.LoadBoard(plik))
    with open(cel, "w", encoding="utf-8") as fh:
        json.dump(wynik, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in wynik.get("po", wynik["przed"]).items()}, ensure_ascii=False))
    if "zmiany" in wynik:
        z = wynik["zmiany"]
        print("usunięte przelotki:", [(r["poz"], [p["pad"] for p in r["pady"]]) for r in z["usuniete_przelotki"]])
        print("pozostawione:", [(r["poz"], r["siec"], [p["pad"] for p in r["pady"]], r["wlasne_sciezki"]) for r in z["pozostawione_przelotki"]])
        print("pasta zdjęta z padów:", z["pasta_zdjeta"], "| napisy:", len(z["napisy"]), "| D2:", z["d2"])
