# Audyt płytki Rev A — streszczenie znalezisk technicznych

> **Audyt agentów SI (Claude), 20.11.2026, pomiary z pliku płytki, bez przeglądu inżyniera.**
> Audyt gotowości płytki Rev A do produkcji wykonali agenci SI w sześciu obszarach (pliki produkcyjne, montaż, zasilanie, interfejsy i złącza, ułożenie płytki, produkt i mechanika). Każdy obszar sprawdził niezależny weryfikator SI, a całość krytyk kompletności SI. Pomiary pochodzą z pliku płytki (`pcb/kicad/pilot_wnet.kicad_pcb`), schematu i kart katalogowych; płytki nie zbudowano. Pełny raport nie jest częścią repozytorium. To streszczenie obejmuje jego znaleziska techniczne i również przygotował je agent SI. **Żaden inżynier elektronik nie przejrzał ani audytu, ani tego streszczenia.**

## Summary (English)

An AI-agent audit (Claude agents, 20 November 2026) checked whether the Rev A board is ready for manufacture. Six areas were audited (fabrication files, assembly, power, interfaces and connectors, layout, product and mechanics), each with an independent AI verifier and a final AI completeness critic. All measurements were taken from the board file, the schematic and datasheets; no board was built, and no engineer has reviewed the audit.

- **No finding shows a schematic error that certainly stops the board from working**; the board would most likely start. The layout, however, has defects that need a re-layout (Rev B): signals on the inner planes (layout-01, zasilanie-15), the buck converter placed against the TI datasheet (zasilanie-01, layout-02), the crystal XO detour (layout-04), ESD diodes far from their connectors (zasilanie-02, interfejsy-04) and Ethernet pairs that are not pairs (layout-05, interfejsy-05). See section 3.
- **Already fixed in the Rev A files (20 Nov 2026):** vias in SMD pads, solder paste on DNP pads, an unavailable status LED part, undersized silkscreen and the CPL rotation/centre table for assembly. See section 2.
- **Safety-relevant open points:** +5 V on pin 3 of the button connectors J10–J15 (produkt-15), the service header J20 does not match a standard FTDI cable (interfejsy-02), swapped power pins on J19/J20 (interfejsy-03), D1 does not protect the buck converter above 6 V (zasilanie-04). See section 4.
- The finding IDs below are used in the README files and in the Rev B task (`.github/ISSUE_TEMPLATE/relayout-rev-b.md`).

## 1. Jak czytać

- **Identyfikatory:** `fab-` pliki produkcyjne, `montaz-` montaż (BOM, CPL), `zasilanie-` zasilanie, zabezpieczenia i ESP32, `interfejsy-` Ethernet, LoRa, I2C, wejścia i złącza, `layout-` ułożenie płytki, `produkt-` produkt i mechanika, `kryt-` krytyk kompletności. Kilka identyfikatorów w jednym wierszu oznacza ten sam problem zgłoszony w kilku obszarach.
- **Waga** to waga po weryfikacji: WAŻNE, DROBNE, INFO. NIEPEWNE oznacza, że weryfikator nie potwierdził ani nie obalił znaleziska.
- **Skutki „wnioskowane”** wynikają z analizy, a nie z pomiaru na sprzęcie.
- **Współrzędne** w mm, w układzie pliku płytki KiCada (oś y w dół, górna krawędź płytki y = 0).
- **Stan pomiarów:** płytka z 19–20.11.2026, przed poprawkami z rozdz. 2. Poprawki nie zmieniły rozmieszczenia elementów ani tras poza usuniętymi przelotkami.
- Pominięto ustalenia procesowe i zakupowe (zatwierdzanie decyzji, wyznaczenie recenzenta, wyceny, wybór producenta, terminy).

## 2. Poprawki wykonane w plikach Rev A (20.11.2026)

