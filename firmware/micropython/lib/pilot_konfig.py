# -*- coding: utf-8 -*-
"""Konfiguracja pilota z pliku JSON na flashu (`/pilot_konfig.json`).

W repozytorium leży tylko szablon `pilot_konfig.przyklad.json` z pustymi polami tajnymi. Klucz HMAC
(32 bajty, hex) generuje Pilot Wnet na komputerze studyjnym i wgrywa wyłącznie kablem USB
(docs/ESP32_PROTOKOL.md, „Parowanie”; implementacja hosta, czyli aplikacja na komputer studyjny, nie jest
jeszcze publiczna) — np. `mpremote cp pilot_konfig.json :pilot_konfig.json`. Tak samo hasło Wi-Fi.

Czysta logika (CPython i MicroPython): `wczytaj(sciezka)` → (konfiguracja, błędy). Brak pliku albo
błędy nie wywracają firmware — `main.py` zostaje w trybie bez nadawania i sygnalizuje to diodą.
"""

try:
    import json
except ImportError:  # starsze MicroPythony
    import ujson as json  # noqa: F401

SCIEZKA = "/pilot_konfig.json"
TRYB_SERWISOWY = False   # ustawia boot.py, gdy BOOT (GPIO0) naciśnięty w oknie po resecie; czyta main.py
DL_KLUCZA = 32
TRANSPORTY = ("usb_hid", "eth_udp", "wifi_udp", "ble")

DOMYSLNA = {
    "wersja": 1,
    "dev_id": 1,
    "klucz_hmac_hex": "",            # NIGDY w repozytorium
    "transporty": ["usb_hid"],       # domyślny i zalecany (protokół)
    "stabilnosc_ms": 5,
    "heartbeat_ms": 1000,
    "limit_ramek_na_s": 40,          # host odrzuca > 50/s
    "watchdog_ms": 0,                # 0 = wyłączony (WDT na ESP32 nie da się zatrzymać — włączać w produkcji)
    "usb": {"produkt": "Pilot Wnet", "producent": "Radio Wnet"},
    "eth": {
        "wlaczony": False,
        "tryb": "dhcp",              # "dhcp" albo "statyczny"
        "adres": "", "maska": "255.255.255.0", "brama": "", "dns": "",
        "dhcp_czekaj_ms": 8000,
        "link_local": True,          # brak DHCP → 169.254.x.y
        "mac": "",                   # pusty = MAC z eFuse ESP32-S3 (adres bazowy + 3)
    },
    "udp": {"host": "", "port": 47231, "port_lokalny": 47231},   # port_lokalny: tu host wysyła HELLO
    "wifi": {"wlaczone": False, "ssid": "", "haslo": ""},   # studio: Wi-Fi wyłączone (R5 rozdz. 5.1)
    "ble": {"nazwa": "Pilot Wnet"},
    "lora": {
        "wlaczona": False,
        "freq_khz": 869525, "bw": "125", "sf": 9, "coding_rate": 5, "output_power": 14,
        "preamble_len": 8,
        "zysk_anteny_dbi": 3.0,      # [DO WERYFIKACJI] karta kupionej anteny
        "straty_db": 0.0,            # pigtail IPEX→SMA; 0 = założenie najostrzejsze
        "zapas_db": 1.0,             # [ROBOCZE] rozrzut mocy modułu (karta E22: 22,3 dBm maks. przy 22)
        "tcxo_mv": None,             # None = konfig_plytki.LORA_TCXO_MV
    },
}


def _scal(baza, nowe):
    wynik = {}
    for k, v in baza.items():
        if isinstance(v, dict) and isinstance(nowe.get(k), dict):
            wynik[k] = _scal(v, nowe[k])
        elif k in nowe:
            wynik[k] = nowe[k]
        else:
            wynik[k] = v
    for k, v in nowe.items():
        if k not in wynik:
            wynik[k] = v
    return wynik


def klucz(konf):
    """Bajty klucza HMAC albo None, gdy pusty lub niepoprawny."""
    h = konf.get("klucz_hmac_hex") or ""
    if len(h) != 2 * DL_KLUCZA:
        return None
    try:
        return bytes(int(h[i:i + 2], 16) for i in range(0, len(h), 2))
    except ValueError:
        return None


def sprawdz(konf):
    """Lista błędów (pusta = konfiguracja kompletna). Nie wypisuje wartości tajnych."""
    b = []
    if konf.get("wersja") != 1:
        b.append("nieznana wersja konfiguracji")
    d = konf.get("dev_id")
    if not isinstance(d, int) or not (1 <= d <= 0xFFFF):
        b.append("dev_id poza zakresem 1–65535")
    if klucz(konf) is None:
        b.append("brak klucza HMAC albo zła długość (wymagane 32 bajty hex)")
    tr = konf.get("transporty") or []
    for t in tr:
        if t not in TRANSPORTY:
            b.append("nieznany transport: %s" % t)
    if not tr:
        b.append("brak transportów")
    if "eth_udp" in tr:
        if not konf["eth"].get("wlaczony"):
            b.append("eth_udp wymaga eth.wlaczony = true")
        if konf["eth"].get("tryb") == "statyczny" and not konf["eth"].get("adres"):
            b.append("eth.tryb = statyczny wymaga eth.adres")
    if ("eth_udp" in tr or "wifi_udp" in tr) and not konf["udp"].get("host"):
        b.append("transport UDP wymaga udp.host (adres komputera studyjnego)")
    for pole in ("port", "port_lokalny"):
        p = konf["udp"].get(pole)
        if not isinstance(p, int) or isinstance(p, bool) or not (1 <= p <= 65535):
            b.append("udp.%s poza zakresem 1–65535" % pole)
    if "wifi_udp" in tr and not (konf["wifi"].get("wlaczone") and konf["wifi"].get("ssid")):
        b.append("wifi_udp wymaga wifi.wlaczone = true i wifi.ssid")
    if konf["eth"].get("tryb") not in ("dhcp", "statyczny"):
        b.append("eth.tryb musi być dhcp albo statyczny")
    return b


def zaladuj_tekst(tekst):
    """Konfiguracja z tekstu JSON → (konf, błędy)."""
    try:
        dane = json.loads(tekst)
    except ValueError:
        return _scal(DOMYSLNA, {}), ["plik konfiguracji nie jest poprawnym JSON"]
    if not isinstance(dane, dict):
        return _scal(DOMYSLNA, {}), ["plik konfiguracji musi zawierać obiekt JSON"]
    konf = _scal(DOMYSLNA, dane)
    return konf, sprawdz(konf)


def wczytaj(sciezka=SCIEZKA):
    """(konf, błędy). Brak pliku = konfiguracja domyślna i błąd „brak pliku”."""
    try:
        with open(sciezka) as f:
            tekst = f.read()
    except OSError:
        konf = _scal(DOMYSLNA, {})
        return konf, ["brak pliku %s" % sciezka] + sprawdz(konf)
    return zaladuj_tekst(tekst)
