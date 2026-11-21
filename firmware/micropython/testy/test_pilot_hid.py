# -*- coding: utf-8 -*-
"""Testy HID producenta: deskryptor raportu, długości raportów, rejestracja USB (atrapy, CPython)."""
import os
import struct
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "lib"))
sys.path.insert(0, TU)
import atrapy  # noqa: E402
import pilot_hid as H  # noqa: E402
import pilot_ramka as R  # noqa: E402


def elementy(d):
    """Parser krótkich elementów HID 1.11 (rozdz. 6.2.2.2): (typ, tag, wartość)."""
    i = 0
    out = []
    while i < len(d):
        b = d[i]
        rozm = (0, 1, 2, 4)[b & 0x03]
        wart = int.from_bytes(bytes(d[i + 1:i + 1 + rozm]), "little")
        out.append(((b >> 2) & 0x03, b >> 4, wart))
        i += 1 + rozm
    if i != len(d):
        raise ValueError("ucięty element")
    return out


def bity_raportow(d):
    """Sumaryczne bity raportów wejściowych i wyjściowych (bez ID raportów)."""
    rozmiar = liczba = 0
    we = wy = 0
    for typ, tag, w in elementy(d):
        if typ == 1 and tag == 0x7:
            rozmiar = w
        elif typ == 1 and tag == 0x9:
            liczba = w
        elif typ == 0 and tag == 0x8:
            we += rozmiar * liczba
        elif typ == 0 and tag == 0x9:
            wy += rozmiar * liczba
    return we, wy


class TestDeskryptor(unittest.TestCase):
    def test_strona_producenta(self):
        el = elementy(H.DESKRYPTOR_RAPORTU)
        self.assertEqual(el[0], (1, 0x0, 0xFF00))   # Usage Page (global) = 0xFF00

    def test_brak_stron_klawiatury_i_myszy(self):
        strony = [w for typ, tag, w in elementy(H.DESKRYPTOR_RAPORTU) if typ == 1 and tag == 0x0]
        self.assertEqual(strony, [0xFF00])          # bez 0x01 (Generic Desktop) i 0x07 (Keyboard)

    def test_dlugosci_raportow(self):
        self.assertEqual(bity_raportow(H.DESKRYPTOR_RAPORTU), (32 * 8, 8 * 8))
        self.assertEqual(H.DL_RAPORTU_WE, R.DL)

    def test_bez_report_id_i_zbalansowane_kolekcje(self):
        el = elementy(H.DESKRYPTOR_RAPORTU)
        self.assertFalse([e for e in el if e[0] == 1 and e[1] == 0x8])   # Report ID
        otw = sum(1 for e in el if e[0] == 0 and e[1] == 0xA)
        zam = sum(1 for e in el if e[0] == 0 and e[1] == 0xC)
        self.assertEqual((otw, zam), (1, 1))
        self.assertEqual(len(H.DESKRYPTOR_RAPORTU), 27)


class TestRaporty(unittest.TestCase):
    def test_raport_to_ramka(self):
        r = R.koduj(0, 7, 1, R.START, 123, b"k" * 32, 99)
        self.assertEqual(H.raport_z_ramki(r), r)
        with self.assertRaises(ValueError):
            H.raport_z_ramki(r[:31])

    def test_hello_w_raporcie_wyjsciowym(self):
        self.assertEqual(H.nonce_z_raportu(bytearray(b"PWN1" + struct.pack("<I", 0xDEADBEEF))), 0xDEADBEEF)
        self.assertIsNone(H.nonce_z_raportu(bytes(8)))


class TestUSBZAtrapami(unittest.TestCase):
    def setUp(self):
        self.r = atrapy.zainstaluj()
        H._aktywny = None

    def tearDown(self):
        atrapy.usun()
        H._aktywny = None

    def test_rejestracja_z_wbudowanym_cdc(self):
        itf = H.uruchom("Pilot Wnet", "Radio Wnet")
        (_, itfs, kw), = self.r.nazwane("usb.init")
        self.assertEqual(itfs, (itf,))
        self.assertIs(kw["builtin_driver"], True)    # REPL po USB zostaje (R5 S10)
        self.assertEqual(kw["product_str"], "Pilot Wnet")
        self.assertIs(H.aktywny(), itf)
        self.assertEqual(itf.report_descriptor, H.DESKRYPTOR_RAPORTU)
        self.assertEqual(len(itf._set_report_buf), 8)
        self.assertEqual(itf.interval_ms, 1)

    def test_punkt_koncowy_miesci_raport(self):
        itf = H.uruchom()
        opis = atrapy.Opis()
        strs = [None, None, None, None]
        itf.desc_cfg(opis, 2, 3, strs)
        (_, nr_itf, n_ep, klasa, podkl, prot, idx), = [w for w in opis.wpisy if w[0] == "interface"]
        self.assertEqual((nr_itf, n_ep, klasa, podkl, prot), (2, 1, 0x03, 0x00, 0x00))
        self.assertEqual(strs[idx], "Pilot Wnet")
        (_, adr, rodzaj, pakiet, okres), = [w for w in opis.wpisy if w[0] == "endpoint"]
        self.assertEqual((adr, rodzaj, okres), (0x83, "interrupt", 1))
        self.assertGreaterEqual(pakiet, H.DL_RAPORTU_WE)
        self.assertLessEqual(pakiet, 64)             # Full Speed: maks. 64 B

    def test_wysylanie_i_nonce(self):
        itf = H.uruchom()
        self.assertIsNone(itf.nonce())
        itf.on_set_report(memoryview(bytearray(b"PWN1" + struct.pack("<I", 5))), 0, 2)
        self.assertEqual(itf.nonce(), 5)
        r = R.koduj(0, 1, 1, 0, 0, b"x" * 32, 5)
        self.assertTrue(itf.wyslij(r))
        self.assertEqual(itf.wyslane, [r])
        itf.otwarty = False
        self.assertFalse(itf.wyslij(r))


if __name__ == "__main__":
    unittest.main(verbosity=1)
