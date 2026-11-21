# -*- coding: utf-8 -*-
"""a) EN modułu ESP32-S3-WROOM-1: RC z obwod.py (R5 z 3V3 do EN, C7 z EN do masy) przy narastaniu 3,3 V.

Wymagania (Espressif, ESP32-S3-WROOM-1 & WROOM-1U Datasheet v1.8):
- rys. 4-2 i tab. 4-6: tSTBL ≥ 50 µs — szyny zasilania mają się ustalić, zanim EN zostanie podniesiony;
  punkt odniesienia na rys. 4-2 to 2,8 V na VDD3P3/VDDA;
- tab. 6-3: VIH_nRST = 0,75 · VDD (zwolnienie resetu), VIL_nRST = 0,25 · VDD, IIL/IIH ≤ 50 nA, CIN = 2 pF;
- tab. 6-2: VDD33 3,0–3,6 V (dodatkowe, ostrzejsze odniesienie: EN rośnie dopiero po wejściu VDD w zakres pracy);
- tab. 4-2: tH = 3 ms (nóżki konfiguracyjne odczytywane po podniesieniu EN) — sprawdzamy GPIO3 (STOP, nóżka
  konfiguracyjna JTAG, rozdz. 4.4), który ma na płytce filtr przycisku z podciąganiem.
Model zasilania: liniowa rampa 0 → 3,3 V w czasie Tr. TLV62569DBV ma miękki start 800 µs (TI SLVSDG1C, tab. 6.5),
ale przy wolno rosnącym VBUS pracuje ze współczynnikiem wypełnienia 100 % (SLVSDG1C 7.3.2), więc 3V3 może rosnąć
tak wolno jak VBUS — stąd przegląd Tr i szukanie granicy.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402

VDD = 3.3
VIH_NRST = 0.75          # · VDD, WROOM-1 v1.8 tab. 6-3
VIL_NRST = 0.25          # · VDD, tab. 6-3
T_STBL = 50e-6           # tab. 4-6
V_ODNIESIENIA = 2.8      # rys. 4-2
VDD_MIN = 3.0            # tab. 6-2
I_UPLYW = 50e-9          # tab. 6-3 (IIL/IIH maks.); znak dobrany na niekorzyść: prąd wpływa do węzła EN
C_IN = 2e-12             # tab. 6-3
T_H = 3e-3               # tab. 4-2


def deck(tr, c_mnoznik=1.0):
    r5, c7 = o.element("R5"), o.element("C7")
    r_pod, r_szer, c_f = o.miedzy("V3", "n_gp"), o.miedzy("n_zl", "n_gp"), o.miedzy("n_gp", "GND")
    tau = r5.wartosc * c7.wartosc * c_mnoznik
    koniec = tr + 8 * tau
    krok = min(tr / 400, 10e-6)
    return f"""* a) EN ESP32-S3: R5/C7 z obwod.py, rampa 3V3 Tr = {tr * 1e3:g} ms, C x {c_mnoznik:g}
