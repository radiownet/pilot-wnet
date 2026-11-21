# -*- coding: utf-8 -*-
"""Porządki opisu (silkscreen) płytki Pilota Wnet — pakiet v0.1, 19.11.2026 (Python KiCada 10).

    python opis_v01.py <plik.kicad_pcb>        (zapisuje plik w miejscu)

1. Oznaczenia, które dublują etykiety funkcji obok (J10–J15: REC…STOP, SW1/SW2: RST/BOOT, J17/J18: OLED/QWIIC) — ukryte
   (zostają na warstwie Fab i w rysunkach montażowych).
2. Oznaczenia U1, U3, U4, U5, J2, J19, Y1 oraz napisy „Radio Wnet · 2026-10 · …” i „SERW” — przesunięte w najbliższe
   miejsce, gdzie ich prostokąt nie nachodzi (z zapasem 0,2 mm) na inny opis, pad na tej stronie ani krawędź (0,5 mm).
3. Linie opisu footprintów, które wychodzą za krawędź płytki (U1 przy antenie, J1 USB-C) — przeniesione na F.Fab/B.Fab.
Bez usuwania elementów (BOARD.Remove w KiCadzie 10 psuje listy SWIG) — tylko widoczność, położenie i warstwa.
"""
import math
import sys

import pcbnew

UKRYJ = ["J10", "J11", "J12", "J13", "J14", "J15", "SW1", "SW2", "J17", "J18"]
PRZESUN_REF = ["U1", "U3", "U4", "U5", "J2", "J19", "Y1"]
PRZESUN_TXT = ["Radio Wnet", "SERW"]
SZER, GLEB = 90.0, 100.0
ZAPAS = 0.2
MM = pcbnew.FromMM


def bb_mm(bb):
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def nachodzi(a, b, m=ZAPAS):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


def main():
    p = sys.argv[1]
    b = pcbnew.LoadBoard(p)
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    # 1. ukryj dublujące oznaczenia
    for r in UKRYJ:
        fps[r].Reference().SetVisible(False)
        print("ukryte", r)
    # 3. linie opisu za krawędzią → Fab
    for f in b.GetFootprints():
        for it in f.GraphicalItems():
            L = it.GetLayer()
            if L not in (pcbnew.F_SilkS, pcbnew.B_SilkS) or it.GetClass() != "PCB_SHAPE":
                continue
            x0, y0, x1, y1 = bb_mm(it.GetBoundingBox())
            if x0 < 0.15 or y0 < 0.15 or x1 > SZER - 0.15 or y1 > GLEB - 0.15:
                it.SetLayer(pcbnew.F_Fab if L == pcbnew.F_SilkS else pcbnew.B_Fab)
                print("na Fab:", f.GetReference(), [round(v, 2) for v in (x0, y0, x1, y1)])

    def przeszkody(strona, pomin):
        """Prostokąty: opis (pola, napisy, kształty footprintów) i pady na stronie `strona`."""
        silk = pcbnew.F_SilkS if strona == "F" else pcbnew.B_SilkS
        cu = pcbnew.F_Cu if strona == "F" else pcbnew.B_Cu
        out = []
        for f in b.GetFootprints():
            for it in f.GraphicalItems():
                if it.GetLayer() == silk and id(it) not in pomin:
                    out.append(bb_mm(it.GetBoundingBox()))
            for fld in (f.Reference(), f.Value()):
                if fld.IsVisible() and fld.GetLayer() == silk and fld.GetText() not in pomin:
                    out.append(bb_mm(fld.GetBoundingBox()))
            for pad in f.Pads():
                if pad.IsOnLayer(cu):
                    x0, y0, x1, y1 = bb_mm(pad.GetBoundingBox())
                    out.append((x0 - 0.1, y0 - 0.1, x1 + 0.1, y1 + 0.1))
        for d in b.GetDrawings():
            if d.GetLayer() == silk and d.GetClass() in ("PCB_TEXT", "PCB_SHAPE") and id(d) not in pomin:
                if d.GetClass() == "PCB_TEXT" and d.GetText() in pomin:
                    continue
                out.append(bb_mm(d.GetBoundingBox()))
        return out

    def przesun(obiekt, klucz, strona, kotwica):
        bb0 = bb_mm(obiekt.GetBoundingBox())
        w, h = bb0[2] - bb0[0], bb0[3] - bb0[1]
        przesz = przeszkody(strona, {klucz})
        cx0, cy0 = (bb0[0] + bb0[2]) / 2, (bb0[1] + bb0[3]) / 2
        najl = None
        krok = 0.25
        for ri in range(0, 60):
            for k in range(max(1, 8 * ri)):
                kat = 2 * math.pi * k / max(1, 8 * ri)
                dx, dy = ri * krok * math.cos(kat), ri * krok * math.sin(kat)
                nb = (bb0[0] + dx, bb0[1] + dy, bb0[2] + dx, bb0[3] + dy)
                if nb[0] < 0.5 or nb[1] < 0.5 or nb[2] > SZER - 0.5 or nb[3] > GLEB - 0.5:
                    continue
                if any(nachodzi(nb, o) for o in przesz):
                    continue
                najl = (dx, dy)
                break
            if najl:
                break
        if najl is None:
            print("BRAK MIEJSCA:", klucz)
            return False
        poz = obiekt.GetPosition()
        obiekt.SetPosition(pcbnew.VECTOR2I(poz.x + MM(round(najl[0], 3)), poz.y + MM(round(najl[1], 3))))
        print("przesunięty", klucz, "o", (round(najl[0], 2), round(najl[1], 2)), "mm, rozmiar", (round(w, 2), round(h, 2)))
        return True

    for r in PRZESUN_REF:
        fld = fps[r].Reference()
        strona = "F" if fld.GetLayer() == pcbnew.F_SilkS else "B"
        przesun(fld, fld.GetText(), strona, fps[r].GetPosition())
    for d in b.GetDrawings():
        if d.GetClass() == "PCB_TEXT" and any(d.GetText().startswith(t) for t in PRZESUN_TXT):
            strona = "F" if d.GetLayer() == pcbnew.F_SilkS else "B"
            przesun(d, d.GetText(), strona, d.GetPosition())
    pcbnew.SaveBoard(p, b)
    print("ZAPIS", flush=True)


if __name__ == "__main__":
    main()