| Poprawka | Znaleziska | Co zrobiono |
|---|---|---|
| ✅ Przelotki w padach SMD | fab-02, layout-03, layout-16, layout-08 | Usunięto 7 przelotek zszywających GND przy padach SMD: R4.2 (dół dzielnika FB przetwornicy; przy rozwartym R4 przetwornica dałaby ok. 0,6 V zamiast 3,3 V), R52.2, C48.2 oraz przy padach elementów DNP (U5.2/U5.3, U6.10, Q5.2, Q3.2). Generator `pcb/plytka.py wykoncz` traktuje teraz każdy pad jako przeszkodę dla przelotek zszywających. Świadomie zostają: GND w padzie U6.2 (E22, DNP; przelotka trasowana), +5V 0,097 mm od miedzi padu U2.5 (zakryta maską), +3V3 0,106 mm od R28.1 oraz dwie nachodzące przelotki +3V3 w (76,2; 88,8) i (76,1; 88,2). |
| ✅ Pasta na padach DNP | fab-05, montaz-08 | F.Paste zdjęta z 94 padów 21 footprintów DNP (m.in. E22, PCA9685 w obudowie TSSOP-28, Q1–Q6). Skutek uboczny: 21 ostrzeżeń DRC `lib_footprint_mismatch` (zamierzone). „Aktualizuj footprinty z biblioteki” przywróci pastę. |
| ✅ Dioda stanu D2 | montaz-03, produkt-06 | Część C72043 była niedostępna; zamiennik C12065 (LITEON LTST-C193TGKT-5A, ten sam footprint, pad 1 = katoda) w płytce, schemacie, `pcb/obwod.py` i BOM. |
| ✅ Opis (sitodruk) | fab-04 | 9 napisów powiększonych do 1,0 mm / kreska 0,15 mm. „SERW” ma 0,8 / 0,15 mm, bo między J19 i J20 nie ma miejsca. Kontrola opisu: 0 błędów. |
| ✅ Obroty i środki w CPL | montaz-01, montaz-02, montaz-04, fab-12, montaz-06, produkt-18 | Bez korekt 7 układów stanęłoby w fabryce obróconych, a 5 z nich nadal trafiłoby na pady (np. SRV05-4 obrócone o 180° zwierają szynę 3V3, U3 bez korekty nie daje 3,3 V). Tabela korekt obrotu i środka dla 12 numerów LCSC jest w `pcb/v01/korekty_jlc.py` (U2 0°, U3 180°, U4 180°, U7 270°, U10–U12 180°; środki U1 o 3,63 mm i J1 o 1,57 mm; złącza J2, J10–J16, J19, J20). Wynik zgadza się 128/128 z dwoma niezależnymi wyliczeniami. Podgląd montażu u producenta trzeba mimo to sprawdzić (znacznik pinu 1, środki U1, J1, J2, zatrzaski JST). |
| ✅ Listwy technologiczne (opis w instrukcji) | fab-03, montaz-07, produkt-05, layout-15 | Płytka nie ma listew, znaczników ani otworów technologicznych. J1 i J2 wystają poza górną krawędź, a U1 stoi 0,05 mm od niej, więc listwy mogą być tylko po lewej i prawej stronie (boki 100 mm), z mostkami zamiast V-cut. Opisane w `zamowienie/README.md`. |

Wynik po poprawkach: DRC 0 błędów, 0 niepołączonych, 0 rozbieżności ze schematem, 21 ostrzeżeń (`lib_footprint_mismatch`, DNP bez pasty); ERC 0 błędów, 6 ostrzeżeń (`lib_symbol_mismatch`). Poprawki sprawdzili niezależni agenci SI, bez przeglądu inżyniera. Płytka Rev A w tym repozytorium jest stanem odniesienia. Szczegóły: `pcb/v01/README_v01.md`, sekcja „Poprawki przed zamówieniem”.

## 3. Wady ułożenia płytki (powód Rev B)

Usunięcie większości z nich wymaga ponownego ułożenia i trasowania płytki. Kryteria odbioru: zadanie Rev B, K1–K12.

