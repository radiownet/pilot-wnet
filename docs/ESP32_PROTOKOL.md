# Fizyczny pilot: protokół ESP32 i czytnik

> Implementacja hosta (aplikacja na komputer studyjny) nie jest (jeszcze) publiczna. Ten dokument opisuje ramkę, sesję, transporty i parowanie oraz zachowanie, którego host wymaga od pilota. Firmware pilota leży w [`firmware/micropython/`](../firmware/micropython/).

Stan na 12.11.2026: Pilot Wnet ma czytnik fizycznego pilota. Są w nim sesja z HELLO i nonce, kontrola każdej ramki, transport UDP (Wi‑Fi albo Ethernet) i odczyt raportów USB HID. Samego urządzenia jeszcze nie ma. Dlatego strona komputera jest sprawdzona emulatorem na pętli zwrotnej (127.0.0.1), a USB i sieć z prawdziwą płytką czekają. Co zostało zmierzone, a co jest założeniem, mówi tabela „Sprawdzone / założone” niżej.

Czytnik jest domyślnie wyłączony. Bez sekcji `[esp32]` z `transport` innym niż `wylaczony` Pilot nie otwiera gniazda ani urządzenia.

Panel ekranowy i fizyczny pilot dają te same zdarzenia, bo oba źródła trafiają do tej samej maski przełączników. Ramki pilota wchodzą jako jedno źródło (HID), niezależnie od tego, czy przyszły po USB, czy po UDP.

## Ramka

32 bajty, little-endian:

```
bajt   pole    typ   znaczenie
0      ver     u8    1
1      flagi   u8    bit1 = heartbeat (ramka podtrzymania, maska bez zmian)
2..4   dev_id  u16   identyfikator pilota (jeden pilot = jeden klucz)
4..8   seq     u32   numer ramki, ściśle rosnący w sesji
8..10  maska   u16   10 bitów: R Y B G START STOP ▲ ▼ ◄ ►
10..14 dev_ms  u32   zegar urządzenia w ms (do pomiaru opóźnień)
14..16 crc16   u16   CRC-16/CCITT-FALSE z bajtów 0..14
16..32 hmac    16 B  HMAC-SHA256(klucz, bajty 0..16 ‖ nonce_hosta u32), obcięty do 16 bajtów
```

Pilot wysyła ramkę przy każdej zmianie maski i co 1 s ramkę podtrzymania. Każda ramka niesie pełną maskę, więc zgubione puszczenie przycisku naprawia następna ramka.

Host (Pilot Wnet) odrzuca ramkę i nie wykonuje żadnej akcji, gdy:

| Licznik w dzienniku | Kiedy |
|---|---|
| `limit` | w ostatniej sekundzie do kontroli przeszło już 50 ramek (okno przesuwne; liczy się każda ramka, także zła) |
| `dlugosc`, `wersja` | zła długość albo wersja |
| `crc` | uszkodzona ramka |
| `hmac`, `brak_klucza` | zły podpis albo brak klucza |
| `stary_nonce` | podpis poprawny, ale z nonce poprzedniej sesji (powtórka nagrania) |
| `inne_urzadzenie` | `dev_id` inny niż sparowany |
| `powtorka` | `seq` nie większy niż ostatni przyjęty |
| `obcy_adres` | datagram UDP spoza adresu pilota z konfiguracji (nie jest nawet parsowany) |

Kolejność kontroli: adres nadawcy, limit, długość, wersja, CRC, HMAC, `dev_id`, numer. Limit stoi przed HMAC celowo: zalew kończy się odrzuceniem nadmiaru bez liczenia skrótów.

## Sesja

1. Pilot Wnet losuje nonce (generator systemowy, 32 bity) i wysyła pilotowi HELLO: `PWN1` + nonce u32 LE, razem 8 bajtów. Po UDP to datagram na adres pilota, po USB raport wyjściowy.
2. Pilot zaczyna numerację ramek od 1 i podpisuje je tym nonce. Dopóki nie przyjdzie pierwsza poprawna ramka, HELLO idzie ponownie co 1 s.
3. Każda poprawna ramka, także podtrzymanie, przedłuża sesję.
4. Brak poprawnej ramki przez 2,5 s kończy sesję. Pilot Wnet zwalnia wtedy wszystkie przełączniki tego źródła, losuje nowy nonce i wysyła nowe HELLO. Dzięki temu urwany kabel albo zerwane połączenie radiowe nie zostawiają „wciśniętego” NIEBIESKIEGO, a ramka nagrana w jednej sesji nie zadziała w następnej.
5. Przyciski trzymane w chwili zestawienia sesji nie działają, dopóki nie zostaną puszczone. Powrót łącza przy trzymanym NIEBIESKIM nie wznawia dyktowania, a zacięty przycisk nie uruchamia niczego przy starcie.

