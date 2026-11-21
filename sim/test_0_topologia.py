# -*- coding: utf-8 -*-
"""0) Czy obwód w pcb/obwod.py nadal ma topologię, którą odtwarzają decki SPICE (bez ngspice, działa wszędzie).

Gdy ktoś przepnie element (np. C7 z EN gdzie indziej) albo zmieni klucz w CZESCI, test wskaże, który deck
przestał odpowiadać płytce. Wartości liczbowe nie są tu powtórzone — sprawdzamy tylko, że da się je odczytać.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402


class TestTopologia(unittest.TestCase):
    def sieci(self, ref, a, b, rodzaj):
        e = o.element(ref)
        self.assertEqual(e.rodzaj, rodzaj, e)
        self.assertEqual({e.a, e.b}, {a, b}, e)
        self.assertFalse(e.dnp, f"{e} jest DNP — deck zakłada element zamontowany")
        self.assertGreater(e.wartosc, 0, e)
        return e

    def test_a_en(self):
        self.sieci("R5", "V3", "en", "R")
        self.sieci("C7", "en", "GND", "C")

    def test_b_reset_w5500(self):
        self.sieci("R61", "V3", "rst", "R")
        self.sieci("C39", "rst", "GND", "C")

    def test_c_wejscie(self):
        for a, b, r in (("n_zl", "n_gp", "R"), ("V3", "n_gp", "R"), ("n_gp", "GND", "C")):
            e = o.miedzy(a, b, r)
            self.assertFalse(e.dnp, e)

    def test_d_vsys(self):
        self.sieci("R51", "V5", "vs", "R")
        self.sieci("R52", "vs", "GND", "R")
        self.sieci("C21", "vs", "GND", "C")

    def test_e_fb(self):
        self.sieci("R3", "V3", "fb", "R")
        self.sieci("R4", "fb", "GND", "R")

    def test_f_kwarc(self):
        self.sieci("C40", "xi", "GND", "C")
        self.sieci("C41", "xo2", "GND", "C")
        self.assertGreater(o.obciazenie_kwarcu_pf(), 0)

    def test_przydzial_pinow(self):
        """Decki zakładają przydział Rev A: test a) modeluje GPIO3 jako STOP z filtrem przycisku (nóżka
        konfiguracyjna), test d) — VSYS_SENSE na GPIO1 (ADC1_CH0). Przy zmianie przydziału w obwod.py test
        wskaże, który deck trzeba przejrzeć. GPIO33–37 zajmuje PSRAM Octal modułu N16R8 — żadne wejście."""
        oczekiwane = [("START", 42), ("STOP", 3), ("JOY_UP", 4), ("JOY_DOWN", 5), ("JOY_LEFT", 6),
                      ("JOY_RIGHT", 7), ("SPRAWDZ", 12), ("WYSLIJ", 15), ("PLAY", 39), ("REC", 41)]
        wej = o.wejscia()
        self.assertEqual(wej, oczekiwane)
        self.assertEqual(dict(wej)["STOP"], 3, "test a) zakłada STOP na GPIO3 (nóżka konfiguracyjna)")
        for nazwa, g in wej:
            self.assertNotIn(g, range(33, 38), f"{nazwa} na GPIO{g} — linie PSRAM Octal")
        self.assertEqual(o.gpio_sieci("vs"), [1], "test d) zakłada VSYS_SENSE na GPIO1 (ADC1_CH0)")

    def test_odczyt_wartosci(self):
        self.assertEqual(o.wartosc_si("4.7k"), 4700.0)
        self.assertAlmostEqual(o.wartosc_si("1uF"), 1e-6)
        self.assertAlmostEqual(o.wartosc_si("6.8pF C0G"), 6.8e-12)
        self.assertEqual(o.wartosc_si("22k 1%"), 22e3)
        self.assertEqual(o.tolerancja("22k 1%"), 0.01)
        self.assertIsNone(o.tolerancja("100k"))
        self.assertEqual(o.element("R3").tolerancja, o.TOL_R_DOMYSLNA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
