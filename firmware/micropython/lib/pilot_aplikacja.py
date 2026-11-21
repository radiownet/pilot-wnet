# -*- coding: utf-8 -*-
"""Aplikacja pilota na płytce Rev A: Wejscia → Planista → Nadajnik → transporty, dioda stanu.

Część synchroniczna (`Aplikacja.krok`, `wzor_diody`) jest testowana w CPythonie z atrapami transportów;
`start()` składa pętlę asyncio z odczytem pinów co 1 ms, Ethernetem, BLE i Wi-Fi.

Sesje: każdy transport ma własny `Nadajnik` (własny nonce i licznik `seq`), bo host uzgadnia sesję
osobno na każdym łączu (HELLO). Planista jest wspólny — o tym, czy wysłać zmianę albo podtrzymanie,
decyduje stan wejść, nie łącze. Ramka idzie na każde łącze, które ma już nonce.

Dioda stanu (GPIO38, wysoki = świeci):
  * błąd konfiguracji / brak klucza HMAC — miga szybko (5 Hz), nic nie jest wysyłane;
  * brak sesji na żadnym łączu — krótki błysk co 2 s;
  * sesja — dioda zgaszona, zapala się na 40 ms przy każdej ramce zmiany (kalibracja opóźnień kamerą,
    docs/ESP32_PROTOKOL.md „Pomiar opóźnień”).
"""

import pilot_planista
import pilot_ramka
import pilot_wejscia

STAN_BLAD = "blad"
STAN_BEZ_SESJI = "bez_sesji"
STAN_SESJA = "sesja"
BLYSK_MS = 40


