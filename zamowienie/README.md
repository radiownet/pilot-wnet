# Pilot Wnet Rev A — instrukcja zamówienia (wersja 2, 20.11.2026)

> Przygotował agent SI (Claude) na podstawie audytu gotowości, niezależnej recenzji i kosztorysu z 20.11.2026
> (streszczenie audytu: [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md)).
> **Zamówienie składa człowiek.** Agent niczego nie zamawia, nie zakłada kont, nie wypełnia formularzy i nie wysyła plików do fabryk.
> Wersja 1 z 18.10 opisywała panel KiKit i pliki, których już nie ma — zastąpiona w całości.

## 0. Stan i warunek

- **Zamawiający:** Radio Wnet Sp. z o.o. (decyzja zespołu projektu 20.11.2026 — D11). Zamówienie jako firma: VAT importowy do odliczenia.
- **Rewizja:** Rev A (decyzja zespołu projektu 20.11.2026: montaż przewlekany THT, bez wyświetlacza TFT).
- **Bramka:** decyzje D1–D10 (`../DECYZJE.md`; D11 zatwierdzona) i decyzja o wadach ułożenia płytki (zob. [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md)) —
  przed zamówieniem. Archiwum Gerberów ma w nazwie `NIE_ZAMAWIAC`, dopóki bramka nie zostanie zamknięta.

## 1. Gdzie

**JLCPCB** (jlcpcb.com) — domyślnie. **PCBWay** (pcbway.com) — kontrolna wycena; wybrać, jeśli po przeglądzie wyjdzie
taniej o ponad ok. 30 USD. Ceny i promocje z 20.11: kosztorys poza repozytorium (zob. [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md), rozdz. 11).

## 2. Pliki (pakiet wygenerowany skryptem `pcb/v01/pakiet_zamowienie_v01.py`, poza repozytorium)

