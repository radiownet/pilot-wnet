# -*- coding: utf-8 -*-
"""Łączy footprinty otworów H1–H4 z ich nowymi symbolami na schemacie (pakiet v0.1, 19.11.2026; Python KiCada 10).

    python otwory_v01.py <plik.kicad_pcb>      (zapis w miejscu)

Ścieżka footprintu = /uid("symbol", ref) — ten sam przepis co schemat.py i plytka.py sciezki; identyfikator
footprintu z biblioteką `MountingHole:` (wcześniej bez niej). Tylko ustawienia, bez usuwania elementów.
"""
import sys
import uuid

import pcbnew

NS = uuid.UUID("6f1c1a0e-0b5e-4a57-9c7e-5049c07a0001")   # jak w schemat.py


def uid(*klucz):
    return str(uuid.uuid5(NS, "/".join(klucz)))


def main():
    p = sys.argv[1]
    b = pcbnew.LoadBoard(p)
    for f in b.GetFootprints():
        ref = f.GetReference()
        if ref in ("H1", "H2", "H3", "H4"):
            f.SetPath(pcbnew.KIID_PATH("/" + uid("symbol", ref)))
            f.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_3.2mm_M3_Pad_Via"))
            for nazwa, wart in (("SetSheetname", "/"), ("SetSheetfile", "pilot_wnet.kicad_sch")):
                if hasattr(f, nazwa):
                    getattr(f, nazwa)(wart)
            print(ref, f.GetPath().AsString(), f.GetFPID().GetLibNickname(), f.GetFPID().GetLibItemName(), flush=True)
    pcbnew.SaveBoard(p, b)
    print("ZAPIS", flush=True)


if __name__ == "__main__":
    main()