| ID | Waga | Problem (pomiar) | Skutek | Naprawa |
|---|---|---|---|---|
| layout-01, zasilanie-15, produkt-07, fab-10 | WAŻNE | Płaszczyzny niosą sygnały: na In1 (GND) ok. 1724 mm ścieżek 52 sieci, na In2 (+3V3) ok. 1563 mm 41 sieci (w tym +5V 202 mm); na F.Cu 853 mm, na B.Cu tylko 96 mm (B.Cu to w 89% wylewka GND). In1 rozpada się na 12 wysp. Pod obrysem W5500 masa In1 pokrywa 39% (34% prostokąta korpusu), In2 48%. Szczeliny w In1 m.in. pod magistralą SPI W5500 (ok. 1,6 × 27 mm) i pod USB D± (ok. 1,4 × 31 mm). Uzasadnienie decyzji D7 („pełna masa”) w `DECYZJE.md` jest przez to nieaktualne. | Wnioskowane: dłuższe drogi prądów powrotnych, większa emisja i przesłuchy (ryzyko w badaniach EMC i RED), słabsze odsprzęganie, słabszy odbiór LoRa. Płytka najpewniej ruszy. | In1 jako ciągła masa bez ścieżek; sygnały na F.Cu i B.Cu (ewentualnie In2), nie pod W5500 i modułem; +5V szeroką ścieżką na warstwie zewnętrznej (K2, K3). |
| zasilanie-01, layout-02 | WAŻNE | Przetwornica U3 (TLV62569) ułożona wbrew rozdz. 10.1 karty TI: przy pinie VIN nie ma kondensatora (C2 100 nF łączy się ścieżką 5,7 mm, C1 10 µF ścieżką 7,2 mm); węzeł SW ma 8,34 mm ścieżki z przewężeniem 0,45 mm i biegnie wokół pinu VIN, L1 stoi 6,6 mm od pinu SW; ścieżka FB biegnie 5,06 mm po In1 bezpośrednio pod padem SW. | Wnioskowane: szpilki na VIN (pętla wejściowa rzędu 5–10 nH, możliwe przekroczenie 6 V), sprzężenie SW do FB (jitter, możliwa niestabilność), emisja ok. 1,5 MHz. Przetwornica najpewniej wystartuje. | Ułożyć według przykładu z karty TI: obrócić U3, kondensator wejściowy ≤ 1–2 mm od pary VIN–GND, L1 przy SW, C3 przy L1, R3/R4 przy FB, FB tylko po F.Cu z dala od SW, kilka przelotek GND (K5). |
| layout-04 | WAŻNE | Kwarc Y1 w (30,0; 42,1); Y1, C40, C41, R58 i R59 stoją 3,5–6 mm od pinów 30/31 W5500. XI ma poprawne ok. 5,1 mm po F.Cu. XO robi objazd: pin 31 → przelotka → In2 dokładnie pod kwarcem → przelotka → R59 i R58 (0 Ω) → C41 → przelotka → In1 → przelotka → Y1.3, razem ok. 17,6 mm i 4 przelotki. Pod kwarcem na In1 biegną LORA_MISO, LORA_MOSI i LORA_NSS; ETH_XI i ETH_XO przecinają SPI LoRa. | Wnioskowane: przesunięcie częstotliwości (Ethernet wymaga ±50 ppm), sprzężenie SPI LoRa do zegara po osadzeniu E22, emisja 25 MHz. Oscylator najpewniej wystartuje. | Y1, C40 i C41 tuż przy pinach 30/31; XO bez przelotek i bez objazdu przez R58; pod kwarcem tylko ciągła masa, pierścień GND na F.Cu (K4). |
| zasilanie-02, interfejsy-04 | WAŻNE / DROBNE | Kanały SRV05-4 (U10–U12) i rezystory R10–R19 przypisano w `pcb/obwod.py` w kolejności listy wejść, a nie położenia złączy. Odległość złącze → dioda w linii prostej: REC 65,9, STOP 60,7, PLAY 52,2, JOY_RIGHT 48,4, START 47,0, JOY_LEFT 46,1 mm; pozostałe 4 wejścia 6,1–24,9 mm; SDA/SCL 15–36 mm. Ścieżki wejść mają do 93 mm (IN_JOY_RIGHT 93,1 mm, IN_REC 90,3 mm), głównie po In1. | Ochronnik zaczyna działać dopiero za kilkudziesięcioma mm ścieżki (ok. 50–90 nH); prąd wyładowania płynie po In1 obok SPI W5500. Ochrona ESD dla 6 wejść jest słabsza, niż zakłada schemat; działanie funkcjonalne bez zmian. | Przypisać kanały do najbliższych złączy, diody ≤ 5 mm od złączy z krótką drogą do GND, wejścia krótko po F.Cu/B.Cu (K8). |
| layout-05, interfejsy-05 | DROBNE | Pary Ethernetu W5500 → HR911105A nie są parami: TX+ 33,6 mm (F.Cu + In1), TX− 22,6 mm (F.Cu + In2 + B.Cu), RX+ 36,7 mm, RX− 32,1 mm, 3–5 przelotek na linię; niedopasowanie ok. 11 mm (TX) i 4,6 mm (RX); ścieżki 0,15–0,2 mm, klasa „Ethernet” obejmuje tylko RX. | Wnioskowane: zamiana części sygnału różnicowego na wspólny i promieniowanie z kabla (ryzyko w badaniach EMC), mniejszy margines przy długich kablach. Łącze 100BASE-TX najpewniej ruszy. | Każda para na jednej warstwie (F.Cu nad ciągłą In1), równolegle, ok. 100 Ω; długości wyrównane; terminacje w linii między W5500 a RJ45 (K6). |
| layout-06 | DROBNE | USB D+/D− nie jest parą różnicową; ochrona ESD na D− jest na odczepie; ścieżki USB przechodzą nad SPI. | USB FS to znosi; ochrona D− nieco słabsza, możliwe sprzężenie zegara SPI (wnioskowane). | Para ok. 90 Ω na F.Cu nad ciągłą masą, D− przez piny U2 tak jak D+ (K7). |
| zasilanie-08, interfejsy-18 | DROBNE | Odsprzęganie W5500: 3 z 6 kondensatorów AVDD stoją po stronie bez pinów AVDD, 5–8 mm od nich; VDD (pin 28) ma najbliższy 100 nF dopiero 6,4 mm dalej. | Słabsze tłumienie zakłóceń w paśmie PHY 100BASE-TX; W5500 najpewniej ruszy. | C32, C33, C35 przy pinach AVDD 8, 11, 17 z przelotką GND przy padzie; C44 przy pinie 28. |
| interfejsy-10 | DROBNE | TOCAP W5500 prowadzony ścieżką 8,9 mm pod obudową, choć C38 stoi 2,5 mm od pinu. | Gorsza stabilność wewnętrznego napięcia odniesienia PHY. | C38 przy pinie 20, C37 przy pinie 22. |
| zasilanie-16, layout-09 | DROBNE | Każdy odbiornik 3V3 (ESP32 pin 2, VDD W5500, wyjście przetwornicy) wisi na jednej przelotce 0,3 mm i ścieżce 0,25 mm; pojedyncze żebra termiczne (reguła w `pcb/kicad/pilot_wnet.kicad_dru`). | Spadek DC pomijalny (ok. 5 mV przy 0,65 A); gorsze odsprzęganie przy impulsach Wi-Fi i PHY. | 2–4 przelotki przy pinach zasilania i przy C3, C5, C44; przyłącza ≥ 0,5–0,6 mm; co najmniej 2 żebra termiczne. |
| kryt-06 | INFO | Trzy wyspy +3V3 na In2 po prawej stronie łączą się z płaszczyzną tylko ścieżkami 0,25 mm (wszystko jest połączone). | — | Zszyć wyspy z płaszczyzną przelotkami albo usunąć sygnały z In2 w tym obszarze. |
| kryt-03 | DROBNE | Wejście VBUS (przed bezpiecznikiem) i szyna +5 V do sześciu złączy przycisków biegną po warstwach wewnętrznych; grubość miedzi wewnętrznej nie jest określona (domyślnie 0,5 oz). Według IPC-2221 ścieżka 0,6 mm przy 0,5 oz nagrzewa się o ok. 60 °C przy 1,1 A (prąd podtrzymania bezpiecznika F1). | Normalnie bez skutków. Przy zwarciu +5 V–GND w wiązce XH (piny 2 i 3 obok siebie, produkt-15) prąd poniżej progu zadziałania bezpiecznika może płynąć długo i przegrzać ścieżkę wewnętrzną; VBUS_C przed bezpiecznikiem chroni tylko port komputera. | Rev A: 1 oz miedzi wewnętrznej w zamówieniu. Rev B: VBUS i +5 V na warstwach zewnętrznych, 0,6–1 mm; gałąź +5 V do przycisków przez osobny bezpiecznik albo rezystor 0 Ω (DNP). |
| interfejsy-12 | DROBNE | I2C 400 kHz: 126–132 mm ścieżek (głównie po In2), podciąganie 4,7 kΩ, ESD daleko od złączy Qwiic. | Z długą wiązką do OLED możliwe błędy NACK. | 100 kHz w firmware albo pomiar zbocza; w razie potrzeby 2,2 kΩ. |
| interfejsy-16 | INFO | Magistrala SPI W5500 ma 50–60 mm, głównie po In1, bez rezystorów szeregowych przy źródle. | Brak problemu przy 20 MHz. | Przy zmianie miedzi 22–33 Ω na SCLK przy ESP32. |
| interfejsy-11, layout-13 | DROBNE / INFO | Ekran RJ45 (CH_GND) bez własnej wyspy, 0,30 mm od GND i od płaszczyzny +3V3; pin 8 (terminacja Boba Smitha) na GND, a nie na masę obudowy jak w referencji. Kondensator 2 kV nie daje izolacji 2 kV przy takich odstępach. | Przy wyładowaniu na obudowę RJ45 możliwy przeskok na GND albo +3V3. | Świadomie połączyć ekran z GND (wlutować R82) albo zrobić wyspę CH_GND z odstępem ≥ 1–2 mm na wszystkich warstwach. |
| layout-12, layout-15 | INFO | Strefa zakazu anteny modułu ESP32 jest czysta na 4 warstwach, ale antena (x 57–75, y 0,05–6,05) leży na laminacie: moduł stoi 0,05 mm od górnej krawędzi. Espressif zaleca antenę poza płytką albo wycięcie płytki pod nią i po bokach. J1 i J2 wystają poza górną krawędź. | Możliwe lekkie rozstrojenie anteny i mniejszy zasięg Wi-Fi/BLE. | Opcjonalnie wycięcie płytki pod anteną albo wysunięcie modułu ok. 6 mm poza krawędź; zasięg zmierzyć w gotowej obudowie. |
| layout-07, fab-07 | DROBNE / INFO | 12 przelotek termicznych 0,3 mm w padzie GND modułu U1, od góry bez maski, niezatykanych. | Część lutowia spłynie do otworów; możliwe pustki pod padem GND. Ryzyko niskie. | Zaakceptować (zgodne z Espressif), zamówić otwory wypełnione albo zmniejszyć ich liczbę; porównać wymiar padu 3,9 mm z rysunkiem Espressif (w tekście 3,7 mm, NIEPEWNE). |
| layout-10 | DROBNE | Brak punktów testowych. | Trudniejsze uruchomienie; sondowanie padów 0402 grozi zwarciem. | Pady testowe ok. 1 mm: VBUS_C, +5V, +3V3, +3V3A, BUCK_SW, 2–3 × GND, ETH_RST, ETH_SCLK/CS. |
| fab-08 | INFO | Projekt nie ma zdefiniowanego stosu warstw; plik zadania Gerbera podaje domyślny stos KiCada. | Impedancja par przypadkowa; dla USB FS i 100BASE-TX zwykle wystarcza. | Wybrać stos 4 warstw producenta i przeliczyć szerokości par (K6, K7). |

