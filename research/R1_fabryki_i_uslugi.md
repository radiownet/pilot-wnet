---
tytul: "R1 — Fabryki i usługi: chińskie drukarnie elektroniki dla Pilota Wnet"
projekt: "Pilot Wnet (wersja arcade, obudowa drewniana)"
tor: "R1 fabryki"
data_sprawdzenia: "2026-10-18"
autor: "opracowanie SI (Claude), do weryfikacji przez człowieka"
status: "research — nic nie zamówiono, nie założono kont, nie użyto kalkulatorów wycen"
---

# R1 — Fabryki i usługi (stan na 18.10.2026)

> **Etykieta:** dokument przygotowany przez agenta SI (Claude) na podstawie stron producentów sprawdzonych 18.10.2026. Wszystkie kwoty są w USD, bez wysyłki i bez VAT, chyba że napisano inaczej. Przy każdej liczbie jest przypis z adresem strony. Tam, gdzie strona producenta nie podaje liczby wprost, wpisano **[DO WERYFIKACJI]**.
>
> **Ograniczenie metody:** zgodnie z zadaniem nie wypełniano formularzy, więc nie korzystano z kalkulatorów wycen (instant quote) żadnej fabryki. Ceny „z kalkulatora” (np. cena 4 warstw dla dokładnych parametrów, koszt wysyłki do Polski) trzeba sprawdzić ręcznie, wgrywając te same pliki Gerber/BOM/CPL do każdej fabryki.

---

## 0. Streszczenie

**Rekomendacja: JLCPCB** (razem z JLC3DP, JLCCNC i magazynem części JLCPCB/LCSC).

Najważniejsze liczby:

- **Powierzchnia za dolara w promocji:** JLCPCB daje 5 płytek 100×100 mm za 2,00 USD, czyli **250 cm²/USD**, i według własnej strony reklamowej dotyczy to warstw 1–4[^jlc-ads][^jlc-proto]. Druga wśród ofert z potwierdzoną liczbą sztuk jest PCBWay: 10 płytek 2-warstwowych 100×100 mm za 5,00 USD, czyli **200 cm²/USD**[^pw-home], ale dla 4 warstw PCBWay podaje 48,00 USD za płytkę 100×100 mm bez wskazania liczby sztuk[^pw-4l], co daje najwyżej około 21 cm²/USD.
- **Jawny cennik montażu:** tylko JLCPCB publikuje pełną tabelę opłat (uruchomienie, szablon, punkt lutowniczy, ładowanie podajników, RTG, lutowanie ręczne)[^jlc-pcba-price]. Pozostałe fabryki podają wyłącznie promocje albo odsyłają do kalkulatora.
- **Części do projektu są w katalogu JLCPCB:** ESP32-S3-WROOM-1-N16R8 (C2913202)[^jlc-esp], WIZnet W5500 (C32843)[^jlc-w5500], moduł LoRa 868 MHz Seeed (C5129913)[^jlc-lora-seeed], złącza JST XH (C157991)[^jlc-jst] i zaciski płaskie 4,8 mm do PCB (Keystone 1212, C3217931)[^jlc-faston].
- **Szacunek montażu 5 płytek u JLCPCB** (montaż standardowy jednostronny, 30 unikalnych części, 350 punktów SMT i 60 punktów THT na płytkę — założenia przykładowe): **około 99,69 USD opłat montażowych** plus części, płytka i wysyłka (wyliczenie w rozdz. 2.2).

Najważniejsze zastrzeżenia:

1. Od 22.08.2026 cena 2 USD jest dostępna **wyłącznie w aplikacji desktopowej JLCONE**, a nie na stronie WWW[^jlcone-news][^jlcone-faq]. Instalacja aplikacji to decyzja zespołu projektu (agent niczego nie instalował).
2. Strony JLCPCB nie są zgodne co do 4 warstw: strona reklamowa podaje „1–4 Layers · 5 pcs · 100×100 mm from $2.00”[^jlc-ads][^jlc-proto], inna strona podaje „4-layer PCBs: $2 for 5 PCBs” bez rozmiaru[^jlc-cheap], a materiały osób trzecich mówią o 50×50 mm dla 4 warstw[^hackclub]. **[DO WERYFIKACJI w JLCONE]**.
3. Moduł ESP32-S3-WROOM-1 ma w JLCPCB status **„Standard Only” i wymaga RTG**[^jlc-esp][^jlc-esp16]. Całe zamówienie przechodzi wtedy na montaż standardowy, a on ma wyższe opłaty i wymaga listew technologicznych (edge rails), które mogą powiększyć płytkę ponad 100×100 mm i wypchnąć ją z promocji **[DO WERYFIKACJI]**.
4. Na pierwszy prototyp (Rev 0) **NextPCB i PCBWay mogą wyjść taniej** dzięki jednorazowym promocjom montażu (NextPCB: do 200 USD rabatu na SMT dla 1–10 szt.[^np-disc]; PCBWay: „$29 in total for 1-20pcs assembly” z darmową wysyłką[^pw-home]). Warunki tych promocji nie są opublikowane w całości, więc przed zamówieniem trzeba porównać trzy wyceny na tych samych plikach.
5. **ALLPCB odpada:** na stronie głównej wisi komunikat, że serwis „will temporarily suspend operations effective immediately” z powodu zmian w ładzie korporacyjnym[^ap-home].

---

## 1. Promocje płytek (bez montażu)

### 1.1. Zestawienie ofert

