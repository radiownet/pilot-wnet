# Pilot Wnet Rev A — płytka (KiCad 10, tor agentowy „kod → KiCad”)

> Projekt przygotował agent SI (Claude) w torze dla inżynierów pracujących agentowo. Każdy krok jest skryptem,
> a wynik to zwykły projekt KiCada 10, który człowiek otwiera i poprawia w GUI. Decyzje: `../DECYZJE.md`.
> Architektura i źródła liczb: `../research/R3_architektura_elektroniki.md` oraz wyciągi z kart producentów
> (workflow 18.10.2026: W5500 + HR911105A wg referencji WIZnet, ESP32-S3-WROOM-1 v1.8 + HDG, Ebyte E22,
> TI TLV62569, biblioteka JLCPCB).

## Tor narzędzi

| Krok | Skrypt | Narzędzie | Wynik |
|---|---|---|---|
| 1. Obwód (źródło prawdy) | `obwod.py` | SKiDL 3.0 | `kicad/pilot_wnet.net`, `kicad/bom_obwod.csv` |
| 2. Schemat | `schemat.py` | własny generator (etykiety sieci, bez przewodów) | `kicad/pilot_wnet.kicad_sch` — ERC: 0 błędów |
| 3. Płytka: obrys, rozmieszczenie, strefy GND, klasy sieci | `plytka.py uloz` | pcbnew (KiCad 10.0.1) | `kicad/pilot_wnet.kicad_pcb`, `.dsn` (plik pośredni, poza repozytorium) |
| 4. Trasowanie | `plytka.py trasuj` | Freerouting 2.5.0 (JAR, JRE 25, `-da`) | ścieżki z `.ses` (plik pośredni, poza repozytorium) |
| 5. Zgodność ze schematem, wykończenie | `plytka.py sciezki`, `plytka.py wykoncz` | pcbnew | ścieżki footprintów = UUID symboli; poszerzenie przewężeń, przelotki zszywające GND, reguły DRU |
| 6. DRC, panel KiKit, pliki JLCPCB, 3D (tor historyczny Rev A z 18.10 — niżej) | `fab.py` | kicad-cli, KiKit 1.8.1 | `wyniki/drc.json`, `kicad/pilot_wnet_panel.kicad_pcb` (poza repozytorium), `wyniki/jlcpcb/`, `wyniki/3d/` |

Kroki 1–6 to tor Rev A z 18.10.2026. Płytka w `kicad/` jest wersją v0.1 (zamówieniową): powstała z wyniku tego toru
dodatkowymi krokami z `v01/README_v01.md` (dotrasowanie, domknięcie, ręczne usunięcie wiszących przelotek, poprawki
opisu i poprawki przed zamówieniem). Panel KiKit 100 × 100 mm z kroku 6 jest torem historycznym (panel z 18.10 miał
starą trasę i nie jest częścią repozytorium) — pliki zamówienia v0.1 robią `v01/eksport_v01.py`
i `v01/pakiet_zamowienie_v01.py` (instrukcja: `../zamowienie/README.md`).

## Uruchamianie

Tor nie zależy od konkretnej maszyny. Potrzebne:

- KiCad 10 (Python KiCada z modułem `pcbnew` i `kicad-cli`); Rev A powstała w 10.0.1, poprawki przed zamówieniem v0.1
  (20.11) w 10.0.8;
- venv z dostępem do `pcbnew`: SKiDL 3.0 (`obwod.py`), KiKit 1.8.1 (tylko `fab.py`), easyeda2kicad (tylko do pobierania
  części z biblioteki EasyEDA/LCSC);
- do `plytka.py trasuj`: Java (JRE) 25 i Freerouting 2.5.0 jako JAR (tor Rev A z 18.10 wskazywał JRE jdk-25.0.4.1+1,
  dotrasowanie v0.1 z 19.11 użyło Temurin JRE 25.0.5+8).

Ścieżki narzędzi ustawiasz zmiennymi środowiskowymi:

| Zmienna | Skrypty | Domyślnie |
|---|---|---|
| `KICAD_CLI` | `cli.py`, `fab.py`, `v01/eksport_v01.py` | `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`; w `eksport_v01.py` instalacja dla użytkownika `%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe` |
| `KICAD10_SYMBOL_DIR` | `obwod.py`, `schemat.py` | `C:\Program Files\KiCad\10.0\share\kicad\symbols` |
| `KICAD10_FOOTPRINT_DIR` | `obwod.py`, `plytka.py`, `sonda_fp.py` | `C:\Program Files\KiCad\10.0\share\kicad\footprints` |
| `KICAD10_3DMODEL_DIR` | KiCad (modele 3D footprintów z biblioteki KiCada); `eksport_v01.py` ustawia ją sam | — |
| `PILOT_JAVA` | `plytka.py trasuj` | `java` z `PATH` |
| `FREEROUTING` | `plytka.py trasuj` | `pcb/narzedzia/freerouting-2.5.0.jar` (katalog `narzedzia/` jest w `.gitignore`) |

Przy KiCadzie zainstalowanym gdzie indziej (instalacja dla użytkownika, Linux, macOS) ustaw zmienne KiCada jawnie.

