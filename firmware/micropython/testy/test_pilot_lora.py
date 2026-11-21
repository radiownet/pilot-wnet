# -*- coding: utf-8 -*-
"""Testy ogranicznika LoRa (decyzja (UE) 2025/105) i opakowania SX1262 z atrapami (CPython)."""
import os
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "lib"))
sys.path.insert(0, TU)
import atrapy  # noqa: E402
import pilot_lora as L  # noqa: E402


def pasmo(nr):
    return [p for p in L.PASMA if p[0] == nr][0]


class TestPasma(unittest.TestCase):
    def test_typowe_kanaly(self):
        self.assertEqual(L.znajdz_pasmo(869525, "125")[0], "54")
        self.assertEqual(L.znajdz_pasmo(868100, "125")[0], "48")
        self.assertEqual(L.znajdz_pasmo(866000, "125")[0], "47")
        self.assertEqual(L.znajdz_pasmo(869850, "125")[0], "56b")
        self.assertEqual(L.znajdz_pasmo(869618, "62.5")[0], "54")   # preset „EU/UK (Narrow)” MeshCore

    def test_krawedzie_kanalu(self):
        self.assertEqual(L.znajdz_pasmo(869525, "250")[0], "54")   # 869,400–869,650 dokładnie
        self.assertIsNone(L.znajdz_pasmo(869526, "250"))
        self.assertIsNone(L.znajdz_pasmo(869525, "500"))
        self.assertEqual(L.znajdz_pasmo(868537.5, "125")[0], "48")  # górna krawędź 868,6 MHz
        self.assertIsNone(L.znajdz_pasmo(868540, "125"))
        self.assertEqual(L.znajdz_pasmo(863062.5, "125")[0], "46a")
        self.assertIsNone(L.znajdz_pasmo(863062, "125"))

    def test_poza_pasmami(self):
        for f in (862000, 868650, 869300, 869675, 870000, 915000):
            self.assertIsNone(L.znajdz_pasmo(f, "125"), f)

    def test_kanal_na_styku_dwoch_pasm_odrzucony(self):
        self.assertIsNone(L.znajdz_pasmo(865000, "125"))   # pół w 46a, pół w 47

    def test_nieznana_szerokosc(self):
        with self.assertRaises(L.BladZgodnosci):
            L.znajdz_pasmo(869525, "100")


class TestMoc(unittest.TestCase):
    def test_pasmo_54_obciete_do_sx1262(self):
        self.assertEqual(L.moc_max_tx_dbm(pasmo("54"), 3.0), 22)

    def test_pasma_25_mw(self):
        # 25 mW = 13,98 dBm e.r.p.; +2,15 dB → 16,13 dBm przy antenie 0 dBi
        self.assertEqual(L.moc_max_tx_dbm(pasmo("48"), 0.0), 16)
        self.assertEqual(L.moc_max_tx_dbm(pasmo("48"), 3.0, 0.0, 1.0), 12)
        self.assertEqual(L.moc_max_tx_dbm(pasmo("48"), 3.0, 0.5, 0.0), 13)   # R3: ok. 13,6 dBm

    def test_duza_antena_w_pasmie_54(self):
        # 27 dBm ERP − 9 dBi + 2,15 = 20,15 → 20
        self.assertEqual(L.moc_max_tx_dbm(pasmo("54"), 9.0), 20)

    def test_sprawdz_konfiguracje(self):
        self.assertEqual(L.sprawdz_konfiguracje({"freq_khz": 868100, "bw": "125", "output_power": 16}, 0.0)[0], "48")
        with self.assertRaises(L.BladZgodnosci):
            L.sprawdz_konfiguracje({"freq_khz": 868100, "bw": "125", "output_power": 17}, 0.0)
        with self.assertRaises(L.BladZgodnosci):
            L.sprawdz_konfiguracje({"freq_khz": 869525, "bw": "125", "output_power": 23}, 0.0)
        with self.assertRaises(L.BladZgodnosci):
            L.sprawdz_konfiguracje({"freq_khz": 915000, "bw": "125", "output_power": 0}, 0.0)
        with self.assertRaises(L.BladZgodnosci):
            L.sprawdz_konfiguracje({"bw": "125", "output_power": 0}, 0.0)


