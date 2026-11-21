# Firmware płytki Pilot Wnet Rev A

Płytka: ESP32‑S3‑WROOM‑1‑N16R8 (16 MB flash, 8 MB PSRAM Octal), W5500 (Ethernet), Ebyte E22‑900M22S (LoRa 868 MHz, montaż ręczny), OLED na I2C. Przydział pinów: `micropython/lib/konfig_plytki.py`, przepisany z `../pcb/obwod.py` (test `test_konfig_plytki.py` porównuje oba pliki).

Ta sama płytka ma dwie role, wybierane wgraniem innego obrazu przez USB (R3, rozdz. 3):

| Rola | Katalog | Stan |
|---|---|---|
| **Pilot** (ramki do komputera studyjnego: USB HID, Ethernet UDP, BLE) | `micropython/` | kod i testy na atrapach; na płytce nieuruchamiany |
| Węzeł Meshtastic® | `meshtastic/variants/esp32s3/diy/pilot_wnet/` | szkic wariantu; niebudowany |
| Węzeł MeshCore | `meshcore/platformio_pilot_wnet.ini` | szkic środowiska; niebudowany |
| Budowa obu wariantów mesh | `ci/build-mesh.yml` | szkic GitHub Actions; nieuruchamiany, poza `.github/workflows` |

## Mapa `micropython/`

| Plik | Co robi |
|---|---|
| `boot.py` | wyłącza Wi‑Fi, rejestruje USB HID obok REPL (`builtin_driver=True`); BOOT naciśnięty w oknie 0,7 s po resecie (dioda świeci) = tryb serwisowy |
| `main.py` | uruchamia `pilot_aplikacja.start()`, chyba że tryb serwisowy |
| `lib/konfig_plytki.py` | tabela pinów Rev A, stałe I2C/SPI, napięcie TCXO jako parametr, `sprawdz()` (PSRAM 33–37, powtórzenia, piny niewyprowadzone) |
| `lib/pilot_konfig.py` | konfiguracja z `/pilot_konfig.json`, walidacja, klucz HMAC |
| `lib/pilot_aplikacja.py` | pętla asyncio: piny co 1 ms → `Wejscia` → `Planista` → `Nadajnik` (osobny na każde łącze) → transporty; dioda stanu |
| `lib/pilot_hid.py` | HID producenta: strona użycia `0xFF00`, raport wejściowy 32 B (ramka), wyjściowy 8 B (HELLO) |
| `lib/pilot_eth.py` | W5500 przez `network.LAN`, DHCP, adres statyczny, link‑local 169.254.x.y |
| `lib/pilot_lora.py` | SX1262 (`lora-sx126x`) z ogranicznikiem zgodności z decyzją (UE) 2025/105 |
| `lib/pilot_ramka.py`, `pilot_wejscia.py`, `pilot_planista.py`, `pilot_transport.py` | protokół v1, wejścia, planista, transporty UDP/BLE (wcześniejsze moduły) |
| `pilot_konfig.przyklad.json` | szablon konfiguracji **bez wartości tajnych** |
| `testy/` | testy w CPythonie z atrapami `machine`, `network`, `bluetooth`, `usb`, `lora` (`testy/atrapy.py`) |

Testy (z katalogu `micropython/`, każdy plik osobno, bez sprzętu):

```
for %f in (testy\test_*.py) do python -I -B -X utf8 %f
```

## 1. Wgranie MicroPythona

Obraz: **ESP32_GENERIC_S3, wariant SPIRAM_OCT, v1.29.0 (24.08.2026)** ze strony https://micropython.org/download/ESP32_GENERIC_S3/ — plik `ESP32_GENERIC_S3-SPIRAM_OCT-20260824-v1.29.0.bin`. Strona nie publikuje sum kontrolnych (sprawdzone 18.10.2026). Po pobraniu policz SHA‑256 (`certutil -hashfile <plik> SHA256`) i zapisz ją przy notatce z wgrania, żeby kolejne płytki dostały ten sam obraz.

