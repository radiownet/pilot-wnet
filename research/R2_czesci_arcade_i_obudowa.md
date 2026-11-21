# R2 — Części arcade i drewniana obudowa Pilota Wnet

- **Tor:** arcade (joystick, przyciski, obudowa, zakupy, zalecenie).
- **Data sprawdzenia wszystkich źródeł:** 18.10.2026 (o ile przy pozycji nie podano inaczej).
- **Opracowanie:** Claude (SI), na zlecenie skryptu orkiestrującego. Raport jest materiałem roboczym do decyzji człowieka; niczego nie kupiono, nie założono kont, nie wysłano formularzy.
- **Powiązane pliki:** `projekt/arcade.toml` (wartości `[ROBOCZE]`), `branding/naklejki.py` (generator naklejek; poza tym repozytorium). Raport tylko proponuje zmiany w tych plikach (sekcja 8), nie wprowadza ich.

---

## 0. Najważniejsze w pięciu zdaniach

1. Nie znalazłem w sieci aktualnych, oficjalnych kart katalogowych ani rysunków wymiarowych Sanwa Denshi i Seimitsu Kogyo: witryna Seimitsu (`http://www.seimitsu.jp/`) zwraca pustą stronę (nagłówek `Last-Modified: Thu, 16 Jan 2020`), a pod HTTPS błąd certyfikatu; domena `sanwa-denshi.co.jp` należy do innego Sanwa (modelarstwo RC). Wszystkie liczby o częściach pochodzą więc od dystrybutorów i sklepów, a wymiary krytyczne dla frezowania trzeba potwierdzić pomiarem próbek.
2. Bieżący `arcade.toml` przewiduje blat „pleksi 3 mm + grafika 0,3 mm + płyta 3 mm” = 6,3 mm, a przyciski zatrzaskowe Sanwa OBSF/OBSC mają według dystrybutorów zakres 2–4 mm albo „do 3,7 mm”. **Przy tym blacie przyciski zatrzaskowe nie zadziałają** — trzeba albo przejść na przyciski wkręcane (Sanwa OBSN do 8 mm, Seimitsu PS-14-GN/DN do 7 mm wg Arcade Express), albo odchudzić blat do ok. 3,1–3,6 mm na płycie metalowej.
3. Następcą Sanwa JLF-TP-8YT jest JLX2-TP-8YT (sklepy podają, że zastępuje JLF i JLX); w UE jest go mało (Arcade Express: brak w magazynie), w USA jest dostępny (Arcade Renovations: 108 szt.). Seimitsu LS-32-01 jest dostępny w UE (Arcade Express: 45 szt.).
4. Pilot stoi w studiu radiowym, więc klik mikroprzełączników trafi do mikrofonów — warto rozważyć ciche wersje: przyciski Sanwa OBSFE-30 (elastomer) i joystick Sanwa JLX2-TPML-8YT-SK (przełączniki listkowe); żaden sprzedawca nie podaje poziomu hałasu w dB, więc decyzja wymaga próby odsłuchowej.
5. Zalecenie (sekcja 7): drewniana skrzynka ze sklejki brzozowej 12–15 mm, blat warstwowy na płycie stalowej 1,5 mm (wariant W1) z przyciskami Sanwa OBSC-30/OBSFE-30/OBSF-24 i joystickiem JLX2-TP-8YT na płytce JLF-P1; jeśli blat ma być w całości drewniany (wariant W2) — przyciski wkręcane Sanwa OBSN-30/OBSN-24 lub Seimitsu PS-14-GN/KN/DN i kieszenie frezowane od spodu.

---

## 1. Metoda, poziomy źródeł i ograniczenia

**Poziomy źródeł** (oznaczenie przy liczbach w tabelach):

| Znak | Rodzaj źródła | Jak traktować liczbę |
|---|---|---|
| **P** | strona producenta (Ultimarc, Adafruit, UPM WISA) | liczba z karty producenta |
| **D** | dystrybutor/sklep specjalistyczny powtarzający dane producenta (Arcade Express, Paradise Arcade Shop, Focus Attack, Arcade Renovations, The Pi Hut, Core Electronics) | liczba z karty sklepu; wymiary do frezowania potwierdzić pomiarem |
| **S** | marketplace, wyciąg wyszukiwarki z niedostępnej strony | **[DO WERYFIKACJI]** |
| **F** | forum, recenzja, serwis społecznościowy (slagcoin.com, TechRadar, komentarze kupujących) | tylko sygnał, nigdy źródło liczby — **[DO WERYFIKACJI]** |

**Ograniczenia stwierdzone 18.10.2026:**

- Sanwa Denshi (三和電子株式会社, Itabashi, Tokio — producent części do automatów) nie ma w wynikach wyszukiwania żadnej strony z katalogiem; `sanwa-denshi.co.jp` to Sanwa od aparatury RC, `sanwadenshi.com` to firma telekomunikacyjna, `www.sanwadenshi.jp` zwraca HTTP 403. Rysunków wymiarowych JLF/OBSF w sieci nie znalazłem.
- Seimitsu Kogyo: `http://www.seimitsu.jp/` — 45 bajtów pustego HTML, `Last-Modified: Thu, 16 Jan 2020 16:17:35 GMT`; `https://www.seimitsu.jp/` — certyfikat wystawiony na `*.alpha-mail.jp`.
- Sklepy japońskie (Tsukumo, Yodobashi) i Monotaro nie odpowiedziały (zerwane połączenie, przekroczony czas, HTTP 403). Ich ceny pochodzą tylko z wyciągów wyszukiwarki (poziom S).
- Strona `akihabarashop.jp`, dawniej znana jako eksporter części arcade, pokazuje dziś niezwiązane artykuły o futbolu — **nie korzystać** (ryzyko przejętej domeny).
- Strona Arcadewinkel (NL) nie otworzyła się z powodu błędu łańcucha certyfikatów.
- Instrukcja PDF pod adresem `arcadespareparts.com/manuals/sanwa_joystick_jlf_tp_8yt_g_green_218.pdf` okazała się instrukcją niezwiązanego konwertera wideo (ID 12205) — **nie korzystać**.

---

## 2. Joysticki

### 2.1. Zestawienie parametrów

