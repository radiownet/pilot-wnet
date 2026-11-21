# -*- coding: utf-8 -*-
"""Testy konfiguracji JSON pilota (CPython): szablon bez sekretów, walidacja, scalanie z domyślną."""
import json
import os
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "lib"))
import pilot_konfig as C  # noqa: E402

SZABLON = os.path.join(TU, "..", "pilot_konfig.przyklad.json")
KLUCZ = "ab" * 32


class TestPortyUdp(unittest.TestCase):
    def test_port_spoza_zakresu_to_blad(self):
        k, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "udp": {"port_lokalny": 70000}}))
        self.assertTrue(any("port_lokalny" in x for x in b))
        k, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "udp": {"port": "47231"}}))
        self.assertTrue(any("udp.port " in x for x in b))

    def test_domyslne_porty_poprawne(self):
        k, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ}))
        self.assertEqual(b, [])
        self.assertEqual(k["udp"]["port_lokalny"], 47231)


class TestSzablon(unittest.TestCase):
    def test_szablon_bez_wartosci_tajnych(self):
        with open(SZABLON, encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(d["klucz_hmac_hex"], "")
        self.assertEqual(d["wifi"]["haslo"], "")
        self.assertEqual(d["wifi"]["ssid"], "")
        self.assertFalse(d["wifi"]["wlaczone"])          # studio: Wi-Fi wyłączone
        self.assertFalse(d["lora"]["wlaczona"])
        self.assertEqual(d["transporty"], ["usb_hid"])

    def test_szablon_ma_te_same_klucze_co_domyslna(self):
        with open(SZABLON, encoding="utf-8") as f:
            d = json.load(f)

        def klucze(x, p=""):
            out = set()
            for k, v in x.items():
                out.add(p + k)
                if isinstance(v, dict):
                    out |= klucze(v, p + k + ".")
            return out
        self.assertEqual(klucze(d), klucze(C.DOMYSLNA))

    def test_szablon_bez_klucza_blokuje_nadawanie(self):
        with open(SZABLON, encoding="utf-8") as f:
            konf, bledy = C.zaladuj_tekst(f.read())
        self.assertIsNone(C.klucz(konf))
        self.assertTrue(any("klucza" in b for b in bledy))


class TestWalidacja(unittest.TestCase):
    def test_kompletna(self):
        konf, bledy = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "dev_id": 3}))
        self.assertEqual(bledy, [])
        self.assertEqual(C.klucz(konf), bytes([0xAB]) * 32)
        self.assertEqual(konf["eth"]["dhcp_czekaj_ms"], 8000)   # scalone z domyślną

    def test_bledny_klucz(self):
        for k in ("ab" * 31, "zz" * 32, ""):
            konf, _ = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": k}))
            self.assertIsNone(C.klucz(konf), k)

    def test_udp_wymaga_hosta_i_interfejsu(self):
        _, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "transporty": ["eth_udp"]}))
        self.assertTrue(any("eth.wlaczony" in x for x in b))
        self.assertTrue(any("udp.host" in x for x in b))
        _, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "transporty": ["eth_udp"],
                                           "eth": {"wlaczony": True}, "udp": {"host": "192.168.77.1"}}))
        self.assertEqual(b, [])

    def test_wifi_wymaga_wlaczenia(self):
        _, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "transporty": ["wifi_udp"],
                                           "udp": {"host": "10.0.0.2"}}))
        self.assertTrue(any("wifi" in x for x in b))

    def test_zly_json_i_nieznany_transport(self):
        _, b = C.zaladuj_tekst("{nie json")
        self.assertTrue(b)
        _, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": KLUCZ, "transporty": ["lora"]}))
        self.assertTrue(any("nieznany transport" in x for x in b))

    def test_brak_pliku(self):
        konf, b = C.wczytaj(os.path.join(TU, "nie_ma_takiego_pliku.json"))
        self.assertTrue(any("brak pliku" in x for x in b))
        self.assertEqual(konf["transporty"], ["usb_hid"])

    def test_bledy_nie_zawieraja_klucza(self):
        _, b = C.zaladuj_tekst(json.dumps({"klucz_hmac_hex": "cd" * 31}))
        self.assertFalse(any("cd" * 4 in x for x in b))


if __name__ == "__main__":
    unittest.main(verbosity=1)
