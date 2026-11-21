# -*- coding: utf-8 -*-
"""Odczyt 10 wejść pilota (joystick 4 + przyciski 6) z eliminacją drgań styków.

Czysta logika, bez `machine`: czytnik podaje surową maskę (bit = wciśnięty), a `Wejscia.krok(maska, t_ms)`
zwraca nową stabilną maskę albo None. Na płytce czytnik to odczyt GPIO z podciąganiem (styk zwiera
do masy, więc wciśnięty = 0 na pinie). Działa w MicroPythonie i w CPythonie (testy).

Zasady jak po stronie komputera studyjnego (implementacja hosta, która nie jest jeszcze publiczna):
przeciwne kierunki joysticka naraz są fizycznie niemożliwe w mikrostykach Sanwa, ale gdy przyjdą
(zwarcie w wiązce), nie wysyłamy ich — zostaje ostatni poprawny stan joysticka, a licznik `odrzuty`
rośnie (do diagnostyki na OLED).
"""

R, Y, B, G, START, STOP, GORA, DOL, LEWO, PRAWO = (1 << i for i in range(10))
JOY = GORA | DOL | LEWO | PRAWO


def joystick_poprawny(maska):
    j = maska & JOY
    if (j & GORA and j & DOL) or (j & LEWO and j & PRAWO):
        return False
    return True


class Wejscia:
    def __init__(self, stabilnosc_ms=5):
        self.stabilnosc_ms = stabilnosc_ms
        self.stabilna = 0
        self._kandydat = 0
        self._od = None
        self.odrzuty = 0

    def krok(self, surowa, t_ms):
        """Wywoływane co ~1 ms. Zwraca nową maskę po stabilnej zmianie, inaczej None."""
        if surowa != self._kandydat:
            self._kandydat = surowa
            self._od = t_ms
            return None
        if self._od is None or surowa == self.stabilna:
            return None
        if t_ms - self._od < self.stabilnosc_ms:
            return None
        nowa = surowa
        if not joystick_poprawny(nowa):
            self.odrzuty += 1
            nowa = (nowa & ~JOY) | (self.stabilna & JOY)
        self._od = None
        if nowa == self.stabilna:
            return None
        self.stabilna = nowa
        return nowa


def maska_z_pinow(wartosci, aktywne_niskie=True):
    """Lista 10 wartości pinów w kolejności bitów → maska."""
    m = 0
    for i, v in enumerate(wartosci):
        if (v == 0) if aktywne_niskie else (v == 1):
            m |= 1 << i
    return m
