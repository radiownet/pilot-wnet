# -*- coding: utf-8 -*-
"""c) Filtr wejścia przycisku (pętla WEJSCIA w obwod.py): złącze → R 1 kΩ → GPIO, 10 kΩ do 3V3, 10 nF do masy.

Przycisk zwiera złącze (n_zl) do masy. Progi wejścia (Espressif, ESP32-S3-WROOM-1 Datasheet v1.8, tab. 6-3):
VIL ≤ 0,25 · VDD, VIH ≥ 0,75 · VDD, CIN = 2 pF, wewnętrzne podciąganie RPU typ. 45 kΩ (gdy firmware je włączy).
Między VIL a VIH stan wejścia jest nieokreślony — liczymy to jako „może dać zbocze”.
Firmware (firmware/micropython/lib/pilot_wejscia.py) odpytuje wejścia co ~1 ms i uznaje zmianę dopiero po 5 ms
stabilności (Wejscia(stabilnosc_ms=5)), więc to on, a nie RC, odpowiada za eliminację drgań styków.
Pojemność SRV05-4 i przewodu do przycisku pominięta (pF wobec 10 nF) [DO WERYFIKACJI: karta Semtech SRV05-4].
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import obwody as o  # noqa: E402

VDD = 3.3
VIL = 0.25 * VDD     # tab. 6-3
VIH = 0.75 * VDD     # tab. 6-3
C_IN = 2e-12         # tab. 6-3
RPU_WEWN = 45e3      # tab. 6-3, typ.
T_NACISK = 1e-3      # chwila wciśnięcia w scenariuszach
STABILNOSC_FW = 5e-3  # pilot_wejscia.py: stabilnosc_ms=5


def elementy():
    return o.miedzy("n_zl", "n_gp"), o.miedzy("V3", "n_gp"), o.miedzy("n_gp", "GND")


def deck(ster_pwl, koniec, nazwa_opis, rpu_wewn=None):
    r_szer, r_pod, c_f = elementy()
    rpu = f"Rpuw vdd gp {o.liczba(rpu_wewn)}\n" if rpu_wewn else ""
    return f"""* c) wejście przycisku: {nazwa_opis}
