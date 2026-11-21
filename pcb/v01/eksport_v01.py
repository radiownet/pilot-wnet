# -*- coding: utf-8 -*-
"""Eksport plików produkcyjnych płytki Pilota Wnet (KiCad 10.0.8, kicad-cli) — 20.11.2026.

    python -I -X utf8 eksport_v01.py <katalog_kicad> <katalog_wyniki>

Zastępuje wcześniejszy skrypt wsadowy `pcb_v01.cmd` (KiCad 10.0.1; poza repozytorium): ERC, schemat PDF, netlista, BOM KiCada, DRC,
Gerbery i wiercenia, plik pozycji (bez DNP), rysunki montażowe czytelne dla fabryki (warstwa Fab z oznaczeniami, bez
wartości, elementy DNP przekreślone, skala dopasowana do kartki, nagłówek PL/EN), PDF-y warstw miedzi i SVG opisu.
Bez SVG schematu i bez `pozycje_kicad_z_dnp.csv` (był identyczny z plikiem bez DNP — pozycje DNP robi teraz
pakiet_zamowienie_v01.py z płytki). PDF-y opisu A4 2:1 składa potem `opis_pdf.py <wyniki>\\montaz <commit>`.
Ścieżka kicad-cli: zmienna KICAD_CLI albo domyślna instalacja użytkownika (winget KiCad.KiCad --scope user).
Gerbery z --check-zones (wypełnienie stref sprawdzane przed eksportem, jak w DRC z --refill-zones).
Katalog wyjściowy jest kasowany tylko wtedy, gdy wygląda na poprzedni wynik tego skryptu (kicad_wersja.txt w środku,
żadnego *.kicad_pcb/*.kicad_sch). Kod wyjścia: 0, gdy wszystkie wywołania kicad-cli zakończyły się kodem 0 (także ERC
i DRC — bez --exit-code-violations kod ≠ 0 oznacza awarię, a naruszenia są w JSON-ach i w podsumowaniu na końcu).
"""
import os
import shutil
import subprocess
import sys

KICAD = os.environ.get("KICAD_CLI", os.path.expandvars(r"%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe"))
SHARE = os.path.join(os.path.dirname(os.path.dirname(KICAD)), "share", "kicad")
ENV = dict(os.environ,
           KICAD10_SYMBOL_DIR=os.path.join(SHARE, "symbols"),
           KICAD10_FOOTPRINT_DIR=os.path.join(SHARE, "footprints"),
           KICAD10_3DMODEL_DIR=os.path.join(SHARE, "3dmodels"))

WARSTWY_GERBER = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"


