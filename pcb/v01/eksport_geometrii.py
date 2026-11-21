# -*- coding: utf-8 -*-
"""Eksport geometrii miedzi płytki do JSON (Python KiCada 10, tylko odczyt).

    python eksport_geometrii.py <plik.kicad_pcb> <wyj.json>

Pady (wielokąt na każdej warstwie miedzi, otwór), ścieżki, przelotki, wypełnione strefy (wielokąty z otworami),
obszary reguł (keepout). Jednostki: mm.
"""
import json
import sys

import pcbnew

MIEDZ = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]


def mm(v):
    return round(pcbnew.ToMM(v), 5)


def pkt(p):
    return [mm(p.x), mm(p.y)]


def linia(lc):
    return [pkt(lc.CPoint(i)) for i in range(lc.PointCount())]


def wielokaty(ps):
    out = []
    for i in range(ps.OutlineCount()):
        zew = linia(ps.COutline(i))
        dziury = [linia(ps.CHole(i, j)) for j in range(ps.HoleCount(i))]
        out.append({"zew": zew, "dziury": dziury})
    return out


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())   # świeże wypełnienie w pamięci (plik bez zmian)
    nazwy = {L: b.GetLayerName(L) for L in MIEDZ}
    wynik = {"pady": [], "sciezki": [], "przelotki": [], "strefy": [], "reguly": []}
    for f in b.GetFootprints():
        for p in f.Pads():
            wpis = {"ref": f.GetReference(), "nr": p.GetNumber(), "siec": p.GetNetname(),
                    "poz": pkt(p.GetPosition()), "atr": int(p.GetAttribute()),
                    "otwor": [mm(p.GetDrillSize().x), mm(p.GetDrillSize().y)], "ksztalt": {}}
            for L in MIEDZ:
                if p.IsOnLayer(L):
                    try:
                        ps = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                    except TypeError:
                        ps = p.GetEffectivePolygon(pcbnew.ERROR_INSIDE)
                    wpis["ksztalt"][nazwy[L]] = wielokaty(ps)
            wynik["pady"].append(wpis)
        for z in f.Zones():
            if z.GetIsRuleArea():
                wynik["reguly"].append({"ref": f.GetReference(), "warstwy": [nazwy[L] for L in MIEDZ if z.IsOnLayer(L)],
                                        "zakaz_sciezek": z.GetDoNotAllowTracks(), "zakaz_przelotek": z.GetDoNotAllowVias(),
                                        "zakaz_miedzi": z.GetDoNotAllowZoneFills(),
                                        "obrys": wielokaty(z.Outline())})
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            wynik["przelotki"].append({"poz": pkt(t.GetPosition()), "sr": mm(t.GetWidth(pcbnew.F_Cu)) if hasattr(t, "GetWidth") else 0.6,
                                       "otwor": mm(t.GetDrillValue()), "siec": t.GetNetname()})
        else:
            wynik["sciezki"].append({"a": pkt(t.GetStart()), "b": pkt(t.GetEnd()), "w": mm(t.GetWidth()),
                                     "warstwa": b.GetLayerName(t.GetLayer()), "siec": t.GetNetname()})
    for z in b.Zones():
        if z.GetIsRuleArea():
            wynik["reguly"].append({"ref": "", "warstwy": [nazwy[L] for L in MIEDZ if z.IsOnLayer(L)],
                                    "zakaz_sciezek": z.GetDoNotAllowTracks(), "zakaz_przelotek": z.GetDoNotAllowVias(),
                                    "zakaz_miedzi": z.GetDoNotAllowZoneFills(), "obrys": wielokaty(z.Outline())})
            continue
        for L in MIEDZ:
            if z.IsOnLayer(L):
                wynik["strefy"].append({"siec": z.GetNetname(), "warstwa": nazwy[L],
                                        "wypelnienie": wielokaty(z.GetFilledPolysList(L))})
    json.dump(wynik, open(sys.argv[2], "w", encoding="utf-8"))
    print("pady", len(wynik["pady"]), "ścieżki", len(wynik["sciezki"]), "przelotki", len(wynik["przelotki"]),
          "strefy", len(wynik["strefy"]), "reguły", len(wynik["reguly"]), flush=True)


if __name__ == "__main__":
    main()