def wzor_diody(stan, t_ms, ostatnia_zmiana_ms=None):
    """True = dioda świeci w chwili t_ms."""
    if stan == STAN_BLAD:
        return (t_ms // 100) % 2 == 0
    if stan == STAN_BEZ_SESJI:
        return t_ms % 2000 < 60
    return ostatnia_zmiana_ms is not None and 0 <= t_ms - ostatnia_zmiana_ms < BLYSK_MS


class Aplikacja:
    def __init__(self, konf, klucz, transporty):
        self.konf = konf
        self.klucz = klucz
        self.wejscia = pilot_wejscia.Wejscia(konf.get("stabilnosc_ms", 5))
        self.planista = pilot_planista.Planista(konf.get("heartbeat_ms", 1000), konf.get("limit_ramek_na_s", 40))
        self.lacza = []   # [transport, Nadajnik, ostatni_nonce]
        for t in transporty:
            self.dodaj_transport(t)
        self.ostatnia_zmiana_ms = None
        self.wyslane = 0
        self.nieudane = 0

    def dodaj_transport(self, t):
        # bez klucza Nadajnik dostaje pusty — `krok` i tak nic nie wysyła (stan błędu)
        self.lacza.append([t, pilot_ramka.Nadajnik(self.konf["dev_id"], self.klucz or b""), None])

    def stan(self):
        if not self.klucz:
            return STAN_BLAD
        for _, nad, _ in self.lacza:
            if nad.nonce is not None:
                return STAN_SESJA
        return STAN_BEZ_SESJI

    def _odswiez_sesje(self):
        for l in self.lacza:
            n = l[0].nonce()
            if n is not None and n != l[2]:
                l[1].nowa_sesja(n)
                l[2] = n
            elif n is None and l[2] is not None:   # łącze zerwane — bez ramek do nowego HELLO
                l[1].nonce = None
                l[2] = None

    def krok(self, t_ms, wartosci_pinow):
        """Jeden obrót pętli: wartości 10 pinów w kolejności bitów maski. Zwraca liczbę wysłanych ramek."""
        if not self.klucz:
            return 0
        self._odswiez_sesje()
        maska = pilot_wejscia.maska_z_pinow(wartosci_pinow)
        nowa = self.wejscia.krok(maska, t_ms)
        decyzja = self.planista.krok(t_ms, nowa)
        if decyzja is None:
            return 0
        m, hb = decyzja
        if m is None:
            m = self.wejscia.stabilna
        else:
            self.ostatnia_zmiana_ms = t_ms
        n = 0
        dev_ms = t_ms & 0xFFFFFFFF
        for t, nad, _ in self.lacza:
            r = nad.ramka(m, dev_ms, heartbeat=hb)
            if r is None:
                continue
            if t.wyslij(r):
                n += 1
            else:
                self.nieudane += 1
        self.wyslane += n
        return n


# ------------------------------------------------------------------ część tylko dla MicroPythona

def _wylacz_wifi():
    import network
    for i in (network.STA_IF, network.AP_IF):
        try:
            network.WLAN(i).active(False)
        except Exception:  # noqa: BLE001 — brak radia w kompilacji to też „wyłączone”
            pass


def _adres_lokalny(adres_interfejsu, konf):
    """(adres, port) gniazda UDP pilota: host wysyła HELLO na adres pilota i `udp.port_lokalny`.
    Przypięcie do adresu interfejsu pozwala mieć ten sam port na Ethernecie i Wi‑Fi naraz."""
    return (adres_interfejsu, int(konf["udp"].get("port_lokalny") or konf["udp"]["port"]))


async def _petla_wejsc(app, piny, zegar):
    import asyncio
    while True:
        app.krok(zegar(), [p.value() for p in piny])
        await asyncio.sleep_ms(1)


async def _petla_diody(app, led, wdt, zegar):
    # Ten sam zegar co w `_petla_wejsc`: `ostatnia_zmiana_ms` pochodzi z niego, a `time.ticks_ms()` liczy od
    # rozruchu (inne zero) i przewija się co 2^30 ms — błysk 40 ms przy zmianie by się rozjechał.
    import asyncio
    while True:
        t = zegar()
        led.value(1 if wzor_diody(app.stan(), t, app.ostatnia_zmiana_ms) else 0)
        if wdt is not None:
            wdt.feed()
        await asyncio.sleep_ms(10)


async def _ethernet(app, konf):
    import pilot_eth
    import pilot_transport
    try:
        lan = pilot_eth.utworz(konf["eth"])
    except Exception as e:  # noqa: BLE001
        print("pilot: Ethernet niedostępny:", e)
        return
    adres = await pilot_eth.czekaj_na_adres(lan, konf["eth"])
    print("pilot: Ethernet", adres, "MAC", ":".join("%02x" % b for b in lan.config("mac")))
    if adres and "eth_udp" in konf["transporty"]:
        app.dodaj_transport(pilot_transport.TransportUDP(konf["udp"]["host"], konf["udp"]["port"], "eth_udp",
                                                         lokalny=_adres_lokalny(adres, konf)))


async def _wifi(app, konf):
    import asyncio
    import network
    import pilot_transport
    w = network.WLAN(network.STA_IF)
    w.active(True)
    w.connect(konf["wifi"]["ssid"], konf["wifi"]["haslo"])
    for _ in range(200):
        if w.isconnected():
            break
        await asyncio.sleep_ms(100)
    if not w.isconnected():
        print("pilot: Wi-Fi bez połączenia")
        return
    try:
        adres = w.ifconfig()[0]
    except AttributeError:
        adres = w.ipconfig("addr4")[0]
    app.dodaj_transport(pilot_transport.TransportUDP(konf["udp"]["host"], konf["udp"]["port"], "wifi_udp",
                                                     lokalny=_adres_lokalny(adres, konf)))


async def _ble(app, konf):
    import asyncio
    import pilot_transport
    t = pilot_transport.TransportBLE(konf["ble"]["nazwa"])
    app.dodaj_transport(t)
    asyncio.create_task(t.odbieraj_hello())
    while True:
        pol = await t.czekaj_na_polaczenie()
        await pol.disconnected(timeout_ms=None)
        t.zerwij_sesje()


def start(sciezka_konfiguracji=None):
    """Punkt wejścia z `main.py`."""
    import asyncio
    import machine
    import konfig_plytki as K
    import pilot_hid
    import pilot_konfig
    import pilot_lora

    led = machine.Pin(K.LED_STATUS, machine.Pin.OUT, value=0)
    konf, bledy = pilot_konfig.wczytaj(sciezka_konfiguracji or pilot_konfig.SCIEZKA)
    bledy = K.sprawdz(tcxo_mv=konf["lora"].get("tcxo_mv") or K.LORA_TCXO_MV) + bledy
    for b in bledy:
        print("pilot: BŁĄD", b)
    for w in K.ostrzezenia():
        print("pilot: uwaga", w)
    klucz = None if bledy else pilot_konfig.klucz(konf)

    if not konf["wifi"].get("wlaczone"):
        _wylacz_wifi()

    transporty = []
    hid = pilot_hid.aktywny()
    if "usb_hid" in konf["transporty"]:
        if hid is not None:
            transporty.append(hid)
        else:
            print("pilot: USB HID nie został uruchomiony w boot.py")
    app = Aplikacja(konf, klucz, transporty)

    piny = [machine.Pin(g, machine.Pin.IN) for g in K.PINY_MASKI]   # podciąganie zewnętrzne 10 kΩ
    zegar = pilot_lora._ZegarMonotoniczny()
    wdt = machine.WDT(timeout=konf["watchdog_ms"]) if konf.get("watchdog_ms") else None

    async def glowna():
        asyncio.create_task(_petla_diody(app, led, wdt, zegar))
        if klucz is None:
            while True:            # tryb bez nadawania; REPL po USB dostępny przez Ctrl-C
                await asyncio.sleep_ms(1000)
        if konf["eth"].get("wlaczony"):
            asyncio.create_task(_ethernet(app, konf))
        if "wifi_udp" in konf["transporty"] and konf["wifi"].get("wlaczone"):
            asyncio.create_task(_wifi(app, konf))
        if "ble" in konf["transporty"]:
            asyncio.create_task(_ble(app, konf))
        if konf["lora"].get("wlaczona"):
            try:
                app.lora = pilot_lora.PilotLoRa(konf["lora"])   # dla aplikacji; pilot sam nic nie nadaje
            except Exception as e:  # noqa: BLE001
                print("pilot: LoRa wyłączona:", e)
        await _petla_wejsc(app, piny, zegar)

    asyncio.run(glowna())
