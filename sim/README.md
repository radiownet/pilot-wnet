# Pilot Wnet Rev A — testy obwodów w SPICE (`sim/`)

Testy sprawdzają w ngspice proste obwody analogowe płytki Rev A wobec progów z kart producentów. Wartości
elementów **nie są tu przepisane ręcznie**: `obwody.py` czyta `pcb/obwod.py` drzewem składni (bez importu SKiDL-a) —
tabelę `CZESCI` i wywołania `f.R(...)` / `f.C(...)` w `buduj()` — i z nich generuje decki `.cir`. Zmiana wartości w
`obwod.py` zmienia symulację; przepięcie elementu wywraca `test_0_topologia.py`.

## Uruchomienie

Wymagane: ngspice 47 (`ngspice_con` albo `ngspice` w PATH, albo ścieżka w zmiennej `PILOT_NGSPICE`) i `spicelib`
z PyPI (`pip install spicelib`, najlepiej w osobnym venv). Z katalogu `sim/`:

```
python -I -B -X utf8 -m unittest discover -s . -p "test_*.py"     # wszystkie testy
python -I -B -X utf8 test_b_reset_w5500.py                        # jeden moduł
```

Testy zapisują w `sim/wyniki/` decki `.cir`, przebiegi `.raw`, dzienniki `.log` i zbiorczy `wyniki.json` (te same
liczby drukuje każdy test w wierszu `[obwód] {...}`).

Bez ngspice (albo bez spicelib) działają testy obliczeniowe i topologii, a testy SPICE są pomijane.

Ścieżki można zmienić zmiennymi `PILOT_NGSPICE` (plik `ngspice_con.exe`) i `PILOT_OBWOD` (plik `obwod.py`).

### Narzędzia użyte w przebiegu z 18.10.2026

| narzędzie | gdzie | skąd | sprawdzenie |
|---|---|---|---|
| ngspice 47 (64 bit, KLU) | `bin\ngspice_con.exe` z archiwum (Windows, 64 bit) | `ngspice-47_64.7z` z https://sourceforge.net/projects/ngspice/files/ng-spice-rework/47/ | SHA-1 `498ecc543f73056df1e342f48c3b49e769b9cf2c`, MD5 `550f3a5a278ddcb464470878aa173482` — zgodne z sumami na stronie plików SourceForge |
| spicelib 1.6.4 (+ scipy 1.17.1, psutil 7.2.2, clipin 1.0.0) | osobny venv | PyPI, `pip install --no-cache-dir` | — |

Archiwum `.7z` rozpakował `tar` z Windows 11 (bsdtar 3.8.8, libarchive). Zgłosił 20 wpisów „empty or unreadable
filename” i je pominął; rozpakowało się 920 wpisów, w tym `bin\ngspice_con.exe` (wersja potwierdzona `-v`:
„ngspice-47”, kompilacja 11.08.2026) i 7 bibliotek modeli kodowych `lib\ngspice\*.cm`. Testy z nich nie korzystają.
Gdyby kiedyś brakowało pliku, rozpakować archiwum 7-Zipem.

## Co pokrywają testy

| plik | obwód z `obwod.py` | kryterium (źródło) |
|---|---|---|
| `test_0_topologia.py` | R5/C7, R61/C39, filtr wejścia, R51/R52/C21, R3/R4, C40/C41; lista `WEJSCIA` i `vs += io(1)` | decki zgadzają się z siecią w `buduj()`; elementy zamontowane (nie DNP); przydział pinów Rev A, który zakładają decki (STOP = GPIO3, VSYS_SENSE = GPIO1, żadne wejście na GPIO33–37) |
| `test_a_en_esp32.py` | EN: R5 z 3V3, C7 do masy; GPIO3 (STOP, nóżka konfiguracyjna) | tSTBL ≥ 50 µs od VDD = 2,8 V do EN = 0,75·VDD (ESP32-S3-WROOM-1 v1.8, rys. 4-2, tab. 4-6, tab. 6-3); EN dopiero po VDD = 3,0 V (tab. 6-2); GPIO3 ≥ VIH przy zwolnieniu EN (rozdz. 4.4, tab. 4-2) |
| `test_b_reset_w5500.py` | RSTn: R61 z 3V3, C39 do masy, wewnętrzne RPU 50–112 kΩ | RSTn poniżej VT+ min 1,53 V przez ≥ 500 µs od VDD = 2,97 V (W5500 v1.1.0, s. 59 i 60) |
| `test_c_wejscie_przycisku.py` | złącze → 1 kΩ → GPIO, 10 kΩ do 3V3, 10 nF | VIL 0,25·VDD / VIH 0,75·VDD (WROOM-1 v1.8 tab. 6-3); czasy zboczy; drgania 50 µs; RPU 45 kΩ |
| `test_d_dzielnik_vsys.py` | R51/R52 100 k/100 k, C21 100 nF na GPIO1 | ustalanie, błąd od upływu 50 nA, zakres ATTEN3 0–2900 mV i błąd ±50 mV (ESP32-S3 Series v2.2, tab. 5-6) |
| `test_e_dzielnik_fb.py` | R3 100 k / R4 22 k, VFB 0,588/0,6/0,612 V | 3,327 V nominalnie; narożniki i Monte Carlo (2000) w 3,0–3,6 V (TI SLVSDG1C tab. 6.5; WROOM-1 tab. 6-2) |
| `test_f_kwarc_w5500.py` | C40/C41 18 pF, kwarc CL 18 pF | obliczenie CL_ef i odstrojenia (W5500 v1.1.0, s. 60: ±30 ppm, C0 ≤ 7 pF, CL 18 pF) |