| Fabryka | 2 warstwy — oferta | 4 warstwy — oferta | Grubość / kolor w promocji | Czas produkcji | Kupony dla nowych |
|---|---|---|---|---|---|
| **JLCPCB** | 2,00 USD za 5 szt., 100×100 mm, warstwy 1–4[^jlc-ads][^jlc-proto]; „$2 for 5 PCBs, any color”[^jlc-cheap]. **Tylko w aplikacji JLCONE**[^jlcone-faq] | 2,00 USD za 5 szt. 100×100 mm wg strony reklamowej[^jlc-ads]; inna strona bez rozmiaru[^jlc-cheap] — **[DO WERYFIKACJI]** | Kolory: zielony, czerwony, żółty, niebieski, biały, czarny; inne niż zielony to „two more days”[^jlc-quote]. Grubości dla 2 i 4 warstw: 0,4–2,0 mm[^jlc-cap]; 0,6 mm tylko do 100×100 mm i nie dla 4 warstw[^jlc-quote]. Grubość objęta ceną 2 USD: **[DO WERYFIKACJI]** | 2 warstwy, 5 szt.: 24 h; 4 warstwy, 5 szt.: 2–5 dni (FR-4, 1,6 mm, 1 oz, HASL, zielona maska, do 100×100 mm)[^jlc-time] | Pakiet nowego klienta: PCB 6 USD (zamówienie > 2 USD bez wysyłki), SMT 10 USD (> 2 USD), CNC 20 USD, druk 3D 2×10 USD, wysyłka 10 USD (wysyłka > 15 USD)[^jlc-coupons]. W JLCONE: pakiet 104 USD i losowy rabat 1–20 USD na zamówienie[^jlcone-faq]. „Multiple coupons cannot be combined on a single order”[^jlcone-news] |
| **PCBWay** | 5,00 USD za 10 szt., 1–2 warstwy, 100×100 mm, link oferty ustawia 1,6 mm; czas 24 h[^pw-home] | 48,00 USD za „100x100mm 4 layers”, liczba sztuk niepodana[^pw-4l] | 1,6 mm (parametr linku oferty)[^pw-home]; kolor w promocji niepodany. Kolory w ofercie ogólnej: zielony, czerwony, żółty, niebieski, biały, czarny[^pw-2l] | 2 warstwy: 24 h[^pw-home]; 4 warstwy: niepodane | Kupon 5,00 USD dla nowych[^pw-home] |
| **NextPCB** | „Starting price” 5 USD, FAQ: do 100×100 mm, liczba sztuk niepodana; od 24 h[^np-proto]. Blog z 2026: 5 szt. 100×100 mm 2 warstwy „around $5 to $15”[^np-2v4] | „Starting price” 30 USD, 48 h[^np-proto]; blog: 5 szt. 100×100 mm „around $30 to $60”[^np-2v4] | Niepodane | 2 warstwy od 24 h, 4 warstwy 48 h[^np-proto] | Pierwsze zamówienie PCB: jeśli cena PCB ≤ 20 USD, płaci się 0,10 USD, w przeciwnym razie −20 USD; wysyłka −10 USD (tylko DHL/FedEx); jeden kupon na klienta; nie dotyczy PCBA; ważne do 31.12.2026[^np-free] (blog podaje 30.12.2026[^np-disc]) |
| **ALLPCB** | „From $5 per 5 pcs” dla FR-4, bez rozmiaru i liczby warstw[^ap-home] | Niepodane | Niepodane | FR-4 „from 24 hours”[^ap-home] | „$1 Prototype” i „$30 off Shipping” dla nowych[^ap-home]. **Serwis zawieszony**[^ap-home] |
| **Seeed Fusion** | 4,90 USD, gdy liczba sztuk < 10 i rozmiar < 100×100 mm[^sd-price]; strona PCBA podaje „From a little as $9.90 for 10 pieces”[^sd-pcba] — sprzeczność | Niepodane | Grubości 2 warstw: 0,6–3,0 mm; 4 warstw: 0,8–3,0 mm[^sd-wiki]; warunki promocji niepodane | „Quick Turnaround from 24 hours build time”[^sd-fusion] | „There are no coupons available”[^sd-fusion] |
| **Elecrow** | „$4.9 USD PCB prototype” (bez rozmiaru i liczby sztuk)[^el-pcb]; oferta 1 USD za 10 szt. dotyczy **tylko projektów urządzeń medycznych**, raz na konto na akcję[^el-pcb][^el-special] | Niepodane | 8 kolorów maski: zielony, czerwony, żółty, niebieski, biały, czarny, fioletowy, matowy czarny[^el-pcb]; „6 different colors without extra fees”[^el-proto]; grubości FR-4 0,6–2,5 mm[^el-pcb] | Przykładowe zamówienie: 4–7 dni roboczych[^el-pcb] | 500 punktów (5 USD) dla nowych, maks. 40% koszyka[^el-special] |

### 1.2. Kryterium zespołu projektu: cm² płytki za 1 USD (tylko cena płytek, bez wysyłki)

Wzór: `liczba sztuk × powierzchnia jednej płytki (cm²) ÷ cena (USD)`. Płytka 100×100 mm = 100 cm².

| Fabryka | 2 warstwy | 4 warstwy | Uwagi |
|---|---|---|---|
| **JLCPCB** | 5 × 100 ÷ 2,00 = **250 cm²/USD**[^jlc-ads] | 5 × 100 ÷ 2,00 = **250 cm²/USD**, jeśli promocja obejmuje 100×100 mm[^jlc-ads]; jeśli tylko 50×50 mm (sygnał z materiałów trzecich[^hackclub]): 5 × 25 ÷ 2,00 = **62,5 cm²/USD** | Tylko JLCONE[^jlcone-faq]. Rozmiar dla 4 warstw **[DO WERYFIKACJI]** |
| **PCBWay** | 10 × 100 ÷ 5,00 = **200 cm²/USD**[^pw-home] | 48,00 USD[^pw-4l]: przy 5 szt. **10,4**, przy 10 szt. **20,8 cm²/USD** | Liczba sztuk dla 48 USD **[DO WERYFIKACJI]** |
| **NextPCB** | 5 USD[^np-proto]: przy 5 szt. **100**, przy 10 szt. **200 cm²/USD**; wg bloga 5 szt. za 5–15 USD[^np-2v4]: **33–100 cm²/USD** | 30 USD[^np-proto], przy 5 szt.: **16,7 cm²/USD**; wg bloga 30–60 USD[^np-2v4]: **8,3–16,7 cm²/USD** | Jednorazowo dla nowego klienta[^np-free]: 2 warstwy za 0,10 USD (teoretycznie 5000 cm²/USD, raz); 4 warstwy za 30 − 20 = 10 USD → **50 cm²/USD** (raz) |
| **ALLPCB** | „$5 per 5 pcs”[^ap-home]; przy 100×100 mm: **100 cm²/USD** | Brak danych | Serwis zawieszony — nie brać pod uwagę |
| **Seeed Fusion** | 5 × 100 ÷ 4,90 ≈ **102 cm²/USD** (przy < 10 szt.)[^sd-price]; albo 10 × 100 ÷ 9,90 ≈ **101 cm²/USD**[^sd-pcba] | Brak danych **[DO WERYFIKACJI]** | Sprzeczne ceny 4,90 i 9,90 USD |
| **Elecrow** | 4,9 USD[^el-pcb]: przy 10 szt. ≈ **204**, przy 5 szt. ≈ **102 cm²/USD** | Brak danych **[DO WERYFIKACJI]** | Liczba sztuk i rozmiar dla 4,9 USD **[DO WERYFIKACJI]** |

**Wniosek:** w kryterium „największa powierzchnia za najmniej dolarów” wygrywa JLCPCB (250 cm²/USD dla 2 warstw, a przy potwierdzeniu rozmiaru także dla 4 warstw). Przewaga nad PCBWay przy 2 warstwach wynosi 25% (250 wobec 200), a przy 4 warstwach jest co najmniej dwunastokrotna (250 wobec najwyżej 20,8).

**Pułapki rozmiaru:**

- Promocje dotyczą płytek **do** 100×100 mm[^jlc-ads][^sd-price]. Płytka „około 100×100 mm” musi zmieścić się w tym wymiarze z marginesem.
- Montaż standardowy JLCPCB wymaga listew technologicznych i znaczników (edge rails / fiducials: „Necessary”)[^jlc-pcba-cap]. Jeśli listwy dokłada fabryka, wymiar zamówionej płytki rośnie — czy wychodzi wtedy poza promocję: **[DO WERYFIKACJI]**. Bezpieczny wariant projektowy to płytka mniejsza niż 100×100 mm albo listwy wliczone w obrys 100×100 mm.

### 1.3. Zmiany cen w 2026 (tło)

- JLCPCB 13.06.2026: wzrost kosztów laminatu, „dynamic material pricing” od 26.06.2026 dla FR4, FPC, aluminium, miedzi, Rogers, teflonu, bez podania kwot[^jlc-pricing-jun].
- JLCPCB 03.08.2026: zniesienie tymczasowych dopłat ilościowych dla 1-, 2- i 4-warstwowych FR-4 (wcześniej m.in. dla zamówień powyżej 50 m²)[^jlc-fr4-aug].
- JLCPCB 06.08.2026: „slight increase” cen 4 warstw z przelotkami wypełnianymi żywicą (resin filled); tymczasowo około 15 dni[^jlc-resin-aug]. Płytka pilota nie potrzebuje przelotek wypełnianych żywicą, jeśli projekt jej nie wymusi.
- Na stronach JLCPCB i JLC3DP widnieje baner „Account Restriction Notice” bez treści w pobranym tekście[^jlc-pricing-jun][^jlc3dp] — **[DO WERYFIKACJI]**, czego dotyczy.

---

## 2. Montaż SMT i THT

### 2.1. Zestawienie