def cli(*args, log=None):
    r = subprocess.run([KICAD, *args], env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
    linia = f"[rc={r.returncode}] kicad-cli {' '.join(args)}"
    print(linia)
    if log is not None:
        log.append({"polecenie": args, "rc": r.returncode, "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]})
    return r.returncode


NAGLOWEK = {
    "gora": ("Pilot Wnet Rev A — rysunek montażowy, strona GÓRNA (widok z góry)",
             "Assembly drawing, TOP side (top view). Designators from F.Fab; pin 1 = chamfered corner / dot. "
             "Crossed-out parts are DNP — do not populate. CPL angles in KiCad convention (CCW positive, top view)."),
    "dol": ("Pilot Wnet Rev A — rysunek montażowy, strona DOLNA (widok od spodu, lustro)",
            "Assembly drawing, BOTTOM side (mirrored, bottom view). No parts are placed on the bottom side."),
}


def naglowek_rysunku(pdf, strona):
    try:
        import pymupdf
    except ImportError:
        print("pymupdf niedostępny — rysunek bez nagłówka")
        return
    pl, en = NAGLOWEK[strona]
    doc = pymupdf.open(pdf)
    pg = doc[0]
    html = (f"<p><b>{pl}</b><br>{en}<br>Pakiet v0.1, 2026-11-20 · Radio Wnet · szkic wspomagany SI (AI-assisted draft) — "
            f"do przeglądu przed zamówieniem</p>")
    pg.insert_htmlbox(pymupdf.Rect(28, 14, pg.rect.width - 28, 70), html,
                      css="* {font-family: sans-serif; font-size: 8pt; line-height: 1.25; margin: 0;}")
    tmp = pdf + ".tmp"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf)


def main(kicad_dir, wyn):
    pcb = os.path.join(kicad_dir, "pilot_wnet.kicad_pcb")
    sch = os.path.join(kicad_dir, "pilot_wnet.kicad_sch")
    if os.path.isdir(wyn):
        zawartosc = [n for _, _, pliki in os.walk(wyn) for n in pliki]
        if any(n.endswith((".kicad_pcb", ".kicad_sch", ".kicad_pro")) for n in zawartosc) or \
                (zawartosc and "kicad_wersja.txt" not in os.listdir(wyn)):
            raise SystemExit(f"odmawiam skasowania {wyn}: to nie wygląda na katalog wyników eksport_v01.py")
        shutil.rmtree(wyn)
    for k in ("gerber", "schemat", "montaz"):
        os.makedirs(os.path.join(wyn, k))
    log = []
    with open(os.path.join(wyn, "kicad_wersja.txt"), "w", encoding="utf-8") as f:
        f.write(subprocess.run([KICAD, "version"], capture_output=True, text=True).stdout)
    # ERC, schemat, BOM
    cli("sch", "erc", "--format", "json", "--severity-all", "-o", os.path.join(wyn, "erc.json"), sch, log=log)
    cli("sch", "erc", "--format", "report", "--severity-all", "-o", os.path.join(wyn, "erc.rpt"), sch, log=log)
    cli("sch", "export", "pdf", "-o", os.path.join(wyn, "schemat", "pilot_wnet_schemat.pdf"), sch, log=log)
    cli("sch", "export", "netlist", "--format", "kicadsexpr", "-o", os.path.join(wyn, "schemat", "pilot_wnet.net"), sch, log=log)
    cli("sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC,${DNP},${QUANTITY}",
        "--labels", "Refy,Wartosc,Footprint,LCSC,DNP,Ilosc", "--group-by", "Value,Footprint,LCSC,${DNP}",
        "--ref-range-delimiter", "", "-o", os.path.join(wyn, "bom_kicad.csv"), sch, log=log)
    # DRC z kontrolą zgodności ze schematem i ponownym wypełnieniem stref
    cli("pcb", "drc", "--schematic-parity", "--refill-zones", "--format", "json", "--severity-all",
        "-o", os.path.join(wyn, "drc.json"), pcb, log=log)
    cli("pcb", "drc", "--schematic-parity", "--refill-zones", "--format", "report", "--severity-all",
        "-o", os.path.join(wyn, "drc.rpt"), pcb, log=log)
    # Gerbery i wiercenia
    g = os.path.join(wyn, "gerber")
    cli("pcb", "export", "gerbers", "-l", WARSTWY_GERBER, "--subtract-soldermask", "--check-zones", "-o", g, pcb, log=log)
    cli("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--excellon-units", "mm",
        "--generate-map", "--map-format", "pdf", "-o", g + os.sep, pcb, log=log)
    # Pozycje (konwencja KiCada; bez DNP — elementy DNP mają też atrybut exclude_from_pos_files)
    cli("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp",
        "-o", os.path.join(wyn, "pozycje_kicad.csv"), pcb, log=log)
    # Rysunki montażowe: Fab z oznaczeniami, bez wartości, DNP przekreślone, skala automatyczna. Bez ramki KiCada
    # (tabliczka zasłaniała J14/J15) — nagłówek PL/EN dopisuje naglowek_rysunku() (pymupdf, jeśli jest).
    m = os.path.join(wyn, "montaz")
    for strona, warstwa, lustro in (("gora", "F.Fab", []), ("dol", "B.Fab", ["--mirror"])):
        cli("pcb", "export", "pdf", "-l", f"{warstwa},Edge.Cuts", "--mode-single", *lustro, "--exclude-value",
            "--crossout-DNP-footprints-on-fab-layers", "--scale", "0", "--black-and-white",
            "-o", os.path.join(m, f"montaz_{strona}.pdf"), pcb, log=log)
        naglowek_rysunku(os.path.join(m, f"montaz_{strona}.pdf"), strona)
    cli("pcb", "export", "pdf", "-l", "F.Cu,In1.Cu,In2.Cu,B.Cu,Edge.Cuts", "--mode-separate", "-o", m + os.sep, pcb, log=log)
    # Opis jak w Gerberze (SVG; PDF A4 2:1 składa v01/opis_pdf.py)
    cli("pcb", "export", "svg", "-l", "F.Cu,F.Mask,F.Silkscreen,Edge.Cuts", "--subtract-soldermask", "--drill-shape-opt", "0",
        "--mode-single", "--fit-page-to-board", "--exclude-drawing-sheet", "-o", os.path.join(m, "opis_gora.svg"), pcb, log=log)
    cli("pcb", "export", "svg", "-l", "B.Cu,B.Mask,B.Silkscreen,Edge.Cuts", "--subtract-soldermask", "--drill-shape-opt", "0",
        "--mirror", "--mode-single", "--fit-page-to-board", "--exclude-drawing-sheet", "-o", os.path.join(m, "opis_dol.svg"), pcb, log=log)
    import json
    with open(os.path.join(wyn, "eksport_log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    bledne = [e for e in log if e["rc"] != 0]
    from collections import Counter
    drc = json.load(open(os.path.join(wyn, "drc.json"), encoding="utf-8"))
    erc = json.load(open(os.path.join(wyn, "erc.json"), encoding="utf-8"))
    print("DRC:", dict(Counter((v["severity"], v["type"]) for v in drc.get("violations", []))),
          "| niepołączone:", len(drc.get("unconnected_items", [])), "| zgodność ze schematem:", len(drc.get("schematic_parity", [])))
    print("ERC:", dict(Counter((v["severity"], v["type"]) for s in erc.get("sheets", []) for v in s.get("violations", []))))
    print(f"wywołań: {len(log)}, z błędem: {len(bledne)}")
    return 1 if bledne else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
