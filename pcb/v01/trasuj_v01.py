# -*- coding: utf-8 -*-
"""Dotrasowanie płytki Pilota Wnet Rev A (pakiet v0.1, 19.11.2026) — etapy pcbnew (KiCad 10, Python KiCada).

Uruchamiać pythonem KiCada z katalogu `pcb` (obok `plytka.py`, `netlista.py`, `schemat.py`):

    python trasuj_v01.py stat  <kat_kicad>
    python trasuj_v01.py dsn   <kat_kicad> <tryb> <plik.dsn>
    python trasuj_v01.py ses   <kat_kicad> <tryb> <plik.ses>

tryb:
  plaszczyzny — In1.Cu (GND) i In2.Cu (+3V3) oznaczone jako warstwy zasilania (LT_POWER): sygnały tylko na F.Cu i B.Cu,
                płaszczyzny niecięte; zalecane przez R3/D7 (4 warstwy: In1 = GND, In2 = +3V3).
  sygnal      — jak 18.10: wszystkie 4 warstwy dostępne dla sygnałów.
dsn: z płytki usuwa wszystkie ścieżki i przelotki oraz strefy GND na warstwach zewnętrznych (dochodzą po trasowaniu,
     tak jak w `plytka.py uloz`), rozmieszczenie bez zmian; zapisuje DSN. Płytki NIE zapisuje.
ses: wczytuje płytkę, usuwa stare ścieżki i przelotki (strefy zostają), importuje SES, wypełnia strefy, zapisuje.
     Potem: `python plytka.py wykoncz --wyjscie <kat_kicad>` (poszerzenia, przelotki zszywające, reguły DRU).
"""
import os
import sys
from collections import Counter

import pcbnew


def wczytaj(kat):
    return pcbnew.LoadBoard(os.path.join(kat, "pilot_wnet.kicad_pcb"))


def stat(b, opis):
    c = Counter()
    for t in b.GetTracks():
        c["przelotka" if t.GetClass() == "PCB_VIA" else b.GetLayerName(t.GetLayer())] += 1
    typy = {b.GetLayerName(L): int(b.GetLayerType(L)) for L in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)}
    strefy = Counter((b.GetLayerName(z.GetLayer()), z.GetNetname(), z.GetIsRuleArea()) for z in b.Zones())
    print(opis, "ścieżki/przelotki:", dict(c), "typy warstw:", typy, "strefy:", dict(strefy), flush=True)


def bez_sciezek(b):
    for t in list(b.GetTracks()):
        b.Remove(t)


def tryb_warstw(b, tryb):
    if tryb == "plaszczyzny":
        b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
        b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    elif tryb != "sygnal":
        sys.exit("tryb: plaszczyzny | sygnal")


def main():
    etap, kat = sys.argv[1], sys.argv[2]
    b = wczytaj(kat)
    if etap == "stat":
        stat(b, "PŁYTKA")
        return
    tryb, plik = sys.argv[3], sys.argv[4]
    if etap == "dsn":
        # płytka już wyczyszczona na tekście (czysc_plytke.py): bez ścieżek, przelotek i stref zewnętrznych
        stat(b, "DO DSN")
        print("DSN", pcbnew.ExportSpecctraDSN(b, plik), plik, flush=True)
    elif etap == "ses":
        # płytka wyczyszczona na tekście (bez ścieżek i przelotek, strefy zostają)
        print("SES", pcbnew.ImportSpecctraSES(b, plik), flush=True)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        stat(b, "PO SES")
        pcbnew.SaveBoard(os.path.join(kat, "pilot_wnet.kicad_pcb"), b)
        print("ZAPIS", flush=True)


if __name__ == "__main__":
    main()