esptool z oficjalnego źródła (PyPI `esptool`, Espressif). Na komputerze studyjnym nie instalujemy narzędzi — wgrywa człowiek na swojej maszynie albo na maszynie roboczej, w osobnym środowisku wirtualnym Pythona (venv).

Tryb pobierania: przytrzymaj **BOOT** (SW2, GPIO0) i podłącz USB albo naciśnij reset (EN na złączu serwisowym J20). GPIO46 ma rezystor do masy, więc USB‑Serial/JTAG zgłosi się jako port COM. START (GPIO42) nie wpływa na rozruch (DECYZJE D9).

```
esptool --chip esp32s3 --port COM7 erase-flash
esptool --chip esp32s3 --port COM7 --baud 460800 write-flash 0 ESP32_GENERIC_S3-SPIRAM_OCT-20260824-v1.29.0.bin
```

Starsze esptool (v4) używają zapisu `esptool.py … erase_flash` i `write_flash` — tak podaje strona MicroPythona. Numer portu (`COM7`) sprawdź w Menedżerze urządzeń.

## 2. Biblioteki i pliki pilota (mpremote)

`mpremote` (PyPI, projekt MicroPython). `mpremote mip install` pobiera pakiety micropython-lib na komputerze i kopiuje je przez USB do `/lib` na płytce — płytka nie potrzebuje sieci.

```
mpremote connect COM7 mip install usb-device-hid
mpremote connect COM7 mip install aioble
mpremote connect COM7 mip install lora-sync lora-sx126x
mpremote connect COM7 fs cp -r lib :
mpremote connect COM7 fs cp boot.py main.py :
```

Wersje sprawdzone w kodzie (micropython-lib `master`, commit `90028be0829c6e988b5e239b28f39fb91b6b20e2`, 18.10.2026): `usb-device-hid` 0.2.0, `lora-sx126x` 0.1.6. `pilot_hid.PilotHID.desc_cfg` powtarza logikę klasy bazowej `HIDInterface` — po aktualizacji pakietu porównaj obie metody.

## 3. Konfiguracja

1. Skopiuj `pilot_konfig.przyklad.json` **poza repozytorium** jako `pilot_konfig.json` (plik jest w `.gitignore`).
2. Wpisz `dev_id` i `klucz_hmac_hex` (32 bajty = 64 znaki hex). Docelowo klucz generuje Pilot Wnet na komputerze studyjnym i trzyma w profilu użytkownika (`../docs/ESP32_PROTOKOL.md`, „Parowanie”; implementacja hosta, czyli aplikacja na komputer studyjny, nie jest jeszcze publiczna). Do czasu wdrożenia parowania: klucz wygenerowany lokalnie (`python -c "import secrets; print(secrets.token_hex(32))"`), zapisany w profilu użytkownika, nigdy w gicie, w czacie ani w notatkach.
3. Wgraj wyłącznie kablem USB: `mpremote connect COM7 fs cp pilot_konfig.json :pilot_konfig.json`, potem reset (`mpremote reset`).

Najważniejsze pola:

