# -*- coding: utf-8 -*-
"""Tabela pinów i stałe płytki Pilota Wnet Rev A (ESP32-S3-WROOM-1-N16R8).

Jedno miejsce na przydział GPIO w firmware. Źródło prawdy obwodu to `pcb/obwod.py` (SKiDL):
lista `WEJSCIA`, słownik `eth`, lista `lora`, sieci `LED_STATUS`, `VSYS_SENSE`, `EXP_IO13`. Zmiana pinu
w obwodzie = zmiana tutaj; `sprawdz()` wyłapuje powtórzenia i piny zakazane.

Uwagi do Rev A (R3 rozdz. 6.2, DECYZJE D9):
  * wejścia aktywne niskim, podciąganie zewnętrzne 10 kΩ, przed GPIO rezystor 1 kΩ i 10 nF do masy —
    w firmware `Pin.IN` bez wewnętrznego podciągania;
  * START na GPIO42, nie GPIO0 (wciśnięty START przy resecie nie może włączać trybu pobierania);
  * GPIO0 = tylko przycisk BOOT na płytce, GPIO46 = strapping z rezystorem do masy, bez funkcji;
  * GPIO33–37 to linie PSRAM Octal (SPIIO4–SPIIO7, SPIDQS) — nie wolno ich dotykać;
  * reset W5500 tylko obwodem RC (bez GPIO), PCA9685 (0x40) niemontowany (DECYZJE D1).
Moduł działa w MicroPythonie i w CPythonie (testy) — nie importuje `machine`.
"""

WERSJA_PLYTKI = "Rev A"
MODUL = "ESP32-S3-WROOM-1-N16R8"

# ------------------------------------------------------------------ wejścia (aktywne niskim)
# Kolejność = kolejność bitów maski w protokole v1: R Y B G START STOP ▲ ▼ ◄ ►
# R = RECORD (czerwony), Y = PLAY (żółty), B = WYŚLIJ (niebieski), G = SPRAWDŹ (zielony) — R3 rozdz. 1 i 6.2.
WEJSCIA = (
    ("REC", 41),
    ("PLAY", 39),
    ("WYSLIJ", 15),
    ("SPRAWDZ", 12),
    ("START", 42),
    ("STOP", 3),
    ("JOY_UP", 4),
    ("JOY_DOWN", 5),
    ("JOY_LEFT", 6),
    ("JOY_RIGHT", 7),
)
PINY_MASKI = tuple(g for _, g in WEJSCIA)   # indeks = numer bitu maski
WEJSCIA_AKTYWNE_NISKIM = True

BOOT = 0                      # przycisk na płytce (strapping), w aplikacji: tryb serwisowy przy starcie
LED_STATUS = 38               # zielona dioda SMD, stan wysoki = świeci
LED_AKTYWNA_WYSOKIM = True

# ------------------------------------------------------------------ I2C (OLED, Qwiic, złącze rozszerzeń)
I2C_ID = 0
I2C_SDA = 17
I2C_SCL = 18
I2C_CZESTOTLIWOSC = 400_000   # [ROBOCZE] SSD1306/SH1106 pracują z 400 kHz; z długą wiązką Qwiic zejść do 100 kHz
OLED_ADRES = 0x3C             # SSD1306 albo SH1106
PCA9685_ADRES = 0x40          # NIEMONTOWANY w Rev A (DECYZJE D1)
PCA9685_MONTOWANY = False

# ------------------------------------------------------------------ Ethernet W5500 (SPI3_HOST jak w Meshtastic)
ETH_SPI_ID = 2                # machine.SPI(2) = SPI3_HOST na ESP32-S3; LoRa na SPI(1)
ETH_SCLK = 48
ETH_MOSI = 21
ETH_MISO = 47
ETH_CS = 45                   # strapping VDD_SPI — przy N16R8 napięcie ustala eFuse (R3 rozdz. 6.4)
ETH_INT = 14
ETH_RESET = None              # tylko RC, bez GPIO
ETH_PHY_ADDR = 0              # MicroPython quickref ESP32: phy_addr=0 dla W5500

# ------------------------------------------------------------------ LoRa Ebyte E22-900M22S (SX1262)
LORA_SPI_ID = 1               # machine.SPI(1) = SPI2_HOST
LORA_SCK = 10
LORA_MOSI = 11
LORA_MISO = 9
LORA_NSS = 40
LORA_BUSY = 16
LORA_DIO1 = 8
LORA_NRST = 2                 # Rev A: NRESET na GPIO2 (R3 rozdz. 6.4); GPIO46 tylko przez zworkę R77 (DNP)
LORA_SPI_BAUD = 2_000_000     # [ROBOCZE] karta E22: SPI 0–10 Mb/s (R3 rozdz. 5.2)
LORA_DIO2_RF_SW = True        # DIO2 → TXEN, NOT DIO2 → RXEN (74LVC1G04) — sposób 1 z R3 rozdz. 5.3
# TCXO 32 MHz zasilany z DIO3. Meshtastic t-eth-elite: 1,8 V; Ebyte V1.5 (wg zlecenia): 2,2 V.
# [DO WERYFIKACJI] w karcie E22-900M22S wersji kupionej partii — parametr konfiguracji `lora.tcxo_mv`.
LORA_TCXO_MV = 1800
LORA_TCXO_MV_KANDYDACI = (1800, 2200)
LORA_TCXO_START_US = 1000     # domyślna wartość sterownika lora-sx126x