| Fabryka | Uruchomienie i szablon | Punkt lutowniczy | Opłata za rodzaj części | THT | Strony / ilości | Magazyn części i części powierzone |
|---|---|---|---|---|---|---|
| **JLCPCB** | Ekonomiczny: uruchomienie 8,18, szablon 1,53. Standardowy: uruchomienie 25,56 (1 strona) / 51,12 (2 strony), szablon 8,21 / 16,42[^jlc-pcba-price] | SMT 0,0016 USD (ekonomiczny do 100 000 pkt; standardowy do 50 000 pkt, potem 0,0013 i 0,0012)[^jlc-pcba-price] | Ekonomiczny: 3,07 USD za każdy rodzaj części rozszerzonej, podstawowe bez opłaty. Standardowy: 1,53 USD za każdy rodzaj części, także podstawowej[^jlc-pcba-price]. FAQ: części „Preferred Extended” zwolnione z opłaty w trybie ekonomicznym[^jlc-faq1] | Lutowanie ręczne 3,58 USD za zamówienie + 0,0164 USD/pkt (do 10 000 pkt)[^jlc-pcba-price]; części „wave soldering” montowane ręcznie, czas +1 dzień[^jlc-faq1] | Ekonomiczny: jedna strona, 2–50 szt., 0,8–1,6 mm, 1–3 dni. Standardowy: 1 lub 2 strony, 2–80 000 szt., od 4 dni[^jlc-pcba-cap] | Strona główna: „740,000+ in-stock parts” / „680,000+”[^jlc-home]; FAQ: 698 podstawowych i 300k+ rozszerzonych[^jlc-faq1] (dane niespójne). LCSC: „760,000+ SKUs”[^lcsc]. Części powierzone: odprawa ok. 45 USD (paczka < 5000 CNY) lub 85 USD (> 5000 CNY), + 70 USD za każde 50 numerów części powyżej 50[^jlc-consign] |
| **PCBWay** | Szablon: na jednej stronie „PCBA provides free stencil” i jednocześnie „$15/pcs”[^pw-asm] — sprzeczność | Niepublikowane; kalkulator liczy wg liczby unikalnych części, SMD, BGA/QFP i THT[^pw-quotesmt] | Niepublikowane | Obsługiwany SMT, THT i mieszany[^pw-asm-cap] | 1 lub 2 strony; „Minimum order of 5 pieces”[^pw-asm-cap] (Q&A z 2020: „no MOQ for assembled boards”[^pw-qa]) | Turnkey, kitted/consigned, combo[^pw-asm-cap]; przy częściach powierzonych pasywnych 0603–1206 minimum 50 szt. w tym 30 zapasu[^pw-qa] |
| **NextPCB** | Szablon „Free with all PCBA orders”[^np-asm]; uruchomienie niepublikowane | Niepublikowane | Niepublikowane | SMT, THT, mieszany, lutowanie automatyczne i ręczne[^np-asm] | 1 lub 2 strony; bez MOQ, od 1 szt.[^np-asm] | HQ Online „600K+” części w magazynie; dostęp do „Over 20 million components”[^np-asm]; turnkey, częściowo, powierzone[^np-asm] |
| **ALLPCB** | „$35/10 pcs” PCBA dla wszystkich[^ap-home] | Niepublikowane | Niepublikowane | Brak danych | Brak danych | Serwis zawieszony[^ap-home] |
| **Seeed Fusion** | Niepublikowane na stronie; „No Operation Fees on orders over 100 pcs”[^sd-pcba] | Niepublikowane | Niepublikowane | SMT, THT, 1/2 strony, mieszany[^sd-pcba] | PCBA od 1 szt., PCB od 5 szt.[^sd-wiki] | Open Parts Library „over 150,000 locally in-stock parts”; turnkey „from 7 working days” przy częściach z OPL[^sd-pcba] |
| **Elecrow** | Szablon 12,00 USD (przykład kosztorysu)[^el-pcba] | Niepublikowane; zależy od liczby padów SMT, THT i ilości[^el-pcba] | Części powierzone bez opłaty manipulacyjnej[^el-home] | Wliczony w wycenę padów THT[^el-pcba] | Od 1 szt.; do 20 szt. zamówienie online, powyżej 20 szt. wycena ręczna[^el-pcba] | Turnkey, powierzone, combo; zapas: pasywne 0603–1206 min. 50 + 30 szt., 0201/0402 min. 100 + 50 szt.[^el-pcba]. Czas ogólny 3 tygodnie[^el-pcba] |

**Promocje montażu (październik 2026):**

- **JLCPCB:** miesięczne kupony SMT — strona „cheapest-pcb-way” podaje „$24 SMT Coupons Monthly”[^jlc-cheap], blog z 27.02.2024 wymienia zestaw 25 USD (6, 9, 10 USD SMT oraz 6 i 9 USD „Special Offer”)[^jlc-freeasm]. Aktualność zestawu z 2024: **[DO WERYFIKACJI]**. Strona główna: „PCB Assembly starts at $8.00”[^jlc-home].
- **PCBWay:** „Only $ 29 in total for 1-20pcs assembly” z darmową wysyłką[^pw-home]; strona montażu podaje też czas „3-5 days”[^pw-asm]. Warunki (liczba unikalnych części, padów, strony): **[DO WERYFIKACJI]**. Kalkulator pokazuje „50% OFF Assembly Sale” bez warunków[^pw-quotesmt].
- **NextPCB:** do 200 USD rabatu na SMT dla 1–10 szt., minimalne zamówienie SMT 50 USD, tylko FR4 i turnkey, wykluczone zamówienia z ≥ 5% części powierzonych, bez wysyłki, z darmowym testem funkcjonalnym do 10 szt.[^np-disc]; 50% rabatu na SMT dla 100 szt. przy zamówieniu > 300 USD[^np-disc]; „Free assembly on your first Rev 0 order, up to $500 USD”[^np-asm]. Strona zawiera sprzeczności (czas Rev 0: 48 h i 7 dni roboczych)[^np-asm].
- **Seeed Fusion:** „Free Shipping on all PCBA orders”[^sd-pcba].
- **Elecrow:** darmowy test funkcjonalny dla zamówień powyżej 2000 USD, darmowa kontrola wizualna 100%[^el-pcba].

### 2.2. Wyliczenie montażu u JLCPCB dla Pilota Wnet

Założenia przykładowe (do zastąpienia prawdziwym BOM): 5 płytek, montaż jednostronny, 30 unikalnych części, 350 punktów SMT i 60 punktów THT na płytkę (gniazdo RJ45 z transformatorem, złącza JST XH, ewentualnie zaciski 4,8 mm), RTG wymagane tylko dla modułu ESP32-S3.

Moduł ESP32-S3-WROOM-1-N16R8 ma status „Standard Only”[^jlc-esp], więc całe zamówienie idzie montażem standardowym:

| Pozycja | Stawka | Wartość (USD) |
|---|---|---|
| Uruchomienie (1 strona) | 25,56[^jlc-pcba-price] | 25,56 |
| Szablon (1 strona) | 8,21[^jlc-pcba-price] | 8,21 |
| Ładowanie podajników | 30 × 1,53[^jlc-pcba-price] | 45,90 |
| Punkty SMT | 5 × 350 = 1750 × 0,0016[^jlc-pcba-price] | 2,80 |
| RTG modułu ESP32-S3 | 5 szt. × 1,64 (próg 1–10 szt.)[^jlc-pcba-price] | 8,20 |
| Lutowanie ręczne — opłata | 3,58 za zamówienie[^jlc-pcba-price] | 3,58 |
| Lutowanie ręczne — punkty THT | 5 × 60 = 300 × 0,0164[^jlc-pcba-price] | 4,92 |
| Pakowanie | 0,50 + 0,00003 × 500 cm²[^jlc-pcba-price] | 0,52 |
| **Razem opłaty montażowe** | | **99,69** |

Do tego: płytki (2,00 USD w JLCONE, jeśli promocja obejmie 4 warstwy 100×100 mm[^jlc-ads]), części (ceny modułów nie są widoczne w pobranym tekście stron części — **[DO WERYFIKACJI]**), wysyłka i podatki (rozdz. 5). Jeden kupon SMT nowego klienta obniża sumę o 10 USD[^jlc-coupons].

