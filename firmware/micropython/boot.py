# -*- coding: utf-8 -*-
"""boot.py — płytka Pilota Wnet Rev A. Uruchamia się przed main.py.

1. Wi-Fi wyłączone od startu (studio: RØDE Interview PRO w 2,4 GHz, R5 rozdz. 5.1); main.py włączy je
   tylko, gdy konfiguracja ma `wifi.wlaczone = true`.
2. USB HID producenta obok REPL (`builtin_driver=True`, R5 S10) — konfiguracja USB musi być w boot.py.
   Przycisk BOOT (GPIO0) naciśnięty w oknie zaraz po resecie (dioda stanu świeci ok. 0,7 s) = tryb
   serwisowy: bez HID i bez pętli pilota, sam REPL. BOOT trzymany już w chwili resetu = tryb pobierania ROM.
Każdy błąd jest łapany: płytka zawsze zostaje dostępna przez REPL po USB-CDC.
"""

import sys

if "/lib" not in sys.path:
    sys.path.append("/lib")

try:
    import network
    for _i in (network.STA_IF, network.AP_IF):
        try:
            network.WLAN(_i).active(False)
        except Exception:  # noqa: BLE001
            pass
except ImportError:
    pass

try:
    import pilot_konfig
except Exception as e:  # noqa: BLE001
    pilot_konfig = None
    print("boot: brak lib/pilot_konfig.py:", e)

# GPIO0 to pin strapping: BOOT trzymany w chwili resetu włącza tryb pobierania ROM i boot.py w ogóle się nie
# wykona. Dlatego tryb serwisowy wybiera się PO resecie: dioda stanu świeci przez OKNO_SERWISOWE_MS i w tym
# czasie trzeba nacisnąć BOOT. Jednorazowy odczyt na samym początku praktycznie nie dawał się trafić.
OKNO_SERWISOWE_MS = 700   # [ROBOCZE] opóźnia start pilota o ten czas
try:
    import machine
    import time
    import konfig_plytki
    if pilot_konfig is not None:
        _boot = machine.Pin(konfig_plytki.BOOT, machine.Pin.IN)   # podciąganie zewnętrzne 10 kΩ (R9)
        _led = machine.Pin(konfig_plytki.LED_STATUS, machine.Pin.OUT, value=1)
        _t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), _t0) < OKNO_SERWISOWE_MS:
            if _boot.value() == 0:
                pilot_konfig.TRYB_SERWISOWY = True
                break
            time.sleep_ms(5)
        _led.value(0)
except Exception as e:  # noqa: BLE001
    print("boot: odczyt BOOT nieudany:", e)

if pilot_konfig is not None and pilot_konfig.TRYB_SERWISOWY:
    print("boot: tryb serwisowy (BOOT wciśnięty) — bez USB HID i bez pętli pilota")
elif pilot_konfig is not None:
    try:
        _konf, _ = pilot_konfig.wczytaj()
        if "usb_hid" in _konf["transporty"]:
            import pilot_hid
            pilot_hid.uruchom(_konf["usb"]["produkt"], _konf["usb"]["producent"])
    except Exception as e:  # noqa: BLE001 — brak usb-device-hid albo USBDevice w kompilacji
        print("boot: USB HID nieaktywny:", e)
