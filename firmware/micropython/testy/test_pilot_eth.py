# -*- coding: utf-8 -*-
"""Testy inicjalizacji W5500 (atrapa network.LAN, CPython): piny, adres statyczny, DHCP, link-local."""
import asyncio
import os
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "lib"))
sys.path.insert(0, TU)
import atrapy  # noqa: E402
import pilot_eth as E  # noqa: E402

if not hasattr(asyncio, "sleep_ms"):   # MicroPython ma sleep_ms; w CPythonie zastępnik
    asyncio.sleep_ms = lambda ms: asyncio.sleep(0)


class TestW5500(unittest.TestCase):
    def setUp(self):
        self.r = atrapy.zainstaluj()

    def tearDown(self):
        atrapy.usun()

    def test_piny_i_argumenty_lan(self):
        E.utworz({})
        (_, nr, piny), = self.r.nazwane("SPI")
        self.assertEqual(nr, 2)
        self.assertEqual(piny, {"sck": 48, "mosi": 21, "miso": 47})
        (_, kw), = self.r.nazwane("LAN")
        self.assertEqual(kw["phy_type"], 23)          # atrapa network.PHY_W5500
        self.assertEqual(kw["phy_addr"], 0)
        self.assertEqual((kw["cs"], kw["int"]), (45, 14))
        self.assertNotIn("reset", kw)                 # reset W5500 tylko RC
        self.assertEqual(self.r.nazwane("LAN.active"), [("LAN.active", True)])

    def test_adres_statyczny(self):
        E.utworz({"tryb": "statyczny", "adres": "192.168.77.2", "maska": "255.255.255.0", "brama": ""})
        self.assertEqual(self.r.nazwane("LAN.ifconfig"),
                         [("LAN.ifconfig", ("192.168.77.2", "255.255.255.0", "0.0.0.0", "0.0.0.0"))])

    def test_wlasny_mac_przed_wlaczeniem(self):
        E.utworz({"mac": "02:00:5e:10:20:30"})
        kolejnosc = [w[0] for w in self.r.wywolania if w[0].startswith("LAN.")]
        self.assertEqual(kolejnosc, ["LAN.config", "LAN.active"])
        with self.assertRaises(ValueError):
            E.mac_z_tekstu("01:00:5e:00:00:01")   # adres grupowy

    def test_dhcp_bez_odpowiedzi_daje_link_local(self):
        lan = E.utworz({"tryb": "dhcp"})
        a = asyncio.run(E.czekaj_na_adres(lan, {"tryb": "dhcp", "dhcp_czekaj_ms": 300, "link_local": True}))
        self.assertEqual(a, E.adres_link_local(lan.config("mac")))
        self.assertEqual(self.r.nazwane("LAN.ifconfig")[-1][1][1], "255.255.0.0")

    def test_dhcp_bez_link_local(self):
        lan = E.utworz({})
        self.assertIsNone(E.po_czasie_dhcp(lan, {"link_local": False}))

    def test_dhcp_udany(self):
        lan = E.utworz({})
        lan.polaczony = True
        lan._ip = ("10.0.0.5", "255.255.255.0", "10.0.0.1", "10.0.0.1")
        self.assertEqual(asyncio.run(E.czekaj_na_adres(lan, {"tryb": "dhcp"})), "10.0.0.5")
        self.assertEqual(self.r.nazwane("LAN.ifconfig"), [])


class TestLinkLocal(unittest.TestCase):
    def test_zakres_rfc3927(self):
        for m4 in (0, 1, 253, 254, 255):
            for m5 in (0, 255):
                a = E.adres_link_local(bytes((2, 0, 0, 0, m4, m5)))
                o = [int(x) for x in a.split(".")]
                self.assertEqual(o[:2], [169, 254])
                self.assertTrue(1 <= o[2] <= 254, a)


if __name__ == "__main__":
    unittest.main(verbosity=1)