Porównanie: gdyby wszystkie części kwalifikowały się do montażu ekonomicznego (np. inny wariant modułu — **[DO WERYFIKACJI]**), przy 10 rodzajach części rozszerzonych suma wyniosłaby 8,18 + 1,53 + 10 × 3,07 + 2,80 + 8,20 + 3,58 + 4,92 = **59,91 USD**[^jlc-pcba-price], czyli około 40% mniej. Układ W5500 i moduł LoRa Seeed C5129913 mają status „Economic and Standard”[^jlc-w5500][^jlc-lora-seeed]; o trybie decyduje moduł ESP32-S3.

Wniosek projektowy: **dobór części pod tryb montażu JLCPCB to największa pojedyncza oszczędność** — ładowanie podajników (45,90 USD) przewyższa wszystkie pozostałe pozycje.

### 2.3. Części kluczowe w katalogu JLCPCB (sprawdzone 18.10.2026)

| Część | Numer JLCPCB | Status | Tryb montażu | Uwagi |
|---|---|---|---|---|
| ESP32-S3-WROOM-1-N16R8 | C2913202 | Extended | Standard Only, RTG wymagane, MSL 3[^jlc-esp] | Części zakupione zostają w bibliotece klienta, „cannot be shipped separately”[^jlc-esp] |
| ESP32-S3-WROOM-1-N16 | C2913199 | Extended | Standard Only, MSL 3[^jlc-esp16] | — |
| WIZnet W5500 (Ethernet z PHY) | C32843 | Extended | Economic and Standard[^jlc-w5500] | Stan magazynu niewidoczny w pobranym tekście **[DO WERYFIKACJI]** |
| Moduł LoRa Seeed 317990829 (868/915 MHz, SMD-28P 12×12 mm) | C5129913 | Extended | Economic and Standard[^jlc-lora-seeed] | Strona nie podaje układu radiowego **[DO WERYFIKACJI]** (czy SX1262 — ważne dla Meshtastic/MeshCore) |
| JST XH 5-pin B5B-XH-A | C157991 | Extended (wg wyniku wyszukiwania)[^jlc-jst] | THT, lutowanie falą/ręczne | **[DO WERYFIKACJI]** status |
| Zacisk płaski 4,8 mm Keystone 1212 | C3217931 | — | THT („plugin”, lutowanie falą) wg wyniku wyszukiwania[^jlc-faston] | **[DO WERYFIKACJI]** footprint |

W katalogu JLCPCB pojawiają się też inne moduły 868 MHz (np. G-NiceRF LORA1262-868TCXO, C5356644) — parametry trzeba sprawdzić na stronie części **[DO WERYFIKACJI]**.

---

## 3. Druk 3D i obróbka

| Fabryka | SLA | MJF / SLS | FDM | Metale | CNC | Laser / blacha |
|---|---|---|---|---|---|---|
| **JLC3DP / JLCCNC** | Od 0,30 USD, 2 dni, ±0,2 mm; żywice m.in. Ledo 6060, Black Resin, Transparent 8001, „8+ resin materials”[^jlc3dp] | MJF (PA12, PA11, PAC) od 1,00 USD, 3 dni; SLS (m.in. 3301PA, 1172Pro) od 1,00 USD, 3 dni[^jlc3dp]. MJF-PA12 0,275 USD/g od 13.08.2025[^jlc3dp-aug25] (stawka sprzed obniżek z 24.07.2026[^jlc3dp-jul]) | ABS, ASA, PLA, PA12-CF, TPU od 1,00 USD, 3 dni[^jlc3dp]; PETG nie ma na liście[^jlc3dp] | SLM 316L i tytan TC4 od 8,00 USD, 3 dni[^jlc3dp]; 316L: 72 h, maks. 390×390×290 mm[^jlc3dp-316l]; SLM-316L 0,21 USD/g (08.2025)[^jlc3dp-aug25]; BJ-316L od 5,00 USD[^jlc3dp]; AlSi10Mg nie ma na liście[^jlc3dp]. 24.07.2026: tytan TC4 −47%, PA12-CF −24%, PLA-P −18%, ABS −9%, malowanie natryskowe +16,67%[^jlc3dp-jul] | Frezowanie i toczenie od 5,00 USD, 3 dni, ±0,05 mm; aluminium 6061/7075, mosiądz, miedź, stal, ABS, PA6, PC, **PMMA (akryl)**, POM, FR4; maks. 1100×600×500 mm; **drewna brak**[^jlccnc] | Blacha (cięcie laserowe, gięcie, spawanie) od 0,40 USD, 2 dni, ±0,2 mm; Al 5052, stal nierdzewna 201/304, stal walcowana na zimno, ocynkowana[^jlccnc] |
| **PCBWay** | 15 żywic, m.in. UTR 8360, UTR-8100 przezroczysta, Somos Ledo[^pw-3d] | SLS: PA12, PA12+35% GF, TPU; MJF: HP PA12, PA12 40% GF; PA11 niewymienione[^pw-3d] | PLA, PLA-CF, ABS, PETG, PETG-CF, TPU, PC, ASA, ASA-CF, PEEK, PA6-CF/GF[^pw-3d] | SLM: AlSi10Mg, 316L, tytan TC4, stal narzędziowa[^pw-3d] | CNC „From $25”, 7–9 dni[^pw-home]; materiały: metale i tworzywa, w tym PMMA; drewna brak[^pw-rp] | Blacha: cięcie laserowe, gięcie, wkładki, spawanie, bez cen[^pw-rp]. Druk 3D „From $4.98”, 3–4 dni[^pw-home]. Maks. wymiar druku 2100×700×800 mm[^pw-3d] |
| **NextPCB** | Brak usługi w wynikach | Brak | Brak | Brak | Tylko frezowanie płytek PCB | Brak[^np-home] |
| **ALLPCB** | Linki bez cen[^ap-home] | — | — | — | Linki bez cen[^ap-home] | — |
| **Seeed Fusion** | Druk 3D: tylko STL, maks. 10 MB (strona starsza)[^sd-3d] | — | — | — | CNC wymienione w opisie usług[^sd-what] | Cennik **[DO WERYFIKACJI]** |
| **Elecrow** | Żywice m.in. 9400, przezroczysta, półprzezroczysta, czarna[^el-3d] | Nylon, nylon + włókno szklane[^el-3d] | PLA, PETG (kolory: czarny, biały, pomarańczowy, niebieski, czerwony, zielony)[^el-3d] | 316L, AlSi10Mg, Ti6Al4V[^el-3d] | Usługa wymieniona bez cen[^el-home] | **Akryl laserem:** przykład 4,90 USD za 5 szt. 100×100 mm, 2 mm, przezroczysty; grubości w formularzu 2, 3, 5, 8, 10 mm; kolory: przezroczysty, czarny, fioletowy, biały, niebieski, zielony, czerwony, żółty; grawer i druk UV na zapytanie[^el-acr]. **Drewno laserem:** od 4,80 USD (10×10 cm, 2 mm), grubości 2, 3, 5 mm, maks. 30×30 cm w opcjach, wysyłka w 3–5 dni[^el-wood]. Promocje: druk 3D 1 USD za 1–2 szt. z żywicy 9400 < 50 g (pierwszy projekt dnia)[^el-3d][^el-special]; akryl 1 USD za 5 szt. przezroczysty 2–3 mm do 15×15 cm[^el-special] |

**Wnioski dla obudowy arcade:**

