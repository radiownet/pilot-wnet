---
tytul: "R5 — Krytyka kompletności i luki w raportach R1–R4 (Pilot Wnet, wersja arcade)"
projekt: "Pilot Wnet (wersja arcade, obudowa drewniana, własna płytka ESP32-S3)"
tor: "R5 krytyka"
data_sprawdzenia: "2026-10-18"
autor: "opracowanie SI (Claude), do weryfikacji przez człowieka"
status: "krytyka — nic nie zamówiono, nie założono kont, nie wypełniono formularzy, niczego nie zainstalowano"
---

# R5 — Krytyka kompletności i luki (stan na 18.10.2026)

> **Etykieta:** dokument przygotował agent SI (Claude) jako krytyk kompletności raportów R1–R4. Zawiera wyłącznie wnioski z czterech raportów, z plików projektu (`projekt/arcade.toml` v0.2, `docs/SPRZET.md`, `docs/ESP32_PROTOKOL.md`, wewnętrzny opis wyposażenia studia (poza repozytorium), firmware w `firmware/micropython/`) oraz z kontroli w sieci wykonanej 18.10.2026 między 12:20 a 12:40. Każda nowa liczba ma przy sobie adres źródła albo oznaczenie **[OBLICZENIE R5]**, **[SZACUNEK R5]** lub **[DO WERYFIKACJI]**. Liczby przejęte z R1–R4 mają odnośnik do raportu i rozdziału.
>
> **R4 (narzędzia EDA i testy) to raport wewnętrzny, niepublikowany** — nie ma go w tym repozytorium. Odwołania do niego zostawiono, żeby nie zmieniać treści krytyki. Wątki o wewnętrznej maszynie roboczej usunięto z wersji publicznej.
>
> **Ograniczenia metody:** wyszukiwarka części JLCPCB (`/parts/componentSearch`) zwracała w narzędziu WebFetch „0 Found” nawet dla części, które R3 tam znalazł, więc stanów magazynowych z R3 nie dało się powtórzyć; strony części JLCPCB pokazały typ części i tryb montażu, ale bez stanu i ceny.

---

## 0. Streszczenie

**Werdykt: na podstawie R1–R4 nie da się dziś złożyć zamówienia płytki ani obudowy.** Raporty są rzetelne w swoich torach, ale nie zostały ze sobą uzgodnione. Zamówienie blokuje dziewięć nierozstrzygniętych decyzji (rozdz. 4) oraz kilka sprzeczności, z których najważniejsze są poniżej.