| Parametr | Sanwa JLF-TP-8YT | Sanwa JLX2-TP-8YT | Seimitsu LS-32-01 | Seimitsu LS-40-01 |
|---|---|---|---|---|
| Status rynkowy | sklepy US i ES: brak w magazynie; The Pi Hut (UK): 14 szt. w zestawie z kulą — **D** [1][2][5] | według sklepu następca JLF i JLX — **D** [7] | dostępny w UE — **D** [8] | brak w magazynie w ES — **D** [10] |
| Wysokość | 69 mm (opis sklepu bez punktu odniesienia) — **D** [1] | 69 mm — **D** [6] | 61 mm — **D** [8]; kula 1 1/8″ nad płytką RE, całość 2 1/2″ od płytki do wierzchu kuli — **D** [9] | [DO WERYFIKACJI] |
| Długość trzonu | 32,5 mm „do spodu kuli” — **D** [2] | [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] |
| Masa | 280 g — **D** [1] | 200 g i 280 g na tej samej stronie (sprzeczność) — **D** [6] | 280 g — **D** [8] | 220 g — **D** [10] |
| Płytka montażowa | JLF-P1: 95 × 53 × 1,6 mm — **D** [5]; ta sama płytka u innego sklepu: 94 × 40 mm (sprzeczność) — **D** [11] | JL-P1 / JLF-P1 w zestawie — **D** [6][12] | płytka SE (płaska) lub SS (bliżej powierzchni) — **D** [13] | ta sama płytka co LS-32 — **D** [10] |
| Rozstaw otworów płytki | [DO WERYFIKACJI — zmierzyć próbkę] | jak JLF [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] |
| Maks. grubość panelu | „do 5 mm” — tylko sygnał z agregatora instrukcji (strona zablokowana, HTTP 403) — **F** [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] |
| Bramka (restryktor) | kwadratowa 8/4, przełączana obrotem — **D** [2][5]; ośmiokątna GT-Y osobno | kwadratowa GT-X — **D** [6][12]; Focus Attack pisze o GT-8X — sprzeczność **D** [7]; obrót wewnętrznego pierścienia o 45° daje 4 kierunki — **D** [14] | płytki ograniczające 2/4/8 — **D** [8][9] | 4/8 (bez 2) — **D** [10] |
| Mikroprzełączniki | wlutowane w płytkę TP-MA — **D** [3] | OMRON wlutowane w TP-MA — **D** [6][12] | OMRON wlutowane — **D** [8] | [DO WERYFIKACJI] |
| Złącze | 5-pin męskie, wymaga wiązki JLF-H — **D** [2] | 5-pin; w zestawie AE przewód z jednym końcem odizolowanym — **D** [6] | 5-pin — **D** [8] | 5-pin na płytce — **D** [10] |
| Sprężyna / siła | „light spring” — **D** [2]; zamienne sprężyny 2/4/6 lb — **D** [6][12] | jak obok | „soft spring” — **D** [8] | „soft spring” — **D** [10] |
| Kąt wychylenia | ±8,5° — **S** (marketplace) [15] [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] |
| Trwałość | brak danych w źródłach [DO WERYFIKACJI] | brak danych [DO WERYFIKACJI] | brak danych [DO WERYFIKACJI] | brak danych [DO WERYFIKACJI] |
| Gwint kuli | [DO WERYFIKACJI] | „M6” wg Focus Attack — **D** [7] [DO WERYFIKACJI] | [DO WERYFIKACJI] | [DO WERYFIKACJI] |

**Pinout złącza 5-pin JLF** (Paradise Arcade Shop, **D** [2]): 1 czarny — masa, 2 zielony — góra, 3 żółty — dół, 4 pomarańczowy — lewo, 5 czerwony — prawo. Arcade Express zastrzega, że kolory przewodów zmieniają się między partiami [16], więc przypisanie trzeba sprawdzić multimetrem na próbce, a w firmware MicroPython trzymać mapę pin → kierunek w konfiguracji, nie w kodzie.

**Złącze na płytce TP-MA:** sklepy opisują je jako „JST”, a jeden sklep sprzedaje wtyk 5-pin „pitch JST” do wlutowania [17]; raster (2,5 mm JST XH czy 2,54 mm) nie jest nigdzie podany — **[DO WERYFIKACJI z wtykiem JLF-H przed zaprojektowaniem gniazda na własnej płytce]**.

### 2.2. Różnice JLX2 wobec JLF (wg sklepów)

Focus Attack i Paradise opisują te same zmiany: podstawa z POM zamiast nylonu, łożysko z nylonu zamiast POM, płytka mikroprzełączników z CEM-3 zamiast papieru fenolowego, nowa podkładka w kształcie X [7][12]. Sklepy różnią się co do aktuatora (biały P-W vs czarny P-5 15,8 mm) i bramki (GT-X vs GT-8X) [7][12][14]. Focus Attack ostrzega, że część elementów JLX2 nie jest zamienna z JLF (baza JLX-P-2, łożysko JLX-P-4, podkładka JLX2-MW), a płytka XTP-MA i bramka są zgodne [7]. Wniosek: przy zakupie próbek kupić od razu komplet części zamiennych tej samej generacji.

### 2.3. Wersje ciche (ważne w studiu)

| Model | Co wiadomo | Cena sklepu (18.10.2026) |
|---|---|---|
| Sanwa JLX2-TPML-8YT-SK | przełączniki listkowe Sanwa MLS-57AU, „mostly silent”, 5-stopniowa regulacja punktu zadziałania dla każdego kierunku, brak danych w dB — **D** [18] | 47,95 USD, 1 szt. (Focus Attack) [18]; 48,29 € (Arcade Express, strona kategorii, stan magazynu nieznany) [19]; 48,95 USD (Paradise, wyciąg wyszukiwarki — **S**) |
| Sanwa JLF-TPRG-8BYT-SK | wersja cicha „wysoka sprężystość” z kontaktronami (reed) — **S** | 10 230 JPY, brak (Tsukumo, wyciąg wyszukiwarki — **S**) [DO WERYFIKACJI] |

### 2.4. Uwagi projektowe do joysticka pilota

- Pilot nie jest kontrolerem do bijatyk, tylko do nawigacji w menu. Bramka kwadratowa w trybie 8 kierunków sprzyja przypadkowym skosom. Warto zacząć od trybu 4-kierunkowego (obrót pierścienia restryktora) albo od filtra skosów w firmware i ocenić to na makiecie.
- Gdy blat wyjdzie grubszy niż przewiduje Sanwa, kula siedzi niżej. Sklepy oferują krótszy trzon (60 mm, o 8 mm krótszy od standardowego; 7,11 € w Arcade Express, 2 szt.) [20] i trzon przedłużony (Focus Attack) [3] — dobór dopiero po pomiarze na makiecie.

---

## 3. Przyciski

### 3.1. Przyciski 30 mm i 24 mm Sanwa i Seimitsu

