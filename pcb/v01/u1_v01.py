# -*- coding: utf-8 -*-
"""U1 (ESP32-S3-WROOM-1-N16R8) jako footprint projektowej biblioteki pilot_jlc (pakiet v0.1, 19.11.2026).

    python u1_v01.py <plik.kicad_pcb> <katalog pilot_jlc.pretty>     (Python KiCada 10; zapis płytki w miejscu)

Powód: moduł ma zawężony obrys montażowy i przelotki termiczne (plytka.zawez_obrys_modulu, 18.10), więc różnił się od
RF_Module:ESP32-S3-WROOM-1 z biblioteki KiCada (DRC lib_footprint_mismatch). Kopia egzemplarza z płytki (położenie 0,0,
obrót 0) staje się footprintem `pilot_jlc:ESP32-S3-WROOM-1_Pilot`, a U1 wskazuje na nią. Pady, model 3D i geometria
bez zmian.
"""
import sys

import pcbnew

NAZWA = "ESP32-S3-WROOM-1_Pilot"


def main():
    plik, lib = sys.argv[1], sys.argv[2]
    b = pcbnew.LoadBoard(plik)
    f = next(x for x in b.GetFootprints() if x.GetReference() == "U1")
    try:
        c = pcbnew.FOOTPRINT(f)
    except Exception:
        c = pcbnew.Cast_to_FOOTPRINT(f.Duplicate())
    if c.IsFlipped():
        sys.exit("U1 na spodzie — nieobsługiwane")
    c.SetOrientationDegrees(0)
    c.SetPosition(pcbnew.VECTOR2I(0, 0))
    c.SetFPID(pcbnew.LIB_ID("", NAZWA))
    c.SetPath(pcbnew.KIID_PATH())
    c.Reference().SetText("REF**")
    c.Value().SetText(NAZWA)
    pcbnew.FootprintSave(lib, c)
    f.SetFPID(pcbnew.LIB_ID("pilot_jlc", NAZWA))
    pcbnew.SaveBoard(plik, b)
    print("ZAPIS", lib, NAZWA, flush=True)


if __name__ == "__main__":
    main()
