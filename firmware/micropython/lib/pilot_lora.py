# -*- coding: utf-8 -*-
"""LoRa 868 MHz na płytce Rev A: Ebyte E22-900M22S (SX1262) przez sterownik micropython-lib `lora-sx126x`,
z ogranicznikiem zgodności z decyzją wykonawczą Komisji (UE) 2025/105 (pasma SRD 863–870 MHz).

Sterownik sam nie zna regulacji: moc –9…+22 dBm tylko obcina (R3 rozdz. 5.5). Ten moduł:
  * odmawia konfiguracji, w której kanał (środek ± połowa szerokości) nie mieści się w całości w jednym
    z dozwolonych pasm 46a, 47, 48, 50, 54, 56b;
  * odmawia mocy, przy której e.r.p. przekroczy limit pasma przy podanym zysku anteny i stratach;
  * liczy czas nadawania i nie dopuszcza do przekroczenia cyklu pracy w kroczącym oknie 1 h
    (0,1 % = 3,6 s, 1 % = 36 s, 10 % = 360 s na godzinę — obliczenia R3 rozdz. 5.5).

Tabela pasm — R3 rozdz. 5.5 za decyzją (UE) 2025/105 (Dz.Urz. UE 23.01.2025). Pominięte celowo:
47b (wymaga APC i dotyczy tylko sieci danych) i 56a (5 mW, głos). „Techniki dostępu i łagodzenia
zakłóceń” (LBT+AFA) jako alternatywa dla cyklu pracy nie są zaimplementowane — limiter zawsze stosuje
cykl pracy. Wartości z załącznika polskiego rozporządzenia (Dz.U. 2022 poz. 567) [DO WERYFIKACJI].

Uproszczenia (zachowawcze): emisja liczy się w całości, dopóki jej koniec mieści się w oknie; okno
każdego pasma jest osobne. Po zaniku zasilania licznik startuje od zera — `stan()`/`przywroc()` pozwalają
przechować go w pamięci RTC (przeżywa reset miękki i watchdog, nie odłączenie zasilania).

Czysta logika (`PASMA`, `znajdz_pasmo`, `moc_max_tx_dbm`, `czas_nadawania_us`, `Limiter`,
`sprawdz_konfiguracje`) działa w CPythonie; `PilotLoRa` wymaga MicroPythona i pakietów
`lora-sync` + `lora-sx126x`.
"""

import math

import konfig_plytki as K

OKNO_MS = 3_600_000   # okno obserwacji cyklu pracy: 1 h
ERP_NA_EIRP_DB = 2.15
MOC_MIN_DBM, MOC_MAX_DBM = -9, 22   # zakres SX1262 w sterowniku lora-sx126x

# (nr pasma, od Hz, do Hz, moc maks. mW e.r.p., cykl pracy w promilach)
PASMA = (
    ("46a", 863_000_000, 865_000_000, 25, 1),
    ("47", 865_000_000, 868_000_000, 25, 10),
    ("48", 868_000_000, 868_600_000, 25, 10),
    ("50", 868_700_000, 869_200_000, 25, 1),
    ("54", 869_400_000, 869_650_000, 500, 100),
    ("56b", 869_700_000, 870_000_000, 25, 10),
)

# szerokości pasma LoRa obsługiwane przez sterownik (README lora) → Hz
SZEROKOSCI_HZ = {
    "7.8": 7_812.5, "10.4": 10_416.67, "15.6": 15_625, "20.8": 20_833.33, "31.25": 31_250,
    "41.7": 41_666.67, "62.5": 62_500, "125": 125_000, "250": 250_000, "500": 500_000,
}


class BladZgodnosci(ValueError):
    pass


def _bw_hz(bw):
    klucz = str(bw)
    if klucz.endswith(".0"):
        klucz = klucz[:-2]
    if klucz not in SZEROKOSCI_HZ:
        raise BladZgodnosci("nieobsługiwana szerokość pasma %r kHz" % (bw,))
    return SZEROKOSCI_HZ[klucz]


def znajdz_pasmo(freq_khz, bw):
    """Krotka pasma, w którym mieści się cały kanał, albo None."""
    f = int(round(freq_khz * 1000))
    pol = _bw_hz(bw) / 2
    for p in PASMA:
        if p[1] <= f - pol and f + pol <= p[2]:
            return p
    return None


def mw_na_dbm(mw):
    return 10 * math.log10(mw)


def moc_max_tx_dbm(pasmo, zysk_anteny_dbi, straty_db=0.0, zapas_db=0.0):
    """Największa całkowita moc nadajnika (dBm), przy której e.r.p. ≤ limit pasma.

    e.r.p. [dBm] = P_tx + G_ant [dBi] − straty − 2,15; wynik obcięty do zakresu SX1262."""
    limit = mw_na_dbm(pasmo[3]) - zysk_anteny_dbi + straty_db + ERP_NA_EIRP_DB - zapas_db
    return min(MOC_MAX_DBM, int(math.floor(limit + 1e-9)))