| Model | Montaż | Otwór | Panel (zakres) | Mikroprzełącznik / terminal | Cena sklepu (18.10.2026) |
|---|---|---|---|---|---|
| Sanwa OBSF-30 | zatrzask (2 zaczepy) | 30 mm — **D** [21][22] | do 3,7 mm — **D** [21]; ok. 2–4 mm — **D** [22][23] | SW-68; 2,8 mm (.110″), styki złocone — **D** [21][22][23] | 2,69 €, 41 szt. (Arcade Express) [21]; 3,25 USD (Paradise) [22]; 2,25 £ (The Pi Hut) [23] |
| Sanwa OBSC-30 (przezroczysty) | zatrzask | 30 mm — **D** [24][25] | do 3,7 mm — **D** [24]; 2–4 mm — **D** [25] | SW-68; 2,8 mm — **D** [24] | 4,37 €, 31 szt. (AE) [24]; 4,75 USD (Paradise) [25] |
| Sanwa OBSFE-30 (cichy) | zatrzask | 30 mm | [DO WERYFIKACJI] | elastomerowy popychacz; .110″ — **D** [26] | 3,50 USD (Paradise) [26] |
| Sanwa OBSF-40 | zatrzask | 40 mm — **D** [27] | ok. 2–4 mm — **D** [27] | SW-68; .110″ — **D** [27] | 5,95 USD, wyprzedany (Paradise) [27] |
| Sanwa OBSN-30 | wkręcany | 30 mm | do 8 mm — **D** [28] | SW-68; 2,8 mm — **D** [28] | 3,30 €, 26 szt. (AE) [28]; 3,25 USD, 42 szt. (Focus Attack) [29] |
| Sanwa OBSN-30RG | wkręcany | 30 mm | 0–13 mm; głębokość montażu 44 mm; nakrętka 36 mm — **D** [30] | kontaktron OMRON; 10–50 mln cykli — **D** [30] | wycofany z produkcji wg sklepu; 6,25 USD, wyprzedany [30] |
| Sanwa OBSF-24 | zatrzask | 24 mm | 2–3,9 mm — **S** (wyciąg z Arcade Renovations) [DO WERYFIKACJI] | SW-68 | 2,40–2,75 USD (Paradise, wyciąg — **S**) |
| Sanwa OBSC-24 (przezroczysty) | zatrzask | 24 mm — **D** [31] | do 3,7 mm — **D** [31] | SW-68; 2,8 mm — **D** [31] | 4,17 €, 69 szt. (AE) [31] |
| Sanwa OBSN-24 | wkręcany | 24 mm | do 8 mm — **S** (wyciąg z AE) [DO WERYFIKACJI] | 2,8 mm | 2,02 € (AE, wyciąg — **S**); 2,75 USD (Focus Attack, wyciąg — **S**) |
| Seimitsu PS-14-GN | wkręcany | 30 mm — **D** [32] | do 7 mm; długość 17 mm — **D** [32] | PS-14-G; 2,8 mm — **D** [32]; średnica całkowita 34,5 mm, głębokość montażu 32,5 mm — **D** [33] | 3,66 €, 50 szt. (AE) [32] |
| Seimitsu PS-14-KN (przezroczysty) | wkręcany | 30 mm | „ponad 1/4″” bez maksimum — **D** [34] [DO WERYFIKACJI] | MM9-4 (Tokai Tushinkizai), siła 100 ± 30 g, skok do zadziałania 2,5 ± 0,3 mm, drgania < 10 ms, ponad 2 000 000 cykli; .110″ — **D** [34] | 4,25 USD (Paradise) [34] |
| Seimitsu PS-14-DN | wkręcany | 24 mm — **D** [35] | do 7 mm; długość 14 mm — **D** [35] | PS-14-D; 2,8 mm; opis „bez słyszalnego kliku” — **D** [35] | 3,46 €, 17 szt. (AE) [35] |

**Mikroprzełącznik Sanwa SW-68** (dane z kart OBSF-30/OBSC-30/OBSF-40 w Paradise, **D** [22][25][27]): położenie zadziałania 0,85 mm; skok całkowity 2,53 mm; siła zadziałania 55 g; siła skoku całkowitego 81 g; obciążalność DC 12 V, 100 mA; rezystancja styku ≤ 50 mΩ; izolacja 50 MΩ przy DC 250 V; temperatura pracy −20…+60 °C; trwałość 1 mln cykli przy 5 V DC, 10 mA. Paradise zaznacza przy OBSF-40, że dłuższy skok może zostawić przycisk w stanie „wciśnięty”, jeśli nie zostanie dociśnięty do końca [27].

**Wniosek dla elektroniki:** SW-68 jest wyspecyfikowany przy małym prądzie (10 mA), a styki są złocone [23], co pasuje do wejść GPIO 3,3 V ESP32-S3 z rezystorem podciągającym. Seimitsu MM9 wymaga mniej więcej dwa razy większej siły (100 g wobec 55 g), co może być zaletą dla przycisków o skutkach trudnych do cofnięcia (RECORD, STOP), bo utrudnia przypadkowe wciśnięcie; mieszanie dwóch charakterystyk na jednym blacie trzeba jednak ocenić ręką na makiecie.

### 3.2. Terminale 2,8 mm i 4,8 mm

- Przyciski japońskie (Sanwa, Seimitsu) mają terminale 2,8 mm (.110″) — **D** [21][22][32].
- Przyciski w standardzie amerykańsko-europejskim mają 4,8 mm (.187″): Industrias Lorenzo z mikroprzełącznikiem Cherry D44X 4,8 mm (6,3 mm na życzenie) — **D** [36]; Ultimarc Ultralux — 4,8 mm dla przełącznika i 6,3 mm dla oprawki LED — **P** [37].
- Konektory żeńskie Faston .110 mają w katalogach dwie grubości wsuwki: 2,8 × 0,5 mm (RS, przekrój 0,5–1 mm²) [38] i 0,81 mm (TE 881607-1 u Heilind) [39]. **Grubość terminala SW-68 trzeba zmierzyć na próbce** przed zamówieniem konektorów, inaczej połączenie będzie luźne albo za ciasne.

### 3.3. Przyciski podświetlane

| Model | Rozmiar / montaż | Zasilanie LED | Uwagi | Cena (18.10.2026) |
|---|---|---|---|---|
| Seimitsu PSL-30N | 30 mm, wkręcany; średnica całkowita 34,5 mm, głębokość 32,5 mm — **D** [40] | wbudowana LED 5 V DC — **D** [40] | mikroprzełącznik MM9-PSU-5V; wymaga osobnej wiązki PSL-H — **D** [40][41] | 9,25 USD, wyprzedany [40]; sam przełącznik PSL-30N-5V 7,25 USD [41] |
| Ultimarc Ultralux | otwór 28–30 mm; ramka 3,8 mm nad panelem — **P** [37] | LED 5 V; wersja RGB z wiązką 500 mm — **P** [37] | terminale 4,8 mm / 6,3 mm — **P** [37] | 3,95 USD, RGB 6,70 USD [37] |
| Industrias Lorenzo PSL-H RGB (sprzedawany też jako Ultimarc Classic RGB) | 28 mm, długość 62 mm — **D** [36] | RGB, 4 piny, przewód 500 mm; sklep pisze „5 V lub 12 V” — **D** [36]; inny sklep zaleca wyłącznie 5 V — **S** | Cherry D44X 4,8 mm — **D** [36] | 10,16 €, 40 szt. (AE) [36] |
| Adafruit „Arcade Button with LED 30 mm” (tylko prototyp, nie część profesjonalna) | ok. 30 mm, wkręcany, panel do ok. 20 mm — **P** [42] | 5 V przy 10 mA, dwie LED szeregowo z rezystorem 200 Ω; czerwony i żółty nie działają przy 3,3 V — **P** [42] | — | 2,50 USD [42] |
| Sanwa OBSC-30 + płytka LED Focus Attack „FA 30mm Button RGB LED” | zgodna tylko z obudową OBSF/OBSC i bazą SW-68, nie z OBSC-24 — **S** (wyciąg) | adresowalne RGB — **S** | strona produktu zwróciła 404 | [DO WERYFIKACJI] |

**Wniosek dla elektroniki:** wszystkie potwierdzone LED-y pracują na 5 V. ESP32-S3 ma wyjścia 3,3 V, więc diody trzeba kluczować tranzystorem (np. N-MOSFET po stronie masy) z szyny 5 V. Zasilanie pochodzi z USB-C, więc łączny prąd LED trzeba wliczyć do budżetu prądowego toru R3.

### 3.4. „Przezroczyste na kolorowe” — jak zrobić przyciski z grafiką

