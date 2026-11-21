# -*- coding: utf-8 -*-
"""Pliki zamówienia dla JLCPCB i PCBWay z wyników eksport_v01.py — pakiet v0.1, 20.11.2026.

    python -I -X utf8 pakiet_zamowienie_v01.py <wyniki> <kicad_pcb> <bom_mpn.csv> <katalog_wyjscia>

Wejście: <wyniki> z eksport_v01.py (pozycje_kicad.csv, bom_kicad.csv, gerber/, montaz/), płytka (pozycje i lista DNP),
BOM z MPN i zamiennikami (v01/bom_v0.1_mpn_zamienniki.csv w repo — producent, MPN, opis, zgodność zamiennika).
Wyjście (katalog_wyjscia):
  jlcpcb/cpl_jlcpcb_v0.1.csv  — CPL z korektami obrotu i środka (korekty_jlc.py) — TYLKO dla JLCPCB
  jlcpcb/bom_jlcpcb_v0.1.csv  — Comment, Designator, Footprint, LCSC Part # (bez DNP)
  pcbway/                     — wariant podstawowy: J19 i J20 (listwy 1×6) lutuje fabryka
  pcbway_promocja_29usd/      — wariant pod promocję montażu 29 USD (≤ 100 lutów THT na zamówienie): J19 i J20
                                niemontowane (lutujemy sami) — usunięte z BOM i CPL, dopisane do listy DNP w uwagach
    w każdym: cpl_pcbway_v0.1.csv (Designator, Mid X, Mid Y, Layer, Rotation — konwencja KiCada, bez korekt JLC),
              bom_pcbway_v0.1.csv (po angielsku: Item, Qty/board, Designators, Manufacturer, MPN, Description, Value,
              Package, Type, LCSC ref, Alternate manufacturer, Alternate MPN — zamiennik tylko „1:1 pin i footprint”),
              dnp_reference_v0.1.csv (elementy niemontowane — osobny plik, nie do zakupu),
              montaz_gora.pdf (rysunek montażowy), ORDER_NOTES_PCBWAY.txt (uwagi do wklejenia w zamówienie)
  pozycje_dnp_reczne_v0.1.csv — elementy DNP z pozycjami (konwencja KiCada) — do późniejszego lutowania ręcznego
  pilot_wnet_v0.1_gerber_NIE_ZAMAWIAC.zip — Gerbery + wiercenia (bez PDF map wierceń)
Kontrole: każdy wiersz BOM PCBWay ma MPN; w BOM PCBWay nie ma polskich liter; CPL JLC ma te same oznaczenia co BOM.
"""
import csv
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import korekty_jlc  # noqa: E402

THT_LCSC = {"C12074", "C144395", "C157991", "C37208"}   # RJ45, JST XH 4/5-pin, listwa 1×6
TYP_SPECJALNY = {"C165948": "SMD + 4 THT shell pins"}   # J1 USB-C: nóżki obudowy przewlekane, bez pasty
LISTWY_SERWISOWE = ("J19", "J20")
# Pola po polsku w BOM z MPN → angielski dla fabryki
WARTOSC_EN = {"zielona": "green"}
OPIS_EN = {
    "C167869": "INDUCTOR 2.2uH +/-20% Isat 5.8A Irms 3.2A DCR 39mOhm 4x4mm",
    "C126818": "PTC RESETTABLE FUSE 1206 hold 1.1A trip 2.2A 8V",
}
POLSKIE = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")


def bom_kicad(wyniki):
    return list(csv.DictReader(open(os.path.join(wyniki, "bom_kicad.csv"), encoding="utf-8")))


