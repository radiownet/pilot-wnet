# -*- coding: utf-8 -*-
"""d) Dzielnik VSYS_SENSE: R51 z +5V do GPIO1, R52 do masy, C21 na GPIO1 (obwod.py) — wejście ADC1_CH0.

Źródła:
- Espressif, ESP32-S3 Series Datasheet v2.2, rozdz. 5.5, tab. 5-6: ATTEN3 (11 dB) zakres efektywny 0–2900 mV,
  błąd całkowity po kalibracji ±50 mV; pomiary producenta wykonane z zewnętrznym kondensatorem 100 nF na wejściu;
  tab. 5-5: do 100 kSPS;
- prąd upływu wejścia ADC: karta podaje tylko IIL/IIH ≤ 50 nA dla wejść cyfrowych (ESP32-S3-WROOM-1 Datasheet v1.8,
  tab. 6-3) — przyjmujemy go dla nóżki ADC [DO WERYFIKACJI: karta nie podaje upływu w trybie analogowym];
- pojemność próbkująca ADC: karta jej nie podaje — 10 pF jako założenie [DO WERYFIKACJI];
- zakres VBUS: 4,75–5,25 V wg specyfikacji USB 2.0 [DO WERYFIKACJI w USB 2.0 tab. 7-7], minus spadek na PTC F1
  (pomijamy — zaniża tylko odczyt).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402

V5 = 5.0
VBUS_MAX = 5.25          # [DO WERYFIKACJI] USB 2.0
ATTEN3_MAX = 2.9         # tab. 5-6
BLAD_ADC = 0.050         # tab. 5-6
I_UPLYW = 50e-9          # tab. 6-3 WROOM (przyjęte dla ADC) [DO WERYFIKACJI]
C_PROBKI = 10e-12        # [DO WERYFIKACJI] założenie
LSB = ATTEN3_MAX / 4096  # 12 bitów na zakres ATTEN3 (przybliżenie)


def elementy():
    return o.element("R51"), o.element("R52"), o.element("C21")


def deck(upl):
    r51, r52, c21 = elementy()
    return f"""* d) dzielnik VSYS: R51/R52/C21 z obwod.py, upływ wejścia {upl * 1e9:g} nA (dodatni = wypływa z węzła)
V5 v5 0 PWL(0 0 100u {V5})
R51 v5 vs {o.liczba(r51.wartosc)}
R52 vs 0 {o.liczba(r52.wartosc)}
C21 vs 0 {o.liczba(c21.wartosc)}
Iupl vs 0 {o.liczba(upl)}
.tran 1u 100m 0 20u
.end
"""


class TestDzielnikVsys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o.wymagaj_ngspice(cls)

    def test_ustalanie_i_uplyw(self):
        r51, r52, c21 = elementy()
        idealnie = V5 * r52.wartosc / (r51.wartosc + r52.wartosc)
        wyn = {"idealnie_V": idealnie, "tau_ms": (r51.wartosc * r52.wartosc / (r51.wartosc + r52.wartosc)) * c21.wartosc * 1e3}
        for znak, nazwa in ((+1, "uplyw_wyplywa"), (-1, "uplyw_wplywa"), (0, "bez_uplywu")):
            w = o.uruchom(f"d_vsys_{nazwa}", deck(znak * I_UPLYW))
            t, v = w["time"], w["v(vs)"]
            v_kon = float(v[-1])
            wyn[nazwa] = {
                "v_ustalone_V": v_kon,
                "blad_od_uplywu_mV": (v_kon - idealnie) * 1e3,
                "t_do_1LSB_ms": o.przeciecie(t, v, idealnie - LSB) * 1e3 if znak == 0 else None,
                "t_do_1mV_od_koncowej_ms": o.przeciecie(t, v, v_kon - 1e-3) * 1e3,
                "t_do_0_1proc_ms": o.przeciecie(t, v, v_kon * 0.999) * 1e3,
            }
        o.zapisz_wynik("d_dzielnik_vsys", wyn)
        bez = wyn["bez_uplywu"]
        self.assertAlmostEqual(bez["v_ustalone_V"], idealnie, delta=1e-4)
        # upływ 50 nA przez Rth = 50 kΩ daje ~2,5 mV — ma być ≤ 10 % błędu ADC po kalibracji (±50 mV)
        for n in ("uplyw_wyplywa", "uplyw_wplywa"):
            self.assertLessEqual(abs(wyn[n]["blad_od_uplywu_mV"]), 0.1 * BLAD_ADC * 1e3, wyn[n])
        # pierwszy wiarygodny pomiar po włączeniu: < 100 ms (firmware może odczekać przed pierwszym odczytem)
        self.assertLess(bez["t_do_1LSB_ms"], 100, bez)


class TestDzielnikVsysObliczenia(unittest.TestCase):
    """Bez SPICE — działa także bez ngspice."""

    def test_zakres_attenuacji_przy_tolerancji(self):
        """Najwyższe napięcie na GPIO1 przy VBUS = 5,25 V i najgorszym rozrzucie 1 % — w zakresie ATTEN3."""
        r51, r52, _ = elementy()
        a = r52.wartosc * (1 + r52.tolerancja)
        b = r51.wartosc * (1 - r51.tolerancja)
        v_max = VBUS_MAX * a / (a + b)
        k_min = (r52.wartosc * (1 - r52.tolerancja)) / (r52.wartosc * (1 - r52.tolerancja) + r51.wartosc * (1 + r51.tolerancja))
        k_max = a / (a + b)
        wyn = {"v_gpio1_max_V": v_max, "wspolczynnik_min": k_min, "wspolczynnik_max": k_max,
               "rozrzut_wspolczynnika_proc": (k_max / k_min - 1) * 100}
        o.zapisz_wynik("d_dzielnik_vsys", {"zakres": wyn})
        self.assertLess(v_max, ATTEN3_MAX, wyn)

    def test_obciazenie_przez_probkowanie(self):
        """Średni prąd ładowania pojemności próbkującej (model najgorszy: rozładowana przed każdą próbką)
        działa jak rezystancja 1/(Cs·f) do masy. Liczone, nie symulowane — Cs to założenie."""
        r51, r52, _ = elementy()
        rth = r51.wartosc * r52.wartosc / (r51.wartosc + r52.wartosc)
        idealnie = V5 * r52.wartosc / (r51.wartosc + r52.wartosc)
        wyn = {}
        for f in (10, 1e3, 100e3):
            r_eq = 1 / (C_PROBKI * f)
            wyn[f"blad_mV_przy_{f:g}Hz"] = -idealnie * rth / (rth + r_eq) * 1e3
        o.zapisz_wynik("d_dzielnik_vsys", {"probkowanie_Cs10pF": wyn})
        # odczyt stanu zasilania raz na sekundę lub rzadziej: błąd pomijalny wobec ±50 mV
        self.assertLess(abs(wyn["blad_mV_przy_10Hz"]), 0.1, wyn)


if __name__ == "__main__":
    unittest.main(verbosity=2)