1. **Kolor z korpusu, ikona z wkładki (zalecane):** Sanwa OBSC-30 w kolorach przezroczystych (czerwony, żółty, niebieski, zielony) [24]; po zdjęciu popychacza wyjmuje się białą wkładkę i wkłada własną [25]. Arcade Express podaje średnicę grafiki **20,7 mm** dla OBSC-30 [24] — i tę samą liczbę dla OBSC-24 [31], co przy przycisku 24 mm jest podejrzane: **[DO WERYFIKACJI pomiarem]**. Ikona jest wtedy pod przezroczystym kapturkiem i nie ściera się od palca.
2. **Korpus bezbarwny, kolor i ikona z wydruku:** OBSC-30 „crystal clear” (Paradise) z wkładką wydrukowaną w pełnym kolorze — pełna kontrola nad barwą zgodną z identyfikacją Radia Wnet.
3. **Naklejka na wierzch popychacza (obecny plan `naklejki.py`):** bezbarwna folia z białym nadrukiem na kolorowym przycisku OBSF-30. Najtańsze, ale ikona jest pod palcem i będzie się ścierać. Generator przyjmuje dziś średnicę naklejki 0,75 × średnica przycisku (22,5 mm dla 30 mm) — wymiaru płaskiej części popychacza nie znalazłem w źródłach **[DO WERYFIKACJI pomiarem]**.
4. **Wersja wkręcana do drewna:** Seimitsu PS-14-KN (przezroczysty korpus, kolorowy popychacz) [34] i PSL-30N z LED [40]. Czy da się w nich umieścić wkładkę — źródła milczą **[DO WERYFIKACJI]**.

---

## 4. Obudowa drewniana

### 4.1. Materiały i grubości

- **Sklejka brzozowa:** UPM WISA podaje grubości standardowe 6,5 / 9 / 12 / 15 / 18 / 21 / 24 / 27 / 30 / 35 / 40 / 45 / 50 mm (nominalne) i gęstość ok. 680 kg/m³ (±50 kg) — **P** [43]. **Uwaga:** `arcade.toml` przewiduje dno 6,0 mm, a w tej serii najcieńsza jest 6,5 mm; inne grubości (np. 6 mm, 3 mm) trzeba sprawdzić u konkretnego dostawcy płyt **[DO WERYFIKACJI]**.
- **MDF:** zestaw bartop Arcade Express jest z MDF 16 mm pokrytego melaminą, z rowkiem na listwę T-molding 16 mm; wersja z panelem metalowym ma panel ze stali węglowej 1,5 mm malowanej proszkowo; zestaw pleksi ma 3 mm — wszystko z wyciągu wyszukiwarki, bo strona produktu przekierowała na kategorię — **S** [44] [DO WERYFIKACJI]. Listwy U-molding w tym sklepie: 16 mm za 1,88 €, 19 mm za 1,98 € (jednostka sprzedaży niepodana) [44].
- **Pleksi (PMMA)** chroni grafikę; grafika leży pod pleksi. Grubość wpływa bezpośrednio na zgodność z zatrzaskami (sekcja 4.2).

Zalecenie materiałowe: na boki, przód i tył sklejka brzozowa 12 lub 15 mm (sztywna, dobrze trzyma wkręty i wkładki gwintowane, krawędź warstwowa wygląda dobrze pod lakierem). MDF jest tańszy i łatwiej się frezuje, ale słabiej trzyma gwinty i źle znosi wilgoć; do pilota w studiu sklejka jest lepsza.

### 4.2. Kluczowy problem: grubość blatu a sposób montażu przycisków

| Stos blatu | Suma | OBSF/OBSC (zatrzask, ≤ 3,7 mm [21] / 2–4 mm [22]) | OBSN (≤ 8 mm [28]) | PS-14-GN/DN (≤ 7 mm [32][35]) | JLF (≤ 5 mm — **F**) |
|---|---|---|---|---|---|
| obecny `arcade.toml`: pleksi 3 + grafika 0,3 + płyta 3 | 6,3 mm | **nie** | tak | tak | prawdopodobnie za grubo [DO WERYFIKACJI] |
| W1a: pleksi 2 + folia 0,1 + stal/aluminium 1,5 | 3,6 mm | na granicy — ryzyko tolerancji pleksi | tak | tak | tak |
| W1b: pleksi 1,5 + folia 0,1 + stal/aluminium 1,5 | 3,1 mm | tak, z zapasem | tak | tak | tak |
| W2: pleksi 2 + folia 0,1 + drewno 3 (pozostawione po frezowaniu kieszeni od spodu) | 5,1 mm | **nie** | tak | tak | na granicy |
| W2 bez pleksi: laminowana grafika na drewnie 3 mm | ok. 3,2 mm | tak | tak | tak | tak |

Liczby w kolumnie „suma” to moje obliczenie z założonych grubości warstw, nie dane producenta; zakresy paneli pochodzą z kart dystrybutorów podanych w nagłówkach.

### 4.3. Warianty montażu w drewnie 12–18 mm

**W1 — drewniana skrzynka, płyta nośna z metalu (zalecany).** Rama i dno ze sklejki 12–15 mm. W górnej krawędzi ramy frezuje się wpust na płytę stalową lub aluminiową 1,5 mm (cięcie laserowe, malowanie proszkowe) z otworami 30/24 mm, oknem na OLED i otworem na trzon joysticka. Na płycie leży folia z grafiką i pleksi 1,5–2 mm. Przyciski zatrzaskowe Sanwa (także ciche OBSFE-30 i przezroczyste OBSC-30) wchodzą w cały stos; joystick przykręca się płytką JLF-P1 od spodu płyty. Rozwiązanie odpowiada panelom metalowym, do których są projektowane przyciski zatrzaskowe (opisy „for metal control panels” [22][27]) i panelowi stalowemu 1,5 mm z zestawu bartop [44]. Drewno pozostaje widoczną obudową. Wymaga dodatkowego zlecenia blachy — można je dołączyć do zamówienia w chińskiej fabryce (tor R1 — **[DO WERYFIKACJI oferty]**).

**W2 — blat w całości z drewna 12–18 mm.**
- Otwory przelotowe 30 mm i 24 mm (dla wkręcanych średnica otworu równa średnicy gwintu — wg AE otwór 30 mm dla PS-14-GN [32]).
- Od spodu kieszenie wiertłem Forstnera lub frezarką CNC do pozostawienia 3 mm drewna. Średnica kieszeni co najmniej 40 mm, bo nakrętka przycisku 30 mm ma ok. 36 mm (OBSN-30RG: 36 mm — **D** [30]; slagcoin: 35–36 mm — **F**). Przy rozstawie środków 36,5–42 mm kieszenie się zachodzą, więc praktyczniej jest wyfrezować jedną wspólną kieszeń pod całe pole przycisków.
- Przyciski wkręcane: Sanwa OBSN-30/OBSN-24 albo Seimitsu PS-14-GN/KN/DN. Stos 3 mm drewna + 2 mm pleksi + folia mieści się w ich zakresach (≤ 7–8 mm). Kupujący w Focus Attack opisuje, że blat 0,75″ był za gruby i trzeba go było sfrezować do ok. 0,4″ — sygnał zgodny z powyższym (**F**) [29].
- Przyciski zatrzaskowe w W2 tylko bez pleksi nad nimi (grafika laminowana na drewnie, łączna grubość ≤ 3,7 mm).
- Joystick: (a) kieszeń od spodu o wymiarach płytki JLF-P1 (95 × 53 mm wg [5]; sprzeczne 94 × 40 mm wg [11] — **zmierzyć**) do pozostawienia ok. 3 mm drewna, płytka przykręcona wkrętami do drewna; (b) płytka JLF-P1-S (96 × 53 mm, stal nierdzewna, 6,30 €, 14 szt. — **D** [45]), którą sklep poleca do grubszych paneli drewnianych, a kupujący do paneli od 16 mm (**F**); (c) montaż od góry bez płytki, śruby z łbem stożkowym schowane pod pleksi (Arcade Renovations sprzedaje zestaw „hidden hardware” ze śrubami 1/2″ [14]). Wybór po makiecie, bo zmienia wysokość kuli nad blatem.

