# -*- coding: utf-8 -*-
"""Transporty ramek pilota do komputera studyjnego: UDP (Wi-Fi i Ethernet) oraz Bluetooth LE (GATT).

Wspólny interfejs: `wyslij(ramka_32B)`, `nonce()` → ostatni nonce sesji od hosta albo None.
Uzgadnianie sesji (v1): host wysyła komunikat HELLO = b"PWN1" + nonce u32 LE; pilot zaczyna
numerację ramek od 1 i podpisuje je tym nonce. Komunikat nie jest podpisany: podrobiony HELLO
może najwyżej zerwać sesję (host odrzuci ramki z cudzym nonce), nie da się nim wstrzyknąć akcji.
Moduł używa API MicroPythona (`socket`, `bluetooth`, `aioble`); w CPythonie testowalna jest tylko
warstwa parsowania HELLO.
"""
import struct

HELLO = b"PWN1"
PORT_UDP = 47231  # [ROBOCZE] port Pilota Wnet na komputerze studyjnym; regułę zapory zakłada zespół projektu


def parsuj_hello(dane):
    """b"PWN1" + u32 → nonce albo None."""
    if len(dane) == 8 and dane[:4] == HELLO:
        return struct.unpack("<I", dane[4:8])[0]
    return None


class TransportUDP:
    """Wi-Fi albo Ethernet — po zestawieniu interfejsu sieciowego to ten sam kod gniazd."""

    def __init__(self, host, port=PORT_UDP, nazwa="udp", lokalny=None):
        """`lokalny` = (adres_interfejsu, port) — stały port, na który host wysyła HELLO. Bez niego gniazdo
        ma port efemeryczny, a pilot przed HELLO nic nie nadaje, więc host nie miałby dokąd odpowiedzieć."""
        import socket
        self.nazwa = nazwa
        self.adres = (host, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if lokalny is not None:
            self.s.bind(lokalny)
        self.s.setblocking(False)
        self._nonce = None

    def wyslij(self, ramka):
        try:
            self.s.sendto(ramka, self.adres)
            return True
        except OSError:
            return False

    def nonce(self):
        try:
            while True:
                dane, skad = self.s.recvfrom(64)
                if skad[0] != self.adres[0]:
                    continue  # tylko od skonfigurowanego hosta
                n = parsuj_hello(dane)
                if n is not None:
                    self._nonce = n
        except OSError:
            pass
        return self._nonce


class TransportBLE:
    """GATT: charakterystyka ramek (notify) i charakterystyka HELLO (write). Wymaga aioble."""

    UUID_USLUGI = "6e57b001-7069-6c6f-7477-6e6574000001"   # [ROBOCZE] własne UUID 128-bit
    UUID_RAMKI = "6e57b002-7069-6c6f-7477-6e6574000001"
    UUID_HELLO = "6e57b003-7069-6c6f-7477-6e6574000001"

    def __init__(self, nazwa_urzadzenia="Pilot Wnet"):
        import aioble
        import bluetooth
        self.aioble = aioble
        self.nazwa_urzadzenia = nazwa_urzadzenia
        self.nazwa = "ble"
        usl = aioble.Service(bluetooth.UUID(self.UUID_USLUGI))
        self.ch_ramki = aioble.Characteristic(usl, bluetooth.UUID(self.UUID_RAMKI), read=True, notify=True)
        self.ch_hello = aioble.Characteristic(usl, bluetooth.UUID(self.UUID_HELLO), write=True, capture=True)
        aioble.register_services(usl)
        self.polaczenie = None
        self._nonce = None

    async def czekaj_na_polaczenie(self):
        """Ogłasza się i czeka na komputer studyjny; wiązanie LE Secure Connections ustawia warstwa systemu."""
        self.polaczenie = await self.aioble.advertise(250_000, name=self.nazwa_urzadzenia, services=[])
        return self.polaczenie

    async def odbieraj_hello(self):
        while True:
            _, dane = await self.ch_hello.written()
            n = parsuj_hello(bytes(dane))
            if n is not None:
                self._nonce = n

    def wyslij(self, ramka):
        if self.polaczenie is None:
            return False
        try:
            self.ch_ramki.notify(self.polaczenie, ramka)
            return True
        except Exception:
            return False

    def nonce(self):
        return self._nonce

    def zerwij_sesje(self):
        """Po rozłączeniu: bez połączenia i bez nonce, nowa sesja dopiero po kolejnym HELLO."""
        self.polaczenie = None
        self._nonce = None