## 4. Schemat i elektryka

| ID | Waga | Problem | Skutek | Naprawa |
|---|---|---|---|---|
| produkt-15, interfejsy-06 | WAŻNE | Pin 3 każdego złącza przycisku J10–J15 ma zawsze +5 V, choć tor podświetlenia (PCA9685, Q1–Q6) jest DNP; +5 V leży tuż obok wejścia. | Pomyłka w ręcznie robionej wiązce poda 5 V przez diodę SRV05-4 na szynę 3V3 (ESP32 maks. 3,6 V): ryzyko uszkodzenia ESP32-S3 lub W5500. | Rev A: wiązki obsadzać tylko na pinach 1–2, rysunek wiązki, sprawdzić każdą wiązkę miernikiem. Rev B: rezystor 100–470 Ω szeregowo przed SRV05-4 albo TVS tylko do GND; rezystor 0 Ω (DNP) w zasilaniu złączy albo inny układ pinów. |
| interfejsy-02 | DROBNE | J20 ma układ GND, 3V3, EN, IO0, TXD0, RXD0. Typowy kabel FTDI TTL-232R-3V3 i przejściówki w tym układzie mają GND, CTS#, VCC (+5 V), TXD, RXD, RTS#. Przy GND na pinie 1: +5 V kabla → EN, TXD kabla → IO0, RTS# → RXD0; wciśnięcie RST (SW1) zwiera zasilanie kabla. Odwrócony kabel daje +5 V na IO0. | 5 V na EN lub IO0 ponad dopuszczalne napięcie, prąd przez diody ESD do szyny 3V3: ryzyko uszkodzenia ESP32-S3; brak odbioru danych. | Rev A: nie wpinać kabla FTDI wprost, przewody łączyć pojedynczo, bez VCC. Rev B: układ FTDI (1 GND, 4 RXD0, 5 TXD0, bez VCC; EN przez 100 nF dla automatycznego resetu), EN i IO0 osobno. |
| interfejsy-03 | DROBNE | J19 i J20 to identyczne listwy 1 × 6 w odstępie 5,2 mm, z odwrotnym układem zasilania (J19: pin 1 +3V3, pin 2 GND; J20: pin 1 GND, pin 2 +3V3). | Zamiana przewodów zwiera +3V3 albo podaje napięcie na wyjście przejściówki. | Różne złącza albo ten sam układ zasilania na pinach 1–2 obu listew i większy odstęp; minimum: legenda pinów po obu stronach płytki. |
| zasilanie-04 | DROBNE | D1 SMF5.0A (przebicie 6,4–7,0 V) nie chroni przetwornicy U3 (VIN maks. 6 V). Decyzja D2 w `DECYZJE.md` uznaje temat za zamknięty. | Przy przepięciu VBUS 6–7 V albo długim powyżej 9 V może zginąć U3, a po nim szyna 3V3. Dla prototypu ryzyko do przyjęcia. | Rev A: przyjąć świadomie i poprawić zapis D2. Rev B: ogranicznik przepięć lub eFuse ok. 5,8–6 V przed U3 albo przetwornica o wejściu ≥ 17 V. |
| zasilanie-11 | DROBNE | J19.6 (+5V) leży obok J19.5 (GPIO13 bez rezystora i ESD) i blisko J20 (J20.2 = +3V3). | Pomyłka przy podłączaniu może uszkodzić ESP32 i W5500. | Rev A: legenda pinów, tylko przejściówki 3,3 V. Rev B: 100–330 Ω szeregowo w EXP_IO13, +5V nie na skrajnym pinie obok sygnału. |
| zasilanie-12 | INFO | Zasilanie podane na J20.2 (3V3) albo J19.6 (+5V) trafia zwrotnie na VBUS złącza USB. | Niezgodne z zasadą, że urządzenie USB nie zasila VBUS. | Przy pracy z J20 nie podawać VCC z przejściówki, gdy pilot jest wpięty w USB. |
| zasilanie-06, interfejsy-07 | DROBNE | U7 (74LVC1G04) jest montowany, a jego wejście LORA_DIO2 wisi, dopóki E22 (U6) jest DNP. | Kilka mA zbędnego poboru, możliwy szum na 3V3. | U7 i R79 jako DNP do czasu montażu E22 albo 100 kΩ do GND na LORA_DIO2. |
| interfejsy-08 | INFO | E22-900M22S pin 12: Ebyte podaje NRST, projekt łączy go z GND. | LoRa może nie wystartować po wlutowaniu modułu (E22 jest DNP). | Przed wlutowaniem zmierzyć na module ciągłość pinu 12 z GND i z pinem 15; jeśli pin 12 to NRST, nie lutować pada 12. W Rev B sprawdzić przy przerysowaniu footprintu. |
| interfejsy-09, montaz-13 | DROBNE | Kwarc W5500 o CL = 18 pF z kondensatorami C40/C41 po 18 pF: rzeczywiste obciążenie ok. 12–14 pF. | Częstotliwość zawyżona, mniejszy zapas; najpewniej działa (tak rysuje WIZnet). | Na prototypie zmierzyć częstotliwość; w razie potrzeby C40/C41 22–27 pF C0G (tylko BOM). Symulacje: `sim/README.md`. |
| zasilanie-14, interfejsy-14 | INFO | Reset W5500 tylko z obwodu RC (R61/C39); przycisk RST, watchdog i reset programowy ESP32 nie resetują W5500. | Rzadkie zawieszenie W5500 wymaga odłączenia zasilania. | Firmware: reset programowy W5500 przy starcie. Rev B: RSTn z GPIO albo z ESP_EN przez diodę. |
| zasilanie-10 | INFO | GPIO45 (CS W5500) podciągnięty R68 do 1. Bezpieczne tylko dla modułu z PSRAM (N16R8); moduł bez PSRAM nie wystartuje. | Brak problemu przy N16R8. | Nie dopuszczać zamiennika U1; na pierwszej sztuce odczytać eFuse (`espefuse.py summary`: VDD_SPI_FORCE, VDD_SPI_TIEH). |
| zasilanie-13 | INFO | Pojemność wyjściowa TLV62569 i C4 (feed-forward, 6,8 pF) poza macierzą sprawdzoną przez TI; 6,8 pF nie pasuje do tego dzielnika. | Ewentualnie słabsza odpowiedź na skoki obciążenia. | Zmierzyć odpowiedź na skok obciążenia przy nadawaniu Wi-Fi; C4 zostawić DNP albo użyć ok. 27–33 pF. |
| zasilanie-07 | DROBNE | D2 dostaje ok. 0,6–0,8 mA z GPIO38 przez 1 kΩ. | Słabe, ale widoczne światło. | Dla jaśniejszego światła R50 330–470 Ω (bez zmiany miedzi). |
| zasilanie-03 | NIEPEWNE | R6/R7 (22 Ω w torze USB D−/D+) to jedyna droga D−/D+ do modułu; dostępność części przy montażu była niepewna. | Bez nich USB jest przerwane (zostaje UART na J20). | Sprawdzić dostępność przy zamówieniu; ewentualny zamiennik 22 Ω 1% albo 0 Ω. |
| zasilanie-09 | INFO | Budżet prądu z USB: ok. 0,2–0,4 A w konfiguracji Rev A (LoRa DNP, Wi-Fi wyłączone), 0,46–0,52 A przy wszystkich szczytach naraz. | Mieści się w 500 mA. | Utrzymać Wi-Fi domyślnie wyłączone; po montażu LoRa zmierzyć pobór. |
| zasilanie-05 | INFO | F1 (1206L110THYR, Vmax 8 V): kolejność J1 → F1 → D1 poprawna. | Brak problemu przy zasilaniu 5 V. | Ewentualna zmiana razem z zasilanie-04 w Rev B. |
| interfejsy-13 | INFO | LORA_NSS bez podciągania (linie LoRa i PCA9685 przy DNP bez zagrożeń). | — | Opcjonalnie 10–100 kΩ przy następnej zmianie miedzi. |
| interfejsy-15 | INFO | Ethernet bez auto-MDIX; adres MAC z eFuse ESP32. | — | Test na prototypie. |
| interfejsy-17 | INFO | Joystick J16 (XH 5-pin) wymaga własnej wiązki; kierunki są wpisane na stałe w firmware. | Zamienione kierunki da się poprawić w firmware albo wiązce. | Zmierzyć kolejność na próbce joysticka; opcjonalnie mapa kierunków w konfiguracji. |
| kryt-07 | INFO | Niezależna kontrola zgodności schemat–płytka: 0 rozbieżności pad–sieć. `pcb/kicad/pilot_wnet.net` nie zawiera H1–H4. | — | Przy następnym eksporcie odświeżyć netlistę (`kicad-cli sch export netlist`). |
| kryt-08 | INFO | Sterownik W5500 (`network.LAN`) jest w konfiguracji bazowej portu ESP32 MicroPythona; zegar SPI 20 MHz. | — | Przy wgraniu sprawdzić `network.PHY_W5500` i adres MAC (`firmware/README.md`). |