Testy oznaczone `expectedFailure` to **wymagania, których obecny projekt nie spełnia** — zostawione celowo, żeby
było je widać w każdym przebiegu („expected failures=5”: b) rampa 8 ms, c) zwarcie i rozwarcie 50 µs, f) dwa
przypadki budżetu ppm). Po poprawce obwodu test zgłosi „unexpected success” i
wtedy zdejmuje się dekorator.

## Wyniki (przebieg 18.10.2026, ngspice 47, Windows 64 bit)

`Ran 32 tests … OK (expected failures=5)` (przebieg po recenzji; liczby bez zmian względem pierwszego przebiegu). Liczby z `wyniki/wyniki.json`:

**a) EN ESP32-S3** (rampa liniowa 0 → 3,3 V w czasie Tr; upływ 50 nA na niekorzyść, CIN 2 pF)

| Tr | C7 | VDD = 2,8 V | EN = 0,75·VDD | tSTBL |
|---|---|---|---|---|
| 0,5 ms | 1 µF | 0,42 ms | 14,11 ms | 13 684 µs |
| 0,8 ms (tSS TLV62569DBV) | 1 µF | 0,68 ms | 14,26 ms | 13 581 µs |
| 5 ms | 1 µF | 4,24 ms | 16,46 ms | 12 218 µs |
| 5 ms | 0,5 µF | 4,24 ms | 9,64 ms | 5 393 µs |

Granica (bisekcja): tSTBL ≥ 50 µs do Tr = 46,1 ms (C7 nominalnie) i 22,9 ms (połowa pojemności).
GPIO3 w chwili zwolnienia EN: 3,30 V we wszystkich przypadkach.

**b) Reset W5500** — czas RSTn < VT+ od VDD = 2,97 V (wymagane ≥ 500 µs).
Scenariusz najgorszy: R61 −1 %, RPU = 50 kΩ, C39 = 0,5 µF, upływ 1 µA do węzła.

| Tr | nominalny (VT+ min / typ / max) | najgorszy (VT+ min) |
|---|---|---|
| 0,5 ms | 5 315 / 5 882 / 6 376 µs | 2 357 µs |
| 0,8 ms | 5 196 / 5 764 / 6 258 µs | 2 241 µs |
| 5 ms | 3 631 / 4 199 / 4 692 µs | 804 µs |

Granica: 500 µs utrzymane do Tr = 14,9 ms (nominalnie) i **6,0 ms (najgorszy)** — wymaganie 5 ms spełnione,
wymaganie robocze 8 ms (jak w a) nie (oczekiwana porażka).

**c) Wejście przycisku** — zwolniony 3,30 V, wciśnięty 0,300 V (z RPU 45 kΩ: 0,359 V; VIL = 0,825 V).
Po wciśnięciu VIL po 15,9 µs (opadanie 90→10 % 20,0 µs); po zwolnieniu VIH po 129,1 µs (narastanie 10→90 %
219,8 µs). Drgnięcia: rozwarcie 50 µs przy wciśniętym podnosi GPIO do 1,48 V (< VIH, ale > VIL — strefa
nieokreślona); zwarcie 50 µs przy zwolnionym ściąga GPIO do 0,31 V (pełne zbocze). RC tłumi bez wejścia w
strefę nieokreśloną tylko zwarcia ≤ 2,9 µs i rozwarcia ≤ 19,2 µs; rozwarcie nie dochodzi do VIH do 129 µs.

**d) VSYS** — 2,500 V przy 5,00 V; τ = 5,0 ms; do 1 LSB (0,71 mV) po 40,9 ms, do 0,1 % po 34,6 ms.
Upływ ±50 nA: ±2,50 mV na GPIO1. Najwyższe napięcie przy 5,25 V i 1 %: 2,651 V (< 2,9 V); rozrzut
współczynnika 0,495–0,505 (2,0 %). Próbkowanie (Cs = 10 pF, założenie): −0,0125 mV przy 10 Hz, −1,25 mV
przy 1 kHz, −119 mV przy ciągłych 100 kSPS.

**e) FB TLV62569** — nominalnie 3,3273 V (obliczenie 3,32727 V). Narożniki (R ±1 %, VFB 0,588/0,612 V):
3,2078–3,4500 V. Monte Carlo 2000 (rozkład równomierny): 3,2221–3,4409 V, średnia 3,3271 V, σ = 45,2 mV.
Wszystko w 3,0–3,6 V (ESP32-S3) i 2,97–3,63 V (W5500).

