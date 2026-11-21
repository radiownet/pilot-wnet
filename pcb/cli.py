# -*- coding: utf-8 -*-
"""Cienka nakładka na kicad-cli (KiCad 10) do wywołań ze skryptów toru: python cli.py <argumenty kicad-cli...>.
Kod wyjścia kicad-cli przechodzi dalej (ERC/DRC z --exit-code-violations: 0 = czysto, 5 = naruszenia)."""
import os
import subprocess
import sys

KICAD_CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
r = subprocess.run([KICAD_CLI] + sys.argv[1:])
print(f"[kicad-cli rc={r.returncode}]")
sys.exit(r.returncode)