Vdd vdd 0 {VDD}
Rpod vdd gp {o.liczba(r_pod.wartosc)}
{rpu}Rszer zl gp {o.liczba(r_szer.wartosc)}
Cf gp 0 {o.liczba(c_f.wartosc)}
Cin gp 0 {o.liczba(C_IN)}
* przycisk: przełącznik sterowany napięciem (1 V = zwarty), 0,1 Ω / 1 TΩ
Sp zl 0 ster 0 styk
.model styk sw(vt=0.5 vh=0.01 ron=0.1 roff=1e12)
Vster ster 0 PWL({ster_pwl})
.tran 0.1u {o.liczba(koniec)} 0 0.5u
.end
"""


def pwl_impuls(t0, szer, zwarty_przed):
    """Sterowanie przełącznika: stan zwarty_przed (0/1), w chwili t0 na czas szer odwrotny (zbocza 10 ns)."""
    a, b = (1, 0) if zwarty_przed else (0, 1)
    e = 10e-9
    return " ".join(o.liczba(x) for x in (0, a, t0, a, t0 + e, b, t0 + szer, b, t0 + szer + e, a))


def czysty_nacisk(rpu_wewn=None):
    """Wciśnięcie w T_NACISK, trzymanie 2 ms, zwolnienie."""
    t_zw = T_NACISK + 2e-3
    w = o.uruchom("c_przycisk_czysty" + ("_rpu" if rpu_wewn else ""),
                  deck(pwl_impuls(T_NACISK, 2e-3, False), t_zw + 1.5e-3, "czyste wciśnięcie 2 ms", rpu_wewn))
    t, v = w["time"], w["v(gp)"]
    v_wys = o.wartosc_w(t, v, T_NACISK * 0.9)
    v_nis = o.wartosc_w(t, v, t_zw - 1e-6)
    v90, v10 = v_nis + 0.9 * (v_wys - v_nis), v_nis + 0.1 * (v_wys - v_nis)
    return {
        "v_zwolniony_V": v_wys, "v_wcisniety_V": v_nis,
        "opoznienie_do_VIL_us": (o.przeciecie(t, v, VIL, -1, T_NACISK) - T_NACISK) * 1e6,
        "opadanie_90_10_us": (o.przeciecie(t, v, v10, -1, T_NACISK) - o.przeciecie(t, v, v90, -1, T_NACISK)) * 1e6,
        "opoznienie_do_VIH_us": (o.przeciecie(t, v, VIH, +1, t_zw) - t_zw) * 1e6,
        "narastanie_10_90_us": (o.przeciecie(t, v, v90, +1, t_zw) - o.przeciecie(t, v, v10, +1, t_zw)) * 1e6,
    }


def impuls(szer, zwarty_przed):
    """Jedno drgnięcie styku: zwarcie (zwarty_przed=False) albo rozwarcie (True) na czas szer."""
    rodz = "rozwarcie" if zwarty_przed else "zwarcie"
    w = o.uruchom(f"c_impuls_{rodz}_{szer * 1e6:.0f}us",
                  deck(pwl_impuls(T_NACISK, szer, zwarty_przed), T_NACISK + szer + 0.5e-3, f"{rodz} {szer * 1e6:g} µs"))
    t, v = w["time"], w["v(gp)"]
    od = T_NACISK * 0.5
    okno = (t >= od)
    return {"min_V": float(v[okno].min()), "max_V": float(v[okno].max())}


class TestWejsciePrzycisku(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o.wymagaj_ngspice(cls)

    def test_poziomy_i_czasy_czystego_nacisku(self):
        w = czysty_nacisk()
        o.zapisz_wynik("c_wejscie_przycisku", {"czysty_nacisk": w})
        self.assertGreaterEqual(w["v_zwolniony_V"], VIH, w)
        self.assertLessEqual(w["v_wcisniety_V"], VIL, w)
        # odpowiedź w obu kierunkach dużo krótsza niż okres odpytywania 1 ms
        self.assertLess(w["opoznienie_do_VIL_us"], 100, w)
        self.assertLess(w["opoznienie_do_VIH_us"], 1000, w)

    def test_z_wewnetrznym_podciaganiem(self):
        # firmware może włączyć Pin.PULL_UP (45 kΩ równolegle) — poziom niski nadal poniżej VIL
        w = czysty_nacisk(rpu_wewn=RPU_WEWN)
        o.zapisz_wynik("c_wejscie_przycisku", {"czysty_nacisk_z_rpu45k": w})
        self.assertLessEqual(w["v_wcisniety_V"], VIL, w)
        self.assertGreaterEqual(w["v_zwolniony_V"], VIH, w)

    def test_rozwarcie_50us_przy_wcisnietym_nie_dochodzi_do_vih(self):
        """Słabsze kryterium (spełnione): rozwarcie 50 µs nie podnosi GPIO do VIH, czyli nie daje pewnego stanu wysokiego."""
        w = impuls(50e-6, zwarty_przed=True)
        o.zapisz_wynik("c_wejscie_przycisku", {"rozwarcie_50us": w})
        self.assertLess(w["max_V"], VIH, f"rozwarcie 50 µs przekracza VIH: {w}")

    @unittest.expectedFailure
    def test_rozwarcie_50us_przy_wcisnietym_nie_daje_zbocza(self):
        """WYMAGANIE NIESPEŁNIONE przez sam RC (oczekiwana porażka): zgodnie z umową z nagłówka strefa VIL–VIH
        „może dać zbocze”, a rozwarcie 50 µs podnosi GPIO ponad VIL (ok. 1,5 V wobec 0,825 V). Histerezy wejścia
        karta modułu nie podaje, więc i tu ochronę daje firmware (5 ms stabilności). Po zmianie filtra zdjąć dekorator."""
        w = impuls(50e-6, zwarty_przed=True)
        self.assertLess(w["max_V"], VIL, f"rozwarcie 50 µs wchodzi w strefę nieokreśloną: {w}")

    @unittest.expectedFailure
    def test_zwarcie_50us_przy_zwolnionym_nie_daje_zbocza(self):
        """WYMAGANIE NIESPEŁNIONE przez sam RC (oczekiwana porażka): przy zwarciu stała czasowa to
        (1 kΩ ∥ 10 kΩ) · 10 nF ≈ 9 µs, więc 50 µs zwarcia sprowadza GPIO poniżej VIL. Ochronę daje firmware
        (5 ms stabilności), nie filtr. Gdy filtr zostanie zmieniony tak, że test przejdzie, zdjąć dekorator."""
        w = impuls(50e-6, zwarty_przed=False)
        o.zapisz_wynik("c_wejscie_przycisku", {"zwarcie_50us": w})
        self.assertGreater(w["min_V"], VIL, f"zwarcie 50 µs schodzi poniżej VIL: {w}")

    def test_granice_odfiltrowanych_impulsow(self):
        """Najdłuższe impulsy, które RC jeszcze tłumi (bez wejścia w strefę nieokreśloną), oraz zapas firmware."""
        def zwarcie(szer):
            return impuls(szer, False)["min_V"] - VIH        # ≥ 0: wejście nadal pewnie wysokie
        def rozwarcie(szer):
            return VIL - impuls(szer, True)["max_V"]         # ≥ 0: wejście nadal pewnie niskie
        def rozwarcie_vih(szer):
            return VIH - impuls(szer, True)["max_V"]         # ≥ 0: nie dochodzi do VIH
        def us(x):
            return None if x is None else x * 1e6     # bisekcja zwraca None, gdy już najkrótszy impuls narusza próg
        g = {
            "zwarcie_max_bez_strefy_us": us(o.bisekcja(zwarcie, 0.05e-6, 50e-6, krokow=12)),
            "zwarcie_50us_min_V": impuls(50e-6, False)["min_V"],
            "rozwarcie_max_bez_strefy_us": us(o.bisekcja(rozwarcie, 0.05e-6, 200e-6, krokow=12)),
            "rozwarcie_max_ponizej_VIH_us": us(o.bisekcja(rozwarcie_vih, 1e-6, 1000e-6, krokow=12)),
        }
        o.zapisz_wynik("c_wejscie_przycisku", {"granice": g})
        self.assertIsNotNone(g["zwarcie_max_bez_strefy_us"], g)
        self.assertIsNotNone(g["rozwarcie_max_ponizej_VIH_us"], g)
        # impuls krótszy niż ~1 µs (np. zakłócenie na przewodzie) nie może zmienić stanu
        self.assertGreater(g["zwarcie_max_bez_strefy_us"], 1.0, g)
        self.assertGreater(g["rozwarcie_max_ponizej_VIH_us"], 50.0, g)
        # drgania dłuższe od tych granic musi odfiltrować firmware: 5 ms stabilności ≫ granice RC
        self.assertGreater(STABILNOSC_FW * 1e6, 10 * g["rozwarcie_max_ponizej_VIH_us"], g)


if __name__ == "__main__":
    unittest.main(verbosity=2)
