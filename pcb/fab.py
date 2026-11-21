# -*- coding: utf-8 -*-
"""Pilot Wnet Rev A — pliki produkcyjne i 3D (Python z venv: KiCad 10 + KiKit 1.8.1; tor historyczny Rev A z 18.10 —
pliki zamówienia v0.1 robią v01/eksport_v01.py i v01/pakiet_zamowienie_v01.py).

    python fab.py

1. DRC płytki z kontrolą zgodności ze schematem → wyniki/drc.json (kod 5 = naruszenia; zapisujemy raport i idziemy dalej).
2. Panel 100 × 100 mm: płytka 90 × 100 mm + listwy 5 mm po lewej i prawej, 3 znaczniki, 3 otwory technologiczne
   (JLCPCB Standard PCBA wymaga listew — R5 S6; DECYZJE D7) → kicad/pilot_wnet_panel.kicad_pcb (plik wynikowy,
   poza repozytorium).
3. KiKit `fab jlcpcb`: gerbers.zip, bom.csv (bez DNP), pos.csv z korektami obrotów → wyniki/jlcpcb/.
4. Rendery (kicad-cli pcb render) i modele STEP/GLB płytki → wyniki/3d/.
"""
import os
import subprocess
import sys

TU = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
KIKIT = os.path.join(os.path.dirname(sys.executable), "kikit.exe")
PCB = os.path.join("kicad", "pilot_wnet.kicad_pcb")
SCH = os.path.join("kicad", "pilot_wnet.kicad_sch")
PANEL = os.path.join("kicad", "pilot_wnet_panel.kicad_pcb")


def uruchom(nazwa, polecenie, dozwolone=(0,)):
    r = subprocess.run(polecenie, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ogon = "\n".join((r.stdout + r.stderr).strip().splitlines()[-8:])
    print(f"[{nazwa}] rc={r.returncode}\n{ogon}")
    if r.returncode not in dozwolone:
        sys.exit(f"{nazwa}: błąd")
    return r.returncode


def main():
    os.chdir(TU)
    os.makedirs(os.path.join("wyniki", "3d"), exist_ok=True)
    uruchom("drc", [CLI, "pcb", "drc", "--schematic-parity", "--refill-zones", "--format", "json", "--severity-all",
                    "--exit-code-violations", "-o", os.path.join("wyniki", "drc.json"), PCB], (0, 5))
    uruchom("panel", [KIKIT, "panelize",
                      "--layout", "grid; rows: 1; cols: 1",
                      "--framing", "railslr; width: 5mm",
                      "--tooling", "3hole; hoffset: 2.5mm; voffset: 2.5mm; size: 1.152mm",
                      "--fiducials", "3fid; hoffset: 2.5mm; voffset: 8mm; coppersize: 1mm; opening: 2mm",
                      "--cuts", "vcuts; clearance: 0.4mm",
                      "--text", "simple; text: Pilot Wnet Rev A JLCJLCJLCJLC; anchor: mt; voffset: 3mm; hjustify: center; vjustify: center",
                      "--post", "millradius: 1mm",
                      PCB, PANEL])
    uruchom("fab", [KIKIT, "fab", "jlcpcb", "--assembly", "--schematic", SCH, "--field", "LCSC", "--missingError",
                    "--no-drc", PANEL, os.path.join("wyniki", "jlcpcb")])
    for strona in ("top", "bottom"):
        uruchom(f"render_{strona}", [CLI, "pcb", "render", "--side", strona, "--quality", "high", "--perspective",
                                     "-w", "2000", "-h", "1400", "--background", "opaque",
                                     "-o", os.path.join("wyniki", "3d", f"plytka_{strona}.png"), PCB], (0, 1))
    uruchom("render_34", [CLI, "pcb", "render", "--side", "top", "--quality", "high", "--perspective",
                          "--rotate", "-40,0,30", "--zoom", "0.9", "-w", "2000", "-h", "1400", "--background", "opaque",
                          "-o", os.path.join("wyniki", "3d", "plytka_34.png"), PCB], (0, 1))
    uruchom("step", [CLI, "pcb", "export", "step", "--subst-models", "--force", "-o", os.path.join("wyniki", "3d", "pilot_wnet.step"), PCB], (0, 1, 2))
    uruchom("glb", [CLI, "pcb", "export", "glb", "--subst-models", "--include-tracks", "--include-pads", "--include-zones",
                    "--include-silkscreen", "--include-soldermask", "--force", "-o", os.path.join("wyniki", "3d", "pilot_wnet.glb"), PCB], (0, 1, 2))


if __name__ == "__main__":
    main()
