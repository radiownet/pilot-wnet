# Pilot Wnet

**Otwarty pilot studyjny dla radia: przyciski arcade i joystick na płytce z ESP32-S3, zaprojektowanej do łączności przez USB HID, Ethernet i Bluetooth LE (firmware jeszcze nie uruchomiony na płytce) i do pracy jako węzeł sieci LoRa 868 MHz (szkice wariantów firmware).**

English: [README.md](README.md)

> [!WARNING]
> **Rev A to prototyp. NIE ZAMAWIAĆ płytki Rev A.**
> Ułożenie płytki ma znane wady (zob. [Znane wady Rev A](#znane-wady-rev-a)). Przed produkcją trzeba ją ponownie rozmieścić i poprowadzić ścieżki (Rev B).

> [!IMPORTANT]
> **Projekt wygenerowany przy udziale SI, bez przeglądu inżyniera.** Schemat i płytkę Rev A wygenerowały skrypty w Pythonie (z użyciem SKiDL, Freeroutingu i własnego routera), które napisali i uruchamiali agenci SI (Claude). ERC i DRC pokazują 0 błędów, ale projektu nie przejrzał żaden inżynier elektronik. Zob. [Jak powstał projekt](#jak-powstał-projekt).

## Czym jest Pilot Wnet

Pilot Wnet to fizyczny pilot (sterownik) do studia radiowego. Powstał w polskim radiu Radio Wnet (Radio Wnet Sp. z o.o.) i jest publikowany jako otwarty sprzęt (open hardware). Realizator wciska duże przyciski arcade albo porusza joystickiem, a pilot wysyła do komputera studyjnego podpisane ramki ze stanem wejść. Oprogramowanie na komputerze zamienia je na akcje.

- **Sterowanie:** sześć przycisków arcade (cztery kolorowe, START i STOP) i czterokierunkowy joystick w drewnianej obudowie w stylu automatu do gier (bartop); złącze Qwiic dla wyświetlacza OLED na I2C.
- **Łącza z komputerem studyjnym (według projektu):** USB HID, Ethernet (UDP) i Bluetooth LE. Wi-Fi jest dostępne, ale domyślnie wyłączone. Każda ramka ma CRC-16 i obcięty HMAC-SHA256 związany z jednorazową liczbą (nonce) sesji, którą podaje komputer. Ramkę i sesję opisuje [docs/ESP32_PROTOKOL.md](docs/ESP32_PROTOKOL.md).
- **Węzeł mesh:** na tej samej płytce jest moduł LoRa Ebyte E22-900M22S (868 MHz). Po wgraniu innego firmware płytka może działać jako węzeł sieci opartej na Meshtastic® albo MeshCore (szkice wariantów, jeszcze niezbudowane).

**Nie ma publicznej aplikacji hosta.** Przez USB pilot jest urządzeniem HID producenta (strona użycia `0xFF00`), które wysyła ramki uwierzytelnione HMAC, więc do użycia potrzebne jest własne oprogramowanie na komputerze; punktem odniesienia jest opis protokołu wyżej. Implementacja hosta (aplikacja na komputer studyjny) nie jest (jeszcze) publiczna; obecnie odbiera USB HID i UDP, a BLE istnieje tylko w firmware.

### Sprzęt w skrócie (Rev A)

| Blok | Rev A |
|---|---|
| Płytka | 90 × 100 mm, 4 warstwy (F.Cu sygnały, In1 GND, In2 +3V3, B.Cu sygnały), FR-4 1,6 mm, wszystkie elementy na górze, KiCad 10 |
| Mikrokontroler | ESP32-S3-WROOM-1-N16R8 (16 MB flash, 8 MB PSRAM Octal). Moduł stoi równo z górną krawędzią; jego antena PCB leży nad płytką, ze strefą bez miedzi na wszystkich czterech warstwach (Espressif zaleca antenę poza krawędzią albo wycięcie płytki; do rozważenia w Rev B) |
| Ethernet | WIZnet W5500 z kwarcem 25 MHz, gniazdo RJ45 HR911105A ze zintegrowanym transformatorem (W5500 nie ma auto-MDIX) |
| Zasilanie | tylko USB-C 5 V (bezpiecznik, TVS, USBLC6), przetwornica obniżająca TI TLV62569 5 V → 3,3 V; w Rev A bez akumulatora |
| LoRa | Ebyte E22-900M22S (SX1262, TCXO), 868 MHz, lutowany ręcznie (fabryka go nie montuje), antena przez złącze IPEX modułu |
| Wejścia | 6 × JST XH 4-pin dla przycisków (J10–J15: sygnał, GND, LED+ 5 V, LED−), JST XH 5-pin dla joysticka (J16); filtry RC i diody ESD SRV05-4 |
| Pozostałe | Qwiic dla OLED (J17) i dla aplikacji (J18), złącze rozszerzeń (J19), serwisowy UART (J20), przyciski RESET i BOOT, dioda stanu |
| Bez montażu (DNP) | sterownik podświetlenia przycisków (PCA9685 + 6 × AO3400A), moduł E22, rezystory opcji, kondensatory USB, kondensator feed-forward przetwornicy |
| Montaż | ok. 128 elementów montowanych, 43 pozycje BOM z numerami LCSC (montaż w JLCPCB) |

Decyzje projektowe z uzasadnieniem: [DECYZJE.md](DECYZJE.md) (D1–D11). Część wpisów jest nieaktualna: uzasadnienie D7 („pełna masa”) i sekcja „Konsekwencje” (obudowa dopasowana do płytki) przeczą obecnym plikom, zob. [docs/AUDYT_REV_A.md](docs/AUDYT_REV_A.md).

## Stan

| Część | Stan |
|---|---|
| Schemat | wygenerowany z `pcb/obwod.py` przez `pcb/schemat.py`; ERC: 0 błędów, 6 ostrzeżeń (`lib_symbol_mismatch`: spłaszczone symbole dziedziczące, bez wpływu na połączenia) |
| Płytka Rev A | DRC: 0 błędów, 0 niepołączonych, 0 rozbieżności ze schematem, 21 ostrzeżeń (`lib_footprint_mismatch`: pasta celowo zdjęta z padów elementów DNP); **znane wady ułożenia, NIE ZAMAWIAĆ** |
| Firmware (MicroPython) | napisany i przetestowany w CPythonie na atrapach; **nigdy nie uruchomiony na płytce** |
| Warianty Meshtastic i MeshCore | szkice plików wariantów, niezbudowane |
| Obudowa | parametryczne generatory arkuszy cięcia i modelu 3D; **jeszcze nie pasuje do płytki Rev A** (obrys, wycięcia USB-C, RJ45 i SMA, kieszeń w tylnej ściance D8); część wymiarów to wartości robocze do czasu pomiaru prawdziwych części |
| Symulacje obwodów | testy ngspice dla prostych obwodów analogowych (`sim/`); pięć oczekiwanych porażek pokazuje wymagania, których Rev A nie spełnia |
| Zgodność radiowa (RED/CE) | **nieoceniona** |

Liczby ERC/DRC: KiCad 10.0.8, 20 listopada 2026 r. (`pcb/wyniki/erc.json`, `pcb/wyniki/drc.json`).

## Znane wady Rev A

Audyt agentów SI (agenci Claude, 20.11.2026, pomiary z pliku płytki, bez przeglądu inżyniera) wskazał wady wymienione niżej. To z ich powodu potrzebna jest Rev B: zob. zadanie [Re-layout Rev B](.github/ISSUE_TEMPLATE/relayout-rev-b.md). Identyfikatory znalezisk odsyłają do streszczenia audytu w [docs/AUDYT_REV_A.md](docs/AUDYT_REV_A.md).

1. **Płaszczyzny wewnętrzne niosą sygnały** (layout-01, zasilanie-15). Większość sygnałów biegnie po warstwach wewnętrznych (In1 GND, In2 +3V3), a B.Cu jest prawie pusta. Pod W5500 masa na In1 pokrywa tylko 39% obrysu układu.
2. **Przetwornica U3 (TLV62569) ułożona wbrew karcie TI** (zasilanie-01, layout-02). Kondensator wejściowy stoi daleko od układu, węzeł SW jest długi, a ścieżka FB biegnie pod węzłem SW.
3. **Kwarc 25 MHz (Y1): złe prowadzenie XO** (layout-04). Ścieżka XO od W5500 do Y1 robi objazd 17,6 mm przez 4 przelotki (przez R58 i C41) i biegnie po In2 dokładnie pod kwarcem; pod nim na In1 biegną ścieżki SPI LoRa. XI (5,1 mm) jest poprawne.
4. **Ochrona ESD daleko od złączy** (zasilanie-02, interfejsy-04). Dla 6 z 10 wejść kanał SRV05-4 stoi 46–66 mm (w linii prostej) od swojego złącza, bo kanały przypisano w kolejności listy, a nie położenia; ścieżki wejść mają do 93 mm, głównie po In1.
5. **Pary Ethernetu** (layout-05, interfejsy-05). Ścieżki od W5500 do RJ45 nie są poprowadzone jako pary różnicowe nad ciągłą masą: połówki par biegną po różnych warstwach, z różnicą długości 11 mm i 4,6 mm.

Inne otwarte sprawy (więcej w [docs/AUDYT_REV_A.md](docs/AUDYT_REV_A.md)):

- Kondensatory obciążenia kwarcu (2 × 18 pF) są prawdopodobnie za małe dla kwarcu o CL = 18 pF, więc generator może pracować za szybko (interfejsy-09). Wyniki symulacji i warianty poprawki: [sim/README.md](sim/README.md).
- Obwód RC resetu W5500 ma mały zapas przy wolnym narastaniu 3V3 (ten sam plik); W5500 resetuje tylko ten obwód RC, a nie ESP32 (interfejsy-14).
- J19 (rozszerzenia) i J20 (serwisowy UART) to listwy 1 × 6 z **odwrotnym układem zasilania** (J19: pin 1 = +3V3, pin 2 = GND; J20: pin 1 = GND, pin 2 = +3V3). Przejściówka UART wpięta w złą listwę zamieni zasilanie z masą (interfejsy-03).
- **J20 nie pasuje do typowego kabla FTDI 6-pin**: przy każdej orientacji VCC kabla (+5 V) trafia na EN albo IO0 (interfejsy-02).
- **Pin 3 każdego złącza przycisku J10–J15 ma zawsze +5 V**, choć sterownik LED nie jest zamontowany; źle obsadzona wiązka poda 5 V przez SRV05-4 na szynę 3V3 (produkt-15, interfejsy-06).
- **Dioda D1 (SMF5.0A, przebicie 6,4–7,0 V) nie chroni U3**, którego wejście ma maksimum 6 V (zasilanie-04).
- USB D+/D− nie są poprowadzone jako para, a ochrona ESD na D− jest na odczepie (layout-06).
- Wejście U7 (74LVC1G04) wisi w powietrzu, dopóki moduł E22 nie jest wlutowany (zasilanie-06, interfejsy-07).
- Footprint USB-C (J1) trzeba jeszcze sprawdzić z kartą złącza.
- Firmware używa VID/PID wbudowanych w MicroPythona; projekt nie ma własnej pary VID/PID.

## Jak powstał projekt

Pilot Wnet to eksperyment w projektowaniu sprzętu z agentami SI i tak go oznaczamy.

- Obwód jest opisany w Pythonie w SKiDL 3.0 (`pcb/obwod.py`). Własny generator tworzy z niego schemat KiCada (`pcb/schemat.py`, etykiety sieci zamiast przewodów).
- Rozmieszczenie, strefy masy i klasy sieci ustawiają skrypty przez API Pythona KiCada (`pcb/plytka.py`). Ścieżki poprowadził Freerouting 2.5.0, a ostatnie połączenia domknął własny router rastrowy (`pcb/v01/`).
- Te skrypty, firmware w MicroPythonie z testami, testy SPICE, generatory obudowy i modelu w Blenderze, raporty (`research/`), rejestr decyzji, instrukcję zamówienia, streszczenie audytu i tę dokumentację napisali agenci SI (Claude, Anthropic) pod kierunkiem ludzi. Decyzje oznaczone jako domyślne czekają na zatwierdzenie przez zespół projektu.
- Wynik przechodzi ERC i DRC z 0 błędów. **Schematu ani płytki nie przejrzał jeszcze żaden inżynier elektronik**, a audyt opisany wyżej pokazuje, że 0 błędów DRC nie oznacza dobrej płytki.

Rev B ma być krokiem, w którym prowadzenie przejmują ludzie: ponowne trasowanie przez projektanta, przegląd przez innych i automatyczne ERC/DRC przy każdej zmianie.

## Układ repozytorium

| Ścieżka | Zawartość |
|---|---|
| `pcb/kicad/` | projekt KiCad 10: schemat, płytka, reguły, netlista, tablice bibliotek |
| `pcb/lib/` | biblioteka projektu (symbole i footprinty; bez modelu 3D E22) |
| `pcb/*.py`, `pcb/v01/` | skrypty generatora i kontroli: obwód SKiDL, generator schematu, rozmieszczenie, trasowanie, eksport plików produkcyjnych (opisy: `pcb/README.md`, `pcb/v01/README_v01.md`) |
| `pcb/wyniki/` | raporty ERC i DRC (JSON) |
| `firmware/micropython/` | firmware pilota w MicroPythonie i testy w CPythonie (`testy/`) |
| `firmware/meshtastic/`, `firmware/meshcore/` | szkice wariantów węzła mesh (niezbudowane); `firmware/ci/build-mesh.yml` to nieaktywny szkic workflow |
| `sim/` | testy ngspice prostych obwodów analogowych, generowane z `pcb/obwod.py` |
| `projekt/` | `arcade.toml` (wymiary obudowy i części; nadal zakłada starszą płytkę 100 × 100 mm, zob. [Stan](#stan)) i generator arkuszy cięcia (SVG do lasera/CNC) |
| `blender/` | generator modelu 3D i renderów obudowy (Blender w trybie wsadowym; wyników i grafiki blatu nie ma w repozytorium) |
| `zamowienie/` | instrukcja zamówienia Rev A (tylko informacyjnie: Rev A nie zamawiać) |
| `research/` | raporty R1, R2, R3 i R5 (opracowanie SI, źródła z datą sprawdzenia; R4 nie wchodzi do repozytorium) |
| `docs/` | protokół ramki i sesji (`ESP32_PROTOKOL.md`), opis sprzętu (`SPRZET.md`), streszczenie audytu (`AUDYT_REV_A.md`) |
| `DECYZJE.md` | rejestr decyzji D1–D11 |
| `LICENSES/`, `REUSE.toml`, `NOTICE.md` | teksty licencji, licencje poszczególnych plików (REUSE) i informacje o materiałach osób trzecich |
| `.github/` | workflow CI, szablony zgłoszeń i pull requestów |

## Jak odtworzyć i sprawdzić

### ERC i DRC (KiCad 10)

Pliki płytki i projektu są zapisane w KiCad 10.0.8; schemat zapisuje skrypt `pcb/schemat.py` w starszym formacie pliku, który KiCad 10 otwiera i przy zapisie konwertuje (należy się spodziewać jednorazowej dużej zmiany pliku). Z katalogu `pcb/kicad/`:

```sh
kicad-cli sch erc --severity-all --format json -o ../wyniki/erc.json pilot_wnet.kicad_sch
kicad-cli pcb drc --schematic-parity --refill-zones --severity-all --format json -o ../wyniki/drc.json pilot_wnet.kicad_pcb
```

Oczekiwany wynik: 0 błędów w obu raportach, 0 niepołączonych, 0 rozbieżności ze schematem i ostrzeżenia wymienione w sekcji [Stan](#stan). CI wykonuje te same kontrole w oficjalnym obrazie Dockera `kicad/kicad:10.0.8` przy każdym pushu do main i każdym pull requeście ([.github/workflows/kicad.yml](.github/workflows/kicad.yml)) i zapisuje raporty jako artefakty. Bramka: **0 błędów, 0 niepołączonych i 0 rozbieżności ze schematem**; pozostałe ostrzeżenia sprawdza przegląd.

Nie uruchamiaj „Aktualizuj footprinty z biblioteki” dla elementów DNP: przywraca pastę, którą celowo zdjęto.

### Testy firmware (bez sprzętu)

CPython 3.11 lub nowszy, tylko biblioteka standardowa; moduły MicroPythona zastępują atrapy (`testy/atrapy.py`). Każdy plik testów uruchamia się osobno, z katalogu `firmware/micropython/`:

```sh
for t in testy/test_*.py; do python -I -B -X utf8 "$t" || echo "NIEUDANY: $t"; done
```

Windows (cmd): `for %f in (testy\test_*.py) do python -I -B -X utf8 %f`

Atrapy pokazują tylko, że kod woła API z właściwymi pinami i argumentami. Nie pokazują, że USB HID, W5500 czy SX1262 naprawdę tak działają na płytce. Kilka testów jest celowo pominiętych: dokumentują otwarte znaleziska. CI: [.github/workflows/firmware.yml](.github/workflows/firmware.yml).

### Symulacje obwodów (opcjonalnie)

Z katalogu `sim/`: `python -I -B -X utf8 -m unittest discover -s . -p "test_*.py"`. Bez ngspice działają tylko testy obliczeniowe i topologii. Testy SPICE wymagają konsolowego programu ngspice (ścieżka w zmiennej `PILOT_NGSPICE`) i pakietu `spicelib` z PyPI, który dociąga NumPy i SciPy.

### Ponowne wygenerowanie płytki ze skryptów

Tor generatora publikujemy dla przejrzystości, ale nie jest jeszcze gotowym procesem budowania. Wymaga Pythona KiCada 10, SKiDL 3.0 i Freeroutingu 2.5.0 na środowisku Javy, a część skryptów nadal zakłada środowisko pierwotnych autorów. Ponowne uruchomienie `pcb/plytka.py` nadpisuje ręczne zmiany miedzi.

### Zależności

| Zadanie | Wymaga |
|---|---|
| Testy firmware | CPython ≥ 3.11, tylko biblioteka standardowa |
| Firmware na płytce | MicroPython dla ESP32-S3 i pakiety micropython-lib `usb-device-hid`, `aioble`, `lora-sync`, `lora-sx126x` (instalacja przez `mpremote mip install`, zob. `firmware/README.md`) |
| ERC/DRC | KiCad 10 (`kicad-cli`) |
| Generator płytki (`pcb/`) | Python KiCada 10 (`pcbnew`), SKiDL 3.0, Freerouting 2.5.0 ze środowiskiem Javy, KiKit 1.8.1 (`pcb/fab.py`), NumPy (router w `pcb/v01/`), PyMuPDF (`pcb/v01/opis_pdf.py`) |
| Symulacje (`sim/`) | ngspice (program konsolowy), `spicelib` (z NumPy i SciPy) |
| Obudowa (`projekt/`, `blender/`) | Python ≥ 3.11 (`tomllib`); Blender w trybie wsadowym dla `blender/` |
| Kontrola licencji | `reuse` (narzędzie REUSE) |

## Licencje

| Zakres | Licencja |
|---|---|
| Projekt sprzętu: projekt KiCad i biblioteka projektu (`pcb/`), razem ze skryptami generującymi projekt i ich danymi CSV/JSON; geometria obudowy i części oraz generator arkuszy cięcia (`projekt/`) | [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt) |
| Oprogramowanie: firmware w MicroPythonie z testami (`firmware/micropython/`), pliki pomocnicze MeshCore (`firmware/meshcore/`), szkic CI mesh (`firmware/ci/`), symulacje (`sim/`), generator Blendera (`blender/`), workflow CI | [MIT](LICENSES/MIT.txt) |
| Dokumentacja: pliki README, `docs/`, `research/`, `DECYZJE.md`, `zamowienie/`, CONTRIBUTING, NOTICE, szablony GitHuba | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt) |
| Pliki `.gitignore` | [CC0-1.0](LICENSES/CC0-1.0.txt) |

Wyjątki:

- `firmware/meshtastic/` to utwór zależny firmware Meshtastic i podlega GPL ([GPL-3.0-only](LICENSES/GPL-3.0-only.txt)), tak jak oryginał.
- `pcb/lib/pilot_jlc.pretty/ESP32-S3-WROOM-1_Pilot.kicad_mod` i `USB_C_Receptacle_HRO_TYPE-C-31-M-12_Pilot.kicad_mod` to zmienione footprinty z bibliotek KiCada: CC-BY-SA-4.0 z [wyjątkiem bibliotek KiCada](LICENSES/KiCad-libraries-exception.txt).
- Symbol i footprint E22-900M22S (`pcb/lib/pilot_jlc.kicad_sym`, `WIRELM-SMD_E22-900M22S.kicad_mod`) przekonwertowano z biblioteki EasyEDA/LCSC narzędziem easyeda2kicad. Warunki ich rozpowszechniania nie są ustalone ([LicenseRef-EasyEDA-Library](LICENSES/LicenseRef-EasyEDA-Library.txt)); są dołączone tylko po to, żeby projekt dało się otworzyć, i w Rev B zostaną przerysowane z karty Ebyte. Płytka, schemat i netlista zawierają ich osadzone kopie. Modelu 3D E22 nie ma w repozytorium.
- `DCO.txt` wolno kopiować tylko bez zmian ([LicenseRef-DCO](LICENSES/LicenseRef-DCO.txt)).

Licencja każdego pliku jest zapisana w formacie [REUSE](https://reuse.software/) (`LICENSES/`, `REUSE.toml`); sprawdza ją `reuse lint`, także w CI ([.github/workflows/reuse.yml](.github/workflows/reuse.yml)). Informacje o materiałach osób trzecich: [NOTICE.md](NOTICE.md). CERN-OHL-S jest licencją silnie wzajemną: kto przekazuje innym (sprzedaje, rozdaje) płytki zrobione według zmienionego projektu albo sam zmieniony projekt, musi udostępnić odbiorcom pełne źródła na tej samej licencji.

Lokalizacja źródeł (Source Location, CERN-OHL-S, pkt 4): <https://github.com/radiownet/pilot-wnet>. Rev A nie ma jej jeszcze na sitodruku; Rev B będzie miała.

## Radio i bezpieczeństwo

- Pilot Wnet jest urządzeniem radiowym: ESP32-S3 ma Wi-Fi i Bluetooth LE, a moduł E22 nadaje LoRa w paśmie 868 MHz. **Zgodności z dyrektywą RED ani oznakowania CE nie oceniano.** Moduł ESP32-S3 ma ocenę radiową producenta, ale to nie czyni zgodnym całego urządzenia.
- Budujesz i używasz urządzenia na własną odpowiedzialność. Kto wprowadza zbudowane egzemplarze do obrotu, odpowiada za ich zgodność.
- Przestrzegaj zasad dla urządzeń krótkiego zasięgu 868 MHz tam, gdzie nadajesz: podpasmo, maksymalna moc e.r.p. i cykl pracy (w UE: zalecenie ERC 70-03 i decyzja (UE) 2025/105). Sterownik LoRa w MicroPythonie ma odrzucać ustawienia spoza dozwolonych podpasm, moc ponad limit e.r.p. i nadawanie ponad cykl pracy (sprawdzony tylko na atrapach; licznik cyklu pracy zaczyna od zera po każdym włączeniu zasilania, chyba że aplikacja go odtworzy). W konfiguracji ustaw prawidłowo zysk anteny i straty. Warianty Meshtastic i MeshCore nie korzystają z tego sterownika; mają własne ustawienia regionu i cyklu pracy: sprawdź je przed nadawaniem.
- Surowe LoRa z firmware w MicroPythonie nie rozmawia z sieciami Meshtastic ani MeshCore.
- Nie nadawaj bez anteny podłączonej do modułu LoRa.
- Zasilaj płytkę wyłącznie z USB-C (5 V). Przy pierwszym uruchomieniu użyj zasilacza z ograniczeniem prądu albo miernika USB.
- **Wiązki J10–J15 obsadzaj tylko na pinach 1–2**, dopóki sterownik LED nie jest zamontowany: pin 3 ma zawsze +5 V.
- **Nie wpinaj typowego kabla FTDI 6-pin w J20** i uważaj na odwrotny układ zasilania na J19 i J20 (zob. [Znane wady Rev A](#znane-wady-rev-a)). Używaj tylko przejściówek UART 3,3 V i nie podłączaj ich VCC.
- D1 nie chroni przetwornicy U3 (wejście maks. 6 V) przed przepięciem na VBUS w zakresie 6–7 V ani przed długim przepięciem powyżej 9 V (zasilanie-04).

## Jak pomóc

- **Pytania, pomysły, Twój egzemplarz:** GitHub Discussions (Ogłoszenia, Pytania, Pokaż swoją płytkę, Pomysły).
- **Błędy i uwagi z przeglądu projektu:** Issues.
- **Główne otwarte zadanie: ponowne trasowanie Rev B.** [Szablon zadania](.github/ISSUE_TEMPLATE/relayout-rev-b.md) zawiera kryteria odbioru K1–K12. Ta praca może być płatna: zapytaj w Discussions.
- Każdy commit wymaga podpisu DCO (`git commit -s`). Wkład przygotowany z pomocą SI jest mile widziany, jeśli jest ujawniony i przejrzany przez człowieka. Szczegóły: [CONTRIBUTING.md](CONTRIBUTING.md) (po angielsku, ze streszczeniem po polsku).

## Język

Większość dokumentacji (decyzje, raporty, opisy projektu, protokół, streszczenie audytu) jest po polsku. Po angielsku są README.md (ten plik to jego polska wersja), CONTRIBUTING, NOTICE i szablony GitHuba. Tłumaczenia są mile widziane, jako pull requesty albo w Discussions. Zgłoszenia i pull requesty można pisać po polsku albo po angielsku.

## Znaki towarowe

- Nazwy „Radio Wnet” i „Pilot Wnet” oznaczają Radio Wnet Sp. z o.o.; logotypy Radia Wnet nie są objęte licencjami tego repozytorium i nie ma ich w repozytorium.
- Meshtastic® is a registered trademark of Meshtastic LLC. Meshtastic software components are released under various licenses, see GitHub for details. No warranty is provided - use at your own risk. (Meshtastic® jest zastrzeżonym znakiem towarowym Meshtastic LLC; brzmienie oświadczenia według polityki znaków Meshtastic.) Projekt nie jest powiązany z projektem Meshtastic ani przez niego popierany; nazwy używamy tylko do opisu zgodności i nie jest częścią nazwy produktu.
- To samo dotyczy MeshCore oraz innych nazw produktów i firm wymienionych w repozytorium: należą do swoich właścicieli.

## Kontakt i bezpieczeństwo

Repozytorium nie podaje danych kontaktowych osób: prosimy o kontakt przez GitHub Discussions albo Issues. Problemy bezpieczeństwa (np. w uwierzytelnianiu ramek) zgłaszaj poufnie przyciskiem „Report a vulnerability” w zakładce Security, a nie w publicznym zgłoszeniu.

---

*Ten plik przygotował agent SI (Claude) pod kierunkiem ludzi.*
