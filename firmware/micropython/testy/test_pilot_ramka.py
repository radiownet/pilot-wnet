# -*- coding: utf-8 -*-
"""Testy ramki pilota w CPythonie: te same wektory co w implementacji hosta (aplikacja na komputer
studyjny; jej kod nie jest jeszcze publiczny).

    python -I -B -X utf8 firmware\\micropython\\testy\\test_pilot_ramka.py
"""
import hashlib
import hmac
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import pilot_ramka as P  # noqa: E402

# Wektor wspólny z testem implementacji hosta (kod hosta nie jest jeszcze publiczny).
RAMKA_WEKTOR = dict(flagi=0, dev_id=7, seq=42, maska=0b10_0100_0001, dev_ms=123456, klucz=b"klucz-testowy", nonce=99)


class TestRamka(unittest.TestCase):
    def test_crc_wektor(self):
        self.assertEqual(P.crc16(b"123456789"), 0x29B1)

    def test_hmac_rfc4231(self):
        self.assertEqual(P.hmac_sha256(bytes([0x0B] * 20), b"Hi There").hex(),
                         "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7")
        self.assertEqual(P.hmac_sha256(b"Jefe", b"what do ya want for nothing?").hex(),
                         "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843")
        self.assertEqual(P.hmac_sha256(bytes([0xAA] * 131), b"Test Using Larger Than Block-Size Key - Hash Key First").hex(),
                         "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54")
        # zgodność z biblioteką standardową
        for k, m in ((b"", b""), (b"k" * 64, b"x" * 300), (os.urandom(17), os.urandom(33))):
            self.assertEqual(P.hmac_sha256(k, m), hmac.new(k, m, hashlib.sha256).digest())

    def test_cobs_wektory(self):
        self.assertEqual(P.cobs_koduj(bytes([0x00])), bytes([0x01, 0x01]))
        self.assertEqual(P.cobs_koduj(bytes([0x11, 0x22, 0x00, 0x33])), bytes([0x03, 0x11, 0x22, 0x02, 0x33]))
        self.assertEqual(P.cobs_koduj(bytes([0x11, 0x00, 0x00, 0x00])), bytes([0x02, 0x11, 0x01, 0x01, 0x01]))
        for n in (0, 1, 31, 253, 254, 255, 600):
            dane = bytes(i % 7 for i in range(n))
            k = P.cobs_koduj(dane)
            self.assertNotIn(0, k)
            self.assertEqual(P.cobs_dekoduj(k), dane, n)
        self.assertIsNone(P.cobs_dekoduj(bytes([0x05, 0x01])))

    def test_ramka_w_obie_strony(self):
        w = RAMKA_WEKTOR
        b = P.koduj(w["flagi"], w["dev_id"], w["seq"], w["maska"], w["dev_ms"], w["klucz"], w["nonce"])
        self.assertEqual(len(b), 32)
        self.assertEqual(P.dekoduj(b, w["klucz"], w["nonce"]), (0, 7, 42, 0b10_0100_0001, 123456))
        for klucz, nonce, kod in ((b"inny", 99, P.BLAD_HMAC), (w["klucz"], 100, P.BLAD_HMAC), (b"", 99, P.BLAD_BRAK_KLUCZA)):
            with self.assertRaises(P.BladRamki) as e:
                P.dekoduj(b, klucz, nonce)
            self.assertEqual(e.exception.kod, kod)
        zly = bytearray(b)
        zly[9] ^= 1
        with self.assertRaises(P.BladRamki) as e:
            P.dekoduj(bytes(zly), w["klucz"], w["nonce"])
        self.assertEqual(e.exception.kod, P.BLAD_CRC)

    def test_wektor_wspolny_z_rustem(self):
        w = RAMKA_WEKTOR
        b = P.koduj(w["flagi"], w["dev_id"], w["seq"], w["maska"], w["dev_ms"], w["klucz"], w["nonce"])
        # Stała przepisana do testu implementacji hosta; zmiana formatu ramki musi zmienić OBA testy.
        self.assertEqual(b.hex(), WEKTOR_HEX)

    def test_nadajnik_czeka_na_nonce_i_numeruje(self):
        n = P.Nadajnik(3, b"k")
        self.assertIsNone(n.ramka(P.R, 0))
        n.nowa_sesja(5)
        r1 = n.ramka(P.R | P.GORA, 10)
        r2 = n.ramka(0, 20, heartbeat=True)
        self.assertEqual(P.dekoduj(r1, b"k", 5)[2], 1)
        self.assertEqual(P.dekoduj(r2, b"k", 5)[:3], (P.FLAGA_HEARTBEAT, 3, 2))
        n.nowa_sesja(6)
        self.assertEqual(P.dekoduj(n.ramka(0, 30), b"k", 6)[2], 1, "nowa sesja = numeracja od 1")


WEKTOR_HEX = "010007002a000000410240e20100438fd37d9ffded7d88378dd62c75cdc51bf2"

if __name__ == "__main__":
    if "--wektor" in sys.argv:
        w = RAMKA_WEKTOR
        print(P.koduj(w["flagi"], w["dev_id"], w["seq"], w["maska"], w["dev_ms"], w["klucz"], w["nonce"]).hex())
        sys.exit(0)
    unittest.main(verbosity=1)
