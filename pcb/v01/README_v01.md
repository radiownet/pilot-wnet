# Pakiet v0.1 — dotrasowanie płytki Rev A (19.11.2026)

Etykieta: przygotowane przez SI (Claude Code), **szkic do weryfikacji przez elektronika — NIE ZAMAWIAĆ**. Pełny pakiet (Gerber, CPL, BOM z MPN i zamiennikami, TFT, README dla elektronika) nie jest częścią repozytorium; pliki zamówienia (Gerber, CPL, BOM) odtwarzają skrypty z sekcji „Poprawki przed zamówieniem” (pełny tor na końcu pliku).

## Dlaczego

Płytka z 18.10 miała w DRC 40 niepołączonych połączeń + 6 błędów. Tor z `../README.md` (venv SKiDL/KiKit, JRE 25, Freerouting) leżał na dysku maszyny roboczej, niedostępnym 19.11. Kroki pcbnew szły w KiCadzie 10.0.1 (Python KiCada, kicad-cli), a Freerouting 2.5.0 — decyzją zespołu projektu (19.11) — na komputerze studyjnym, z przenośnego Temurin JRE 25.0.5+8 w lokalnym katalogu narzędzi poza repozytorium (SHA-256 sprawdzone z sumami wydawców; do usunięcia po pracy). Tor Rev A z 18.10 wskazywał JRE jdk-25.0.4.1+1 (komentarz przy `JAVA` w `../plytka.py`); ścieżki Javy i Freeroutingu ustawiają zmienne `PILOT_JAVA` i `FREEROUTING` (`../README.md`).

## Łańcuch, który dał obecny `kicad/pilot_wnet.kicad_pcb`

Podział: kroki pcbnew Pythonem KiCada (`trasuj_v01.py` uruchamiany obok `plytka.py`), Freerouting osobno (`java -Xmx1500m -jar freerouting-2.5.0.jar --gui.enabled=false -de X.dsn -do X.ses --router.autorouter.max_passes=40 -mt 8 -da`, analityka wyłączona, priorytet BelowNormal).

1. `czysc_plytke.py` — czyści płytkę na tekście (ścieżki, przelotki; do DSN także strefy GND na F/B). W KiCadzie 10 po `BOARD.Remove(ścieżka)` listy `Tracks()`/`Zones()` zwracają gołe `SwigPyObject`, więc czyszczenie przez pcbnew nie działa.
2. Klasy sieci: GND i +3V3 w nowej klasie `Plaszczyzny` 0,25 mm; `Zasilanie` (+5V, VBUS_C, BUCK_SW) 0,6 → 0,4 mm. Przyczyna: Freerouting nie zwęża ścieżek, a 0,6 mm nie dochodzi do padów W5500 (LQFP-48, raster 0,5 mm).
3. Wariant „sygnał 2”: świeże trasowanie DSN bez ścieżek, 4 warstwy sygnałowe → DRC 6 niepołączonych.
4. Wariant „kontynuacja 3”: DSN z trasą z kroku 3 (istniejące ścieżki zostają), Zasilanie 0,4 mm → Freerouting dokłada brakujące → DSN/SES tego kroku nie są w repozytorium (pliki pośrednie jednego przebiegu; wynik trasowania jest w `kicad/pilot_wnet.kicad_pcb`).
5. `trasuj_v01.py ses` (import SES do płytki bez ścieżek, wypełnienie stref) → `../plytka.py wykoncz` (poszerzenia, przelotki zszywające GND, DRU) → `przesun_otwory.py` (H1–H4 o 0,1 mm do środka).
6. DRC: `kicad-cli pcb drc --schematic-parity --refill-zones` (`ses_v01.cmd`, katalog roboczy w zmiennej `PRACA`), podsumowanie `drc_podsumuj_v01.py`.

Porównane warianty (DRC KiCada; liczniki Freeroutingu zaniżają braki, bo SES nie zawiera części sieci):