## 5. Montaż (otwarte)

| ID | Waga | Problem | Skutek | Naprawa |
|---|---|---|---|---|
| montaz-12 | DROBNE | Cztery nóżki obudowy gniazda USB-C J1 (THT) nie mają pasty. | Gniazdo trzymane tylko padami SMD może się oderwać przy wtykaniu kabla. | Zlecić lutowanie nóżek albo dolutować je ręcznie. |
| fab-09 | INFO | Wykończenie HASL przy rastrze 0,5 mm (W5500, USB-C). | Nieco większe ryzyko mostków. | Rozważyć ENIG. |
| fab-11 | INFO | Część parametrów leży na granicy reguł producenta (zgodne, bez zapasu). | Brak, dopóki producent nie zaostrzy reguł. | Opcjonalnie wydłużyć krótsze szczeliny USB-C, jeśli karta HRO na to pozwala (niesprawdzone). |

## 6. Mechanika i obudowa

| ID | Waga | Problem | Skutek | Naprawa |
|---|---|---|---|---|
| produkt-08, layout-11 | DROBNE | `projekt/arcade.toml` (i `arkusze_ciecia.py`, generator Blendera) zakłada płytkę 100 × 100 mm; otwór RJ45 jest przesunięty o ok. 15 mm względem gniazda, 3 z 4 otworów na tulejki M3 nie trafiają w H1–H4, brak kieszeni D8. Czoła J1 i J2 leżą ok. 13–14 mm pod zewnętrzną powierzchnią ściany 12 mm. Wpis „Konsekwencje” w `DECYZJE.md` twierdzi przeciwnie. | Wycięte według plików drewno nie przyjmie płytki. Płytki to nie dotyczy. | Obudowę dopasować do płytki (nie odwrotnie): obrys 90 × 100 mm, H1–H4, położenia J1, J2, D2 i strefy U1 odczytane z pliku płytki; kieszeń D8. Drewno ciąć po pomiarach próbek. |
| produkt-09 | DROBNE | Oś złącza SMA anteny LoRa w ściance wypada na wysokości płytki, 1,5–6,5 mm obok modułu U1 z anteną PCB. | Kolizja mechaniczna, rozstrojenie anteny Wi-Fi/BLE, sprzężenie nadajnika LoRa 22 dBm z ESP32; przewód IPEX przejdzie nad strefą anteny 2,4 GHz. | Otwór SMA poza obrysem płytki po stronie E22 albo nad poziomem elementów; przewód IPEX z dala od U1. |
| produkt-10 | DROBNE | Dioda stanu D2 świeci w górę, do wnętrza zamkniętej obudowy. | Stanu pilota nie widać z zewnątrz. | Diody RJ45 i OLED jako sygnalizacja albo światłowód w ściance. |
| produkt-16 | NIEPEWNE | USB-C w kieszeni D8 (3 mm drewna + 0,5 mm luzu, otwór 10 × 4,5 mm): wtyk może nie wejść na pełną głębokość. | Brak styku albo luźne połączenie. | Próba na kawałku sklejki z kablami, których używa studio. |
| layout-14 | INFO | BOOT/RST i złącze serwisowe J20 są dostępne tylko po otwarciu obudowy. | Odzysk po nieudanej aktualizacji firmware wymaga rozkręcenia. | Opcjonalnie otwór serwisowy w dnie albo przyciski wyprowadzone na zewnątrz. |
| produkt-17 | INFO | Instrukcja zamówienia przewidywała wysyłkę płyty stalowej, pleksi i wydruków 3D razem z płytkami, choć otwory joysticka w płycie mają powstać dopiero po pomiarze próbki (JLF-P1), a płyta waży ok. 0,93 kg. Moduł E22 nie ma ustalonego źródła (pusta karta w LCSC). | Elementy obudowy zamówione przed pomiarami mogą nie pasować do części. | Najpierw zamówić tylko płytki z montażem; blachę, pleksi i wydruki dopiero po pomiarach próbek. E22 nie jest potrzebny do uruchomienia (LoRa domyślnie wyłączona). |