Zwolnienie po ciszy działa jak puszczenie przycisku. Przy NIEBIESKIM oznacza to koniec dyktowania i wpisanie tekstu bez Entera; Enter nadal wymaga START (reguła bezpieczeństwa hosta).

HELLO nie jest podpisany. Podrobiony HELLO może zerwać sesję (pilot zacznie podpisywać cudzym nonce, a host odrzuci ramki i po 2,5 s wyśle własny), ale nie da się nim wywołać akcji. Złe ramki nie podtrzymują sesji: zalew śmieci przy milczącym pilocie i tak kończy się zwolnieniem po 2,5 s.

### Blokada ekranu

Fizyczny pilot nie może więcej niż pilot-klawiatura. Przy zablokowanym ekranie i na pulpicie bezpiecznym (UAC, Ctrl+Alt+Del) Windows nie dostarcza Pilotowi klawiszy F13–F22, ale ramki z sieci przychodziłyby dalej. Dlatego w takim stanie z wciśnięć fizycznego pilota przechodzi tylko STOP. Puszczenia przechodzą wszystkie. Nagrania nie da się więc zacząć ani potwierdzić pilotem przy zablokowanym ekranie, a zatrzymać da się zawsze.

## Czytnik po stronie hosta

Czytnik w niepublicznej aplikacji hosta składa się z tych części:

- ramka: CRC, HMAC, kodowanie; kontrola numeru, limitu w oknie przesuwnym i maski;
- sesja: HELLO, nonce, cisza 2,5 s, blokada przycisków trzymanych przy starcie, liczniki odrzuceń (czysta logika bez gniazd i zegara);
- UDP: wątek z gniazdem, jeden adres nasłuchu, jeden adres pilota;
- USB HID: raporty przez Raw Input (`WM_INPUT`), HELLO raportem wyjściowym;
- plik klucza parowania i losowanie nonce;
- emulator urządzenia na pętli zwrotnej.

```
UDP:  gniazdo → wątek esp32-udp → czytnik (limit, HMAC, nonce, numer, cisza) → skrzynka → wątek UI
USB:  WM_INPUT → okno → wątek UI → czytnik → …
dalej wspólnie: przełączniki (źródło HID) → akordy → automat → polecenia
```

Do wątku UI po UDP docierają tylko zdarzenia po weryfikacji. Raporty USB weryfikuje ten sam czytnik w wątku UI, bo Raw Input dostarcza je do okna.

## Konfiguracja hosta

```toml
[esp32]
transport = "udp"              # "wylaczony" (domyślnie) | "udp" | "usb_hid"
dev_id = 1                     # jak dev_id w pilot_konfig.json urządzenia
plik_klucza = '%LOCALAPPDATA%\PilotWnet\esp32_klucz.hex'
nasluch = "192.168.1.20:47231" # adres interfejsu komputera studyjnego i port; nigdy 0.0.0.0
pilot = "192.168.1.77:47231"   # adres pilota i jego udp.port_lokalny
# usb_vid = 0x0000             # USB HID: oba wymagane przy transport = "usb_hid"
# usb_pid = 0x0000
```