# ------------------------------------------------------------------ inne
EXP_IO13 = 13                 # złącze rozszerzeń J19 (i opcjonalnie RXEN przez R80, DNP)
VSYS_SENSE = 1                # ADC1_CH0, dzielnik 100 k / 100 k z 5 V
VSYS_DZIELNIK = 2.0           # [ROBOCZE] skalibrować pomiarem
USB_DM, USB_DP = 19, 20
UART0_TX, UART0_RX = 43, 44   # złącze serwisowe J20

# ------------------------------------------------------------------ ograniczenia modułu
# WROOM-1 wyprowadza IO0–IO21 i IO35–IO48 (R3 rozdz. 6.2); przy PSRAM Octal IO33–IO37 zajmuje pamięć
# (ESP-IDF v6.1, GPIO, za R5 rozdz. 1).
WYPROWADZONE = set(list(range(0, 22)) + list(range(35, 49)))
ZAKAZANE_PSRAM = set(range(33, 38))
STRAPPING = set((0, 3, 45, 46))
TCXO_ZAKRES_MV = (1600, 3300)  # zakres przyjmowany przez sterownik lora-sx126x


def piny():
    """Słownik sygnał → GPIO dla wszystkich funkcji płytki (bez None)."""
    p = {}
    for nazwa, g in WEJSCIA:
        p["BTN_" + nazwa] = g
    p.update({
        "BOOT": BOOT, "LED_STATUS": LED_STATUS,
        "I2C_SDA": I2C_SDA, "I2C_SCL": I2C_SCL,
        "ETH_SCLK": ETH_SCLK, "ETH_MOSI": ETH_MOSI, "ETH_MISO": ETH_MISO, "ETH_CS": ETH_CS, "ETH_INT": ETH_INT,
        "LORA_SCK": LORA_SCK, "LORA_MOSI": LORA_MOSI, "LORA_MISO": LORA_MISO, "LORA_NSS": LORA_NSS,
        "LORA_BUSY": LORA_BUSY, "LORA_DIO1": LORA_DIO1, "LORA_NRST": LORA_NRST,
        "EXP_IO13": EXP_IO13, "VSYS_SENSE": VSYS_SENSE,
        "USB_DM": USB_DM, "USB_DP": USB_DP, "UART0_TX": UART0_TX, "UART0_RX": UART0_RX,
    })
    if ETH_RESET is not None:
        p["ETH_RESET"] = ETH_RESET
    return p


def sprawdz(mapa=None, tcxo_mv=None):
    """Lista błędów konfiguracji pinów (pusta = w porządku).

    Sprawdza: piny PSRAM Octal (33–37), piny niewyprowadzone z modułu, powtórzenia GPIO między
    sygnałami, liczbę wejść maski, napięcie TCXO w zakresie sterownika. `mapa` pozwala sprawdzić
    inny przydział (testy, przyszły Rev B)."""
    mapa = piny() if mapa is None else mapa
    tcxo_mv = LORA_TCXO_MV if tcxo_mv is None else tcxo_mv
    bledy = []
    uzyte = {}
    for sygnal in sorted(mapa):
        g = mapa[sygnal]
        if not isinstance(g, int) or g < 0:
            bledy.append("%s: niepoprawny numer GPIO %r" % (sygnal, g))
            continue
        if g in ZAKAZANE_PSRAM:
            bledy.append("%s: GPIO%d należy do PSRAM Octal (33–37)" % (sygnal, g))
        elif g not in WYPROWADZONE:
            bledy.append("%s: GPIO%d nie jest wyprowadzony z modułu WROOM-1" % (sygnal, g))
        if g in uzyte:
            bledy.append("GPIO%d użyty dwa razy: %s i %s" % (g, uzyte[g], sygnal))
        else:
            uzyte[g] = sygnal
    if len(PINY_MASKI) != 10:
        bledy.append("maska v1 ma 10 bitów, a tabela WEJSCIA %d pozycji" % len(PINY_MASKI))
    if not (TCXO_ZAKRES_MV[0] <= tcxo_mv <= TCXO_ZAKRES_MV[1]):
        bledy.append("TCXO %d mV poza zakresem sterownika %d–%d mV" % ((tcxo_mv,) + TCXO_ZAKRES_MV))
    return bledy


def ostrzezenia(mapa=None, tcxo_mv=None):
    """Rzeczy dozwolone, ale wymagające uwagi (nie blokują startu)."""
    mapa = piny() if mapa is None else mapa
    tcxo_mv = LORA_TCXO_MV if tcxo_mv is None else tcxo_mv
    w = []
    for sygnal in sorted(mapa):
        g = mapa[sygnal]
        if g in STRAPPING and sygnal not in ("BOOT", "ETH_CS", "BTN_STOP"):
            w.append("%s na pinie strapping GPIO%d" % (sygnal, g))
    if tcxo_mv not in LORA_TCXO_MV_KANDYDACI:
        w.append("TCXO %d mV spoza wartości z kart (1800 Meshtastic, 2200 Ebyte V1.5) [DO WERYFIKACJI]" % tcxo_mv)
    return w