## 7. Sprawdzone i w porządku (wybór)

- Pliki produkcyjne mieszczą się w możliwościach producenta: najwęższa ścieżka 0,15 mm, odstępy DRC ≥ 0,15 mm, mostki maski między padami różnych sieci ≥ 0,15 mm, odstępy otwór–otwór i otwór–miedź z zapasem, miedź ≥ 0,40 mm od krawędzi, wszystkie warstwy w obrysie 90 × 100 mm (fab-13).
- BOM (43 pozycje) i CPL (128 elementów) są spójne; elementy DNP nie trafiają do BOM ani CPL; wszystkie części leżą na stronie górnej.
- Strefa zakazu anteny modułu jest czysta na wszystkich 4 warstwach (layout-12).
- Co do schematu poprawne są: USB-C (rezystory CC 5,1 kΩ, bezpiecznik, TVS, USBLC6), przetwornica (rozkład pinów, dzielnik 3,33 V, dławik, kondensatory) i W5500 (wartości zgodne z referencją WIZnet).
- **Obalone:** interfejsy-01 (obawa, że podciągnięcie GPIO45 ustawi 1,8 V na flash i PSRAM). Dla modułu N16R8 z PSRAM napięcie VDD_SPI ustala eFuse, a nie GPIO45 (karta ESP32-S3-WROOM-1, rys. 8-1).
- Niezależna kontrola zgodności schemat–płytka: 0 rozbieżności pad–sieć (kryt-07).

