# -*- coding: utf-8 -*-
"""f) Kwarc 25 MHz W5500: obciążenie C40/C41 (obwod.py) wobec CL kwarcu (XTAL25 w CZESCI). Obliczenie, nie SPICE.

Źródła:
- W5500 Datasheet Version 1.1.0, s. 60, 5.5.3 Crystal Characteristics: 25 MHz, tolerancja ±30 ppm (25 °C),
  pojemność równoległa C0 ≤ 7 pF, CL = 18 pF, starzenie ±3 ppm/rok;
- CL kwarcu YXC X322525MRB4SI = 18 pF (uwaga w CZESCI);
- pojemność pasożytnicza (ścieżki + nóżki XI/XO W5500): karta W5500 jej nie podaje — 2–6 pF jako założenie
  [DO WERYFIKACJI: pomiar częstotliwości na płytce];
- pojemność dynamiczna kwarcu C1: brak w karcie W5500, karta YXC nieodczytana — 3–8 fF jako założenie
  typowe dla 3225 / 25 MHz [DO WERYFIKACJI w karcie YXC];
- budżet 100BASE-TX ±50 ppm [DO WERYFIKACJI w IEEE 802.3 cl. 24/25].
Wzory: CL_ef = C40·C41/(C40+C41) + Cpas;  odstrojenie Δf/f ≈ (C1/2)·(1/(C0+CL_ef) − 1/(C0+CL)).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402

TOL_KWARCU_PPM = 30.0        # W5500 s. 60
C0_MAX_PF = 7.0              # W5500 s. 60
C_PAS_PF = (2.0, 6.0)        # [DO WERYFIKACJI] założenie
C1_FF = (3.0, 8.0)           # [DO WERYFIKACJI] założenie
BUDZET_PPM = 50.0            # [DO WERYFIKACJI] IEEE 802.3


def odstrojenie_ppm(c1_ff, c0_pf, cl_ef_pf, cl_pf):
    return (c1_ff * 1e-3 / 2) * (1 / (c0_pf + cl_ef_pf) - 1 / (c0_pf + cl_pf)) * 1e6


def liczenie():
    c40, c41 = o.element("C40").wartosc * 1e12, o.element("C41").wartosc * 1e12
    cl = o.obciazenie_kwarcu_pf()
    szereg = c40 * c41 / (c40 + c41)
    wyn = {"CL_kwarcu_pF": cl, "C40_pF": c40, "C41_pF": c41, "szeregowo_pF": szereg,
           "CL_ef_pF": [szereg + c for c in C_PAS_PF],
           "C_zalecane_pF": [2 * (cl - c) for c in C_PAS_PF]}
    # odstrojenie: najgorszy przypadek przy małym C0 (2 pF) i dużym C1 oraz najmniejszej CL_ef
    przypadki = {}
    for c0 in (2.0, C0_MAX_PF):
        for c1 in C1_FF:
            for cpas in C_PAS_PF:
                przypadki[f"C0={c0:g}pF C1={c1:g}fF Cpas={cpas:g}pF"] = round(odstrojenie_ppm(c1, c0, szereg + cpas, cl), 1)
    wyn["odstrojenie_ppm"] = przypadki
    wyn["odstrojenie_max_ppm"] = max(przypadki.values())
    wyn["suma_z_tolerancja_max_ppm"] = wyn["odstrojenie_max_ppm"] + TOL_KWARCU_PPM
    return wyn


class TestKwarcW5500(unittest.TestCase):
    def test_obciazenie_ponizej_cl(self):
        """Charakterystyka: przy 2 × 18 pF kwarc widzi mniej niż 18 pF, czyli pracuje powyżej 25 MHz."""
        w = liczenie()
        o.zapisz_wynik("f_kwarc_w5500", w)
        self.assertLess(max(w["CL_ef_pF"]), w["CL_kwarcu_pF"], w)
        self.assertGreater(min(w["odstrojenie_ppm"].values()), 0, w)

    @unittest.expectedFailure
    def test_przypadek_typowy_w_budzecie(self):
        """WYMAGANIE NIESPEŁNIONE (oczekiwana porażka): C1 = 5 fF, C0 = 2 pF, Cpas = 4 pF (środek założeń)
        daje ok. +42 ppm, a z tolerancją ±30 ppm ponad ±50 ppm. Po zmianie C40/C41 albo po odczycie C1/C0 z karty
        YXC (gdy wyjdzie mniej) zdjąć dekorator."""
        c40, c41 = o.element("C40").wartosc * 1e12, o.element("C41").wartosc * 1e12
        cl = o.obciazenie_kwarcu_pf()
        d = odstrojenie_ppm(5.0, 2.0, c40 * c41 / (c40 + c41) + 4.0, cl)
        # wariant poprawki do porównania: 2 × 27 pF (wartość z szeregu E12 najbliższa 2 · (CL − 4 pF) = 28 pF)
        d27 = odstrojenie_ppm(5.0, 2.0, 27 * 27 / 54 + 4.0, cl)
        o.zapisz_wynik("f_kwarc_w5500", {"typowo_ppm": round(d, 1), "typowo_przy_2x27pF_ppm": round(d27, 1)})
        self.assertLessEqual(d + TOL_KWARCU_PPM, BUDZET_PPM, d)

    @unittest.expectedFailure
    def test_najgorszy_przypadek_w_budzecie(self):
        """WYMAGANIE NIESPEŁNIONE przy skrajnych założeniach (oczekiwana porażka): C1 = 8 fF, C0 = 2 pF,
        Cpas = 2 pF daje odstrojenie, które z tolerancją ±30 ppm przekracza ±50 ppm. Rozstrzyga karta YXC (C1, C0)
        albo pomiar na płytce; poprawka to większe C40/C41 (pole C_zalecane_pF). Po poprawce zdjąć dekorator."""
        w = liczenie()
        self.assertLessEqual(w["suma_z_tolerancja_max_ppm"], BUDZET_PPM, w)


if __name__ == "__main__":
    unittest.main(verbosity=2)
