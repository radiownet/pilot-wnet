# -*- coding: utf-8 -*-
"""Testy tabeli pinów Rev A (CPython): zgodność z pcb/obwod.py i wykrywanie konfliktów."""
import os
import re
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "lib"))
import konfig_plytki as K  # noqa: E402
import pilot_wejscia as W  # noqa: E402

OBWOD = os.path.join(TU, "..", "..", "..", "pcb", "obwod.py")


def _obwod():
    with open(OBWOD, encoding="utf-8") as f:
        return f.read()


def _gpio(wzor_przed, t=None):
    """Numer GPIO z `<wzor_przed>io(N)` — także w opakowaniu `nazwij(io(N), "...")`."""
    t = _obwod() if t is None else t
    m = re.search(wzor_przed + r"\s*(?:nazwij\()?io\((\d+)\)", t)
    return int(m.group(1)) if m else None


class TestZgodnoscZObwodem(unittest.TestCase):
    """Piny przepisane z obwod.py — test czyta plik SKiDL jako tekst, bez importu SKiDL."""

    def test_wejscia(self):
        blok = re.search(r"WEJSCIA = \[(.*?)\]", _obwod(), re.S).group(1)
        z_obwodu = {n: int(g) for n, g in re.findall(r'\("(\w+)", (\d+)\)', blok)}
        self.assertEqual(z_obwodu, dict(K.WEJSCIA))

    def test_ethernet(self):
        blok = re.search(r"eth = \{(.*?)\}\n", _obwod(), re.S).group(1)
        z_obwodu = {s: int(g) for s, g in re.findall(r'\("(ETH_\w+)", (\d+)\)', blok)}
        self.assertEqual(z_obwodu, {"ETH_CS": K.ETH_CS, "ETH_SCLK": K.ETH_SCLK, "ETH_MISO": K.ETH_MISO,
                                    "ETH_MOSI": K.ETH_MOSI, "ETH_INT": K.ETH_INT})

    def test_lora(self):
        t = _obwod()
        blok = re.search(r"lora = \[(.*?)\]\n", t, re.S).group(1)
        z_obwodu = {s: int(g) for s, g in re.findall(r'"(LORA_\w+)", (\d+)\)', blok)}
        self.assertEqual(z_obwodu, {"LORA_NSS": K.LORA_NSS, "LORA_SCK": K.LORA_SCK, "LORA_MOSI": K.LORA_MOSI,
                                    "LORA_MISO": K.LORA_MISO, "LORA_BUSY": K.LORA_BUSY, "LORA_DIO1": K.LORA_DIO1})
        self.assertEqual(_gpio(r'"R76", nrst,', t), K.LORA_NRST)

    def test_pozostale(self):
        t = _obwod()
        self.assertEqual(_gpio(r"\bled \+=", t), K.LED_STATUS)
        self.assertEqual(_gpio(r"\bvs \+=", t), K.VSYS_SENSE)
        self.assertEqual(_gpio(r"\bexp13 \+=", t), K.EXP_IO13)
        self.assertEqual(_gpio(r"\bsda \+=", t), K.I2C_SDA)
        self.assertEqual(_gpio(r"\bscl \+=", t), K.I2C_SCL)
        self.assertEqual(_gpio(r"sw_boot\[1\] \+=", t), K.BOOT)
        self.assertIn('"PCA9685PW", "PCA", "U5", dnp=True', t)   # PCA9685 niemontowany
        self.assertIn("ETH_RST", t)                              # reset W5500 tylko siecią RC


class TestTabela(unittest.TestCase):
    def test_brak_konfliktow_w_rev_a(self):
        self.assertEqual(K.sprawdz(), [])

    def test_kolejnosc_bitow_maski(self):
        nazwy = [n for n, _ in K.WEJSCIA]
        self.assertEqual(nazwy.index("REC"), W.R.bit_length() - 1)
        self.assertEqual(nazwy.index("SPRAWDZ"), W.G.bit_length() - 1)
        self.assertEqual(nazwy.index("START"), W.START.bit_length() - 1)
        self.assertEqual(nazwy.index("JOY_RIGHT"), W.PRAWO.bit_length() - 1)
        self.assertEqual(len(K.PINY_MASKI), 10)

    def test_start_nie_na_gpio0(self):
        self.assertNotIn(0, K.PINY_MASKI)   # DECYZJE D9

    def test_psram_wykryty(self):
        for g in (33, 34, 35, 36, 37):
            m = K.piny()
            m["LORA_DIO2_SX1280"] = g
            self.assertTrue(any("PSRAM" in b for b in K.sprawdz(m)), g)

    def test_powtorzenie_wykryte(self):
        m = K.piny()
        m["BTN_PLAY"] = K.ETH_CS
        self.assertTrue(any("dwa razy" in b for b in K.sprawdz(m)))

    def test_niewyprowadzony_wykryty(self):
        m = K.piny()
        m["X"] = 22
        self.assertTrue(any("nie jest wyprowadzony" in b for b in K.sprawdz(m)))

    def test_tcxo(self):
        self.assertTrue(K.sprawdz(tcxo_mv=1500))
        self.assertTrue(K.sprawdz(tcxo_mv=3400))
        self.assertEqual(K.sprawdz(tcxo_mv=2200), [])
        self.assertEqual(K.ostrzezenia(tcxo_mv=1800), [])
        self.assertTrue(K.ostrzezenia(tcxo_mv=2000))

    def test_strapping_jako_ostrzezenie(self):
        m = K.piny()
        m["BTN_REC"] = 46
        self.assertTrue(any("GPIO46" in w for w in K.ostrzezenia(m)))
        self.assertEqual(K.ostrzezenia(), [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
