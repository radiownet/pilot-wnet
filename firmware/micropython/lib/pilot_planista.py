# -*- coding: utf-8 -*-
"""Planista ramek pilota: kiedy wysłać ramkę zmiany, a kiedy podtrzymanie (heartbeat).

Czysta logika (testowana w CPythonie). Zasady protokołu v1 (docs/ESP32_PROTOKOL.md):
  * każda zmiana stabilnej maski = natychmiastowa ramka;
  * bez zmian = ramka podtrzymania co `heartbeat_ms` (host zwalnia przełączniki po 2,5 s ciszy);
  * nie więcej niż `limit_na_s` ramek na sekundę (host odrzuca nadmiar) — zmiany szybsze niż limit
    są scalane: wysyłamy najnowszą maskę, gdy limit pozwoli.
"""


class Planista:
    def __init__(self, heartbeat_ms=1000, limit_na_s=40):
        self.heartbeat_ms = heartbeat_ms
        self.limit_na_s = limit_na_s
        self.ostatnia_ms = None
        self.okno_od = 0
        self.w_oknie = 0
        self.zalegla = None  # maska czekająca na wolne miejsce w limicie

    def _mozna(self, t):
        if t - self.okno_od >= 1000:
            self.okno_od = t
            self.w_oknie = 0
        return self.w_oknie < self.limit_na_s

    def _wyslano(self, t):
        self.w_oknie += 1
        self.ostatnia_ms = t

    def krok(self, t, nowa_maska=None):
        """Zwraca (maska, heartbeat) do wysłania albo None. `nowa_maska` = wynik Wejscia.krok()."""
        if nowa_maska is not None:
            self.zalegla = nowa_maska
        if self.zalegla is not None and self._mozna(t):
            m, self.zalegla = self.zalegla, None
            self._wyslano(t)
            return m, False
        if self.ostatnia_ms is None or t - self.ostatnia_ms >= self.heartbeat_ms:
            if self._mozna(t):
                self._wyslano(t)
                return None, True
        return None