- **Drewniany korpus bartopa** nie jest usługą żadnej z tych fabryk w potrzebnej skali: JLCCNC i PCBWay nie wymieniają drewna[^jlccnc][^pw-rp], a Elecrow tnie drewno do 30×30 cm i 5 mm grubości[^el-wood]. Korpus lepiej zlecić w Polsce (CNC/laser płyt) — osobny tor **[DO WERYFIKACJI w torze obudowy]**.
- **Panel sterowania i wkładki:** akryl cięty laserem (Elecrow, do 10 mm w formularzu[^el-acr]; JLCCNC frezuje PMMA[^jlccnc]) albo blacha aluminiowa 5052 z JLCCNC[^jlccnc] nadają się na płytę pod joystick i przyciski.
- **Drobne elementy** (uchwyty płytki, dystanse, ramka OLED, osłona gniazda RJ45): MJF PA12 lub SLA w JLC3DP od 1,00 / 0,30 USD[^jlc3dp], wysłane razem z płytkami.

---

## 4. Inne usługi

| Usługa | JLCPCB | PCBWay | NextPCB | Seeed Fusion | Elecrow |
|---|---|---|---|---|---|
| Naklejki, etykiety, nadruki (obudowa, przezroczyste wkładki przycisków) | Nie znaleziono usługi | Nie znaleziono usługi | Nie znaleziono | Nie znaleziono | „Personalized labeling” bez szczegółów[^el-home]; druk UV i sitodruk na akrylu na zapytanie[^el-acr] |
| Wiązki i kable (JST, zaciski 4,8 mm) | Kable tylko jako części do PCBA, bez wysyłki osobno[^jlc-esp]; usługi wiązek nie znaleziono | „Cable Wire Harness Assembly” jako opcja wyceny poza kalkulatorem[^pw-quotesmt] | Usługa wiązek: JST, Molex, Hirose, IDC i inne; MOQ 1 szt.; zaciski typu faston 4,8 mm **niewymienione**[^np-cable] | Nie znaleziono | „Customized Cable Solutions”, „custom wiring harness” bez cen[^el-home] |
| Montaż w obudowie (box build) | Nie znaleziono | Opcja wyceny poza kalkulatorem[^pw-quotesmt] | Niewymieniony[^np-asm] | Nie znaleziono | Usługa w menu; strona usługi zwraca błąd 404 (18.10.2026)[^el-box] |
| Programowanie układów | „We support program some parts”, wycena po przeglądzie inżynierskim[^jlc-faq2] | „Firmware loading” w kalkulatorze[^pw-quotesmt]; programowanie przed montażem, opłata osobno[^pw-qa] | „IC programming” w ofercie[^np-asm] | Wymienione bez ceny[^sd-wiki] | „Flashing/Testing Cost” w formule wyceny[^el-pcba] |
| Testy funkcjonalne | Nie znaleziono; RTG i AOI w cenniku/zdolnościach[^jlc-pcba-cap] | „Function test” w kalkulatorze; opłata wg czasu[^pw-quotesmt][^pw-qa] | Darmowy test funkcjonalny do 10 szt. w promocji[^np-disc] | Test funkcjonalny wg planu klienta, płatny[^sd-wiki] | Darmowy dla zamówień > 2000 USD; przyrząd ICT 300–1000 USD na projekt[^el-pcba] |

**Wniosek:** naklejki i przezroczyste wkładki do przycisków arcade nie są typową usługą tych fabryk — trzeba je zlecić lokalnie albo kupić gotowe u dostawców części arcade **[DO WERYFIKACJI w torze części arcade]**. Wiązkę od mikroprzełączników (zaciski 4,8 mm) do złącz JST na płytce najprościej kupić gotową u dostawcy części arcade lub zrobić samemu; z fabryk usługę wiązek z JST potwierdza NextPCB[^np-cable], a PCBWay i Elecrow deklarują ją bez szczegółów[^pw-quotesmt][^el-home].

---

## 5. Wysyłka do Polski, VAT, cło

### 5.1. Prawo UE od 1.07.2026 (źródła urzędowe)

- Od 1.07.2026 do 1.07.2028 obowiązuje cło **3 EUR za „item”** w przesyłkach o wartości do 150 EUR; „item” to towary o tej samej klasyfikacji taryfowej, opisie i pochodzeniu, a w praktyce cło nalicza się **za linię zgłoszenia**[^eu-a2m]. Przykład Komisji: pięć koszulek = 3 EUR, koszulka i zegarek = 6 EUR[^eu-taxud].
- Cło 3 EUR stosuje się niezależnie od reżimu VAT (IOSS, szczególne procedury, zwykły VAT importowy)[^eu-a2m].
- Opłata manipulacyjna UE (handling fee) jest osobnym środkiem: Komisja podaje „autumn 2026”, kwota i data „to be determined”[^eu-taxud]; Access2Markets wspomina termin 1.11.2026[^eu-a2m]; FAQ JLCPCB podaje „November 2026”, szczegóły nieustalone[^jlc-eu-faq]; blog PCBWay pisze o 2 EUR za przesyłkę od 1.11.2026[^pw-eu] (źródło nieurzędowe). Kwota: **[DO WERYFIKACJI]**.
- VAT w Polsce: stawka podstawowa 23%[^pl-vat1]; w imporcie stawki są takie same jak w kraju, a podstawą jest wartość celna powiększona o cło; czynny podatnik VAT może odliczyć VAT z importu[^pl-vat2].
- Stawka celna dla płytek drukowanych (CN 8534) i zmontowanych modułów: **[DO WERYFIKACJI w TARIC]**.

### 5.2. Fabryki

| Fabryka | Przewoźnicy i czas | Koszt do Polski | VAT / IOSS / DDP | Uwagi |
|---|---|---|---|---|
| **JLCPCB** | DHL, FedEx, UPS i inne; „most orders arriving within 2–7 business days”[^jlc-home] | Liczony wg wagi przy wycenie[^jlc-ship2]; kwota **[DO WERYFIKACJI w kalkulatorze]**. Kupon 10 USD na wysyłkę powyżej 15 USD[^jlc-coupons]; JLCONE ma „Exclusive Shipping Rates”[^jlcone-faq] | Klient indywidualny do 150 EUR: VAT pobiera JLCPCB; firma: VAT pobiera urząd celny[^jlc-customs]. IOSS pokrywa tylko VAT, nie cło 3 EUR[^jlc-eu-news]. **Opcja DDP:** JLCPCB nalicza i pobiera przy zamówieniu VAT, cło tymczasowe i opłatę przewoźnika[^jlc-eu-faq]. „Global Standard Direct Line” jest zawsze traktowana jako B2C, nawet z danymi firmy[^jlc-eu-faq] | Opłaty przewoźników za wyłożenie cła/VAT w Polsce: DHL 2,5% min. 69,00 PLN; UPS 3% min. 85,00 PLN (+41,30 PLN poniżej 22 EUR); FedEx 2,5% min. 63,60 PLN[^jlc-eu-faq]. Przerwa świąteczna 1–4.10.2026 już minęła[^jlc-news] |
| **PCBWay** | DHL 3–7 dni rob., UPS 3–7, FedEx 4–7, Global Standard/Direct 8–13 dni rob., EMS i poczta 15–30 dni rob.[^pw-ship] | Niepublikowany, w kalkulatorze[^pw-ship] | Kalkulator: „Customs duties and VAT are not included!”[^pw-quotesmt]; stara strona pomocy (2018) wspomina DDP/IOSS bez szczegółów[^pw-customs]; PCBWayExpress z DDP (2020) obejmował UK, Hiszpanię, Niemcy, Francję, Włochy — **bez Polski**[^pw-express] | Strona pomocy wspomina fabrykę w UE z wysyłką tylko w UE — **[DO WERYFIKACJI]**, czy dotyczy prototypów[^pw-eu-factory] |
| **NextPCB** | Kurierzy DHL, UPS, FedEx; poczta (China Post, EU Post)[^np-eu] | Niepublikowany; ceny „ex-works”, bez wysyłki i ceł[^np-prices] | „NextPCB has fully activated IOSS” (29.06.2026) dla B2C do 150 EUR; B2B i > 150 EUR bez IOSS; DDP niewymienione[^np-eu] | Cło pobiera przewoźnik, IOSS go nie pokrywa[^np-eu] |
| **ALLPCB** | — | „$30 off Shipping”[^ap-home] | — | Serwis zawieszony[^ap-home] |
| **Seeed Fusion** | **[DO WERYFIKACJI]** | „Free Shipping on all PCBA orders”[^sd-pcba] | **[DO WERYFIKACJI]** | — |
| **Elecrow** | Poczta polecona 7–25 dni (do 2 kg); DHL ok. 3–5 dni rob.[^el-ship] | Poczta: 3,18 USD za pierwsze 10 g + 0,18 USD za każde kolejne 10 g[^el-ship]. Dla przykładowej paczki 5 płytek 100×100 mm o wadze 275 g[^el-pcb]: 3,18 + 27 × 0,18 = **8,04 USD** (wyliczenie). DHL w koszyku[^el-ship] | Podatki i cła nie są wliczone, płaci kupujący[^el-ship]; DDP/IOSS niewymienione | — |

