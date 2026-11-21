# -*- coding: utf-8 -*-
"""USB HID producenta (strona użycia 0xFF00) — domyślny transport ramek pilota do komputera studyjnego.

Pilot nie jest klawiaturą ani myszą: deskryptor raportu ma tylko stronę producenta, więc system nie
przyjmie z niego naciśnięć klawiszy (ochrona przed BadUSB — docs/ESP32_PROTOKOL.md, „Transporty”).
Windows obsługuje takie urządzenie sterownikiem klasy HID bez instalacji.

Raporty (bez identyfikatorów raportów):
  * wejściowy (urządzenie → host) 32 B = ramka protokołu v1 z `pilot_ramka` bez zmian;
  * wyjściowy (host → urządzenie) 8 B = HELLO: b"PWN1" + nonce u32 LE (jak w `pilot_transport`).
    Urządzenie nie ma punktu końcowego OUT, więc Windows wysyła raport wyjściowy żądaniem SET_REPORT
    na punkcie sterującym (`WriteFile`/`HidD_SetOutputReport` z buforem 9 B: bajt 0 = 0x00, bo brak ID).

Warstwa USB: micropython-lib `usb-device-hid` (`usb.device.hid.HIDInterface`) i `usb.device.get().init(…,
builtin_driver=True)`. `builtin_driver=True` zostawia wbudowany port szeregowy USB-CDC z REPL obok HID —
bez tego REPL może zniknąć aż do trybu awaryjnego albo skasowania flasha (README micropython-lib/usb,
R5 S10). Konfiguracja USB należy do `boot.py`.

Punkt końcowy przerwań: klasa bazowa `HIDInterface` (usb-device-hid 0.2.0) deklaruje pakiet 8 B, więc
raport 32 B szedłby w 4 transakcjach. `desc_cfg` poniżej powtarza logikę klasy bazowej z pakietem 64 B
(maksimum Full Speed) i odpytywaniem co 1 ms. Zgodność z kolejnymi wersjami usb-device-hid — sprawdzić
przy aktualizacji pakietu.
"""

import pilot_ramka
import pilot_transport

DL_RAPORTU_WE = pilot_ramka.DL      # 32
DL_RAPORTU_WY = 8                   # HELLO
DL_PAKIETU = 64
ODPYTYWANIE_MS = 1

# Deskryptor raportu HID 1.11 (rozdz. 6.2.2), strona producenta 0xFF00
DESKRYPTOR_RAPORTU = bytes((
    0x06, 0x00, 0xFF,   # Usage Page (Vendor Defined 0xFF00)
    0x09, 0x01,         # Usage (0x01) — pilot
    0xA1, 0x01,         # Collection (Application)
    0x09, 0x02,         #   Usage (0x02) — ramka
    0x15, 0x00,         #   Logical Minimum (0)
    0x26, 0xFF, 0x00,   #   Logical Maximum (255)
    0x75, 0x08,         #   Report Size (8)
    0x95, DL_RAPORTU_WE,  # Report Count (32)
    0x81, 0x02,         #   Input (Data, Variable, Absolute)
    0x09, 0x03,         #   Usage (0x03) — HELLO
    0x95, DL_RAPORTU_WY,  # Report Count (8)
    0x91, 0x02,         #   Output (Data, Variable, Absolute)
    0xC0,               # End Collection
))

_aktywny = None


def raport_z_ramki(ramka):
    """Ramka 32 B → raport wejściowy (ten sam ciąg bajtów); inna długość = ValueError."""
    if len(ramka) != DL_RAPORTU_WE:
        raise ValueError("raport HID musi mieć %d bajtów" % DL_RAPORTU_WE)
    return bytes(ramka)


def nonce_z_raportu(dane):
    """Raport wyjściowy HELLO → nonce albo None."""
    return pilot_transport.parsuj_hello(bytes(dane))


def _klasa():
    from usb.device.hid import HIDInterface

    class PilotHID(HIDInterface):
        """Interfejs HID pilota; ten sam kontrakt co transporty: `wyslij`, `nonce`, `nazwa`."""

        nazwa = "usb_hid"

        def __init__(self):
            super().__init__(DESKRYPTOR_RAPORTU, set_report_buf=bytearray(DL_RAPORTU_WY),
                             interface_str="Pilot Wnet", interval_ms=ODPYTYWANIE_MS)
            self._nonce = None

        def desc_cfg(self, desc, itf_num, ep_num, strs):
            # jak HIDInterface.desc_cfg, ale pakiet DL_PAKIETU zamiast 8 B
            desc.interface(itf_num, 1, 0x03, 0x00, 0x00, len(strs) if self.interface_str else 0)
            if self.interface_str:
                strs.append(self.interface_str)
            self.get_hid_descriptor(desc)
            self._int_ep = ep_num | 0x80
            desc.endpoint(self._int_ep, "interrupt", DL_PAKIETU, self.interval_ms)
            self.idle_rate = 0
            self.protocol = 1

        def on_set_report(self, report_data, report_id, report_type):
            n = nonce_z_raportu(report_data)
            if n is not None:
                self._nonce = n
            return True

        def wyslij(self, ramka):
            if not self.is_open():
                return False
            return self.send_report(raport_z_ramki(ramka), timeout_ms=2)

        def nonce(self):
            return self._nonce

    return PilotHID


def uruchom(produkt="Pilot Wnet", producent="Radio Wnet"):
    """Rejestruje HID obok wbudowanego CDC (REPL). Wołać z `boot.py`. Zwraca interfejs."""
    global _aktywny
    import usb.device
    itf = _klasa()()
    # VID/PID zostają wbudowane (MicroPython) — własnej pary nie mamy [DO WERYFIKACJI przed seryjną].
    usb.device.get().init(itf, builtin_driver=True, product_str=produkt, manufacturer_str=producent)
    _aktywny = itf
    return itf


def aktywny():
    """Interfejs zarejestrowany w `boot.py` (moduły z `boot.py` zostają w sys.modules dla `main.py`)."""
    return _aktywny