| Plik | JLCPCB | PCBWay |
|---|---|---|
| `pilot_wnet_v0.1_gerber_NIE_ZAMAWIAC.zip` — Gerbery + wiercenia, pojedyncza płytka 90 × 100 mm | ✔ | ✔ |
| `jlcpcb\bom_jlcpcb_v0.1.csv` — BOM (Comment, Designator, Footprint, LCSC Part #), bez DNP | ✔ | — |
| `jlcpcb\cpl_jlcpcb_v0.1.csv` — pozycje **z korektami obrotu i środka dla biblioteki JLC** | ✔ | **NIE** |
| `pcbway\bom_pcbway_v0.1.csv` — BOM po angielsku (MPN, producent, Type SMD/THT; zamienniki tylko 1:1) | — | ✔ |
| `pcbway\dnp_reference_v0.1.csv` — elementy niemontowane, tylko informacyjnie (nie do zakupu) | — | ✔ |
| `pcbway\cpl_pcbway_v0.1.csv` — pozycje w konwencji KiCada (bez korekt JLC) | **NIE** | ✔ |
| `pcbway\montaz_gora.pdf` — rysunek montażowy (oznaczenia, DNP przekreślone) | opcjonalnie | ✔ |
| `pcbway\ORDER_NOTES_PCBWAY.txt` — uwagi do wklejenia w zamówienie | — | ✔ |
| `pcbway_promocja_29usd\` — to samo, ale J19/J20 niemontowane (pod promocję montażu 29 USD) | — | ✔ (wariant) |
| `pozycje_dnp_reczne_v0.1.csv` — pozycje elementów DNP do późniejszego lutowania ręcznego | — | — |

Pliki tworzy `pcb/v01/eksport_v01.py` (kicad-cli) i `pcb/v01/pakiet_zamowienie_v01.py` (BOM z MPN:
`pcb/v01/bom_v0.1_mpn_zamienniki.csv`); korekty CPL: `pcb/v01/korekty_jlc.py`.

## 3. JLCPCB — krok po kroku

**Płytka:** warstwy 4 · wymiar 90 × 100 mm · ilość 5 · grubość 1,6 mm · kolor zielony, opis biały · wykończenie
LeadFree HASL (OSP jest bez dopłaty, ale dla 3 gołych płytek lutowanych później ręcznie lepszy HASL) · miedź zewnętrzna
1 oz (D7), wewnętrzna 0,5 oz — domyślna JLC i wystarczająca w normalnej pracy; 1 oz tylko przy symbolicznej dopłacie
(zapas przy zwarciu w wiązce +5 V, audyt SI kryt-03 — zob. [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md); plik `.gbrjob` z KiCada podaje 0,035 mm, ale fabryka bierze stos
wybrany w zamówieniu) · stos warstw: domyślny JLC, bez kontroli impedancji · przelotki: tented (zakryte maską) ·
„Confirm Production file”: Yes.

**Montaż (PCBA):** typ **Standard** (moduł ESP32-S3 C2913202 jest „Standard Only”, z RTG) · strona Top · ilość 2 ·
**Edge rails / fiducials: Added by JLCPCB** i w uwagach: „Rails on LEFT and RIGHT edges only (100 mm sides), mouse-bites,
no V-cut — J1, J2 and U1 overhang the top edge. Please hand-solder the 4 through-hole shell pins of J1 (USB-C).
U1 and U4 are MSL 3.” · **Confirm Parts Placement: Yes** (0,45 USD; inżynier przysyła podgląd do akceptacji przed
lutowaniem). Jeśli fabryka zapyta o pastę na padach elementów niemontowanych: „use supplied paste layer” (pasta
jest z nich zdjęta celowo). ESP32-S3-WROOM-1 ma kod eksportowy ECCN 5A992.c — fabryka może poprosić o deklarację.

**BOM i CPL:** wgrać `jlcpcb\bom_jlcpcb_v0.1.csv` i `jlcpcb\cpl_jlcpcb_v0.1.csv`. Sprawdzić, że wszystkie 43 pozycje
mają część na stanie (D2 = C12065). W podglądzie rozmieszczenia sprawdzić (ok. 20 min):
1. kropkę nóżki 1 korpusu przy znaczniku nóżki 1 na płytce: U2, U3, U4, U7, U10, U11, U12;
2. pokrycie wszystkich padów: U1 (ESP32), J1 (USB-C), J2 (RJ45);
3. zatrzaski gniazd JST XH J10–J16 zgodnie z rysunkiem `pcbway\montaz_gora.pdf`;
4. katody D1, D2; pobieżnie elementy bierne.
Jeśli coś się nie zgadza — poprawić w podglądzie (obrót/przesunięcie) i opisać to w zgłoszeniu (issue).

**Wysyłka i podatki:** DHL Express z DDP (VAT i opłata przewoźnika przy zamówieniu) albo bez DDP (VAT i opłata DHL
przy doręczeniu). Dane: **Radio Wnet Sp. z o.o.**, NIP w adresie i na fakturze. **Nie wybierać „Global Standard
Direct Line”** (JLC traktuje ją zawsze jako sprzedaż dla osoby prywatnej). Kupon: jeden na zamówienie — sprawdzić
w Coupon Center (miesięczny SMT, Black Friday do 2.12.2026, pakiet nowego klienta, jeśli spółka nie ma konta).

## 4. PCBWay — krok po kroku

Płytka: te same parametry co w JLC (4 warstwy, 90 × 100, 5 szt., 1,6 mm, HASL bezołowiowy, zielona, ścieżka 5/5 mil).
Montaż: turnkey, 2 szt., Top. Wybrać JEDEN z dwóch gotowych zestawów i wgrać z niego `bom_pcbway_v0.1.csv`,
`cpl_pcbway_v0.1.csv`, `montaz_gora.pdf` (i ewentualnie `dnp_reference_v0.1.csv` jako informację), a treść
`ORDER_NOTES_PCBWAY.txt` wkleić w uwagi:
- `pcbway\` — J19 i J20 (listwy 1×6) lutuje fabryka (118 lutów THT na 2 płytki);
- `pcbway_promocja_29usd\` — pod promocję montażu 29 USD (≤ 100 lutów THT na zamówienie): J19 i J20 niemontowane,
  usunięte z BOM i CPL, w uwagach na liście DNP (94 luty THT); listwy 1×6 lutujemy sami.
Poprosić o zdjęcia pierwszej płytki do akceptacji. Zamienniki: tylko te z kolumny Alternate (sprawdzone 1:1), inne
wymagają naszej zgody (pkt 6 uwag).

## 5. Części kupowane osobno (nie z fabryki płytek) — bez zmian względem wersji 1

E22-900M22S ×2 (+1) z przewodem IPEX→SMA i anteną 868 MHz ≤ 3 dBi; OLED 1,3″ I2C z przewodem Qwiic; joystick Sanwa
JLX2-TP-8YT (+ LB-35, JLF-P1, wiązka JLF-H); przyciski Sanwa OBSC-30 (×4 kolory), OBSC-24 (START), OBSF-30 (STOP);
wiązki JST XH ↔ Faston 2,8 mm — **tylko na pinach 1–2 gniazd przycisków (pin 3 = +5 V, tor LED jest DNP;
audyt SI produkt-15 — zob. [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md))**; śruby, dystanse M3 × 8, wkładki M4; kabel USB-C i Ethernet Cat5e.
Blachy, pleksi i wydruków 3D **nie** dołączać do paczki z płytkami przed pomiarami próbek (audyt SI produkt-17 — zob. [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md)).

## 6. Przed zamówieniem — lista kontrolna (HITL)

1. D1–D10 zatwierdzone (D11 — 20.11); decyzja o wadach ułożenia (zob. [`docs/AUDYT_REV_A.md`](../docs/AUDYT_REV_A.md)).
2. Pakiet wygenerowany z zatwierdzonego commitu (DRC 0 błędów, 0 niepołączonych; ERC 0 błędów).
3. Podgląd DFM i montażu w fabryce (pkt 3), stany części w dniu zamówienia.
4. Dwie wyceny na tych samych plikach (JLCPCB, PCBWay), ten sam zamawiający.
5. Procedura pierwszego uruchomienia: zasilacz z ograniczeniem prądu albo miernik USB, esptool.
6. Zgodność radiowa (RED) i próba w studiu przed użyciem na antenie.