### 5.3. Co to znaczy dla Radia Wnet

- Zamówienie **na firmę (B2B)** idzie formalną odprawą ze zwykłą stawką celną, bez reguły 3 EUR[^jlc-eu-faq]. Kurier pobierze VAT 23% i opłatę za wyłożenie należności — u DHL minimum 69,00 PLN na przesyłkę[^jlc-eu-faq]. VAT z importu firma może odliczyć[^pl-vat2].
- Zamówienie **jako osoba prywatna (B2C) do 150 EUR**: VAT pobiera fabryka przez IOSS, cło 3 EUR za linię zgłoszenia pobierze przewoźnik albo fabryka w opcji DDP[^jlc-eu-faq][^eu-a2m]. Czy VAT zapłacony przez IOSS da się odliczyć w firmie: **[DO WERYFIKACJI z księgową]**.
- **Łączenie zamówień:** płytki, druk 3D i blacha z ekosystemu JLC mogą przyjść jedną paczką; FAQ JLCPCB radzi przy B2C łączyć towar powyżej 150 EUR, bo wtedy obowiązuje zwykła taryfa zamiast 3 EUR za linię[^jlc-eu-news]. Przy kilku liniach (płytki, części drukowane, blacha) to może się opłacać — **[DO WERYFIKACJI wg kodów CN]**.

---

## 6. Rekomendacja: jedna fabryka

### JLCPCB (z JLC3DP, JLCCNC i biblioteką części JLCPCB/LCSC)

**Uzasadnienie liczbami:**

1. **Powierzchnia za dolara:** 250 cm²/USD dla 2 warstw[^jlc-ads] wobec 200 cm²/USD w PCBWay[^pw-home] i około 100–204 cm²/USD u pozostałych (rozdz. 1.2). Dla 4 warstw 100×100 mm, jeśli JLCONE potwierdzi rozmiar, 250 cm²/USD wobec najwyżej 20,8 cm²/USD w PCBWay[^pw-4l] i 16,7 cm²/USD w NextPCB[^np-proto].
2. **Przewidywalny koszt montażu:** pełny, opublikowany cennik (rozdz. 2.1)[^jlc-pcba-price]. Dla 5 płytek opłaty montażowe wynoszą około 99,69 USD w trybie standardowym, a przy częściach zgodnych z trybem ekonomicznym około 59,91 USD (rozdz. 2.2). U PCBWay, NextPCB, Seeed i Elecrow tej kalkulacji nie da się zrobić bez kalkulatora.
3. **Części do projektu są w jednym katalogu:** ESP32-S3[^jlc-esp], W5500[^jlc-w5500], LoRa 868 MHz[^jlc-lora-seeed], JST XH[^jlc-jst], zaciski 4,8 mm[^jlc-faston], z widocznym statusem trybu montażu na stronie każdej części.
4. **Druk 3D i obróbka w tym samym ekosystemie:** SLA od 0,30 USD, MJF/FDM od 1,00 USD[^jlc3dp], CNC od 5,00 USD, blacha od 0,40 USD[^jlccnc]; kupony nowego klienta 20 USD na CNC i 2 × 10 USD na druk 3D[^jlc-coupons].
5. **Wysyłka do UE z DDP:** VAT, cło tymczasowe i opłata przewoźnika naliczane przy zamówieniu[^jlc-eu-faq], z opublikowanymi stawkami opłat przewoźników dla Polski[^jlc-eu-faq] — tylko JLCPCB publikuje te dane dla Polski.

**Warunki i ryzyka tej rekomendacji:**

- Cena 2 USD wymaga aplikacji JLCONE[^jlcone-faq] — decyzja zespołu projektu.
- Rozmiar 4 warstw w promocji: **[DO WERYFIKACJI w JLCONE]**.
- Moduł ESP32-S3-WROOM-1 wymusza montaż standardowy[^jlc-esp] (szablon 8,21 zamiast 1,53, uruchomienie 25,56 zamiast 8,18, 1,53 USD za każdy rodzaj części[^jlc-pcba-price]) i listwy technologiczne[^jlc-pcba-cap].

**Alternatywa taktyczna na Rev 0:** przed pierwszym zamówieniem warto porównać trzy wyceny na tych samych plikach:

- **JLCPCB:** płytki 2,00 USD[^jlc-ads] i opłaty montażowe ok. 99,69 USD (rozdz. 2.2) minus kupon 10 USD[^jlc-coupons].
- **NextPCB:** płytki 4-warstwowe od 30 USD minus 20 USD kuponu[^np-proto][^np-free], montaż SMT do 200 USD rabatu dla 1–10 szt. przy turnkey (warunek: minimalne zamówienie SMT 50 USD)[^np-disc]. Może wyjść taniej przy pierwszym prototypie, ale tylko raz, bez druku 3D i ze sprzecznymi czasami realizacji[^np-asm].
- **PCBWay:** 4 warstwy 48,00 USD[^pw-4l] i montaż „$29 in total for 1-20pcs” z darmową wysyłką[^pw-home]. Przy nieznanych warunkach promocji może wyjść taniej przy 4 warstwach.

Wyceny musi uruchomić człowiek. Agent nie wypełniał formularzy.

---

## 7. Lista do weryfikacji

1. JLCONE: czy 2 USD obejmuje 4 warstwy 100×100 mm, jaka grubość i jaki kolor; czy listwy technologiczne wypychają płytkę z promocji.
2. PCBWay: liczba sztuk dla ceny 48 USD (4 warstwy 100×100 mm); warunki promocji montażu 29 USD i czy darmowa wysyłka obejmuje Polskę.
3. NextPCB: co znaczy „minimalne zamówienie SMT 50 USD” w promocji −200 USD; liczba sztuk w cenie „od 5 USD” i „od 30 USD”.
4. Seeed Fusion: aktualna cena 2 warstw (4,90 czy 9,90 USD) i cena 4 warstw; wysyłka i VAT do Polski.
5. Elecrow: liczba sztuk i rozmiar dla „$4.9 USD PCB prototype”; cena 4 warstw.
6. Kwota opłaty manipulacyjnej UE od listopada 2026 (Komisja: „to be determined”).
7. Stawka celna TARIC dla CN 8534 (płytki) i dla zmontowanych modułów.
8. Czy VAT zapłacony przez IOSS (wysyłka B2C) da się odliczyć w firmie — pytanie do księgowej.
9. Koszt wysyłki JLCPCB/PCBWay/NextPCB do Polski dla paczki ok. 300 g (kalkulator).
10. Ceny i stany magazynowe modułów ESP32-S3, W5500 i LoRa 868 MHz (strony części nie pokazały ich w pobranym tekście); który moduł LoRa ma SX1262 (zgodność z Meshtastic/MeshCore).
11. Treść banera „Account Restriction Notice” na stronach JLCPCB/JLC3DP.
12. Kupony SMT JLCPCB w październiku 2026 (zestaw 24–25 USD miesięcznie opisany w 2024).
13. Status ALLPCB (serwis zawieszony) — czy wróci.