**UWAGA: każdy krok łańcucha nadpisuje pliki w `kicad/`.** `obwod.py --wyjscie kicad` nadpisuje `pilot_wnet.net`
i `bom_obwod.csv`; `schemat.py` — `pilot_wnet.kicad_sch`, `piny_nc.json` i `sym-lib-table`; `plytka.py uloz`, `trasuj`,
`sciezki` i `wykoncz` — płytkę (`uloz` także `fp-lib-table`, `wykoncz` — `pilot_wnet.kicad_dru`). Uruchomienie łańcucha
w `kicad/` zniszczy płytkę v0.1 (zamówieniową), która powstała dodatkowym torem z `v01/README_v01.md`. Do eksperymentów
używaj osobnego katalogu **obok `lib/`** (np. `kicad_proba/`, jest w `.gitignore`): tabele bibliotek i model 3D E22
wskazują `${KIPRJMOD}/../lib`, a `plytka.py uloz` czyta `piny_nc.json` z katalogu wyjściowego i bez niego DRC zgłosi
niezgodność ze schematem. `schemat.py --wyjscie` przyjmuje ścieżkę pliku, nie katalogu.

Z katalogu `pcb/`, Pythonem KiCada (venv jak wyżej):

```bash
python obwod.py --wyjscie kicad_proba && python schemat.py --netlista kicad_proba/pilot_wnet.net --wyjscie kicad_proba/pilot_wnet.kicad_sch && python plytka.py uloz --netlista kicad_proba/pilot_wnet.net --wyjscie kicad_proba && python plytka.py trasuj --wyjscie kicad_proba --przebiegi 15 && python plytka.py sciezki --wyjscie kicad_proba && python plytka.py wykoncz --wyjscie kicad_proba
```

`fab.py` nie ma parametrów i działa zawsze na `kicad/`: nadpisuje `wyniki/drc.json` (raport płytki v0.1 w repozytorium)
i tworzy panel `kicad/pilot_wnet_panel.*` (w `.gitignore`). Freerouting z `-mt 8` nie jest deterministyczny, więc łańcuch
nie odtworzy płytki bajt w bajt; stanem odniesienia jest `kicad/pilot_wnet.kicad_pcb` w tym repozytorium.

Model 3D modułu E22 (`lib/pilot_jlc.3dshapes/WIRELM-SMD_L20.0-W14.0-H3.0-E22-900M22S.step`, z biblioteki EasyEDA/LCSC
przez easyeda2kicad) **nie jest dołączony** — jego licencja jest nieustalona. Footprint i płytka nadal go wskazują, więc
podgląd 3D, rendery i eksport STEP/GLB (`fab.py`) pokażą moduł E22 bez bryły (KiCad może zgłosić brak modelu); miedzi,
Gerberów ani BOM to nie zmienia.

## Płytka

- 90 × 100 mm, 4 warstwy (In1 GND, In2 +3V3), FR-4 1,6 mm; w torze Rev A z 18.10 panel 100 × 100 mm z listwami 5 mm po bokach (KiKit, `fab.py`) — tor historyczny, zamówienie v0.1: `v01/eksport_v01.py` i `../zamowienie/README.md`.
- Tylna krawędź (y = 0) przy tylnej ściance obudowy: USB-C (J1), RJ45 z transformatorem (J2), antena PCB modułu ESP32-S3-WROOM-1 (strefa bez miedzi z footprintu), dioda stanu D2.
- Przednia krawędź: złącza 6 przycisków JST XH 4-pin (J10–J15: 1 sygnał, 2 GND, 3 LED+ 5 V, 4 LED−); lewa: joystick XH 5-pin (J16: 1 GND, 2 góra, 3 dół, 4 lewo, 5 prawo). Prawa: Qwiic OLED (J17) i Qwiic aplikacji (J18), rozszerzenia (J19), serwis UART (J20), RESET i BOOT.
- Przydział GPIO: tabela w `obwod.py` i `../firmware/micropython/lib/konfig_plytki.py` (zgodne, sprawdzone przez recenzenta firmware).
- Bez montażu (DNP): tor podświetlenia (PCA9685, 6 × AO3400A — D1), moduł E22 (lutowany ręcznie — D4), rezystory opcji, kondensatory USB, feed-forward przetwornicy.

## Znane ograniczenia i decyzje techniczne

- **schematizer 0.2.0** (SKiDL) zwierał sieci (ERC: +3V3 z GND) i zapisywał symbol HR911105A nieczytelny dla KiCada 10.0.1 — zastąpiony `schemat.py`.
- **Freerouting CLI 2.5.0 (natywny)** wywraca się w pętli trasowania (GraalVM: brak konfiguracji serializacji `ComponentOutline`) i wisi — używamy JAR na JRE 25.
- Footprint WROOM-1 ma zawężony obrys montażowy (biblioteczny obejmował 15 mm wokół anteny; strefę RF pilnuje strefa bez miedzi) i przelotki termiczne 0,3 mm (min. JLCPCB dla 2 warstw) — stąd ostrzeżenie `lib_footprint_mismatch`.
- Symbol E22 z easyeda2kicad (C411293) ma ręcznie nadane typy pinów wg karty Ebyte.
- Antena LoRa przez złącze IPEX na module (bez ścieżki RF 50 Ω na płytce bez kontroli impedancji).
- Ostrzeżenia ERC `lib_symbol_mismatch` (AO3400A, TLV62569): spłaszczone symbole dziedziczące, bez wpływu na połączenia.