def czas_nadawania_us(dl, sf, bw, coding_rate=5, preambula=8, crc=True, jawny_naglowek=True, ldro=None):
    """Czas emisji pakietu LoRa w µs (wzór z karty SX1261/2, rozdz. 6.1.4 — Semtech)."""
    bw_hz = _bw_hz(bw)
    t_sym_us = (1 << sf) * 1_000_000 / bw_hz
    if ldro is None:
        ldro = t_sym_us >= 16_380   # zalecenie karty: LDRO przy symbolu ≥ 16,38 ms
    de = 1 if ldro else 0
    h = 1 if jawny_naglowek else 0
    c = 1 if crc else 0
    cr = coding_rate - 4
    if sf < 7:
        licznik = 8 * dl + 16 * c - 4 * sf + 20 * h
        n_pre = preambula + 6.25
    else:
        licznik = 8 * dl + 16 * c - 4 * sf + 8 + 20 * h
        n_pre = preambula + 4.25
    n_pay = 8 + max(math.ceil(licznik / (4 * (sf - 2 * de))), 0) * (cr + 4)
    return int(math.ceil((n_pre + n_pay) * t_sym_us))


class Limiter:
    """Cykl pracy w kroczącym oknie 1 h, osobno dla każdego pasma. `t_ms` = zegar monotoniczny."""

    def __init__(self, okno_ms=OKNO_MS):
        self.okno_ms = okno_ms
        self._emisje = {}   # nr pasma → lista (koniec_ms, czas_us)

    def _sprzatnij(self, nr, t_ms):
        lst = self._emisje.get(nr, [])
        granica = t_ms - self.okno_ms
        lst = [e for e in lst if e[0] > granica]
        self._emisje[nr] = lst
        return lst

    @staticmethod
    def limit_us(pasmo, okno_ms=OKNO_MS):
        return pasmo[4] * okno_ms   # promil × okno [ms] = µs (1 ‰ z 3 600 000 ms = 3 600 000 µs)

    def wykorzystane_us(self, pasmo, t_ms):
        return sum(e[1] for e in self._sprzatnij(pasmo[0], t_ms))

    def zezwol(self, pasmo, czas_us, t_ms):
        """True, jeśli emisja `czas_us` rozpoczęta w `t_ms` zmieści się w limicie (≤)."""
        return self.wykorzystane_us(pasmo, t_ms) + czas_us <= self.limit_us(pasmo, self.okno_ms)

    def zapisz(self, pasmo, czas_us, t_ms):
        """Rejestruje emisję rozpoczętą w `t_ms`."""
        koniec = t_ms + (czas_us + 999) // 1000
        self._sprzatnij(pasmo[0], t_ms).append((koniec, czas_us))

    def pozostalo_us(self, pasmo, t_ms):
        return max(0, self.limit_us(pasmo, self.okno_ms) - self.wykorzystane_us(pasmo, t_ms))

    def stan(self, t_ms):
        """Stan do przechowania: lista (nr, ms_od_konca_do_teraz, czas_us)."""
        out = []
        for nr in sorted(self._emisje):
            for koniec, czas in self._sprzatnij(nr, t_ms):
                out.append((nr, t_ms - koniec, czas))
        return out

    def przywroc(self, stan, t_ms):
        for nr, wiek, czas in stan:
            self._emisje.setdefault(nr, []).append((t_ms - wiek, czas))


def sprawdz_konfiguracje(lora_cfg, zysk_anteny_dbi, straty_db=0.0, zapas_db=0.0):
    """Zwraca pasmo albo rzuca BladZgodnosci (pasmo, moc). Nie dopuszcza cichego obcięcia mocy."""
    f = lora_cfg.get("freq_khz")
    if f is None:
        raise BladZgodnosci("brak freq_khz")
    bw = lora_cfg.get("bw", "125")
    p = znajdz_pasmo(f, bw)
    if p is None:
        raise BladZgodnosci("kanał %s kHz ± %s/2 kHz poza dozwolonymi pasmami 863–870 MHz" % (f, bw))
    moc = lora_cfg.get("output_power", 14)
    if not (MOC_MIN_DBM <= moc <= MOC_MAX_DBM):
        raise BladZgodnosci("moc %s dBm poza zakresem SX1262 (%d…%d)" % (moc, MOC_MIN_DBM, MOC_MAX_DBM))
    mmax = moc_max_tx_dbm(p, zysk_anteny_dbi, straty_db, zapas_db)
    if moc > mmax:
        raise BladZgodnosci("moc %s dBm przekracza %d mW e.r.p. pasma %s (maks. %d dBm przy %s dBi)"
                            % (moc, p[3], p[0], mmax, zysk_anteny_dbi))
    return p