| Wariant | Niepołączone | Błędy | Uwagi |
|---|---:|---:|---|
| stan z 18.10 | 40 | 6 | sygnały także na In1/In2 |
| „płaszczyzny” (In1/In2 jako power, sygnały tylko F/B) | 79 | 6 | za mało miejsca na 2 warstwach |
| „sygnał” (4 warstwy, klasy z 18.10) | 36 | 7 | |
| „kontynuacja” (trasa z 18.10 + Freerouting) | 16 | 6 | |
| „sygnał 2” (klasa `Plaszczyzny` 0,25 mm) | 6 | 7 | |
| „kontynuacja 2” (kontynuacja + klasa 0,25) | 10 | 6 | |
| **„kontynuacja 3” + otwory** (z „sygnał 2”, Zasilanie 0,4) | **5** | **3** | wybrany |

## Domknięcie (19.11, po wariancie końcowym) — DRC: 0 błędów, 0 niepołączonych

Zakres zadania („Domknij 5 połączeń zasilania i 3 odstępy”):
1. `eksport_geometrii.py` (Python KiCada 10, tylko odczyt, strefy wypełnione w pamięci) → geometria miedzi do JSON.
2. `domknij.py` + `router_v01.py` + `geom_v01.py` (Python + numpy): router rastrowy 0,05 mm po F.Cu/B.Cu z przelotkami 0,6/0,3 mm; przeszkody = miedź innych sieci powiększona o 0,205 mm + 0,035 mm zapasu, krawędź 0,4 mm, obszar anteny; przelotki ≥ 0,1 mm od padów SMD (każdej sieci) i otwór–otwór ≥ 0,26 mm; każdy wynikowy odcinek i przelotka sprawdzone dokładnie. Zadania: `domkniecie_zadania.json`, wynik: `domkniecie_wynik.json`.
   - +5V U2.5 ↔ D1.1 (0,4 mm, 2 przelotki); +3V3: F.Cu (76,2; 88,8) ↔ (70,7; 85,1) przez B.Cu, (81,7; 68,4) ↔ (84,3; 77,0) po F.Cu, J17.2 ↔ J20.2 przez B.Cu, J19.1 → przelotka do głównej wyspy strefy +3V3 na In2 (największe wypełnienie, margines 0,5 mm).
   - Odstępy: I2C_SDA od J19.3 do (84,094; 57,5301) przetrasowane przez B.Cu z przelotką w dół na In2 (5 starych odcinków na In2 usunięte); ETH_TXP_U na In1 — 2 krótkie odcinki obok przelotki ETH_RXN_U przetrasowane.
3. `wstaw_domkniecie.py` (usunięcie 7 odcinków po uuid, dopisanie 30 odcinków i 7 przelotek), wypełnienie stref, DRC.
4. Usunięte 8 wiszących przelotek po autorouterze (+3V3_RF, LORA_DIO2, ETH_RD+, ETH_TOCAP, LORA_DIO1, LORA_NRST, VSYS_SENSE, BUCK_SW) i 1 wiszący odcinek LORA_DIO2 — DRC po każdym kroku bez nowych niepołączeń.

DRC po domknięciu (19.11 16:16; obecny stan — sekcja „Opis — druga poprawka” niżej): **0 błędów, 0 niepołączonych**, 37 ostrzeżeń (36 opisu: `silk_overlap` 18, `silk_over_copper` 14, `silk_edge_clearance` 4; 1 `lib_footprint_mismatch` WROOM-1 — świadomie), 4 uwagi zgodności (H1–H4 bez symboli).

Stan przed domknięciem (wariant końcowy z tabeli): 5 niepołączonych zasilania — +3V3 ×4 (wyspy przy J17–J20: J19.1 i J20.2 bez dojścia do strefy In2, dwa przerwane odcinki F.Cu) i +5V ×1 (D1.1 ↔ U2.5, ok. 7 mm) — oraz 3 odstępy 0,190 mm przy regule klasy 0,200 mm (globalne minimum płytki 0,15 mm): I2C_SDA na In2 przy padzie J19.4, ścieżka ETH_TXP_U na In1 przy przelotce ETH_RXN_U (×2). Próba mikroprzesunięć (`popraw_odstepy.py`, skrypt spoza repozytorium) przenosiła kolizje gdzie indziej — odrzucona. Sygnały biegną także po In1 (GND) i In2 (+3V3), co tnie płaszczyzny — do oceny elektronika.

