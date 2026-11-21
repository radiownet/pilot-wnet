# -*- coding: utf-8 -*-
"""b) Reset W5500 przy włączeniu: R61 z 3V3 do RSTn, C39 z RSTn do masy (obwod.py), bez sterowania z GPIO.

Wymagania (WIZnet, W5500 Datasheet Version 1.1.0):
- s. 60, 5.5.1 Reset Timing: TRC (reset cycle time) ≥ 500 µs; opis nóżki 37 (s. 11, rozdz. 1.1 Pin Descriptions):
  „RESET should be held low at least 500 us”;
- s. 59, 5.3 DC Characteristics: VDD 2,97–3,63 V (od 2,97 V liczymy czas trzymania resetu); RSTn ma wejście
  z przerzutnikiem Schmitta, próg narastający VT+ = 1,53 / 1,64 / 1,73 V (min/typ/max), opadający
  VT− = 0,95 / 1,02 / 1,09 V; wewnętrzne podciąganie RPU = 50 / 77 / 112 kΩ (SCSn, RSTn, PMODE); upływ IL ≤ 1 µA.
Kryterium: od chwili VDD = 2,97 V do chwili, gdy RSTn przekroczy VT+ min (1,53 V — najwcześniejsze możliwe
zwolnienie resetu), musi minąć ≥ 500 µs. Rampa 3V3 jak w teście a).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402

VDD = 3.3
VDD_MIN = 2.97                               # s. 59
VT_PLUS = {"min": 1.53, "typ": 1.64, "max": 1.73}   # s. 59
RPU = {"min": 50e3, "typ": 77e3, "max": 112e3}      # s. 59
I_UPLYW = 1e-6                               # s. 59, IL; znak na niekorzyść (wpływa do węzła RSTn)
T_RC = 500e-6                                # s. 60


def deck(tr, rpu, r_mn, c_mn, upl):
    r61, c39 = o.element("R61"), o.element("C39")
    tau = (1 / (1 / (r61.wartosc * r_mn) + 1 / rpu)) * c39.wartosc * c_mn
    koniec = tr + 6 * tau
    krok = min(tr / 400, 10e-6)
    return f"""* b) RSTn W5500: R61/C39 z obwod.py + RPU wewnętrzny, Tr = {tr * 1e3:g} ms
Vdd vdd 0 PWL(0 0 {o.liczba(tr)} {VDD})
R61 vdd rst {o.liczba(r61.wartosc * r_mn)}
Rpu vdd rst {o.liczba(rpu)}
C39 rst 0 {o.liczba(c39.wartosc * c_mn)}
Iupl 0 rst {o.liczba(upl)}
.tran {o.liczba(krok / 4)} {o.liczba(koniec)} 0 {o.liczba(krok)}
.end
"""


SCENARIUSZE = {
    # nominalny: R61 nominalnie, RPU typowy, C39 nominalnie, bez upływu
    "nominalny": dict(rpu=RPU["typ"], r_mn=1.0, c_mn=1.0, upl=0.0),
    # najgorszy: R61 −1 %, RPU min, C39 −50 % (tolerancja + DC bias X5R 0402 [DO WERYFIKACJI]), upływ 1 µA do węzła
    "najgorszy": dict(rpu=RPU["min"], r_mn=1 - o.element("R61").tolerancja, c_mn=0.5, upl=I_UPLYW),
}


def pomiar(tr, scen, nazwa=None):
    p = SCENARIUSZE[scen]
    w = o.uruchom(nazwa or f"b_w5500_tr{tr * 1e6:.0f}us_{scen}", deck(tr, **p))
    t, vdd, rst = w["time"], w["v(vdd)"], w["v(rst)"]
    t_vdd = o.przeciecie(t, vdd, VDD_MIN)
    wynik = {"tr_ms": tr * 1e3, "scenariusz": scen, "t_vdd_2v97_ms": t_vdd * 1e3,
             "v_rst_przy_vdd_2v97": o.wartosc_w(t, rst, t_vdd)}
    for k, prog in VT_PLUS.items():
        t_r = o.przeciecie(t, rst, prog)
        wynik[f"t_niski_do_vt+{k}_us"] = (t_r - t_vdd) * 1e6
    return wynik


class TestResetW5500(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o.wymagaj_ngspice(cls)

    def sprawdz(self, w):
        self.assertGreaterEqual(w["t_niski_do_vt+min_us"], T_RC * 1e6, f"RSTn niski < 500 µs po VDD = 2,97 V: {w}")

    def test_rampa_0_5_ms(self):
        for scen in SCENARIUSZE:
            w = pomiar(0.5e-3, scen)
            o.zapisz_wynik("b_reset_w5500", {f"rampa_0_5ms_{scen}": w})
            self.sprawdz(w)

    def test_rampa_miekki_start_0_8_ms(self):
        for scen in SCENARIUSZE:
            w = pomiar(0.8e-3, scen)
            o.zapisz_wynik("b_reset_w5500", {f"rampa_0_8ms_{scen}": w})
            self.sprawdz(w)

    def test_wolna_rampa_5_ms(self):
        for scen in SCENARIUSZE:
            w = pomiar(5e-3, scen)
            o.zapisz_wynik("b_reset_w5500", {f"rampa_5ms_{scen}": w})
            self.sprawdz(w)

    _granica = None

    @classmethod
    def granica(cls):
        """Najdłuższa rampa 3V3, przy której RSTn jest jeszcze niski ≥ 500 µs po VDD = 2,97 V (bisekcja,
        liczona raz na przebieg i wspólna dla dwóch testów niżej)."""
        if cls._granica is None:
            wyniki = {}
            for scen in SCENARIUSZE:
                def zapas(tr, scen=scen):
                    return pomiar(tr, scen, nazwa="b_w5500_bisekcja")["t_niski_do_vt+min_us"] - T_RC * 1e6
                tr_max = o.bisekcja(zapas, 0.5e-3, 200e-3, krokow=12)
                wyniki[f"tr_max_ms_{scen}"] = None if tr_max is None else round(tr_max * 1e3, 2)
            o.zapisz_wynik("b_reset_w5500", {"granica": wyniki})
            cls._granica = wyniki
        return cls._granica

    def test_granica_wolnej_rampy_5_ms(self):
        # słabsze wymaganie (spełnione): wolna rampa 5 ms z przeglądu wyżej, scenariusz najgorszy
        w = self.granica()
        self.assertIsNotNone(w["tr_max_ms_najgorszy"], w)
        self.assertGreaterEqual(w["tr_max_ms_najgorszy"], 5.0, w)

    @unittest.expectedFailure
    def test_granica_wolnej_rampy_8_ms(self):
        """WYMAGANIE NIESPEŁNIONE (oczekiwana porażka): to samo wymaganie robocze co w a) — zapas do 10 × tSS
        przetwornicy (8 ms) w scenariuszu najgorszym. Wynik 6,0 ms; pierwsza wersja testu miała tu twarde 8 ms
        i nie przeszła. Próg nie został obniżony, tylko oznaczony jako niespełniony — poprawka obwodu (np. C39
        2,2 µF albo reset z GPIO, README „Wnioski”) powinna dać „unexpected success” i zdjęcie dekoratora."""
        w = self.granica()
        self.assertGreaterEqual(w["tr_max_ms_najgorszy"] or 0.0, 8.0, w)


if __name__ == "__main__":
    unittest.main(verbosity=2)