_KLUCZE_LORA_CFG = ("freq_khz", "sf", "bw", "coding_rate", "output_power", "preamble_len",
                    "implicit_header", "crc_en", "syncword", "invert_iq_tx", "invert_iq_rx")


class PilotLoRa:
    """SX1262 na E22-900M22S z limiterem. `konf` = sekcja `lora` konfiguracji pilota."""

    def __init__(self, konf, limiter=None, zegar_ms=None):
        self.konf = dict(konf)
        self.limiter = limiter or Limiter()
        self.lora_cfg = {k: self.konf[k] for k in _KLUCZE_LORA_CFG if k in self.konf}
        # Szerokość i moc zawsze jawnie w lora_cfg: sprawdzamy dokładnie te wartości, które dostanie
        # sterownik — bez polegania na tym, że jego wartości domyślne są takie same jak nasze.
        self.lora_cfg.setdefault("bw", "125")
        self.lora_cfg.setdefault("output_power", 14)
        self.pasmo = sprawdz_konfiguracje(self.lora_cfg, self._zysk(), self._straty(), self._zapas())
        self._zegar = zegar_ms or _ZegarMonotoniczny()
        tcxo = self.konf.get("tcxo_mv") or K.LORA_TCXO_MV
        bledy = K.sprawdz(tcxo_mv=tcxo)
        if bledy:
            raise BladZgodnosci("; ".join(bledy))
        import machine
        from lora import SX1262   # mip: lora-sync + lora-sx126x
        Pin = machine.Pin
        spi = machine.SPI(K.LORA_SPI_ID, baudrate=K.LORA_SPI_BAUD, sck=Pin(K.LORA_SCK),
                          mosi=Pin(K.LORA_MOSI), miso=Pin(K.LORA_MISO))
        self.modem = SX1262(spi, Pin(K.LORA_NSS), busy=Pin(K.LORA_BUSY), dio1=Pin(K.LORA_DIO1),
                            reset=Pin(K.LORA_NRST), dio2_rf_sw=K.LORA_DIO2_RF_SW,
                            dio3_tcxo_millivolts=tcxo, dio3_tcxo_start_time_us=K.LORA_TCXO_START_US,
                            lora_cfg=self.lora_cfg)

    def _zysk(self):
        return float(self.konf.get("zysk_anteny_dbi", 3.0))

    def _straty(self):
        return float(self.konf.get("straty_db", 0.0))

    def _zapas(self):
        return float(self.konf.get("zapas_db", 1.0))

    def konfiguruj(self, **zmiany):
        """Zmiana parametrów radia — tylko po pozytywnym sprawdzeniu zgodności."""
        nowa = dict(self.lora_cfg)
        nowa.update(zmiany)
        p = sprawdz_konfiguracje(nowa, self._zysk(), self._straty(), self._zapas())
        self.modem.configure(zmiany)
        self.lora_cfg, self.pasmo = nowa, p

    def czas_us(self, dl):
        """Czas emisji: większa z wartości sterownika i wzoru z karty (zachowawczo)."""
        c = self.lora_cfg
        wlasny = czas_nadawania_us(dl, c.get("sf", 7), c.get("bw", "125"), c.get("coding_rate", 5),
                                   c.get("preamble_len", 12), c.get("crc_en", True),
                                   not c.get("implicit_header", False))
        try:
            return max(wlasny, int(self.modem.get_time_on_air_us(dl)))
        except AttributeError:
            return wlasny

    def nadaj(self, dane):
        """True po wysłaniu; False, gdy limiter odmówił (nic nie wychodzi w eter)."""
        t = self._zegar()
        czas = self.czas_us(len(dane))
        if not self.limiter.zezwol(self.pasmo, czas, t):
            return False
        self.limiter.zapisz(self.pasmo, czas, t)
        self.modem.send(dane)
        return True

    def odbierz(self, timeout_ms=None):
        return self.modem.recv(timeout_ms)


class _ZegarMonotoniczny:
    """`time.ticks_ms()` przewija się co 2^30 ms (ok. 12,4 doby) — tu licznik bez przewinięcia."""

    def __init__(self):
        import time
        self._time = time
        self._mp = hasattr(time, "ticks_ms")   # False w CPythonie (testy): time.monotonic bez przewinięcia
        self._ost = time.ticks_ms() if self._mp else int(time.monotonic() * 1000)
        self._suma = 0

    def __call__(self):
        if not self._mp:
            return int(self._time.monotonic() * 1000) - self._ost
        teraz = self._time.ticks_ms()
        self._suma += self._time.ticks_diff(teraz, self._ost)
        self._ost = teraz
        return self._suma