## 8. Czego nie sprawdzono

- Wnętrze przycisku TS-1187A i biegunowość diod w gnieździe HR911105A: tylko wobec bibliotek, bez karty producenta.
- Footprint modułu LoRa E22 i kolizja pasma 863–865 MHz z bezprzewodowymi mikrofonami w studiu.
- Wydajność prądowa portu USB-C komputera studyjnego i stacji dokującej.
- Interpretacja plików przez system CAM producenta i podgląd montażu.
- Wpływ stalowej płyty blatu nad modułem na antenę Wi-Fi i BLE.

## 9. Pierwsze uruchomienie (propozycja audytu, kryt-05)

1. Oględziny: znacznik pinu 1 na U2, U3, U4, U7, U10–U12 i U1.
2. Omomierzem +5V–GND, +3V3–GND i +3V3A–GND przed zasileniem.
3. Pierwsze zasilanie przez tester USB z odczytem prądu albo z zasilacza 5 V z ograniczeniem prądu (ok. 0,1–0,3 A).
4. Pomiar +3V3: oczekiwane 3,21–3,45 V (dzielnik R3/R4).
5. Dopiero potem połączenie USB z komputerem, wgranie MicroPythona, odczyt eFuse (zasilanie-10) i pomiar częstotliwości kwarcu (interfejsy-09).