Host odrzuca konfigurację, gdy `nasluch` albo `pilot` nie jest adresem IPv4 z portem z sieci prywatnej (RFC 1918), link-local (169.254/16) albo pętli zwrotnej (odpadają 0.0.0.0, adresy publiczne, rozgłoszeniowe, grupowe i zakres 100.64/10), gdy port nasłuchu jest niższy niż 1024, gdy tylko jeden z adresów jest pętlą zwrotną, gdy `plik_klucza` leży poza `%LOCALAPPDATA%\PilotWnet\`, gdy `transport = "usb_hid"` nie ma `usb_vid` albo `usb_pid` (stronę użycia 0xFF00 mają też inne urządzenia, a HELLO to raport wyjściowy, więc bez identyfikatorów mogłoby trafić do obcego sprzętu) i gdy w sekcji jest pole spoza listy, także `klucz` — klucza nie da się wpisać do TOML.

Gdy brakuje pliku klucza albo port jest zajęty, Pilot startuje normalnie, a czytnik zostaje wyłączony. Powód jest w dzienniku (`esp32_blad`) i na panelu.

Port 47231 jest roboczy, taki sam jak `PORT_UDP` w firmware. Regułę zapory dla niego zakłada administrator komputera studyjnego po przeglądzie bezpieczeństwa.

## Dziennik hosta

Host zapisuje w dzienniku start czytnika (`esp32_start`), początek i koniec sesji z powodem i czasem bez ramki (`esp32_sesja`), zwolnienie przełączników źródła (`esp32_zwolnienie`), wciśnięcia pominięte przy zablokowanym ekranie (`esp32_blokada`), odrzucone ramki z licznikami z tabeli w rozdziale „Ramka” (`esp32_odrzut`, zbiorczo, najwyżej raz na sekundę), błędy gniazda, urządzenia albo startu (`esp32_blad`, ten sam błąd najwyżej raz na minutę) oraz podłączenie albo odłączenie pilota USB (`esp32_urzadzenie`). Wpisy nie zawierają treści ramek, klucza, nonce ani adresów spoza konfiguracji.

## Transporty

| Transport | Kodowanie | Opóźnienie (szacunek) | Stan w Pilocie Wnet |
|---|---|---|---|
| USB HID producenta | raport 32 B, strona użycia `0xFF00` (ang. vendor-defined), użycie `0x01` | 1–3 ms | Odczyt przez Raw Input i HELLO przez `HidD_SetOutputReport` napisane, **niesprawdzone na urządzeniu**. Domyślny i zalecany: pilot nie jest klawiaturą, więc nie może wpisywać tekstu w system (ochrona przed BadUSB). Windows obsługuje go bez sterownika. |
| Wi‑Fi albo Ethernet (UDP) | datagram 32 B | 2–20 ms | Działa i jest sprawdzony emulatorem na 127.0.0.1. Z płytką niesprawdzony. Jeden interfejs, jeden adres pilota. |
| USB CDC (port szeregowy) | COBS z separatorem `0x00` | 1–3 ms | Tylko kodek COBS. Zapas dla płytek bez natywnego HID. |
| Bluetooth LE | charakterystyka GATT z powiadomieniami | 8–45 ms | Brak po stronie Pilota Wnet. Wiązanie LE Secure Connections; klucz HMAC wgrywany wyłącznie przez USB, nigdy przez radio. |

Opóźnienia są szacunkami z typowych parametrów transportów (okres odpytywania USB 1 ms, interwał połączenia BLE 7,5–45 ms). Zmierzone zostaną dopiero na prawdziwej płytce.

Naraz działa jeden transport. Firmware umie wysyłać tę samą ramkę kilkoma łączami, ale Pilot Wnet słucha tylko tego z konfiguracji.

## Próba na pętli zwrotnej (emulator hosta)

Emulator w aplikacji hosta gra rolę urządzenia: czeka na HELLO, zaczyna numery od 1, wysyła podtrzymanie co sekundę. Działa wyłącznie na 127.0.0.1, wysyła tylko START i kierunki joysticka (nigdy kolory ani STOP) i nie wypisuje klucza. Nie wstrzykuje klawiszy ani myszy: jego jedynym wyjściem są datagramy UDP do hosta. Scenariusz pełny obejmuje poprawne ramki, złe ramki (przekłamany podpis, obcy klucz, podmieniona maska, poprawnie podpisana ramka z innego gniazda), powtórkę, zalew 500 ramek naraz, ciszę przy trzymanym START, ramki ze starej sesji i odzysk w nowej sesji. W całym przebiegu akcja START ma wystąpić dokładnie 4 razy; każda dodatkowa oznaczałaby, że przeszła zła ramka.

Wynik próby z 12.11.2026, godz. 21:30 (host w trybie próbnym, bez skutków; emulator jako osobny proces): START 4 razy, odrzuty `hmac 3` i `obcy_adres 1`, `powtorka 3`, `limit 451`, `stary_nonce 5`; koniec sesji po 2501 ms bez ramki, zwolnienie w wątku UI po 0,08 ms; nowe HELLO dotarło do emulatora po 2501 ms. Host słuchał tylko na 127.0.0.1:47231.

## Sprawdzone / założone

Stan na 12.11.2026, komputer studyjny, build debug. „Sprawdzone” znaczy: jest test albo pomiar, który można powtórzyć. Testy hosta nie są (jeszcze) publiczne.

| Co | Stan | Jak |
|---|---|---|
| Ramka bajt w bajt zgodna z firmware | sprawdzone | wspólny wektor testowy: [`firmware/micropython/testy/test_pilot_ramka.py`](../firmware/micropython/testy/test_pilot_ramka.py) (implementacja hosta niepubliczna) |
| HELLO zgodne z firmware (`PWN1` + nonce LE; raport USB 9 B z zerem na początku) | sprawdzone na poziomie bajtów | testy hosta i firmware; z urządzeniem nie |
| Zły HMAC, obcy klucz, podmieniona maska nie dają akcji | sprawdzone | testy hosta na prawdziwych gniazdach; próba z emulatorem |
| Nonce sesji: ramka z innej sesji odrzucona | sprawdzone | testy hosta; próba z emulatorem |
| Najwyżej 50 ramek na sekundę | sprawdzone | test hosta; na gniazdach: z 600 ramek w 90 ms przeszło 49 (pięćdziesiątą była ramka otwierająca sesję) |
| Cisza 2,5 s zwalnia przełączniki | sprawdzone | czysta logika: dokładnie 2500 ms; na gniazdach: 2500–2501 ms w 6 pomiarach (kryterium 2600 ms) |
| Pozostałe kontrole hosta: zwolnienie dociera do automatu (puszczony NIEBIESKI), dziennik odrzutów bez treści, nasłuch tylko na adresie z konfiguracji, start USB HID bez urządzenia | sprawdzone | testy i próba hosta; testy pilnują reguł: każdą z 9 celowych usterek w kodzie hosta (wyłączony HMAC, limit, kontrola numeru, cisza późniejsza o 200 ms, stary nonce w nowej sesji, obcy adres, obcy `dev_id`, brak blokady startowej, brak zwolnienia) wykrył co najmniej jeden test |
| Opóźnienie na pętli zwrotnej: datagram → zdarzenie dla aplikacji | sprawdzone | test hosta: p50 0,14–0,15 ms, p99 0,22–0,37 ms (3 przebiegi po 100 ramek) |
| USB HID: raporty z urządzenia (rozmiar 33 B z zerem na początku), `HidD_SetOutputReport`, powiadomienia o podłączeniu | **założone** | napisane według dokumentacji Windows i `pilot_hid.py`; bez urządzenia nie da się sprawdzić |
| USB HID: identyfikatory VID/PID | **założone** | firmware używa wbudowanej pary MicroPythona; własnej nie ma. Trzeba je odczytać z płytki i wpisać do `[esp32]` |
| Blokada ekranu przepuszcza z pilota tylko STOP | częściowo | test funkcji w hoście; na zablokowanym ekranie nie próbowane (komputer studyjny pracuje) |
| Pilot wysyła ramki z portu `udp.port_lokalny` (host sprawdza adres i port nadawcy) | **założone** | wynika z `pilot_transport.py`; na płytce niesprawdzone |
| Pierwsza ramka po HELLO przychodzi w ciągu 1 s | **założone** | wynika z `heartbeat_ms` w firmware; gdyby trwało ponad 2,5 s, sesja by się nie zestawiła |
| Opóźnienia na prawdziwym łączu, utrata pakietów Wi‑Fi | **założone** | zob. „Pomiar opóźnień” |
| Reguła zapory Windows dla portu UDP | nie ma | zakłada administrator komputera studyjnego po przeglądzie bezpieczeństwa |
| Parowanie (wgranie klucza na urządzenie) | nie ma | plan niżej |

## Zalecana płytka

ESP32‑S3: ma natywne USB (HID i CDC bez osobnego mostka), Bluetooth LE i Wi‑Fi. Unikamy płytek z mostkami CP210x i CH34x, które wymagają sterowników. Konkretny model i jego parametry trzeba sprawdzić u producenta przed zakupem [DO WERYFIKACJI].

Własna płytka tego repozytorium (Rev A) jest opisana w [`pcb/README.md`](../pcb/README.md), a obudowa arcade w [`projekt/arcade.toml`](../projekt/arcade.toml).

## Parowanie (plan, w większości niezaimplementowane)

1. Pilot Wnet generuje klucz HMAC (32 bajty) i zapisuje go w profilu użytkownika, poza repozytorium. **To już działa** w aplikacji hosta: polecenie tworzy plik z `esp32.plik_klucza`, nie nadpisuje istniejącego i nie wypisuje klucza.
2. Klucz trafia do pilota wyłącznie kablem USB, jako `klucz_hmac_hex` w `pilot_konfig.json` na urządzeniu. Dziś to krok ręczny (`mpremote cp`).
3. Od tej chwili ramki bez poprawnego HMAC są ignorowane na każdym transporcie.

## Pomiar opóźnień

Każda ramka niesie `dev_ms`. Pilot Wnet notuje czas odbioru (QPC) i może policzyć dwie rzeczy:

- **dryf zegarów**: różnica `dev_ms` i czasu hosta na ramkach podtrzymania, wygładzona w czasie;
- **opóźnienie zdarzenia**: czas odbioru ramki ze zmianą maski minus oczekiwany czas hosta dla jej `dev_ms`.

Dziś host mierzy tylko drogę od gniazda do polecenia. Dryf i opóźnienie zdarzenia z `dev_ms` nie są jeszcze liczone, bo bez urządzenia nie ma czego mierzyć.

Do kalibracji bezwzględnej: dioda na pilocie zapala się przy wysłaniu ramki, a kamera albo fotodioda przy ekranie rejestruje zmianę na panelu. Różnica obejmuje wtedy także rysowanie i DWM.