**W0 — makieta funkcjonalna bez frezowania.** Przyciski Adafruit 30 mm (panel do ok. 20 mm, **P** [42]) pozwalają zbudować szybką makietę ze sklejki 12–18 mm do testów ergonomii i firmware. Nie są to części profesjonalne i nie powinny trafić do wersji docelowej.

### 4.4. Dostęp serwisowy, nóżki, wykończenie

- Dostęp serwisowy: dno przykręcane do ramy na wkładkach gwintowanych M4 wkręcanych w sklejkę (zamiast wkrętów w drewno, które wyrabiają się przy wielokrotnym otwieraniu). Alternatywa: blat na zawiasie fortepianowym z tyłu i zamek lub magnesy z przodu — wygodne przy wymianie przycisków, ale wymaga luzu na kable przy otwieraniu. Konkretne typy wkładek i zawiasów **[DO WERYFIKACJI]**.
- Nóżki: gumowe lub silikonowe, przyklejane albo przykręcane; `arcade.toml` przewiduje Ø 20 × 4 mm — to wartość robocza, bez źródła.
- Krawędzie: listwa T-molding wymaga rowka frezem tarczowym; przy sklejce brzozowej można ją pominąć i zostawić lakierowaną krawędź warstw.
- Przewody: dla przycisków z terminalami 2,8 mm — wiązka masy na 22 konektory (3,56 €, 56 szt.) i wiązki sygnałowe 2 × 4 z wtykami Dupont, 50 cm (3,04 €, 173 szt.) w Arcade Express [46][47]; dla joysticka wiązka JLF-H, 50 cm, wtyk JST (2,02 €, 10 szt.) [16]. Wtyki Dupont pasują do listwy goldpin na własnej płytce, ale ich rastra sklep nie podaje **[DO WERYFIKACJI]**.

### 4.5. Układy rozmieszczenia i odstępy

Producenci automatów (Taito Vewlix, Namco Noir, Sega Astro City) nie publikują w sieci rysunków wymiarowych paneli. Wszystkie liczby poniżej pochodzą z serwisu społecznościowego slagcoin.com (**F**, sygnał) [48] i wymagają wydruku 1:1 na makiecie:

- przyciski 30 mm: wierzch 33–34 mm, nakrętki 35–36 mm, minimalny rozstaw środków 35–36 mm, typowy 36–36,5 mm;
- przyciski 24 mm: minimalny rozstaw ok. 29 mm;
- odstęp między rzędami: ok. 36 mm lub 39 mm;
- odległość środka joysticka od środka najbliższego przycisku: ok. 5,9 / 6,3 / 9,5 cm; joystick ok. 9,5–10 mm poniżej przycisku palca wskazującego górnego rzędu;
- wielu graczy woli układ obrócony ok. 10° zgodnie z ruchem wskazówek zegara;
- Sega (Astro City, Blast City): układ „standardowy japoński”, łukowy; Vewlix: ostatnie kolumny przesunięte w górę, dolne przyciski palca wskazującego i środkowego bliżej niż 36 mm;
- Noir: według recenzji TechRadar przyciski rozstawione nieco szerzej niż w Vewlix (**F**) [49].

**Odniesienie do obecnego układu w `arcade.toml`:** cztery przyciski kolorowe stoją w siatce 2 × 2 o rozstawie 42 mm w obu osiach, czyli powyżej typowych 36–36,5 mm, i nakrętki 36 mm się nie zderzą. Joystick (u = −92) jest 122 mm od najbliższej kolumny przycisków (u = 30) — więcej niż w układach do gier, co dla pilota z osobnymi funkcjami jest akceptowalne, ale warto sprawdzić na makiecie, czy dłoń nie musi „przeskakiwać”. STOP jest ok. 71 mm od PLAY (obliczone z `arcade.toml`), co ogranicza przypadkowe wciśnięcia.

---

## 5. Gdzie kupić (stan 18.10.2026)

Nie znalazłem listy autoryzowanych dystrybutorów publikowanej przez Sanwa Denshi ani Seimitsu. Określenia „Official Sanwa Product direct from Japan” (The Pi Hut, Core Electronics) są deklaracjami sprzedawców [23][50].

| Sklep | Kraj | Co ma (przykłady) | Uwagi |
|---|---|---|---|
| Arcade Express | Hiszpania (UE), Granada | Sanwa JLF/JLX2/TPML, OBSF/OBSC/OBSN, Seimitsu LS-32/LS-40, PS-14, Industrias Lorenzo, wiązki | ceny z VAT; JLF i JLX2 bez stanu, LS-32-01 45 szt. [1][6][8]; koszt wysyłki do Polski [DO WERYFIKACJI] |
| The Pi Hut | Wielka Brytania (poza UE) | JLF-TP-8YT + LB-35 26,50 £ (14 szt.), OBSF-30 2,25 £, OBSF-24 2,50 £, JLF-H 5,50 £ [5][23][51] | po Brexicie możliwe cło/VAT importowy i opłaty kuriera [DO WERYFIKACJI] |
| Paradise Arcade Shop | USA | pełna gama Sanwa/Seimitsu, dane SW-68 | wiele pozycji „sold out” [2][22]; cło i VAT przy imporcie [DO WERYFIKACJI] |
| Focus Attack | USA | JLX2-TP-8YT 26,95 USD, JLX2-TPML 47,95 USD (1 szt.), OBSN-30 3,25 USD (42 szt.) [7][18][29] | jak wyżej |
| Arcade Renovations | USA | JLX2-TP-8YT 27,95 USD, 108 szt. [14] | jak wyżej |
| Ultimarc | Wielka Brytania (producent) | Ultralux 3,95 USD, RGB 6,70 USD [37] | producent własnych przycisków (nie Sanwa) |
| pinballshop.nl | Holandia (UE) | wiązka masy Ultimarc 32 konektory 4,8/6,3 mm, 16,95 € (wyciąg — **S**) | [DO WERYFIKACJI] |
| Kiwi Electronics | Holandia (UE) | duże przyciski 60 mm z LED (do 12 V), 3,99 € netto / 4,91 € brutto, 18 szt. [52] | części ogólne, nie profesjonalne arcade |
| Tsukumo, Yodobashi | Japonia | Sanwa, Seimitsu (np. LS-32-01 3 828 JPY — **S**; przyciski Sanwa 398–660 JPY — **S**) | strony nie odpowiedziały; wysyłka za granicę [DO WERYFIKACJI] |
| Sprzedawcy z Hongkongu na eBay | Hongkong | zestawy Sanwa | deklaracje sprzedawców, brak weryfikacji autentyczności |