Panel KiKit z 18.10 (`kicad/pilot_wnet_panel.kicad_pcb`) był **nieaktualny** — zawierał starą trasę — i nie jest częścią repozytorium; `../fab.py` tworzy panel od nowa (KiKit 1.8.1), a pliki zamówienia v0.1 robią `eksport_v01.py` i `pakiet_zamowienie_v01.py`.

## Opis — druga poprawka (20.11): napisy pod korpusami, poza płytką, za blisko i mylące

Zakres zadania („Poprawić na płytce etykiety Y1 i H1 i przeplotować PDF-y opisu” — decyzja zespołu projektu). Przegląd renderów 19.11 pokazał, że `opis_v01.py` szukał wolnego miejsca po prostokątach napisów, bez korpusów elementów, a DRC KiCada (`min_silk_clearance` = 0) nic z tego nie zgłasza. Cztery rundy adwersaryjnej weryfikacji agentami (21 + 19 + 11 + 7) dołożyły m.in.: „SERW” (złącze serwisowe J20) stał przy J19 — obie listwy 1×6 mają różny układ zasilania (J19: 1 = +3V3, 2 = GND; J20: 1 = GND, 2 = +3V3), więc przejściówka UART wpięta w złą listwę zamieni zasilanie z masą; kilka napisów stykało się z innym opisem lub padem; pierwsze wersje poprawki stawiały U7/Y1 przy cudzych elementach, a „SERW” przy przycisku BOOT.

`opis2_v01.py` (Python KiCada 10) mierzy wszystko na kształcie tuszu (`GetEffectiveTextShape` — kreski z grubością, jak w Gerberze), nie na prostokącie napisu. Błędy: tusz na korpusie elementu tej strony (prostokąt Fab, także własny i DNP; otwór montażowy = koło 3,5 mm, podkładka M3), < 0,3 mm od krawędzi lub poza płytką, < 0,15 mm od otwarcia maski, < 0,15 mm od innego opisu, napis bliżej konkurenta niż własnego elementu. Konkurent (mierzony po courtyardzie i padach — courtyard modułu U6 nie obejmuje jego padów) = element z tym samym prefiksem, a dla etykiet funkcji także właściciel innej etykiety funkcji (właściciele z `plytka.py` w. 285–291: REC…STOP = J10…J15, JOY = J16 z netów, OLED = J17, QWIIC = J18, EXP = J19, SERW = J20, RST = SW1, BOOT = SW2). Poprawka: przy samym odstępie — najmniejsze przesunięcie (krok 0,05 mm); w pozostałych przypadkach najbliższe miejsce przy korpusie właściciela (krok 0,25 mm; ten sam obrót, potem drugi, na końcu czcionka 0,8 mm = `min_text_height` z tą samą kreską). Warunki nowego miejsca: krawędź ≥ 0,5 mm, korpusy ≥ 0,15, pady ≥ 0,2, linie opisu ≥ 0,2, inne napisy ≥ 0,4, otwory przelotek ≥ 0,05, własny obrys ≥ 0,75 mm bliżej niż obrys i pady każdego konkurenta; kary: pierścień przelotki pod tuszem, a przy przenoszeniu do właściciela także korpus obcego elementu bliżej niż własny. Płytka zapisywana tylko wtedy, gdy po poprawce kontrola nie ma błędów (kod wyjścia ≠ 0 w przeciwnym razie).

Uruchomione na stanie płytki z 19.11 (stan spoza tego repozytorium — płytka Rev A w repozytorium jest stanem odniesienia). Przed: 42 napisy, 10 z błędami. Przesunięte (tusz w mm płytki):

