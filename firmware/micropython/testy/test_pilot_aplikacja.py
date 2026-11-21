# -*- coding: utf-8 -*-
"""Testy pętli aplikacji (CPython): piny → maska → ramki na łączach z własnymi sesjami, dioda stanu."""
import os
import struct
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "lib"))
import pilot_aplikacja as A  # noqa: E402
import pilot_ramka as R  # noqa: E402

KLUCZ = b"\x11" * 32
PUSTE = [1] * 10   # wszystkie piny w stanie wysokim = nic nie wciśnięte


class Lacze:
    def __init__(self, nazwa, nonce=None, dziala=True):
        self.nazwa = nazwa
        self._nonce = nonce
        self.dziala = dziala
        self.ramki = []

    def nonce(self):
        return self._nonce

    def wyslij(self, r):
        if self.dziala:
            self.ramki.append(r)
        return self.dziala


def piny(*wcisniete_bity):
    w = list(PUSTE)
    for b in wcisniete_bity:
        w[b] = 0
    return w


def konf():
    return {"dev_id": 9, "stabilnosc_ms": 5, "heartbeat_ms": 1000, "limit_ramek_na_s": 40}


class TestAplikacja(unittest.TestCase):
    def test_zmiana_po_stabilizacji_trafia_na_kazde_lacze(self):
        a, b = Lacze("usb_hid", 100), Lacze("eth_udp", 200)
        app = A.Aplikacja(konf(), KLUCZ, [a, b])
        app.krok(0, PUSTE)                     # pierwszy heartbeat
        for t in range(1, 8):
            app.krok(t, piny(4))               # START (bit 4)
        zmiany = [R.dekoduj(r, KLUCZ, 100) for r in a.ramki]
        self.assertEqual(zmiany[-1][3], R.START)
        self.assertEqual(zmiany[-1][0] & R.FLAGA_HEARTBEAT, 0)
        self.assertEqual(R.dekoduj(b.ramki[-1], KLUCZ, 200)[3], R.START)   # własny nonce łącza
        self.assertEqual(app.ostatnia_zmiana_ms, 6)

    def test_heartbeat_co_sekunde(self):
        a = Lacze("usb_hid", 1)
        app = A.Aplikacja(konf(), KLUCZ, [a])
        for t in range(0, 2001):
            app.krok(t, PUSTE)
        hb = [R.dekoduj(r, KLUCZ, 1) for r in a.ramki]
        self.assertEqual(len(hb), 3)
        self.assertTrue(all(x[0] & R.FLAGA_HEARTBEAT for x in hb))
        self.assertEqual([x[2] for x in hb], [1, 2, 3])   # seq rośnie

    def test_bez_nonce_nic_nie_wychodzi(self):
        a = Lacze("ble")
        app = A.Aplikacja(konf(), KLUCZ, [a])
        for t in range(0, 1500):
            app.krok(t, piny(0))
        self.assertEqual(a.ramki, [])
        self.assertEqual(app.stan(), A.STAN_BEZ_SESJI)

    def test_nowe_hello_zaczyna_sesje_od_seq_1(self):
        a = Lacze("usb_hid", 7)
        app = A.Aplikacja(konf(), KLUCZ, [a])
        for t in range(0, 1001):
            app.krok(t, PUSTE)
        a._nonce = 8
        app.krok(2000, PUSTE)
        self.assertEqual(R.dekoduj(a.ramki[-1], KLUCZ, 8)[2], 1)

    def test_zerwane_lacze_traci_sesje(self):
        a = Lacze("ble", 7)
        app = A.Aplikacja(konf(), KLUCZ, [a])
        app.krok(0, PUSTE)
        self.assertEqual(app.stan(), A.STAN_SESJA)
        a._nonce = None
        app.krok(1000, PUSTE)
        self.assertEqual(app.stan(), A.STAN_BEZ_SESJI)

    def test_brak_klucza(self):
        a = Lacze("usb_hid", 1)
        app = A.Aplikacja(konf(), None, [a])
        for t in range(0, 1500):
            self.assertEqual(app.krok(t, piny(5)), 0)
        self.assertEqual(a.ramki, [])
        self.assertEqual(app.stan(), A.STAN_BLAD)

    def test_nieudane_wyslanie_liczone(self):
        a = Lacze("eth_udp", 1, dziala=False)
        app = A.Aplikacja(konf(), KLUCZ, [a])
        app.krok(0, PUSTE)
        self.assertEqual(app.nieudane, 1)

    def test_hello_przez_hid(self):
        import pilot_transport as T
        self.assertEqual(T.parsuj_hello(b"PWN1" + struct.pack("<I", 3)), 3)