**Polska:** nie znalazłem polskiego sklepu z oryginalnymi częściami Sanwa lub Seimitsu (wyszukiwania po polsku, Botland, Kamami, Allegro bez trafień w wynikach). Oferty Allegro trzeba sprawdzać pojedynczo **[DO WERYFIKACJI]**.

**Podróbki:** fora i kupujący zalecają kupowanie u znanych sklepów specjalistycznych i porównywanie z oficjalnymi zdjęciami Sanwa (**F**). AliExpress i anonimowych sprzedawców na marketplace’ach należy traktować jako źródło niepewne.

**Orientacyjny koszt części (ceny sklepu Arcade Express z 18.10.2026, z VAT, bez wysyłki), wariant W2 z przyciskami wkręcanymi:** joystick JLX2-TP-8YT 26,42 € (gdy wróci do magazynu) [6] + 5 × OBSN-30 po 3,30 € = 16,50 € [28] + OBSN-24 ok. 2,02 € (**S**) + JLF-H 2,02 € [16] + wiązka masy 3,56 € [46] + wiązki sygnałowe 3,04 € [47] ≈ 53,6 € plus kula LB-35 [cena w AE — DO WERYFIKACJI]. Suma jest moim obliczeniem z cen sklepu.

---

## 6. Uwagi o hałasie, trwałości i bezpieczeństwie użycia

- Ciche wersje (OBSFE-30, JLX2-TPML-8YT-SK) nie mają w źródłach danych w dB. Trzeba nagrać próbkę przy mikrofonie studyjnym w odległości typowej dla stanowiska i porównać z OBSF-30/JLX2-TP-8YT.
- Trwałość: SW-68 — 1 mln cykli przy 5 V/10 mA [22]; Seimitsu MM9-4 — ponad 2 mln cykli [34]; kontaktrony OBSN-30RG — 10–50 mln, ale model wycofany [30]. Dla pilota w codziennym użyciu wszystkie wystarczą; trwałość joysticków nie jest podana nigdzie.
- RECORD i STOP mają skutki trudne do cofnięcia na antenie. Poza odstępem na blacie warto rozważyć cięższy przełącznik (Seimitsu, 100 g) lub podwyższony pierścień wokół STOP; to propozycja projektowa do sprawdzenia na makiecie.

---

## 7. Zalecenie

### 7.1. Wybór części

| Funkcja | Wariant W1 (płyta metalowa, zatrzaski) — zalecany | Wariant W2 (pełne drewno, wkręcane) |
|---|---|---|
| Joystick | Sanwa JLX2-TP-8YT + kula Sanwa LB-35; opcjonalnie bramka ośmiokątna GTX-Y; do studia rozważyć Sanwa JLX2-TPML-8YT-SK (cichy) | to samo; alternatywa dostępna od ręki w UE: Seimitsu LS-32-01 (2/4/8 kierunków) — wtedy inna płytka montażowa |
| REC / PLAY / WYŚLIJ / SPRAWDŹ (30 mm) | Sanwa OBSC-30 przezroczysty czerwony / żółty / niebieski / zielony z wkładkami z ikonami; jeśli próba odsłuchowa wypadnie źle — OBSFE-30 (cichy) z naklejką | Sanwa OBSN-30 czerwony / żółty / niebieski / zielony albo Seimitsu PS-14-GN w tych kolorach; dla REC z podświetleniem Seimitsu PSL-30N (LED 5 V) + wiązka PSL-H |
| START (mały, 24 mm) | Sanwa OBSC-24 przezroczysty bezbarwny lub biały albo OBSF-24 | Sanwa OBSN-24 lub Seimitsu PS-14-DN |
| STOP (duży) | 30 mm: Sanwa OBSF-30 czarny (ten sam otwór i mikroprzełącznik); jeśli musi być większy — Sanwa OBSF-40 (40 mm, uwaga na dłuższy skok i dostępność) | 30 mm: Sanwa OBSN-30 czarny; większych przycisków wkręcanych z serii japońskich nie znalazłem |
| Wersja przezroczysta do grafiki | OBSC-30 / OBSC-24 + wkładka (Ø 20,7 mm wg AE, do pomiaru) | Seimitsu PS-14-KN / PSL-30N (możliwość wkładki do sprawdzenia) |

### 7.2. Sposób montażu (skrót)

- **W1:** rama i dno ze sklejki brzozowej 12–15 mm; płyta nośna stal/aluminium 1,5 mm wpuszczona we wpust ramy; folia z grafiką i pleksi 1,5–2 mm; przyciski zatrzaskowe przez cały stos (≤ 3,7 mm); joystick na JLF-P1 od spodu płyty, śruby M4 (AE poleca do JLF-P1 śruby M4 z łbem płaskim 15 mm [11]); dno na wkładkach gwintowanych M4.
- **W2:** blat ze sklejki 12–18 mm; kieszenie od spodu do pozostawienia 3 mm, Ø ≥ 40 mm lub wspólna kieszeń; przyciski wkręcane; joystick w kieszeni na JLF-P1, na JLF-P1-S albo montaż od góry.

### 7.3. Lista akcesoriów (do zamówienia razem z próbkami)

| Pozycja | Ilość | Uwagi |
|---|---|---|
| Wiązka joysticka Sanwa JLF-H (5-pin JST, 50 cm) | 1 + 1 zapas | [16] |
| Wtyk/gniazdo 5-pin do wlutowania w płytkę (pod JLF-H) | 2 | raster do pomiaru [17] |
| Płytka JLF-P1 (jest w zestawie JLX2) i JLF-P1-S | 1 + 1 | P1-S tylko w W2 [45] |
| Kula Sanwa LB-35 | 1 | 35 mm [5] |
| Bramka ośmiokątna GTX-Y | 1 | opcja, 4,95 USD w Arcade Renovations (wyciąg — **S**) |
| Krótszy trzon JLF/JLX (60 mm) | 1 | tylko gdy kula za wysoko [20] |
| Wiązka masy 2,8 mm (22 konektory) | 1 | [46] |
| Wiązki sygnałowe 2,8 mm → Dupont, 2 × 4, 50 cm | 1–2 | [47] |
| Konektory Faston żeńskie 2,8 mm z osłonką izolacyjną | 20 | grubość wsuwki do pomiaru [38][39] |
| Wiązka PSL-H (tylko przy PSL-30N) | 1 na przycisk | [40] |
| Śruby M4 × 15 mm z łbem płaskim + nakrętki | 4 | do JLF-P1 [11] |
| Wkładki gwintowane M4 do sklejki + śruby M4 do dna | 6–8 | [DO WERYFIKACJI typu] |
| Nóżki gumowe/silikonowe | 4 | wymiar roboczy z `arcade.toml` |
| Próbki „na zapas”: po 1 szt. OBSF-30, OBSC-30, OBSFE-30, OBSN-30, PS-14-GN | 5 | do pomiarów i próby odsłuchowej |

### 7.4. Kolejność działań

1. Kupić komplet próbek (joystick, po jednym przycisku każdego typu, płytki, wiązki) — decyzja i zakup po stronie człowieka.
2. Zmierzyć suwmiarką: rozstaw otworów i wymiary JLF-P1, wysokość joysticka nad i pod płytką, głębokość korpusów przycisków pod panelem, średnicę nakrętek, średnicę wkładek OBSC, grubość terminali SW-68, raster złącza TP-MA. Wyniki wpisać do `arcade.toml` w miejsce `[ROBOCZE]` z adnotacją „pomiar próbki, data”.
3. Zbudować makietę W0 lub W2 z blatu 12–18 mm i sprawdzić ergonomię oraz hałas przy mikrofonie.
4. Wybrać wariant W1 albo W2 i dopiero wtedy wygenerować arkusze cięcia.
5. Opcjonalnie poprosić dystrybutora (np. Arcade Express) o rysunki wymiarowe producenta — wysłanie zapytania wymaga zgody człowieka.