| Napis | Błąd | Po |
|---|---|---|
| Y1 | pod korpusem W5500 (U4) | pod kwarcem, z lewej (x 26,4–28,1, y 44,0–45,2) |
| H1 | poza płytką (tusz y −1,17…−0,02) | pod otworem, 3,66 mm od środka (poza podkładką M3) |
| U5 (DNP) | pod własnym korpusem | nad górnym rzędem nóżek |
| U7 | tusz 0,18 mm od krawędzi, 0,10 mm od linii U7 | pionowo przy znaczniku pinu 1 U7, nad C50 (krawędź 0,54 mm; do obrysu U7 0,40, do U6 3,41 mm; najbliższy korpus to C50, 0,48 mm — miejsce z prawej strony U7 odpadło: 0,30 mm od padów U6 i na otworze przelotki) |
| SERW | bliżej J19 niż J20 | przy lewym boku J20, jak „EXP” przy J19 (do obrysu J20 0,0, do J19 0,85 mm; do opisu J20 0,21 mm); czcionka 0,9 → 0,8 mm, kreska 0,135 bez zmian |
| J20 | 0,086 mm od pada SW2.2 | +0,75 mm w x (przy +0,15 kreska „J” leżała na otworze przelotki); do SW2.2 0,82 mm |
| U10, U11, U12 | 0,035 mm od trójkąta pinu 1 | U10 +0,08 / −0,18 mm, U11 i U12 −0,20 mm w y |
| FB2 | 0,027 mm od linii opisu U6 | pod dławikiem FB2 (+0,39 / +2,82 mm) |

Po: 0 błędów. Informacyjnie zostają: napisy, których najbliższym korpusem jest sąsiedni element (m.in. U10–U12 nad swoimi układami, ale bliżej R21/R15/C18; U7 przy C50 — tusz wchodzi 0,07 mm w courtyard C50, do padu C50 0,30 mm, do własnych padów 0,55 mm; C50 nie ma nadrukowanego oznaczenia); przelotki (zakryte maską) pod tuszem 14 napisów (było 19; m.in. PLAY…STOP nad rzędem przelotek zszywających y = 92, „PILOT WNET Rev A”, legenda na stronie B), J16 0,43 mm od krawędzi, legendy na stronie B bez wskazania złącza — do oceny elektronika.

Zmiana w pliku płytki: 9 linii `(at …)` pól Reference i napis „SERW” (położenie, rozmiar; KiCad zapisał blok w innym miejscu pliku, uuid ten sam); miedź, strefy, footprinty bez zmian; Gerbery różnią się tylko `F_Silkscreen`. DRC: 0 błędów, 0 ostrzeżeń, 0 niepołączonych, 0 uwag zgodności (`../wyniki/drc.json`). (Liczby DRC w sekcji „Domknięcie” wyżej to stan z 19.11 przed poprawkami opisu i symbolami otworów.)

PDF-y opisu (od 20.11 `eksport_v01.py` i `opis_pdf.py` w `v01/`; wcześniej wsadowy `pcb_v01.cmd`, poza repozytorium): `kicad-cli pcb export pdf` rysował opis pod miedzią (kolejność `-l` = kolejność rysowania), a jego ploter PDF rozsuwa spacje (napisy wielowyrazowe dłuższe o 1,1–1,8 mm niż w Gerberze). Teraz: SVG z `--subtract-soldermask --drill-shape-opt 0 --fit-page-to-board` (geometria jak w Gerberze, bez otworów nad tuszem), przekolorowany i złożony na A4 w skali 2:1 z podziałką.

## Poprawki przed zamówieniem (20.11, KiCad 10.0.8)

Poprawki z audytu gotowości i niezależnej recenzji (20.11; wprowadzone decyzją zespołu projektu; streszczenie audytu: `../../docs/AUDYT_REV_A.md`). KiCad 10.0.8 zainstalowany na komputerze studyjnym dla użytkownika (winget `KiCad.KiCad --scope user`, bez uprawnień administratora; `%LOCALAPPDATA%\Programs\KiCad\10.0`), globalne tabele bibliotek skopiowane z szablonu instalacji. Eksport płytki sprzed poprawek w 10.0.8 dał geometrię Gerberów identyczną z 10.0.1 (12 z 13 warstw bajtowo po pominięciu nagłówków; opis górny — ta sama geometria, inna kolejność kresek), DRC 0/0/0, ERC 6 ostrzeżeń jak wcześniej — tor nie zależy od konkretnej maszyny.

Łańcuch (od stanu płytki z 20.11 rano, po drugiej poprawce opisu; stan spoza tego repozytorium — płytka Rev A w repozytorium jest wynikiem łańcucha i stanem odniesienia): `zamowienie_v01.py popraw` → `opis2_v01.py popraw` → `eksport_v01.py` → `pakiet_zamowienie_v01.py`.