class TestCzasNadawania(unittest.TestCase):
    def test_sf7(self):
        # 12,25 symbolu preambuły + 28 symboli danych × 1,024 ms
        self.assertEqual(L.czas_nadawania_us(10, 7, "125", 5, 8), 41_216)

    def test_sf12_z_ldro(self):
        # LDRO włączone (symbol 32,768 ms): 12,25 + 43 = 55,25 symbolu
        self.assertEqual(L.czas_nadawania_us(32, 12, "125", 5, 8), 1_810_432)

    def test_dluzszy_pakiet_dluzej(self):
        self.assertGreater(L.czas_nadawania_us(64, 9, "125"), L.czas_nadawania_us(16, 9, "125"))


class TestCyklPracy(unittest.TestCase):
    def test_limity_w_oknie_godziny(self):
        self.assertEqual(L.Limiter.limit_us(pasmo("54")), 360_000_000)   # 10 % = 360 s
        self.assertEqual(L.Limiter.limit_us(pasmo("48")), 36_000_000)    # 1 % = 36 s
        self.assertEqual(L.Limiter.limit_us(pasmo("47")), 36_000_000)
        self.assertEqual(L.Limiter.limit_us(pasmo("56b")), 36_000_000)
        self.assertEqual(L.Limiter.limit_us(pasmo("46a")), 3_600_000)    # 0,1 % = 3,6 s
        self.assertEqual(L.Limiter.limit_us(pasmo("50")), 3_600_000)

    def _graniczny(self, nr):
        p = pasmo(nr)
        lim = L.Limiter.limit_us(p)
        li = L.Limiter()
        self.assertTrue(li.zezwol(p, lim, 0))         # dokładnie limit — wolno
        self.assertFalse(li.zezwol(p, lim + 1, 0))    # o 1 µs więcej — nie
        li.zapisz(p, lim - 1000, 0)
        self.assertTrue(li.zezwol(p, 1000, 10))
        self.assertFalse(li.zezwol(p, 1001, 10))
        li.zapisz(p, 1000, 10)
        self.assertEqual(li.pozostalo_us(p, 20), 0)
        self.assertFalse(li.zezwol(p, 1, 20))
        return p, li, lim

    def test_10_procent(self):
        self._graniczny("54")

    def test_1_procent(self):
        self._graniczny("48")

    def test_0_1_procent(self):
        self._graniczny("46a")

    def test_okno_kroczace(self):
        p = pasmo("50")
        li = L.Limiter()
        li.zapisz(p, 3_600_000, 0)          # cały limit 0,1 %; emisja kończy się w 3600 ms
        koniec = 3_600
        self.assertFalse(li.zezwol(p, 1, koniec + L.OKNO_MS - 1))
        self.assertTrue(li.zezwol(p, 3_600_000, koniec + L.OKNO_MS))

    def test_pasma_niezalezne(self):
        li = L.Limiter()
        li.zapisz(pasmo("54"), L.Limiter.limit_us(pasmo("54")), 0)
        self.assertFalse(li.zezwol(pasmo("54"), 1, 1))
        self.assertTrue(li.zezwol(pasmo("48"), 1000, 1))

    def test_stan_i_przywrocenie(self):
        p = pasmo("48")
        li = L.Limiter()
        li.zapisz(p, 30_000_000, 1000)
        s = li.stan(50_000)
        nowy = L.Limiter()
        nowy.przywroc(s, 7)                 # inny zegar po resecie
        self.assertEqual(nowy.pozostalo_us(p, 7), 6_000_000)
        self.assertFalse(nowy.zezwol(p, 6_000_001, 7))