---

## 8. Proponowane zmiany w `projekt/arcade.toml` (niewprowadzone)

| Klucz | Obecnie | Propozycja | Uzasadnienie |
|---|---|---|---|
| `[blat] pleksi, grafika, plyta` | 3,0 + 0,3 + 3,0 = 6,3 mm | W1: 1,5–2,0 + 0,1 + 1,5 (metal) albo W2: przyciski wkręcane | zatrzaski ≤ 3,7 mm [21] / 2–4 mm [22] |
| `[blat] plyta` komentarz | „zakres grubości z karty Sanwa” | „zakres z kart dystrybutorów, nie Sanwa” | brak karty producenta (sekcja 1) |
| `[joystick] plytka_mont` | [53, 86] | [53, 95] × 1,6 mm `[ROBOCZE — pomiar]` | The Pi Hut: 95 × 53 × 1,6 mm [5]; 86 mm nie znalazłem w żadnym źródle |
| `[joystick] wys_nad` | 33 mm do środka kuli | `[ROBOCZE]` — trzon 32,5 mm sięga do spodu kuli [2], więc środek kuli będzie wyżej o promień kuli (17,5 mm) minus grubość blatu ponad płytką | do pomiaru |
| `[joystick] otwor`, `wys_pod` | 24 mm, 62 mm | bez zmian, ale oznaczyć `[DO WERYFIKACJI]` | brak źródła; AE podaje tylko wysokość całkowitą 69 mm [1] |
| `[przycisk_wspolne] glebokosc_pod` | 31 mm | minimum luzu pod blatem 45 mm `[ROBOCZE]` | PS-14: 32,5 mm [33]; OBSN-30RG: 44 mm [30]; OBSF-30: brak danych |
| `[obudowa] dno` | 6,0 mm | 6,5 mm (WISA) lub potwierdzić 6 mm u dostawcy | lista grubości WISA [43] |
| `naklejki.py` `naklejka_srednica` | 0,75 × średnica | dla wkładek OBSC: 20,7 mm `[ROBOCZE]` | AE [24] |

---

## 9. Zbiorcza lista [DO WERYFIKACJI]

1. Rozstaw otworów płytek JLF-P1, JLF-P1-S, Seimitsu SE/SS i ich rzeczywiste wymiary (sprzeczność 95 × 53 mm [5] vs 94 × 40 mm [11]).
2. Maksymalna grubość panelu dla JLF/JLX2 (sygnał „5 mm” bez dostępnego źródła).
3. Wysokość joysticka nad i pod panelem, kąt wychylenia (±8,5° tylko z marketplace), gwint kuli (M6 wg Focus Attack).
4. Raster złącza TP-MA i wtyku JLF-H.
5. Głębokość korpusu OBSF-30/OBSC-30 pod panelem, średnica części zatrzaskowej, płaska część popychacza pod naklejkę.
6. Średnica wkładki OBSC-24 (AE podaje 20,7 mm, jak dla OBSC-30).
7. Maksymalna grubość panelu dla PS-14-KN, OBSN-24 i OBSF-24 (tylko wyciągi wyszukiwarki).
8. Grubość terminala SW-68 (0,5 czy 0,8 mm) i dobór konektorów Faston.
9. Poziom hałasu OBSFE-30 i JLX2-TPML-8YT-SK w warunkach studia.
10. Dostępność JLX2-TP-8YT w UE; koszty wysyłki z ES; cło i VAT importowy z UK i USA.
11. Polscy sprzedawcy oryginalnych części Sanwa/Seimitsu.
12. Oferta chińskiej fabryki na cięcie i malowanie płyty stalowej 1,5 mm (tor R1).
13. Typy wkładek gwintowanych, zawiasów i nóżek.
14. Wymiary płytki JLF-P1 podaje tylko The Pi Hut [5]; Focus Attack sprzedaje ją za 5,95 USD bez wymiarów [4], a Arcade Express podaje inne wymiary [11].

---

## 10. Źródła (wszystkie sprawdzone 18.10.2026)