| Pole | Domyślnie | Uwagi |
|---|---|---|
| `transporty` | `["usb_hid"]` | także `eth_udp`, `wifi_udp`, `ble` — ramka idzie na każde łącze z uzgodnioną sesją |
| `eth.wlaczony`, `eth.tryb` | `false`, `dhcp` | `statyczny` wymaga `eth.adres`; bez DHCP po `dhcp_czekaj_ms` adres link‑local |
| `eth.mac` | pusty | pusty = MAC z eFuse ESP32‑S3 (adres bazowy + 3, ESP‑IDF v6.1) [DO WERYFIKACJI na płytce] |
| `udp.host`, `udp.port`, `udp.port_lokalny` | —, 47231, 47231 | adres i port komputera studyjnego; HELLO przyjmowane tylko od niego. Gniazdo pilota jest przypięte do `adres_interfejsu:port_lokalny` — host wysyła HELLO właśnie tam (pilot przed HELLO nic nie nadaje, więc host musi znać adres pilota: statyczny albo z DHCP) |
| `wifi.wlaczone` | `false` | w studiu Wi‑Fi wyłączone (R5, rozdz. 5.1); `boot.py` wyłącza je zawsze przy starcie |
| `lora.wlaczona` | `false` | pilot sam niczego nie nadaje; obiekt `PilotLoRa` jest dla aplikacji |
| `lora.tcxo_mv` | `null` → 1800 | 1,8 V (Meshtastic) albo 2,2 V (Ebyte V1.5) — [DO WERYFIKACJI w karcie partii] |
| `lora.zysk_anteny_dbi`, `straty_db`, `zapas_db` | 3,0 / 0,0 / 1,0 | wchodzą do limitu mocy e.r.p.; zysk z karty kupionej anteny [DO WERYFIKACJI] |
| `watchdog_ms` | 0 | 0 = wyłączony; na ESP32 WDT nie da się zatrzymać, więc włączać dopiero w egzemplarzu studyjnym |

Ethernet prosto do komputera studyjnego: W5500 nie ma auto‑MDIX (karta W5500, R3 rozdz. 4.4). Kabel prosty zadziała, jeśli karta sieciowa po drugiej stronie ma auto‑MDIX; inaczej kabel skrzyżowany albo przełącznik. Przy kablu bezpośrednim najprościej: adresy statyczne po obu stronach (np. pilot 192.168.77.2, komputer studyjny 192.168.77.1 — [ROBOCZE]). Link‑local działa także, ale komputer studyjny (APIPA) i pilot losują adresy, więc `udp.host` trzeba wtedy znać z góry. Regułę zapory dla UDP 47231 zakłada zespół projektu na komputerze studyjnym (zasady bezpieczeństwa hosta opisuje dokumentacja aplikacji na komputer studyjny, która nie jest jeszcze publiczna).

## 4. Działanie

- **Dioda stanu (GPIO38):** szybkie miganie 5 Hz = błąd konfiguracji albo brak klucza (nic nie jest wysyłane); krótki błysk co 2 s = brak sesji; przy sesji zgaszona i błysk 40 ms przy każdej ramce zmiany (kalibracja opóźnień kamerą).
- **USB:** urządzenie złożone — port szeregowy z REPL (wbudowany CDC) i HID producenta. Host wysyła HELLO raportem wyjściowym 8 B (`PWN1` + nonce u32 LE; w Windows bufor 9 B z bajtem 0 = 0x00, bo deskryptor nie ma ID raportów), pilot odpowiada ramkami 32 B w raportach wejściowych co najwyżej co 1 ms. VID/PID zostają wbudowane w MicroPythona — własnej pary nie mamy [DO WERYFIKACJI przed serią]; host powinien rozpoznawać pilota po stronie użycia `0xFF00` i nazwie produktu.
- **Tryb serwisowy:** po resecie dioda stanu świeci ok. 0,7 s — naciśnięcie BOOT w tym czasie → bez HID i bez pętli, sam REPL. BOOT trzymany już w chwili resetu to tryb pobierania ROM (GPIO0 jest pinem strapping), więc wtedy `boot.py` się nie wykona. Ctrl‑C w REPL przerywa też zwykłą pętlę.
- **LoRa:** `PilotLoRa` odmawia konfiguracji poza pasmami 46a, 47, 48, 50, 54, 56b (kanał musi mieścić się w całości w jednym paśmie), mocy ponad limit e.r.p. pasma i nadawania ponad cykl pracy w kroczącym oknie 1 h (0,1 % / 1 % / 10 %). Limit liczony od startu — po odłączeniu zasilania licznik zaczyna od zera (`Limiter.stan()` / `przywroc()` do przechowania w pamięci RTC). Surowe LoRa z MicroPythona nie rozmawia z sieciami Meshtastic ani MeshCore (R3, rozdz. 7.2).

