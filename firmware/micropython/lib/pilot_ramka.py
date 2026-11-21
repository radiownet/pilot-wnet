# -*- coding: utf-8 -*-
"""Ramka pilota ESP32 → Pilot Wnet (protokół v1), wersja MicroPython.

Bajt w bajt zgodna ze specyfikacją docs/ESP32_PROTOKOL.md („Ramka”) i z implementacją hosta (aplikacja
na komputer studyjny; jej kod nie jest jeszcze publiczny). Działa w MicroPythonie (ESP32-S3) i w CPythonie
(testy na komputerze).

Ramka 32 bajty, little-endian:
  0 ver u8 = 1 · 1 flagi u8 (bit1 = heartbeat) · 2..4 dev_id u16 · 4..8 seq u32 (ściśle rosnący
  w sesji) · 8..10 maska u16 (R Y B G START STOP ▲ ▼ ◄ ►) · 10..14 dev_ms u32 · 14..16 crc16
  (CRC-16/CCITT-FALSE z bajtów 0..14) · 16..32 HMAC-SHA256(klucz, bajty 0..16 ‖ nonce_hosta u32)
  obcięty do 16 bajtów.
W USB CDC i UART ramka idzie zakodowana COBS z separatorem 0x00.
"""

try:
    import hashlib
except ImportError:  # starsze MicroPythony
    import uhashlib as hashlib  # noqa: F401
import struct

WERSJA = 1
FLAGA_HEARTBEAT = 0x02
DL = 32
MASKA_WSZYSTKO = 0x03FF

# Bity maski — kolejność jak w polu `maska` w docs/ESP32_PROTOKOL.md (implementacja hosta niepubliczna)
R, Y, B, G, START, STOP, GORA, DOL, LEWO, PRAWO = (1 << i for i in range(10))

BLAD_DLUGOSC = "dlugosc"
BLAD_WERSJA = "wersja"
BLAD_CRC = "crc"
BLAD_HMAC = "hmac"
BLAD_BRAK_KLUCZA = "brak_klucza"


class BladRamki(ValueError):
    def __init__(self, kod):
        super().__init__(kod)
        self.kod = kod


def crc16(dane):
    crc = 0xFFFF
    for b in dane:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def _sha256(dane):
    return hashlib.sha256(dane).digest()


def hmac_sha256(klucz, dane):
    """HMAC wg RFC 2104 (MicroPython nie ma modułu hmac w rdzeniu)."""
    klucz = bytes(klucz)
    if len(klucz) > 64:
        klucz = _sha256(klucz)
    klucz = klucz + bytes(64 - len(klucz))
    wew = bytes(b ^ 0x36 for b in klucz)
    zew = bytes(b ^ 0x5C for b in klucz)
    return _sha256(zew + _sha256(wew + bytes(dane)))


def _rowne_stalym_czasem(a, b):
    if len(a) != len(b):
        return False
    r = 0
    for x, y in zip(a, b):
        r |= x ^ y
    return r == 0


def koduj(flagi, dev_id, seq, maska, dev_ms, klucz, nonce):
    """Zwraca 32 bajty ramki."""
    naglowek = struct.pack("<BBHIHI", WERSJA, flagi & 0xFF, dev_id & 0xFFFF, seq & 0xFFFFFFFF,
                           maska & 0xFFFF, dev_ms & 0xFFFFFFFF)
    naglowek += struct.pack("<H", crc16(naglowek))
    h = hmac_sha256(klucz, naglowek + struct.pack("<I", nonce & 0xFFFFFFFF))
    return naglowek + h[:16]


def dekoduj(b, klucz, nonce):
    """Zwraca (flagi, dev_id, seq, maska, dev_ms) albo rzuca BladRamki."""
    if not klucz:
        raise BladRamki(BLAD_BRAK_KLUCZA)
    if len(b) != DL:
        raise BladRamki(BLAD_DLUGOSC)
    if b[0] != WERSJA:
        raise BladRamki(BLAD_WERSJA)
    if crc16(b[:14]) != struct.unpack("<H", b[14:16])[0]:
        raise BladRamki(BLAD_CRC)
    h = hmac_sha256(klucz, bytes(b[:16]) + struct.pack("<I", nonce & 0xFFFFFFFF))
    if not _rowne_stalym_czasem(h[:16], b[16:32]):
        raise BladRamki(BLAD_HMAC)
    _, flagi, dev_id, seq, maska, dev_ms = struct.unpack("<BBHIHI", b[:14])
    return flagi, dev_id, seq, maska & MASKA_WSZYSTKO, dev_ms


def cobs_koduj(dane):
    """COBS bez końcowego separatora 0x00."""
    out = bytearray([0])
    kod_idx = 0
    kod = 1
    for b in dane:
        if b == 0:
            out[kod_idx] = kod
            kod_idx = len(out)
            out.append(0)
            kod = 1
        else:
            out.append(b)
            kod += 1
            if kod == 0xFF:
                out[kod_idx] = kod
                kod_idx = len(out)
                out.append(0)
                kod = 1
    out[kod_idx] = kod
    return bytes(out)


def cobs_dekoduj(dane):
    """Zwraca bajty albo None przy błędnym kodowaniu."""
    out = bytearray()
    i = 0
    n = len(dane)
    while i < n:
        kod = dane[i]
        if kod == 0 or i + kod > n:
            return None
        out.extend(dane[i + 1:i + kod])
        i += kod
        if kod < 0xFF and i < n:
            out.append(0)
    return bytes(out)


class Nadajnik:
    """Strona pilota: numer ramki rośnie w sesji, nonce przychodzi od hosta przy połączeniu."""

    def __init__(self, dev_id, klucz):
        self.dev_id = dev_id
        self.klucz = bytes(klucz)
        self.nonce = None
        self.seq = 0
        self.maska = 0

    def nowa_sesja(self, nonce):
        self.nonce = nonce & 0xFFFFFFFF
        self.seq = 0

    def ramka(self, maska, dev_ms, heartbeat=False):
        """Ramka zmiany maski albo podtrzymania; None, dopóki host nie podał nonce."""
        if self.nonce is None:
            return None
        self.seq += 1
        self.maska = maska & MASKA_WSZYSTKO
        return koduj(FLAGA_HEARTBEAT if heartbeat else 0, self.dev_id, self.seq, self.maska, dev_ms,
                     self.klucz, self.nonce)