1. Arcade Express — Sanwa JLF-TP-8YT: https://www.arcadexpress.com/en/joysticks/9-424-sanwa-jlf-tp-8yt-arcade-joystick.html
2. Paradise Arcade Shop — Sanwa JLF-TP-8YT: https://paradisearcadeshop.com/products/sanwa-jlf-tp-8yt-joystick
3. Focus Attack — Sanwa JLF-TP-8YT: https://focusattack.com/sanwa-jlf-tp-8yt-joystick-precursor-to-jlx-tp-8yt/
4. Focus Attack — płytka JLF-P1 (5,95 USD, masa 1,90 oz, wymiarów strona nie podaje): https://focusattack.com/jlf-p1-mounting-plate
5. The Pi Hut — Sanwa JLF-TP-8YT/LB-35: https://thepihut.com/products/official-sanwa-8-way-arcade-joystick-jlf-tp-8yt
6. Arcade Express — Sanwa JLX2-TP-8YT: https://arcadexpress.com/en/joysticks/900-13160-arcade-joystick-sanwa-jlx-tp-8y.html
7. Focus Attack — Sanwa JLX2-TP-8YT: https://focusattack.com/sanwa-jlx2-tp-8yt-joystick-successor-to-sanwa-jlx/
8. Arcade Express — Seimitsu LS-32-01 SE: https://www.arcadexpress.com/en/joysticks/454-1683-seimitsu-ls-32-01-se-arcade-joystick.html
9. Paradise Arcade Shop — Seimitsu LS-32-01: https://paradisearcadeshop.com/products/seimitsu-ls-32-01-joystick
10. Arcade Express — Seimitsu LS-40-01: https://www.arcadexpress.com/joysticks-arcade/253-496-joystick-seimitsu-ls-40-01.html
11. Arcade Express — Sanwa JLF-P1: https://www.arcadexpress.com/en/joysticks-accesories/853-sanwa-jlf-p1-mounting-plate.html
12. Paradise Arcade Shop — Sanwa JLX2-TP-8YT: https://paradisearcadeshop.com/products/sanwa-jlx2-tp-8yt-joystick
13. Arcade Express — płytka Seimitsu SE LS-32/38/40 (wyciąg wyszukiwarki): https://www.arcadexpress.com/en/joysticks-accesories/851-seimitsu-se-ls-32-38-40-mounting-plate.html
14. Arcade Renovations — Sanwa JLX2-TP-8YT: https://www.arcaderenovations.com/sanwa-8-way-joystick-jlx2-tp-8yt.html
15. IBSPOT (marketplace) — JLF-TP-8YT-SK-R: https://ibspot.com/products/sanwa-denshi-jlf-tp-8yt-sk-r-electronic-board-joystick-lever-controller-red
16. Arcade Express — wiązka Sanwa JLF-H: https://www.arcadexpress.com/en/cables-wires/1293-5-pin-sanwa-jlf-h-cable-for-joystick.html
17. Arcade Express — złącze 5-pin do JLF/JLX (wyciąg wyszukiwarki): https://www.arcadexpress.com/en/electronics-power-supplies/1200-conector-pitch-sanwa-de-5-pines-joystick-sanwa-jlf-jlx.html
18. Focus Attack — Sanwa JLX2-TPML-8YT-SK: https://focusattack.com/sanwa-jlx2-tpml-8yt-sk-adjustable-silent-leaf-microswitch-joystick/
19. Arcade Express — lista joysticków Sanwa (strona kategorii): https://www.arcadexpress.com/en/joysticks/387-1220-nsadkfljasndkfjasndkfl.html
20. Arcade Express — krótszy trzon JLF/JLX: https://www.arcadexpress.com/en/joysticks-accesories/943-short-shaft-joystick-sanwa-jlf-jlx-8mm.html
21. Arcade Express — Sanwa OBSF-30: https://www.arcadexpress.com/en/arcade-pushbuttons/104-sanwa-obsf-30-japanese-arcade-button.html
22. Paradise Arcade Shop — Sanwa OBSF-30 czerwony: https://paradisearcadeshop.com/products/sanwa-obsf-30-snap-in-button-red
23. The Pi Hut — Sanwa OBSF-30: https://thepihut.com/products/official-sanwa-arcade-button
24. Arcade Express — Sanwa OBSC-30: https://www.arcadexpress.com/en/buttons/373-1157-sanwa-obsc-30-translucent-japanese-arcade-button-30mm.html
25. Paradise Arcade Shop — Sanwa OBSC-30 przezroczysty czerwony: https://paradisearcadeshop.com/products/sanwa-obsc-30-snap-in-button-clear-red
26. Paradise Arcade Shop — Sanwa OBSFE-30: https://paradisearcadeshop.com/collections/joystick-ball-tops-bat-tops/products/sanwa-obsfe-30-snap-in-silent-button-black
27. Paradise Arcade Shop — Sanwa OBSF-40: https://paradisearcadeshop.com/products/sanwa-obsf-40-snap-in-button-red
28. Arcade Express — Sanwa OBSN-30: https://www.arcadexpress.com/en/arcade-pushbuttons/303-sanwa-obsn-30-screw-in-japanese-arcade-button.html
29. Focus Attack — Sanwa OBSN-30 biały: https://focusattack.com/sanwa-obsn-30mm-screw-button-white
30. Paradise Arcade Shop — Sanwa OBSN-30RG: https://paradisearcadeshop.com/products/sanwa-obsn-30rg-screw-in-button-red
31. Arcade Express — Sanwa OBSC-24: https://www.arcadexpress.com/en/arcade-pushbuttons/372-sanwa-obsc-24-translucent-japanese-arcade-button-24mm.html
32. Arcade Express — Seimitsu PS-14-GN: https://arcadexpress.com/en/arcade-pushbuttons/671-seimitsu-ps-14-gn-screw-in-japanese-arcade-push-button-30mm.html
33. Paradise Arcade Shop — Seimitsu PS-14-GN (wyciąg wyszukiwarki z wymiarami 34,5 / 32,5 mm): https://paradisearcadeshop.com/products/seimitsu-ps-14-gn-30-mm-screw-in-button-pink
34. Paradise Arcade Shop — Seimitsu PS-14-KN przezroczysty czerwony: https://paradisearcadeshop.com/collections/joystick-ball-tops-bat-tops/products/seimitsu-ps-14-kn-30-mm-screw-in-button-clear-red
35. Arcade Express — Seimitsu PS-14-DN: https://arcadexpress.com/en/arcade-pushbuttons/670-seimitsu-ps-14-dn-screw-in-japanese-arcade-push-button-24mm.html
36. Arcade Express — Industrias Lorenzo PSL-H RGB: https://www.arcadexpress.com/en/arcade-pushbuttons/421-boton-il-concavo-.html
37. Ultimarc (producent) — Ultralux Chrome Illuminated Pushbuttons: https://ultimarc.com/arcade/buttons/ultralux-chrome-illuminated-pushbuttons
38. RS Components — TE FASTON .110, 2,8 × 0,5 mm: https://uk.rs-online.com/web/p/spade-connectors/6805729
39. Heilind — TE 881607-1: https://www.heilind.com/amp881607-1.html
40. Paradise Arcade Shop — Seimitsu PSL-30N przezroczysty czerwony: https://paradisearcadeshop.com/collections/joystick-ball-tops-bat-tops/products/seimitsu-psl-30n-30-mm-screw-in-button-clear-red
41. Paradise Arcade Shop — Seimitsu PSL-30N-5V (mikroprzełącznik z LED): https://paradisearcadeshop.com/collections/joystick-ball-tops-bat-tops/products/seimitsu-psl-30n-5v-switch
42. Adafruit (producent) — Arcade Button with LED 30 mm, nr 3489: https://www.adafruit.com/product/3489
43. UPM WISA (producent) — Sizes, thicknesses and weights: https://wisaplywood.com/specifying-wisa/sizes-thicknesses-and-weights
44. Arcade Express — Bartop XL (wyciąg wyszukiwarki; strona przekierowała na kategorię): https://www.arcadexpress.com/en/bartop-maquina-arcade/1166-bartop-xl-kit-de-maderas-con-panel-metalico.html oraz https://www.arcadexpress.com/en/bartop-maquina-arcade/1167-bartop-xl-wooden-kit-with-wooden-cpo-for-21-monitor.html
45. Arcade Express — Sanwa JLF-P1-S: https://arcadexpress.com/en/joysticks-accesories/852-sanwa-jlf-p1-s-mounting-plate.html
46. Arcade Express — wiązka masy 22 konektory: https://www.arcadexpress.com/en/cables-wires/200-ground-22-buttons-28mm-48mm-63mm-dupont.html
47. Arcade Express — wiązki sygnałowe 2 × 4 Dupont: https://www.arcadexpress.com/en/cables-wires/201-2-x-arcade-wiring-action-8-buttons-284863mm-dupont.html
48. slagcoin.com — Button Layouts (serwis społecznościowy, sygnał): https://www.slagcoin.com/joystick/layout.html
49. TechRadar — recenzja Hori Fighting Stick Alpha (sygnał): https://www.techradar.com/gaming/hori-fighting-stick-alpha-review
50. Core Electronics — Sanwa OBSF-30: https://core-electronics.com.au/sanwa-round-30mm-snap-in-arcade-button-red.html
51. The Pi Hut — Sanwa OBSF-24TR: https://www.thepihut.com/products/official-sanwa-triangle-snap-in-arcade-button-obsf-24tr
52. Kiwi Electronics — przycisk 60 mm z LED: https://www.kiwi-electronics.com/en/switches-buttons-115/arcade-buttons-307/large-arcade-button-with-led-60mm-red-1563

Strony sprawdzone bez użytecznej treści: `http://www.seimitsu.jp/` (pusta), `https://www.sanwa-denshi.co.jp/` (Sanwa RC), `https://www.sanwadenshi.com/` (inna firma), `https://www.sanwadenshi.jp/` (HTTP 403), `https://akihabarashop.jp/` (niezwiązana treść), `https://www.arcadewinkel.nl/…` (błąd certyfikatu), `shop.tsukumo.co.jp` i `yodobashi.com` (brak odpowiedzi), `monotaro.com` (HTTP 403).