Vdd vdd 0 PWL(0 0 {o.liczba(tr)} {VDD})
R5 vdd en {o.liczba(r5.wartosc)}
C7 en 0 {o.liczba(c7.wartosc * c_mnoznik)}
Cin en 0 {o.liczba(C_IN)}
Iupl 0 en {o.liczba(I_UPLYW)}
* GPIO3 (STOP): podciąganie {r_pod.ref} i kondensator {c_f.ref} z pętli wejść, przycisk zwolniony
Rpod vdd g3 {o.liczba(r_pod.wartosc)}
Cf g3 0 {o.liczba(c_f.wartosc)}
Rszer g3 zl3 {o.liczba(r_szer.wartosc)}
Rotw zl3 0 1e12
.tran {o.liczba(krok / 4)} {o.liczba(koniec)} 0 {o.liczba(krok)}
.end
"""


def pomiar(tr, c_mnoznik=1.0, nazwa=None):
    w = o.uruchom(nazwa or f"a_en_tr{tr * 1e6:.0f}us_c{c_mnoznik:g}", deck(tr, c_mnoznik))
    t, vdd, en, g3 = w["time"], w["v(vdd)"], w["v(en)"], w["v(g3)"]
    t_ref = o.przeciecie(t, vdd, V_ODNIESIENIA)
    t_min = o.przeciecie(t, vdd, VDD_MIN)
    # zwolnienie resetu: EN ≥ 0,75 · VDD(t); liczymy dopiero od VDD > 0,1 V (przy 0 V oba są zerem)
    t_od = o.przeciecie(t, vdd, 0.1)
    t_en = o.przeciecie(t, en, VIH_NRST * vdd, od=t_od)
    return {
        "tr_ms": tr * 1e3, "c_mnoznik": c_mnoznik,
        "t_vdd_2v8_ms": t_ref * 1e3, "t_vdd_3v0_ms": t_min * 1e3, "t_en_vih_ms": t_en * 1e3,
        "tstbl_us": (t_en - t_ref) * 1e6, "zapas_po_3v0_us": (t_en - t_min) * 1e6,
        "v_en_przy_vdd_2v8": o.wartosc_w(t, en, t_ref),
        "v_gpio3_przy_en": o.wartosc_w(t, g3, t_en),
    }


class TestEnEsp32(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o.wymagaj_ngspice(cls)

    def sprawdz(self, wynik):
        self.assertGreaterEqual(wynik["tstbl_us"], T_STBL * 1e6, f"tSTBL < 50 µs: {wynik}")
        self.assertGreater(wynik["zapas_po_3v0_us"], 0, f"EN zwolniony przed VDD = 3,0 V: {wynik}")
        # EN w chwili VDD = 2,8 V tylko zapisujemy (v_en_przy_vdd_2v8): karta wymaga stanu < VIH_nRST,
        # a nie < VIL_nRST, więc to nie jest kryterium. GPIO3 (konfiguracja JTAG) ma być ustalony w stanie wysokim, zanim EN zwolni reset
        self.assertGreaterEqual(wynik["v_gpio3_przy_en"], 0.75 * VDD, wynik)

    def test_rampa_0_5_ms(self):
        w = pomiar(0.5e-3)
        o.zapisz_wynik("a_en_esp32", {"rampa_0_5ms": w})
        self.sprawdz(w)

    def test_rampa_miekki_start_0_8_ms(self):
        w = pomiar(0.8e-3)   # tSS TLV62569DBV typ. 800 µs (SLVSDG1C tab. 6.5)
        o.zapisz_wynik("a_en_esp32", {"rampa_0_8ms": w})
        self.sprawdz(w)

    def test_rampa_5_ms(self):
        w = pomiar(5e-3)
        o.zapisz_wynik("a_en_esp32", {"rampa_5ms": w})
        self.sprawdz(w)

    def test_rampa_5_ms_kondensator_polowa(self):
        # C7 0402 X5R przy 3,3 V traci część pojemności (DC bias) i ma tolerancję — połowa nominału jako scenariusz
        # pesymistyczny [DO WERYFIKACJI: krzywa DC bias C52923 u producenta]
        w = pomiar(5e-3, c_mnoznik=0.5)
        o.zapisz_wynik("a_en_esp32", {"rampa_5ms_c_polowa": w})
        self.sprawdz(w)

    def test_granica_wolnej_rampy(self):
        """Najdłuższa rampa 3V3, przy której nadal tSTBL ≥ 50 µs (bisekcja po symulacjach)."""
        wyniki = {}
        for c_m in (1.0, 0.5):
            def zapas(tr, c_m=c_m):
                return pomiar(tr, c_m, nazwa="a_en_bisekcja")["tstbl_us"] - T_STBL * 1e6
            tr_max = o.bisekcja(zapas, 0.5e-3, 400e-3, krokow=12)
            wyniki[f"tr_max_ms_c{c_m:g}"] = None if tr_max is None else round(tr_max * 1e3, 2)
        o.zapisz_wynik("a_en_esp32", {"granica": wyniki})
        # wymaganie robocze: zapas co najmniej do 10 × tSS przetwornicy (8 ms), także przy połowie pojemności
        self.assertIsNotNone(wyniki["tr_max_ms_c0.5"], wyniki)   # None: już rampa 0,5 ms łamie tSTBL
        self.assertGreaterEqual(wyniki["tr_max_ms_c0.5"], 8.0, wyniki)


if __name__ == "__main__":
    unittest.main(verbosity=2)
