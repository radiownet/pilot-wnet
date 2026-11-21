# -*- coding: utf-8 -*-
"""Testy eliminacji drgań i reguły joysticka (CPython).

    python -I -B -X utf8 firmware\\micropython\\testy\\test_pilot_wejscia.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import pilot_wejscia as W  # noqa: E402


def przebieg(w, probki):
    """probki: lista (t_ms, maska) co 1 ms; zwraca listę (t, nowa_maska) zmian."""
    out = []
    for t, m in probki:
        r = w.krok(m, t)
        if r is not None:
            out.append((t, r))
    return out


class TestWejscia(unittest.TestCase):
    def test_drgania_nie_daja_zdarzen(self):
        w = W.Wejscia(5)
        # styk drga 4 ms, potem stoi wciśnięty
        probki = [(t, W.R if t % 2 else 0) for t in range(4)] + [(t, W.R) for t in range(4, 20)]
        # ostatnie przejście na „wciśnięty” w t=3, stabilnie 5 ms → zdarzenie w t=8
        self.assertEqual(przebieg(w, probki), [(8, W.R)])

    def test_puszczenie_tez_stabilizowane(self):
        w = W.Wejscia(5)
        przebieg(w, [(t, W.G) for t in range(10)])
        zm = przebieg(w, [(t, 0 if t != 12 else W.G) for t in range(10, 25)])
        self.assertEqual(zm, [(18, 0)])

    def test_ukos_i_odrzut_przeciwnych(self):
        w = W.Wejscia(2)
        self.assertEqual(przebieg(w, [(t, W.GORA | W.LEWO) for t in range(5)]), [(2, W.GORA | W.LEWO)])
        # zwarcie w wiązce: ▲ i ▼ naraz — joystick zostaje jak był, przycisk przechodzi
        zm = przebieg(w, [(t, W.GORA | W.DOL | W.B) for t in range(5, 12)])
        self.assertEqual(zm, [(7, W.GORA | W.LEWO | W.B)])
        self.assertEqual(w.odrzuty, 1)

    def test_maska_z_pinow(self):
        self.assertEqual(W.maska_z_pinow([0, 1, 1, 1, 1, 1, 1, 1, 1, 0]), W.R | W.PRAWO)
        self.assertEqual(W.maska_z_pinow([1] * 10), 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