1. **Przelotki w padach** (audyt fab-02/layout-03/16, recenzja W3): usunięte 7 przelotek zszywających GND przy padach SMD — (5; 23) R4.2 (dół dzielnika FB przetwornicy), (80; 8) R52.2, (44; 11) C48.2 oraz przy padach elementów DNP (59; 68) U5.2/U5.3, (5; 56) U6.10, (62; 77) Q5.2, (35; 77) Q3.2. Kryterium: miedź przelotki < 0,2 mm od miedzi padu SMD i przelotka GND bez własnych ścieżek (masa padów idzie strefami). Zostają: (5; 41) GND w padzie U6.2 (E22, DNP; przelotka trasowana — usunięcie wymagałoby przetrasowania), (13,55; 11,513) +5V przy U2.5 i (71,4; 85,41) +3V3 przy R28.1 (z dołączonymi ścieżkami, bez nakładania miedzi). Usuwanie na tekście pliku po uuid (w KiCadzie 10 po `BOARD.Remove()` listy obiektów zwracają gołe `SwigPyObject`), potem świeże wczytanie i wypełnienie stref. `plytka.py wykoncz`: każdy pad jest teraz przeszkodą dla przelotek zszywających (wcześniej pomijał pady SMD sieci GND).
2. **Pasta na elementach DNP** (audyt fab-05/montaz-08, recenzja W2): F.Paste zdjęta z 94 padów 21 footprintów DNP. Skutek uboczny: 21 ostrzeżeń DRC `lib_footprint_mismatch` (footprint różni się od biblioteki warstwą pasty) — zamierzone.
3. **D2** C72043 (stan 0 w JLC i LCSC) → C12065 (LITEON LTST-C193TGKT-5A; ten sam footprint EasyEDA LED0603-RD, pad 1 = katoda): płytka, schemat, `obwod.py`, `kicad/bom_obwod.csv`.
4. **Opis**: 9 napisów płytki do 1,0 mm / 0,15 mm (minimum JLC); „SERW” 0,8 mm / 0,15 mm (między J19 i J20 nie ma miejsca na 1,0 mm; 0,8 mm = minimum PCBWay). `opis2_v01.py popraw` przesunął „Radio Wnet · 2026-10 · …” (nachodził na C20) o (−1,577; +0,759) mm i „QWIIC” o (+0,528; +0,155) mm; kontrola opisu: 0 błędów.
5. **Tabliczka**: Pilot Wnet, rev A, 2026-11-20, Radio Wnet (plik zadania Gerbera miał „rev?”).
6. **Pliki montażu**: `korekty_jlc.py` — tabela korekt obrotu i środka dla 12 numerów LCSC (układ footprintu, więc działa po przesunięciu elementu); odtwarza oba wzorce CPL z 20.11 (audyt i niezależna recenzja, zgodne między sobą 128/128) z różnicą 0. `eksport_v01.py` — odpowiednik wcześniejszego skryptu wsadowego `pcb_v01.cmd` (poza repozytorium; + rysunek montażowy z warstwy Fab: oznaczenia, bez wartości, DNP przekreślone, skala automatyczna, nagłówek PL/EN; stary `montaz_gora.pdf` był ucięty i nieczytelny — recenzja W6). `pakiet_zamowienie_v01.py` — osobne zestawy dla JLCPCB (CPL z korektami) i PCBWay (CPL w konwencji KiCada, BOM po angielsku z Type SMD/THT i DNP osobno, rysunek, uwagi do zamówienia), pozycje DNP do lutowania ręcznego, zip Gerberów.

Wynik: DRC 0 błędów, 0 niepołączonych, 0 uwag zgodności, 21 ostrzeżeń `lib_footprint_mismatch` (DNP bez pasty); ERC 6 ostrzeżeń `lib_symbol_mismatch` (jak wcześniej). Gerbery względem stanu sprzed poprawek: maski F/B, B.Paste i obrys bez zmian; F.Paste −94 otwory (wyłącznie pady DNP); PTH 760 → 753 otwory; miedź zmieniona przy usuniętych przelotkach (wypełnienia stref); opis F/B. Instrukcja zamówienia: `../../zamowienie/README.md` (wersja 2).

