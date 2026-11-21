# -*- coding: utf-8 -*-
"""J1 (USB-C HRO TYPE-C-31-M-12) jako footprint projektowej biblioteki pilot_jlc (pakiet v0.1, 19.11.2026).

    python j1_v01.py <plik.kicad_pcb> <katalog pilot_jlc.pretty>     (Python KiCada 10; zapis płytki w miejscu)

Powód: 19.11 linie opisu J1 wychodzące za krawędź płytki (gniazdo wystaje 0,6 mm poza krawędź) przeniesiono
na F.Fab, przez co footprint różnił się od biblioteki KiCada (DRC lib_footprint_mismatch). Kopia egzemplarza
z płytki (położenie 0,0, obrót 0) staje się footprintem `pilot_jlc:USB_C_Receptacle_HRO_TYPE-C-31-M-12_Pilot`,
a J1 wskazuje na nią. Pady, model 3D i geometria bez zmian.
"""
import sys

import pcbnew

NAZWA = "USB_C_Receptacle_HRO_TYPE-C-31-M-12_Pilot"


def main():
    plik, lib = sys.argv[1], sys.argv[2]
    b = pcbnew.LoadBoard(plik)
    f = next(x for x in b.GetFootprints() if x.GetReference() == "J1")
    try:
        c = pcbnew.FOOTPRINT(f)
    except Exception:
        c = pcbnew.Cast_to_FOOTPRINT(f.Duplicate())
    if c.IsFlipped():
        sys.exit("J1 na spodzie — nieobsługiwane")
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