1. **Moduł LoRa.** R1 wpisuje do katalogu „moduł LoRa 868 MHz Seeed C5129913” jako dostępny w JLCPCB. Sprawdziłem w LCSC: to **LoRa-E5 z własnym mikrokontrolerem STM32WLE5JC**, z oznaczeniem „Out of stock” (https://www.lcsc.com/product-detail/C5129913.html). Nie nadaje się do Meshtastic/MeshCore na ESP32 (zgodnie z R3, rozdz. 5.1). Moduł wybrany przez R3, Ebyte E22-900M22S, R3 widział w JLCPCB w liczbie 5 szt. jako zamówienie przedpłacone. Dziś strona części nie pokazuje stanu, a wyszukiwarka JLCPCB nie zwraca wyników. Strona produktu LCSC dla C411293 zwraca HTTP 404. **Dostępności modułu radiowego do montażu w fabryce nie potwierdzono.**
2. *(Pominięte w wersji publicznej: punkt dotyczył miejsca na dysku wewnętrznej maszyny roboczej.)*
3. **Gniazda USB-C i RJ45 w ściance 12 mm.** `arcade.toml` stawia tylną krawędź płytki 2 mm od wewnętrznej strony tylnej ścianki ze sklejki 12 mm, czyli czoła gniazd leżą ok. 14 mm za zewnętrzną powierzchnią **[OBLICZENIE R5]**. Wycięcie na USB-C ma 10 × 4,5 mm. Żaden raport nie sprawdził, czy wtyczka USB-C i zatrzask wtyczki RJ45 w ogóle dosięgną gniazda. To trzeba rozwiązać przed cięciem drewna (rozdz. 4.4).
4. **Podświetlenie przycisków.** R3 projektuje sterownik PCA9685, sześć tranzystorów i sześć złączy 4-pinowych na diody przycisków. Tymczasem R2 w zalecanym wariancie W1 wybiera Sanwa OBSC-30, OBSF-30 i OBSC-24. W tabeli przycisków podświetlanych R2 (rozdz. 3.3) mają one diodę tylko przez płytkę LED firmy trzeciej, której strona zwróciła błąd 404. Wbudowane diody mają w R2 Seimitsu PSL-30N z wariantu W2, Ultimarc Ultralux i Industrias Lorenzo. Decyzji „podświetlenie: tak/nie” nie ma.
5. **Złącza przewodów.** R1 wpisuje zaciski 4,8 mm (Keystone 1212). Według R2 przyciski Sanwa i Seimitsu mają terminale 2,8 mm i zaleca wiązki zakończone wtykami Dupont, czyli pod goldpin 2,54 mm. R3 umieszcza na płytce gniazda JST XH o rastrze 2,5 mm. Te trzy systemy do siebie nie pasują.
6. **Płytka bez parametrów produkcyjnych.** Żaden raport nie ustala liczby warstw, grubości, wykończenia, koloru maski ani obrysu z listwami technologicznymi. JLCPCB w montażu standardowym wymaga listew („Edge rails … Standard PCBA: Necessary”) i wysyła płytki z listwami domyślnie (https://jlcpcb.com/capabilities/pcb-assembly-capabilities). `arcade.toml` przewiduje płytkę dokładnie 100 × 100 mm, więc po dodaniu listew wyjdzie poza promocję „do 100 × 100 mm” z R1.
7. **Zgodność radiowa i studio.** R3 słusznie wskazuje dyrektywę RED. Pomija jednak dwie rzeczy. Wymagania cyberbezpieczeństwa RED (art. 3 ust. 3 lit. d–f) obowiązują od 1.08.2025 (https://www.nist.gov/document/nist-red-nb-assessment-checklist-articles-33-d-e-f-cybersecurity-version-10-september-25), a pilot z Wi-Fi im podlega. Do tego dochodzi ryzyko zakłóceń w studiu: mikrofon RØDE Interview PRO pracuje w 2,4 GHz (wewnętrzny opis wyposażenia studia, poza repozytorium), a pasmo 863–865 MHz służy mikrofonom bezprzewodowym (https://eur-lex.europa.eu/eli/dec_impl/2014/641/oj, motywy decyzji).
8. **Koszt i cło.** Z liczb R1 i R3 (opłaty montażowe 99,69 USD + kluczowe części 5 × 23,6 USD + płytki 2,00 USD) wychodzi ok. 219,69 USD **[OBLICZENIE R5]**, zanim doliczy się elementy pasywne i wysyłkę. Przy każdym kursie poniżej ok. 1,46 USD za euro to więcej niż 150 EUR **[OBLICZENIE R5]**, więc scenariusz R1 „B2C do 150 EUR z cłem 3 EUR” nie dotyczy zamówienia pięciu zmontowanych płytek. Obowiązuje wtedy zwykła odprawa (R1, rozdz. 5.3).

Mocne strony, które warto zachować: R1 jako jedyny zebrał pełny cennik montażu i opłaty przewoźników dla Polski. R2 uczciwie stwierdza brak oficjalnych kart Sanwa i Seimitsu i wymusza pomiar próbek. R3 dobrze uzasadnia wybór ESP32-S3 i układu pinów zgodnego z LilyGO T-ETH-Elite. R4 (raport wewnętrzny, niepublikowany) odpowiedzialnie wyłącza z budowy lokalnej PlatformIO dla Meshtastic i 3,3 GB modeli 3D KiCada.

---

## 1. Co sprawdziłem w sieci (18.10.2026, 12:20–12:40)

| Wątpliwość | Wynik | Źródło |
|---|---|---|
| Czym jest Seeed 317990829 (C5129913) z R1 | LoRa-E5 z wbudowanym STM32WLE5JC; „Out of stock”; cena referencyjna 8,064 USD (1+), 7,8588 USD (10+) | https://www.lcsc.com/product-detail/C5129913.html |
| E22-900M22S w JLCPCB (C411293) | Typ „Extended”, „PCBA Type: Economic and Standard”, obudowa „SMD,20x14mm”; stanu i ceny strona nie pokazała | https://jlcpcb.com/partdetail/Chengdu_Ebyte_ElecTech-E22900M22S/C411293 |
| E22-900M22S w wyszukiwarce JLCPCB | „Search results (0 Found)” (prawdopodobnie strona renderowana skryptem — wynik niemiarodajny) | https://jlcpcb.com/parts/componentSearch?searchTxt=E22-900M22S |
| E22-900M22S w LCSC | strona produktu C411293 — HTTP 404 | https://www.lcsc.com/product-detail/C411293.html |
| ESP32-S3-WROOM-1-N16R8 w JLCPCB | „Extended”, „Standard Only”, „X-ray Inspection: Required”, „MSL 3” | https://jlcpcb.com/partdetail/3198300-ESP32_S3_WROOM_1N16R8/C2913202 |
| ESP32-S3-WROOM-1U-N16R8 (C3013946) | wyszukiwarka „0 Found”; trybu montażu nie potwierdziłem | https://jlcpcb.com/parts/componentSearch?searchTxt=C3013946 |
| Listwy technologiczne w JLCPCB | Standard PCBA: listwy i znaczniki „Necessary”; pojedyncza płytka 70×70–460×500 mm; panel 70×70–250×250 mm; „Assembled PCBs are typically shipped with manufacturing rails (tooling edges) attached by default” | https://jlcpcb.com/capabilities/pcb-assembly-capabilities |
| Cennik montażu JLCPCB (aktualizacja 09.09.2026) | stawki z R1 potwierdzone; dodatkowo w tabeli: „Confirm parts placement” 0,45 USD, „Fixture” 8,21 USD za przyrząd (dla 1–29 szt. 16,42 USD), przechowywanie szablonu i przyrządu po 4,93 USD, „Pre-reflow soldering” 0,016 USD/pkt; strona nie wyjaśnia, kiedy te opłaty się nalicza | https://jlcpcb.com/help/article/pcb-assembly-price |
| Oferta 2 USD w JLCONE | „available exclusively through JLCONE Desktop and is no longer available on the JLCPCB website”; brak szczegółów warstw, rozmiaru i grubości; aktualizacja 22.09.2026 | https://jlcpcb.com/help/article/jlcone-desktop-app |
| Piny ESP32-S3 przy PSRAM Octal | „When using Octal flash or Octal PSRAM or both, GPIO33 ~ GPIO37 are connected to SPIIO4 ~ SPIIO7 and SPIDQS”; GPIO0, 3, 45, 46 to piny strapping; GPIO19/20 domyślnie USB-JTAG | https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/peripherals/gpio.html |
| Wariant Meshtastic `t-eth-elite` | sterowniki RF95, SX1262, SX1280 i LR1121 wykrywane w czasie pracy; SX1280: DIO2 33, DIO3 34, RXEN 13, TXEN 38; GPS RX 39, TX 42, 9600 b/s; LED 38; RESET 46 | https://raw.githubusercontent.com/meshtastic/firmware/develop/variants/esp32s3/t-eth-elite/variant.h |
| Skaner I2C Meshtastic pod adresem 0x40 | sprawdza INA226/INA260, ES7210, SHT2x (wysyła bajty „0xFA, 0x0F” i „0xFC, 0xC9”), INA219, HM330X; pętla skanuje 0x08–0x77 | https://raw.githubusercontent.com/meshtastic/firmware/develop/src/detect/ScanI2CTwoWire.cpp |
| HID producenta w MicroPythonie | `usb-device-hid` pozwala zbudować „any kind of HID device”, przykład z własnym deskryptorem; bez `builtin_driver=True` port szeregowy REPL może stać się niedostępny | https://github.com/micropython/micropython-lib/tree/master/micropython/usb |
| TPS63802 — napięcie wejścia | zakres 1,3–5,5 V, start powyżej 1,8 V; cewka 0,47 µH, kondensator wyjściowy min. 22 µF; tabeli Absolute Maximum Ratings nie odczytałem | https://www.ti.com/product/TPS63802 ; https://www.ti.com/document-viewer/TPS63802/datasheet |
| E22-900MM22S (zapas z R3) | SX1262, 850–930 MHz, 22 dBm, 10 × 10 × 2,5 mm; TCXO, rozkład pinów i przełącznik RF nie są podane na stronie | https://www.cdebyte.com/products/E22-900MM22S |
| Blacha w JLCCNC | grubości m.in. 1,5 mm; materiały Al 5052, stal nierdzewna 201/304, stal walcowana na zimno, ocynkowana; malowanie proszkowe dla wszystkich; wkładek wciskanych (PEM) strona nie wymienia; maks. długość 800 mm; tolerancja cięcia ±0,1 mm; 2–5 dni roboczych; cena tylko z wyceny | https://jlccnc.com/sheet-metal-fabrication |
| Certyfikat CE dla ESP32-S3-WROOM-1U | w wynikach wyszukiwania tylko SRRC i ISED; CE i listy anten **nie znalazłem** | https://www.espressif.com/en/certificates |
| RED — cyberbezpieczeństwo | art. 3 ust. 3 lit. d–f obowiązują od 1.08.2025; normy zharmonizowane EN 18031-1/-2/-3:2024 | https://www.nist.gov/document/nist-red-nb-assessment-checklist-articles-33-d-e-f-cybersecurity-version-10-september-25 ; https://digital.gob.es/content/dam/portal-mtdfp/avance-digital/telecomunicacion-e-infraestructuras-digitales/areas_interes/equipos-telecomunicacion/documents/Guia-aplicacion-EN-18031.pdf |
| RED — „oddanie do użytku” | dyrektywa obejmuje udostępnianie na rynku i oddanie do użytku, rozumiane jako pierwsze użycie przez użytkownika końcowego w UE (wg wyniku wyszukiwania tekstu skonsolidowanego) **[DO WERYFIKACJI w tekście art. 1 i 2]** | https://eur-lex.europa.eu/eli/dir/2014/53/2024-12-28/eng/pdf |
| Mikrofony bezprzewodowe 863–865 MHz | decyzja 2014/641/UE w motywach: 863–865 MHz zharmonizowane dla SRD „including wireless audio PMSE applications”; EN 300 422 obejmuje mikrofony w tym paśmie do 10 mW (opis normy — źródło pośrednie). Czy decyzję 2014/641/UE uchylono nowszą — **[DO WERYFIKACJI]** | https://eur-lex.europa.eu/eli/dec_impl/2014/641/oj ; https://standards.globalspec.com/std/10063151/en-300-422-2 |
| Wydajność portów USB-C komputera studyjnego | porty z USB Power Delivery; prądu dla urządzeń zasilanych z portu nie znalazłem | wyniki wyszukiwania (sprzedawcy, nie HP) — **[DO WERYFIKACJI w QuickSpecs HP]** |
| Sanwa JLF-H — raster złącza | sprzedawca podaje „5-pin JST” i wolne końce przewodów, bez rastra | https://www.arcadexpress.com/en/cables-wires/1293-5-pin-sanwa-jlf-h-cable-for-joystick.html |

---

## 2. Sprzeczności między raportami

| Nr | Raporty | Co mówi jeden | Co mówi drugi lub co stwierdziłem | Wniosek i decyzja do podjęcia |
|---|---|---|---|---|
| S1 | R1 ↔ R3 | R1 (rozdz. 0, 2.3, 6): moduł LoRa Seeed C5129913 jest w katalogu JLCPCB, tryb „Economic and Standard” | R3 (rozdz. 5.1): to nie jest moduł SX1262 sterowany przez SPI, stan 0 szt.; LCSC potwierdza LoRa-E5 z STM32WLE5JC i brak w magazynie (rozdz. 1) | Twierdzenie R1, że wszystkie kluczowe części są w jednym katalogu, nie dotyczy radia. Pozycję C5129913 trzeba usunąć z zestawień R1. |
| S2 | R1 ↔ R3 | R1 zakłada montaż wszystkich części w JLCPCB | R3: E22-900M22S w JLCPCB 5 szt., zamówienie przedpłacone; LCSC bez wyników. Dziś stanu nie da się odczytać (rozdz. 1) | Trzy drogi: (a) zamówienie przedpłacone w JLCPCB z ryzykiem czasu i ilości; (b) części powierzone — odprawa ok. 45 USD (R1, rozdz. 2.1); (c) moduł radiowy na osobnej płytce lub na złączu, lutowany ręcznie w Polsce. **Decyzja zespołu projektu.** |
| S3 | R1 wewnętrznie | Wariant „montaż ekonomiczny 59,91 USD” przy „innym wariancie modułu” | ESP32-S3-WROOM-1-N16R8 ma „Standard Only” i wymaga RTG (rozdz. 1); dla WROOM-1U trybu nie potwierdziłem | Scenariusz 59,91 USD jest dziś nierealny, dopóki żaden moduł ESP32-S3 z PSRAM nie ma potwierdzonego trybu ekonomicznego **[DO WERYFIKACJI]**. Do budżetu trzeba przyjąć tryb standardowy. |
| S4 | R1 ↔ R2 | R1: zaciski płaskie 4,8 mm na płytce (Keystone 1212, C3217931) | R2 (rozdz. 3.2): Sanwa i Seimitsu mają terminale 2,8 mm; 4,8 mm tylko Ultralux i Industrias Lorenzo | Przy częściach z zalecenia R2 zaciski 4,8 mm na płytce są zbędne. Usunąć z BOM, chyba że wybierze się Ultralux. |
| S5 | R2 ↔ R3 | R2 (rozdz. 4.4, 7.3): wiązki 2,8 mm → Dupont, wiązka JLF-H z jednym wolnym końcem | R3 (rozdz. 9.4): gniazda JST XH 2,5 mm (B4B-XH, XH-5) na płytce | Wtyk Dupont nie pasuje do XH. Trzeba wybrać jeden system: goldpin 2,54 mm pod gotowe wiązki z R2 albo XH z wiązkami zarabianymi samodzielnie lub zamówionymi (NextPCB robi wiązki JST — R1, rozdz. 4). Raster złącza joysticka nadal **[DO WERYFIKACJI pomiarem]**. |
| S6 | R2 ↔ R3 | R2, wariant W1: OBSC-30, OBSF-30, OBSC-24 (bez wbudowanych diod; dla OBSC-30 R2 wymienia tylko płytkę LED firmy trzeciej ze stroną 404) | R3 (rozdz. 9.3, 12): PCA9685 (3,3271 USD), 6 × AO3400A, 6 × B4B-XH z liniami LED+/LED–, szyna 5 V | Bez decyzji o podświetleniu płytka ma ok. 4,09 USD części na sztukę **[OBLICZENIE R5 z cen R3: 3,3271 + 6 × 0,0972 + 0,0804 + 0,1001]** i cztery dodatkowe rodzaje części po 1,53 USD opłaty za podajnik (R1). Propozycja: w Rev A pola lutownicze bez montażu (DNP) albo usunięcie tego toru. |
| S7 | R2 ↔ R3 ↔ R1 ↔ `arcade.toml` | R2 i `arcade.toml` v0.2: płyta nośna ze stali 1,5 mm na całym blacie | R3 (rozdz. 2.2): pod metalem lepszy jest WROOM-1U z anteną zewnętrzną; BOM R3 i wyliczenia R1 zakładają WROOM-1 z anteną PCB; `arcade.toml` nie ma otworu na antenę 2,4 GHz (są tylko USB-C, RJ45 i SMA dla LoRa) | Decyzja WROOM-1 albo WROOM-1U. Przy 1U potrzebne są: antena 2,4 GHz, przewód U.FL, drugi otwór w ściance i sprawdzenie, jakie anteny obejmuje deklaracja CE modułu (certyfikatu CE dla 1U nie znalazłem — rozdz. 1). Alternatywa: zostawić WROOM-1, ale z anteną przy krawędzi płytki, poza obrysem płyty stalowej, i sprawdzić zasięg pomiarem. |
| S8 | R2 ↔ `arcade.toml` | R2 (rozdz. 0, 4.2, 8): „obecny `arcade.toml`” ma blat 6,3 mm i zatrzaski nie zadziałają | `arcade.toml` v0.2 ma już 1,5 + 0,1 + 1,5 = 3,1 mm (wariant W1b) | Sprzeczność rozwiązana w pliku, ale R2 opisuje stan nieaktualny. Otwarte zostaje mocowanie płytki JLF-P1 w stali 1,5 mm pod pleksi 1,5 mm. `arcade.toml` sam proponuje trzpienie wciskane M4 albo łby w kieszeniach pleksi **[DO WERYFIKACJI z fabryką]**, a strona JLCCNC nie wymienia wciskanych trzpieni (rozdz. 1). Trzeba więc znaleźć wykonawcę, który je wciśnie, albo zmienić sposób mocowania. |
| S9 | Wymaganie ↔ R2 | Zadanie: STOP „duży” | R2 i `arcade.toml`: STOP to OBSF-30, ma 30 mm jak przyciski kolorowe; OBSF-40 wyprzedany (R2 [27]) | Wymaganie nie jest spełnione. Zespół projektu decyduje: STOP 30 mm wyróżniony kolorem i miejscem albo inny duży przycisk (dostępność **[DO WERYFIKACJI]**). |
| S10 | R3 ↔ `docs/ESP32_PROTOKOL.md` | R3 (rozdz. 7.1): do testu „klawiatura HID” | Protokół: HID producenta, strona użycia 0xFF00, „pilot nie jest klawiaturą” (ochrona przed BadUSB) | Testować `usb-device-hid` z własnym deskryptorem (micropython-lib to dopuszcza — rozdz. 1), nie klawiaturę. Jeśli REPL po USB ma zostać, w `boot.py` trzeba użyć `builtin_driver=True`; bez tego port szeregowy może stać się niedostępny aż do trybu awaryjnego lub skasowania pamięci (rozdz. 1). |
| S11 | R3 ↔ R4 | R3 (rozdz. 6.3): własny wariant Meshtastic i MeshCore do skompilowania | R4 (raport wewnętrzny, niepublikowany; rozdz. 5.6): nie budować na komputerze studyjnym, tylko w GitHub Actions | Zgodne co do kierunku, ale nikt nie przygotował repozytorium CI. Bez tego Rev A nie ma firmware'u mesh. |
| S12 | — | — | — | *(Pominięte w wersji publicznej: wiersz dotyczył miejsca na dysku wewnętrznej maszyny roboczej.)* |
| S13 | R3 ↔ ESP-IDF | R3 (rozdz. 6.1): układ T-ETH-Elite „nie koliduje” z PSRAM; zachowanie GPIO33/34 do testu | Wariant `t-eth-elite` definiuje dla SX1280 DIO2 = 33 i DIO3 = 34 (rozdz. 1). Przy PSRAM Octal GPIO33–37 to linie SPIIO4–SPIIO7 i SPIDQS pamięci (rozdz. 1) | To nie jest rzecz do testu, tylko do poprawki projektu: we własnym wariancie wyłączyć wykrywanie SX1280, LR1121 i RF95, żeby firmware nigdy nie dotknął GPIO33/34. Oryginalnego obrazu `t-eth-elite` na płytce bez radia nie uruchamiać. |
| S14 | R3 ↔ Meshtastic | R3 (rozdz. 9.3): adres PCA9685 względem skanera **[DO WERYFIKACJI]** | Skaner pod 0x40 wysyła sekwencje dwubajtowe „0xFA, 0x0F” i „0xFC, 0xC9” (rozdz. 1). W układzie z rejestrami pod tymi adresami (PCA9685 ma tam według mojej wiedzy rejestry ALL_LED **[DO WERYFIKACJI w karcie NXP]**) to zapis rejestru | Ustawić PCA9685 zworkami na adres, którego skaner nie sprawdza żadną sekwencją zapisu **[DO WERYFIKACJI w `ScanI2CTwoWire.cpp`: INA_ADDR, INA_ADDR_ALTERNATE, INA_ADDR_WAVESHARE_UPS]**, albo zrezygnować z PCA9685 (S6). |
| S15 | R3 wewnętrznie | rozdz. 0: „potwierdzony szczytowy pobór 0,61–0,63 A” | rozdz. 8.5: OLED, PCA9685, SK6812 i diody przycisków mają **[DO WERYFIKACJI]** | To suma szczytów z kart dla trzech odbiorników, czyli **dolna granica**, a nie wartość potwierdzona. Sformułowanie trzeba poprawić. |
| S16 | R3 ↔ TI | R3 (rozdz. 8.1): SMF5.0A ogranicza do 9,2 V; zgodność z wejściem TPS63802 **[DO WERYFIKACJI]** | Strona TI podaje zakres pracy 1,3–5,5 V, bez wartości maksymalnej dopuszczalnej (rozdz. 1) | Otwarte. Przy napięciu ograniczania 9,2 V wobec górnej granicy zakresu pracy 5,5 V trzeba sprawdzić w karcie tabelę Absolute Maximum Ratings. Jeśli granica jest niższa niż napięcie ograniczania, potrzebny jest bezpiecznik PTC i ogranicznik o niższym napięciu albo układ eFuse **[DO WERYFIKACJI]**. |
| S17 | R1 ↔ wysyłka | R1 (rozdz. 7, pkt 9): paczka ok. 300 g | W1 dokłada płytę stalową ok. 340 × 232 × 1,5 mm o masie ok. 0,93 kg; aluminium 5052 ok. 0,32 kg **[SZACUNEK R5; wymiary z `arcade.toml`, gęstości przyjęte podręcznikowo: stal 7,85 g/cm³, aluminium 2,7 g/cm³]** | Wycena wysyłki z blachą będzie wyraźnie inna. Porównać z cięciem laserowym w Polsce (brak wyceny w R1–R4). |

---

## 3. Liczby bez źródła albo ze źródłem niepewnym

| Raport | Liczba | Problem | Co zrobić |
|---|---|---|---|
| R1, rozdz. 2.2 | 30 rodzajów części, 350 punktów SMT, 60 punktów THT | Założenia przykładowe, nieuzgodnione z BOM z R3 | BOM R3 ma 20 rodzajów części SMT montowanych domyślnie (bez opcji). Lista braków R3 dodaje kolejne (cewka, kondensatory przetwornicy, PTC, dioda, rezystory 1 kΩ, 4,7 kΩ, 100 kΩ, 200 Ω, kondensatory 10 nF i 1 µF, elementy toru Ethernet). Daje to ok. 33–40 rodzajów **[SZACUNEK R5]** i opłatę za podajniki ok. 50–61 USD zamiast 45,90 USD **[OBLICZENIE R5: 33–40 × 1,53 USD]**. Policzyć na gotowym BOM. |
| R1, rozdz. 2.2 | razem 99,69 USD | W cenniku są pozycje nieuwzględnione: „Confirm parts placement” 0,45 USD, „Fixture” 16,42 USD dla 1–29 szt., „Pre-reflow soldering” 0,016 USD/pkt (rozdz. 1) | Sprawdzić w wycenie JLCPCB, czy te opłaty dotyczą płytki z częściami przewlekanymi **[DO WERYFIKACJI]**. |
| R1, rozdz. 1.2 | 250 cm²/USD dla 4 warstw | Strona JLCONE nie podaje warstw ani rozmiaru (rozdz. 1) | Liczba nadal niepotwierdzona. Opłaty montażu wynoszą ok. 100 USD (R1), a cena 5 płytek w JLCONE 2,00 USD. Ceny tych samych płytek na stronie WWW nikt nie sprawdził **[DO WERYFIKACJI]**. Dopiero ta liczba pokaże, czy instalacja JLCONE ma znaczenie dla kosztu. |
| R1, rozdz. 7, pkt 9 | paczka 300 g | Szacunek bez źródła | Zastąpić wagą z kalkulatora po decyzji o blasze (S17). |
| R2, rozdz. 4.5 | rozstawy 35–36,5 mm, 29 mm, 5,9/6,3/9,5 cm | Tylko serwis społecznościowy (oznaczenie F) | Wydruk 1:1 i makieta, jak zaleca R2. |
| R2, rozdz. 3.4 | wkładka 20,7 mm dla OBSC-30 i OBSC-24 | Ta sama liczba dla dwóch średnic — podejrzane (R2 sam to zaznacza) | Pomiar próbek; `arcade.toml` ma obie wartości jako `[ROBOCZE]`. |
| R2, rozdz. 3.1 | OBSF-30: 2,69 € w Arcade Express | Wynik wyszukiwarki pokazuje 2,19 € (poziom S, możliwie inna wersja strony) | Sprawdzić cenę w dniu zakupu. |
| R2 / `arcade.toml` | joystick: 69 mm (całość, AE), trzon 32,5 mm do spodu kuli, `wys_pod` 62 mm (bez źródła), `wys_nad` 46,9 mm (obliczenie) | Liczby nie mają wspólnego punktu odniesienia. Skrzynkę podniesiono o 10 mm pod joystick na podstawie wartości bez źródła | W miejscu joysticka (v = 0) zewnętrzna wysokość wynosi 85 mm, a wolne miejsce pod blatem 85 − 3,1 − 6,5 = 75,4 mm wobec wymaganych 62 + 8 = 70 mm, czyli zapas ok. 5 mm **[OBLICZENIE R5 z `arcade.toml`]**. Zmierzyć próbkę przed cięciem drewna. |
| R2 / `arcade.toml` | `glebokosc_pod` 45 mm pod przyciskami | `[ROBOCZE]`, przyjęte z dwóch innych modeli (PS-14: 32,5 mm; OBSN-30RG: 44 mm) | Pomiar OBSC-30 z konektorami. Ważne, bo REC i PLAY stoją nad płytką (rozdz. 4.4). |
| R3, rozdz. 8.1 | Rd 5,1 kΩ; domyślnie 500 mA z portu | Bez źródła USB-IF (R3 sam oznacza) | Sprawdzić w specyfikacji USB Type-C i w specyfikacji komputera studyjnego oraz stacji HP. |
| R3, rozdz. 8.5 | sprawność 85 % | Założenie (R3 oznacza) | Wykresy w karcie TPS63802. |
| R3, rozdz. 5.1 | E22-900M22S: 5 szt. | Dziś nie do powtórzenia (rozdz. 1) | Sprawdzić ręcznie w JLCPCB w dniu zamówienia. |
| R3, rozdz. 11 | RAK4630-8 / -9 a pasma | R3 oznacza **[DO WERYFIKACJI]** | Dotyczy dopiero Rev B. |
| R4 (raport wewnętrzny, niepublikowany), rozdz. 2.4 i 7.2 | 1,5–2,5 GB (KiCad bez modeli 3D) i inne `[SZACUNEK]` | Szacunki bez pomiaru | Mierzyć przyrost po każdym kroku, jak zaleca R4. |

---

## 4. Braki, które zablokują zamówienie

### 4.1. Płytka — parametry produkcyjne (nikt ich nie ustalił)

| Parametr | Stan w R1–R4 | Co trzeba ustalić |
|---|---|---|
| Liczba warstw | R1 porównuje ceny 2 i 4 warstw; R3 nie wybiera | Decyzja: 4 warstwy (pełna masa pod modułami radiowymi, W5500 i przetwornicą) albo 2 warstwy. Wpływa na cenę u wszystkich fabryk (R1, rozdz. 1.2). |
| Grubość, miedź | R1 cytuje czasy dla 1,6 mm i 1 oz | Przyjąć 1,6 mm i 1 oz, zgodnie z `arcade.toml` (`grub = 1.6`), i wpisać do pakietu zamówienia. |
| Wykończenie | brak | HASL bezołowiowy albo ENIG. W BOM są drobne obudowy: LQFP-48 (W5500), VSON-HR 3 × 2 mm (TPS63802), TSSOP-28 (PCA9685) — R3, rozdz. 4.3, 8.2, 9.3. Decyzja wpływa na cenę **[DO WERYFIKACJI w kalkulatorze]**. |
| Obrys z listwami | `arcade.toml`: 100 × 100 mm; JLCPCB: listwy wymagane w Standard PCBA i wysyłane domyślnie (rozdz. 1) | Projektować płytkę mniejszą (np. 100 × 90 mm z listwami w obrysie 100 × 100 mm) albo przyjąć wyjście poza promocję. Uzgodnić z `[plytka]` w `arcade.toml` i z tulejkami M3. |
| Droga sygnału antenowego | R3 dopuszcza złącze IPEX na module albo U.FL na płytce (rozdz. 5.7) | Jeśli U.FL na płytce, potrzebna ścieżka 50 Ω, czyli kontrolowana impedancja i znany układ warstw. Najprościej użyć IPEX modułu i pominąć ścieżkę RF na płytce. |
| Liczba płytek zmontowanych | R1 liczy 5 szt. | JLCPCB montuje w trybie standardowym od 2 szt. (R1, rozdz. 2.1). Przy 2 szt. koszt części spada o ok. 70,8 USD **[OBLICZENIE R5: 3 × 23,6 USD z R3]**, a opłaty stałe zostają. Decyzja zespołu projektu. |
| Pliki | brak schematu, płytki, BOM i CPL; `docs/SPRZET.md` wskazuje na `pcb/README.md` i `zamowienie/`, których nie ma (o 12:29 powstał tylko `pcb/lib/`) | Zamówienie wymaga: Gerberów, wierceń, BOM z numerami C, CPL z korektami obrotów i przeglądu podglądu w JLCPCB przez człowieka (R4, rozdz. 8). |

### 4.2. Montaż i części

- **Moduł LoRa i jego źródło** — S1, S2. Bez tej decyzji nie da się zamknąć BOM.
- **WROOM-1 czy WROOM-1U** — S7.
- **Podświetlenie** — S6. **Akumulator** — R3 przewiduje TP4056 jako opcję (rozdz. 8.3). Zalecam w Rev A pola bez montażu i bez ogniwa: ogniwo Li-ion w drewnianej skrzynce w studiu to dodatkowe ryzyko pożarowe, a R3 sam wskazuje, że do pracy na baterii lepszy jest Rev B z nRF52840 (rozdz. 8.6).
- **Brakujące elementy BOM** — R3 sam wymienia brak dławików, kondensatorów, elementów toru Ethernet z noty WIZnet, bezpiecznika PTC, złącza ogniwa, diody statusu i kondensatora wejściowego (rozdz. 12). Bez nich nie ma BOM do wyceny.
- **Adres MAC dla W5500** — W5500 nie ma własnego numeru MAC, a raporty nie mówią, skąd firmware go weźmie (np. z eFuse ESP32-S3) **[DO WERYFIKACJI w dokumentacji ESP-IDF i MicroPython `network.LAN`]**.
- **Złącza wejść** — S4, S5.

### 4.3. Anteny

- **LoRa:** typ, zysk i długość anteny 868 MHz, przewód IPEX → SMA i jego długość, złącze SMA na ściankę 12 mm. Czy gwint złącza obejmie 12 mm sklejki, czy trzeba wiercić pogłębienie, nie wiadomo **[DO WERYFIKACJI w karcie złącza]**. Zysk anteny decyduje o mocy, którą wolno ustawić w pasmach 25 mW (R3, rozdz. 5.5).
- **2,4 GHz:** S7.

### 4.4. Mechanika obudowy wobec płytki (luka między R2 i R3)

- **Gniazda w ściance 12 mm** (rozdz. 0, pkt 3). Rozwiązania do wyboru: (a) gniazda panelowe na tylnej ściance (USB-C i RJ45 typu keystone) z krótkimi przewodami do płytki; (b) kieszeń frezowana od środka, pocieniająca ściankę wokół gniazd; (c) wysunięcie krawędzi płytki w szczelinę w ściance. Żadnej z tych wersji nie ma w `arkusze_ciecia.py`, który dla tylnej ścianki rysuje tylko prostokąty i koło (z dopiskiem „wymiary zweryfikować z płytką”).
- **Przyciski nad płytką:** REC (u = 30, v = 22) i PLAY (u = 72, v = 22) leżą nad obrysem płytki (x od −10 do 90 mm, y od 1 do 101 mm). Spód ich korpusów (45 mm, wartość robocza) wypada ok. 39,7 mm nad zewnętrznym dnem, a wierzch płytki 6,5 + 8 + 1,6 = 16,1 mm nad dnem, więc luz wynosi ok. 23,6 mm na elementy, konektory i przewody **[OBLICZENIE R5 z `arcade.toml`]**. Sprawdzić kolizje w STEP (R4, rozdz. 6, pkt 3), zanim powstanie rozmieszczenie elementów.
- **Uziemienie płyty stalowej:** płyta W1 przykrywa cały blat, a trzon joysticka jest metalowy. Raporty nie mówią, czy płytę łączyć z masą płytki (ekranowanie i ESD) **[DO WERYFIKACJI — decyzja projektowa]**.
- **Mocowanie JLF-P1 w stali 1,5 mm** — S8.
- **Mocowanie OLED** pod oknem 34 × 18 mm w płycie i folii (`arcade.toml`) — brak opisu w R2 i R3.

### 4.5. Firmware (warunek sensu zamówienia)

- **Ścieżka kompilacji Meshtastic/MeshCore** (CI) — S11.
- **Własny wariant Meshtastic** z wyłączonymi SX1280/LR1121/RF95 i GPS — S13. R3 proponuje `#define HAS_GPS 0`; trzeba też upewnić się, że GPIO39 (PLAY) i GPIO42 nie będą sterowane jako UART **[DO WERYFIKACJI w kodzie]**.
- **HID producenta** w MicroPythonie — S10. Firmware w repozytorium ma dziś transporty UDP i BLE (`pilot_transport.py`), ale nie ma USB, choć protokół nazywa USB HID „domyślnym i zalecanym”.
- **Test na LilyGO T-ETH-Elite przed zamówieniem PCB** (R3, rozdz. 3.2) — dobry pomysł, ale zakup płytki to decyzja człowieka, a jej ceny i dostępności żaden raport nie podał **[DO WERYFIKACJI]**.

### 4.6. Narzędzia

*(Pominięte w wersji publicznej: punkt dotyczył miejsca na dysku i instalacji programów na wewnętrznej maszynie roboczej.)*

### 4.7. Formalności

- **Kto zamawia:** spółka (B2B, odprawa formalna, odliczenie VAT) czy osoba prywatna (B2C, IOSS). Przy wartości powyżej 150 EUR (rozdz. 0, pkt 8) obowiązuje zwykła odprawa, VAT 23 % i opłata przewoźnika za wyłożenie należności: DHL 2,5 %, min. 69,00 PLN; UPS 3 %, min. 85,00 PLN; FedEx 2,5 %, min. 63,60 PLN (R1, rozdz. 5.2, za https://jlcpcb.com/help/article/eu-customs-reform-faq). Decyzja zamawiającego.
- **Kod taryfowy zmontowanej płytki z radiem** i stawka celna — R1 oznacza **[DO WERYFIKACJI w TARIC]**.
- **RED** — rozdz. 5.

### 4.8. Usługi lokalne (żaden raport ich nie wycenił)

Korpus ze sklejki (CNC lub laser), druk folii z grafiką, pleksi 1,5 mm z otworami, wkładki do OBSC, ewentualnie blacha w Polsce zamiast JLCCNC. R1 i R2 mówią „zlecić lokalnie”, ale nie podają wykonawcy, ceny ani terminu **[DO WERYFIKACJI]**.

---

## 5. Ryzyka pominięte w R1–R4

1. **Zakłócenia w studiu, 2,4 GHz.** RØDE Interview PRO łączy się z odbiornikiem Series IV w 2,4 GHz (wewnętrzny opis wyposażenia studia, poza repozytorium; za https://rode.com/en/microphones/wireless/interview-pro). ESP32-S3 nadaje Wi-Fi z mocą do 20,5 dBm (R3, rozdz. 8.5). Raporty nie oceniają współistnienia. Zalecenie: w studiu łącze przez Ethernet lub USB, Wi-Fi domyślnie wyłączone, BLE z małą mocą. Próbę zrobić z nagraniem kontrolnym mikrofonu.
2. **Zakłócenia w studiu, okolice 868 MHz.** Pasmo 863–865 MHz jest używane przez mikrofony bezprzewodowe (rozdz. 1). Węzeł LoRa na 869,525 MHz (R3, rozdz. 7.2) z mocą do 22 dBm (R3, rozdz. 5.2) jest od tego pasma odległy o 4,5–6,5 MHz **[OBLICZENIE R5]**. Może zagłuszać odbiorniki stojące obok, jeśli redakcja ma takie mikrofony **[DO WERYFIKACJI: jakie częstotliwości mają systemy bezprzewodowe w studiu Wnet]**.
3. **RED obejmuje też urządzenie zrobione na własny użytek firmy.** Dyrektywa dotyczy także oddania do użytku, czyli pierwszego użycia przez użytkownika końcowego (rozdz. 1, **[DO WERYFIKACJI w art. 1–2]**). Wyjątek dla urządzeń budowanych przez krótkofalowców dotyczy krótkofalowców, nie spółki (sygnał z UBA: https://www.uba.be/en/news/new-european-directive-making-available-market-radio-equipment). Do tego dochodzą wymagania cyberbezpieczeństwa od 1.08.2025 (EN 18031-1). Pilot jest urządzeniem z Wi-Fi, wiązaniem BLE i kluczem HMAC (`docs/ESP32_PROTOKOL.md`). Część tych środków już jest, ale nikt nie zestawił ich z normą. Pytanie do prawnika lub laboratorium przed użyciem pilota w studiu.
4. **START na GPIO0.** Wciśnięcie START podczas resetu uruchamia tryb pobierania. R3 traktuje to jako zaletę (rozdz. 9.4). W studiu oznacza to, że pilot podłączany z wciśniętym START albo resetowany przez watchdog przy wciśniętym START przestaje działać do kolejnego resetu. Do rozważenia: START na innym pinie (np. GPIO42 po wyłączeniu GPS we własnym wariancie, za rezystorem 1 kΩ z R3), a BOOT tylko jako przycisk na płytce. Koszt: Meshtastic straci przycisk użytkownika na GPIO0 we własnym wariancie **[DO WERYFIKACJI w `BUTTON_PIN`]**.
5. **Uzależnienie od biblioteki fabryki.** Części kupione w JLCPCB „cannot be shipped separately” (R1, rozdz. 8). Przy pre-orderze E22 i nieudanym montażu moduły zostają w Chinach. To dodatkowy argument za radiem na złączu (S2, wariant c).

---

## 6. Do sprawdzenia przez człowieka (w kolejności użycia)

**Decyzje zespołu projektu (przed projektem płytki):**
1. Podświetlenie przycisków: tak czy nie w Rev A (S6).
2. Akumulator: zalecam „nie” w Rev A (rozdz. 4.2).
3. WROOM-1 czy WROOM-1U i gdzie antena 2,4 GHz (S7).
4. Moduł LoRa i źródło: pre-order w JLCPCB, części powierzone czy moduł na złączu (S2).
5. System złączy wejść: goldpin 2,54 mm czy JST XH (S5).
6. STOP 30 mm czy większy (S9).
7. Liczba warstw, wykończenie, liczba płytek zmontowanych (2 czy 5), zamawiający (spółka czy osoba) (rozdz. 4.1, 4.7).
8. Gniazda panelowe czy kieszeń w tylnej ściance (rozdz. 4.4).

**Pomiary i zakupy próbek (zakup robi człowiek):**
9. Joystick JLX2/JLF: wysokość nad i pod blatem, rozstaw otworów JLF-P1, raster złącza i kolejność przewodów JLF-H (R2, rozdz. 7.4).
10. OBSC-30, OBSC-24, OBSF-30: głębokość pod blatem z konektorami, średnica wkładek, grubość terminala SW-68.
11. Wtyczka USB-C i RJ45 wobec ścianki 12 mm na kawałku sklejki z wyciętym otworem.
12. Odsłuch klików przy mikrofonie studyjnym (R2, rozdz. 6).

**Sprawdzenia w dniu zamówienia (strony fabryk, bez wypełniania formularzy przez agenta):**
13. Stan E22-900M22S (C411293), E22-900MM22S (C5333985) i Ra-01SH (C2764087) w JLCPCB; tryb montażu ESP32-S3-WROOM-1U (C3013946).
14. Wycena tych samych plików w JLCPCB, PCBWay i NextPCB, z listwami; czy naliczane są „Fixture”, „Confirm parts placement” i „Pre-reflow soldering”.
15. Waga i koszt wysyłki z blachą i bez niej; DDP a odprawa formalna; kod taryfowy.
16. JLCONE: cena tych samych płytek na stronie WWW, żeby ocenić, czy instalacja aplikacji ma znaczenie dla kosztu (rozdz. 3, wiersz R1 1.2).

**Dokumenty techniczne:**
17. TPS63802: tabela Absolute Maximum Ratings wobec 9,2 V z SMF5.0A (S16).
18. PCA9685: mapa rejestrów pod 0xFA–0xFD i domyślny adres; adresy INA w skanerze Meshtastic (S14).
19. ESP32-S3-WROOM-1U: deklaracja CE i lista anten u Espressif (S7).
20. Wydajność prądowa portów USB-C komputera studyjnego i stacji HP; auto-MDIX stacji (R3, rozdz. 4.4).
21. Źródło MAC dla W5500 w MicroPythonie i Meshtastic (rozdz. 4.2).

**Przed użyciem w studiu:**
22. Częstotliwości mikrofonów i odsłuchów bezprzewodowych w studiu Wnet (rozdz. 5, pkt 1–2).
23. RED: konsultacja z prawnikiem lub laboratorium, także w zakresie cyberbezpieczeństwa (rozdz. 5, pkt 3).

---

## 7. Proponowana ścieżka odblokowania

1. **Decyzje 1–8** (rozdz. 6) zapisane w `arcade.toml` i w nowym `pcb/README.md`, zanim powstanie schemat.
2. **Próbki i makieta** (punkty 9–12). Bez nich nie wolno ciąć drewna ani zamykać wysokości skrzynki (rozdz. 3, wiersz o joysticku).
3. **Narzędzia** (R4 — raport wewnętrzny, niepublikowany).
4. **Schemat i płytka** z obrysem uwzględniającym listwy, złączami zgodnymi z wiązkami i radiem z potwierdzonym źródłem. Kontrola kolizji w STEP z modelem obudowy.
5. **Firmware:** wariant Meshtastic bez SX1280/LR1121/RF95 i GPS, kompilowany w CI; test HID producenta w MicroPythonie; najlepiej najpierw na T-ETH-Elite.
6. **Trzy wyceny** na tych samych plikach, wykonane przez człowieka (R1, rozdz. 6).
7. **Zamówienie** składa człowiek (HITL, `docs/SPRZET.md`).
8. **Zgodność radiowa i próba w studiu** przed pierwszym użyciem na antenie.

---

## 8. Źródła sprawdzone przez R5 (18.10.2026)

- LCSC, C5129913 (Seeed 317990829, LoRa-E5) — https://www.lcsc.com/product-detail/C5129913.html
- LCSC, C411293 (HTTP 404) — https://www.lcsc.com/product-detail/C411293.html
- JLCPCB, część C411293 E22-900M22S — https://jlcpcb.com/partdetail/Chengdu_Ebyte_ElecTech-E22900M22S/C411293
- JLCPCB, wyszukiwarka E22-900M22S i C3013946 (0 wyników w narzędziu) — https://jlcpcb.com/parts/componentSearch?searchTxt=E22-900M22S ; https://jlcpcb.com/parts/componentSearch?searchTxt=C3013946
- JLCPCB, część C2913202 ESP32-S3-WROOM-1-N16R8 — https://jlcpcb.com/partdetail/3198300-ESP32_S3_WROOM_1N16R8/C2913202
- JLCPCB, „PCB Assembly Capabilities” — https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- JLCPCB, „PCB Assembly Cost”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/pcb-assembly-price
- JLCPCB, „JLCONE FAQ”, aktualizacja 22.09.2026 — https://jlcpcb.com/help/article/jlcone-desktop-app
- JLCCNC, „Sheet Metal Fabrication” — https://jlccnc.com/sheet-metal-fabrication
- Texas Instruments, TPS63802 — https://www.ti.com/product/TPS63802 ; https://www.ti.com/document-viewer/TPS63802/datasheet
- Ebyte, E22-900MM22S — https://www.cdebyte.com/products/E22-900MM22S
- Espressif, ESP-IDF v6.1, GPIO (ESP32-S3) — https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32s3/api-reference/peripherals/gpio.html
- Espressif, certyfikaty — https://www.espressif.com/en/certificates
- Meshtastic, `variants/esp32s3/t-eth-elite/variant.h` i `platformio.ini` — https://raw.githubusercontent.com/meshtastic/firmware/develop/variants/esp32s3/t-eth-elite/variant.h ; https://raw.githubusercontent.com/meshtastic/firmware/develop/variants/esp32s3/t-eth-elite/platformio.ini
- Meshtastic, `src/detect/ScanI2C.h` i `ScanI2CTwoWire.cpp` — https://raw.githubusercontent.com/meshtastic/firmware/develop/src/detect/ScanI2C.h ; https://raw.githubusercontent.com/meshtastic/firmware/develop/src/detect/ScanI2CTwoWire.cpp
- micropython-lib, `micropython/usb` — https://github.com/micropython/micropython-lib/tree/master/micropython/usb
- Decyzja wykonawcza Komisji 2014/641/UE — https://eur-lex.europa.eu/eli/dec_impl/2014/641/oj
- EN 300 422-2, opis normy (źródło pośrednie) — https://standards.globalspec.com/std/10063151/en-300-422-2
- Dyrektywa 2014/53/UE, tekst skonsolidowany (wynik wyszukiwania) — https://eur-lex.europa.eu/eli/dir/2014/53/2024-12-28/eng/pdf
- NIST, lista kontrolna RED art. 3.3 d/e/f (data stosowania 1.08.2025) — https://www.nist.gov/document/nist-red-nb-assessment-checklist-articles-33-d-e-f-cybersecurity-version-10-september-25
- Ministerstwo ds. cyfryzacji Hiszpanii, przewodnik EN 18031 — https://digital.gob.es/content/dam/portal-mtdfp/avance-digital/telecomunicacion-e-infraestructuras-digitales/areas_interes/equipos-telecomunicacion/documents/Guia-aplicacion-EN-18031.pdf
- UBA (sygnał, nie źródło liczby) — https://www.uba.be/en/news/new-european-directive-making-available-market-radio-equipment
- Arcade Express, wiązka JLF-H — https://www.arcadexpress.com/en/cables-wires/1293-5-pin-sanwa-jlf-h-cable-for-joystick.html
- Pliki projektu (odczyt): `projekt/arcade.toml` v0.2, `projekt/arkusze_ciecia.py`, `docs/SPRZET.md`, `docs/ESP32_PROTOKOL.md`, `firmware/micropython/lib/pilot_wejscia.py`, `pilot_transport.py`.