Uwagi z weryfikacji poprawek (20.11, 3 soczewki + krytyk; werdykt: OK z uwagami; szczegóły: `../../docs/AUDYT_REV_A.md`). Odtwarzalność sprawdzono przed publikacją na płytce wejściowej spoza tego repozytorium: `zamowienie_v01.py popraw` + `opis2_v01.py popraw` dały identyczny plik, a drugi przebieg nic nie zmienia. Płytka Rev A w tym repozytorium jest stanem odniesienia:
- Świadomie pozostawione: przelotka +5V (13,55; 11,513) 0,097 mm od miedzi padu U2.5 (zakryta maską, ta sama sieć, otwór 0,25 mm od padu); +3V3 (71,4; 85,41) 0,106 mm od R28.1; GND (5; 41) w padzie U6.2 (E22, DNP, przelotka trasowana); dwie nachodzące przelotki +3V3 (76,2; 88,8) i (76,1; 88,2) (odstęp otworów 0,298 mm ≥ minimów JLC 0,2 i PCBWay 0,28).
- `plytka.py wykoncz` po zmianie (każdy pad przeszkodą, odstęp 0,3 mm) usunąłby jeszcze 4 przelotki siatki przy (32; 44) Y1.2, (62; 14) i (62; 17) U1.41, (83; 8) H2.1 (odstęp 0,255–0,285 mm, nieszkodliwe) — płytka v0.1 powstała przez punktowe usunięcie 7 przelotek w `zamowienie_v01.py`, nie przez ponowne `wykoncz`.
- „Aktualizuj footprinty z biblioteki” przywróci pastę na padach DNP — potem znowu `zamowienie_v01.py popraw`; na końcu toru `zamowienie_v01.py kontrola` musi dać `pady_dnp_z_pasta = 0` i `male_napisy = 0`.
- C48.2 (1 nF 2 kV, ekran RJ45 → GND) stracił przelotkę przy padzie; masa przez strefę F.Cu (4 szprychy 0,4 mm) i ścieżkę do przelotki 2,9 mm dalej — łączność OK.
- Wypełnienie stref w płytce wejściowej (20.11 rano) było nieaktualne w 3 drobnych miejscach (poniżej 0,02 mm²); teraz zapisane = ponowne wypełnienie.
- `kicad/pilot_wnet.net`: D2 → C12065 (wejście `schemat.py`/`plytka.py`; inaczej regeneracja przywróciłaby C72043). Stary panel KiKit (`kicad/pilot_wnet_panel.kicad_pcb`, nieaktualny, z C72043) nie jest częścią repozytorium.
- `pilot_wnet.kicad_pro` przepisany przez KiCad 10.0.8 (jawne wartości domyślne: ustawienia nowych stref, `td_enabled`) — bez wpływu na DRC i strefy (sprawdzone).
- BOM z MPN i zamiennikami jest teraz w repo: `v01/bom_v0.1_mpn_zamienniki.csv` (wejście dla BOM PCBWay; D2 = C12065, zamiennik C72043 opisany jako oryginał bez stanu). BOM PCBWay bierze zamiennik tylko przy zgodności „1:1 pin i footprint” (inne wymagają zgody — pkt 6 uwag), bez polskich tekstów; DNP w osobnym `dnp_reference_v0.1.csv`. Dwa zestawy PCBWay: `pcbway/` (J19/J20 lutuje fabryka) i `pcbway_promocja_29usd/` (J19/J20 niemontowane — ≤ 100 lutów THT na zamówienie: 94 zamiast 118).
- `opis_pdf.py` przeniesiony z pakietu zamówienia do repozytorium (`v01/`); poprawiony podpis: 12 przelotek termicznych w padzie masy U1 jest od góry odsłoniętych (recenzja D3). Pełny tor: `zamowienie_v01.py popraw` → `opis2_v01.py popraw` → `zamowienie_v01.py kontrola` → `eksport_v01.py kicad <wyniki>` → `opis_pdf.py <wyniki>\montaz <commit>` → `pakiet_zamowienie_v01.py <wyniki> kicad\pilot_wnet.kicad_pcb v01\bom_v0.1_mpn_zamienniki.csv <pakiet>`.
