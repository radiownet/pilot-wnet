@echo off
rem uzycie: set "PRACA=<katalog roboczy>" && ses_v01.cmd <tryb>   (plaszczyzny | sygnal); SES w <PRACA>\w_<tryb>\<tryb>.ses
rem <PRACA>\pcb = kopia pcb/ z trasuj_v01.py obok plytka.py (jak w docstringu trasuj_v01.py)
set T=%1
set PY="C:\Program Files\KiCad\10.0\bin\python.exe"
set K="C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
set KICAD10_SYMBOL_DIR=C:\Program Files\KiCad\10.0\share\kicad\symbols
set KICAD10_FOOTPRINT_DIR=C:\Program Files\KiCad\10.0\share\kicad\footprints
set KICAD10_3DMODEL_DIR=C:\Program Files\KiCad\10.0\share\kicad\3dmodels
set PYTHONIOENCODING=utf-8
cd /d "%PRACA%\pcb"
%PY% -X utf8 trasuj_v01.py ses ..\w_%T%\kicad %T% "%PRACA%\w_%T%\%T%.ses"
%PY% -X utf8 plytka.py wykoncz --wyjscie ..\w_%T%\kicad
%PY% -X utf8 trasuj_v01.py stat ..\w_%T%\kicad
%K% pcb drc --schematic-parity --refill-zones --format json --severity-all -o ..\w_%T%\drc.json ..\w_%T%\kicad\pilot_wnet.kicad_pcb
%K% pcb drc --schematic-parity --refill-zones --format report --severity-all -o ..\w_%T%\drc.rpt ..\w_%T%\kicad\pilot_wnet.kicad_pcb
echo == koniec %T%