**f) Kwarc W5500** — 2 × 18 pF szeregowo = 9 pF; z pasożytniczymi 2–6 pF CL_ef = 11–15 pF wobec CL = 18 pF.
Odstrojenie (założone C1 3–8 fF, C0 2–7 pF): od +8,2 do +107,7 ppm; środek założeń +41,7 ppm; z tolerancją
±30 ppm do +137,7 ppm wobec budżetu ±50 ppm. Dla CL = 18 pF kondensatory powinny mieć 2·(CL − Cpas) =
24–32 pF; przy 2 × 27 pF środek założeń daje +3,2 ppm.

## Wnioski dla projektu

1. **Reset W5500 ma mały zapas przy wolnym narastaniu 3V3.** W najgorszym scenariuszu 500 µs mieści się tylko
   do rampy 6,0 ms (przy 5 ms zostaje 804 µs). Wymaganie robocze 8 ms (jak dla EN) nie jest spełnione i zostaje
   w testach jako oczekiwana porażka (`test_granica_wolnej_rampy_8_ms`); osobny test pilnuje słabszego progu 5 ms. Przy szybkim starcie przetwornicy
   (tSS 800 µs) zapas jest duży (≥ 2,2 ms). Zwiększenie zapasu: C39 2,2 µF albo reset z GPIO.
   Rzeczywisty kształt 3V3 przy wolno rosnącym VBUS **[DO WERYFIKACJI pomiarem]**.
2. **Filtr RC przycisku nie eliminuje drgań 50 µs** (zwarcie: stała 9,1 µs). Robi to firmware
   (`pilot_wejscia.py`: 5 ms stabilności przy odpytywaniu co ~1 ms). Rozwarcie 50 µs zostaje w strefie
   nieokreślonej wejścia (1,48 V przy VIL = 0,825 V) — wg umowy testu c) to „może dać zbocze”, więc też
   oczekiwana porażka; histerezy wejścia ESP32-S3 karta modułu nie podaje.
3. **Kwarc W5500 prawdopodobnie pracuje szybciej niż 25 MHz** (ok. +42 ppm w środku założeń: C1 5 fF, C0 2 pF, Cpas 4 pF; w całej siatce założeń
   +8…+108 ppm), bo
   2 × 18 pF to za mało dla CL = 18 pF. Przed zamówieniem: odczytać C0/C1 z karty YXC X322525MRB4SI i rozważyć
   2 × 27 pF albo kwarc o CL 12 pF; na płytce zmierzyć częstotliwość.
4. EN, dzielnik VSYS i FB mają duże zapasy.

## Czego testy nie pokrywają

- **RF**: tor LoRa (E22-900M22S, przełącznik DIO2/inwerter, TCXO z DIO3), antena PCB ESP32-S3, dopasowanie,
  linie 50 Ω — wymaga pomiarów VNA/analizatorem, nie SPICE.
- **EMC i ESD**: emisja przetwornicy, prądy powrotne, SRV05-4, ekran RJ45, odporność na wyładowania — tylko
  badania w laboratorium.
- **Temperatura**: wszystkie liczby dla 25 °C (karty podają je w tej temperaturze); brak dryfu VFB, kwarcu,
  pojemności X5R w temperaturze.
- **Przetwornica dynamicznie**: tętnienia, stabilność pętli, odpowiedź na skok prądu (Wi-Fi), feed-forward C4 —
  deck e) to idealny wzmacniacz błędu w punkcie pracy.
- **Rzeczywisty kształt zasilania**: rampy są liniowe; nie ma modelu VBUS z koncentratora, bezpiecznika PTC,
  UVLO TLV62569 ani zaników zasilania (brown-out, krótkie przerwy) — EN i RSTn po krótkim zaniku mogą nie zdążyć
  się rozładować.
- **Ethernet** (terminacje, transformator RJ45), **USB** (22 Ω, USBLC6), **I2C** (4,7 kΩ, pojemność przewodu OLED).
- **Pojemność X5R pod napięciem**: zamiast krzywej DC bias scenariusz „połowa nominału” **[DO WERYFIKACJI]**.
- Założenia oznaczone w kodzie `[DO WERYFIKACJI]`: upływ i pojemność próbkująca ADC, pojemności pasożytnicze i
  parametry dynamiczne kwarcu, zakres VBUS, budżet ppm 100BASE-TX.

## Karty producentów użyte w testach

- Espressif, *ESP32-S3-WROOM-1 & WROOM-1U Datasheet* v1.8 — https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- Espressif, *ESP32-S3 Series Datasheet* v2.2 — https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- WIZnet, *W5500 Datasheet* Version 1.1.0 — https://docs.wiznet.io/img/products/w5500/W5500_ds_v110e.pdf
- Texas Instruments, *TLV62569* SLVSDG1C (XII 2016, rev. X 2017) — https://www.ti.com/lit/ds/symlink/tlv62569.pdf

Odczyt 18.10.2026 (tekst wyciągnięty z PDF-ów; numery stron jak w stopkach kart).