class TestPilotLoRaZAtrapami(unittest.TestCase):
    def setUp(self):
        self.r = atrapy.zainstaluj()
        self.t = [0]

    def tearDown(self):
        atrapy.usun()

    def _konf(self, **zm):
        k = {"freq_khz": 869525, "bw": "125", "sf": 9, "coding_rate": 5, "output_power": 14,
             "preamble_len": 8, "zysk_anteny_dbi": 3.0, "straty_db": 0.0, "zapas_db": 1.0}
        k.update(zm)
        return k

    def test_piny_i_parametry_sterownika(self):
        lo = L.PilotLoRa(self._konf(), zegar_ms=lambda: self.t[0])
        spi = self.r.nazwane("SPI")[0]
        self.assertEqual(spi[1], 1)
        self.assertEqual((spi[2]["sck"], spi[2]["mosi"], spi[2]["miso"]), (10, 11, 9))
        _, cs, kw = self.r.nazwane("SX1262")[0]
        self.assertEqual(cs, 40)
        self.assertEqual((kw["busy"], kw["dio1"], kw["reset"]), (16, 8, 2))
        self.assertIs(kw["dio2_rf_sw"], True)
        self.assertEqual(kw["dio3_tcxo_millivolts"], 1800)
        self.assertEqual(kw["lora_cfg"]["freq_khz"], 869525)
        self.assertNotIn("zysk_anteny_dbi", kw["lora_cfg"])
        self.assertEqual(lo.pasmo[0], "54")

    def test_szerokosc_i_moc_zawsze_jawne_dla_sterownika(self):
        # bez bw/output_power w konfiguracji sterownik nie może dostać własnych wartości domyślnych
        k = self._konf()
        del k["bw"], k["output_power"]
        L.PilotLoRa(k, zegar_ms=lambda: self.t[0])
        kw = self.r.nazwane("SX1262")[0][2]
        self.assertEqual((kw["lora_cfg"]["bw"], kw["lora_cfg"]["output_power"]), ("125", 14))

    def test_tcxo_z_konfiguracji(self):
        L.PilotLoRa(self._konf(tcxo_mv=2200))
        self.assertEqual(self.r.nazwane("SX1262")[0][2]["dio3_tcxo_millivolts"], 2200)

    def test_poza_pasmem_nie_dotyka_sprzetu(self):
        with self.assertRaises(L.BladZgodnosci):
            L.PilotLoRa(self._konf(freq_khz=869300))
        with self.assertRaises(L.BladZgodnosci):
            L.PilotLoRa(self._konf(freq_khz=868100, output_power=14))   # 25 mW przy 3 dBi
        self.assertEqual(self.r.nazwane("SPI"), [])
        self.assertEqual(self.r.nazwane("SX1262"), [])

    def test_limiter_odmawia_nadania(self):
        # pasmo 50 (0,1 % = 3,6 s): SF12, 32 B = 1,81 s — mieszczą się jeden… i nie dwa pakiety
        lo = L.PilotLoRa(self._konf(freq_khz=869000, sf=12, output_power=10), zegar_ms=lambda: self.t[0])
        self.assertEqual(lo.pasmo[0], "50")
        self.assertTrue(lo.nadaj(bytes(32)))
        self.t[0] = 5_000
        self.assertFalse(lo.nadaj(bytes(32)))
        self.assertEqual(len(lo.modem.wyslane), 1)
        self.t[0] = 1_811 + L.OKNO_MS
        self.assertTrue(lo.nadaj(bytes(32)))

    def test_konfiguruj_tylko_zgodnie(self):
        lo = L.PilotLoRa(self._konf())
        with self.assertRaises(L.BladZgodnosci):
            lo.konfiguruj(freq_khz=869300)
        self.assertEqual(lo.lora_cfg["freq_khz"], 869525)
        self.assertEqual(self.r.nazwane("SX1262.configure"), [])
        lo.konfiguruj(output_power=20)
        self.assertEqual(self.r.nazwane("SX1262.configure")[0][1], {"output_power": 20})


if __name__ == "__main__":
    unittest.main(verbosity=1)