## 10. Zastrzeżenia

- Audyt, weryfikację i to streszczenie przygotowali agenci SI. Nikt z wykształceniem inżynierskim ich nie przejrzał.
- Liczby pochodzą z pomiarów pliku płytki i z kart katalogowych. Skutki opisane jako wnioskowane nie były sprawdzane na sprzęcie.
- Brak znaleziska nie oznacza braku wady. Rozdział 8 wymienia obszary, których nikt nie sprawdził.

## 11. Pliki poza repozytorium

Repozytorium nie zawiera plików pośrednich i lokalnych: wymiany z Freeroutingiem (`pcb/kicad/*.dsn`, `*.ses`), panelu KiKit (`pilot_wnet_panel.*`, tor historyczny z 18.10), lokalnych ustawień KiCada (`*.kicad_prl`) ani pośrednich raportów DRC. Nie ma w nim też skryptów do uruchamiania obliczeń na maszynie roboczej, raportu R4, logotypów Radia Wnet (znak towarowy) ani modelu 3D E22 (licencja nieustalona, zob. `NOTICE.md`). Pełny raport audytu, kosztorys i wyceny także nie są częścią repozytorium.

---

*Streszczenie przygotował agent SI (Claude) na podstawie raportu audytu agentów SI z 20.11.2026; bez przeglądu inżyniera.*