def bom_jlc(wyniki, cel):
    n = 0
    with open(cel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for r in bom_kicad(wyniki):
            if r["DNP"].strip():
                continue
            w.writerow([r["Wartosc"], r["Refy"], r["Footprint"].split(":")[-1], r["LCSC"]])
            n += 1
    return n


def cpl_kicad(wyniki, cel, pomin=()):
    wej = [r for r in csv.DictReader(open(os.path.join(wyniki, "pozycje_kicad.csv"), encoding="utf-8"))
           if r["Ref"] not in pomin]
    with open(cel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in wej:
            w.writerow([r["Ref"], f"{float(r['PosX']):.4f}mm", f"{float(r['PosY']):.4f}mm",
                        "Top" if r["Side"] == "top" else "Bottom", f"{float(r['Rot']) % 360:.1f}"])
    return len(wej)


def mpn_mapa(bom_mpn):
    """LCSC → dane producenta z BOM z MPN (pierwszy wiersz z danym numerem)."""
    m = {}
    for r in csv.DictReader(open(bom_mpn, encoding="utf-8-sig")):
        m.setdefault(r["lcsc"].strip(), r)
    return m


def po_angielsku(tekst):
    t = tekst.replace("、", ", ")
    return re.sub(r"(\d),(\d)", r"\1.\2", t)


def wiersz_pcbway(r, d, refy):
    lcsc = r["LCSC"].strip()
    zgodny = d.get("zgodnosc_zamiennika", "").strip().startswith("1:1")
    alt_prod = d.get("zamiennik_producent", "") if zgodny else ""
    alt_mpn = d.get("zamiennik_mpn", "") if zgodny else ""
    return {
        "Qty/board": str(len(refy)), "Designators": ", ".join(refy), "Manufacturer": d.get("producent", ""),
        "MPN": d.get("mpn", ""), "Description": po_angielsku(OPIS_EN.get(lcsc, d.get("opis_karty", r["Wartosc"]))),
        "Value": WARTOSC_EN.get(r["Wartosc"], r["Wartosc"]), "Package": r["Footprint"].split(":")[-1],
        "Type": TYP_SPECJALNY.get(lcsc, "THT" if lcsc in THT_LCSC else "SMD"), "LCSC ref": lcsc,
        "Alternate manufacturer": alt_prod, "Alternate MPN": alt_mpn,
    }


POLA = ["Item", "Qty/board", "Designators", "Manufacturer", "MPN", "Description", "Value", "Package", "Type",
        "LCSC ref", "Alternate manufacturer", "Alternate MPN"]


def bom_pcbway(wyniki, bom_mpn, kat, dodatkowe_dnp=()):
    mp = mpn_mapa(bom_mpn)
    montowane, dnp = [], []
    for r in bom_kicad(wyniki):
        refy = [x.strip() for x in r["Refy"].split(",") if x.strip()]
        d = mp.get(r["LCSC"].strip(), {})
        if r["DNP"].strip():
            dnp.append(wiersz_pcbway(r, d, refy))
            continue
        zost = [x for x in refy if x not in dodatkowe_dnp]
        pom = [x for x in refy if x in dodatkowe_dnp]
        if zost:
            montowane.append(wiersz_pcbway(r, d, zost))
        if pom:
            dnp.append(wiersz_pcbway(r, d, pom))
    for nazwa, wiersze, prefiks in (("bom_pcbway_v0.1.csv", montowane, ""), ("dnp_reference_v0.1.csv", dnp, "DNP-")):
        with open(os.path.join(kat, nazwa), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=POLA)
            w.writeheader()
            for i, r in enumerate(wiersze, 1):
                w.writerow({"Item": f"{prefiks}{i}", **r})
    braki_mpn = [r["LCSC ref"] for r in montowane if not r["MPN"]]
    polskie = [r["Designators"] for r in montowane + dnp if any(POLSKIE.search(str(v)) for v in r.values())]
    assert not braki_mpn, f"BOM PCBWay: wiersze bez MPN {braki_mpn}"
    assert not polskie, f"BOM PCBWay: polskie litery w wierszach {polskie}"
    return {"pozycji": len(montowane), "sztuk/płytkę": sum(int(r["Qty/board"]) for r in montowane),
            "z zamiennikiem 1:1": sum(1 for r in montowane if r["Alternate MPN"]),
            "dnp_pozycji": len(dnp), "dnp_sztuk": sum(int(r["Qty/board"]) for r in dnp)}


def footprinty(kicad_pcb):
    """Footprinty z płytki: ref → (wartość, nazwa footprintu, x, y, obrót, strona, dnp)."""
    t = open(kicad_pcb, encoding="utf-8").read()
    wynik = {}
    for blok in re.split(r"\n\t\(footprint ", t)[1:]:
        nazwa = re.match(r'"([^"]+)"', blok).group(1).split(":")[-1]
        blok = blok.split("\n\t)\n", 1)[0]
        ref = re.search(r'\(property "Reference" "([^"]+)"', blok).group(1)
        war = re.search(r'\(property "Value" "([^"]*)"', blok).group(1)
        at = re.search(r"\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", blok)
        dnp = bool(re.search(r"\n\t\t\(attr[^\n]*\bdnp\b", blok))
        strona = "bottom" if '(layer "B.Cu")' in blok.split("\n\t\t(property", 1)[0] else "top"
        wynik[ref] = (war, nazwa, float(at.group(1)), float(at.group(2)), float(at.group(3) or 0), strona, dnp)
    return wynik


def klucz_ref(ref):
    return (re.sub(r"\d", "", ref), int(re.sub(r"\D", "", ref) or 0))


def pozycje_dnp(fp, cel):
    dnp = sorted((r for r, v in fp.items() if v[6]), key=klucz_ref)
    with open(cel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Ref", "Val", "Package", "PosX", "PosY", "Rot", "Side"])
        for r in dnp:
            war, nazwa, x, y, rot, strona, _ = fp[r]
            w.writerow([r, war, nazwa, f"{x:.4f}", f"{-y:.4f}", f"{rot % 360:.1f}", strona])
    return dnp


def zakresy(refy):
    """['Q1','Q2','Q3','R40'] → 'Q1-Q3, R40'."""
    grupy, wynik = {}, []
    for r in sorted(refy, key=klucz_ref):
        grupy.setdefault(re.sub(r"\d", "", r), []).append(int(re.sub(r"\D", "", r)))
    for p, nr in grupy.items():
        start = prev = nr[0]
        for n in nr[1:] + [None]:
            if n is not None and n == prev + 1:
                prev = n
                continue
            wynik.append(f"{p}{start}" if start == prev else f"{p}{start}-{p}{prev}")
            if n is not None:
                start = prev = n
    return ", ".join(wynik)


def notatka(dnp, listwy_montowane):
    tht = "J2 (RJ45 HanRun HR911105A), J10-J15 (JST B4B-XH-A), J16 (JST B5B-XH-A)"
    if listwy_montowane:
        tht += ", J19 and J20 (1x6 2.54 mm pin headers)"
        listwy = "J19/J20 are populated by the factory in this order variant."
    else:
        listwy = ("J19 and J20 (1x6 2.54 mm pin headers) are NOT populated in this order variant (we solder them "
                  "ourselves) - they are removed from the BOM and pick & place file and listed as DNP above.")
    return f"""PILOT WNET Rev A - order notes for PCBWay (turnkey assembly), 2026-11-20
================================================================
Board: 90 x 100 mm, 4 layers (L1 F.Cu signal, L2 In1 GND plane, L3 In2 +3V3 plane, L4 B.Cu), FR-4 1.6 mm,
outer copper 1 oz, inner copper 0.5 oz (1 oz acceptable), lead-free HASL, green mask, white silkscreen,
no impedance control. Assembly: TOP side only. Quantity: 5 PCBs, 2 assembled.

1. Pick & place (cpl_pcbway_v0.1.csv): KiCad 10 export, units mm, same coordinate origin as the Gerber files
   (top-left corner of the board outline = 0,0; X to the right, Y negative downwards: the board spans
   X 0..90, Y 0..-100). Rotation counter-clockwise positive viewed from top; zero orientation = KiCad / IPC-7351
   library footprints; centroid = KiCad footprint origin. NOT corrected for any other library convention.
   Please confirm the orientation of U1-U4, U7, U10-U12 (pin 1), D1/D2 (cathode) and the JST XH connectors
   J10-J16 (latch side) against the assembly drawing (montaz_gora.pdf) and send photos of the first board.
2. DNP - do NOT populate: {zakresy(dnp)}.
   They are NOT in bom_pcbway_v0.1.csv nor in the pick & place file; for reference only they are listed in
   dnp_reference_v0.1.csv (do not purchase). They are crossed out on the assembly drawing and have no solder
   paste in the paste layer.
3. Through-hole parts soldered by the factory: {tht}.
   J1 (USB-C, SMD) has 4 through-hole shell pins without paste - please hand-solder them.
   {listwy}
4. Components stand close to the board edges and J1 (USB-C), J2 (RJ45) and U1 (antenna) overhang the TOP edge.
   If break-away rails are needed, add them ONLY on the LEFT and RIGHT edges (100 mm sides), with mouse-bites
   (no V-cut along the copper planes), fiducials on the rails.
5. U1 ESP32-S3-WROOM-1-N16R8 and U4 W5500 are MSL 3 (bake if needed). U1 has a ground pad underneath: X-ray
   inspection requested if available. ESP32-S3-WROOM-1 export classification ECCN 5A992.c.
6. Alternates: listed alternates (Alternate MPN column) are pre-checked 1:1 pin and footprint compatible. Passive
   parts (R, C) may be replaced by equivalents with the same value, package, voltage rating, tolerance and
   dielectric. ANY other substitution (ICs, connectors, crystal, fuse, ferrite beads, ESP32 module, LED) requires
   our written approval before production.
7. AI-assisted design (draft reviewed before ordering). Please report any DFM question before production.
"""


def zestaw_pcbway(wyniki, bom_mpn, fp, kat, listwy_montowane):
    os.makedirs(kat, exist_ok=True)
    dodatkowe = () if listwy_montowane else LISTWY_SERWISOWE
    dnp = sorted([r for r, v in fp.items() if v[6]] + list(dodatkowe), key=klucz_ref)
    r = {"cpl": cpl_kicad(wyniki, os.path.join(kat, "cpl_pcbway_v0.1.csv"), pomin=dodatkowe)}
    r.update(bom_pcbway(wyniki, bom_mpn, kat, dodatkowe_dnp=dodatkowe))
    shutil.copy2(os.path.join(wyniki, "montaz", "montaz_gora.pdf"), os.path.join(kat, "montaz_gora.pdf"))
    with open(os.path.join(kat, "ORDER_NOTES_PCBWAY.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(notatka(dnp, listwy_montowane))
    return r


def main(wyniki, kicad_pcb, bom_mpn, wyj):
    os.makedirs(os.path.join(wyj, "jlcpcb"), exist_ok=True)
    raport = {}
    bom_j = os.path.join(wyj, "jlcpcb", "bom_jlcpcb_v0.1.csv")
    raport["bom_jlc_pozycji"] = bom_jlc(wyniki, bom_j)
    w = korekty_jlc.cpl(os.path.join(wyniki, "pozycje_kicad.csv"), bom_j)
    korekty_jlc.zapisz(w, os.path.join(wyj, "jlcpcb", "cpl_jlcpcb_v0.1.csv"))
    raport["cpl_jlc_pozycji"] = len(w)
    fp = footprinty(kicad_pcb)
    raport["pcbway (J19/J20 montowane)"] = zestaw_pcbway(wyniki, bom_mpn, fp, os.path.join(wyj, "pcbway"), True)
    raport["pcbway_promocja_29usd (J19/J20 DNP)"] = zestaw_pcbway(wyniki, bom_mpn, fp, os.path.join(wyj, "pcbway_promocja_29usd"), False)
    raport["pozycje_dnp"] = len(pozycje_dnp(fp, os.path.join(wyj, "pozycje_dnp_reczne_v0.1.csv")))
    kat = os.path.join(wyniki, "gerber")
    cel = os.path.join(wyj, "pilot_wnet_v0.1_gerber_NIE_ZAMAWIAC.zip")
    with zipfile.ZipFile(cel, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(kat)):
            if not n.endswith(".pdf"):
                z.write(os.path.join(kat, n), n)
    raport["zip_plikow"] = len(zipfile.ZipFile(cel).namelist())
    for k, v in raport.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
