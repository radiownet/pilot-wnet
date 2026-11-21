# -*- coding: utf-8 -*-
"""Atrapy modułów MicroPythona (machine, network, bluetooth, usb.device, usb.device.hid, lora) dla testów
w CPythonie. Zapisują wywołania; niczego nie udają poza tym, co testy sprawdzają.

Atrapa nie zastępuje próby na płytce: potwierdza tylko, że kod woła API z właściwymi pinami i
argumentami, a nie że W5500, SX1262 czy USB naprawdę tak działają.
"""
import sys
import types

MODULY = ("machine", "network", "bluetooth", "usb", "usb.device", "usb.device.hid", "lora")


class Rejestr:
    def __init__(self):
        self.wywolania = []

    def zapisz(self, *a):
        self.wywolania.append(a)

    def nazwane(self, nazwa):
        return [w for w in self.wywolania if w[0] == nazwa]


def zainstaluj():
    """Wstawia atrapy do sys.modules i zwraca rejestr wywołań."""
    r = Rejestr()

    # ---------------------------------------------------------------- machine
    machine = types.ModuleType("machine")

    class Pin:
        IN, OUT = 1, 2

        def __init__(self, nr, tryb=None, value=None):
            self.nr = nr
            self.tryb = tryb
            self._v = 1 if value is None else value
            r.zapisz("Pin", nr, tryb)

        def value(self, v=None):
            if v is None:
                return self._v
            self._v = v
            return None

        def __repr__(self):
            return "Pin(%d)" % self.nr

    class SPI:
        def __init__(self, id_, **kw):
            self.id = id_
            self.kw = kw
            r.zapisz("SPI", id_, {k: (v.nr if isinstance(v, Pin) else v) for k, v in kw.items()})

    class WDT:
        def __init__(self, timeout):
            r.zapisz("WDT", timeout)

        def feed(self):
            pass

    machine.Pin, machine.SPI, machine.WDT = Pin, SPI, WDT
    machine.idle = lambda: None

    # ---------------------------------------------------------------- network
    network = types.ModuleType("network")
    network.PHY_W5500 = 23
    network.STA_IF, network.AP_IF = 0, 1

    class LAN:
        def __init__(self, **kw):
            self.kw = kw
            self._mac = bytes((0x24, 0x6F, 0x28, 0xAB, 0xCD, 0xEF))
            self._ip = ("0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0")
            self.polaczony = False
            self.aktywny = False
            r.zapisz("LAN", {k: (v.nr if isinstance(v, Pin) else v) for k, v in kw.items()})

        def active(self, v=None):
            if v is None:
                return self.aktywny
            self.aktywny = v
            r.zapisz("LAN.active", v)
            return None

        def config(self, *a, **kw):
            if kw.get("mac") is not None:
                self._mac = bytes(kw["mac"])
                r.zapisz("LAN.config", kw)
                return None
            if a == ("mac",):
                return self._mac
            raise ValueError(a)

        def ifconfig(self, krotka=None):
            if krotka is None:
                return self._ip
            self._ip = tuple(krotka)
            r.zapisz("LAN.ifconfig", tuple(krotka))
            return None

        def isconnected(self):
            return self.polaczony

    class WLAN:
        def __init__(self, i):
            self.i = i

        def active(self, v=None):
            r.zapisz("WLAN.active", self.i, v)

    network.LAN, network.WLAN = LAN, WLAN

    # ---------------------------------------------------------------- bluetooth
    bluetooth = types.ModuleType("bluetooth")
    bluetooth.UUID = lambda s: s

    # ---------------------------------------------------------------- usb.device, usb.device.hid
    usb = types.ModuleType("usb")
    usb.__path__ = []
    usb_device = types.ModuleType("usb.device")
    usb_device.__path__ = []

    class Urzadzenie:
        def init(self, *itfs, **kw):
            r.zapisz("usb.init", itfs, kw)

    _urz = Urzadzenie()
    usb_device.get = lambda: _urz
    usb.device = usb_device

    hid = types.ModuleType("usb.device.hid")

    class HIDInterface:
        def __init__(self, report_descriptor, extra_descriptors=[], set_report_buf=None, protocol=0,
                     interface_str=None, interval_ms=8):
            self.report_descriptor = report_descriptor
            self.extra_descriptors = extra_descriptors
            self._set_report_buf = set_report_buf
            self.protocol = protocol
            self.interface_str = interface_str
            self.interval_ms = interval_ms
            self._int_ep = None
            self.otwarty = True
            self.wyslane = []

        def get_hid_descriptor(self, desc=None):
            r.zapisz("hid_descriptor", len(self.report_descriptor))
            return b""

        def is_open(self):
            return self.otwarty

        def send_report(self, report_data, timeout_ms=100):
            self.wyslane.append(bytes(report_data))
            return True

    hid.HIDInterface = HIDInterface
    usb_device.hid = hid

    # ---------------------------------------------------------------- lora
    lora = types.ModuleType("lora")

    class SX1262:
        def __init__(self, spi, cs, **kw):
            self.spi, self.cs, self.kw = spi, cs, kw
            self.wyslane = []
            r.zapisz("SX1262", cs.nr, {k: (v.nr if isinstance(v, Pin) else v) for k, v in kw.items()})

        def get_time_on_air_us(self, dl):
            return 0   # atrapa; PilotLoRa bierze większą wartość ze wzoru karty

        def send(self, dane):
            self.wyslane.append(bytes(dane))

        def configure(self, cfg):
            r.zapisz("SX1262.configure", dict(cfg))

    lora.SX1262 = SX1262

    for nazwa, mod in (("machine", machine), ("network", network), ("bluetooth", bluetooth), ("usb", usb),
                       ("usb.device", usb_device), ("usb.device.hid", hid), ("lora", lora)):
        sys.modules[nazwa] = mod
    return r


def usun():
    for n in MODULY:
        sys.modules.pop(n, None)


class Opis:
    """Atrapa usb.device.core.Descriptor: zapisuje interface() i endpoint()."""

    def __init__(self):
        self.wpisy = []

    def interface(self, *a):
        self.wpisy.append(("interface",) + a)

    def endpoint(self, *a):
        self.wpisy.append(("endpoint",) + a)