class _Stop(Exception):
    pass


class TestPetlaDiody(unittest.TestCase):
    def test_dioda_liczy_czas_zegarem_petli_wejsc(self):
        # ostatnia_zmiana_ms pochodzi z zegara pętli wejść; dioda musi używać tego samego zegara,
        # a nie time.ticks_ms() (inne zero) — inaczej błysk 40 ms przy zmianie się rozjeżdża
        import types
        app = A.Aplikacja(konf(), KLUCZ, [Lacze("usb_hid", 1)])
        app.krok(0, PUSTE)                     # uzgodnienie sesji na łączu
        app.ostatnia_zmiana_ms = 5000

        class Led:
            stany = []

            def value(self, v):
                self.stany.append(v)

        atrapa = types.ModuleType("asyncio")

        async def sleep_ms(ms):
            raise _Stop()
        atrapa.sleep_ms = sleep_ms
        stary = sys.modules.get("asyncio")
        sys.modules["asyncio"] = atrapa
        try:
            led = Led()
            with self.assertRaises(_Stop):
                A._petla_diody(app, led, None, lambda: 5010).send(None)
            self.assertEqual(led.stany, [1])
        finally:
            if stary is not None:
                sys.modules["asyncio"] = stary
            else:
                del sys.modules["asyncio"]


class TestUdp(unittest.TestCase):
    def test_gniazdo_przypiete_do_portu_lokalnego(self):
        # bez stałego portu host nie ma dokąd wysłać HELLO (pilot przed HELLO milczy)
        import types
        import pilot_transport as T
        zapis = []

        class Gniazdo:
            def __init__(self, *a):
                pass

            def bind(self, adr):
                zapis.append(adr)

            def setblocking(self, v):
                pass

        atrapa = types.ModuleType("socket")
        atrapa.AF_INET, atrapa.SOCK_DGRAM, atrapa.socket = 2, 2, Gniazdo
        stary = sys.modules.get("socket")
        sys.modules["socket"] = atrapa
        try:
            k = {"udp": {"host": "192.168.77.1", "port": 47231, "port_lokalny": 47232}}
            T.TransportUDP("192.168.77.1", 47231, "eth_udp", lokalny=A._adres_lokalny("192.168.77.2", k))
            T.TransportUDP("192.168.77.1", 47231, "eth_udp")
        finally:
            sys.modules["socket"] = stary
        self.assertEqual(zapis, [("192.168.77.2", 47232)])


class TestDioda(unittest.TestCase):
    def test_wzory(self):
        self.assertTrue(A.wzor_diody(A.STAN_BLAD, 0))
        self.assertFalse(A.wzor_diody(A.STAN_BLAD, 100))
        self.assertTrue(A.wzor_diody(A.STAN_BEZ_SESJI, 2010))
        self.assertFalse(A.wzor_diody(A.STAN_BEZ_SESJI, 1000))
        self.assertTrue(A.wzor_diody(A.STAN_SESJA, 1039, 1000))
        self.assertFalse(A.wzor_diody(A.STAN_SESJA, 1040, 1000))
        self.assertFalse(A.wzor_diody(A.STAN_SESJA, 5, None))


if __name__ == "__main__":
    unittest.main(verbosity=1)