---

## 8. Ryzyka

- **Promocje zmieniają się bez zapowiedzi:** JLCPCB od 26.06.2026 stosuje „dynamic material pricing” i prosi o opieranie się na wycenie w czasie rzeczywistym[^jlc-pricing-jun]; NextPCB traktuje ceny reklamowe jako „indicative”[^np-prices].
- **Uzależnienie od aplikacji JLCONE:** cena 2 USD i specjalne stawki wysyłki są tylko w aplikacji[^jlcone-faq].
- **Części zamknięte w bibliotece fabryki:** części kupione w JLCPCB „cannot be shipped separately”[^jlc-esp] — nie da się ich odebrać do ręcznego montażu w Polsce.
- **Koszt przy każdej przesyłce firmowej:** opłata przewoźnika za wyłożenie VAT/cła (DHL min. 69 PLN)[^jlc-eu-faq] — przy małych zamówieniach może przekroczyć cenę płytek.
- **Sprzeczne dane na stronach producentów:** liczba części w magazynie JLCPCB (680 tys., 740 tys., 300 tys.+)[^jlc-home][^jlc-faq1]; czas montażu JLCPCB („1 to 3 days” / „4 days or more”[^jlc-pcba-cap] wobec „90% … within 24 hours”[^jlc-faq1]); szablon PCBWay „free” i „$15”[^pw-asm]; czasy Rev 0 w NextPCB[^np-asm].
- **ALLPCB zawieszone**[^ap-home]: nie składać tam zamówień.
- **Promocje mogą być niedostępne z kontem firmowym albo wykluczać się nawzajem:** „Multiple coupons cannot be combined on a single order”[^jlcone-news]; promocja NextPCB jest jednorazowa[^np-free].
- **Moduły radiowe:** wybór modułu LoRa wpływa na zgodność z Meshtastic/MeshCore i na tryb montażu — tor R-radio **[DO WERYFIKACJI]**.

---

## 9. Źródła (wszystkie sprawdzone 18.10.2026)

Fora i serwisy trzecie użyto tylko jako sygnał, nie jako źródło liczby (oznaczone „sygnał”).

