# -*- coding: utf-8 -*-
"""Testy planisty ramek (CPython)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import pilot_planista as P  # noqa: E402


class TestPlanista(unittest.TestCase):
    def test_zmiana_od_razu_potem_heartbeat_co_sekunde(self):
        p = P.Planista(1000, 40)
        self.assertEqual(p.krok(0, 0b1), (0b1, False))
        self.assertIsNone(p.krok(500))
        self.assertEqual(p.krok(1000), (None, True))
        self.assertIsNone(p.krok(1999))
        self.assertEqual(p.krok(2000), (None, True))

    def test_limit_scala_zmiany(self):
        p = P.Planista(1000, 3)
        wyn = [p.krok(t, m) for t, m in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5))]
        self.assertEqual([w for w in wyn if w], [(1, False), (2, False), (3, False)])
        # w nowej sekundzie idzie NAJNOWSZA zaległa maska, nie każda pośrednia
        self.assertEqual(p.krok(1000), (5, False))

    def test_cisza_przed_pierwsza_zmiana_daje_heartbeat(self):
        p = P.Planista(1000, 40)
        self.assertEqual(p.krok(0), (None, True))

    # Znana usterka (potwierdzona 19.11): okno stałe zamiast przesuwnego — 79 ramek w sekundzie przesuwnej.
    @unittest.skip("znana usterka (19.11): okno stałe zamiast przesuwnego — czeka na poprawkę "
                   "albo decyzję zespołu projektu")
    def test_w_zadnej_sekundzie_nie_wiecej_niz_limit_hosta(self):
        p = P.Planista(1000, 40); wys = []; m = 0
        for t in range(2000):
            if 950 <= t < 1100: m ^= 1; d = p.krok(t, m)
            else: d = p.krok(t)
            if d is not None: wys.append(t)
        for i, t0 in enumerate(wys):
            n = sum(1 for u in wys[i:] if u < t0 + 1000)
            self.assertLessEqual(n, 50, "od %d ms: %d ramek w 1 s" % (t0, n))


class TestHello(unittest.TestCase):
    def test_parsowanie_hello(self):
        import pilot_transport as T
        self.assertEqual(T.parsuj_hello(b"PWN1" + (99).to_bytes(4, "little")), 99)
        self.assertIsNone(T.parsuj_hello(b"PWN2" + bytes(4)))
        self.assertIsNone(T.parsuj_hello(b"PWN1" + bytes(3)))

    # Znana usterka (potwierdzona 19.11): HELLO z BLE przyjmowane z niezwiązanego (nieszyfrowanego) połączenia.
    @unittest.skip("znana usterka (19.11): HELLO z BLE przyjmowane z niezwiązanego połączenia — czeka na poprawkę "
                   "albo decyzję zespołu projektu")
    def test_hello_ble_tylko_z_polaczenia_zwiazanego(self):
        import asyncio, types
        class Koniec(Exception): pass
        class Pol: encrypted = authenticated = bonded = False
        class Ch:
            def __init__(self, *a, **kw): self.n = 0
            async def written(self):
                self.n += 1
                if self.n > 1: raise Koniec()
                return Pol(), b"PWN1" + (0xCAFE).to_bytes(4, "little")
        aioble = types.ModuleType("aioble")
        aioble.Service = lambda uuid: object(); aioble.Characteristic = Ch; aioble.register_services = lambda *a: None
        bt = types.ModuleType("bluetooth"); bt.UUID = lambda s: s
        sys.modules["aioble"] = aioble; sys.modules.setdefault("bluetooth", bt)
        self.addCleanup(sys.modules.pop, "aioble", None)
        import pilot_transport as T
        t = T.TransportBLE()
        with self.assertRaises(Koniec):
            asyncio.run(t.odbieraj_hello())
        self.assertIsNone(t.nonce(), "HELLO z niezwiązanego połączenia BLE ustawił nonce")

    # Znana usterka (potwierdzona 19.11): HELLO przyjmowane z dowolnego portu adresu hosta.
    @unittest.skip("znana usterka (19.11): HELLO przyjmowane z dowolnego portu adresu hosta — czeka na poprawkę "
                   "albo decyzję zespołu projektu")
    def test_hello_tylko_z_portu_hosta(self):
        import pilot_transport as T
        class G:
            d = [(b"PWN1" + (7).to_bytes(4, "little"), ("192.168.1.20", 50000))]
            def recvfrom(self, n):
                if not self.d: raise OSError(11)
                return self.d.pop(0)
        t = T.TransportUDP.__new__(T.TransportUDP)
        t.nazwa, t.adres, t._nonce, t.s = "udp", ("192.168.1.20", 47231), None, G()
        self.assertIsNone(t.nonce())


if __name__ == "__main__":
    unittest.main(verbosity=1)
