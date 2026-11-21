# -*- coding: utf-8 -*-
"""e) Napięcie 3V3 z dzielnika FB przetwornicy TLV62569: R3 z +3V3 do FB, R4 z FB do masy (obwod.py).

Źródła:
- TI, TLV62569 SLVSDG1C (rev. X 2017), tab. 6.5 Electrical Characteristics: VFB = 0,588 / 0,6 / 0,612 V
  (min/typ/max); prądu wejściowego FB karta nie podaje — pomijamy [DO WERYFIKACJI];
- tolerancja rezystorów: dopisek „1%” w CZESCI albo domyślne 1 % (obwod.py, komentarz nad tabelą);
- granice: ESP32-S3-WROOM-1 Datasheet v1.8, tab. 6-2: VDD33 3,0–3,6 V; dodatkowo W5500 Datasheet v1.1.0, s. 59:
  VDD 2,97–3,63 V.
Model przetwornicy: idealny wzmacniacz błędu (VCVS, wzmocnienie 1e6) utrzymujący V(FB) = VFB, obciążenie 10 Ω.
Pomijamy tętnienia, odpowiedź na skok obciążenia i dryf temperaturowy (README).
Skrajne przypadki: 8 narożników (R3 ±, R4 ±, VFB min/max). Monte Carlo: 2000 kopii regulatora w jednym decku
(jedno .op), rozkład równomierny w granicach tolerancji (pesymistyczny wobec normalnego), ziarno stałe.
"""
import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402

VFB = {"min": 0.588, "typ": 0.6, "max": 0.612}   # SLVSDG1C tab. 6.5
ESP_MIN, ESP_MAX = 3.0, 3.6                      # WROOM-1 v1.8 tab. 6-2
N_MC = 2000
ZIARNO = 20261018


def elementy():
    return o.miedzy("V3", "fb", "R"), o.miedzy("fb", "GND", "R")


def deck(kopie):
    """kopie: lista (r3, r4, vfb). Każda kopia to osobny regulator out_i."""
    linie = ["* e) dzielnik FB TLV62569: R3/R4 z obwod.py, idealny wzmacniacz błędu, kopii: %d" % len(kopie)]
    for i, (r3, r4, vfb) in enumerate(kopie):
        linie += [f"Vr{i} ref{i} 0 {o.liczba(vfb)}",
                  f"E{i} out{i} 0 ref{i} fb{i} 1e6",
                  f"R3_{i} out{i} fb{i} {o.liczba(r3)}",
                  f"R4_{i} fb{i} 0 {o.liczba(r4)}",
                  f"Rl{i} out{i} 0 10"]
    linie += [".op", ".end"]
    return "\n".join(linie) + "\n"


def napiecia(nazwa, kopie):
    w = o.uruchom(nazwa, deck(kopie))
    return [float(w[f"v(out{i})"][0]) for i in range(len(kopie))]


class TestDzielnikFb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o.wymagaj_ngspice(cls)

    def test_nominal_i_narozniki(self):
        r3, r4 = elementy()
        nom = [(r3.wartosc, r4.wartosc, VFB["typ"])]
        naroz = []
        for s3, s4, v in itertools.product((-1, 1), (-1, 1), ("min", "max")):
            naroz.append((r3.wartosc * (1 + s3 * r3.tolerancja), r4.wartosc * (1 + s4 * r4.tolerancja), VFB[v]))
        u = napiecia("e_fb_narozniki", nom + naroz)
        wyn = {"nominalne_V": u[0], "obliczone_V": VFB["typ"] * (1 + r3.wartosc / r4.wartosc),
               "naroznik_min_V": min(u[1:]), "naroznik_max_V": max(u[1:]),
               "tolerancja_R3": r3.tolerancja, "tolerancja_R4": r4.tolerancja}
        o.zapisz_wynik("e_dzielnik_fb", wyn)
        self.assertAlmostEqual(u[0], 3.327, delta=0.001)          # komentarz w obwod.py: 3,327 V
        self.assertAlmostEqual(u[0], wyn["obliczone_V"], delta=1e-4)
        self.assertGreaterEqual(wyn["naroznik_min_V"], ESP_MIN, wyn)
        self.assertLessEqual(wyn["naroznik_max_V"], ESP_MAX, wyn)

    def test_monte_carlo(self):
        r3, r4 = elementy()
        los = random.Random(ZIARNO)
        kopie = [(r3.wartosc * (1 + los.uniform(-1, 1) * r3.tolerancja),
                  r4.wartosc * (1 + los.uniform(-1, 1) * r4.tolerancja),
                  los.uniform(VFB["min"], VFB["max"])) for _ in range(N_MC)]
        u = sorted(napiecia("e_fb_monte_carlo", kopie))
        sr = sum(u) / len(u)
        sd = (sum((x - sr) ** 2 for x in u) / (len(u) - 1)) ** 0.5
        wyn = {"n": N_MC, "min_V": u[0], "max_V": u[-1], "srednia_V": sr, "odch_std_mV": sd * 1e3,
               "p0_1_V": u[int(0.001 * N_MC)], "p99_9_V": u[int(0.999 * N_MC) - 1]}
        o.zapisz_wynik("e_dzielnik_fb", {"monte_carlo": wyn})
        self.assertGreaterEqual(u[0], ESP_MIN, wyn)
        self.assertLessEqual(u[-1], ESP_MAX, wyn)


if __name__ == "__main__":
    unittest.main(verbosity=2)