[^jlc-home]: JLCPCB, strona główna — https://jlcpcb.com/
[^jlc-ads]: JLCPCB, „Professional PCB Prototypes” (porównanie producentów) — https://jlcpcb.com/ads/pcb-manufacturer-comparison
[^jlc-proto]: JLCPCB, „Fast PCB Prototypes in 24 Hours” — https://jlcpcb.com/ads/pcb-prototype
[^jlc-cheap]: JLCPCB, „All PCB Prototype the Cheapest PCB Way” — https://jlcpcb.com/cheapest-pcb-way
[^jlcone-news]: JLCPCB, „JLCPCB Unveils JLCONE: $2 PCBs & Exclusive Shipping Rates”, 22.08.2026 — https://jlcpcb.com/news/jlcpcb-jlcone-desktop-app
[^jlcone-faq]: JLCPCB, „JLCONE FAQ”, aktualizacja 22.09.2026 — https://jlcpcb.com/help/article/jlcone-desktop-app
[^jlc-time]: JLCPCB, „PCB Fabrication Services and Production Time”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/pcb-fabrication-services-and-production-time
[^jlc-quote]: JLCPCB, kalkulator (tylko odczyt opisu opcji, bez wypełniania) — https://cart.jlcpcb.com/quote
[^jlc-cap]: JLCPCB, „PCB Capabilities” — https://jlcpcb.com/capabilities/pcb-capabilities
[^jlc-pcba-price]: JLCPCB, „PCB Assembly Cost: What Does the Price Include?”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/pcb-assembly-price
[^jlc-pcba-cap]: JLCPCB, „PCB Assembly Capabilities” — https://jlcpcb.com/capabilities/pcb-assembly-capabilities
[^jlc-faq1]: JLCPCB, „PCB Assembly FAQs”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/pcb-assembly-faqs
[^jlc-faq2]: JLCPCB, „PCB Assembly FAQs (Part 2)”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2
[^jlc-coupons]: JLCPCB, „New Customer Coupon Guide”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/new-customer-coupons
[^jlc-freeasm]: JLCPCB, „Free PCB Assembly for 1–6 Layer Boards…”, 27.02.2024 — https://jlcpcb.com/blog/free-assembly-for-1-6-layer-pcbs-and-discounts-on-8-20-layer-pcba
[^jlc-pricing-jun]: JLCPCB, „Notice Regarding Recent PCB Pricing and Capacity Allocation Measures”, 13.06.2026 — https://jlcpcb.com/news/jlcpcb-pcb-pricing-notice
[^jlc-fr4-aug]: JLCPCB, „JLCPCB Adjusts FR4 PCB Pricing as Raw Material Costs Stabilize”, 03.08.2026 — https://jlcpcb.com/news/jlcpcb-fr4-pcb-price-adjustment-august2026
[^jlc-resin-aug]: JLCPCB, „Temporary Adjustments for Resin Plugging Process & 6+ Layer PCB Orders”, 06.08.2026 — https://jlcpcb.com/news/pcb-lead-time-and-price-adjustment-august2026
[^jlc-news]: JLCPCB, Newsroom (m.in. „September & October 2026 Holiday Schedule Notice”, 15.09.2026) — https://jlcpcb.com/news oraz https://jlcpcb.com/news/page/2
[^jlc-eu-news]: JLCPCB, „Notice on the Implementation of the EU Tax Reform Effective July 2026”, 27.06.2026 — https://jlcpcb.com/news/eu-customs-reform-2026
[^jlc-eu-faq]: JLCPCB, „EU Tax Reform July 2026 – Client FAQ”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/eu-customs-reform-faq
[^jlc-customs]: JLCPCB, „Customs, Duties and Taxes”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/customs,-duties-and-taxes
[^jlc-ship2]: JLCPCB, „How much does shipping cost?”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/how-much-does-shipping-cost (oraz https://jlcpcb.com/help/article/shipping-methods-and-delivery-time — tabela jest obrazem, nieczytelna)
[^jlc-consign]: JLCPCB, „Important note … before you consign the part to JLCPCB”, aktualizacja 09.09.2026 — https://jlcpcb.com/help/article/important-note-before-you-consign-the-part-to-jlcpcb
[^jlc-esp]: JLCPCB, część C2913202 ESP32-S3-WROOM-1-N16R8 — https://jlcpcb.com/partdetail/3198300-ESP32_S3_WROOM_1N16R8/C2913202
[^jlc-esp16]: JLCPCB, część C2913199 ESP32-S3-WROOM-1-N16 — https://jlcpcb.com/partdetail/3198297-ESP32_S3_WROOM_1N16/C2913199
[^jlc-w5500]: JLCPCB, część C32843 W5500 — https://jlcpcb.com/partdetail/Wiznet-W5500/C32843
[^jlc-lora-seeed]: JLCPCB, część C5129913 Seeed 317990829 — https://jlcpcb.com/partdetail/Seeed-317990829/C5129913
[^jlc-jst]: JLCPCB, część C157991 JST B5B-XH-A (wg wyniku wyszukiwania) — https://jlcpcb.com/partdetail/JST-B5B_XH_A_LF_SN/C157991
[^jlc-faston]: JLCPCB, część C3217931 Keystone 1212 (wg wyniku wyszukiwania) — https://jlcpcb.com/partdetail/Keystone-1212/C3217931
[^lcsc]: LCSC, strona główna — https://www.lcsc.com/
[^jlc3dp]: JLC3DP, strona główna — https://jlc3dp.com/
[^jlc3dp-jul]: JLC3DP, „Material & Service Price Updates”, obowiązuje od 24.07.2026 — https://jlc3dp.com/news/materials-finishing-pricing-update-july2026
[^jlc3dp-aug25]: JLC3DP, „Major Material Price Cuts…”, 13.08.2025 — https://jlc3dp.com/news/drastic-material-price-cuts-and-adjusted-post-processing-service-fees
[^jlc3dp-316l]: JLC3DP, „316L Stainless Steel”, aktualizacja 08.09.2026 — https://jlc3dp.com/help/article/316l-stainless-steel
[^jlccnc]: JLCCNC, strona główna — https://jlccnc.com/
[^hackclub]: Sygnał (strona trzecia): Hack Club, „JLC Cost optimizing” — https://highway.hackclub.com/guides/JLC-cost-optimizing
[^pw-home]: PCBWay, strona główna — https://www.pcbway.com/
[^pw-4l]: PCBWay, „100x100mm – 4 Layer PCB” — https://www.pcbway.com/pcb_prototype/4_Layer_pcb/
[^pw-2l]: PCBWay, „100x100mm – 2 Layer PCB” — https://www.pcbway.com/pcb_prototype/2_Layer_pcb/
[^pw-asm]: PCBWay, „Surface Mount SMT PCB Assembly Service” — https://www.pcbway.com/pcb-assembly.html
[^pw-asm-cap]: PCBWay, „PCB assembly services / Capabilities” — https://www.pcbway.com/pcb_prototype/PCB_assembly_Capabilities.html
[^pw-quotesmt]: PCBWay, kalkulator montażu (tylko odczyt opisu opcji) — https://www.pcbway.com/quotesmt.aspx
[^pw-qa]: PCBWay, „PCBWay Q&A-004 … PCB Assembly Service”, 22.10.2020 — https://www.pcbway.com/blog/PCB_Basic_Information/PCBWay_Q_A_004___Common_Questions_for_PCB_Assembly_Service_on_PCBWay_02.html
[^pw-3d]: PCBWay, „3D Printing” — https://www.pcbway.com/rapid-prototyping/3d-printing/
[^pw-rp]: PCBWay, „Rapid Prototyping” — https://www.pcbway.com/rapid-prototyping/
[^pw-ship]: PCBWay, „Shipping Method Guide” — https://www.pcbway.com/shipping_method_guide.aspx
[^pw-eu]: PCBWay, „EU Customs Reform 2026…”, 24.06.2026 — https://www.pcbway.com/blog/News/EU_Customs_Reform_2026_End_of_the_150_Duty_Exemption_for_Low_Value_Imports_2ec7a7f4.html
[^pw-customs]: PCBWay, „Do I have to pay for customs and import taxes?”, 2018 — https://www.pcbway.com/helpcenter/Findproducts/Do_I_have_to_pay_for_customs_and_import_taxes_.html
[^pw-express]: PCBWay, „PCBWayExpress — European Exclusive Route Logistic”, 26.10.2020 — https://www.pcbway.com/blog/Activities/PCBWayExpress___European_Exclusive_Route_Logistic.html
[^pw-eu-factory]: PCBWay, „Quick-turn PCB” (wzmianka o fabryce w UE, wg wyniku wyszukiwania) — https://www.pcbway.com/QuickOrderOnline.aspx
[^np-home]: NextPCB, strona główna — https://www.nextpcb.com/
[^np-free]: NextPCB, „First PCB Order Free” — https://www.nextpcb.com/free-pcb-prototype
[^np-disc]: NextPCB, „Empowering Your 2026 Innovation…”, aktualizacja 07.2026 — https://www.nextpcb.com/blog/nextpcb-discount
[^np-proto]: NextPCB, „PCB Prototype Services” — https://www.nextpcb.com/pcb-prototype
[^np-2v4]: NextPCB, „2-Layer or 4-Layer PCB?…”, 04.2026, aktualizacja 06.2026 — https://www.nextpcb.com/blog/2-layer-vs-4-layer-pcb
[^np-asm]: NextPCB, „PCB Assembly Services” — https://www.nextpcb.com/pcb-assembly-services
[^np-prices]: NextPCB, „PCB & PCB Assembly Pricing Policy” — https://www.nextpcb.com/prices
[^np-eu]: NextPCB, „Changes to EU Customs Policy Effective July 1st 2026”, 29.06.2026 — https://www.nextpcb.com/news/eu-customs-reform-2026
[^np-cable]: NextPCB, „Custom Cable Assembly & Wire Harness Manufacturing” — https://www.nextpcb.com/cable-assembly-services
[^ap-home]: ALLPCB, strona główna z komunikatem o zawieszeniu działania — https://www.allpcb.com/
[^sd-fusion]: Seeed Fusion PCB — https://www.seeedstudio.com/fusion_pcb.html
[^sd-price]: Seeed, „Why do Fusion PCB prices fluctuate so much?” — https://support.seeed.cc/portal/en/kb/articles/why-do-fusion-pcb-prices-fluctuate-so-much
[^sd-pcba]: Seeed Fusion PCB Assembly — https://www.seeedstudio.com/pcb-assembly.html
[^sd-wiki]: Seeed Wiki, „Seeed Fusion PCB & PCBA Service Guide”, aktualizacja 16.09.2026 — https://wiki.seeedstudio.com/Service_for_Fusion_PCB/
[^sd-what]: Seeed, „What is Fusion?” — https://support.seeed.cc/portal/en/kb/articles/what-is-fusion
[^sd-3d]: Seeed Fusion 3D Printing (strona starsza, wg wyniku wyszukiwania) — http://www.seeedstudio.com/fusion-3d-printing.html
[^el-home]: Elecrow, strona główna — https://www.elecrow.com/
[^el-pcb]: Elecrow, „PCB manufacturing and PCB prototyping” — https://www.elecrow.com/pcb-manufacturing.html
[^el-special]: Elecrow, „PCB and 3D Printing and Acrylic Laser Cutting Special Promotion” — https://www.elecrow.com/special-offer.html
[^el-proto]: Elecrow, „PCB Prototyping” — https://www.elecrow.com/pcb-prototyping-1.html
[^el-pcba]: Elecrow, „PCB Assembly” — https://www.elecrow.com/pcb-assembly.html
[^el-3d]: Elecrow, „3D Printing Service” — https://www.elecrow.com/3d-printing-service.html
[^el-acr]: Elecrow, „Acrylic Laser Cutting Service” — https://www.elecrow.com/acrylic-cutting.html
[^el-wood]: Elecrow, „5pcs Wood Laser Cutting Service” — https://www.elecrow.com/5pcs-wood-laser-cutting-service.html
[^el-ship]: Elecrow, „Shipping & Returns” — https://www.elecrow.com/shippinginfo
[^el-box]: Elecrow, strona „Box Build & Final Assembly” (błąd 404 przy próbie 18.10.2026) — https://www.elecrow.com/box-build-assembly.html
[^eu-a2m]: Komisja Europejska, Access2Markets, „EU applies €3 customs duty per item on low-value e-commerce consignments”, 30.06.2026 — https://trade.ec.europa.eu/access-to-markets/en/news/eu-applies-eu3-customs-duty-item-low-value-e-commerce-consignments
[^eu-taxud]: Komisja Europejska, DG TAXUD, „Guidance and legal text on temporary flat fee on low-value imports…”, 08.06.2026 — https://taxation-customs.ec.europa.eu/news/guidance-and-legal-text-temporary-flat-fee-low-value-imports-which-will-apply-until-1-july-2028-2026-06-08_en
[^pl-vat1]: biznes.gov.pl, „Jak prawidłowo rozliczyć VAT” — https://www.biznes.gov.pl/pl/portal/00232
[^pl-vat2]: biznes.gov.pl, „Rozliczanie VAT w imporcie towarów” — https://www.biznes.gov.pl/pl/portal/00262