## 5. Ograniczenia

**Atrapa nie zastępuje próby na sprzęcie.** Testy potwierdzają logikę (maska, ramki, sesje, deskryptor, limiter, argumenty wywołań z pinami Rev A) i to, że kod woła API z właściwymi argumentami. Nie potwierdzają, że:

- kompilacja ESP32_GENERIC_S3 v1.29.0 ma `machine.USBDevice` (runtime USB) i że HID działa obok REPL na N16R8 — [DO WERYFIKACJI testem]; bez tego `boot.py` wypisze błąd, a REPL zostanie;
- kompilacja ma włączony sterownik W5500, `lan.ifconfig()` jest nadal dostępne (starsze API) i `lan.config('mac')` zwraca adres bazowy + 3 (porównać z `esptool read-mac`);
- E22‑900M22S startuje z TCXO 1,8 V — błąd „BUSY timeout” sterownika często oznacza złe zasilanie TCXO (README lora); wtedy spróbować 2,2 V;
- Windows wysyła raport wyjściowy przez SET_REPORT bez punktu końcowego OUT i odbiera raporty 32 B w jednym pakiecie (punkt końcowy 64 B, nadpisany `desc_cfg`);
- BLE łączy się i wiąże (LE Secure Connections ustawia warstwa systemu) — pilot nie ogranicza mocy BLE.

Inne braki: brak transportu USB CDC z COBS (jest w protokole, nie ma w firmware), brak obsługi OLED, brak sondy ARP przy link‑local, warianty Meshtastic i MeshCore nie zostały zbudowane (kompilacja PlatformIO poza zakresem Rev A). Przed użyciem LoRa na antenie poza testami — zgodność urządzenia z RED (R3, rozdz. 5.6) i wartości z polskiego rozporządzenia (Dz.U. 2022 poz. 567) [DO WERYFIKACJI].

## 6. Warianty mesh

- **Meshtastic** (`meshtastic/variants/esp32s3/diy/pilot_wnet/`): skopiować do `variants/esp32s3/diy/pilot_wnet/` w repozytorium meshtastic/firmware, `pio run -e pilot_wnet`. Różnice względem `t-eth-elite`: LORA_RESET 2, bez GPS (GPIO39 = PLAY, GPIO42 = START nie mogą być UART‑em), tylko SX1262 (bez RF95, SX1280, LR1121 — firmware nie dotknie GPIO33/34, R5 S13), bez karty SD, przycisk 0, LED 38, Ethernet bez zmian. Pliki są utworem zależnym Meshtastic i podlegają **GPL‑3.0**. Meshtastic® is a registered trademark of Meshtastic LLC. Meshtastic software components are released under various licenses, see GitHub for details. No warranty is provided - use at your own risk.
- **MeshCore** (`meshcore/platformio_pilot_wnet.ini`): skopiować jako `variants/pilot_wnet/platformio.ini` w repozytorium MeshCore; środowiska `PilotWnet_sx1262_companion_radio_usb` i `PilotWnet_sx1262_repeater` (hasło administratora ze zmiennej `PILOT_MC_ADMIN_HASLO`, nigdy w pliku; `meshcore/wymagaj_hasla.py` skopiowany obok przerywa budowę przekaźnika, gdy zmienna jest pusta). Cykl pracy MeshCore (współczynnik „af”) sprawdzić przed nadawaniem w paśmie 54 [DO WERYFIKACJI]. Różnice: P_LORA_RESET 2 oraz I2C na 17/18. MeshCore: licencja MIT.
- Oryginalnego obrazu `t-eth-elite` na tej płytce nie uruchamiać (R5 S13).
